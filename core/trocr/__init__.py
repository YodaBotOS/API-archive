# https://github.com/JeyyGit/Jeyy-Bot/blob/47ff713be8beb30116f990c99b2a021de4bdf7b9/utils/trocr.py#L29

from io import BytesIO
from dataclasses import dataclass, field

from google.cloud import translate
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont

from core.ocr import OCR
from core.executor import executor_function


@dataclass
class BoundingPoly:
    x: int = 0
    y: int = 0


@dataclass
class TextAnnotation:
    text: str
    bounding_box: list[BoundingPoly] = field(default_factory=lambda: [BoundingPoly()])


class TranslateOCRError(Exception):
    ...


class TranslateOCR:
    font = ImageFont.truetype('assets/fonts/SourceHanSans-Bold.ttc', 50)

    def __init__(self, ocr: OCR, project_id: str = None):
        self.ocr: OCR = ocr

        self.project_id: str = project_id

        self.translate: translate.TranslationServiceClient = translate.TranslationServiceClient()
        self.location = "global"
        self.parent = f"projects/{project_id}/locations/{self.location}"

    async def run(self, image: BytesIO | bytes, lang: str):
        if isinstance(image, BytesIO):
            image = image.getvalue()

        image = ImageOps.contain(Image.open(image), (1024, 1024))

        buf = BytesIO()
        image.save(buf, 'PNG')
        buf.seek(0)

        text_annotations = await self.ocr.request(buf.getvalue(), raw=True)

        return await self.replace_text(text_annotations, lang, image)

    async def __call__(self, image: BytesIO, lang: str):
        return await self.run(image, lang)

    @staticmethod
    def calculate_width_height(tl, tr, br, bl):
        width = (max(tr.x, br.x) - min(tl.x, bl.x))
        height = (max(bl.y, br.y) - min(tl.y, tr.y))

        return width, height

    @staticmethod
    def optimize_text_annotations(full_text_annotation: dict) -> list[TextAnnotation]:
        blocks = full_text_annotation['pages'][0]['blocks']

        text_annotation = []  # [ { text: ..., boundingBox: [{x: ..., y: ...}, ...] } ]

        paragraphs = []

        for block in blocks:
            paragraphs.extend(block['paragraphs'])

        for paragraph in paragraphs:
            bound = paragraph['boundingBox']['vertices']

            # Bounding box can have an empty dict, and if it is, x = 0 and y = 0
            tl, tr, br, bl = [BoundingPoly(**x) for x in bound]

            text = ""

            for word in paragraph['words']:
                for symbol in word['symbols']:
                    stext = symbol['text']

                    if prop := symbol.get('property'):
                        break_type = prop['detectedBreak']['type']

                        # https://cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse#breaktype
                        if break_type in ('SPACE', 'SURE_SPACE'):
                            stext += ' '

                    text += stext

            bounding_box = [tl, tr, br, bl]

            data = TextAnnotation(text, bounding_box)

            text_annotation.append(data)

        return text_annotation

    @executor_function
    def replace_text(self, data: dict, lang: str, image: Image):
        full_text_annotation = data["responses"][0]["fullTextAnnotation"]
        text_annotations = self.optimize_text_annotations(full_text_annotation)

        original_text = ""
        translated_text = ""

        for text_annotation in text_annotations:
            text = text_annotation.text

            original_text += f"{text}\n"

            tl, tr, br, bl = text_annotation.bounding_box

            if tl.x >= br.x or tl.y >= br.y:
                raise TranslateOCRError('invalid bounding box')

            translated, source, destination = self.translate_func(text, lang)

            translated_text += f"{translated}\n"

            crop_field = image.crop((tl.x, tl.y, br.x, br.y))
            blurred = crop_field.filter(ImageFilter.GaussianBlur(15))
            image.paste(blurred, (tl.x, tl.y))

            placeholder = Image.new('RGBA', (1024 * 5, 1024), (0, 0, 0, 0))
            draw = ImageDraw.Draw(placeholder)
            draw.text((placeholder.size[0] // 2, 512), translated, 'white', self.font, 'mt', align='center',
                      stroke_width=4, stroke_fill='black')

            width, height = self.calculate_width_height(tl, tr, br, bl)

            bbox = placeholder.getbbox()
            cropped_placeholder = placeholder.crop((bbox[0] - 2, bbox[1] - 2, bbox[2] + 2, bbox[3] + 2))
            fit_field = cropped_placeholder.resize((width, height))

            image.paste(fit_field, (tl.x, tl.y), fit_field)

        return image, original_text.strip(), translated_text.strip()

    def get_supported_languages(self):
        response = self.translate.get_supported_languages(parent=self.parent, display_language_code="en")

        return [{"code": lang.language_code, "name": lang.display_name} for lang in response.languages]

    def translate_func(self, text, dest):
        resp = self.translate.translate_text(
            request={
                "parent": self.parent,
                "contents": [text],
                "mime_type": "text/plain",
                # "source_language_code": source,
                "target_language_code": dest,
            }
        )

        return resp.translations[0].translated_text, resp.translations[0].detected_language_code, dest

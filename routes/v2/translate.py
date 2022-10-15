import random
import string

import boto3
import fastapi  # type: ignore
from fastapi import *
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from core.ocr import OCR
from core.trocr import TranslateOCR
from core.translate import Translate
from core.utils import JSONResponse

import config

router = APIRouter(
    prefix="/translate",
)

translate = Translate(config.GCP_PROJECT_ID)
ocr = OCR(config.GCP_TOKEN)
trocr = TranslateOCR(ocr, config.GCP_PROJECT_ID)
s3 = boto3.client("s3", endpoint_url=config.R2_ENDPOINT_URL, aws_access_key_id=config.R2_ACCESS_KEY_ID,
                  aws_secret_access_key=config.R2_SECRET_ACCESS_KEY)


class InputTools(BaseModel):
    text: str
    language: str
    num_choices: int | None = 1


class DetectLanguage(BaseModel):
    text: str


class TranslateObj(BaseModel):
    text: str
    target_language: str
    source_language: str | None = None


@router.on_event("startup")
async def startup():
    await translate.get_languages(force_call=True, add_to_cache=True)


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v2 translate")


@router.get("/languages")
async def languages():
    langs = translate.get_languages()

    d = {"supportedLanguages": langs}

    return JSONResponse(d, status_code=200)


@router.post("/detect-language")
async def detect_language(item: DetectLanguage):
    text = item.text

    lang = await translate.detect_language(text)

    return JSONResponse(lang, status_code=200)


@router.post("/input-tools")
async def input_tools(item: InputTools):
    text = item.text
    language = item.language
    num_choices = item.num_choices

    if num_choices > 10:
        return JSONResponse({'error': {'code': 400}, 'message': 'num_choices cannot be greater than 10.'},
                            status_code=400)

    tools = await translate.input_tools(text, language, num_choices=num_choices)

    return JSONResponse(tools, status_code=200)


@router.post("/translate")
async def translate_text(item: TranslateObj):
    text = item.text
    target_language = item.target_language
    source_language = item.source_language

    res = await translate.translate(text, target_language, source_language=source_language)

    return JSONResponse(res, status_code=200)


async def render_image(lang, image):
    if not image:
        return JSONResponse({'error': {'code': 400}, 'message': 'Image is required.'}, status_code=400)

    img_bytes = await image.read()

    if not img_bytes:
        return JSONResponse({'error': {'code': 400}, 'message': 'Image is required.'}, status_code=400)

    img, original_text, translated_text = await trocr.run(img_bytes, lang)

    hash = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(10, 50)))

    img.save(f'tmp/{hash}.png', 'PNG')

    s3.upload_file(f'tmp/{hash}.png', 'translate-ocr', f'{hash}.png')

    url = f'https://translate-ocr-cdn.api.yodabot.xyz/{hash}.png'

    return JSONResponse({'url': url, 'originalText': original_text, 'translatedText': translated_text}, status_code=200)


@router.post("/translate")
async def translate_image(lang: str, image: UploadFile = File()):
    return await render_image(lang, image)


@router.post("/translate/image")
async def translate_image(lang: str, image: UploadFile = File()):
    return await render_image(lang, image)


@router.post("/translate/image/render")
async def translate_image_render(lang: str, image: UploadFile = File()):
    return await render_image(lang, image)


@router.get("/translate/image/languages")
async def translate_image_languages():
    langs = translate.get_languages()

    d = {"supportedLanguages": langs}

    return JSONResponse(d, status_code=200)

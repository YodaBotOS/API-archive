import random
import string

import boto3
import fastapi  # type: ignore
from fastapi import *
from fastapi.responses import PlainTextResponse

from core.ocr import OCR
from core.trocr import TranslateOCR
from core.utils import JSONResponse

import config

router = APIRouter(
    prefix="/ocr",
)

ocr = OCR(config.GCP_TOKEN)
trocr = TranslateOCR(ocr, config.GCP_PROJECT_ID)
s3 = boto3.client("s3", endpoint_url=config.R2_ENDPOINT_URL, aws_access_key_id=config.R2_ACCESS_KEY_ID,
                  aws_secret_access_key=config.R2_SECRET_ACCESS_KEY)


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v2 ocr")


@router.post("/execute")
async def execute(image: UploadFile = File()):
    if not image:
        return JSONResponse({'error': {'code': 400}, 'message': 'Image is required.'}, status_code=400)

    img = await image.read()

    if not img:
        return JSONResponse({'error': {'code': 400}, 'message': 'Image is required.'}, status_code=400)

    text = await ocr(img)

    js = {'text': text.strip()}

    return JSONResponse(js, status_code=200)


async def render_image(lang, image):
    if not image:
        return JSONResponse({'error': {'code': 400}, 'message': 'Image is required.'}, status_code=400)

    img_bytes = await image.read()

    if not img_bytes:
        return JSONResponse({'error': {'code': 400}, 'message': 'Image is required.'}, status_code=400)

    img, original_text, translated_text = await trocr.run(img_bytes, lang)

    hash = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(10, 50)))

    img.save(f'tmp/{hash}.png', 'PNG')

    s3.upload_file(f'tmp/{hash}.png', config.R2_BUCKET, f'ocr/{hash}.png')

    url = f'https://{config.R2_HOST}/ocr/{hash}.png'

    return JSONResponse({'url': url, 'originalText': original_text, 'translatedText': translated_text}, status_code=200)


@router.post("/translate/image")
async def translate_image(lang: str, image: UploadFile = File()):
    return await render_image(lang, image)


@router.post("/translate/image/render")
async def translate_image_render(lang: str, image: UploadFile = File()):
    return await render_image(lang, image)


@router.get("/translate/image/languages")
async def translate_image_languages():
    langs = trocr.get_supported_languages()

    d = {"supportedLanguages": langs}

    return JSONResponse(d, status_code=200)


def init_router(app):
    return router

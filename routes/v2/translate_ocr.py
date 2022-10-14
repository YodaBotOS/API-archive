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
    prefix="/translate-ocr",
)

ocr = OCR(config.GCP_TOKEN)
trocr = TranslateOCR(ocr, config.GCP_PROJECT_ID)
s3 = boto3.client("s3", endpoint_url=config.R2_ENDPOINT_URL, aws_access_key_id=config.R2_ACCESS_KEY_ID,
                  aws_secret_access_key=config.R2_SECRET_ACCESS_KEY)


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v2 translate-ocr")


@router.post("/render")
async def render(lang: str, image: UploadFile = File()):
    if not image:
        return JSONResponse({'error': {'code': 400}, 'message': 'Image is required.'}, status_code=400)

    img_bytes = await image.read()

    img = await trocr.run(img_bytes, lang)

    hash = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(10, 50)))

    img.save(f'tmp/{hash}.png', 'PNG')

    s3.upload_file(f'tmp/{hash}.png', 'translate-ocr', f'{hash}.png')

    url = f'https://translate-ocr.api.yodabot.xyz/{hash}.png'

    return JSONResponse({'url': url}, status_code=200)


@router.get("/languages")
async def languages():
    langs = trocr.get_supported_languages()

    res = {"supportedLanguages": langs}

    return JSONResponse(res, status_code=200)

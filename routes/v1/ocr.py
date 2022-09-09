import fastapi  # type: ignore
from fastapi import *
from fastapi.responses import *

from core.ocr import OCR

import config

router = APIRouter(
    prefix="/ocr",
)

ocr = OCR(config.GCP_TOKEN)


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v1 ocr")


@router.post("/execute")
async def execute(image: UploadFile = File()):
    if not image:
        return JSONResponse({'error': {'code': 400}, 'message': 'Image is required.'}, status_code=400)

    img = await image.read()

    text = await ocr(img)

    js = {'text': text.strip()}

    return JSONResponse(js, status_code=200)

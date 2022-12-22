import uuid

import boto3
import fastapi  # type: ignore
from fastapi import *
from fastapi.responses import PlainTextResponse

import config
from core.utils import JSONResponse, StringIntEncoder
from core.image import *

router = APIRouter(
    prefix="/image",
)

s3 = boto3.client("s3", endpoint_url=config.R2_ENDPOINT_URL, aws_access_key_id=config.R2_ACCESS_KEY_ID,
                  aws_secret_access_key=config.R2_SECRET_ACCESS_KEY)
art = GenerateArt(
    (s3, config.R2_BUCKET, config.R2_HOST),
    (config.OPENAI_KEY, config.DREAM_KEY, (config.COMPUTER_VISION_KEYS, config.COMPUTER_VISION_REGION))
)


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v3 image")


@router.post("/generate", response_class=JSONResponse)
async def generate_image(request: Request):
    js = await request.json()

    prompt = js.get("prompt")
    n = js.get("amount", 3)
    size = js.get("size")
    ip = request.headers.get("cf-connecting-ip")  # Cloudflare

    if not ip:
        ip = uuid.uuid4()

    user = str(StringIntEncoder.encode(ip))  # IDK how else to identify user to openai in a better way

    if not prompt:
        return JSONResponse({"error": {"code": 400}, "message": "Missing/invalid prompt in JSON body."}, status_code=400)

    if not n or not isinstance(n, int) or 1 > n or n > 10:
        return JSONResponse({
            "error": {"code": 400},
            "message": "Missing/invalid amount in JSON body. Must be a integer between 1 and 10."
        }, status_code=400)

    size_err = JSONResponse({
        "error": {"code": 400},
        "message": "Missing/invalid size in JSON body. Should be something like \"1024x1024\". Allowed values are "
                   "\"256x256\", \"512x512\", \"1024x1024\""
    }, status_code=400)

    if not size:
        return size_err

    try:
        width, height = size.split("x")

        if not width.isdigit() or not height.isdigit():
            return size_err

        if width != height:
            return size_err

        if width not in ["1024", "512", "256"] or height not in ["1024", "512", "256"]:
            return size_err

        if width == "1024" and height == "1024":
            size = Size.LARGE
        elif width == "512" and height == "512":
            size = Size.MEDIUM
        elif width == "256" and height == "256":
            size = Size.SMALL
    except:
        return size_err

    images = await art.create_image(prompt, n, size=size, user=user)

    return JSONResponse({"generatedImages": images.get_urls(), "type": "classic"}, status_code=200)


@router.post("/generate/variations", response_class=JSONResponse)
async def generate_image_variations(request: Request, file: UploadFile = File()):
    js = await request.json()

    n = js.get("amount", 3)
    size = js.get("size")
    ip = request.headers.get("cf-connecting-ip")  # Cloudflare

    if not ip:
        ip = uuid.uuid4()

    user = str(StringIntEncoder.encode(ip))  # IDK how else to identify user to openai in a better way

    img_file_err = JSONResponse({"error": {"code": 400}, "message": "Missing/invalid image file in request."},
                                status_code=400)

    if not file:
        return img_file_err

    image_file = await file.read()

    if not image_file:
        return img_file_err

    if not n or not isinstance(n, int) or 1 > n or n > 10:
        return JSONResponse({
            "error": {"code": 400},
            "message": "Missing/invalid amount in JSON body. Must be a integer between 1 and 10."
        }, status_code=400)

    size_err = JSONResponse({
        "error": {"code": 400},
        "message": "Missing/invalid size in JSON body. Should be something like \"1024x1024\". Allowed values are "
                   "\"256x256\", \"512x512\", \"1024x1024\""
    }, status_code=400)

    if not size:
        return size_err

    try:
        width, height = size.split("x")

        if not width.isdigit() or not height.isdigit():
            return size_err

        if width != height:
            return size_err

        if width not in ["1024", "512", "256"] or height not in ["1024", "512", "256"]:
            return size_err

        if width == "1024" and height == "1024":
            size = Size.LARGE
        elif width == "512" and height == "512":
            size = Size.MEDIUM
        elif width == "256" and height == "256":
            size = Size.SMALL
    except:
        return size_err

    images = await art.create_image_variations(image_file, n, size=size, user=user)

    return JSONResponse({"generatedImages": images.get_urls(), "type": "variations"}, status_code=200)


@router.post("/generate/style", response_class=JSONResponse)
async def generate_image_with_style(request: Request):
    js = await request.json()

    prompt = js.get("prompt")
    n = js.get("amount", 3)
    style = js.get("style")
    size = js.get("size")

    if not prompt:
        return JSONResponse({"error": {"code": 400}, "message": "Missing/invalid prompt in JSON body."}, status_code=400)

    if not n or not isinstance(n, int) or 1 > n or n > 10:
        return JSONResponse({
            "error": {"code": 400},
            "message": "Missing/invalid amount in JSON body. Must be a integer between 1 and 10."
        }, status_code=400)

    style_err = JSONResponse({
        "error": {"code": 400},
        "message": "Missing/invalid style in JSON body. Take a look at /image/generate/style/available-styles for a "
                   "list of the available styles. You can either provide the name or ID of the style."
    }, status_code=400)

    if not style:
        return style_err

    style = (
        await art.style.get_style(int(style))
        if isinstance(style, int) or (isinstance(style, str) and style.isdigit()) else
        await art.style.get_style_from_name(style, lower=True)
    )

    if not style:
        return style_err

    size_err = JSONResponse({
        "error": {"code": 400},
        "message": "Missing/invalid size in JSON body."
    }, status_code=400)

    if not size:
        return size_err

    try:
        width, height = size.split("x")

        if not width.isdigit() or not height.isdigit():
            return size_err

        width = int(width)
        height = int(height)
    except:
        return size_err

    images = await art.style.generate(prompt, n, width=width, height=height)

    return JSONResponse({"generatedImages": [i.result for i in images], "type": "style"}, status_code=200)


@router.get("/generate/style/available-styles", response_class=JSONResponse)
async def get_available_styles():
    styles = await art.style.get_styles(return_js=True)

    return JSONResponse({"styles": [s for s in styles]}, status_code=200)


@router.post("/analyze", response_class=JSONResponse)
async def analyze_image(file: UploadFile = File()):
    img_file_err = JSONResponse({"error": {"code": 400}, "message": "Missing/invalid image file in request."},
                                status_code=400)

    if not file:
        return img_file_err

    image_file = await file.read()

    if not image_file:
        return img_file_err

    data = await art.analyze(image_file)

    return JSONResponse(data, status_code=200)


def init_router(app):
    return router

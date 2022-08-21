import fastapi  # type: ignore
from fastapi import APIRouter
from fastapi.responses import *

from .music import router as music_router


router = APIRouter()
routes = [
    ("Music", music_router),
]

for name, route in routes:
    router.include_router(route, tags=[name])


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v1")

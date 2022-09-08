import fastapi  # type: ignore
from fastapi import APIRouter
from fastapi.responses import *

from .music import router as music_router
from .lyrics import router as lyrics_router


router = APIRouter()
routes = [
    ("Music", music_router),
    ("Lyrics", lyrics_router)
]

for name, route in routes:
    router.include_router(route, tags=[name])


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v1")

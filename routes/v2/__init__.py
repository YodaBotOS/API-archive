import fastapi  # type: ignore
from fastapi import APIRouter
from fastapi.responses import *

from .music import init_router as music_router
from .lyrics import init_router as lyrics_router
from .chat import init_router as chat_router
from .grammar_correction import init_router as grammar_correction_router
from .study_notes import init_router as study_notes_router
from .ocr import init_router as ocr_router
from .translate import init_router as translate_router
from .translate_ocr import init_router as translate_ocr_router

router = APIRouter(deprecated=True)
routes = [
    ("Music", music_router),
    ("Lyrics", lyrics_router),
    ("Chat", chat_router),
    ("Grammar Correction", grammar_correction_router),
    ("Study Notes", study_notes_router),
    ("OCR", ocr_router),
    ("Translate", translate_router),
    ("Translate OCR", translate_ocr_router),
]


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v2")


@router.get("/version", include_in_schema=False)
async def root():
    return PlainTextResponse("v2")


def init_router(app):
    for name, route in routes:
        router.include_router(route(app), tags=[name])

    return router

import typing

import fastapi  # type: ignore
from fastapi import *
from fastapi.responses import *

from core.study_notes import StudyNotes
import config

router = APIRouter(
    prefix="/study-notes",
)

study_notes = StudyNotes(config.openai_token)


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v1 study-notes")


@router.get("/generate")
async def generate(topic: str, amount: typing.Optional[int] = 5):
    if not topic:
        return JSONResponse({'error': {'code': 400}, 'message': 'Topic is required.'}, status_code=400)

    if 1 > amount or amount > 10:
        return JSONResponse({'error': {'code': 400}, 'message': 'Amount must be at least 1 and lest or equal to 10.'},
                            status_code=400)

    notes = await study_notes(topic, amount)

    js = {'topic': topic, 'amount': amount, 'notes': notes}

    return JSONResponse(js, status_code=200)

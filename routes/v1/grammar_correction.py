import fastapi  # type: ignore
from fastapi import *
from fastapi.responses import *

from core.grammar_correction import GrammarCorrection
import config

router = APIRouter(
    prefix="/grammar-correction",
)

grammar_correction = GrammarCorrection(config.openai_token)


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v1 grammar-correction")


@router.get("/correct")
async def correct(text: str):
    corrected = await grammar_correction(text)

    if corrected == "This is incorrect English. Please try again.":
        return JSONResponse({'error': {'code': 400}, 'message': 'This is incorrect English. Please try again.'},
                            status_code=400)

    js = {'original': text, 'corrected': corrected, 'different': text != corrected}

    return JSONResponse(js, status_code=200)


def init_router(app):
    return router

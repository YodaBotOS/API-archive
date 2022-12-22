import uuid
import typing

import fastapi  # type: ignore
from fastapi import *
from fastapi.responses import *

import config
from core.chat import Chat
from core.utils import JSONResponse
from core.db import Database

router = APIRouter(
    prefix="/chat",
)

db = Database(config.DATABASE_HOST, config.DATABASE_AUTH)
chat = Chat(config.openai_token, db)


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v3 chat")


@router.post("/start")
async def chat_start(id: typing.Optional[str] = None):
    id = str(id or uuid.uuid4())

    if await chat.job_id_present(id):
        return JSONResponse({'error': {'code': 400}, 'message': 'Job ID already exists.'}, status_code=400)

    resp = await chat.start(id)

    return JSONResponse(resp, status_code=200)


@router.post("/custom-start")
async def chat_custom_start(request: Request, id: typing.Optional[str] = None):
    id = str(id or uuid.uuid4())

    if not id.startswith('custom-'):
        id = 'custom-' + id

    if await chat.job_id_present(id):
        return JSONResponse({'error': {'code': 400}, 'message': 'Job ID already exists.'}, status_code=400)

    try:
        js = await request.json()

        prompts: list[tuple[str, str]] = js['prompts']

        next_check = "Human"

        for i, (who, content) in enumerate(prompts):
            content = content.replace('\n', ' ').strip()

            if not content:
                return JSONResponse({'error': {'code': 400}, 'message': 'Invalid prompts.'}, status_code=400)

            prompts[i] = (who, content)

            if who not in ("AI", "User"):
                return JSONResponse({'error': {'code': 400}, 'message': 'Invalid prompts.'}, status_code=400)

            if who == next_check:
                match who:
                    case "Human":
                        next_check = "AI"
                    case "AI":
                        next_check = "Human"
            else:
                return JSONResponse({'error': {'code': 400}, 'message': 'Invalid prompts.'}, status_code=400)
    except:
        return JSONResponse({'error': {'code': 400}, 'message': 'Invalid Body/JSON Format.'}, status_code=400)

    resp = await chat.custom_start(id, prompts)

    return JSONResponse(resp, status_code=200)


@router.get("/status")
async def chat_status(id: str):
    if not await chat.job_id_present(id):
        return JSONResponse({'error': {'code': 404}, 'message': 'Job ID does not exist, stopped or has expired (3 '
                                                                'minutes passed).'}, status_code=404)

    resp = await chat.get(id)

    return JSONResponse(resp, status_code=200)


@router.post("/send")
async def chat_send(id: str, message: str):
    message = message.replace('\n', ' ').replace('Human:', '').replace('AI:', '').strip()

    if not await chat.job_id_present(id):
        return JSONResponse({'error': {'code': 404}, 'message': 'Job ID does not exist, stopped or has expired (3 '
                                                                'minutes passed).'}, status_code=404)

    resp = await chat.respond(id, message)

    return JSONResponse(resp, status_code=200)


@router.get("/get-last-response")
async def chat_get_last_response(id: str):
    if not await chat.job_id_present(id):
        return JSONResponse({'error': {'code': 404}, 'message': 'Job ID does not exist, stopped or has expired (3 '
                                                                'minutes passed).'}, status_code=404)

    resp = await chat.get(id)

    for who, content in reversed(resp['messages']):
        if who == 'AI':
            return JSONResponse({'message': content}, status_code=200)

    return JSONResponse({'message': None}, status_code=200)


@router.delete("/end")
async def chat_end(id: str):
    if not await chat.job_id_present(id):
        return JSONResponse({'error': {'code': 404}, 'message': 'Job ID does not exist, stopped or has expired (3 '
                                                                'minutes passed).'}, status_code=404)

    resp = await chat.stop(id)

    return JSONResponse(resp, status_code=200)


def init_router(app):
    return router

import uuid
import typing

import fastapi  # type: ignore
from fastapi import *
from fastapi.responses import *
from redis import asyncio as aioredis  # type: ignore

from core.chat import Chat

import config

router = APIRouter(
    prefix="/chat",
)

redis = aioredis.Redis(**config.REDIS, db=2)
chat = Chat(config.openai_token, redis)


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v1 chat")


@router.post("/start")
async def chat_start(id: typing.Optional[str] = None):
    id = str(id or uuid.uuid4())

    if chat.job_id_present(id):
        return JSONResponse({'error': {'code': 400}, 'message': 'Job ID already exists.'}, status_code=400)

    resp = await chat.start(id)

    return JSONResponse(resp, status_code=200)


@router.get("/status")
async def chat_status(id: str):
    if not chat.job_id_present(id):
        return JSONResponse({'error': {'code': 404}, 'message': 'Job ID does not exist, stopped or has expired (3 '
                                                                'minutes passed).'}, status_code=404)

    resp = await chat.get(id)

    return JSONResponse(resp, status_code=200)


@router.post("/send")
async def chat_send(id: str, message: str):
    message = message.replace('\n', ' ').replace('Human:', '').replace('AI:', '').strip()

    if not chat.job_id_present(id):
        return JSONResponse({'error': {'code': 404}, 'message': 'Job ID does not exist, stopped or has expired (3 '
                                                                'minutes passed).'}, status_code=404)

    resp = await chat.respond(id, message)

    return JSONResponse(resp, status_code=200)


@router.get("/get-last-response")
async def chat_get_last_response(id: str):
    if not chat.job_id_present(id):
        return JSONResponse({'error': {'code': 404}, 'message': 'Job ID does not exist, stopped or has expired (3 '
                                                                'minutes passed).'}, status_code=404)

    resp = await chat.get(id)

    for who, content in reversed(resp['messages']):
        if who == 'AI':
            return JSONResponse({'message': content}, status_code=200)

    return JSONResponse({'message': None}, status_code=200)


@router.delete("/end")
async def chat_end(id: str):
    if not chat.job_id_present(id):
        return JSONResponse({'error': {'code': 404}, 'message': 'Job ID does not exist, stopped or has expired (3 '
                                                                'minutes passed).'}, status_code=404)

    resp = await chat.stop(id)

    return JSONResponse(resp, status_code=200)

import json
import os
import string
import random
import base64
from typing import *

import boto3
import aiohttp
import fastapi  # type: ignore
from fastapi import *
from fastapi.responses import PlainTextResponse
from redis import asyncio as aioredis  # type: ignore

import config
from core.utils import JSONResponse
from core.genre_classification.src.get_genre import main as get_genre


router = APIRouter(
    prefix="/music",
)

redis = aioredis.Redis(**config.REDIS, db=1)

s3 = boto3.client("s3", region_name=config.S3_BUCKET_REGION, aws_access_key_id=config.S3_AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=config.S3_AWS_SECRET_ACCESS_KEY)


async def get_dolby_io_token(sess):
    url = "https://api.dolby.io/v1/auth/token"

    payload = "grant_type=client_credentials"

    basic = f'{config.DOLBY_IO_APP_KEY}:{config.DOLBY_IO_APP_SECRET}'
    b64 = base64.b64encode(basic.encode()).decode()

    headers = {
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64}"
    }

    async with sess.post(url, data=payload, headers=headers) as resp:
        token_data = await resp.json()
        token = token_data["token_type"] + " " + token_data["access_token"]

    return token


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v2 music")


@router.post("/predict-genre", response_class=JSONResponse)
async def predict_genre(mode: Literal["fast", "best"] = "fast", file: UploadFile = File()):
    """
    Predict the genre of a specific audio file.
    """

    hash = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(10, 50)))

    with open(f"tmp/{hash}.mp3", "wb") as f:
        f.write(await file.read())

    if mode == "fast":
        genres = get_genre([f"tmp/{hash}.mp3"])

        os.remove(f"tmp/{hash}.mp3")

        return JSONResponse(genres)
    elif mode == "best":
        async with aiohttp.ClientSession() as sess:
            token = await get_dolby_io_token(sess)

            s3.upload_file(f"tmp/{hash}.mp3", config.S3_BUCKET, f"v1/music/predict-genre/in/{hash}.mp3")

            os.remove(f"tmp/{hash}.mp3")

            url = "https://api.dolby.com/media/analyze"

            payload = {
                "output": {
                    "auth": {
                        "key": config.S3_AWS_ACCESS_KEY_ID,
                        "secret": config.S3_AWS_SECRET_ACCESS_KEY,
                    },
                    "url": f"s3://{config.S3_BUCKET}/v1/music/predict-genre/out/{hash}.json",
                },
                "input": {
                    "auth": {
                        "key": config.S3_AWS_ACCESS_KEY_ID,
                        "secret": config.S3_AWS_SECRET_ACCESS_KEY,
                    },
                    "url": f"s3://{config.S3_BUCKET}/v1/music/predict-genre/in/{hash}.mp3",
                }
            }

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": token,
            }

            async with sess.post(url, json=payload, headers=headers) as resp:
                data = await resp.json()

                job_id = data['job_id']

                await redis.set(job_id, hash)

                return data
    else:
        os.remove(f"tmp/{hash}.mp3")

        return PlainTextResponse("Invalid mode")


@router.get('/predict-genre/{job_id}')
async def get_predict_genre(job_id: str):
    try:
        hash = (await redis.get(job_id)).decode()
    except KeyError:
        hash = None

    if not hash:
        return JSONResponse({"error": {"code": 404}, "message": "Job ID not found, or has already expired "
                                                                "(3 minutes after success/failed/cancelled)."},
                            status_code=404)

    async with aiohttp.ClientSession() as sess:
        token = await get_dolby_io_token(sess)

        url = "https://api.dolby.com/media/analyze"

        params = {
            "job_id": job_id,
        }

        headers = {
            "Accept": "application/json",
            "Authorization": token,
        }

        async with sess.get(url, params=params, headers=headers) as resp:
            resp.raise_for_status()
            
            data = await resp.json()

            # data status = "running" | "success" | "failed" | "pending" | "cancelled"

            status = data["status"]

            if status in ["success", "failed", "cancelled"]:
                if await redis.ttl(job_id) in [-1, None]:
                    await redis.expire(job_id, 3 * 60)  # 3 minutes

            if status == "Success":
                d = {
                    "status": "success",
                    "progress": 100,
                }

                obj = s3.get_object(Bucket=config.S3_BUCKET, Key=f"v1/music/predict-genre/out/{hash}.json")

                obj_body = obj["Body"].read().decode("utf-8")

                result = json.loads(obj_body)

                result = result['processed_region']['audio']['music']['sections'][0]['genre']

                result_d = {}

                for name, confidence in result:
                    result_d[name] = confidence * 100

                d['result'] = result_d

                return JSONResponse(d)
            else:
                d = {
                    "status": data["status"].lower(),
                    "result": {},
                }

                if prog := data.get("progress") and data['status'] == "Running":
                    d["progress"] = prog

                return JSONResponse(d)

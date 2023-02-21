import json
import os
import string
import random
import base64
import datetime
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
from core.db import Database

router = APIRouter(
    prefix="/music",
)

db = Database(config.DATABASE_HOST, config.DATABASE_AUTH)

s3 = boto3.client("s3", region_name=config.S3_BUCKET_REGION, aws_access_key_id=config.R2_ACCESS_KEY_ID,
                  aws_secret_access_key=config.R2_SECRET_ACCESS_KEY, endpoint_url=config.R2_ENDPOINT_URL)


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

def create_presigned_url(bucket_name, object_name, operation='get_object', expiration=3600):
    return s3.generate_presigned_url(operation,
        Params={'Bucket': bucket_name, 'Key': object_name},
        ExpiresIn=expiration
    )


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v3 music")


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

            s3.upload_file(f"tmp/{hash}.mp3", config.R2_BUCKET, f"predict-genre/input/{hash}.mp3")
            
            input_url = create_presigned_url(config.R2_BUCKET, f"predict-genre/input/{hash}.mp3")
            output_url = create_presigned_url(config.R2_BUCKET, f"predict-genre/output/{hash}.json", operation='put_object', expiration=7200)

            os.remove(f"tmp/{hash}.mp3")

            url = "https://api.dolby.com/media/analyze"

            payload = {
                "output": output_url,
                "input": input_url
            }

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": token,
            }

            async with sess.post(url, json=payload, headers=headers) as resp:
                data = await resp.json()

                job_id = data['job_id']

                await db.query("INSERT INTO predict_genre (job_id, hash) VALUES ($1, $2)", job_id, hash)

                return data
    else:
        os.remove(f"tmp/{hash}.mp3")

        return PlainTextResponse("Invalid mode")


@router.get('/predict-genre/{job_id}')
async def get_predict_genre(job_id: str):
    d = await db.query("SELECT * FROM predict_genre WHERE job_id = $1", job_id)
    d = d.results[0].result[0]
    
    ex_ori = d['expire']
    d['expire'] = datetime.datetime.utcfromtimestamp(d['expire']) if d['expire'] else datetime.datetime.now() + datetime.timedelta(days=1)

    if not d['hash'] or datetime.datetime.utcnow() > d['expire']:
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

            if status.lower() in ["success", "failed", "cancelled"] and not ex_ori:
                expire = int((datetime.datetime.utcnow() + datetime.timedelta(minutes=3)).timestamp()) 

                await db.query("UPDATE predict_genre SET expire = $2 WHERE job_id = $1", expire, job_id)

            if status == "Success":
                d = {
                    "status": "success",
                    "progress": 100,
                }

                obj = s3.get_object(Bucket=config.R2_BUCKET, Key=f"predict-genre/output/{hash}.json")

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
                    "status": status.lower(),
                    "result": {},
                }

                if prog := data.get("progress") and data['status'] == "Running":
                    d["progress"] = prog

                return JSONResponse(d)


def init_router(app):
    return router

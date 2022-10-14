import re
import os
import json
from urllib.parse import quote as safe_text_url

import boto3
import aiohttp
import fastapi  # type: ignore
from fastapi import *
from fastapi.responses import PlainTextResponse
from redis import asyncio as aioredis  # type: ignore

import config

from core.app import JSONResponse
from core.lyrics import Lyrics, Tokens

router = APIRouter(
    prefix="/lyrics",
)

redis = aioredis.Redis(**config.REDIS)

tokens = Tokens(**config.LYRIC_TOKENS)
lyrics = Lyrics(redis, tokens)

s3 = boto3.client("s3", endpoint_url=config.R2_ENDPOINT_URL, aws_access_key_id=config.R2_ACCESS_KEY_ID,
                  aws_secret_access_key=config.R2_SECRET_ACCESS_KEY)
lyric_bucket = 'lyrics-cdn'
cdn_url = 'lyrics-cdn.api.yodabot.xyz'

for i in ['lyric-images', 'shazam-lyrics']:
    try:
        os.mkdir(f'./{i}')
    except:
        continue


@router.get("/", include_in_schema=False)
async def root():
    return PlainTextResponse("Hello World! Version v2 lyrics")


@router.get("/search")
async def search(q: str):
    q = q.replace('+', ' ').strip()

    regex_res = re.findall(r'\(.*\)', q)
    for i in regex_res:
        q = q.replace(i, '')

    if not q:
        return JSONResponse({'error': {'code': 400}, 'message': 'No query provided.'}, status_code=400)

    res = await lyrics.get(q)

    if not res:
        return JSONResponse({'title': None, 'artist': None, 'lyrics': None, 'images': {}}, status_code=404)

    if not os.path.exists(f'./lyric-images/{res.title}-{res.artist}'):
        os.mkdir(f'./lyric-images/{res.title}-{res.artist}')

    if res._images_from_redis and res.images:
        images = res.images
    else:
        db = json.loads(await redis.get(q.lower()))

        if db.get('images'):
            images = db['images']
        else:
            images = {}

            for image_name, url in res.images.items():
                async with aiohttp.ClientSession() as sess:
                    async with sess.get(url) as resp:
                        image_content = await resp.read()

                with open(f'./lyric-images/{res.title}-{res.artist}/{image_name}.jpg', 'wb') as f:
                    f.write(image_content)

                s3.upload_file(
                    f'./lyric-images/{res.title}-{res.artist}/{image_name}.jpg',
                    lyric_bucket,
                    f'lyrics/{res.title}-{res.artist}/{image_name}.jpg'
                )

                x = safe_text_url(res.title + '-' + res.artist)

                images[image_name] = f'lyrics/{x}/{image_name}.jpg'

                os.remove(f'./lyric-images/{res.title}-{res.artist}/{image_name}.jpg')

            try:
                os.remove(f'./lyric-images/{res.title}-{res.artist}')
            except:
                pass

            if images:
                db['images'] = images

                await redis.set(q.lower(), json.dumps(db))

    i = {}

    for name, endpoint in images.items():
        i[name] = f'https://{cdn_url}/{endpoint}'

    title = res.title
    lyric = str(res)
    artist = res.artist

    d = {'title': str(title), 'artist': str(artist), 'lyrics': lyric, 'images': i}

    return JSONResponse(d)

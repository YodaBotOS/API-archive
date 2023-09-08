import os
import json
import asyncio

import sentry_sdk
from fastapi import FastAPI as App
from fastapi.responses import Response

import config

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GOOGLE_CREDENTIALS_PATH

# from .db import init_db
from routes import v1, v2, v3


def setup_sentry():
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=1.0,
    )


def on_startup(app: App):
    async def _():
        # db = await init_db(sync=False)
        #
        # with open('schema.sql', 'r') as f:
        #     query = f.read()
        #
        # async with db.acquire() as conn:
        #     await conn.execute(query)

        pass

    return _


def on_shutdown(app: App):
    async def _():
        # await app.db.close()
        pass

    return _


def make_tmp_dir(app: App):
    try:
        os.mkdir("tmp")
    except FileExistsError:
        pass


def add_routes(app: App):
    routes = [("1", v1.init_router), ("2", v2.init_router), ("3", v3.init_router)]

    latest = app.version.lstrip("latest-")

    for name, route in routes:
        r = route(app)

        if "v" + name == latest:
            app.include_router(r, tags=[f"v{name}"], prefix="/v/latest", include_in_schema=False)
            app.include_router(r, prefix="/api")

        app.include_router(r, tags=[f"v{name}"], prefix=f"/v/{name}",
                           include_in_schema=False)

def add_google_analytics(app: App):
    ga_script = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={code}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', '{code}');
</script>
    """
    
    @app.middleware("http")
    async def insert_js(request, call_next):
        path = request.scope["path"]  # get the request route
        response = await call_next(request)
        
        try:
            response_body = ""
            async for chunk in response.body_iterator:
                response_body += chunk.decode()
    
            charset_tag = '<meta charset="utf-8">'
            color_scheme_tag = '<meta name="color-scheme" content="light dark">'
            if charset_tag in response_body:
                response_body = response_body.replace(charset_tag, charset_tag + ga_script.format(code=config.GOOGLE_ANALYTICS_CODE))
            elif color_scheme_tag in response_body:
                response_body = response_body.replace(color_scheme_tag, color_scheme_tag + ga_script.format(code=config.GOOGLE_ANALYTICS_CODE))
            else:
                response_body = response_body.replace('<head>', '<head>\n' + ga_script.format(code=config.GOOGLE_ANALYTICS_CODE))
    
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        except:
            return response


def init_database(app: App):
    # app.db = init_db(sync=True)
    pass


def callback(app: App):
    funcs = (init_database, add_routes, make_tmp_dir, add_google_analytics)

    for func in funcs:
        func(app)

    return app

import os
import json

import sentry_sdk
from fastapi import FastAPI as App
from fastapi.responses import Response

import config
from routes import v1, v2


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
        pass

    return _


def on_shutdown(app: App):
    async def _():
        pass

    return _


def make_tmp_dir(app: App):
    try:
        os.mkdir("tmp")
    except FileExistsError:
        pass


def set_envs(app: App):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GOOGLE_CREDENTIALS_PATH


def add_routes(app: App):
    routes = [("1", v1.router), ("2", v2.router),]

    latest = app.version.lstrip("latest-")

    for name, route in routes:
        if "v" + name == latest:
            app.include_router(route, tags=[f"v{name}"], prefix="/v/latest", include_in_schema=False)
            app.include_router(route, prefix="/api")

        app.include_router(route, tags=[f"v{name}"], prefix=f"/v/{name}",
                           include_in_schema=False)


def callback(app: App):
    funcs = (add_routes, make_tmp_dir, set_envs,)

    for func in funcs:
        func(app)

    return app

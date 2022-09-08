import os

from fastapi import FastAPI as App
from routes import v1


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


def add_routes(app: App):
    routes = [("1", v1.router), ]

    latest = app.version.lstrip("latest-")

    for name, route in routes:
        if "v" + name == latest:
            app.include_router(route, tags=[f"v{name}"], prefix="/v/latest", include_in_schema=False)
            app.include_router(route, prefix="/api")

        app.include_router(route, tags=[f"v{name}"], prefix=f"/v/{name}",
                           include_in_schema=False)


def callback(app: App):
    funcs = (add_routes, make_tmp_dir,)

    for func in funcs:
        func(app)

    return app

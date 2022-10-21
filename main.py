import fastapi  # type: ignore
from fastapi import FastAPI as App
from fastapi.responses import *
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from core.app import callback, on_startup, on_shutdown, setup_sentry

setup_sentry()

app = App(
    title="Yoda API",
    description="A public API hosted by YodaBotOS. [Open-Sourced at GitHub](https://github.com/YodaBotOS/API)",
    version="latest-v2",
    redoc_url=None,
    docs_url=None,
    openapi_url="/assets/openapi.json",
)
app = callback(app)
app.add_event_handler("startup", on_startup(app))
app.add_event_handler("shutdown", on_shutdown(app))

app.mount("/assets", StaticFiles(directory="assets"), name="assets")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://api.yodabot.xyz/assets/transparent-yoda.png"
    }

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/docs", include_in_schema=False)
async def docs():
    return get_redoc_html(openapi_url="/assets/openapi.json", title=app.title,
                          redoc_favicon_url="/favicon.ico")


@app.get("/playground", include_in_schema=False)
async def playground():
    return get_swagger_ui_html(openapi_url="/assets/openapi.json", title=f"{app.title} - Playground",
                               swagger_favicon_url="/favicon.ico")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("assets/transparent-favicon.ico")


@app.get("/_health_check", include_in_schema=False)
async def health_check():
    return PlainTextResponse("OK")

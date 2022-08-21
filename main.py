import fastapi  # type: ignore
from fastapi import FastAPI as App
from fastapi.responses import *

from core.app import callback, on_startup, on_shutdown

app = App(
    title="Yoda API",
    description="A public API hosted by YodaBotOS.",
    version="latest-v1",
    redoc_url="/docs",
    docs_url="/playground",
    openapi_url="/assets/openapi.json",
)
app = callback(app)
app.add_event_handler("startup", on_startup(app))
app.add_event_handler("shutdown", on_shutdown(app))


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("assets/transparent-favicon.ico")

from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from src.api.v1 import api_router
from src.core.config import get_settings

app = FastAPI(title="API Login", version="0.1.0")
settings = get_settings()

origins = [str(url) for url in settings.cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(api_router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

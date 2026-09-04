from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.v1 import api_router
from src.core.config import get_settings
from src.core.exceptions import AppError

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.version)

origins = [str(url) for url in settings.cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    mapping = {
        "UserNotFoundError": status.HTTP_404_NOT_FOUND,
        "UserAlreadyExistsError": status.HTTP_409_CONFLICT,
        "InvalidCredentialsError": status.HTTP_401_UNAUTHORIZED,
        "UnauthorizedError": status.HTTP_403_FORBIDDEN,
        "InvalidTokenError": status.HTTP_401_UNAUTHORIZED,
        "TokenExpiredError": status.HTTP_401_UNAUTHORIZED,
    }
    code = mapping.get(exc.__class__.__name__, status.HTTP_400_BAD_REQUEST)
    return JSONResponse(status_code=code, content={"detail": str(exc)})


# API routes versionadas
app.include_router(api_router)

# Alias legado sem prefixo para compatibilidade com testes antigos
from src.api.v1.endpoints.auth import router as auth_router  # noqa: E402

app.include_router(auth_router)

# Static files (frontend demo)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running", "version": settings.version}


from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scholaris.api.routes import router
from scholaris.config import load_config
from scholaris.utils.logging import setup_logging

config = load_config()
logger = setup_logging(config.app.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("application_starting")
    yield
    logger.info("application_shutting_down")


app = FastAPI(
    title="Scholaris API",
    description="Academic Knowledge Graph QA Assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "Scholaris API",
        "version": "0.1.0",
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "scholaris.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

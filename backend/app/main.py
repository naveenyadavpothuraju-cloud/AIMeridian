"""AIMeridian FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    # TODO Phase 1h: start APScheduler here
    yield
    # TODO Phase 1h: shutdown APScheduler here


app = FastAPI(
    title="AIMeridian API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Health check endpoint used by Railway and uptime monitors."""
    return {"status": "ok", "version": "0.1.0"}

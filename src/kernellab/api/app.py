"""FastAPI application factory for Kernel Lab."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from kernellab import __version__


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle."""
    from kernellab.persistence.database import DatabaseManager

    db = DatabaseManager()
    db.create_tables()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Kernel Lab API",
        version=__version__,
        description="A reproducible laboratory for kernel and driver development.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    from kernellab.api.routes import health, jobs, labs

    app.include_router(health.router)
    app.include_router(labs.router, prefix="/api/v1")
    app.include_router(jobs.router, prefix="/api/v1")

    return app


app = create_app()

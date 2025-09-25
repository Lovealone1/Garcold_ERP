import time
import json
from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.v1_0.v1_router import v1_router
from app.app_containers import ApplicationContainer  
from app.utils.database import async_session  

PREFIX = "/sales-api"

def create_app() -> FastAPI:
    """FastAPI configuration for the Sales System."""

    container = ApplicationContainer()
    container.db_session.override(async_session)

    app = FastAPI(
        openapi_url=f"{PREFIX}/openapi.json",
        docs_url=f"{PREFIX}/docs",
        redoc_url=f"{PREFIX}/redoc",
        title="Sales Management API",
        description="API to manage sales, products, clients and utilities in the sales system.",
        lifespan=lifespan,
    )
    app.container = container
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    base_router = APIRouter(prefix=PREFIX)
    base_router.include_router(v1_router)

    @base_router.get("/")
    @base_router.get("/ready")
    async def ready():
        return {"message": "Sales API Server is running"}

    app.include_router(base_router)
    return app

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.container.init_resources()
    yield

app = create_app()

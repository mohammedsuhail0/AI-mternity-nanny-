from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import init_db, close_db
from app.db.seed import seed_demo_data
from app.api.auth import router as auth_router
from app.api.companion import router as companion_router
from app.api.dashboard import router as dashboard_router
from app.api.patients import router as patients_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    await seed_demo_data()
    yield
    await close_db()


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(
        settings,
        "ALLOWED_ORIGINS",
        ["http://localhost:3000", "http://127.0.0.1:3000"],
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(companion_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(patients_router, prefix=settings.API_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}

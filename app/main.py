from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.orchestrator.routes import router as orchestrator_router
from app.backend.routes_drafts import router as drafts_router
from app.devops.health import router as health_router
from app.db.base import engine, run_migrations

def create_app() -> FastAPI:
    app = FastAPI(
        title="Agentic Dev Team",
        description="Multi-agent web development system",
        version="1.0.0"
    )
    
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    if os.getenv("RUN_DB_MIGRATIONS") == "1":
        run_migrations()
    
    app.include_router(orchestrator_router, prefix="/intake", tags=["orchestrator"])
    app.include_router(drafts_router, prefix="/v1", tags=["drafts"])
    app.include_router(health_router, tags=["health"])
    
    return app

app = create_app()

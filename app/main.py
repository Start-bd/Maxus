"""
FastAPI Application Entry Point for Manus Agent System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.db.database import create_tables
from app.api.routes import router
from app.services.llm_service import LLMService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Manus Agent System...")
    # Initialize database tables
    create_tables()
    # Initialize LLM service and attach to app state
    app.state.llm_service = LLMService()
    logger.info("Manus Agent System started successfully")
    yield
    logger.info("Shutting down Manus Agent System...")


app = FastAPI(
    title="Manus Agent System",
    description="Multi-agent system for content automation, news aggregation and SEO optimization",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "running",
        "service": "Manus Agent System",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "manus-agent"}

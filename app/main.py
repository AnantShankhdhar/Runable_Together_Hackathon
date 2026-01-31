"""
Industrial Maintenance Intelligence API

FastAPI application for converting unstructured maintenance documents
into structured, searchable reliability intelligence.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .database import init_db
from .routes import documents_router, failures_router, equipment_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("🚀 Starting Maintenance Intelligence API...")
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Industrial Maintenance Intelligence API

Transform unstructured maintenance documents into decision-ready reliability intelligence.

### Core Features

- **Document Processing**: Upload work orders, failure reports, equipment logs
- **AI Extraction**: Claude Sonnet extracts structured data from free text
- **Semantic Search**: Find similar past failures using vector embeddings
- **Failure Analytics**: Track patterns, trends, and recurring issues
- **Equipment Intelligence**: Monitor reliability metrics per asset

### Cost Optimization

- Extraction caching to avoid reprocessing
- Batch embedding for reduced API calls
- Configurable processing thresholds
    """,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents_router)
app.include_router(failures_router)
app.include_router(equipment_router)


@app.get("/", tags=["Health"])
async def root():
    """API root - health check"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_services": {
            "claude": "configured" if settings.ANTHROPIC_API_KEY else "not_configured",
            "openai_embeddings": "configured" if settings.OPENAI_API_KEY else "not_configured",
        }
    }


@app.get("/config", tags=["Health"])
async def get_config():
    """Get current configuration (non-sensitive)"""
    return {
        "claude_model": settings.CLAUDE_MODEL,
        "embedding_model": settings.OPENAI_EMBEDDING_MODEL,
        "embedding_dimension": settings.OPENAI_EMBEDDING_DIMENSION,
        "embedding_batch_size": settings.EMBEDDING_BATCH_SIZE,
        "extraction_cache_ttl_days": settings.EXTRACTION_CACHE_TTL_DAYS,
    }


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )

"""
LLM Lab - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.api.routes import experiments, responses, metrics, export
from app.core.config import settings
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events: startup and shutdown"""
    # Initialize database
    init_db()
    yield
    # Cleanup if needed


app = FastAPI(
    title="LLM Lab API",
    description="Experimental console for analyzing LLM parameter effects",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
# Filter out regex patterns from allow_origins and use allow_origin_regex instead
cors_origins = [origin for origin in settings.CORS_ORIGINS if not "*" in origin]
cors_origin_regex = r"https://.*\.vercel\.app" if any("*" in origin for origin in settings.CORS_ORIGINS) else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(experiments.router, prefix="/api/experiments", tags=["experiments"])
app.include_router(responses.router, prefix="/api/responses", tags=["responses"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(export.router, prefix="/api/export", tags=["export"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "LLM Lab API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

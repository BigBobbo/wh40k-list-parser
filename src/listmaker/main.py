"""FastAPI application for Warhammer 40K List Builder."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database.connection import init_db
from .features.api.routers import army_parser, datasheets, factions, lists

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="A web-based army list builder for Warhammer 40K 10th Edition",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.version,
        "docs": f"{settings.api_prefix}/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


# Include routers
app.include_router(factions.router, prefix=settings.api_prefix)
app.include_router(datasheets.router, prefix=settings.api_prefix)
app.include_router(lists.router, prefix=settings.api_prefix)
app.include_router(army_parser.router, prefix=settings.api_prefix)

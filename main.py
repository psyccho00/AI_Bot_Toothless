import anyio._backends._asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings
from database.connection import init_db
from routes.profile_routes import router as profile_router
from routes.app_routes import router as app_router

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Your Personal AI Health Companion",
    version=settings.APP_VERSION
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static frontend assets
app.mount("/app", StaticFiles(directory="frontend", html=True), name="static")

# Mount API Routers
app.include_router(profile_router)
app.include_router(app_router)

@app.on_event("startup")
def startup_event():
    """Run database table setups and migrations on startup"""
    init_db()
    print("[OK] Database initialized and migrations successfully verified")
    print(f"[Toothless] Welcome to {settings.APP_NAME}!")

@app.get("/")
def root():
    """Root endpoint for status inspection"""
    return {
        "message": f"🐉 Welcome to {settings.APP_NAME} - Your AI Health Assistant",
        "version": settings.APP_VERSION,
        "description": "Normalized multi-user companion API supporting multi-provider AI.",
        "endpoints": {
            "app_interface": "/app",
            "profile_selection": "/users/profiles",
            "api_documentation": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

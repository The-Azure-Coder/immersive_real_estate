import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.v1.router import router as api_router

app = FastAPI(title="Immersive Real Estate API", version="1.0.0")

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Serve uploaded files if using local storage
if not settings.USE_S3:
    # Ensure the upload directory exists
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.LOCAL_STORAGE_PATH), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Welcome to Immersive Real Estate API"}

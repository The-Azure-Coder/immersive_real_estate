from fastapi import APIRouter
from app.api.v1.endpoints import auth, properties, professionals

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(properties.router, prefix="/properties", tags=["Properties"])
router.include_router(professionals.router, prefix="/professionals", tags=["Professionals"])

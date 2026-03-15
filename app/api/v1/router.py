from fastapi import APIRouter
from app.api.v1.endpoints import auth, properties, professionals, favorites, messages, floor_plans

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(properties.router, prefix="/properties", tags=["Properties"])
router.include_router(professionals.router, prefix="/professionals", tags=["Professionals"])
router.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])
router.include_router(messages.router, prefix="/messages", tags=["Messages"])
router.include_router(floor_plans.router, prefix="/floor-plans", tags=["Floor Plans"])

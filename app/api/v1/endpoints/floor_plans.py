from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.v1.endpoints.deps import get_db
from app.models.floor_plan import FloorPlan
from app.models.professional import Professional
from app.models.user import User
from app.schemas.floor_plan import FloorPlanOut

router = APIRouter()

@router.get("/", response_model=List[FloorPlanOut])
def list_floor_plans(db: Session = Depends(get_db)):
    plans = db.query(FloorPlan).all()
    results = []
    for plan in plans:
        # Get architect name
        prof = db.query(Professional).filter(Professional.id == plan.professional_id).first()
        user = db.query(User).filter(User.id == prof.user_id).first() if prof else None
        
        plan_dict = {
            "id": plan.id,
            "title": plan.title,
            "description": plan.description,
            "price": plan.price,
            "sqft": plan.sqft,
            "bedrooms": plan.bedrooms,
            "bathrooms": plan.bathrooms,
            "style": plan.style,
            "image_url": plan.image_url,
            "file_url": plan.file_url,
            "created_at": plan.created_at,
            "professional_id": plan.professional_id,
            "architect_name": user.full_name if user else "Unknown Architect"
        }
        results.append(plan_dict)
    return results

@router.get("/{plan_id}", response_model=FloorPlanOut)
def get_floor_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(FloorPlan).filter(FloorPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Floor plan not found")
    
    prof = db.query(Professional).filter(Professional.id == plan.professional_id).first()
    user = db.query(User).filter(User.id == prof.user_id).first() if prof else None
    
    plan.architect_name = user.full_name if user else "Unknown Architect"
    return plan

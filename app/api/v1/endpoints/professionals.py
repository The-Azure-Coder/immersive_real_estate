from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.v1.endpoints.deps import get_db, get_current_user
from app.models.user import User
from app.models.professional import Professional
from app.schemas.professional import ProfessionalCreate, ProfessionalOut

router = APIRouter()

@router.get("/", response_model=List[ProfessionalOut])
def list_professionals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    professionals = db.query(Professional).offset(skip).limit(limit).all()
    return professionals

@router.post("/", response_model=ProfessionalOut, status_code=status.HTTP_201_CREATED)
def create_professional(
    professional_in: ProfessionalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if professional profile already exists
    db_prof = db.query(Professional).filter(Professional.user_id == current_user.id).first()
    if db_prof:
        raise HTTPException(status_code=400, detail="Professional profile already exists")
    
    new_prof = Professional(
        user_id=current_user.id,
        **professional_in.dict()
    )
    db.add(new_prof)
    db.commit()
    db.refresh(new_prof)
    return new_prof

@router.get("/{prof_id}", response_model=ProfessionalOut)
def get_professional(prof_id: int, db: Session = Depends(get_db)):
    prof = db.query(Professional).filter(Professional.id == prof_id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Professional not found")
    return prof

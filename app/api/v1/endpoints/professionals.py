from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.v1.endpoints.deps import get_db, get_current_user
from app.models.user import User
from app.models.professional import Professional
from app.schemas.professional import ProfessionalCreate, ProfessionalOut
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationMetadata

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
def list_professionals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    total_profs = db.query(Professional).count()
    professionals = db.query(Professional).offset(skip).limit(limit).all()
    
    page = (skip // limit) + 1
    total_pages = (total_profs + limit - 1) // limit
    
    return PaginatedResponse(
        success=True,
        data={"professionals": [ProfessionalOut.model_validate(p) for p in professionals]},
        pagination=PaginationMetadata(
            page=page,
            limit=limit,
            totalPages=total_pages,
            totalItems=total_profs,
            hasNext=page < total_pages,
            hasPrev=page > 1
        )
    )

@router.post("/", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
def create_professional(
    professional_in: ProfessionalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if professional profile already exists
    db_prof = db.query(Professional).filter(Professional.user_id == current_user.id).first()
    if db_prof:
        raise HTTPException(
            status_code=400, 
            detail={
                "success": False,
                "error": {
                    "code": "ALREADY_EXISTS",
                    "message": "Professional profile already exists"
                }
            }
        )
    
    new_prof = Professional(
        user_id=current_user.id,
        **professional_in.dict()
    )
    db.add(new_prof)
    db.commit()
    db.refresh(new_prof)
    
    return BaseResponse(
        success=True,
        message="Professional profile created successfully",
        data=ProfessionalOut.model_validate(new_prof)
    )

@router.get("/{prof_id}", response_model=BaseResponse)
def get_professional(prof_id: int, db: Session = Depends(get_db)):
    prof = db.query(Professional).filter(Professional.id == prof_id).first()
    if not prof:
        raise HTTPException(
            status_code=404, 
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Professional profile not found"
                }
            }
        )
    return BaseResponse(
        success=True,
        data=ProfessionalOut.model_validate(prof)
    )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.v1.endpoints.deps import get_db, get_current_user
from app.models.user import User
from app.models.favorite import Favorite
from app.models.property import Property
from app.schemas.favorite import FavoriteCreate, FavoriteOut

router = APIRouter()

@router.get("/", response_model=List[FavoriteOut])
def list_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    return favorites

@router.post("/", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
def add_favorite(
    favorite_in: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if property exists
    property_obj = db.query(Property).filter(Property.id == favorite_in.property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Check if already favorited
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.property_id == favorite_in.property_id
    ).first()
    if existing:
        return existing

    favorite = Favorite(
        user_id=current_user.id,
        property_id=favorite_in.property_id
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.property_id == property_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(favorite)
    db.commit()
    return None

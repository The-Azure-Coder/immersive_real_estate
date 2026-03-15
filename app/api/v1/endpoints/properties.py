from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List
from app.api.v1.endpoints.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyOut, PropertyUpdate
from app.services.storage import upload_file
from app.services.nanobanana import generate_3d_model
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationMetadata

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
def list_properties(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    total_properties = db.query(Property).count()
    properties = db.query(Property).offset(skip).limit(limit).all()
    
    page = (skip // limit) + 1
    total_pages = (total_properties + limit - 1) // limit
    
    return PaginatedResponse(
        success=True,
        data={"properties": [PropertyOut.model_validate(p) for p in properties]},
        pagination=PaginationMetadata(
            page=page,
            limit=limit,
            totalPages=total_pages,
            totalItems=total_properties,
            hasNext=page < total_pages,
            hasPrev=page > 1
        )
    )

@router.post("/", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    title: str = Form(...),
    description: str = Form(None),
    location: str = Form(...),
    price: float = Form(...),
    land_size: float = Form(...),
    image: UploadFile = File(...),
    current_user: User = Depends(require_role("owner")),
    db: Session = Depends(get_db)
):
    # Upload image
    image_url = await upload_file(image, folder="property-images")

    # Create property record
    property_obj = Property(
        owner_id=current_user.id,
        title=title,
        description=description,
        location=location,
        price=price,
        land_size=land_size,
        image_url=image_url
    )
    db.add(property_obj)
    db.commit()
    db.refresh(property_obj)

    # Trigger 3D model generation
    model_url = await generate_3d_model(image_url)
    if model_url:
        property_obj.model_3d_url = model_url
        property_obj.is_model_generated = True
        db.commit()
        db.refresh(property_obj)

    return BaseResponse(
        success=True,
        message="Property created successfully",
        data=PropertyOut.model_validate(property_obj)
    )

@router.get("/{property_id}", response_model=BaseResponse)
def get_property(property_id: int, db: Session = Depends(get_db)):
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=404, 
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Property not found"
                }
            }
        )
    return BaseResponse(
        success=True,
        data=PropertyOut.model_validate(property_obj)
    )

@router.put("/{property_id}", response_model=BaseResponse)
def update_property(
    property_id: int,
    property_update: PropertyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=404, 
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Property not found"
                }
            }
        )
    
    if property_obj.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=403, 
            detail={
                "success": False,
                "error": {
                    "code": "ACCESS_DENIED",
                    "message": "Not authorized to update this property"
                }
            }
        )
    
    update_data = property_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(property_obj, key, value)
    
    db.commit()
    db.refresh(property_obj)
    return BaseResponse(
        success=True,
        message="Property updated successfully",
        data=PropertyOut.model_validate(property_obj)
    )

@router.delete("/{property_id}", response_model=BaseResponse)
def delete_property(
    property_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=404, 
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Property not found"
                }
            }
        )
    
    if property_obj.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=403, 
            detail={
                "success": False,
                "error": {
                    "code": "ACCESS_DENIED",
                    "message": "Not authorized to delete this property"
                }
            }
        )
    
    db.delete(property_obj)
    db.commit()
    return BaseResponse(
        success=True,
        message="Property deleted successfully"
    )

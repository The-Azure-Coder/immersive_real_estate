# Backend Team — Hackathon Implementation Plan
**24-Hour Sprint · FastAPI + PostgreSQL · Version 1.0**

> Reference: `Master_Implementation_Plan_upd.md` — Backend sections (4, 5, 6, 7, 8, 9, 10, 18)
>
> **Coordinate with Frontend team on:** API contract (Section A below), CORS origin, and base URL.

---

## Team Goal

Deliver a working REST API that the frontend can connect to live. All endpoints must return real data from PostgreSQL by demo time. External services (S3, Nanobanana) use local/mock fallbacks during the hackathon.

---

## A. API Contract (Share with Frontend Team at Hour 0)

Base URL: `http://localhost:8000`

| Endpoint | Method | Auth | Priority |
|---|---|---|---|
| `/api/v1/auth/register` | POST | No | P1 |
| `/api/v1/auth/login` | POST | No | P1 |
| `/api/v1/properties/` | GET | No | P1 |
| `/api/v1/properties/` | POST (multipart) | Bearer | P1 |
| `/api/v1/properties/{id}` | GET | No | P1 |
| `/api/v1/properties/{id}/model-status` | GET | No | P1 |
| `/api/v1/professionals/` | GET | No | P2 |
| `/api/v1/professionals/` | POST | Bearer | P2 |
| `/api/v1/professionals/{id}` | GET | No | P2 |
| `/api/v1/properties/{id}/generate-3d` | POST | Bearer | P2 |
| `/api/v1/properties/{id}/walkthrough-config` | GET / PUT | No / Bearer | P3 |

**Auth header format:** `Authorization: Bearer <jwt_token>`

**Token response format:**
```json
{ "access_token": "...", "token_type": "bearer" }
```

**Property response format (PropertyOut):**
```json
{
  "id": 1,
  "title": "Modern Cottage",
  "description": "...",
  "location": "Kingston, Jamaica",
  "price": 250000,
  "land_size": 150,
  "image_url": "/uploads/images/abc123.jpg",
  "images": [
    { "url": "/uploads/images/abc123.jpg", "image_type": "exterior_front" }
  ],
  "model_3d_url": null,
  "model_3d_status": "pending",
  "is_model_generated": false,
  "owner_id": 1,
  "created_at": "2026-03-14T10:00:00"
}
```

---

## B. Project Structure

```
realestate-api/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── property.py
│   │   └── professional.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── property.py
│   │   └── professional.py
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py
│   │   │   ├── properties.py
│   │   │   ├── professionals.py
│   │   │   └── deps.py
│   │   └── router.py
│   └── services/
│       ├── nanobanana.py
│       └── storage.py
├── alembic/
├── .env
└── requirements.txt
```

---

## C. Environment Setup (`.env`)

```env
DATABASE_URL=postgresql://postgres:password@localhost/realestate
SECRET_KEY=hackathon-secret-key-change-in-prod
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
NANOBANANA_API_KEY=your-key-or-leave-blank-for-mock
USE_S3=false
LOCAL_STORAGE_PATH=./uploads
```

---

## D. Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic \
            python-multipart python-jose[cryptography] \
            passlib[bcrypt] httpx python-dotenv pillow piexif pytest httpx
```

---

## E. 24-Hour Timeline

### Hour 0–1 | Setup & API Contract

**Tasks:**
- [ ] Create project folder, venv, install deps
- [ ] Create `.env` from template above
- [ ] Create PostgreSQL database: `createdb realestate`
- [ ] Share API contract (Section A) with frontend team
- [ ] Agree on CORS origin (`http://localhost:3000`)

**Deliverable:** Project runs `uvicorn app.main:app --reload` without errors

---

### Hour 1–3 | Core Config + Database

**`app/core/config.py`:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    NANOBANANA_API_KEY: str = ""
    USE_S3: bool = False
    LOCAL_STORAGE_PATH: str = "./uploads"
    class Config:
        env_file = ".env"

settings = Settings()
```

**`app/core/database.py`:**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**`app/core/security.py`:**
```python
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def get_password_hash(password): return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

---

### Hour 3–5 | User Model + Auth Endpoints

**`app/models/user.py`:**
```python
from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    buyer = "buyer"
    owner = "owner"
    architect = "architect"
    professional = "professional"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.buyer)
    is_active = Column(Boolean, default=True)
```

**`app/schemas/user.py`:**
```python
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.buyer

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    class Config: from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
```

**`app/api/v1/endpoints/auth.py`:**
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role
    )
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}
```

**`app/api/v1/endpoints/deps.py`:**
```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user = db.query(User).filter(User.id == int(payload["sub"])).first()
        if not user: raise HTTPException(401, "User not found")
        return user
    except JWTError:
        raise HTTPException(401, "Invalid token")

def require_role(*roles: str):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value not in roles:
            raise HTTPException(403, "Insufficient permissions")
        return current_user
    return checker
```

**Test auth is working:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@test.com","password":"password123","full_name":"Test User","role":"owner"}'
```

---

### Hour 5–9 | Property Model + CRUD + Image Upload

**`app/models/property.py`:**
```python
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ModelStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    complete = "complete"
    failed = "failed"

class ImageType(str, enum.Enum):
    exterior_front = "exterior_front"
    exterior_back = "exterior_back"
    exterior_left = "exterior_left"
    exterior_right = "exterior_right"
    interior_living = "interior_living"
    interior_bedroom = "interior_bedroom"
    interior_kitchen = "interior_kitchen"
    aerial = "aerial"
    other = "other"

class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    location = Column(String)
    price = Column(Float)
    land_size = Column(Float)
    image_url = Column(String)           # cover image
    model_3d_url = Column(String, nullable=True)
    model_3d_status = Column(SAEnum(ModelStatus), default=ModelStatus.pending)
    is_model_generated = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete")
    walkthrough_config = relationship("PropertyWalkthroughConfig", back_populates="property", uselist=False)

class PropertyImage(Base):
    __tablename__ = "property_images"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    url = Column(String, nullable=False)
    image_type = Column(SAEnum(ImageType), default=ImageType.other)
    sort_order = Column(Integer, default=0)
    property = relationship("Property", back_populates="images")

class PropertyWalkthroughConfig(Base):
    __tablename__ = "property_walkthrough_configs"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), unique=True)
    spawn_position = Column(JSON, default={"x": 0, "y": 1.7, "z": 0})
    hotspots = Column(JSON, default=[])
    model_scale = Column(Float, default=1.0)
    floor_count = Column(Integer, default=1)
    property = relationship("Property", back_populates="walkthrough_config")
```

**`app/services/storage.py`** (local only for hackathon):
```python
import os, uuid, shutil
from fastapi import UploadFile
from app.core.config import settings

def save_upload(file: UploadFile, folder: str = "images") -> str:
    dest_dir = os.path.join(settings.LOCAL_STORAGE_PATH, folder)
    os.makedirs(dest_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "file.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(dest_dir, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return f"/uploads/{folder}/{filename}"
```

**`app/services/nanobanana.py`** (mock for hackathon):
```python
import httpx, asyncio
from app.core.config import settings

# Set MOCK_3D=true in .env to skip real API during hackathon
MOCK_3D = not bool(settings.NANOBANANA_API_KEY)

async def generate_building_3d_model(images: list[dict]) -> dict | None:
    if MOCK_3D:
        await asyncio.sleep(2)  # simulate delay
        # Return a demo GLB URL (use a public sample GLB for the demo)
        return {
            "model_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Box/glTF-Binary/Box.glb",
            "job_id": "mock-job-123"
        }
    payload = {
        "images": images, "format": "glb",
        "model_type": "building", "optimize": True, "output_scale": "metric"
    }
    headers = {"Authorization": f"Bearer {settings.NANOBANANA_API_KEY}"}
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post("https://api.nanobanana.ai/v1/generate-3d", json=payload, headers=headers)
        r.raise_for_status()
        return r.json()
```

**`app/api/v1/endpoints/properties.py`:**
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import asyncio
from app.core.database import get_db
from app.api.v1.endpoints.deps import get_current_user, require_role
from app.models.property import Property, PropertyImage, PropertyWalkthroughConfig, ModelStatus, ImageType
from app.services.storage import save_upload
from app.services.nanobanana import generate_building_3d_model

router = APIRouter(prefix="/properties", tags=["properties"])

def run_3d_generation(property_id: int, images: list[dict], db: Session):
    """Background task: generate 3D model and update DB"""
    import asyncio
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop: return
    prop.model_3d_status = ModelStatus.processing
    db.commit()
    try:
        result = asyncio.run(generate_building_3d_model(images))
        if result:
            prop.model_3d_url = result["model_url"]
            prop.model_3d_status = ModelStatus.complete
            prop.is_model_generated = True
            # Create default walkthrough config
            if not prop.walkthrough_config:
                config = PropertyWalkthroughConfig(property_id=property_id)
                db.add(config)
    except Exception as e:
        prop.model_3d_status = ModelStatus.failed
        print(f"3D generation failed: {e}")
    db.commit()

@router.get("/")
def list_properties(db: Session = Depends(get_db)):
    return db.query(Property).filter(Property.is_approved == True).all()

@router.get("/{id}")
def get_property(id: int, db: Session = Depends(get_db)):
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop: raise HTTPException(404, "Property not found")
    return prop

@router.get("/{id}/model-status")
def get_model_status(id: int, db: Session = Depends(get_db)):
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop: raise HTTPException(404, "Property not found")
    return {
        "status": prop.model_3d_status.value if prop.model_3d_status else "pending",
        "model_url": prop.model_3d_url,
        "progress": 100 if prop.model_3d_status == ModelStatus.complete else 50
    }

@router.post("/", status_code=201)
async def create_property(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(...),
    price: float = Form(...),
    land_size: float = Form(0),
    generate_3d: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    image_front: Optional[UploadFile] = File(None),
    image_back: Optional[UploadFile] = File(None),
    image_left: Optional[UploadFile] = File(None),
    image_right: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_role("owner", "admin"))
):
    cover_url = None
    property_images = []

    # Save cover image
    if image:
        cover_url = save_upload(image)

    # Save multi-angle images
    angle_files = [
        (image_front, ImageType.exterior_front),
        (image_back, ImageType.exterior_back),
        (image_left, ImageType.exterior_left),
        (image_right, ImageType.exterior_right),
    ]
    for f, img_type in angle_files:
        if f:
            url = save_upload(f)
            property_images.append({"url": url, "type": img_type})
            if not cover_url:
                cover_url = url

    prop = Property(
        owner_id=current_user.id,
        title=title, description=description,
        location=location, price=price, land_size=land_size,
        image_url=cover_url,
        is_approved=True  # auto-approve for hackathon demo
    )
    db.add(prop); db.commit(); db.refresh(prop)

    for img in property_images:
        pi = PropertyImage(property_id=prop.id, url=img["url"], image_type=img["type"])
        db.add(pi)
    db.commit()

    if generate_3d and property_images:
        images_payload = [{"url": img["url"], "type": img["type"].value} for img in property_images]
        background_tasks.add_task(run_3d_generation, prop.id, images_payload, db)

    db.refresh(prop)
    return prop

@router.post("/{id}/generate-3d")
async def trigger_generation(
    id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("owner", "admin"))
):
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop: raise HTTPException(404, "Not found")
    images_payload = [{"url": img.url, "type": img.image_type.value} for img in prop.images]
    if not images_payload: raise HTTPException(400, "No images uploaded for this property")
    background_tasks.add_task(run_3d_generation, id, images_payload, db)
    return {"message": "3D generation started"}

@router.get("/{id}/walkthrough-config")
def get_walkthrough_config(id: int, db: Session = Depends(get_db)):
    config = db.query(PropertyWalkthroughConfig).filter(
        PropertyWalkthroughConfig.property_id == id
    ).first()
    if not config: raise HTTPException(404, "No walkthrough config")
    return config

@router.put("/{id}/walkthrough-config")
def update_walkthrough_config(
    id: int, data: dict, db: Session = Depends(get_db),
    current_user = Depends(require_role("owner", "admin"))
):
    config = db.query(PropertyWalkthroughConfig).filter(
        PropertyWalkthroughConfig.property_id == id
    ).first()
    if not config:
        config = PropertyWalkthroughConfig(property_id=id)
        db.add(config)
    for key, val in data.items():
        setattr(config, key, val)
    db.commit(); db.refresh(config)
    return config
```

---

### Hour 9–12 | Professional Profiles

**`app/models/professional.py`:**
```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.core.database import Base

class Professional(Base):
    __tablename__ = "professionals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    profession = Column(String)
    bio = Column(String)
    hourly_rate = Column(Float)
    portfolio_url = Column(String)
```

**`app/api/v1/endpoints/professionals.py`:**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.endpoints.deps import require_role
from app.models.professional import Professional

router = APIRouter(prefix="/professionals", tags=["professionals"])

@router.get("/")
def list_professionals(profession: str = None, db: Session = Depends(get_db)):
    q = db.query(Professional)
    if profession: q = q.filter(Professional.profession == profession)
    return q.all()

@router.get("/{id}")
def get_professional(id: int, db: Session = Depends(get_db)):
    p = db.query(Professional).filter(Professional.id == id).first()
    if not p: raise HTTPException(404, "Not found")
    return p

@router.post("/", status_code=201)
def create_professional(data: dict, db: Session = Depends(get_db),
                         current_user = Depends(require_role("architect", "professional", "owner"))):
    existing = db.query(Professional).filter(Professional.user_id == current_user.id).first()
    if existing: raise HTTPException(400, "Profile already exists")
    p = Professional(user_id=current_user.id, **data)
    db.add(p); db.commit(); db.refresh(p)
    return p
```

---

### Hour 12–14 | main.py + Router + Migrations

**`app/api/v1/router.py`:**
```python
from fastapi import APIRouter
from app.api.v1.endpoints import auth, properties, professionals

router = APIRouter()
router.include_router(auth.router)
router.include_router(properties.router)
router.include_router(professionals.router)
```

**`app/main.py`:**
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router
from app.core.config import settings
from app.core.database import Base, engine
import os

# Create tables (use Alembic in production — ok for hackathon)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Immersive Real Estate API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# Serve uploaded files
os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.LOCAL_STORAGE_PATH), name="uploads")

app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health(): return {"status": "ok"}
```

**Run migrations (or just use `create_all` for hackathon):**
```bash
# Simple approach for hackathon — create_all in main.py handles table creation
uvicorn app.main:app --reload --port 8000
```

---

### Hour 14–18 | Integration Testing & CORS Verification

Work with frontend team to verify each endpoint works end-to-end:

```bash
# Test register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"owner@test.com","password":"pass1234","full_name":"Jane Owner","role":"owner"}'

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -F 'username=owner@test.com' -F 'password=pass1234'

# Test property creation (use TOKEN from login response)
curl -X POST http://localhost:8000/api/v1/properties/ \
  -H 'Authorization: Bearer TOKEN' \
  -F 'title=Beach House' -F 'location=Montego Bay' \
  -F 'price=350000' -F 'land_size=200' \
  -F 'image_front=@/path/to/front.jpg'

# Poll status
curl http://localhost:8000/api/v1/properties/1/model-status
```

**Verify in Swagger UI:** `http://localhost:8000/docs`

---

### Hour 18–22 | Seed Data + Polish

Create a seed script `seed.py` so demo has real content:

```python
# seed.py — run once: python seed.py
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.property import Property, PropertyImage, PropertyWalkthroughConfig, ModelStatus, ImageType

db = SessionLocal()

# Demo users
owner = User(email="owner@demo.com", full_name="Sarah Owner",
             hashed_password=get_password_hash("demo1234"), role=UserRole.owner)
buyer = User(email="buyer@demo.com", full_name="John Buyer",
             hashed_password=get_password_hash("demo1234"), role=UserRole.buyer)
db.add_all([owner, buyer]); db.commit()

# Demo property with mock 3D model
prop = Property(
    owner_id=owner.id, title="Modern Beach Villa", location="Montego Bay, Jamaica",
    description="Stunning beachfront property with panoramic ocean views.",
    price=850000, land_size=400,
    image_url="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800",
    model_3d_url="https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Box/glTF-Binary/Box.glb",
    model_3d_status=ModelStatus.complete, is_model_generated=True, is_approved=True
)
db.add(prop); db.commit()

config = PropertyWalkthroughConfig(
    property_id=prop.id,
    spawn_position={"x": 0, "y": 1.7, "z": 0},
    hotspots=[
        {"label": "Living Room",   "position": {"x": 1, "y": 1.7, "z": 1}, "camera_direction": {"x": 0, "y": 0, "z": -1}},
        {"label": "Master Bedroom","position": {"x": 3, "y": 1.7, "z": 2}, "camera_direction": {"x": -1, "y": 0, "z": 0}}
    ],
    floor_count=2
)
db.add(config); db.commit()
print("Seed complete — owner@demo.com / demo1234")
```

---

### Hour 22–24 | Final Checks

- [ ] All P1 endpoints return correct data
- [ ] CORS allows frontend origin
- [ ] `/uploads` serves files correctly
- [ ] `/docs` Swagger UI accessible
- [ ] Seed data loaded (`python seed.py`)
- [ ] 3D model generation mock returning a GLB URL
- [ ] Walkthrough config endpoint returns hotspot data

---

## F. Hackathon Scope — What to Cut if Behind

| Feature | Cut if needed |
|---|---|
| Professional profiles | Skip — use frontend mock data |
| Alembic migrations | Use `create_all` only |
| Image preprocessing (EXIF strip, resize) | Skip — save raw uploads |
| Re-trigger 3D generation endpoint | Skip for demo |
| Walkthrough config PUT | Return hardcoded defaults |

---

## G. Known Shortcuts (Technical Debt for Post-Hackathon)

- `is_approved=True` auto-approval — production needs admin review flow
- `create_all` instead of Alembic migrations
- Synchronous `run_3d_generation` in `BackgroundTasks` — production should use Celery
- No S3 — local file serving only
- Minimal error validation on form fields

---

*Backend plan derived from `Master_Implementation_Plan_upd.md` Sections 4–10, 18*

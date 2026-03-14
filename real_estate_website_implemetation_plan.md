# Immersive Real Estate Platform – RESTful API Implementation Plan

This document provides a comprehensive implementation plan for the backend API of an immersive real estate marketplace. It builds upon the initial guide, adding detailed steps for development, testing, and deployment, with a strong emphasis on **testing before serving the application**. The plan is structured to be followed sequentially, ensuring a robust and maintainable codebase.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
- [Database Setup with Migrations](#database-setup-with-migrations)
- [Models and Relationships](#models-and-relationships)
- [Pydantic Schemas](#pydantic-schemas)
- [Authentication & Role-Based Access Control](#authentication--role-based-access-control)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Properties](#properties)
  - [Users & Professionals](#users--professionals)
- [Nanobanana AI Integration](#nanobanana-ai-integration)
- [File Upload & Storage](#file-upload--storage)
  - [Conditional Storage: Local vs S3](#conditional-storage-local-vs-s3)
- [Testing Strategy](#testing-strategy)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [Running Tests](#running-tests)
- [README: API Testing Guide](#readme-api-testing-guide)
- [Deployment Considerations](#deployment-considerations)
- [Conclusion](#conclusion)

---

## Architecture Overview

The system follows a modern RESTful API design using:

- **FastAPI** – high-performance web framework with automatic OpenAPI documentation.
- **SQLAlchemy** – ORM for PostgreSQL database.
- **Alembic** – database migrations.
- **Pydantic** – data validation and serialization.
- **JWT** – stateless authentication with role-based access control.
- **Nanobanana AI** – external service for 3D model generation.
- **Cloud Storage (AWS S3)** – for images and generated GLB files (with fallback to local storage in development).
- **Pytest** – testing framework.

The API is structured in a modular way, separating concerns into models, schemas, routers, services, and auth.

---

## Prerequisites

- Python 3.9+
- PostgreSQL (local or cloud)
- (Optional) AWS S3 bucket and credentials – if not provided, local storage will be used.
- Nanobanana API key
- Git

---

## Project Setup

1. **Create project directory and virtual environment**

```bash
mkdir realestate-api
cd realestate-api
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic python-multipart requests python-jose[cryptography] passlib[bcrypt] boto3 pytest pytest-asyncio httpx python-dotenv
```

3. **Initialize project structure**

```
realestate-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── property.py
│   │   └── professional.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── property.py
│   │   └── professional.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── properties.py
│   │   │   │   └── professionals.py
│   │   │   └── router.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── nanobanana.py
│   │   └── storage.py
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_properties.py
│   └── test_nanobanana.py
├── alembic/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

4. **Create `.env` file**

```
# Database
DATABASE_URL=postgresql://user:pass@localhost/realestate

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Nanobanana
NANOBANANA_API_KEY=your-key

# Storage – S3 (optional)
USE_S3=false   # Set to 'true' to enable S3; otherwise local storage used
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_BUCKET_NAME=your-bucket
AWS_REGION=us-east-1

# Local storage path (used when USE_S3=false)
LOCAL_STORAGE_PATH=./uploads
```

5. **Load environment variables** in `app/core/config.py`

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    NANOBANANA_API_KEY: str

    # S3 settings (optional)
    USE_S3: bool = False
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    AWS_REGION: Optional[str] = "us-east-1"

    # Local storage
    LOCAL_STORAGE_PATH: str = "./uploads"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Database Setup with Migrations

1. **Configure database connection** in `app/core/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

2. **Initialize Alembic**

```bash
alembic init alembic
```

3. **Configure `alembic.ini`** to use the database URL:

```
sqlalchemy.url = postgresql://user:pass@localhost/realestate
```

4. **In `alembic/env.py`**, set the `target_metadata`:

```python
from app.core.database import Base
from app.models import user, property, professional   # import all models
target_metadata = Base.metadata
```

5. **Generate initial migration**

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## Models and Relationships

Enhance the models with proper relationships and fields.

**`app/models/user.py`**

```python
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    BUYER = "buyer"
    OWNER = "owner"
    ARCHITECT = "architect"
    MASON = "mason"
    CARPENTER = "carpenter"
    CONTRACTOR = "contractor"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.BUYER)
    is_active = Column(Boolean, default=True)

    # Relationships
    properties = relationship("Property", back_populates="owner")
    professional_profile = relationship("Professional", back_populates="user", uselist=False)
```

**`app/models/property.py`**

```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, index=True)
    description = Column(String)
    location = Column(String)
    price = Column(Float)
    land_size = Column(Float)
    image_url = Column(String)          # original image URL (S3 or local)
    model_3d_url = Column(String, nullable=True)  # GLB model URL
    is_model_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="properties")
```

**`app/models/professional.py`** (for marketplace profiles)

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Professional(Base):
    __tablename__ = "professionals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    profession = Column(String)   # e.g., architect, mason
    bio = Column(Text)
    portfolio_url = Column(String, nullable=True)
    hourly_rate = Column(Float, nullable=True)

    user = relationship("User", back_populates="professional_profile")
```

---

## Pydantic Schemas

Define request/response models for API validation and documentation.

**`app/schemas/user.py`**

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.BUYER

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
```

**`app/schemas/property.py`**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PropertyBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: str
    price: float
    land_size: float

class PropertyCreate(PropertyBase):
    pass

class PropertyOut(PropertyBase):
    id: int
    owner_id: int
    image_url: str
    model_3d_url: Optional[str] = None
    is_model_generated: bool
    created_at: datetime

    class Config:
        from_attributes = True
```

**`app/schemas/professional.py`**

```python
from pydantic import BaseModel
from typing import Optional

class ProfessionalBase(BaseModel):
    profession: str
    bio: Optional[str] = None
    portfolio_url: Optional[str] = None
    hourly_rate: Optional[float] = None

class ProfessionalCreate(ProfessionalBase):
    pass

class ProfessionalOut(ProfessionalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
```

---

## Authentication & Role-Based Access Control

**`app/core/security.py`**

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

**`app/api/v1/endpoints/auth.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}
```

**Dependency for current user and role checking** in `app/api/v1/endpoints/deps.py`

```python
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.api.v1.endpoints.auth import oauth2_scheme

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker
```

---

## API Endpoints

Organize endpoints under versioned router.

**`app/api/v1/router.py`**

```python
from fastapi import APIRouter
from app.api.v1.endpoints import auth, properties, professionals

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(properties.router, prefix="/properties", tags=["Properties"])
router.include_router(professionals.router, prefix="/professionals", tags=["Professionals"])
```

### Properties Endpoints

**`app/api/v1/endpoints/properties.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List
from app.api.v1.endpoints.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyOut
from app.services.storage import upload_file
from app.services.nanobanana import generate_3d_model

router = APIRouter()

@router.get("/", response_model=List[PropertyOut])
def list_properties(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    properties = db.query(Property).offset(skip).limit(limit).all()
    return properties

@router.post("/", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
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
    # Upload image to S3 or local storage (based on configuration)
    image_url = await upload_file(image, folder="property-images")

    # Create property record
    property = Property(
        owner_id=current_user.id,
        title=title,
        description=description,
        location=location,
        price=price,
        land_size=land_size,
        image_url=image_url
    )
    db.add(property)
    db.commit()
    db.refresh(property)

    # Trigger 3D model generation (can be background task)
    try:
        model_url = await generate_3d_model(image_url)
        property.model_3d_url = model_url
        property.is_model_generated = True
        db.commit()
    except Exception as e:
        # Log error, but don't fail the upload
        print(f"3D generation failed: {e}")

    return property

@router.get("/{property_id}", response_model=PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(404, "Property not found")
    return property

@router.put("/{property_id}", response_model=PropertyOut)
def update_property(
    property_id: int,
    property_update: PropertyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(404, "Property not found")
    # Check ownership
    if property.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(403, "Not authorized to update this property")
    for key, value in property_update.dict().items():
        setattr(property, key, value)
    db.commit()
    db.refresh(property)
    return property

@router.delete("/{property_id}", status_code=204)
def delete_property(
    property_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(404, "Property not found")
    if property.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(403, "Not authorized to delete this property")
    db.delete(property)
    db.commit()
    return None
```

### Professionals Endpoints

Similar CRUD, but only accessible by professionals themselves or admin. We'll skip for brevity.

---

## Nanobanana AI Integration

**`app/services/nanobanana.py`**

```python
import httpx
from app.core.config import settings
from typing import Optional

async def generate_3d_model(image_url: str) -> Optional[str]:
    """
    Call Nanobanana API to generate a 3D model from an image URL.
    Returns the URL of the generated GLB model.
    """
    api_url = "https://api.nanobanana.ai/v1/generate-3d"
    headers = {
        "Authorization": f"Bearer {settings.NANOBANANA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "image_url": image_url,
        "format": "glb"
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("model_url")
```

**Error handling**: Wrap in try-except and log errors.

---

## File Upload & Storage

This service handles file uploads either to AWS S3 or to the local filesystem, based on the `USE_S3` environment variable. If S3 is not configured, it stores files locally and returns a local URL (which can be served by FastAPI static files).

**`app/services/storage.py`**

```python
import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings

# Conditionally import boto3 only if S3 is used
if settings.USE_S3:
    import boto3
    from botocore.exceptions import ClientError

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

async def upload_file(file: UploadFile, folder: str = "") -> str:
    """
    Upload a file to either S3 or local storage based on USE_S3 setting.
    Returns the public URL or local path URL.
    """
    if settings.USE_S3:
        return await _upload_to_s3(file, folder)
    else:
        return await _upload_to_local(file, folder)

async def _upload_to_s3(file: UploadFile, folder: str) -> str:
    """Upload to S3 and return public URL."""
    file_extension = file.filename.split('.')[-1]
    file_key = f"{folder}/{uuid.uuid4()}.{file_extension}"
    try:
        # Reset file pointer to beginning (important after potential reads)
        await file.seek(0)
        s3_client.upload_fileobj(
            file.file,
            settings.AWS_BUCKET_NAME,
            file_key,
            ExtraArgs={"ACL": "public-read"}  # or use presigned URLs
        )
        url = f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
        return url
    except ClientError as e:
        raise Exception(f"S3 upload failed: {e}")

async def _upload_to_local(file: UploadFile, folder: str) -> str:
    """Save file locally and return URL path (to be served via FastAPI static files)."""
    # Ensure upload directory exists
    upload_dir = Path(settings.LOCAL_STORAGE_PATH) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = upload_dir / filename

    # Save file
    await file.seek(0)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Return URL that will be served by FastAPI static files
    # e.g., /uploads/property-images/filename.jpg
    return f"/uploads/{folder}/{filename}"
```

**Serving local files in development** – Add this to `app/main.py` to serve uploaded files when using local storage.

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.v1.router import router as api_router

app = FastAPI(title="Immersive Real Estate API")

# Include API router
app.include_router(api_router)

# Serve uploaded files if using local storage
if not settings.USE_S3:
    # Ensure the upload directory exists
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.LOCAL_STORAGE_PATH), name="uploads")
```

---

## Testing Strategy

Testing is crucial to ensure API reliability. We'll use `pytest` with `httpx.AsyncClient` for FastAPI testing. The tests should cover both S3 and local storage scenarios, but for simplicity we can mock the storage service.

### Setup Testing Environment

1. **Install test dependencies** (already included: pytest, pytest-asyncio, httpx).

2. **Create `conftest.py`** in the `tests` directory to define fixtures.

```python
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Use a separate test database
SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/realestate_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
```

### Unit Tests

Test individual functions, e.g., password hashing, token creation, and storage service (mocked).

**`tests/test_auth_unit.py`**

```python
from app.core.security import get_password_hash, verify_password, create_access_token
from jose import jwt
from app.core.config import settings

def test_password_hashing():
    password = "secret"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)

def test_create_access_token():
    data = {"sub": "1", "role": "owner"}
    token = create_access_token(data)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "1"
    assert payload["role"] == "owner"
```

**`tests/test_storage.py`** – test local and S3 uploads with mocking.

```python
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.storage import upload_file, _upload_to_local, _upload_to_s3
from fastapi import UploadFile
import io

@pytest.mark.asyncio
async def test_upload_to_local(tmp_path, monkeypatch):
    # Override LOCAL_STORAGE_PATH to temp path
    monkeypatch.setattr("app.core.config.settings.LOCAL_STORAGE_PATH", str(tmp_path))
    file_content = b"fake image content"
    file = UploadFile(filename="test.jpg", file=io.BytesIO(file_content))
    url = await _upload_to_local(file, "test-folder")
    assert url.startswith("/uploads/test-folder/")
    # Check file was saved
    saved_path = tmp_path / "test-folder" / url.split("/")[-1]
    assert saved_path.exists()
    assert saved_path.read_bytes() == file_content

@pytest.mark.asyncio
async def test_upload_to_s3(monkeypatch):
    mock_s3 = MagicMock()
    monkeypatch.setattr("app.services.storage.s3_client", mock_s3)
    monkeypatch.setattr("app.core.config.settings.USE_S3", True)
    file_content = b"fake image content"
    file = UploadFile(filename="test.jpg", file=io.BytesIO(file_content))
    url = await _upload_to_s3(file, "test-folder")
    assert "s3.amazonaws.com" in url
    mock_s3.upload_fileobj.assert_called_once()
```

### Integration Tests

Test API endpoints using the test client.

**`tests/test_properties.py`**

```python
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock

def test_create_property(client, db, monkeypatch):
    # Mock storage upload to return a fake URL (to avoid real file handling)
    async def mock_upload_file(*args, **kwargs):
        return "https://fake-s3-url/image.jpg"

    monkeypatch.setattr("app.services.storage.upload_file", mock_upload_file)

    # Mock nanobanana generation
    async def mock_generate(*args, **kwargs):
        return "https://fake-model-url/model.glb"

    monkeypatch.setattr("app.services.nanobanana.generate_3d_model", mock_generate)

    # First register a user
    user_data = {
        "email": "owner@test.com",
        "password": "testpass",
        "full_name": "Test Owner",
        "role": "owner"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Login
    login_data = {
        "username": "owner@test.com",
        "password": "testpass"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]

    # Upload property with image (mock file)
    files = {
        "image": ("test.jpg", b"fake image content", "image/jpeg")
    }
    form_data = {
        "title": "Beautiful House",
        "location": "New York",
        "price": 500000,
        "land_size": 200.5
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/properties/", data=form_data, files=files, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Beautiful House"
    assert data["owner_id"] == user_id
    assert data["image_url"] == "https://fake-s3-url/image.jpg"
    assert data["model_3d_url"] == "https://fake-model-url/model.glb"

def test_list_properties(client):
    response = client.get("/api/v1/properties/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

**Mock external services** to avoid real API calls during tests. We've already mocked storage and nanobanana.

### Running Tests

Create a `pytest.ini` or just run:

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

Add a `test` script in `pyproject.toml` or use `tox` for CI.

**Ensure tests pass before serving the application.** In a CI/CD pipeline, this is enforced.

---

## README: API Testing Guide

The `README.md` should include clear instructions for setting up and testing the API. Below is a template.

```markdown
# Immersive Real Estate API

## Setup

1. Clone the repository
2. Create virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your configuration (database, Nanobanana API key).  
   - To use S3 for file storage, set `USE_S3=true` and provide AWS credentials.  
   - Otherwise, files will be saved locally under `./uploads` and served via FastAPI static files.
4. Run database migrations:
   ```bash
   alembic upgrade head
   ```
5. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Interactive docs available at `/docs` (Swagger UI) and `/redoc`.

## Testing

We use `pytest` for testing. Ensure the test database is configured (set `DATABASE_URL` in `.env` to a separate test database, e.g., `realestate_test`).

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

Before deploying or serving the application, always run the test suite to verify integrity.

## Storage Configuration

- **S3 Mode** (`USE_S3=true`): Files are uploaded to your S3 bucket and public URLs are stored.
- **Local Mode** (`USE_S3=false`): Files are saved in the `./uploads` directory and served under the `/uploads` endpoint. This is ideal for development without AWS credentials.

## Example API Calls

### Register a user
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret", "full_name": "John Doe", "role": "owner"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secret"
```

### Create a property (authenticated)
```bash
curl -X POST http://localhost:8000/api/v1/properties/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Cozy Cottage" \
  -F "location=Countryside" \
  -F "price=250000" \
  -F "land_size=150" \
  -F "image=@/path/to/image.jpg"
```

```

---

## Deployment Considerations

- Use **Gunicorn + Uvicorn workers** for production.
- Set up a **reverse proxy** (Nginx) with SSL.
- Use environment variables for secrets; never commit `.env`.
- Configure **CORS** appropriately in FastAPI.
- Use **database connection pooling**.
- Implement **rate limiting** and **DDOS protection**.
- Set up **logging** (e.g., with Sentry).
- Use **background tasks** (Celery, ARQ) for long-running 3D generation to avoid blocking requests.
- For local file storage in production, ensure the `./uploads` directory is backed up and served via a CDN or Nginx (not just FastAPI static files). However, it's recommended to use S3 or similar for production.

---

## Conclusion

This implementation plan provides a solid foundation for building a RESTful API for an immersive real estate platform. By following the outlined steps, you'll have a well-structured, testable, and scalable backend. Remember: **always test before serving** – it ensures reliability and reduces bugs in production.

The integration with Nanobanana AI adds a unique immersive experience, and the role-based system caters to a diverse set of users. The storage service is flexible, allowing both local development and cloud-based production setups. With proper testing and documentation, the API will be ready for frontend consumption and eventual deployment.
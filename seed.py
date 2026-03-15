import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal, engine
from app.models.user import User, UserRole, Account
from app.models.property import Property
from app.models.professional import Professional
from app.core.security import get_password_hash

def seed_db():
    # 1. Drop all existing tables and types to start clean
    print("Cleaning database...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users, properties, professionals, \"user\", session, account CASCADE;"))
        conn.execute(text("DROP TYPE IF EXISTS userrole CASCADE;"))
        conn.commit()

    db = SessionLocal()
    
    # 2. Create tables
    from app.core.database import Base
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Seeding database...")

    # 3. Seed Users
    users_to_create = [
        {"email": "admin@example.com", "first_name": "Admin", "last_name": "User", "role": UserRole.ADMIN, "password": "adminpassword"},
        {"email": "owner1@example.com", "first_name": "John", "last_name": "Owner", "role": UserRole.OWNER, "password": "password123"},
        {"email": "owner2@example.com", "first_name": "Sarah", "last_name": "Landlord", "role": UserRole.OWNER, "password": "password123"},
        {"email": "architect1@example.com", "first_name": "Alice", "last_name": "Architect", "role": UserRole.ARCHITECT, "password": "password123"},
        {"email": "mason1@example.com", "first_name": "Mike", "last_name": "Mason", "role": UserRole.MASON, "password": "password123"},
        {"email": "buyer1@example.com", "first_name": "Bob", "last_name": "Buyer", "role": UserRole.BUYER, "password": "password123"},
    ]

    created_users = {}
    for user_data in users_to_create:
        user_id = uuid.uuid4().hex
        new_user = User(
            id=user_id,
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=user_data["role"],
            email_verified=True
        )
        db.add(new_user)
        
        # Create Account
        new_account = Account(
            id=uuid.uuid4().hex,
            user_id=user_id,
            account_id=user_data["email"],
            provider_id="credential",
            password=get_password_hash(user_data["password"])
        )
        db.add(new_account)
        created_users[user_data["email"]] = new_user

    db.commit()

    # 4. Seed Professionals
    professionals_data = [
        {
            "user_id": created_users["architect1@example.com"].id,
            "profession": "Architect",
            "bio": "Specialized in modern sustainable homes.",
            "hourly_rate": 150.0
        },
        {
            "user_id": created_users["mason1@example.com"].id,
            "profession": "Mason",
            "bio": "Excellence in brickwork and stonemasonry for over 10 years.",
            "hourly_rate": 85.0
        }
    ]

    for prof_data in professionals_data:
        new_prof = Professional(**prof_data)
        db.add(new_prof)
    
    db.commit()

    # 5. Seed Properties
    properties_data = [
        {
            "owner_id": created_users["owner1@example.com"].id,
            "title": "Modern Loft in Downtown",
            "description": "A beautiful loft with high ceilings and industrial feel.",
            "location": "New York, NY",
            "price": 850000.0,
            "land_size": 120.0,
            "image_url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
        },
        {
            "owner_id": created_users["owner2@example.com"].id,
            "title": "Suburban Family House",
            "description": "Spacious house with a large backyard and 4 bedrooms.",
            "location": "Austin, TX",
            "price": 450000.0,
            "land_size": 350.0,
            "image_url": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
        }
    ]

    for prop_data in properties_data:
        new_prop = Property(**prop_data)
        db.add(new_prop)
    
    db.commit()
    print("Seeding completed successfully!")
    db.close()

if __name__ == "__main__":
    seed_db()

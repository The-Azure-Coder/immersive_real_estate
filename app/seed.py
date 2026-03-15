import os
import sys
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.property import Property
from app.models.professional import Professional
from app.models.floor_plan import FloorPlan
from app.models.favorite import Favorite
from app.models.message import Conversation, Message

def seed_db():
    db = SessionLocal()
    print("Clearing existing data...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("Creating users...")
    # Admin / Owner
    admin = User(
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Alexander Vance",
        role=UserRole.OWNER
    )
    # Professional (Architect)
    architect_user = User(
        email="architect@test.com",
        hashed_password=get_password_hash("architect123"),
        full_name="Sarah Chen",
        role=UserRole.ARCHITECT
    )
    # Buyer
    buyer = User(
        email="buyer@test.com",
        hashed_password=get_password_hash("buyer123"),
        full_name="John Doe",
        role=UserRole.BUYER
    )
    
    db.add_all([admin, architect_user, buyer])
    db.commit()
    db.refresh(admin)
    db.refresh(architect_user)
    db.refresh(buyer)

    print("Creating professional profile...")
    prof_profile = Professional(
        user_id=architect_user.id,
        profession="architect",
        bio="Award-winning architect specialized in glass and steel structures that harmonize with natural landscapes.",
        portfolio_url="https://portfolio.sarahchen.com",
        hourly_rate=185.0
    )
    db.add(prof_profile)
    db.commit()
    db.refresh(prof_profile)

    print("Creating properties...")
    p1 = Property(
        owner_id=admin.id,
        title="Azure Bay Waterfront",
        description="A breathtaking waterfront parcel with 200ft of private shoreline. Perfect for a modern glass villa.",
        location="Malibu, CA",
        price=1250000.0,
        land_size=1.5,
        image_url="https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
        is_model_generated=True,
        model_3d_url="https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Duck/glTF-Binary/Duck.glb"
    )
    p2 = Property(
        owner_id=admin.id,
        title="Summit Peak Estate",
        description="High-altitude plot with 360-degree views of the Rockies. Ideal for an off-grid luxury retreat.",
        location="Aspen, CO",
        price=850000.0,
        land_size=4.2,
        image_url="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b",
        is_model_generated=False # Will show as "None" or "Pending" in UI
    )
    
    db.add_all([p1, p2])
    db.commit()
    db.refresh(p1)
    db.refresh(p2)

    print("Creating floor plans...")
    fp1 = FloorPlan(
        professional_id=prof_profile.id,
        title="The Glass Pavilion",
        description="An open-concept 3-bedroom masterpiece with floor-to-ceiling windows and a central courtyard.",
        price=450.0,
        sqft=2800,
        bedrooms=3,
        bathrooms=3.5,
        style="Modern",
        image_url="https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
        file_url="https://example.com/plan1.pdf"
    )
    db.add(fp1)
    db.commit()

    print("Creating messages...")
    conv = Conversation(user1_id=buyer.id, user2_id=admin.id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    
    m1 = Message(conversation_id=conv.id, sender_id=buyer.id, content="Hi! I'm interested in the Azure Bay property.")
    m2 = Message(conversation_id=conv.id, sender_id=admin.id, content="Hello John, it's still available. Would you like to schedule a 3D walkthrough?")
    db.add_all([m1, m2])
    db.commit()

    print("Creating favorites...")
    fav = Favorite(user_id=buyer.id, property_id=p1.id)
    db.add(fav)
    db.commit()

    print("Database seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_db()

"""
Seed Data Script for Ezzy Traders Backend
Populates the database with initial data for development and testing
"""

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timezone
from db_helper.models import Employee, Unit, DoorType, DoorTypeThicknessOption, Attribute, AttributeOption
import dependencies

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def seed_employee_data(db: Session):
    """Seed employee data"""
    # Check if employee already exists
    existing_employee = db.query(Employee).filter(Employee.username == "shabbir").first()
    if existing_employee:
        print("Employee 'shabbir' already exists, skipping...")
        return
    
    # Create employee with hashed password
    employee = Employee(
        username="shabbir",
        hashed_password=hash_password("shabbir"),
        email="shabbir@ezzytraders.com",
        phone="+1234567890",
        first_name="Shabbir",
        last_name="Admin",
        role="admin",
        is_active=True,
        created_by="system",
        updated_by="system"
    )
    
    db.add(employee)
    db.commit()
    print("Employee 'shabbir' created successfully with password 'shabbir'")


def seed_unit_data(db: Session):
    """Seed unit data"""
    units_data = [
        {"name": "Piece", "abbreviation": "pc", "unit_type": "Single"},
        {"name": "Square Foot", "abbreviation": "sqft", "unit_type": "Area"},
        {"name": "Linear Foot", "abbreviation": "lf", "unit_type": "Linear"},
        {"name": "Kilogram", "abbreviation": "kg", "unit_type": "Weight"},
        {"name": "Meter", "abbreviation": "m", "unit_type": "Linear"},
        {"name": "Millimeter", "abbreviation": "mm", "unit_type": "Linear"}
    ]
    
    for unit_data in units_data:
        existing_unit = db.query(Unit).filter(Unit.name == unit_data["name"]).first()
        if not existing_unit:
            unit = Unit(
                **unit_data,
                created_by="system",
                updated_by="system"
            )
            db.add(unit)
    
    db.commit()
    print("Unit data seeded successfully")


def seed_door_type_data(db: Session):
    """Seed door type data"""
    door_types_data = [
        {"name": "Solid Wood Door", "description": "Premium solid wood door"},
        {"name": "Hollow Core Door", "description": "Lightweight hollow core door"},
        {"name": "Metal Door", "description": "Security metal door"},
        {"name": "Glass Door", "description": "Modern glass door"}
    ]
    
    for door_type_data in door_types_data:
        existing_door_type = db.query(DoorType).filter(DoorType.name == door_type_data["name"]).first()
        if not existing_door_type:
            door_type = DoorType(
                **door_type_data,
                created_by="system",
                updated_by="system"
            )
            db.add(door_type)
    
    db.commit()
    print("Door type data seeded successfully")


def seed_thickness_options(db: Session):
    """Seed thickness options for door types"""
    # Get door types
    solid_wood = db.query(DoorType).filter(DoorType.name == "Solid Wood Door").first()
    hollow_core = db.query(DoorType).filter(DoorType.name == "Hollow Core Door").first()
    
    if solid_wood:
        thickness_options = [
            {"thickness_value": 35.0, "cost_per_sqft": 25.00},
            {"thickness_value": 45.0, "cost_per_sqft": 35.00},
            {"thickness_value": 55.0, "cost_per_sqft": 45.00}
        ]
        
        for option_data in thickness_options:
            existing_option = db.query(DoorTypeThicknessOption).filter(
                DoorTypeThicknessOption.door_type_id == solid_wood.id,
                DoorTypeThicknessOption.thickness_value == option_data["thickness_value"]
            ).first()
            
            if not existing_option:
                thickness_option = DoorTypeThicknessOption(
                    door_type_id=solid_wood.id,
                    **option_data,
                    created_by="system",
                    updated_by="system"
                )
                db.add(thickness_option)
    
    if hollow_core:
        thickness_options = [
            {"thickness_value": 35.0, "cost_per_sqft": 15.00},
            {"thickness_value": 45.0, "cost_per_sqft": 20.00}
        ]
        
        for option_data in thickness_options:
            existing_option = db.query(DoorTypeThicknessOption).filter(
                DoorTypeThicknessOption.door_type_id == hollow_core.id,
                DoorTypeThicknessOption.thickness_value == option_data["thickness_value"]
            ).first()
            
            if not existing_option:
                thickness_option = DoorTypeThicknessOption(
                    door_type_id=hollow_core.id,
                    **option_data,
                    created_by="system",
                    updated_by="system"
                )
                db.add(thickness_option)
    
    db.commit()
    print("Thickness options seeded successfully")


def seed_attribute_data(db: Session):
    """Seed attribute data"""
    # Get units
    piece_unit = db.query(Unit).filter(Unit.name == "Piece").first()
    sqft_unit = db.query(Unit).filter(Unit.name == "Square Foot").first()
    kg_unit = db.query(Unit).filter(Unit.name == "Kilogram").first()
    
    attributes_data = [
        {
            "name": "Premium Finish",
            "description": "High-quality premium finish",
            "double_side": True,
            "cost_type": "constant",
            "fixed_cost": 50.00
        },
        {
            "name": "Custom Size",
            "description": "Custom size adjustment",
            "double_side": False,
            "cost_type": "variable",
            "cost_per_unit": 2.50,
            "unit_id": sqft_unit.id if sqft_unit else None
        },
        {
            "name": "Special Handling",
            "description": "Special handling requirements",
            "double_side": False,
            "cost_type": "direct"
        },
        {
            "name": "Hardware Package",
            "description": "Complete hardware package",
            "double_side": False,
            "cost_type": "constant",
            "fixed_cost": 75.00
        }
    ]
    
    for attr_data in attributes_data:
        existing_attr = db.query(Attribute).filter(Attribute.name == attr_data["name"]).first()
        if not existing_attr:
            attribute = Attribute(
                **attr_data,
                created_by="system",
                updated_by="system"
            )
            db.add(attribute)
    
    db.commit()
    print("Attribute data seeded successfully")


def seed_attribute_options(db: Session):
    """Seed attribute options"""
    # Get attributes
    premium_finish = db.query(Attribute).filter(Attribute.name == "Premium Finish").first()
    hardware_package = db.query(Attribute).filter(Attribute.name == "Hardware Package").first()
    
    if premium_finish:
        options_data = [
            {"name": "Standard Premium", "cost": 50.00, "display_order": 1},
            {"name": "Deluxe Premium", "cost": 75.00, "display_order": 2},
            {"name": "Ultra Premium", "cost": 100.00, "display_order": 3}
        ]
        
        for option_data in options_data:
            existing_option = db.query(AttributeOption).filter(
                AttributeOption.attribute_id == premium_finish.id,
                AttributeOption.name == option_data["name"]
            ).first()
            
            if not existing_option:
                option = AttributeOption(
                    attribute_id=premium_finish.id,
                    **option_data,
                    created_by="system",
                    updated_by="system"
                )
                db.add(option)
    
    if hardware_package:
        options_data = [
            {"name": "Basic Hardware", "cost": 75.00, "display_order": 1},
            {"name": "Premium Hardware", "cost": 120.00, "display_order": 2},
            {"name": "Luxury Hardware", "cost": 200.00, "display_order": 3}
        ]
        
        for option_data in options_data:
            existing_option = db.query(AttributeOption).filter(
                AttributeOption.attribute_id == hardware_package.id,
                AttributeOption.name == option_data["name"]
            ).first()
            
            if not existing_option:
                option = AttributeOption(
                    attribute_id=hardware_package.id,
                    **option_data,
                    created_by="system",
                    updated_by="system"
                )
                db.add(option)
    
    db.commit()
    print("Attribute options seeded successfully")


def seed_all_data(db: Session):
    """Seed all data"""
    print("Starting data seeding...")
    
    seed_employee_data(db)
    seed_unit_data(db)
    seed_door_type_data(db)
    seed_thickness_options(db)
    seed_attribute_data(db)
    seed_attribute_options(db)
    
    print("All data seeded successfully!")


if __name__ == "__main__":
    # Create a database session directly instead of calling the generator function
    from dependencies import SessionLocal
    
    db = SessionLocal()
    try:
        seed_all_data(db)
    finally:
        db.close()
    
    # This can be run directly or imported and called from other scripts
    print("Seed data script loaded. Use seed_all_data(db_session) to populate the database.")

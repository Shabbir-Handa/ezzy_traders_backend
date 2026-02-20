"""
Seed Data Script
Seeds the database with initial data for testing and development.
Includes: Employee, Units, Services, Service Groupings, Door Types, and a Sample Customer.
"""

import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal, engine
from app.models import (
    Base, Employee, Customer, Unit,
    Service, ServiceOption, ServiceGrouping, ServiceGroupingChild,
    DoorType, DoorTypeThicknessOption, DoorTypeService,
)

try:
    import bcrypt
except ImportError:
    bcrypt = None


def hash_password(password: str) -> str:
    if bcrypt:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return password


def seed():
    db = SessionLocal()

    try:
        # ==================================================================
        # 1. EMPLOYEE (Admin)
        # ==================================================================
        existing_admin = db.query(Employee).filter(Employee.username == "admin").first()
        if not existing_admin:
            admin = Employee(
                first_name="Admin",
                last_name="User",
                username="admin",
                email="admin@ezzytraders.com",
                phone="0000000000",
                hashed_password=hash_password("admin123"),
                role="admin",
                created_by="system",
                updated_by="system",
            )
            db.add(admin)
            db.flush()
            print("✅ Admin employee seeded")
        else:
            print("⏭️  Admin employee already exists, skipping")

        # ==================================================================
        # 2. UNITS
        # ==================================================================
        units_data = [
            {"name": "Square Foot", "abbreviation": "sqft", "unit_type": "area"},
            {"name": "Linear Foot", "abbreviation": "lf", "unit_type": "length"},
            {"name": "Piece", "abbreviation": "pc", "unit_type": "quantity"},
            {"name": "Kilogram", "abbreviation": "kg", "unit_type": "weight"},
            {"name": "Meter", "abbreviation": "m", "unit_type": "length"},
            {"name": "Millimeter", "abbreviation": "mm", "unit_type": "length"},
            {"name": "Inch", "abbreviation": "in", "unit_type": "length"},
            {"name": "Liter", "abbreviation": "ltr", "unit_type": "volume"},
            {"name": "Hour", "abbreviation": "hr", "unit_type": "time"},
        ]

        unit_map = {}
        for u in units_data:
            existing = db.query(Unit).filter(Unit.name == u["name"]).first()
            if not existing:
                unit = Unit(**u, created_by="system", updated_by="system")
                db.add(unit)
                db.flush()
                unit_map[u["abbreviation"]] = unit
                print(f"  ✅ Unit: {u['name']}")
            else:
                unit_map[u["abbreviation"]] = existing
                print(f"  ⏭️  Unit: {u['name']} exists")

        # ==================================================================
        # 3. SERVICES
        # ==================================================================

        # --- CONSUMABLE: Laminate (area-based, both_sides, with options) ---
        svc_laminate = db.query(Service).filter(Service.name == "Laminate").first()
        if not svc_laminate:
            svc_laminate = Service(
                name="Laminate",
                description="Laminate sheet applied to door surface",
                service_type="consumable",
                consumable_kind="area",
                cost=15.0,
                both_sides=True,
                unit_id=unit_map["sqft"].id,
                created_by="system", updated_by="system",
            )
            db.add(svc_laminate)
            db.flush()

            # Options: different laminate grades
            for opt_name, opt_cost in [("Standard Laminate", 15.0), ("Premium Laminate", 25.0), ("Designer Laminate", 40.0)]:
                db.add(ServiceOption(service_id=svc_laminate.id, name=opt_name, cost=opt_cost, created_by="system", updated_by="system"))

            db.flush()
            print("  ✅ Service: Laminate (consumable, area)")
        else:
            print("  ⏭️  Service: Laminate exists")

        # --- CONSUMABLE: Edge Banding (length-based) ---
        svc_edge = db.query(Service).filter(Service.name == "Edge Banding").first()
        if not svc_edge:
            svc_edge = Service(
                name="Edge Banding",
                description="PVC edge banding tape",
                service_type="consumable",
                consumable_kind="length",
                cost=5.0,
                both_sides=False,
                unit_id=unit_map["lf"].id,
                created_by="system", updated_by="system",
            )
            db.add(svc_edge)
            db.flush()
            print("  ✅ Service: Edge Banding (consumable, length)")
        else:
            print("  ⏭️  Service: Edge Banding exists")

        # --- CONSUMABLE: Paint (area-based) ---
        svc_paint = db.query(Service).filter(Service.name == "Paint").first()
        if not svc_paint:
            svc_paint = Service(
                name="Paint",
                description="Spray paint finish",
                service_type="consumable",
                consumable_kind="area",
                cost=12.0,
                both_sides=True,
                unit_id=unit_map["sqft"].id,
                created_by="system", updated_by="system",
            )
            db.add(svc_paint)
            db.flush()
            print("  ✅ Service: Paint (consumable, area)")
        else:
            print("  ⏭️  Service: Paint exists")

        # --- ADD-ON: Hardware Package (with options) ---
        svc_hardware = db.query(Service).filter(Service.name == "Hardware Package").first()
        if not svc_hardware:
            svc_hardware = Service(
                name="Hardware Package",
                description="Door hardware fittings",
                service_type="add_on",
                cost=500.0,
                both_sides=False,
                created_by="system", updated_by="system",
            )
            db.add(svc_hardware)
            db.flush()

            for opt_name, opt_cost in [("Basic Hardware", 500.0), ("Premium Hardware", 1200.0), ("Luxury Hardware", 2500.0)]:
                db.add(ServiceOption(service_id=svc_hardware.id, name=opt_name, cost=opt_cost, created_by="system", updated_by="system"))

            db.flush()
            print("  ✅ Service: Hardware Package (add-on)")
        else:
            print("  ⏭️  Service: Hardware Package exists")

        # --- ADD-ON: Glass Panel (with options) ---
        svc_glass = db.query(Service).filter(Service.name == "Glass Panel").first()
        if not svc_glass:
            svc_glass = Service(
                name="Glass Panel",
                description="Decorative glass insert",
                service_type="add_on",
                cost=800.0,
                both_sides=False,
                created_by="system", updated_by="system",
            )
            db.add(svc_glass)
            db.flush()

            for opt_name, opt_cost in [("Clear Glass", 800.0), ("Frosted Glass", 1200.0)]:
                db.add(ServiceOption(service_id=svc_glass.id, name=opt_name, cost=opt_cost, created_by="system", updated_by="system"))

            db.flush()
            print("  ✅ Service: Glass Panel (add-on)")
        else:
            print("  ⏭️  Service: Glass Panel exists")

        # --- ADD-ON: Lock Set (no options, fixed cost) ---
        svc_lock = db.query(Service).filter(Service.name == "Lock Set").first()
        if not svc_lock:
            svc_lock = Service(
                name="Lock Set",
                description="Door lock mechanism",
                service_type="add_on",
                cost=350.0,
                both_sides=False,
                created_by="system", updated_by="system",
            )
            db.add(svc_lock)
            db.flush()
            print("  ✅ Service: Lock Set (add-on, no options)")
        else:
            print("  ⏭️  Service: Lock Set exists")

        # --- LABOUR: Installation Labour ---
        svc_install = db.query(Service).filter(Service.name == "Installation Labour").first()
        if not svc_install:
            svc_install = Service(
                name="Installation Labour",
                description="Labour charge for door installation",
                service_type="labour",
                both_sides=False,
                created_by="system", updated_by="system",
            )
            db.add(svc_install)
            db.flush()
            print("  ✅ Service: Installation Labour (labour)")
        else:
            print("  ⏭️  Service: Installation Labour exists")

        # --- LABOUR: Custom Cutting ---
        svc_cutting = db.query(Service).filter(Service.name == "Custom Cutting").first()
        if not svc_cutting:
            svc_cutting = Service(
                name="Custom Cutting",
                description="Custom cutting and shaping",
                service_type="labour",
                both_sides=False,
                created_by="system", updated_by="system",
            )
            db.add(svc_cutting)
            db.flush()
            print("  ✅ Service: Custom Cutting (labour)")
        else:
            print("  ⏭️  Service: Custom Cutting exists")

        # ==================================================================
        # 4. SERVICE GROUPING: Full Finish Package
        # ==================================================================
        grp_finish = db.query(ServiceGrouping).filter(ServiceGrouping.name == "Full Finish Package").first()
        if not grp_finish:
            grp_finish = ServiceGrouping(
                name="Full Finish Package",
                description="Complete finish package: laminate + edge banding",
                created_by="system", updated_by="system",
            )
            db.add(grp_finish)
            db.flush()

            db.add(ServiceGroupingChild(grouping_id=grp_finish.id, service_id=svc_laminate.id, required=True, created_by="system", updated_by="system"))
            db.add(ServiceGroupingChild(grouping_id=grp_finish.id, service_id=svc_edge.id, required=True, created_by="system", updated_by="system"))
            db.flush()
            print("  ✅ Service Grouping: Full Finish Package")
        else:
            print("  ⏭️  Service Grouping: Full Finish Package exists")

        # ==================================================================
        # 5. DOOR TYPES
        # ==================================================================

        # --- Flush Door ---
        dt_flush = db.query(DoorType).filter(DoorType.name == "Flush Door").first()
        if not dt_flush:
            dt_flush = DoorType(name="Flush Door", description="Standard flush door", created_by="system", updated_by="system")
            db.add(dt_flush)
            db.flush()

            # Thickness options
            for tv, cpq in [(19, 45.0), (25, 55.0), (30, 65.0), (35, 75.0)]:
                db.add(DoorTypeThicknessOption(door_type_id=dt_flush.id, thickness_value=tv, cost_per_sqft=cpq, created_by="system", updated_by="system"))
            db.flush()

            # Associate services
            db.add(DoorTypeService(door_type_id=dt_flush.id, service_id=svc_laminate.id, required=False, created_by="system", updated_by="system"))
            db.add(DoorTypeService(door_type_id=dt_flush.id, service_id=svc_edge.id, required=False, created_by="system", updated_by="system"))
            db.add(DoorTypeService(door_type_id=dt_flush.id, service_id=svc_hardware.id, required=False, created_by="system", updated_by="system"))
            db.add(DoorTypeService(door_type_id=dt_flush.id, service_id=svc_lock.id, required=False, created_by="system", updated_by="system"))
            db.add(DoorTypeService(door_type_id=dt_flush.id, service_id=svc_install.id, required=False, created_by="system", updated_by="system"))
            db.flush()

            print("  ✅ Door Type: Flush Door (4 thicknesses + 5 services)")
        else:
            print("  ⏭️  Door Type: Flush Door exists")

        # --- Panel Door ---
        dt_panel = db.query(DoorType).filter(DoorType.name == "Panel Door").first()
        if not dt_panel:
            dt_panel = DoorType(name="Panel Door", description="Panel design door", created_by="system", updated_by="system")
            db.add(dt_panel)
            db.flush()

            for tv, cpq in [(25, 70.0), (30, 85.0), (35, 100.0)]:
                db.add(DoorTypeThicknessOption(door_type_id=dt_panel.id, thickness_value=tv, cost_per_sqft=cpq, created_by="system", updated_by="system"))
            db.flush()

            db.add(DoorTypeService(door_type_id=dt_panel.id, service_id=svc_paint.id, required=False, created_by="system", updated_by="system"))
            db.add(DoorTypeService(door_type_id=dt_panel.id, service_id=svc_hardware.id, required=False, created_by="system", updated_by="system"))
            db.add(DoorTypeService(door_type_id=dt_panel.id, service_id=svc_glass.id, required=False, created_by="system", updated_by="system"))
            db.add(DoorTypeService(door_type_id=dt_panel.id, service_id=svc_install.id, required=False, created_by="system", updated_by="system"))
            db.flush()

            print("  ✅ Door Type: Panel Door (3 thicknesses + 4 services)")
        else:
            print("  ⏭️  Door Type: Panel Door exists")

        # --- Fire Door ---
        dt_fire = db.query(DoorType).filter(DoorType.name == "Fire Door").first()
        if not dt_fire:
            dt_fire = DoorType(name="Fire Door", description="Fire-rated safety door", created_by="system", updated_by="system")
            db.add(dt_fire)
            db.flush()

            for tv, cpq in [(35, 120.0), (44, 150.0)]:
                db.add(DoorTypeThicknessOption(door_type_id=dt_fire.id, thickness_value=tv, cost_per_sqft=cpq, created_by="system", updated_by="system"))
            db.flush()

            db.add(DoorTypeService(door_type_id=dt_fire.id, service_id=svc_hardware.id, required=True, created_by="system", updated_by="system"))
            db.add(DoorTypeService(door_type_id=dt_fire.id, service_id=svc_lock.id, required=True, created_by="system", updated_by="system"))
            db.add(DoorTypeService(door_type_id=dt_fire.id, service_id=svc_install.id, required=True, created_by="system", updated_by="system"))
            db.add(DoorTypeService(door_type_id=dt_fire.id, service_id=svc_cutting.id, required=False, created_by="system", updated_by="system"))
            # Use grouping
            db.add(DoorTypeService(door_type_id=dt_fire.id, grouping_id=grp_finish.id, required=False, created_by="system", updated_by="system"))
            db.flush()

            print("  ✅ Door Type: Fire Door (2 thicknesses + grouping)")
        else:
            print("  ⏭️  Door Type: Fire Door exists")

        # ==================================================================
        # 6. SAMPLE CUSTOMER
        # ==================================================================
        existing_customer = db.query(Customer).filter(Customer.name == "Test Customer").first()
        if not existing_customer:
            customer = Customer(
                name="Test Customer",
                email="test@example.com",
                phone="9876543210",
                address="123 Main Street",
                city="Mumbai",
                state="Maharashtra",
                postal_code="400001",
                country="India",
                created_by="system",
                updated_by="system",
            )
            db.add(customer)
            db.flush()
            print("  ✅ Sample customer seeded")
        else:
            print("  ⏭️  Sample customer exists")

        db.commit()
        print("\n🎉 Seed data complete!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seed failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

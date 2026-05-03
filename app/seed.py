"""Small idempotent seed dataset for Swagger demonstrations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FPGADevice, Mission, User, Vendor
from app.security import hash_password


DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo123"


def seed_database(db: Session) -> None:
    """Create example vendors, devices, and one mission if the database is empty."""
    demo_user = db.scalar(select(User).where(User.email == DEMO_EMAIL))
    if demo_user is None:
        demo_user = User(
            email=DEMO_EMAIL,
            full_name="Demo User",
            hashed_password=hash_password(DEMO_PASSWORD),
        )
        db.add(demo_user)
        db.flush()

    vendors = _seed_vendors(db)
    _seed_devices(db, vendors)
    _seed_mission(db, demo_user)
    db.commit()


def _seed_vendors(db: Session) -> dict[str, Vendor]:
    vendor_data = [
        ("Microchip", "United States", "https://www.microchip.com"),
        ("AMD Xilinx", "United States", "https://www.amd.com"),
        ("NanoXplore", "France", "https://www.nanoxplore.com"),
    ]

    vendors: dict[str, Vendor] = {}
    for name, country, website in vendor_data:
        vendor = db.scalar(select(Vendor).where(Vendor.name == name))
        if vendor is None:
            vendor = Vendor(name=name, country=country, website=website)
            db.add(vendor)
            db.flush()
        vendors[name] = vendor
    return vendors


def _seed_devices(db: Session, vendors: dict[str, Vendor]) -> None:
    device_data = [
        {
            "vendor": "Microchip",
            "name": "RTG4",
            "family": "RTG4",
            "logic_cells": 150000,
            "tid_krad": 100.0,
            "max_power_w": 4.5,
            "temp_min_c": -55,
            "temp_max_c": 125,
            "package": "Ceramic CGA",
            "is_space_grade": True,
        },
        {
            "vendor": "AMD Xilinx",
            "name": "XQRKU060",
            "family": "Kintex UltraScale",
            "logic_cells": 725000,
            "tid_krad": 100.0,
            "max_power_w": 18.0,
            "temp_min_c": -55,
            "temp_max_c": 125,
            "package": "Ceramic BGA",
            "is_space_grade": True,
        },
        {
            "vendor": "Microchip",
            "name": "RT PolarFire RTPF500T",
            "family": "PolarFire",
            "logic_cells": 480000,
            "tid_krad": 100.0,
            "max_power_w": 10.0,
            "temp_min_c": -55,
            "temp_max_c": 125,
            "package": "Ceramic BGA",
            "is_space_grade": True,
        },
        {
            "vendor": "NanoXplore",
            "name": "NG-MEDIUM",
            "family": "BRAVE",
            "logic_cells": 120000,
            "tid_krad": 50.0,
            "max_power_w": 5.0,
            "temp_min_c": -40,
            "temp_max_c": 125,
            "package": "CQFP",
            "is_space_grade": True,
        },
    ]

    for item in device_data:
        vendor = vendors[item["vendor"]]
        existing = db.scalar(
            select(FPGADevice).where(
                FPGADevice.vendor_id == vendor.id,
                FPGADevice.name == item["name"],
            )
        )
        if existing is None:
            payload = {key: value for key, value in item.items() if key != "vendor"}
            db.add(FPGADevice(vendor_id=vendor.id, **payload))


def _seed_mission(db: Session, demo_user: User) -> None:
    existing = db.scalar(select(Mission).where(Mission.name == "LEO Earth Observation Demo"))
    if existing is None:
        db.add(
            Mission(
                owner_id=demo_user.id,
                name="LEO Earth Observation Demo",
                orbit="LEO",
                description="Small satellite payload controller example.",
                required_tid_krad=50.0,
                min_logic_cells=100000,
                max_power_w=8.0,
                required_temp_min_c=-40,
                required_temp_max_c=85,
            )
        )

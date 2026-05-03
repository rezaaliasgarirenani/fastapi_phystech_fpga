"""SQLAlchemy ORM models for the FPGA selection domain."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class User(Base):
    """Registered API user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    missions: Mapped[list[Mission]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


class Vendor(Base):
    """FPGA device vendor."""

    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    devices: Mapped[list[FPGADevice]] = relationship(
        back_populates="vendor", cascade="all, delete-orphan"
    )


class FPGADevice(Base):
    """Radiation-resistant FPGA device description."""

    __tablename__ = "fpga_devices"
    __table_args__ = (UniqueConstraint("vendor_id", "name", name="uq_device_vendor_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    family: Mapped[str] = mapped_column(String(120), nullable=False)
    logic_cells: Mapped[int] = mapped_column(Integer, nullable=False)
    tid_krad: Mapped[float] = mapped_column(Float, nullable=False)
    max_power_w: Mapped[float] = mapped_column(Float, nullable=False)
    temp_min_c: Mapped[int] = mapped_column(Integer, nullable=False)
    temp_max_c: Mapped[int] = mapped_column(Integer, nullable=False)
    package: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_space_grade: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    vendor: Mapped[Vendor] = relationship(back_populates="devices")


class Mission(Base):
    """Space mission requirements for FPGA selection."""

    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    orbit: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    required_tid_krad: Mapped[float] = mapped_column(Float, nullable=False)
    min_logic_cells: Mapped[int] = mapped_column(Integer, nullable=False)
    max_power_w: Mapped[float] = mapped_column(Float, nullable=False)
    required_temp_min_c: Mapped[int] = mapped_column(Integer, nullable=False)
    required_temp_max_c: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    owner: Mapped[User] = relationship(back_populates="missions")

"""FPGA device CRUD routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import FPGADevice, Vendor
from app.schemas import FPGADeviceCreate, FPGADeviceRead, FPGADeviceUpdate
from app.security import get_current_user


router = APIRouter(prefix="/fpga-devices", tags=["fpga_devices"])


@router.post(
    "/",
    response_model=FPGADeviceRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_device(
    payload: FPGADeviceCreate,
    db: Annotated[Session, Depends(get_db)],
) -> FPGADevice:
    """Create an FPGA device."""
    _ensure_vendor_exists(payload.vendor_id, db)
    device = FPGADevice(**payload.model_dump())
    db.add(device)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device with this name already exists for the vendor",
        ) from exc
    db.refresh(device)
    return device


@router.get("/", response_model=list[FPGADeviceRead])
def list_devices(
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> list[FPGADevice]:
    """List FPGA devices."""
    statement = (
        select(FPGADevice)
        .options(selectinload(FPGADevice.vendor))
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


@router.get("/{device_id}", response_model=FPGADeviceRead)
def read_device(device_id: int, db: Annotated[Session, Depends(get_db)]) -> FPGADevice:
    """Read one FPGA device."""
    return _get_device_or_404(device_id, db)


@router.patch(
    "/{device_id}",
    response_model=FPGADeviceRead,
    dependencies=[Depends(get_current_user)],
)
def update_device(
    device_id: int,
    payload: FPGADeviceUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> FPGADevice:
    """Update one FPGA device."""
    device = _get_device_or_404(device_id, db)
    update_data = payload.model_dump(exclude_unset=True)
    if "vendor_id" in update_data:
        _ensure_vendor_exists(update_data["vendor_id"], db)

    for field, value in update_data.items():
        setattr(device, field, value)
    _validate_device_temperature(device)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device with this name already exists for the vendor",
        ) from exc
    db.refresh(device)
    return device


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def delete_device(device_id: int, db: Annotated[Session, Depends(get_db)]) -> Response:
    """Delete one FPGA device."""
    device = _get_device_or_404(device_id, db)
    db.delete(device)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _get_device_or_404(device_id: int, db: Session) -> FPGADevice:
    statement = (
        select(FPGADevice)
        .options(selectinload(FPGADevice.vendor))
        .where(FPGADevice.id == device_id)
    )
    device = db.scalar(statement)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


def _ensure_vendor_exists(vendor_id: int, db: Session) -> None:
    if db.get(Vendor, vendor_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")


def _validate_device_temperature(device: FPGADevice) -> None:
    if device.temp_min_c > device.temp_max_c:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="temp_min_c must be less than or equal to temp_max_c",
        )

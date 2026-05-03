"""Vendor CRUD routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Vendor
from app.schemas import VendorCreate, VendorRead, VendorUpdate
from app.security import get_current_user


router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.post(
    "/",
    response_model=VendorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_vendor(payload: VendorCreate, db: Annotated[Session, Depends(get_db)]) -> Vendor:
    """Create a vendor."""
    vendor = Vendor(**payload.model_dump())
    db.add(vendor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vendor with this name already exists",
        ) from exc
    db.refresh(vendor)
    return vendor


@router.get("/", response_model=list[VendorRead])
def list_vendors(
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> list[Vendor]:
    """List vendors."""
    return list(db.scalars(select(Vendor).offset(skip).limit(limit)).all())


@router.get("/{vendor_id}", response_model=VendorRead)
def read_vendor(vendor_id: int, db: Annotated[Session, Depends(get_db)]) -> Vendor:
    """Read one vendor."""
    return _get_vendor_or_404(vendor_id, db)


@router.patch(
    "/{vendor_id}",
    response_model=VendorRead,
    dependencies=[Depends(get_current_user)],
)
def update_vendor(
    vendor_id: int,
    payload: VendorUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Vendor:
    """Update one vendor."""
    vendor = _get_vendor_or_404(vendor_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vendor, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vendor with this name already exists",
        ) from exc
    db.refresh(vendor)
    return vendor


@router.delete(
    "/{vendor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def delete_vendor(vendor_id: int, db: Annotated[Session, Depends(get_db)]) -> Response:
    """Delete one vendor."""
    vendor = _get_vendor_or_404(vendor_id, db)
    db.delete(vendor)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _get_vendor_or_404(vendor_id: int, db: Session) -> Vendor:
    vendor = db.get(Vendor, vendor_id)
    if vendor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor

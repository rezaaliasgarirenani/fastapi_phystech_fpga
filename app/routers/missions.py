"""Mission CRUD routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mission, User
from app.schemas import MissionCreate, MissionRead, MissionUpdate
from app.security import get_current_user


router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("/", response_model=MissionRead, status_code=status.HTTP_201_CREATED)
def create_mission(
    payload: MissionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Mission:
    """Create a mission owned by the current user."""
    mission = Mission(owner_id=current_user.id, **payload.model_dump())
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


@router.get("/", response_model=list[MissionRead])
def list_missions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> list[Mission]:
    """List missions owned by the current user."""
    statement = (
        select(Mission)
        .where(Mission.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


@router.get("/{mission_id}", response_model=MissionRead)
def read_mission(
    mission_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Mission:
    """Read one mission owned by the current user."""
    mission = _get_mission_or_404(mission_id, db)
    _ensure_mission_owner(mission, current_user)
    return mission


@router.patch("/{mission_id}", response_model=MissionRead)
def update_mission(
    mission_id: int,
    payload: MissionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Mission:
    """Update one mission owned by the current user."""
    mission = _get_mission_or_404(mission_id, db)
    _ensure_mission_owner(mission, current_user)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(mission, field, value)
    _validate_mission_temperature(mission)

    db.commit()
    db.refresh(mission)
    return mission


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(
    mission_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Delete one mission owned by the current user."""
    mission = _get_mission_or_404(mission_id, db)
    _ensure_mission_owner(mission, current_user)
    db.delete(mission)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _get_mission_or_404(mission_id: int, db: Session) -> Mission:
    mission = db.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    return mission


def _ensure_mission_owner(mission: Mission, user: User) -> None:
    if mission.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own missions",
        )


def _validate_mission_temperature(mission: Mission) -> None:
    if mission.required_temp_min_c > mission.required_temp_max_c:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="required_temp_min_c must be less than or equal to required_temp_max_c",
        )

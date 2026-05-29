"""Business endpoint for FPGA recommendation."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import FPGADevice, Mission, User
from app.recommendation import rank_devices
from app.schemas import MissionRequirements, RecommendationRequest, RecommendationResult
from app.security import get_current_user


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/", response_model=list[RecommendationResult])
def recommend_from_request(
    payload: RecommendationRequest,
    db: Annotated[Session, Depends(get_db)],
) -> list[RecommendationResult]:
    """Recommend devices from ad hoc mission requirements."""
    devices = _load_candidate_devices(payload, db)
    return rank_devices(devices, payload)


@router.get("/mission/{mission_id}", response_model=list[RecommendationResult])
def recommend_for_mission(
    mission_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[RecommendationResult]:
    """Recommend devices for a stored mission owned by the current user."""
    mission = db.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    if mission.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only request recommendations for your own missions",
        )

    requirements = MissionRequirements.model_validate(mission, from_attributes=True)
    devices = _load_candidate_devices(requirements, db)
    return rank_devices(devices, requirements)


def _load_candidate_devices(
    requirements: MissionRequirements,
    db: Session,
) -> list[FPGADevice]:
    statement = (
        select(FPGADevice)
        .options(selectinload(FPGADevice.vendor))
        .where(
            FPGADevice.tid_krad >= requirements.required_tid_krad,
            FPGADevice.logic_cells >= requirements.min_logic_cells,
            FPGADevice.max_power_w <= requirements.max_power_w,
            FPGADevice.temp_min_c <= requirements.required_temp_min_c,
            FPGADevice.temp_max_c >= requirements.required_temp_max_c,
        )
    )
    return list(db.scalars(statement).all())

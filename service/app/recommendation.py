"""Simple FPGA ranking algorithm for mission requirements."""

from collections.abc import Sequence

from app.models import FPGADevice
from app.schemas import MissionRequirements, RecommendationResult


def rank_devices(
    devices: Sequence[FPGADevice],
    requirements: MissionRequirements,
) -> list[RecommendationResult]:
    """Return matching devices ranked by a transparent weighted score."""
    recommendations = [
        RecommendationResult(
            device=device,
            score=_calculate_score(device, requirements),
            reasons=_build_reasons(device, requirements),
        )
        for device in devices
        if _matches_requirements(device, requirements)
    ]
    return sorted(recommendations, key=lambda item: item.score, reverse=True)


def _matches_requirements(device: FPGADevice, requirements: MissionRequirements) -> bool:
    return (
        device.tid_krad >= requirements.required_tid_krad
        and device.logic_cells >= requirements.min_logic_cells
        and device.max_power_w <= requirements.max_power_w
        and device.temp_min_c <= requirements.required_temp_min_c
        and device.temp_max_c >= requirements.required_temp_max_c
    )


def _calculate_score(device: FPGADevice, requirements: MissionRequirements) -> float:
    radiation_margin = _capped_margin(device.tid_krad, requirements.required_tid_krad)
    logic_margin = _capped_margin(device.logic_cells, requirements.min_logic_cells)
    power_headroom = min(
        (requirements.max_power_w - device.max_power_w) / requirements.max_power_w,
        1.0,
    )
    temperature_headroom = min(
        (
            requirements.required_temp_min_c
            - device.temp_min_c
            + device.temp_max_c
            - requirements.required_temp_max_c
        )
        / 200,
        1.0,
    )

    score = (
        40.0
        + radiation_margin * 20.0
        + logic_margin * 15.0
        + power_headroom * 15.0
        + temperature_headroom * 5.0
        + (5.0 if device.is_space_grade else 0.0)
    )
    return round(min(score, 100.0), 2)


def _capped_margin(actual: float, required: float) -> float:
    if required <= 0:
        return 1.0
    return min((actual - required) / required, 1.0)


def _build_reasons(device: FPGADevice, requirements: MissionRequirements) -> list[str]:
    tid_margin = device.tid_krad - requirements.required_tid_krad
    logic_margin = device.logic_cells - requirements.min_logic_cells
    power_headroom = requirements.max_power_w - device.max_power_w
    cold_margin = requirements.required_temp_min_c - device.temp_min_c
    hot_margin = device.temp_max_c - requirements.required_temp_max_c

    return [
        f"TID margin: {tid_margin:.1f} krad",
        f"Logic margin: {logic_margin} cells",
        f"Power headroom: {power_headroom:.2f} W",
        f"Temperature margins: {cold_margin} C cold, {hot_margin} C hot",
    ]

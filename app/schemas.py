"""Pydantic schemas for request validation and response serialization."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class Token(BaseModel):
    """OAuth2 bearer token response."""

    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    """Common user fields."""

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)


class UserCreate(UserBase):
    """User registration payload."""

    password: str = Field(min_length=6, max_length=72)


class UserUpdate(BaseModel):
    """Partial user update payload."""

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    password: str | None = Field(default=None, min_length=6, max_length=72)
    is_active: bool | None = None


class UserRead(UserBase):
    """Public user response."""

    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VendorBase(BaseModel):
    """Common vendor fields."""

    name: str = Field(min_length=2, max_length=120)
    country: str | None = Field(default=None, max_length=80)
    website: str | None = Field(default=None, max_length=255)


class VendorCreate(VendorBase):
    """Vendor creation payload."""


class VendorUpdate(BaseModel):
    """Partial vendor update payload."""

    name: str | None = Field(default=None, min_length=2, max_length=120)
    country: str | None = Field(default=None, max_length=80)
    website: str | None = Field(default=None, max_length=255)


class VendorRead(VendorBase):
    """Vendor response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class FPGADeviceBase(BaseModel):
    """Common FPGA device fields."""

    name: str = Field(min_length=2, max_length=120)
    family: str = Field(min_length=2, max_length=120)
    vendor_id: int = Field(gt=0)
    logic_cells: int = Field(gt=0)
    tid_krad: float = Field(ge=0)
    max_power_w: float = Field(gt=0)
    temp_min_c: int = Field(ge=-273)
    temp_max_c: int = Field(le=250)
    package: str | None = Field(default=None, max_length=120)
    is_space_grade: bool = True

    @model_validator(mode="after")
    def validate_temperature_range(self):
        """Ensure the device temperature range is physically valid."""
        if self.temp_min_c > self.temp_max_c:
            raise ValueError("temp_min_c must be less than or equal to temp_max_c")
        return self


class FPGADeviceCreate(FPGADeviceBase):
    """FPGA device creation payload."""


class FPGADeviceUpdate(BaseModel):
    """Partial FPGA device update payload."""

    name: str | None = Field(default=None, min_length=2, max_length=120)
    family: str | None = Field(default=None, min_length=2, max_length=120)
    vendor_id: int | None = Field(default=None, gt=0)
    logic_cells: int | None = Field(default=None, gt=0)
    tid_krad: float | None = Field(default=None, ge=0)
    max_power_w: float | None = Field(default=None, gt=0)
    temp_min_c: int | None = Field(default=None, ge=-273)
    temp_max_c: int | None = Field(default=None, le=250)
    package: str | None = Field(default=None, max_length=120)
    is_space_grade: bool | None = None


class FPGADeviceRead(FPGADeviceBase):
    """FPGA device response."""

    id: int
    vendor: VendorRead | None = None

    model_config = ConfigDict(from_attributes=True)


class MissionRequirements(BaseModel):
    """Reusable mission requirement fields."""

    required_tid_krad: float = Field(ge=0, description="Required TID tolerance in krad")
    min_logic_cells: int = Field(gt=0, description="Minimum required logic cells")
    max_power_w: float = Field(gt=0, description="Maximum allowed power in watts")
    required_temp_min_c: int = Field(ge=-273, description="Minimum mission temperature")
    required_temp_max_c: int = Field(le=250, description="Maximum mission temperature")

    @model_validator(mode="after")
    def validate_temperature_range(self):
        """Ensure the requested mission temperature range is valid."""
        if self.required_temp_min_c > self.required_temp_max_c:
            raise ValueError(
                "required_temp_min_c must be less than or equal to required_temp_max_c"
            )
        return self


class MissionBase(MissionRequirements):
    """Common mission fields."""

    name: str = Field(min_length=2, max_length=120)
    orbit: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=500)


class MissionCreate(MissionBase):
    """Mission creation payload."""


class MissionUpdate(BaseModel):
    """Partial mission update payload."""

    name: str | None = Field(default=None, min_length=2, max_length=120)
    orbit: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    required_tid_krad: float | None = Field(default=None, ge=0)
    min_logic_cells: int | None = Field(default=None, gt=0)
    max_power_w: float | None = Field(default=None, gt=0)
    required_temp_min_c: int | None = Field(default=None, ge=-273)
    required_temp_max_c: int | None = Field(default=None, le=250)


class MissionRead(MissionBase):
    """Mission response."""

    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationRequest(MissionRequirements):
    """Ad hoc recommendation request."""


class RecommendationResult(BaseModel):
    """Ranked FPGA recommendation."""

    device: FPGADeviceRead
    score: float = Field(ge=0, le=100)
    reasons: list[str]

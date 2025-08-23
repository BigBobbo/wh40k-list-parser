"""Pydantic models for army lists."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class UnitEntry(BaseModel):
    """Model representing a unit entry in an army list."""

    unit_entry_id: UUID = Field(default_factory=uuid4, description="Unique entry ID")
    datasheet_id: str = Field(..., description="Reference to unit datasheet")
    quantity: int = Field(1, ge=1, description="Number of units")
    total_cost: int = Field(..., ge=0, description="Total point cost")
    wargear_selections: List[str] = Field(
        default_factory=list, description="Selected wargear options"
    )
    is_warlord: bool = Field(False, description="Whether this unit is the Warlord")
    enhancements: List[str] = Field(
        default_factory=list, description="Selected enhancements"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "datasheet_id": "000000001",
                "quantity": 1,
                "total_cost": 85,
                "wargear_selections": ["Power sword", "Storm shield"],
                "is_warlord": True,
                "enhancements": ["Artificer Armour"],
            }
        }


class ArmyList(BaseModel):
    """Model representing a complete army list."""

    list_id: UUID = Field(default_factory=uuid4, description="Unique list ID")
    name: str = Field(..., description="Army list name")
    faction_id: str = Field(..., description="Army faction")
    detachment_id: Optional[str] = Field(None, description="Selected detachment")
    point_limit: int = Field(2000, description="Point limit for the list")
    units: List[UnitEntry] = Field(
        default_factory=list, description="Units in the army"
    )
    total_points: int = Field(0, description="Total points cost")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Last update timestamp"
    )

    @field_validator("total_points", mode="before")
    @classmethod
    def calculate_total(cls, v: int, info) -> int:
        """Calculate total points from units if not provided."""
        if info.data.get("units"):
            return sum(unit.total_cost for unit in info.data["units"])
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "name": "My Space Marines Army",
                "faction_id": "SM",
                "detachment_id": "gladius",
                "point_limit": 2000,
                "units": [],
                "total_points": 0,
            }
        }


class ArmyListCreate(BaseModel):
    """Model for creating a new army list."""

    name: str = Field(..., description="Army list name")
    faction_id: str = Field(..., description="Army faction")
    detachment_id: Optional[str] = Field(None, description="Selected detachment")
    point_limit: int = Field(2000, description="Point limit for the list")


class ArmyListUpdate(BaseModel):
    """Model for updating an army list."""

    name: Optional[str] = Field(None, description="Army list name")
    detachment_id: Optional[str] = Field(None, description="Selected detachment")
    point_limit: Optional[int] = Field(None, description="Point limit for the list")

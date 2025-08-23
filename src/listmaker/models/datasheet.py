"""Pydantic models for unit datasheets."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RoleType(str, Enum):
    """Unit battlefield roles in Warhammer 40K."""

    HQ = "HQ"
    CHARACTERS = "Characters"
    TROOPS = "Troops"
    ELITES = "Elites"
    FAST_ATTACK = "Fast Attack"
    HEAVY_SUPPORT = "Heavy Support"
    DEDICATED_TRANSPORT = "Dedicated Transport"
    FLYER = "Flyer"
    FORTIFICATION = "Fortification"
    LORD_OF_WAR = "Lord of War"


class Datasheet(BaseModel):
    """Model representing a unit datasheet."""

    datasheet_id: str = Field(..., description="Unique datasheet identifier")
    name: str = Field(..., description="Unit name")
    faction_id: str = Field(..., description="Faction this unit belongs to")
    role: Optional[str] = Field(None, description="Battlefield role")
    base_cost: int = Field(0, description="Base point cost")
    is_legend: bool = Field(False, description="Whether unit is Legends")
    keywords: List[str] = Field(default_factory=list, description="Unit keywords")
    loadout: Optional[str] = Field(None, description="Default wargear loadout")
    transport_capacity: Optional[str] = Field(None, description="Transport capacity")
    damaged_description: Optional[str] = Field(None, description="Damaged profile")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "datasheet_id": "000000001",
                "name": "Space Marine Captain",
                "faction_id": "SM",
                "role": "HQ",
                "base_cost": 85,
                "is_legend": False,
                "keywords": ["INFANTRY", "CHARACTER", "CAPTAIN"],
            }
        }


class UnitComposition(BaseModel):
    """Model representing unit composition rules."""

    datasheet_id: str = Field(..., description="Reference to datasheet")
    line: int = Field(..., description="Line number for ordering")
    description: str = Field(..., description="Composition description")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "datasheet_id": "000000001",
                "line": 1,
                "description": "1 Space Marine Captain",
            }
        }


class ModelCost(BaseModel):
    """Model representing unit/model costs."""

    datasheet_id: str = Field(..., description="Reference to datasheet")
    line: int = Field(..., description="Line number for ordering")
    description: str = Field(..., description="Cost description")
    cost: int = Field(..., description="Point cost")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "datasheet_id": "000000001",
                "line": 1,
                "description": "1 model",
                "cost": 85,
            }
        }

"""Pydantic models for Warhammer 40K factions."""

from typing import Optional

from pydantic import BaseModel, Field


class Faction(BaseModel):
    """Model representing a Warhammer 40K faction."""

    faction_id: str = Field(..., description="Unique faction identifier")
    name: str = Field(..., description="Faction name")
    link: Optional[str] = Field(None, description="Link to faction information")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "faction_id": "SM",
                "name": "Space Marines",
                "link": "https://wahapedia.ru/wh40k10ed/factions/space-marines",
            }
        }

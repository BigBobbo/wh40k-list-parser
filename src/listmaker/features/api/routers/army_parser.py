"""API endpoints for army list parsing."""

from typing import Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....features.list_builder.army_parser import ArmyListParser
from ..dependencies import get_db

router = APIRouter(prefix="/parse", tags=["army-parser"])


class ArmyListParseRequest(BaseModel):
    """Request model for army list parsing."""
    
    army_text: str


class ArmyListParseResponse(BaseModel):
    """Response model for parsed army list."""
    
    faction: Dict
    units: Dict


@router.post("/", response_model=ArmyListParseResponse)
async def parse_army_list(
    request: ArmyListParseRequest,
    db: Session = Depends(get_db),
) -> ArmyListParseResponse:
    """Parse army list text into Godot-compatible format."""
    parser = ArmyListParser(db)
    result = parser.parse_army_list(request.army_text)
    
    return ArmyListParseResponse(
        faction=result["faction"],
        units=result["units"]
    )


@router.get("/example")
async def get_example_army_list() -> Dict:
    """Get an example army list for testing."""
    return {
        "example": """Adeptus Custodes
Strike Force (2000 points)
Shield Host

CHARACTERS

Blade Champion (135 points)
• Warlord
• 1x Vaultswords
• Enhancement: Auric Mantle

Blade Champion (120 points)
• 1x Vaultswords

BATTLELINE

Custodian Guard (170 points)
• 4x Custodian Guard
• 2x Guardian spear
1x Misericordia
2x Praesidium Shield
1x Sentinel blade
1x Vexilla

OTHER DATASHEETS

Caladius Grav-tank (215 points)
• 1x Armoured hull
1x Twin arachnus heavy blaze cannon
1x Twin lastrum bolt cannon

Custodian Wardens (260 points)
• 5x Custodian Warden
• 5x Guardian spear
1x Vexilla"""
    }
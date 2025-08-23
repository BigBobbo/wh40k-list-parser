"""API endpoints for faction management."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ....database.models import FactionModel
from ....models.faction import Faction
from ..dependencies import get_db

router = APIRouter(prefix="/factions", tags=["factions"])


@router.get("/", response_model=List[Faction])
async def get_factions(
    db: Session = Depends(get_db),
) -> List[Faction]:
    """Get all available factions."""
    factions = db.query(FactionModel).all()
    return [
        Faction(
            faction_id=f.faction_id,
            name=f.name,
            link=f.link,
        )
        for f in factions
    ]


@router.get("/{faction_id}", response_model=Faction)
async def get_faction(
    faction_id: str,
    db: Session = Depends(get_db),
) -> Faction:
    """Get a specific faction by ID."""
    faction = (
        db.query(FactionModel).filter(FactionModel.faction_id == faction_id).first()
    )

    if not faction:
        raise HTTPException(status_code=404, detail=f"Faction {faction_id} not found")

    return Faction(
        faction_id=faction.faction_id,
        name=faction.name,
        link=faction.link,
    )

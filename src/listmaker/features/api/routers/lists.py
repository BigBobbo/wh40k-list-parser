"""API endpoints for army list management."""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....features.list_builder.builder import ListBuilder
from ....features.list_builder.calculator import PointsCalculator
from ....features.list_builder.validator import ListValidator
from ....models.army_list import ArmyList, ArmyListCreate, UnitEntry
from ....models.validation import ValidationResult
from ..dependencies import get_db

router = APIRouter(prefix="/lists", tags=["lists"])


@router.post("/", response_model=ArmyList)
async def create_list(
    list_data: ArmyListCreate,
    db: Session = Depends(get_db),
) -> ArmyList:
    """Create a new army list."""
    builder = ListBuilder(db)

    # Check if faction exists
    from ....database.models import FactionModel

    faction = (
        db.query(FactionModel)
        .filter(FactionModel.faction_id == list_data.faction_id)
        .first()
    )
    if not faction:
        raise HTTPException(
            status_code=404, detail=f"Faction {list_data.faction_id} not found"
        )

    # Create the list
    army_list = builder.create_list(list_data)

    return ArmyList(
        list_id=army_list.list_id,
        name=army_list.name,
        faction_id=army_list.faction_id,
        detachment_id=army_list.detachment_id,
        point_limit=army_list.point_limit,
        units=[],
        total_points=0,
        created_at=army_list.created_at,
        updated_at=army_list.updated_at,
    )


@router.get("/", response_model=List[ArmyList])
async def get_lists(
    faction_id: Optional[str] = Query(None, description="Filter by faction"),
    db: Session = Depends(get_db),
) -> List[ArmyList]:
    """Get all army lists with optional filters."""
    from ....database.models import ArmyListModel

    query = db.query(ArmyListModel)

    if faction_id:
        query = query.filter(ArmyListModel.faction_id == faction_id)

    lists = query.all()
    result = []

    for army_list in lists:
        units = []
        for unit in army_list.units:
            units.append(
                UnitEntry(
                    unit_entry_id=unit.unit_entry_id,
                    datasheet_id=unit.datasheet_id,
                    quantity=unit.quantity,
                    total_cost=unit.total_cost,
                    wargear_selections=unit.wargear_selections or [],
                    is_warlord=unit.is_warlord,
                    enhancements=unit.enhancements or [],
                )
            )

        result.append(
            ArmyList(
                list_id=army_list.list_id,
                name=army_list.name,
                faction_id=army_list.faction_id,
                detachment_id=army_list.detachment_id,
                point_limit=army_list.point_limit,
                units=units,
                total_points=army_list.total_points,
                created_at=army_list.created_at,
                updated_at=army_list.updated_at,
            )
        )

    return result


@router.get("/{list_id}", response_model=ArmyList)
async def get_list(
    list_id: str,
    db: Session = Depends(get_db),
) -> ArmyList:
    """Get a specific army list by ID."""
    builder = ListBuilder(db)
    army_list = builder.get_list(list_id)

    if not army_list:
        raise HTTPException(status_code=404, detail=f"Army list {list_id} not found")

    units = []
    for unit in army_list.units:
        units.append(
            UnitEntry(
                unit_entry_id=unit.unit_entry_id,
                datasheet_id=unit.datasheet_id,
                quantity=unit.quantity,
                total_cost=unit.total_cost,
                wargear_selections=unit.wargear_selections or [],
                is_warlord=unit.is_warlord,
                enhancements=unit.enhancements or [],
            )
        )

    return ArmyList(
        list_id=army_list.list_id,
        name=army_list.name,
        faction_id=army_list.faction_id,
        detachment_id=army_list.detachment_id,
        point_limit=army_list.point_limit,
        units=units,
        total_points=army_list.total_points,
        created_at=army_list.created_at,
        updated_at=army_list.updated_at,
    )


@router.delete("/{list_id}")
async def delete_list(
    list_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Delete an army list."""
    builder = ListBuilder(db)
    success = builder.delete_list(list_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Army list {list_id} not found")

    return {"message": f"Army list {list_id} deleted successfully"}


@router.post("/{list_id}/units", response_model=UnitEntry)
async def add_unit(
    list_id: str,
    datasheet_id: str,
    quantity: int = 1,
    db: Session = Depends(get_db),
) -> UnitEntry:
    """Add a unit to an army list."""
    builder = ListBuilder(db)
    validator = ListValidator(db)

    # Validate the addition
    validation = validator.validate_unit_addition(list_id, datasheet_id, quantity)
    if not validation.is_valid:
        error_messages = [e.message for e in validation.errors]
        raise HTTPException(status_code=400, detail="; ".join(error_messages))

    # Add the unit
    try:
        unit_entry = builder.add_unit(list_id, datasheet_id, quantity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return UnitEntry(
        unit_entry_id=unit_entry.unit_entry_id,
        datasheet_id=unit_entry.datasheet_id,
        quantity=unit_entry.quantity,
        total_cost=unit_entry.total_cost,
        wargear_selections=unit_entry.wargear_selections or [],
        is_warlord=unit_entry.is_warlord,
        enhancements=unit_entry.enhancements or [],
    )


@router.delete("/{list_id}/units/{unit_entry_id}")
async def remove_unit(
    list_id: str,
    unit_entry_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Remove a unit from an army list."""
    builder = ListBuilder(db)
    success = builder.remove_unit(list_id, unit_entry_id)

    if not success:
        raise HTTPException(status_code=404, detail="Unit not found in list")

    return {"message": "Unit removed successfully"}


@router.put("/{list_id}/units/{unit_entry_id}/warlord")
async def set_warlord(
    list_id: str,
    unit_entry_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Set a unit as the army's warlord."""
    builder = ListBuilder(db)

    # Check if unit has CHARACTER keyword
    from ....database.models import DatasheetKeywordModel, UnitEntryModel

    unit = (
        db.query(UnitEntryModel)
        .filter(
            UnitEntryModel.unit_entry_id == unit_entry_id,
            UnitEntryModel.list_id == list_id,
        )
        .first()
    )

    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found in list")

    keywords = (
        db.query(DatasheetKeywordModel)
        .filter(DatasheetKeywordModel.datasheet_id == unit.datasheet_id)
        .all()
    )

    if not any(k.keyword == "CHARACTER" for k in keywords):
        raise HTTPException(
            status_code=400, detail="Only CHARACTER units can be Warlords"
        )

    success = builder.set_warlord(list_id, unit_entry_id)

    if not success:
        raise HTTPException(status_code=404, detail="Failed to set warlord")

    return {"message": "Warlord set successfully"}


@router.get("/{list_id}/validate", response_model=ValidationResult)
async def validate_list(
    list_id: str,
    db: Session = Depends(get_db),
) -> ValidationResult:
    """Validate an army list against 10th edition rules."""
    validator = ListValidator(db)
    return validator.validate_list(list_id)


@router.get("/{list_id}/breakdown")
async def get_points_breakdown(
    list_id: str,
    db: Session = Depends(get_db),
):
    """Get detailed points breakdown for an army list."""
    calculator = PointsCalculator(db)
    return calculator.get_points_breakdown(list_id)

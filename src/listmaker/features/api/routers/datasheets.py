"""API endpoints for datasheet management."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....database.models import (
    DatasheetKeywordModel,
    DatasheetModel,
    ModelCostModel,
    UnitCompositionModel,
)
from ....models.datasheet import Datasheet, ModelCost, UnitComposition
from ..dependencies import get_db

router = APIRouter(prefix="/datasheets", tags=["datasheets"])


@router.get("/", response_model=List[Datasheet])
async def get_datasheets(
    faction_id: Optional[str] = Query(None, description="Filter by faction"),
    role: Optional[str] = Query(None, description="Filter by battlefield role"),
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    db: Session = Depends(get_db),
) -> List[Datasheet]:
    """Get all datasheets with optional filters."""
    query = db.query(DatasheetModel)

    # Apply filters
    if faction_id:
        query = query.filter(DatasheetModel.faction_id == faction_id)
    if role:
        query = query.filter(DatasheetModel.role == role)

    datasheets = query.all()
    result = []

    for d in datasheets:
        # Get keywords
        keywords = (
            db.query(DatasheetKeywordModel)
            .filter(DatasheetKeywordModel.datasheet_id == d.datasheet_id)
            .all()
        )
        keyword_list = [k.keyword for k in keywords]

        # Apply keyword filter if specified
        if keyword and keyword.upper() not in keyword_list:
            continue

        # Get base cost
        base_cost = (
            db.query(ModelCostModel)
            .filter(ModelCostModel.datasheet_id == d.datasheet_id)
            .order_by(ModelCostModel.line)
            .first()
        )

        result.append(
            Datasheet(
                datasheet_id=d.datasheet_id,
                name=d.name,
                faction_id=d.faction_id,
                role=d.role,
                base_cost=base_cost.cost if base_cost else 0,
                is_legend=d.is_legend,
                keywords=keyword_list,
                loadout=d.loadout,
                transport_capacity=d.transport_capacity,
                damaged_description=d.damaged_description,
            )
        )

    return result


@router.get("/{datasheet_id}", response_model=Datasheet)
async def get_datasheet(
    datasheet_id: str,
    db: Session = Depends(get_db),
) -> Datasheet:
    """Get a specific datasheet by ID."""
    datasheet = (
        db.query(DatasheetModel)
        .filter(DatasheetModel.datasheet_id == datasheet_id)
        .first()
    )

    if not datasheet:
        raise HTTPException(
            status_code=404, detail=f"Datasheet {datasheet_id} not found"
        )

    # Get keywords
    keywords = (
        db.query(DatasheetKeywordModel)
        .filter(DatasheetKeywordModel.datasheet_id == datasheet_id)
        .all()
    )

    # Get base cost
    base_cost = (
        db.query(ModelCostModel)
        .filter(ModelCostModel.datasheet_id == datasheet_id)
        .order_by(ModelCostModel.line)
        .first()
    )

    return Datasheet(
        datasheet_id=datasheet.datasheet_id,
        name=datasheet.name,
        faction_id=datasheet.faction_id,
        role=datasheet.role,
        base_cost=base_cost.cost if base_cost else 0,
        is_legend=datasheet.is_legend,
        keywords=[k.keyword for k in keywords],
        loadout=datasheet.loadout,
        transport_capacity=datasheet.transport_capacity,
        damaged_description=datasheet.damaged_description,
    )


@router.get("/{datasheet_id}/costs", response_model=List[ModelCost])
async def get_datasheet_costs(
    datasheet_id: str,
    db: Session = Depends(get_db),
) -> List[ModelCost]:
    """Get all cost options for a datasheet."""
    costs = (
        db.query(ModelCostModel)
        .filter(ModelCostModel.datasheet_id == datasheet_id)
        .order_by(ModelCostModel.line)
        .all()
    )

    if not costs:
        raise HTTPException(
            status_code=404, detail=f"No costs found for datasheet {datasheet_id}"
        )

    return [
        ModelCost(
            datasheet_id=c.datasheet_id,
            line=c.line,
            description=c.description,
            cost=c.cost,
        )
        for c in costs
    ]


@router.get("/{datasheet_id}/composition", response_model=List[UnitComposition])
async def get_datasheet_composition(
    datasheet_id: str,
    db: Session = Depends(get_db),
) -> List[UnitComposition]:
    """Get unit composition for a datasheet."""
    compositions = (
        db.query(UnitCompositionModel)
        .filter(UnitCompositionModel.datasheet_id == datasheet_id)
        .order_by(UnitCompositionModel.line)
        .all()
    )

    if not compositions:
        raise HTTPException(
            status_code=404,
            detail=f"No composition found for datasheet {datasheet_id}",
        )

    return [
        UnitComposition(
            datasheet_id=c.datasheet_id,
            line=c.line,
            description=c.description,
        )
        for c in compositions
    ]

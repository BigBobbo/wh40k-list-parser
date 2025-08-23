"""Core list building logic for Warhammer 40K armies."""

from typing import List, Optional

from sqlalchemy.orm import Session

from ...database.models import (
    ArmyListModel,
    DatasheetModel,
    ModelCostModel,
    UnitEntryModel,
)
from ...models import ArmyListCreate


class ListBuilder:
    """Builder for creating and managing army lists."""

    def __init__(self, session: Session):
        """Initialize builder with database session."""
        self.session = session

    def create_list(self, list_data: ArmyListCreate) -> ArmyListModel:
        """Create a new army list."""
        # Create database model
        army_list = ArmyListModel(
            name=list_data.name,
            faction_id=list_data.faction_id,
            detachment_id=list_data.detachment_id,
            point_limit=list_data.point_limit,
            total_points=0,
        )

        self.session.add(army_list)
        self.session.commit()
        self.session.refresh(army_list)

        return army_list

    def get_list(self, list_id: str) -> Optional[ArmyListModel]:
        """Get an army list by ID."""
        return (
            self.session.query(ArmyListModel)
            .filter(ArmyListModel.list_id == list_id)
            .first()
        )

    def get_lists_by_faction(self, faction_id: str) -> List[ArmyListModel]:
        """Get all army lists for a faction."""
        return (
            self.session.query(ArmyListModel)
            .filter(ArmyListModel.faction_id == faction_id)
            .all()
        )

    def add_unit(
        self, list_id: str, datasheet_id: str, quantity: int = 1
    ) -> UnitEntryModel:
        """Add a unit to an army list."""
        # Get the army list
        army_list = self.get_list(list_id)
        if not army_list:
            raise ValueError(f"Army list {list_id} not found")

        # Get the datasheet
        datasheet = (
            self.session.query(DatasheetModel)
            .filter(DatasheetModel.datasheet_id == datasheet_id)
            .first()
        )
        if not datasheet:
            raise ValueError(f"Datasheet {datasheet_id} not found")

        # Check faction compatibility
        if datasheet.faction_id != army_list.faction_id:
            # Allow some cross-faction units (e.g., Imperial Agents with Space Marines)
            # This would need more complex logic in production
            pass

        # Calculate cost
        cost = self.calculate_unit_cost(datasheet_id, quantity)

        # Create unit entry
        unit_entry = UnitEntryModel(
            list_id=list_id,
            datasheet_id=datasheet_id,
            quantity=quantity,
            total_cost=cost,
            is_warlord=False,
            wargear_selections=[],
            enhancements=[],
        )

        self.session.add(unit_entry)

        # Update army list total points
        army_list.total_points += cost
        army_list.updated_at = army_list.updated_at  # Trigger update

        self.session.commit()
        self.session.refresh(unit_entry)

        return unit_entry

    def remove_unit(self, list_id: str, unit_entry_id: str) -> bool:
        """Remove a unit from an army list."""
        # Get the unit entry
        unit_entry = (
            self.session.query(UnitEntryModel)
            .filter(
                UnitEntryModel.unit_entry_id == unit_entry_id,
                UnitEntryModel.list_id == list_id,
            )
            .first()
        )

        if not unit_entry:
            return False

        # Get the army list and update points
        army_list = self.get_list(list_id)
        if army_list:
            army_list.total_points -= unit_entry.total_cost
            army_list.updated_at = army_list.updated_at  # Trigger update

        # Delete the unit entry
        self.session.delete(unit_entry)
        self.session.commit()

        return True

    def set_warlord(self, list_id: str, unit_entry_id: str) -> bool:
        """Set a unit as the army's warlord."""
        # Get all units in the list
        units = (
            self.session.query(UnitEntryModel)
            .filter(UnitEntryModel.list_id == list_id)
            .all()
        )

        # Clear existing warlord and set new one
        for unit in units:
            unit.is_warlord = unit.unit_entry_id == unit_entry_id

        self.session.commit()
        return True

    def calculate_unit_cost(self, datasheet_id: str, quantity: int = 1) -> int:
        """Calculate the cost of a unit based on model count."""
        # Get cost data
        costs = (
            self.session.query(ModelCostModel)
            .filter(ModelCostModel.datasheet_id == datasheet_id)
            .order_by(ModelCostModel.line)
            .all()
        )

        if not costs:
            return 0

        # Simple cost calculation - use first cost entry
        # In production, this would need to handle variable unit sizes
        base_cost = costs[0].cost if costs else 0
        return base_cost * quantity

    def update_list_points(self, list_id: str) -> int:
        """Recalculate and update total points for a list."""
        army_list = self.get_list(list_id)
        if not army_list:
            raise ValueError(f"Army list {list_id} not found")

        # Calculate total from all units
        total = sum(unit.total_cost for unit in army_list.units)
        army_list.total_points = total

        self.session.commit()
        return total

    def delete_list(self, list_id: str) -> bool:
        """Delete an army list."""
        army_list = self.get_list(list_id)
        if not army_list:
            return False

        self.session.delete(army_list)
        self.session.commit()
        return True

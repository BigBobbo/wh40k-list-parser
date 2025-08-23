"""Points calculator for Warhammer 40K units and upgrades."""

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from ...database.models import DatasheetModel, ModelCostModel


class PointsCalculator:
    """Calculate points for units and upgrades."""

    def __init__(self, session: Session):
        """Initialize calculator with database session."""
        self.session = session

    def get_unit_base_cost(self, datasheet_id: str) -> int:
        """Get the base cost of a unit."""
        costs = (
            self.session.query(ModelCostModel)
            .filter(ModelCostModel.datasheet_id == datasheet_id)
            .order_by(ModelCostModel.line)
            .first()
        )

        return costs.cost if costs else 0

    def get_unit_cost_options(self, datasheet_id: str) -> List[Dict[str, any]]:
        """Get all cost options for a unit (different unit sizes)."""
        costs = (
            self.session.query(ModelCostModel)
            .filter(ModelCostModel.datasheet_id == datasheet_id)
            .order_by(ModelCostModel.line)
            .all()
        )

        return [
            {
                "line": cost.line,
                "description": cost.description,
                "cost": cost.cost,
            }
            for cost in costs
        ]

    def calculate_unit_cost(
        self,
        datasheet_id: str,
        model_count: int = 1,
        wargear_selections: List[str] = None,
        enhancements: List[str] = None,
    ) -> int:
        """Calculate total cost for a unit with upgrades."""
        # Get base cost options
        cost_options = self.get_unit_cost_options(datasheet_id)

        if not cost_options:
            return 0

        # Find the appropriate cost based on model count
        # This is simplified - in reality, we'd need to parse the description
        # to match model counts (e.g., "5 models" -> 100 points)
        base_cost = 0
        for option in cost_options:
            # Try to extract model count from description
            description = option["description"].lower()
            if f"{model_count} model" in description:
                base_cost = option["cost"]
                break

        # If no exact match, use the first option as default
        if base_cost == 0 and cost_options:
            base_cost = cost_options[0]["cost"]

        # Add wargear costs (would need wargear cost data)
        wargear_cost = 0
        if wargear_selections:
            # In production, look up wargear costs from database
            pass

        # Add enhancement costs (would need enhancement cost data)
        enhancement_cost = 0
        if enhancements:
            # In production, look up enhancement costs from database
            pass

        return base_cost + wargear_cost + enhancement_cost

    def calculate_list_total(self, list_id: str) -> int:
        """Calculate total points for an entire army list."""
        from ...database.models import UnitEntryModel

        units = (
            self.session.query(UnitEntryModel)
            .filter(UnitEntryModel.list_id == list_id)
            .all()
        )

        total = 0
        for unit in units:
            total += unit.total_cost

        return total

    def get_points_breakdown(self, list_id: str) -> Dict[str, Any]:
        """Get detailed points breakdown for an army list."""
        from ...database.models import UnitEntryModel

        units = (
            self.session.query(UnitEntryModel)
            .filter(UnitEntryModel.list_id == list_id)
            .all()
        )

        breakdown = {
            "units": [],
            "total": 0,
            "by_role": {},
        }

        for unit in units:
            # Get datasheet for role information
            datasheet = (
                self.session.query(DatasheetModel)
                .filter(DatasheetModel.datasheet_id == unit.datasheet_id)
                .first()
            )

            unit_info = {
                "name": datasheet.name if datasheet else "Unknown",
                "role": datasheet.role if datasheet else "Unknown",
                "cost": unit.total_cost,
                "quantity": unit.quantity,
            }

            breakdown["units"].append(unit_info)
            breakdown["total"] += unit.total_cost

            # Group by role
            role = unit_info["role"] or "Other"
            if role not in breakdown["by_role"]:
                breakdown["by_role"][role] = {"count": 0, "points": 0}

            breakdown["by_role"][role]["count"] += unit.quantity
            breakdown["by_role"][role]["points"] += unit.total_cost

        return breakdown

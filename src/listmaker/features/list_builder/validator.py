"""Validation engine for Warhammer 40K 10th edition army list rules."""

from collections import Counter
from typing import List

from sqlalchemy.orm import Session

from ...database.models import (
    ArmyListModel,
    DatasheetKeywordModel,
    DatasheetModel,
)
from ...models.validation import (
    ValidationError,
    ValidationResult,
    ValidationWarning,
)


class ListValidator:
    """Validate army lists against 10th edition rules."""

    def __init__(self, session: Session):
        """Initialize validator with database session."""
        self.session = session

    def validate_list(self, list_id: str) -> ValidationResult:
        """Validate an army list against all rules."""
        errors: List[ValidationError] = []
        warnings: List[ValidationWarning] = []

        # Get the army list
        army_list = (
            self.session.query(ArmyListModel)
            .filter(ArmyListModel.list_id == list_id)
            .first()
        )

        if not army_list:
            errors.append(
                ValidationError(
                    code="LIST_NOT_FOUND",
                    message=f"Army list {list_id} not found",
                    field="list_id",
                )
            )
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Run all validation checks
        self._check_point_limit(army_list, errors)
        self._check_warlord(army_list, errors)
        self._check_datasheet_limits(army_list, errors)
        self._check_minimum_units(army_list, warnings)
        self._check_faction_consistency(army_list, errors)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _check_point_limit(
        self, army_list: ArmyListModel, errors: List[ValidationError]
    ) -> None:
        """Check if army list exceeds point limit."""
        if army_list.total_points > army_list.point_limit:
            errors.append(
                ValidationError(
                    code="EXCEEDS_POINT_LIMIT",
                    message=(
                        f"Army list exceeds {army_list.point_limit} point limit "
                        f"(current: {army_list.total_points})"
                    ),
                    field="total_points",
                )
            )

    def _check_warlord(
        self, army_list: ArmyListModel, errors: List[ValidationError]
    ) -> None:
        """Check if army has a warlord."""
        has_warlord = any(unit.is_warlord for unit in army_list.units)

        if not has_warlord and army_list.units:
            # Check if any unit can be a warlord (CHARACTER keyword)
            has_character = False
            for unit in army_list.units:
                datasheet = (
                    self.session.query(DatasheetModel)
                    .filter(DatasheetModel.datasheet_id == unit.datasheet_id)
                    .first()
                )
                if datasheet:
                    keywords = (
                        self.session.query(DatasheetKeywordModel)
                        .filter(
                            DatasheetKeywordModel.datasheet_id == datasheet.datasheet_id
                        )
                        .all()
                    )
                    if any(k.keyword == "CHARACTER" for k in keywords):
                        has_character = True
                        break

            if has_character:
                errors.append(
                    ValidationError(
                        code="NO_WARLORD",
                        message="Army must have a unit designated as Warlord",
                        field="units",
                    )
                )

    def _check_datasheet_limits(
        self, army_list: ArmyListModel, errors: List[ValidationError]
    ) -> None:
        """Check Rule of Three (max 3 of same datasheet, 6 for Battleline)."""
        # Count datasheets
        datasheet_counts = Counter(unit.datasheet_id for unit in army_list.units)

        for datasheet_id, count in datasheet_counts.items():
            # Get datasheet and keywords
            datasheet = (
                self.session.query(DatasheetModel)
                .filter(DatasheetModel.datasheet_id == datasheet_id)
                .first()
            )

            if not datasheet:
                continue

            # Check if unit has BATTLELINE keyword
            keywords = (
                self.session.query(DatasheetKeywordModel)
                .filter(DatasheetKeywordModel.datasheet_id == datasheet_id)
                .all()
            )
            is_battleline = any(k.keyword == "BATTLELINE" for k in keywords)

            # Apply limits
            max_allowed = 6 if is_battleline else 3

            if count > max_allowed:
                errors.append(
                    ValidationError(
                        code="EXCEEDS_DATASHEET_LIMIT",
                        message=(
                            f"Too many {datasheet.name} units: {count}/{max_allowed} "
                            f"({'Battleline' if is_battleline else 'Standard'} limit)"
                        ),
                        field="units",
                    )
                )

    def _check_minimum_units(
        self, army_list: ArmyListModel, warnings: List[ValidationWarning]
    ) -> None:
        """Check for recommended minimum units."""
        if not army_list.units:
            warnings.append(
                ValidationWarning(
                    code="NO_UNITS",
                    message="Army list has no units",
                    field="units",
                )
            )
            return

        # Check for Battleline units (recommended but not required in 10th)
        has_battleline = False
        for unit in army_list.units:
            keywords = (
                self.session.query(DatasheetKeywordModel)
                .filter(DatasheetKeywordModel.datasheet_id == unit.datasheet_id)
                .all()
            )
            if any(k.keyword == "BATTLELINE" for k in keywords):
                has_battleline = True
                break

        if not has_battleline:
            warnings.append(
                ValidationWarning(
                    code="NO_BATTLELINE",
                    message="Army has no Battleline units (recommended for balanced lists)",
                    field="units",
                )
            )

    def _check_faction_consistency(
        self, army_list: ArmyListModel, errors: List[ValidationError]
    ) -> None:
        """Check that all units belong to compatible factions."""
        army_faction = army_list.faction_id

        for unit in army_list.units:
            datasheet = (
                self.session.query(DatasheetModel)
                .filter(DatasheetModel.datasheet_id == unit.datasheet_id)
                .first()
            )

            if not datasheet:
                continue

            # Check if unit faction matches army faction
            if datasheet.faction_id != army_faction:
                # Check for allowed allied factions
                # In 10th edition, some factions can ally (e.g., Imperial factions)
                if not self._are_factions_allied(army_faction, datasheet.faction_id):
                    errors.append(
                        ValidationError(
                            code="FACTION_MISMATCH",
                            message=(
                                f"Unit {datasheet.name} (faction: {datasheet.faction_id}) "
                                f"cannot be included in {army_faction} army"
                            ),
                            field="units",
                        )
                    )

    def _are_factions_allied(self, faction1: str, faction2: str) -> bool:
        """Check if two factions can be allied."""
        # Imperial factions can ally with each other
        imperial_factions = ["SM", "AM", "AS", "GK", "AC", "AoI", "QI"]

        # Chaos factions can ally with each other
        chaos_factions = ["CSM", "DG", "TS", "WE", "EC", "CD", "QT"]

        # Check if both factions are Imperial
        if faction1 in imperial_factions and faction2 in imperial_factions:
            return True

        # Check if both factions are Chaos
        if faction1 in chaos_factions and faction2 in chaos_factions:
            return True

        # Otherwise, factions cannot ally
        return False

    def validate_unit_addition(
        self,
        list_id: str,
        datasheet_id: str,
        quantity: int = 1,
    ) -> ValidationResult:
        """Validate if a unit can be added to a list."""
        errors: List[ValidationError] = []
        warnings: List[ValidationWarning] = []

        # Get the army list
        army_list = (
            self.session.query(ArmyListModel)
            .filter(ArmyListModel.list_id == list_id)
            .first()
        )

        if not army_list:
            errors.append(
                ValidationError(
                    code="LIST_NOT_FOUND",
                    message=f"Army list {list_id} not found",
                    field="list_id",
                )
            )
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Get the datasheet
        datasheet = (
            self.session.query(DatasheetModel)
            .filter(DatasheetModel.datasheet_id == datasheet_id)
            .first()
        )

        if not datasheet:
            errors.append(
                ValidationError(
                    code="DATASHEET_NOT_FOUND",
                    message=f"Datasheet {datasheet_id} not found",
                    field="datasheet_id",
                )
            )
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Check faction compatibility
        if datasheet.faction_id != army_list.faction_id:
            if not self._are_factions_allied(
                army_list.faction_id, datasheet.faction_id
            ):
                errors.append(
                    ValidationError(
                        code="FACTION_MISMATCH",
                        message=(
                            f"Unit {datasheet.name} cannot be added to "
                            f"{army_list.faction_id} army"
                        ),
                        field="datasheet_id",
                    )
                )

        # Check datasheet limits (including the new unit)
        current_count = sum(
            1 for unit in army_list.units if unit.datasheet_id == datasheet_id
        )
        new_count = current_count + quantity

        keywords = (
            self.session.query(DatasheetKeywordModel)
            .filter(DatasheetKeywordModel.datasheet_id == datasheet_id)
            .all()
        )
        is_battleline = any(k.keyword == "BATTLELINE" for k in keywords)
        max_allowed = 6 if is_battleline else 3

        if new_count > max_allowed:
            errors.append(
                ValidationError(
                    code="WOULD_EXCEED_DATASHEET_LIMIT",
                    message=(
                        f"Adding {quantity} {datasheet.name} would exceed limit "
                        f"({new_count}/{max_allowed})"
                    ),
                    field="quantity",
                )
            )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

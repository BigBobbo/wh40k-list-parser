"""Tests for list validator."""

import pytest

from ....database.models import (
    ArmyListModel,
    DatasheetKeywordModel,
    DatasheetModel,
    FactionModel,
    UnitEntryModel,
)
from ..validator import ListValidator


@pytest.fixture
def validator(test_session):
    """Create a validator instance."""
    return ListValidator(test_session)


@pytest.fixture
def sample_data(test_session):
    """Create sample data for testing."""
    # Create faction
    faction = FactionModel(
        faction_id="SM",
        name="Space Marines",
    )
    test_session.add(faction)

    # Create datasheet
    datasheet = DatasheetModel(
        datasheet_id="000000001",
        name="Space Marine Captain",
        faction_id="SM",
        role="HQ",
        is_legend=False,
    )
    test_session.add(datasheet)

    # Add CHARACTER keyword
    keyword = DatasheetKeywordModel(
        datasheet_id="000000001",
        keyword="CHARACTER",
    )
    test_session.add(keyword)

    # Create army list
    army_list = ArmyListModel(
        list_id="test-list-1",
        name="Test Army",
        faction_id="SM",
        point_limit=2000,
        total_points=85,
    )
    test_session.add(army_list)

    # Add unit to army list
    unit = UnitEntryModel(
        unit_entry_id="unit-1",
        list_id="test-list-1",
        datasheet_id="000000001",
        quantity=1,
        total_cost=85,
        is_warlord=True,
    )
    test_session.add(unit)

    test_session.commit()
    return {"list_id": "test-list-1", "datasheet_id": "000000001"}


def test_validate_valid_list(validator, sample_data):
    """Test validating a valid army list."""
    result = validator.validate_list(sample_data["list_id"])

    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validate_nonexistent_list(validator):
    """Test validating a nonexistent army list."""
    result = validator.validate_list("nonexistent")

    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].code == "LIST_NOT_FOUND"


def test_validate_point_limit_exceeded(validator, test_session, sample_data):
    """Test validating list that exceeds point limit."""
    # Update army list to exceed point limit
    army_list = (
        test_session.query(ArmyListModel)
        .filter(ArmyListModel.list_id == sample_data["list_id"])
        .first()
    )
    army_list.total_points = 2500  # Exceeds 2000 point limit
    test_session.commit()

    result = validator.validate_list(sample_data["list_id"])

    assert result.is_valid is False
    assert any(error.code == "EXCEEDS_POINT_LIMIT" for error in result.errors)


def test_validate_unit_addition_valid(validator, sample_data):
    """Test validating a valid unit addition."""
    result = validator.validate_unit_addition(
        sample_data["list_id"],
        sample_data["datasheet_id"],
        1,
    )

    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validate_unit_addition_nonexistent_list(validator, sample_data):
    """Test validating unit addition to nonexistent list."""
    result = validator.validate_unit_addition(
        "nonexistent",
        sample_data["datasheet_id"],
        1,
    )

    assert result.is_valid is False
    assert any(error.code == "LIST_NOT_FOUND" for error in result.errors)


def test_validate_unit_addition_nonexistent_datasheet(validator, sample_data):
    """Test validating addition of nonexistent datasheet."""
    result = validator.validate_unit_addition(
        sample_data["list_id"],
        "nonexistent",
        1,
    )

    assert result.is_valid is False
    assert any(error.code == "DATASHEET_NOT_FOUND" for error in result.errors)

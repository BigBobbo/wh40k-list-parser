"""Tests for army list models."""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from ..army_list import ArmyList, ArmyListCreate, UnitEntry


def test_unit_entry_valid():
    """Test creating a valid unit entry."""
    unit = UnitEntry(
        datasheet_id="000000001",
        quantity=1,
        total_cost=85,
        wargear_selections=["Power sword"],
        is_warlord=True,
    )

    assert unit.datasheet_id == "000000001"
    assert unit.quantity == 1
    assert unit.total_cost == 85
    assert unit.wargear_selections == ["Power sword"]
    assert unit.is_warlord is True
    assert isinstance(unit.unit_entry_id, type(uuid4()))


def test_unit_entry_defaults():
    """Test unit entry with default values."""
    unit = UnitEntry(
        datasheet_id="000000001",
        total_cost=85,
    )

    assert unit.quantity == 1
    assert unit.wargear_selections == []
    assert unit.is_warlord is False
    assert unit.enhancements == []


def test_army_list_create():
    """Test creating an army list creation request."""
    list_create = ArmyListCreate(
        name="My Army",
        faction_id="SM",
        point_limit=2000,
    )

    assert list_create.name == "My Army"
    assert list_create.faction_id == "SM"
    assert list_create.point_limit == 2000
    assert list_create.detachment_id is None


def test_army_list_valid():
    """Test creating a valid army list."""
    units = [
        UnitEntry(
            datasheet_id="000000001",
            total_cost=85,
            is_warlord=True,
        ),
        UnitEntry(
            datasheet_id="000000002",
            total_cost=200,
        ),
    ]

    army_list = ArmyList(
        name="Test Army",
        faction_id="SM",
        units=units,
        point_limit=2000,
    )

    assert army_list.name == "Test Army"
    assert army_list.faction_id == "SM"
    assert len(army_list.units) == 2
    assert army_list.total_points == 285  # Auto-calculated
    assert isinstance(army_list.created_at, datetime)


def test_army_list_validation_errors():
    """Test army list validation errors."""
    with pytest.raises(ValidationError):
        ArmyList(faction_id="SM", point_limit=2000)  # Missing name

    with pytest.raises(ValidationError):
        ArmyList(name="Test", point_limit=2000)  # Missing faction_id

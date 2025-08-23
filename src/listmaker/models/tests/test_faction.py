"""Tests for faction models."""

import pytest
from pydantic import ValidationError

from ..faction import Faction


def test_faction_valid():
    """Test creating a valid faction."""
    faction = Faction(
        faction_id="SM",
        name="Space Marines",
        link="https://example.com",
    )

    assert faction.faction_id == "SM"
    assert faction.name == "Space Marines"
    assert faction.link == "https://example.com"


def test_faction_minimal():
    """Test creating a faction with minimal data."""
    faction = Faction(
        faction_id="SM",
        name="Space Marines",
    )

    assert faction.faction_id == "SM"
    assert faction.name == "Space Marines"
    assert faction.link is None


def test_faction_validation_error():
    """Test faction validation with invalid data."""
    with pytest.raises(ValidationError):
        Faction(name="Space Marines")  # Missing faction_id

    with pytest.raises(ValidationError):
        Faction(faction_id="SM")  # Missing name

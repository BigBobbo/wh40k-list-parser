"""Tests for CSV parser."""

import tempfile
from pathlib import Path

import pytest

from ..csv_parser import WahapediaCSVParser


@pytest.fixture
def temp_csv_dir():
    """Create a temporary directory with sample CSV files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create sample Factions.csv
        factions_data = """id|name|link|
SM|Space Marines|https://wahapedia.ru/wh40k10ed/factions/space-marines|
AM|Astra Militarum|https://wahapedia.ru/wh40k10ed/factions/astra-militarum|"""

        with open(temp_path / "Factions.csv", "w", encoding="utf-8") as f:
            f.write(factions_data)

        # Create sample Datasheets.csv
        datasheets_data = """id|name|faction_id|role|legend|
000000001|Space Marine Captain|SM|HQ||
000000002|Tactical Squad|SM|Troops||"""

        with open(temp_path / "Datasheets.csv", "w", encoding="utf-8") as f:
            f.write(datasheets_data)

        yield temp_path


def test_csv_parser_initialization():
    """Test CSV parser initialization."""
    parser = WahapediaCSVParser()
    assert parser.data_path.name == "Wahapedia Data"


def test_csv_parser_with_custom_path():
    """Test CSV parser with custom path."""
    custom_path = "/custom/path"
    parser = WahapediaCSVParser(custom_path)
    assert str(parser.data_path) == custom_path


def test_parse_factions(temp_csv_dir):
    """Test parsing factions CSV."""
    parser = WahapediaCSVParser(str(temp_csv_dir))
    df = parser.parse_factions()

    assert len(df) == 2
    assert "faction_id" in df.columns
    assert "name" in df.columns
    assert df.iloc[0]["faction_id"] == "SM"
    assert df.iloc[0]["name"] == "Space Marines"


def test_parse_datasheets(temp_csv_dir):
    """Test parsing datasheets CSV."""
    parser = WahapediaCSVParser(str(temp_csv_dir))
    df = parser.parse_datasheets()

    assert len(df) == 2
    assert "datasheet_id" in df.columns
    assert "name" in df.columns
    assert "faction_id" in df.columns
    assert df.iloc[0]["datasheet_id"] == "000000001"
    assert df.iloc[0]["name"] == "Space Marine Captain"


def test_parse_nonexistent_file():
    """Test parsing nonexistent CSV file."""
    parser = WahapediaCSVParser("/nonexistent/path")
    with pytest.raises(FileNotFoundError):
        parser.parse_factions()

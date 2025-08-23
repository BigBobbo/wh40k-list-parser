"""CSV parser for Wahapedia data files."""

from pathlib import Path
from typing import Dict

import pandas as pd

from ...config import get_settings


class WahapediaCSVParser:
    """Parser for Wahapedia CSV data files."""

    def __init__(self, data_path: str = None):
        """Initialize parser with data path."""
        settings = get_settings()
        self.data_path = Path(data_path or settings.wahapedia_data_path)

    def _read_csv(self, filename: str) -> pd.DataFrame:
        """Read a CSV file with proper encoding and separator."""
        file_path = self.data_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        # Wahapedia CSVs use | separator and may have UTF-8 BOM
        return pd.read_csv(file_path, sep="|", encoding="utf-8-sig")

    def parse_factions(self) -> pd.DataFrame:
        """Parse factions CSV data."""
        df = self._read_csv("Factions.csv")
        # Clean column names
        df.columns = df.columns.str.strip()
        # Rename columns to match our models
        df = df.rename(columns={"id": "faction_id"})
        return df

    def parse_datasheets(self) -> pd.DataFrame:
        """Parse datasheets CSV data."""
        df = self._read_csv("Datasheets.csv")
        df.columns = df.columns.str.strip()
        # Rename columns to match our models
        df = df.rename(columns={"id": "datasheet_id", "legend": "is_legend"})
        # Convert legend column to boolean
        df["is_legend"] = df["is_legend"].fillna("").str.strip() != ""
        return df

    def parse_keywords(self) -> pd.DataFrame:
        """Parse datasheet keywords CSV data."""
        df = self._read_csv("Datasheets_keywords.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_unit_composition(self) -> pd.DataFrame:
        """Parse unit composition CSV data."""
        df = self._read_csv("Datasheets_unit_composition.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_model_costs(self) -> pd.DataFrame:
        """Parse model costs CSV data."""
        df = self._read_csv("Datasheets_models_cost.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_abilities(self) -> pd.DataFrame:
        """Parse abilities CSV data."""
        df = self._read_csv("Abilities.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_wargear(self) -> pd.DataFrame:
        """Parse wargear CSV data."""
        df = self._read_csv("Datasheets_wargear.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_detachment_abilities(self) -> pd.DataFrame:
        """Parse detachment abilities CSV data."""
        df = self._read_csv("Detachment_abilities.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_enhancements(self) -> pd.DataFrame:
        """Parse enhancements CSV data."""
        df = self._read_csv("Enhancements.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_stratagems(self) -> pd.DataFrame:
        """Parse stratagems CSV data."""
        df = self._read_csv("Stratagems.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_model_stats(self) -> pd.DataFrame:
        """Parse model stats CSV data."""
        df = self._read_csv("Datasheets_models.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_datasheet_abilities(self) -> pd.DataFrame:
        """Parse datasheet abilities CSV data."""
        df = self._read_csv("Datasheets_abilities.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_datasheet_options(self) -> pd.DataFrame:
        """Parse datasheet options CSV data."""
        df = self._read_csv("Datasheets_options.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_datasheet_leaders(self) -> pd.DataFrame:
        """Parse datasheet leader relationships CSV data."""
        df = self._read_csv("Datasheets_leader.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_datasheet_enhancements(self) -> pd.DataFrame:
        """Parse datasheet enhancements CSV data."""
        df = self._read_csv("Datasheets_enhancements.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_datasheet_stratagems(self) -> pd.DataFrame:
        """Parse datasheet stratagems CSV data."""
        df = self._read_csv("Datasheets_stratagems.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_datasheet_detachment_abilities(self) -> pd.DataFrame:
        """Parse datasheet detachment abilities CSV data."""
        df = self._read_csv("Datasheets_detachment_abilities.csv")
        df.columns = df.columns.str.strip()
        return df

    def parse_all(self) -> Dict[str, pd.DataFrame]:
        """Parse all CSV files and return as dictionary."""
        return {
            "factions": self.parse_factions(),
            "datasheets": self.parse_datasheets(),
            "keywords": self.parse_keywords(),
            "unit_composition": self.parse_unit_composition(),
            "model_costs": self.parse_model_costs(),
            "model_stats": self.parse_model_stats(),
            "datasheet_abilities": self.parse_datasheet_abilities(),
            "wargear": self.parse_wargear(),
        }

"""Data mapper for converting CSV data to database models."""

from typing import Dict, List

import pandas as pd
from sqlalchemy.orm import Session

from ...database.models import (
    DatasheetKeywordModel,
    DatasheetModel,
    DatasheetModelStatsModel,
    FactionModel,
    ModelCostModel,
    UnitCompositionModel,
)


class DataMapper:
    """Map CSV data to database models."""

    def __init__(self, session: Session):
        """Initialize mapper with database session."""
        self.session = session

    def map_factions(self, df: pd.DataFrame) -> List[FactionModel]:
        """Map factions dataframe to database models."""
        factions = []
        for _, row in df.iterrows():
            faction = FactionModel(
                faction_id=str(row["faction_id"]),
                name=str(row["name"]),
                link=str(row["link"]) if pd.notna(row["link"]) else None,
            )
            factions.append(faction)
        return factions

    def map_datasheets(self, df: pd.DataFrame) -> List[DatasheetModel]:
        """Map datasheets dataframe to database models."""
        datasheets = []
        for _, row in df.iterrows():
            datasheet = DatasheetModel(
                datasheet_id=str(row["datasheet_id"]),
                name=str(row["name"]),
                faction_id=str(row["faction_id"]),
                role=str(row["role"]) if pd.notna(row["role"]) else None,
                is_legend=bool(row.get("is_legend", False)),
                loadout=str(row["loadout"]) if pd.notna(row["loadout"]) else None,
                transport_capacity=(
                    str(row["transport"]) if pd.notna(row["transport"]) else None
                ),
                damaged_description=(
                    str(row["damaged_description"])
                    if pd.notna(row["damaged_description"])
                    else None
                ),
                link=str(row["link"]) if pd.notna(row["link"]) else None,
            )
            datasheets.append(datasheet)
        return datasheets

    def map_keywords(self, df: pd.DataFrame) -> List[DatasheetKeywordModel]:
        """Map keywords dataframe to database models."""
        keywords = []
        for _, row in df.iterrows():
            # Keywords are stored in columns keyword, keyword2, keyword3, etc.
            datasheet_id = str(row["datasheet_id"])
            for col in df.columns:
                if col.startswith("keyword") and pd.notna(row[col]):
                    keyword_value = str(row[col]).strip()
                    if keyword_value:  # Only add non-empty keywords
                        keyword = DatasheetKeywordModel(
                            datasheet_id=datasheet_id,
                            keyword=keyword_value.upper(),  # Normalize to uppercase
                        )
                        keywords.append(keyword)
        return keywords

    def map_unit_composition(self, df: pd.DataFrame) -> List[UnitCompositionModel]:
        """Map unit composition dataframe to database models."""
        compositions = []
        for _, row in df.iterrows():
            composition = UnitCompositionModel(
                datasheet_id=str(row["datasheet_id"]),
                line=int(row["line"]),
                description=str(row["description"]),
            )
            compositions.append(composition)
        return compositions

    def map_model_costs(self, df: pd.DataFrame) -> List[ModelCostModel]:
        """Map model costs dataframe to database models."""
        costs = []
        for _, row in df.iterrows():
            cost = ModelCostModel(
                datasheet_id=str(row["datasheet_id"]),
                line=int(row["line"]),
                description=str(row["description"]),
                cost=int(row["cost"]),
            )
            costs.append(cost)
        return costs

    def map_model_stats(self, df: pd.DataFrame) -> List[DatasheetModelStatsModel]:
        """Map model stats dataframe to database models."""
        stats = []
        for _, row in df.iterrows():
            # Parse toughness value
            toughness = None
            if pd.notna(row["T"]) and str(row["T"]).isdigit():
                toughness = int(row["T"])

            # Parse wounds value
            wounds = None
            if pd.notna(row["W"]) and str(row["W"]).isdigit():
                wounds = int(row["W"])

            # Parse objective control value
            objective_control = None
            if pd.notna(row["OC"]) and str(row["OC"]).isdigit():
                objective_control = int(row["OC"])

            stat = DatasheetModelStatsModel(
                datasheet_id=str(row["datasheet_id"]),
                line=int(row["line"]),
                name=str(row["name"]),
                movement=str(row["M"]) if pd.notna(row["M"]) else None,
                toughness=toughness,
                save=str(row["Sv"]) if pd.notna(row["Sv"]) else None,
                invulnerable_save=str(row["inv_sv"]) if pd.notna(row["inv_sv"]) else None,
                invulnerable_description=str(row["inv_sv_descr"]) if pd.notna(row["inv_sv_descr"]) else None,
                wounds=wounds,
                leadership=str(row["Ld"]) if pd.notna(row["Ld"]) else None,
                objective_control=objective_control,
                base_size=str(row["base_size"]) if pd.notna(row["base_size"]) else None,
                base_size_description=str(row["base_size_descr"]) if pd.notna(row["base_size_descr"]) else None,
            )
            stats.append(stat)
        return stats

    def save_all(self, data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """Save all parsed data to database."""
        counts = {}

        # Save factions
        factions = self.map_factions(data["factions"])
        for faction in factions:
            self.session.merge(faction)  # Use merge to handle duplicates
        counts["factions"] = len(factions)

        # Save datasheets
        datasheets = self.map_datasheets(data["datasheets"])
        for datasheet in datasheets:
            self.session.merge(datasheet)
        counts["datasheets"] = len(datasheets)

        # Save keywords
        keywords = self.map_keywords(data["keywords"])
        # Remove duplicates before saving
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            key = (keyword.datasheet_id, keyword.keyword)
            if key not in seen:
                seen.add(key)
                unique_keywords.append(keyword)
                self.session.merge(keyword)
        counts["keywords"] = len(unique_keywords)

        # Save unit compositions
        compositions = self.map_unit_composition(data["unit_composition"])
        for composition in compositions:
            self.session.merge(composition)
        counts["unit_compositions"] = len(compositions)

        # Save model costs
        costs = self.map_model_costs(data["model_costs"])
        for cost in costs:
            self.session.merge(cost)
        counts["model_costs"] = len(costs)

        # Save model stats
        if "model_stats" in data:
            stats = self.map_model_stats(data["model_stats"])
            for stat in stats:
                self.session.merge(stat)
            counts["model_stats"] = len(stats)

        # Commit all changes
        self.session.commit()

        return counts

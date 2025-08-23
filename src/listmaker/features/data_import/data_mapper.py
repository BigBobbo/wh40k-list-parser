"""Data mapper for converting CSV data to database models."""

from typing import Dict, List

import pandas as pd
from sqlalchemy.orm import Session

from ...database.models import (
    AbilityModel,
    DatasheetAbilityModel,
    DatasheetDetachmentAbilityModel,
    DatasheetEnhancementModel,
    DatasheetKeywordModel,
    DatasheetLeaderModel,
    DatasheetModel,
    DatasheetModelStatsModel,
    DatasheetOptionModel,
    DatasheetStratagemModel,
    DatasheetWargearModel,
    DetachmentAbilityModel,
    EnhancementModel,
    FactionModel,
    ModelCostModel,
    StratagemModel,
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

    def map_wargear(self, df: pd.DataFrame) -> List[DatasheetWargearModel]:
        """Map wargear dataframe to database models."""
        wargear_items = []
        for _, row in df.iterrows():
            # Ensure datasheet_id is properly formatted with leading zeros
            datasheet_id = str(row["datasheet_id"]).zfill(9) if len(str(row["datasheet_id"])) < 9 else str(row["datasheet_id"])
            wargear = DatasheetWargearModel(
                datasheet_id=datasheet_id,
                line=int(row["line"]),
                line_in_wargear=int(row["line_in_wargear"]) if pd.notna(row["line_in_wargear"]) else 1,
                dice=str(row["dice"]) if pd.notna(row["dice"]) else None,
                name=str(row["name"]),
                description=str(row["description"]) if pd.notna(row["description"]) else None,
                range=str(row["range"]) if pd.notna(row["range"]) else None,
                type=str(row["type"]) if pd.notna(row["type"]) else None,
                attacks=str(row["A"]) if pd.notna(row["A"]) else None,
                bs_ws=str(row["BS_WS"]) if pd.notna(row["BS_WS"]) else None,
                strength=str(row["S"]) if pd.notna(row["S"]) else None,
                ap=str(row["AP"]) if pd.notna(row["AP"]) else None,
                damage=str(row["D"]) if pd.notna(row["D"]) else None,
            )
            wargear_items.append(wargear)
        return wargear_items

    def map_abilities(self, df: pd.DataFrame) -> List[AbilityModel]:
        """Map abilities dataframe to database models."""
        abilities = []
        for _, row in df.iterrows():
            ability = AbilityModel(
                ability_id=str(row["id"]),
                name=str(row["name"]),
                legend=str(row["legend"]) if pd.notna(row["legend"]) else None,
                faction_id=str(row["faction_id"]) if pd.notna(row["faction_id"]) else None,
                description=str(row["description"]) if pd.notna(row["description"]) else None,
            )
            abilities.append(ability)
        return abilities

    def map_datasheet_abilities(self, df: pd.DataFrame) -> List[DatasheetAbilityModel]:
        """Map datasheet abilities dataframe to database models."""
        abilities = []
        for _, row in df.iterrows():
            # Pad datasheet_id to match format
            datasheet_id = str(row["datasheet_id"]).zfill(9)
            ability = DatasheetAbilityModel(
                datasheet_id=datasheet_id,
                line=int(row["line"]),
                ability_id=str(row["ability_id"]) if pd.notna(row["ability_id"]) else None,
                model=str(row["model"]) if pd.notna(row["model"]) else None,
                name=str(row["name"]) if pd.notna(row["name"]) else None,
                description=str(row["description"]) if pd.notna(row["description"]) else None,
                type=str(row["type"]) if pd.notna(row["type"]) else None,
                parameter=str(row["parameter"]) if pd.notna(row["parameter"]) else None,
            )
            abilities.append(ability)
        return abilities

    def map_datasheet_options(self, df: pd.DataFrame) -> List[DatasheetOptionModel]:
        """Map datasheet options dataframe to database models."""
        options = []
        for _, row in df.iterrows():
            datasheet_id = str(row["datasheet_id"]).zfill(9)
            option = DatasheetOptionModel(
                datasheet_id=datasheet_id,
                line=int(row["line"]),
                button=str(row["button"]) if pd.notna(row["button"]) else None,
                description=str(row["description"]),
            )
            options.append(option)
        return options

    def map_datasheet_leaders(self, df: pd.DataFrame) -> List[DatasheetLeaderModel]:
        """Map datasheet leaders dataframe to database models."""
        leaders = []
        for _, row in df.iterrows():
            leader = DatasheetLeaderModel(
                leader_id=str(row["leader_id"]).zfill(9),
                attached_id=str(row["attached_id"]).zfill(9),
            )
            leaders.append(leader)
        return leaders

    def map_enhancements(self, df: pd.DataFrame) -> List[EnhancementModel]:
        """Map enhancements dataframe to database models."""
        enhancements = []
        for _, row in df.iterrows():
            enhancement = EnhancementModel(
                enhancement_id=str(row["id"]),
                name=str(row["name"]),
                legend=str(row["legend"]) if pd.notna(row["legend"]) else None,
                faction_id=str(row["faction_id"]),
                description=str(row["description"]) if pd.notna(row["description"]) else None,
                cost=int(row["cost"]) if pd.notna(row["cost"]) and str(row["cost"]).isdigit() else None,
            )
            enhancements.append(enhancement)
        return enhancements

    def map_datasheet_enhancements(self, df: pd.DataFrame) -> List[DatasheetEnhancementModel]:
        """Map datasheet enhancements dataframe to database models."""
        enhancements = []
        for i, row in df.iterrows():
            datasheet_id = str(row["datasheet_id"]).zfill(9)
            enhancement = DatasheetEnhancementModel(
                datasheet_id=datasheet_id,
                line=i + 1,  # Use row index as line number since no line column exists
                enhancement_id=str(row["enhancement_id"]),
            )
            enhancements.append(enhancement)
        return enhancements

    def map_stratagems(self, df: pd.DataFrame) -> List[StratagemModel]:
        """Map stratagems dataframe to database models."""
        stratagems = []
        for _, row in df.iterrows():
            stratagem = StratagemModel(
                stratagem_id=str(row["id"]),
                name=str(row["name"]),
                legend=str(row["legend"]) if pd.notna(row["legend"]) else None,
                faction_id=str(row["faction_id"]),
                cp_cost=int(row["cp_cost"]) if pd.notna(row["cp_cost"]) and str(row["cp_cost"]).isdigit() else None,
                type=str(row["type"]) if pd.notna(row["type"]) else None,
                turn=str(row["turn"]) if pd.notna(row["turn"]) else None,
                phase=str(row["phase"]) if pd.notna(row["phase"]) else None,
                description=str(row["description"]) if pd.notna(row["description"]) else None,
            )
            stratagems.append(stratagem)
        return stratagems

    def map_datasheet_stratagems(self, df: pd.DataFrame) -> List[DatasheetStratagemModel]:
        """Map datasheet stratagems dataframe to database models."""
        stratagems = []
        for i, row in df.iterrows():
            datasheet_id = str(row["datasheet_id"]).zfill(9)
            stratagem = DatasheetStratagemModel(
                datasheet_id=datasheet_id,
                line=i + 1,  # Use row index as line number
                stratagem_id=str(row["stratagem_id"]),
            )
            stratagems.append(stratagem)
        return stratagems

    def map_detachment_abilities(self, df: pd.DataFrame) -> List[DetachmentAbilityModel]:
        """Map detachment abilities dataframe to database models."""
        abilities = []
        for _, row in df.iterrows():
            ability = DetachmentAbilityModel(
                detachment_ability_id=str(row["id"]),
                name=str(row["name"]),
                legend=str(row["legend"]) if pd.notna(row["legend"]) else None,
                faction_id=str(row["faction_id"]),
                detachment=str(row["detachment"]) if pd.notna(row["detachment"]) else None,
                description=str(row["description"]) if pd.notna(row["description"]) else None,
            )
            abilities.append(ability)
        return abilities

    def map_datasheet_detachment_abilities(self, df: pd.DataFrame) -> List[DatasheetDetachmentAbilityModel]:
        """Map datasheet detachment abilities datasheet to database models."""
        abilities = []
        for i, row in df.iterrows():
            datasheet_id = str(row["datasheet_id"]).zfill(9)
            ability = DatasheetDetachmentAbilityModel(
                datasheet_id=datasheet_id,
                line=i + 1,  # Use row index as line number
                detachment_ability_id=str(row["detachment_ability_id"]),
            )
            abilities.append(ability)
        return abilities

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

        # Save wargear
        if "wargear" in data:
            wargear_items = self.map_wargear(data["wargear"])
            for wargear in wargear_items:
                self.session.merge(wargear)
            counts["wargear"] = len(wargear_items)

        # Save datasheet abilities (using existing CSV parsing)
        if "datasheet_abilities" in data:
            ds_abilities = self.map_datasheet_abilities(data["datasheet_abilities"])
            for ability in ds_abilities:
                self.session.merge(ability)
            counts["datasheet_abilities"] = len(ds_abilities)

        # For now, focus on the core data that's working
        # Additional data types will be added in future iterations

        # Commit all changes
        self.session.commit()

        return counts

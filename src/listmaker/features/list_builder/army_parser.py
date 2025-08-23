"""Army list text parser for converting pasted army lists to structured data."""

import re
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ...database.models import (
    DatasheetKeywordModel,
    DatasheetModel,
    DatasheetModelStatsModel,
    DatasheetWargearModel,
)


class ArmyListParser:
    """Parse army list text and convert to structured data."""

    def __init__(self, session: Session):
        """Initialize parser with database session."""
        self.session = session
        
    def parse_army_list(self, army_text: str) -> Dict:
        """Parse army list text and return Godot-compatible structure."""
        lines = army_text.strip().split('\n')
        
        # Extract faction and basic info
        faction_info = self._extract_faction_info(lines)
        
        # Parse units
        units = self._parse_units(lines)
        
        # Convert to Godot format
        godot_units = {}
        for i, unit_data in enumerate(units):
            unit_id = f"U_{unit_data['name'].upper().replace(' ', '_')}_{chr(65+i)}"
            godot_units[unit_id] = self._convert_to_godot_format(unit_id, unit_data)
            
        return {
            "faction": faction_info,
            "units": godot_units
        }
    
    def _extract_faction_info(self, lines: List[str]) -> Dict:
        """Extract faction and army info from first few lines."""
        faction = lines[0].strip() if lines else "Unknown"
        points = 0
        detachment = ""
        
        for line in lines[:5]:
            # Look for points info
            points_match = re.search(r'\((\d+) points\)', line)
            if points_match:
                points = int(points_match.group(1))
                
            # Look for detachment info
            if any(keyword in line.lower() for keyword in ['strike force', 'patrol', 'battalion']):
                detachment = line.strip()
                
        return {
            "name": faction,
            "points": points,
            "detachment": detachment
        }
    
    def _parse_units(self, lines: List[str]) -> List[Dict]:
        """Parse units from army list text."""
        units = []
        current_unit = None
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header
            if line.upper() in ['CHARACTERS', 'BATTLELINE', 'OTHER DATASHEETS', 'ALLIED UNITS']:
                current_section = line.upper()
                continue
                
            # Check if this is a unit entry (has points at the end)
            points_match = re.search(r'^(.+?)\s*\((\d+) points\)$', line)
            if points_match:
                # Save previous unit if exists
                if current_unit:
                    units.append(current_unit)
                    
                # Start new unit
                unit_name = points_match.group(1).strip()
                unit_points = int(points_match.group(2))
                
                current_unit = {
                    'name': unit_name,
                    'points': unit_points,
                    'section': current_section,
                    'wargear': [],
                    'models': [],
                    'is_warlord': False,
                    'enhancements': []
                }
                continue
                
            # Check for special markers
            if current_unit:
                if '• Warlord' in line:
                    current_unit['is_warlord'] = True
                elif '• Enhancement:' in line:
                    enhancement = line.replace('• Enhancement:', '').strip()
                    current_unit['enhancements'].append(enhancement)
                elif line.startswith('• '):
                    # This is wargear or model info
                    wargear_item = line.replace('• ', '').strip()
                    if 'x ' in wargear_item:
                        # This looks like model count info
                        current_unit['models'].append(wargear_item)
                    else:
                        current_unit['wargear'].append(wargear_item)
        
        # Don't forget the last unit
        if current_unit:
            units.append(current_unit)
            
        return units
    
    def _convert_to_godot_format(self, unit_id: str, unit_data: Dict) -> Dict:
        """Convert unit data to Godot-compatible format."""
        # Look up unit in database
        datasheet = self._find_datasheet(unit_data['name'])
        
        if not datasheet:
            # Return basic structure if unit not found
            return self._create_fallback_unit(unit_id, unit_data)
            
        # Get keywords
        keywords = self._get_unit_keywords(datasheet.datasheet_id)
        
        # Get model stats
        model_stats = self._get_model_stats(datasheet.datasheet_id)
        
        # Get wargear/weapons (pad datasheet_id to match wargear table format)
        padded_datasheet_id = datasheet.datasheet_id.zfill(9)
        wargear = self._get_wargear(padded_datasheet_id)
        weapons = [self._format_weapon(w) for w in wargear]
        
        # Parse model count from the unit composition
        model_count = self._parse_model_count(unit_data)
        
        # Create models array
        models = []
        for i in range(model_count):
            model_id = f"m{i+1}"
            
            # Use first model stats as base (most units have consistent stats)
            base_wounds = model_stats[0].wounds if model_stats and model_stats[0].wounds else 1
            base_size_mm = self._parse_base_size(model_stats[0].base_size if model_stats else None)
            
            models.append({
                "id": model_id,
                "wounds": base_wounds,
                "current_wounds": base_wounds,
                "base_mm": base_size_mm,
                "position": None,
                "alive": True,
                "status_effects": []
            })
        
        # Create unit stats
        unit_stats = {}
        if model_stats and model_stats[0]:
            stats = model_stats[0]
            unit_stats = {
                "move": self._parse_movement(stats.movement),
                "toughness": stats.toughness or 3,
                "save": self._parse_save(stats.save),
                "wounds": stats.wounds or 1,
                "leadership": self._parse_leadership(stats.leadership),
                "objective_control": stats.objective_control or 1
            }
        
        return {
            "id": unit_id,
            "squad_id": unit_id,
            "owner": 1,
            "status": "UNDEPLOYED",  # UnitStatus.UNDEPLOYED equivalent
            "meta": {
                "name": unit_data['name'],
                "keywords": keywords,
                "stats": unit_stats,
                "points": unit_data['points'],
                "is_warlord": unit_data['is_warlord'],
                "enhancements": unit_data['enhancements'],
                "wargear": unit_data['wargear'],
                "weapons": weapons
            },
            "models": models
        }
    
    def _find_datasheet(self, unit_name: str) -> Optional[DatasheetModel]:
        """Find datasheet by unit name with fuzzy matching."""
        # First try exact match
        datasheet = (
            self.session.query(DatasheetModel)
            .filter(DatasheetModel.name == unit_name)
            .first()
        )
        
        if datasheet:
            return datasheet
            
        # Try partial match
        datasheet = (
            self.session.query(DatasheetModel)
            .filter(DatasheetModel.name.contains(unit_name))
            .first()
        )
        
        if datasheet:
            return datasheet
            
        # Try reverse partial match (unit name contains datasheet name)
        datasheets = self.session.query(DatasheetModel).all()
        for ds in datasheets:
            if ds.name.lower() in unit_name.lower():
                return ds
                
        return None
    
    def _get_unit_keywords(self, datasheet_id: str) -> List[str]:
        """Get keywords for a datasheet."""
        keywords = (
            self.session.query(DatasheetKeywordModel)
            .filter(DatasheetKeywordModel.datasheet_id == datasheet_id)
            .all()
        )
        return [k.keyword for k in keywords]
    
    def _get_model_stats(self, datasheet_id: str) -> List[DatasheetModelStatsModel]:
        """Get model stats for a datasheet."""
        return (
            self.session.query(DatasheetModelStatsModel)
            .filter(DatasheetModelStatsModel.datasheet_id == datasheet_id)
            .order_by(DatasheetModelStatsModel.line)
            .all()
        )
    
    def _get_wargear(self, datasheet_id: str) -> List[DatasheetWargearModel]:
        """Get wargear/weapons for a datasheet."""
        return (
            self.session.query(DatasheetWargearModel)
            .filter(DatasheetWargearModel.datasheet_id == datasheet_id)
            .order_by(DatasheetWargearModel.line, DatasheetWargearModel.line_in_wargear)
            .all()
        )
    
    def _format_weapon(self, weapon: DatasheetWargearModel) -> Dict:
        """Format weapon data for output."""
        # Clean up HTML tags from description
        description = weapon.description or ""
        description = re.sub(r'<[^>]+>', '', description)  # Remove HTML tags
        
        weapon_data = {
            "name": weapon.name,
            "type": weapon.type,
        }
        
        # Add ranged weapon stats
        if weapon.type == "Ranged":
            weapon_data.update({
                "range": weapon.range,
                "attacks": weapon.attacks,
                "ballistic_skill": weapon.bs_ws,
                "strength": weapon.strength,
                "ap": weapon.ap,
                "damage": weapon.damage,
            })
        # Add melee weapon stats
        elif weapon.type == "Melee":
            weapon_data.update({
                "range": "Melee",
                "attacks": weapon.attacks,
                "weapon_skill": weapon.bs_ws,
                "strength": weapon.strength,
                "ap": weapon.ap,
                "damage": weapon.damage,
            })
        
        # Add special rules if present
        if description:
            weapon_data["special_rules"] = description
            
        return weapon_data
    
    def _parse_model_count(self, unit_data: Dict) -> int:
        """Parse model count from unit data."""
        # Look for model count in various places
        total_count = 1
        
        # Check models array for counts
        for model_desc in unit_data.get('models', []):
            # Look for patterns like "4x Custodian Guard" or "1x Prosecutor Sister Superior"
            count_match = re.search(r'(\d+)x\s+', model_desc)
            if count_match:
                count = int(count_match.group(1))
                total_count += count - 1  # -1 because we start with 1
                
        # If no specific models found, try to parse from unit name or default to 1
        if total_count == 1 and unit_data.get('models'):
            # Count number of model entries as fallback
            total_count = len(unit_data['models'])
            
        return max(1, total_count)  # Always at least 1
    
    def _parse_base_size(self, base_size_str: Optional[str]) -> int:
        """Parse base size to millimeters."""
        if not base_size_str:
            return 32  # Default to 32mm
            
        # Extract numbers from base size string
        size_match = re.search(r'(\d+)', base_size_str)
        if size_match:
            return int(size_match.group(1))
            
        return 32
    
    def _parse_movement(self, movement_str: Optional[str]) -> int:
        """Parse movement value."""
        if not movement_str:
            return 6
            
        # Extract number from movement string like '6"'
        move_match = re.search(r'(\d+)', movement_str)
        if move_match:
            return int(move_match.group(1))
            
        return 6
    
    def _parse_save(self, save_str: Optional[str]) -> int:
        """Parse save value."""
        if not save_str:
            return 3
            
        # Extract number from save string like '3+'
        save_match = re.search(r'(\d+)', save_str)
        if save_match:
            return int(save_match.group(1))
            
        return 3
    
    def _parse_leadership(self, leadership_str: Optional[str]) -> int:
        """Parse leadership value."""
        if not leadership_str:
            return 6
            
        # Extract number from leadership string like '6+'
        ld_match = re.search(r'(\d+)', leadership_str)
        if ld_match:
            return int(ld_match.group(1))
            
        return 6
    
    def _create_fallback_unit(self, unit_id: str, unit_data: Dict) -> Dict:
        """Create fallback unit structure when datasheet not found."""
        return {
            "id": unit_id,
            "squad_id": unit_id,
            "owner": 1,
            "status": "UNDEPLOYED",
            "meta": {
                "name": unit_data['name'],
                "keywords": ["UNKNOWN"],
                "stats": {"move": 6, "toughness": 4, "save": 3},
                "points": unit_data['points'],
                "is_warlord": unit_data['is_warlord'],
                "enhancements": unit_data['enhancements'],
                "wargear": unit_data['wargear']
            },
            "models": [
                {"id": "m1", "wounds": 1, "current_wounds": 1, "base_mm": 32, "position": None, "alive": True, "status_effects": []}
            ]
        }
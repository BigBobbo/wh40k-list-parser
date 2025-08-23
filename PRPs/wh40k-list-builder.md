# Warhammer 40K List Builder - Product Requirements Proposal

## Executive Summary
Build a web-based Warhammer 40K 10th Edition army list builder using Python, FastAPI, and the existing Wahapedia CSV data. The application will allow users to create valid army lists, track points, and manage detachments while following 10th edition rules.

## Context and Research

### Available Data Structure
The project has access to comprehensive Wahapedia CSV data containing:
- **Factions.csv**: 29 factions with IDs and links
- **Datasheets.csv**: Unit profiles with stats, roles, and descriptions
- **Datasheets_models_cost.csv**: Point costs for units
- **Datasheets_unit_composition.csv**: Unit composition rules
- **Datasheets_keywords.csv**: Unit keywords for rules interactions
- **Datasheets_abilities.csv**: Unit special abilities
- **Datasheets_wargear.csv**: Weapon and equipment options
- **Datasheets_options.csv**: Unit upgrade options
- **Detachment_abilities.csv**: Army-wide special rules
- **Enhancements.csv**: Character upgrades
- **Stratagems.csv**: In-game abilities

### Reference Implementations
- **GitHub Examples**:
  - https://github.com/killerHELIX/40K-10E-List-Builder (10th Edition focused)
  - https://github.com/djpiper28/Warhammer-40K-List-Builder (Copyright-free approach)
  - https://furka.github.io/40k-10th-list-builder/ (Web-based implementation)

### Key 10th Edition Rules
- Army lists are built to specific point limits (typically 500, 1000, 1500, 2000 points)
- Each army must have 1+ CHARACTER unit designated as Warlord
- Detachments provide army-wide abilities
- Maximum 3 of the same datasheet (6 for Battleline units)
- Unit composition and wargear options must be validated

## Technical Architecture

### Technology Stack
- **Backend**: Python 3.11+ with FastAPI
- **Database**: SQLite for development, PostgreSQL-ready models
- **Data Models**: Pydantic v2 for validation
- **CSV Processing**: pandas for initial data import
- **Testing**: pytest with 80%+ coverage
- **Package Management**: UV (as per CLAUDE.md)
- **Code Quality**: ruff for linting/formatting, mypy for type checking

### Project Structure
```
src/listmaker/
    __init__.py
    main.py                      # FastAPI app entry point
    config.py                    # Settings management
    tests/
        test_main.py
        conftest.py              # Shared fixtures
    
    # Core modules
    database/
        __init__.py
        connection.py            # Database connection management
        models.py                # SQLAlchemy models
        seed.py                  # CSV data import
        tests/
            test_models.py
            test_seed.py
    
    models/
        __init__.py
        faction.py               # Pydantic models for factions
        datasheet.py             # Unit datasheet models
        army_list.py             # Army list composition
        validation.py            # List validation rules
        tests/
            test_faction.py
            test_datasheet.py
            test_army_list.py
            test_validation.py
    
    # Feature slices
    features/
        data_import/
            __init__.py
            csv_parser.py        # Parse Wahapedia CSVs
            data_mapper.py       # Map CSV to models
            tests/
                test_csv_parser.py
                test_data_mapper.py
        
        list_builder/
            __init__.py
            builder.py           # Core list building logic
            validator.py         # Rule validation
            calculator.py        # Points calculation
            tests/
                test_builder.py
                test_validator.py
                test_calculator.py
        
        api/
            __init__.py
            routers/
                factions.py      # Faction endpoints
                datasheets.py    # Unit data endpoints
                lists.py         # Army list CRUD
            dependencies.py      # Shared dependencies
            tests/
                test_factions.py
                test_datasheets.py
                test_lists.py
```

## Data Models (Pydantic)

### Core Models
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class RoleType(str, Enum):
    HQ = "HQ"
    TROOPS = "Troops"
    ELITES = "Elites"
    FAST_ATTACK = "Fast Attack"
    HEAVY_SUPPORT = "Heavy Support"
    DEDICATED_TRANSPORT = "Dedicated Transport"
    FLYER = "Flyer"
    FORTIFICATION = "Fortification"
    LORD_OF_WAR = "Lord of War"

class Faction(BaseModel):
    faction_id: str
    name: str
    link: Optional[str] = None

class Datasheet(BaseModel):
    datasheet_id: str
    name: str
    faction_id: str
    role: Optional[RoleType] = None
    base_cost: int = 0
    is_legend: bool = False
    keywords: List[str] = []
    
class UnitEntry(BaseModel):
    unit_entry_id: UUID = Field(default_factory=uuid4)
    datasheet_id: str
    quantity: int = 1
    total_cost: int
    wargear_selections: List[str] = []
    is_warlord: bool = False
    
class ArmyList(BaseModel):
    list_id: UUID = Field(default_factory=uuid4)
    name: str
    faction_id: str
    detachment_id: Optional[str] = None
    point_limit: int = 2000
    units: List[UnitEntry] = []
    total_points: int = 0
    created_at: datetime
    updated_at: datetime
    
    @validator('total_points', always=True)
    def calculate_total(cls, v, values):
        if 'units' in values:
            return sum(unit.total_cost for unit in values['units'])
        return 0
```

## Implementation Blueprint

### Phase 1: Data Layer (Tasks 1-4)
```python
# Pseudocode for CSV import
def import_wahapedia_data():
    # 1. Load all CSV files into pandas DataFrames
    factions_df = pd.read_csv("Wahapedia Data/Factions.csv", sep="|")
    datasheets_df = pd.read_csv("Wahapedia Data/Datasheets.csv", sep="|")
    costs_df = pd.read_csv("Wahapedia Data/Datasheets_models_cost.csv", sep="|")
    
    # 2. Clean and transform data
    clean_data(factions_df, datasheets_df, costs_df)
    
    # 3. Create SQLAlchemy models
    for _, row in factions_df.iterrows():
        faction = Faction(
            faction_id=row['id'],
            name=row['name'],
            link=row.get('link')
        )
        db.session.add(faction)
    
    # 4. Import relationships
    import_unit_costs(costs_df)
    import_keywords(keywords_df)
    
    db.session.commit()
```

### Phase 2: Business Logic (Tasks 5-8)
```python
# List validation pseudocode
class ListValidator:
    def validate_list(self, army_list: ArmyList) -> ValidationResult:
        errors = []
        warnings = []
        
        # Check point limit
        if army_list.total_points > army_list.point_limit:
            errors.append(f"List exceeds point limit: {army_list.total_points}/{army_list.point_limit}")
        
        # Check for warlord
        has_warlord = any(unit.is_warlord for unit in army_list.units)
        if not has_warlord:
            errors.append("Army must have a Warlord")
        
        # Check datasheet limits (Rule of Three)
        datasheet_counts = Counter(unit.datasheet_id for unit in army_list.units)
        for datasheet_id, count in datasheet_counts.items():
            datasheet = get_datasheet(datasheet_id)
            max_allowed = 6 if "BATTLELINE" in datasheet.keywords else 3
            if count > max_allowed:
                errors.append(f"Too many {datasheet.name}: {count}/{max_allowed}")
        
        return ValidationResult(errors=errors, warnings=warnings, is_valid=len(errors)==0)
```

### Phase 3: API Layer (Tasks 9-12)
```python
# FastAPI endpoints
from fastapi import APIRouter, HTTPException, Depends
from typing import List

router = APIRouter(prefix="/api/v1", tags=["lists"])

@router.post("/lists", response_model=ArmyList)
async def create_list(
    list_data: ArmyListCreate,
    db: Session = Depends(get_db)
) -> ArmyList:
    """Create a new army list."""
    # Validate faction exists
    faction = db.query(Faction).filter_by(faction_id=list_data.faction_id).first()
    if not faction:
        raise HTTPException(404, f"Faction {list_data.faction_id} not found")
    
    # Create list
    army_list = ArmyList(**list_data.dict())
    
    # Validate list rules
    validator = ListValidator()
    validation = validator.validate_list(army_list)
    if not validation.is_valid:
        raise HTTPException(400, validation.errors)
    
    # Save to database
    db_list = save_army_list(db, army_list)
    return db_list

@router.get("/lists/{list_id}", response_model=ArmyList)
async def get_list(list_id: UUID, db: Session = Depends(get_db)) -> ArmyList:
    """Retrieve an army list by ID."""
    army_list = db.query(ArmyListModel).filter_by(list_id=list_id).first()
    if not army_list:
        raise HTTPException(404, f"List {list_id} not found")
    return army_list
```

## Implementation Tasks (In Order)

1. **Project Setup**
   - Initialize UV environment
   - Install core dependencies (fastapi, uvicorn, pandas, sqlalchemy, pydantic)
   - Create project structure

2. **Data Models**
   - Create Pydantic models for all entities
   - Define SQLAlchemy database models
   - Write model unit tests

3. **CSV Data Import**
   - Build CSV parser for Wahapedia data
   - Create data mapping layer
   - Implement database seeding

4. **Database Layer**
   - Set up SQLite database
   - Create database connection management
   - Implement repository pattern

5. **List Builder Core**
   - Implement list creation logic
   - Add unit selection functionality
   - Calculate points automatically

6. **Validation Engine**
   - Implement 10th edition rules validation
   - Add faction-specific rules
   - Create comprehensive error messages

7. **API Endpoints**
   - Create faction endpoints
   - Build datasheet query endpoints
   - Implement list CRUD operations

8. **Advanced Features**
   - Add wargear selection
   - Implement enhancement system
   - Support detachment abilities

9. **Testing Suite**
   - Write unit tests for all modules
   - Create integration tests
   - Add end-to-end test scenarios

10. **Documentation**
    - API documentation with OpenAPI
    - User guide for list building
    - Developer documentation

## Validation Gates

```bash
# 1. Code Quality Checks
uv run ruff check src/ --fix
uv run ruff format src/
uv run mypy src/

# 2. Unit Tests
uv run pytest tests/ -v --cov=src --cov-report=term-missing

# 3. Integration Tests
uv run pytest tests/integration/ -v

# 4. API Tests
uv run pytest tests/api/ -v

# 5. Run Development Server
uv run uvicorn src.listmaker.main:app --reload --port 8000

# 6. Check API Documentation
# Navigate to http://localhost:8000/docs
```

## Known Gotchas and Solutions

### CSV Data Issues
- **Problem**: Wahapedia CSVs use "|" as separator and may have UTF-8 BOM
- **Solution**: Use `pd.read_csv(file, sep="|", encoding="utf-8-sig")`

### Point Calculations
- **Problem**: Some units have variable costs based on model count
- **Solution**: Parse Datasheets_models_cost.csv carefully, matching line numbers

### Keyword Matching
- **Problem**: Keywords may have variations (e.g., "INFANTRY" vs "Infantry")
- **Solution**: Normalize to uppercase for all keyword comparisons

### Database Relations
- **Problem**: Complex many-to-many relationships between datasheets and options
- **Solution**: Use association tables for wargear, abilities, and keywords

## External Resources

### Documentation
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Pydantic V2 Migration: https://docs.pydantic.dev/latest/migration/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- Pandas CSV Reading: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

### Warhammer 40K Rules
- Core Rules Reference: https://wahapedia.ru/wh40k10ed/the-rules/core-rules/
- Army Construction: https://wahapedia.ru/wh40k10ed/the-rules/playing-the-game/#1.-MUSTER-YOUR-ARMY
- Detachment Rules: https://wahapedia.ru/wh40k10ed/the-rules/playing-the-game/#2.-DETERMINE-MISSION

### Similar Projects for Reference
- React-based builder: https://github.com/killerHELIX/40K-10E-List-Builder
- Vue.js implementation: https://furka.github.io/40k-10th-list-builder/

## Success Criteria

1. **Data Import**: Successfully import all Wahapedia CSV data
2. **List Creation**: Users can create valid army lists
3. **Validation**: Lists are validated against 10th edition rules
4. **Performance**: API responds in <200ms for typical operations
5. **Test Coverage**: Achieve 80%+ test coverage
6. **Documentation**: Complete API documentation available

## Error Handling Strategy

```python
# Custom exception hierarchy
class ListBuilderError(Exception):
    """Base exception for list builder."""
    pass

class ValidationError(ListBuilderError):
    """Raised when list validation fails."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {'; '.join(errors)}")

class DataImportError(ListBuilderError):
    """Raised when CSV import fails."""
    pass

class PointLimitExceeded(ValidationError):
    """Raised when army exceeds point limit."""
    pass

# Global exception handler
@app.exception_handler(ListBuilderError)
async def handle_list_builder_error(request: Request, exc: ListBuilderError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "errors": getattr(exc, 'errors', [])}
    )
```

## Deployment Considerations

1. **Environment Variables**:
   - `DATABASE_URL`: PostgreSQL connection string (production)
   - `DEBUG`: Enable debug mode
   - `CORS_ORIGINS`: Allowed CORS origins

2. **Data Updates**:
   - Implement admin endpoint to re-import CSV data
   - Version tracking for data updates
   - Backup before re-import

3. **Scalability**:
   - Cache faction and datasheet queries
   - Implement pagination for list queries
   - Consider Redis for session storage

## Quality Score: 8/10

### Strengths:
- Comprehensive data model based on actual CSV structure
- Clear implementation phases with validation gates
- Follows all CLAUDE.md conventions
- Includes error handling and testing strategy

### Areas for Enhancement:
- Could add frontend specifications
- Authentication/user management not detailed
- Could include performance benchmarks

This PRP provides sufficient context for one-pass implementation of a functional Warhammer 40K list builder with the provided Wahapedia data.
"""SQLAlchemy database models for Warhammer 40K List Builder."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid4())


class FactionModel(Base):
    """Database model for factions."""

    __tablename__ = "factions"

    faction_id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    link = Column(String(255), nullable=True)

    # Relationships
    datasheets = relationship("DatasheetModel", back_populates="faction")
    army_lists = relationship("ArmyListModel", back_populates="faction")


class DatasheetModel(Base):
    """Database model for unit datasheets."""

    __tablename__ = "datasheets"

    datasheet_id = Column(String(20), primary_key=True)
    name = Column(String(200), nullable=False)
    faction_id = Column(String(10), ForeignKey("factions.faction_id"), nullable=False)
    role = Column(String(50), nullable=True)
    is_legend = Column(Boolean, default=False)
    loadout = Column(Text, nullable=True)
    transport_capacity = Column(String(100), nullable=True)
    damaged_description = Column(Text, nullable=True)
    link = Column(String(255), nullable=True)

    # Relationships
    faction = relationship("FactionModel", back_populates="datasheets")
    keywords = relationship("DatasheetKeywordModel", back_populates="datasheet")
    costs = relationship("ModelCostModel", back_populates="datasheet")
    compositions = relationship("UnitCompositionModel", back_populates="datasheet")
    model_stats = relationship("DatasheetModelStatsModel", back_populates="datasheet")
    unit_entries = relationship("UnitEntryModel", back_populates="datasheet")


class DatasheetKeywordModel(Base):
    """Database model for datasheet keywords."""

    __tablename__ = "datasheet_keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    datasheet_id = Column(
        String(20), ForeignKey("datasheets.datasheet_id"), nullable=False
    )
    keyword = Column(String(50), nullable=False)

    # Relationships
    datasheet = relationship("DatasheetModel", back_populates="keywords")

    __table_args__ = (
        UniqueConstraint("datasheet_id", "keyword", name="uq_datasheet_keyword"),
    )


class UnitCompositionModel(Base):
    """Database model for unit composition rules."""

    __tablename__ = "unit_compositions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    datasheet_id = Column(
        String(20), ForeignKey("datasheets.datasheet_id"), nullable=False
    )
    line = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)

    # Relationships
    datasheet = relationship("DatasheetModel", back_populates="compositions")

    __table_args__ = (
        UniqueConstraint("datasheet_id", "line", name="uq_datasheet_line"),
    )


class ModelCostModel(Base):
    """Database model for unit/model costs."""

    __tablename__ = "model_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    datasheet_id = Column(
        String(20), ForeignKey("datasheets.datasheet_id"), nullable=False
    )
    line = Column(Integer, nullable=False)
    description = Column(String(200), nullable=False)
    cost = Column(Integer, nullable=False)

    # Relationships
    datasheet = relationship("DatasheetModel", back_populates="costs")

    __table_args__ = (
        UniqueConstraint("datasheet_id", "line", name="uq_datasheet_cost_line"),
    )


class ArmyListModel(Base):
    """Database model for army lists."""

    __tablename__ = "army_lists"

    list_id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    faction_id = Column(String(10), ForeignKey("factions.faction_id"), nullable=False)
    detachment_id = Column(String(50), nullable=True)
    point_limit = Column(Integer, default=2000)
    total_points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    faction = relationship("FactionModel", back_populates="army_lists")
    units = relationship(
        "UnitEntryModel", back_populates="army_list", cascade="all, delete-orphan"
    )


class DatasheetModelStatsModel(Base):
    """Database model for unit model stats."""

    __tablename__ = "datasheet_model_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    datasheet_id = Column(
        String(20), ForeignKey("datasheets.datasheet_id"), nullable=False
    )
    line = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    movement = Column(String(10), nullable=True)  # e.g., "6\""
    toughness = Column(Integer, nullable=True)
    save = Column(String(10), nullable=True)  # e.g., "3+"
    invulnerable_save = Column(String(10), nullable=True)  # e.g., "5+"
    invulnerable_description = Column(Text, nullable=True)
    wounds = Column(Integer, nullable=True)
    leadership = Column(String(10), nullable=True)  # e.g., "6+"
    objective_control = Column(Integer, nullable=True)
    base_size = Column(String(20), nullable=True)  # e.g., "32mm"
    base_size_description = Column(Text, nullable=True)

    # Relationships
    datasheet = relationship("DatasheetModel", back_populates="model_stats")

    __table_args__ = (
        UniqueConstraint("datasheet_id", "line", name="uq_datasheet_model_line"),
    )


class UnitEntryModel(Base):
    """Database model for unit entries in army lists."""

    __tablename__ = "unit_entries"

    unit_entry_id = Column(String(36), primary_key=True, default=generate_uuid)
    list_id = Column(String(36), ForeignKey("army_lists.list_id"), nullable=False)
    datasheet_id = Column(
        String(20), ForeignKey("datasheets.datasheet_id"), nullable=False
    )
    quantity = Column(Integer, default=1)
    total_cost = Column(Integer, nullable=False)
    is_warlord = Column(Boolean, default=False)
    wargear_selections = Column(JSON, default=list)
    enhancements = Column(JSON, default=list)

    # Relationships
    army_list = relationship("ArmyListModel", back_populates="units")
    datasheet = relationship("DatasheetModel", back_populates="unit_entries")

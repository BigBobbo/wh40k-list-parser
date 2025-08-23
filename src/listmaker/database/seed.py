"""Database seeding script for importing Wahapedia data."""

import logging


from ..features.data_import.csv_parser import WahapediaCSVParser
from ..features.data_import.data_mapper import DataMapper
from .connection import SessionLocal, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database(data_path: str = None) -> None:
    """Seed database with Wahapedia CSV data."""
    logger.info("Starting database seeding...")

    # Initialize database tables
    init_db()
    logger.info("Database tables initialized")

    # Create parser and mapper
    parser = WahapediaCSVParser(data_path)
    session = SessionLocal()

    try:
        mapper = DataMapper(session)

        # Parse all CSV files
        logger.info("Parsing CSV files...")
        data = parser.parse_all()

        # Save to database
        logger.info("Saving data to database...")
        counts = mapper.save_all(data)

        # Log results
        for table, count in counts.items():
            logger.info(f"Imported {count} {table}")

        logger.info("Database seeding completed successfully!")

    except Exception as e:
        logger.error(f"Error during database seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()

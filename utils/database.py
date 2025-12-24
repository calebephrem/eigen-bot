"""
Database configuration for SQLite3 connections.
This module provides database path constants for sync sqlite3 operations.
"""

import os

# Database file path - stored in the root directory
DATABASE_NAME = "botdata.db"

# Get absolute path to database
def get_database_path() -> str:
    """Get the absolute path to the database file."""
    return os.path.abspath(DATABASE_NAME)

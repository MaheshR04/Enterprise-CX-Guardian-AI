"""
MongoDB Connection Manager Proxy — Backward compatibility wrapper around db_connection.
"""

from app.database.connection import db_connection, DatabaseConnection

# Alias for backward compatibility
db_manager = db_connection
DatabaseManager = DatabaseConnection

__all__ = ["db_manager", "DatabaseManager"]

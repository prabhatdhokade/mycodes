"""
Data Processor Application

A modular, production-ready Python application for config-driven operations 
on CSV/Excel files with database and file output capabilities.
"""

__version__ = "1.0.0"
__author__ = "Data Processor Team"

from .core.reader import DataReader
from .core.writer import DataWriter
from .core.operations import DataOperations
from .db.db_manager import DatabaseManager
from .main import process_data, process_data_with_config

__all__ = [
    "DataReader",
    "DataWriter", 
    "DataOperations",
    "DatabaseManager",
    "process_data",
    "process_data_with_config"
]
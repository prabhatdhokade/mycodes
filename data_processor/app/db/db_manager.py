"""
Database management module for SQLite operations.
"""

import sqlite3
import pandas as pd
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path


class DatabaseManager:
    """
    Handles SQLite database operations.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.connection = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> sqlite3.Connection:
        """
        Establish connection to SQLite database.
        
        Returns:
            SQLite connection object
        """
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(str(self.db_path))
            self.logger.info(f"Connected to database: {self.db_path}")
            return self.connection
        except Exception as e:
            self.logger.error(f"Error connecting to database: {str(e)}")
            raise
    
    def close(self) -> None:
        """
        Close database connection.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
            self.logger.info("Database connection closed")
    
    def write_dataframe(self, 
                       df: pd.DataFrame, 
                       table_name: str, 
                       if_exists: str = 'replace',
                       index: bool = False,
                       **kwargs) -> bool:
        """
        Write DataFrame to SQLite table.
        
        Args:
            df: DataFrame to write
            table_name: Name of the table
            if_exists: How to behave if table exists ('replace', 'append', 'fail')
            index: Whether to write DataFrame index as a column
            **kwargs: Additional arguments for pd.to_sql
            
        Returns:
            True if successful
        """
        if not self.connection:
            self.connect()
        
        try:
            df.to_sql(
                table_name, 
                self.connection, 
                if_exists=if_exists, 
                index=index,
                **kwargs
            )
            self.logger.info(f"Successfully wrote {len(df)} rows to table '{table_name}'")
            return True
        except Exception as e:
            self.logger.error(f"Error writing DataFrame to table: {str(e)}")
            raise
    
    def read_table(self, table_name: str, query: Optional[str] = None) -> pd.DataFrame:
        """
        Read data from SQLite table.
        
        Args:
            table_name: Name of the table to read
            query: Custom SQL query (if None, reads entire table)
            
        Returns:
            DataFrame with table data
        """
        if not self.connection:
            self.connect()
        
        try:
            if query:
                df = pd.read_sql_query(query, self.connection)
            else:
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.connection)
            
            self.logger.info(f"Successfully read {len(df)} rows from table '{table_name}'")
            return df
        except Exception as e:
            self.logger.error(f"Error reading table: {str(e)}")
            raise
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute custom SQL query.
        
        Args:
            query: SQL query to execute
            
        Returns:
            DataFrame with query results
        """
        if not self.connection:
            self.connect()
        
        try:
            df = pd.read_sql_query(query, self.connection)
            self.logger.info(f"Successfully executed query: {query[:50]}...")
            return df
        except Exception as e:
            self.logger.error(f"Error executing query: {str(e)}")
            raise
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        if not self.connection:
            self.connect()
        
        try:
            # Get table schema
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            return {
                "table_name": table_name,
                "columns": [{"name": col[1], "type": col[2], "nullable": not col[3]} for col in columns],
                "row_count": row_count
            }
        except Exception as e:
            self.logger.error(f"Error getting table info: {str(e)}")
            raise
    
    def list_tables(self) -> List[str]:
        """
        List all tables in the database.
        
        Returns:
            List of table names
        """
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            self.logger.info(f"Found {len(tables)} tables in database")
            return tables
        except Exception as e:
            self.logger.error(f"Error listing tables: {str(e)}")
            raise
    
    def drop_table(self, table_name: str) -> bool:
        """
        Drop a table from the database.
        
        Args:
            table_name: Name of the table to drop
            
        Returns:
            True if successful
        """
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.connection.commit()
            self.logger.info(f"Successfully dropped table '{table_name}'")
            return True
        except Exception as e:
            self.logger.error(f"Error dropping table: {str(e)}")
            raise
    
    def create_index(self, table_name: str, column: str, index_name: Optional[str] = None) -> bool:
        """
        Create an index on a table column.
        
        Args:
            table_name: Name of the table
            column: Name of the column to index
            index_name: Name of the index (if None, auto-generated)
            
        Returns:
            True if successful
        """
        if not self.connection:
            self.connect()
        
        try:
            if not index_name:
                index_name = f"idx_{table_name}_{column}"
            
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column})")
            self.connection.commit()
            self.logger.info(f"Successfully created index '{index_name}' on {table_name}.{column}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating index: {str(e)}")
            raise
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
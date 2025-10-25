"""
Data writing module for CSV, Excel, and SQLite files.
"""

import pandas as pd
import logging
from typing import Union, Optional, Dict, Any
from pathlib import Path


class DataWriter:
    """
    Handles writing data to CSV, Excel, and SQLite files.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def write_data(self, 
                   data: pd.DataFrame, 
                   output_type: str, 
                   output_path: str, 
                   **kwargs) -> bool:
        """
        Write DataFrame to specified output format.
        
        Args:
            data: DataFrame to write
            output_type: Type of output ('csv', 'excel', 'sqlite')
            output_path: Path for output file
            **kwargs: Additional arguments for write functions
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If output_type is not supported
        """
        try:
            if output_type.lower() == 'csv':
                return self._write_csv(data, output_path, **kwargs)
            elif output_type.lower() == 'excel':
                return self._write_excel(data, output_path, **kwargs)
            elif output_type.lower() == 'sqlite':
                return self._write_sqlite(data, output_path, **kwargs)
            else:
                raise ValueError(f"Unsupported output type: {output_type}")
        except Exception as e:
            self.logger.error(f"Error writing data: {str(e)}")
            raise
    
    def _write_csv(self, data: pd.DataFrame, output_path: str, **kwargs) -> bool:
        """
        Write DataFrame to CSV file.
        
        Args:
            data: DataFrame to write
            output_path: Path for CSV file
            **kwargs: Additional arguments for pd.to_csv
            
        Returns:
            True if successful
        """
        from .utils import ensure_directory_exists
        
        ensure_directory_exists(output_path)
        
        default_params = {
            'index': False,
            'encoding': 'utf-8'
        }
        default_params.update(kwargs)
        
        data.to_csv(output_path, **default_params)
        self.logger.info(f"Successfully wrote CSV file: {output_path} ({len(data)} rows)")
        return True
    
    def _write_excel(self, data: pd.DataFrame, output_path: str, **kwargs) -> bool:
        """
        Write DataFrame to Excel file.
        
        Args:
            data: DataFrame to write
            output_path: Path for Excel file
            **kwargs: Additional arguments for pd.to_excel
            
        Returns:
            True if successful
        """
        from .utils import ensure_directory_exists
        
        ensure_directory_exists(output_path)
        
        default_params = {
            'index': False,
            'engine': 'openpyxl'
        }
        default_params.update(kwargs)
        
        data.to_excel(output_path, **default_params)
        self.logger.info(f"Successfully wrote Excel file: {output_path} ({len(data)} rows)")
        return True
    
    def _write_sqlite(self, data: pd.DataFrame, output_path: str, **kwargs) -> bool:
        """
        Write DataFrame to SQLite database.
        
        Args:
            data: DataFrame to write
            output_path: Path for SQLite database
            **kwargs: Additional arguments for pd.to_sql
            
        Returns:
            True if successful
        """
        from .utils import ensure_directory_exists
        from ..db.db_manager import DatabaseManager
        
        ensure_directory_exists(output_path)
        
        # Extract table name from kwargs or use default
        table_name = kwargs.pop('table_name', 'processed_data')
        
        # Use DatabaseManager for SQLite operations
        db_manager = DatabaseManager(output_path)
        
        try:
            db_manager.write_dataframe(data, table_name, **kwargs)
            self.logger.info(f"Successfully wrote to SQLite: {output_path} table '{table_name}' ({len(data)} rows)")
            return True
        finally:
            db_manager.close()
    
    def append_data(self, 
                   data: pd.DataFrame, 
                   output_type: str, 
                   output_path: str, 
                   **kwargs) -> bool:
        """
        Append DataFrame to existing file.
        
        Args:
            data: DataFrame to append
            output_type: Type of output ('csv', 'excel')
            output_path: Path for output file
            **kwargs: Additional arguments for write functions
            
        Returns:
            True if successful
        """
        try:
            if output_type.lower() == 'csv':
                return self._append_csv(data, output_path, **kwargs)
            elif output_type.lower() == 'excel':
                return self._append_excel(data, output_path, **kwargs)
            else:
                raise ValueError(f"Append not supported for output type: {output_type}")
        except Exception as e:
            self.logger.error(f"Error appending data: {str(e)}")
            raise
    
    def _append_csv(self, data: pd.DataFrame, output_path: str, **kwargs) -> bool:
        """
        Append DataFrame to CSV file.
        
        Args:
            data: DataFrame to append
            output_path: Path for CSV file
            **kwargs: Additional arguments for pd.to_csv
            
        Returns:
            True if successful
        """
        from .utils import ensure_directory_exists
        
        ensure_directory_exists(output_path)
        
        default_params = {
            'index': False,
            'encoding': 'utf-8',
            'mode': 'a',
            'header': not Path(output_path).exists()
        }
        default_params.update(kwargs)
        
        data.to_csv(output_path, **default_params)
        self.logger.info(f"Successfully appended to CSV file: {output_path} ({len(data)} rows)")
        return True
    
    def _append_excel(self, data: pd.DataFrame, output_path: str, **kwargs) -> bool:
        """
        Append DataFrame to Excel file (creates new sheet).
        
        Args:
            data: DataFrame to append
            output_path: Path for Excel file
            **kwargs: Additional arguments for pd.to_excel
            
        Returns:
            True if successful
        """
        from .utils import ensure_directory_exists
        
        ensure_directory_exists(output_path)
        
        # For Excel append, we'll create a new sheet
        sheet_name = kwargs.pop('sheet_name', f'Sheet_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}')
        
        default_params = {
            'index': False,
            'engine': 'openpyxl',
            'sheet_name': sheet_name
        }
        default_params.update(kwargs)
        
        # If file exists, append to existing workbook
        if Path(output_path).exists():
            with pd.ExcelWriter(output_path, mode='a', engine='openpyxl') as writer:
                data.to_excel(writer, **default_params)
        else:
            data.to_excel(output_path, **default_params)
        
        self.logger.info(f"Successfully appended to Excel file: {output_path} sheet '{sheet_name}' ({len(data)} rows)")
        return True
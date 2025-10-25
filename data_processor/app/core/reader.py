"""
Data reading module for CSV and Excel files.
"""

import pandas as pd
import logging
from typing import List, Union, Optional
from pathlib import Path


class DataReader:
    """
    Handles reading data from CSV and Excel files.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def read_file(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Read a single file (CSV or Excel) into a DataFrame.
        
        Args:
            file_path: Path to the file to read
            **kwargs: Additional arguments for pandas read functions
            
        Returns:
            DataFrame containing the file data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.csv':
                return self._read_csv(file_path, **kwargs)
            elif file_extension in ['.xlsx', '.xls']:
                return self._read_excel(file_path, **kwargs)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
    
    def read_files(self, file_paths: List[str], **kwargs) -> List[pd.DataFrame]:
        """
        Read multiple files into a list of DataFrames.
        
        Args:
            file_paths: List of file paths to read
            **kwargs: Additional arguments for pandas read functions
            
        Returns:
            List of DataFrames
        """
        dataframes = []
        
        for file_path in file_paths:
            try:
                df = self.read_file(file_path, **kwargs)
                dataframes.append(df)
                self.logger.info(f"Successfully read file: {file_path} ({len(df)} rows)")
            except Exception as e:
                self.logger.error(f"Failed to read file {file_path}: {str(e)}")
                raise
        
        return dataframes
    
    def _read_csv(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """
        Read CSV file with default parameters.
        
        Args:
            file_path: Path to CSV file
            **kwargs: Additional arguments for pd.read_csv
            
        Returns:
            DataFrame
        """
        default_params = {
            'encoding': 'utf-8',
            'index_col': None
        }
        default_params.update(kwargs)
        
        return pd.read_csv(file_path, **default_params)
    
    def _read_excel(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """
        Read Excel file with default parameters.
        
        Args:
            file_path: Path to Excel file
            **kwargs: Additional arguments for pd.read_excel
            
        Returns:
            DataFrame
        """
        default_params = {
            'index_col': None,
            'engine': 'openpyxl'
        }
        default_params.update(kwargs)
        
        return pd.read_excel(file_path, **default_params)
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get basic information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"exists": False}
        
        try:
            # Read just the first few rows to get column info
            df = self.read_file(file_path)
            
            return {
                "exists": True,
                "size_bytes": file_path.stat().st_size,
                "rows": len(df),
                "columns": list(df.columns),
                "dtypes": df.dtypes.to_dict(),
                "file_extension": file_path.suffix.lower()
            }
        except Exception as e:
            return {
                "exists": True,
                "error": str(e)
            }
"""
Data transformation operations module.
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Union, Optional
from .utils import safe_eval


class DataOperations:
    """
    Handles various data transformation operations.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def rename_columns(self, data: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Rename columns in the DataFrame.
        
        Args:
            data: Input DataFrame
            mapping: Dictionary mapping old column names to new ones
            
        Returns:
            DataFrame with renamed columns
        """
        try:
            result = data.rename(columns=mapping)
            self.logger.info(f"Renamed columns: {mapping}")
            return result
        except Exception as e:
            self.logger.error(f"Error renaming columns: {str(e)}")
            raise
    
    def filter_rows(self, data: pd.DataFrame, condition: str) -> pd.DataFrame:
        """
        Filter rows based on a condition.
        
        Args:
            data: Input DataFrame
            condition: Pandas query string for filtering
            
        Returns:
            Filtered DataFrame
        """
        try:
            result = data.query(condition)
            self.logger.info(f"Filtered rows with condition: {condition} ({len(result)} rows remaining)")
            return result
        except Exception as e:
            self.logger.error(f"Error filtering rows: {str(e)}")
            raise
    
    def add_column(self, data: pd.DataFrame, name: str, formula: str) -> pd.DataFrame:
        """
        Add a calculated column to the DataFrame.
        
        Args:
            data: Input DataFrame
            name: Name of the new column
            formula: Mathematical expression for the new column
            
        Returns:
            DataFrame with new column
        """
        try:
            result = data.copy()
            result[name] = result.eval(formula)
            self.logger.info(f"Added column '{name}' with formula: {formula}")
            return result
        except Exception as e:
            self.logger.error(f"Error adding column: {str(e)}")
            raise
    
    def drop_duplicates(self, data: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Remove duplicate rows from the DataFrame.
        
        Args:
            data: Input DataFrame
            subset: List of column names to consider for duplicates
            
        Returns:
            DataFrame with duplicates removed
        """
        try:
            result = data.drop_duplicates(subset=subset)
            removed_count = len(data) - len(result)
            self.logger.info(f"Removed {removed_count} duplicate rows")
            return result
        except Exception as e:
            self.logger.error(f"Error dropping duplicates: {str(e)}")
            raise
    
    def drop_nulls(self, data: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Remove rows with null values.
        
        Args:
            data: Input DataFrame
            subset: List of column names to check for nulls
            
        Returns:
            DataFrame with null rows removed
        """
        try:
            result = data.dropna(subset=subset)
            removed_count = len(data) - len(result)
            self.logger.info(f"Removed {removed_count} rows with null values")
            return result
        except Exception as e:
            self.logger.error(f"Error dropping nulls: {str(e)}")
            raise
    
    def merge_dataframes(self, 
                        dataframes: List[pd.DataFrame], 
                        on: str, 
                        how: str = 'inner') -> pd.DataFrame:
        """
        Merge multiple DataFrames.
        
        Args:
            dataframes: List of DataFrames to merge
            on: Column name to merge on
            how: Type of merge ('left', 'right', 'inner', 'outer')
            
        Returns:
            Merged DataFrame
        """
        try:
            if len(dataframes) < 2:
                raise ValueError("At least 2 DataFrames required for merge")
            
            result = dataframes[0]
            for i, df in enumerate(dataframes[1:], 1):
                result = result.merge(df, on=on, how=how, suffixes=('', f'_df{i}'))
            
            self.logger.info(f"Merged {len(dataframes)} DataFrames on column '{on}' using '{how}' join")
            return result
        except Exception as e:
            self.logger.error(f"Error merging DataFrames: {str(e)}")
            raise
    
    def aggregate_data(self, 
                      data: pd.DataFrame, 
                      group_by: List[str], 
                      aggregations: Dict[str, str]) -> pd.DataFrame:
        """
        Aggregate data by grouping columns.
        
        Args:
            data: Input DataFrame
            group_by: List of columns to group by
            aggregations: Dictionary mapping column names to aggregation functions
            
        Returns:
            Aggregated DataFrame
        """
        try:
            result = data.groupby(group_by).agg(aggregations).reset_index()
            self.logger.info(f"Aggregated data by {group_by} with functions: {aggregations}")
            return result
        except Exception as e:
            self.logger.error(f"Error aggregating data: {str(e)}")
            raise
    
    def sort_data(self, data: pd.DataFrame, by: Union[str, List[str]], ascending: bool = True) -> pd.DataFrame:
        """
        Sort DataFrame by specified columns.
        
        Args:
            data: Input DataFrame
            by: Column name(s) to sort by
            ascending: Sort order
            
        Returns:
            Sorted DataFrame
        """
        try:
            result = data.sort_values(by=by, ascending=ascending)
            self.logger.info(f"Sorted data by {by} (ascending={ascending})")
            return result
        except Exception as e:
            self.logger.error(f"Error sorting data: {str(e)}")
            raise
    
    def select_columns(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Select specific columns from DataFrame.
        
        Args:
            data: Input DataFrame
            columns: List of column names to select
            
        Returns:
            DataFrame with selected columns
        """
        try:
            result = data[columns]
            self.logger.info(f"Selected columns: {columns}")
            return result
        except Exception as e:
            self.logger.error(f"Error selecting columns: {str(e)}")
            raise
    
    def fill_nulls(self, data: pd.DataFrame, method: str = 'forward', value: Any = None) -> pd.DataFrame:
        """
        Fill null values in DataFrame.
        
        Args:
            data: Input DataFrame
            method: Method to fill nulls ('forward', 'backward', 'fill', 'value')
            value: Value to fill with (if method is 'value')
            
        Returns:
            DataFrame with filled nulls
        """
        try:
            result = data.copy()
            
            if method == 'value' and value is not None:
                result = result.fillna(value)
            elif method == 'forward':
                result = result.fillna(method='ffill')
            elif method == 'backward':
                result = result.fillna(method='bfill')
            else:
                raise ValueError(f"Invalid fill method: {method}")
            
            self.logger.info(f"Filled nulls using method: {method}")
            return result
        except Exception as e:
            self.logger.error(f"Error filling nulls: {str(e)}")
            raise
    
    def apply_function(self, data: pd.DataFrame, column: str, function: str) -> pd.DataFrame:
        """
        Apply a function to a column.
        
        Args:
            data: Input DataFrame
            column: Column name to apply function to
            function: Function name ('upper', 'lower', 'strip', 'round', etc.)
            
        Returns:
            DataFrame with function applied
        """
        try:
            result = data.copy()
            
            if function == 'upper':
                result[column] = result[column].str.upper()
            elif function == 'lower':
                result[column] = result[column].str.lower()
            elif function == 'strip':
                result[column] = result[column].str.strip()
            elif function == 'round':
                result[column] = result[column].round()
            else:
                raise ValueError(f"Unsupported function: {function}")
            
            self.logger.info(f"Applied function '{function}' to column '{column}'")
            return result
        except Exception as e:
            self.logger.error(f"Error applying function: {str(e)}")
            raise
    
    def execute_operation(self, operation: Dict[str, Any], data: pd.DataFrame) -> pd.DataFrame:
        """
        Execute a single operation on the DataFrame.
        
        Args:
            operation: Operation configuration dictionary
            data: Input DataFrame
            
        Returns:
            Transformed DataFrame
        """
        operation_type = operation.get('type')
        
        if operation_type == 'rename_columns':
            return self.rename_columns(data, operation.get('mapping', {}))
        
        elif operation_type == 'filter_rows':
            return self.filter_rows(data, operation.get('condition', ''))
        
        elif operation_type == 'add_column':
            return self.add_column(
                data, 
                operation.get('name', ''), 
                operation.get('formula', '')
            )
        
        elif operation_type == 'drop_duplicates':
            return self.drop_duplicates(data, operation.get('subset'))
        
        elif operation_type == 'drop_nulls':
            return self.drop_nulls(data, operation.get('subset'))
        
        elif operation_type == 'select_columns':
            return self.select_columns(data, operation.get('columns', []))
        
        elif operation_type == 'sort_data':
            return self.sort_data(
                data, 
                operation.get('by', []), 
                operation.get('ascending', True)
            )
        
        elif operation_type == 'fill_nulls':
            return self.fill_nulls(
                data, 
                operation.get('method', 'forward'),
                operation.get('value')
            )
        
        elif operation_type == 'apply_function':
            return self.apply_function(
                data, 
                operation.get('column', ''), 
                operation.get('function', '')
            )
        
        elif operation_type == 'aggregate':
            return self.aggregate_data(
                data,
                operation.get('group_by', []),
                operation.get('aggregations', {})
            )
        
        else:
            raise ValueError(f"Unknown operation type: {operation_type}")
    
    def execute_operations(self, operations: List[Dict[str, Any]], data: pd.DataFrame) -> pd.DataFrame:
        """
        Execute a list of operations on the DataFrame.
        
        Args:
            operations: List of operation configuration dictionaries
            data: Input DataFrame
            
        Returns:
            Transformed DataFrame
        """
        result = data.copy()
        
        for i, operation in enumerate(operations):
            try:
                self.logger.info(f"Executing operation {i+1}/{len(operations)}: {operation.get('type', 'unknown')}")
                result = self.execute_operation(operation, result)
            except Exception as e:
                self.logger.error(f"Error in operation {i+1}: {str(e)}")
                raise
        
        return result
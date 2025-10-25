"""
Main processing module for data transformation pipeline.
"""

import logging
from typing import Dict, Any, List
import pandas as pd

from .core.reader import DataReader
from .core.writer import DataWriter
from .core.operations import DataOperations
from .core.utils import load_config, validate_config, setup_logging


class DataProcessor:
    """
    Main data processing class that orchestrates the entire pipeline.
    """
    
    def __init__(self, config_path: str, log_level: str = "INFO"):
        """
        Initialize data processor.
        
        Args:
            config_path: Path to configuration file
            log_level: Logging level
        """
        self.logger = setup_logging(log_level)
        self.config = self._load_and_validate_config(config_path)
        
        # Initialize components
        self.reader = DataReader()
        self.writer = DataWriter()
        self.operations = DataOperations()
        
        self.logger.info("DataProcessor initialized successfully")
    
    def _load_and_validate_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load and validate configuration file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Validated configuration dictionary
        """
        try:
            config = load_config(config_path)
            validate_config(config)
            self.logger.info(f"Configuration loaded and validated: {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"Configuration error: {str(e)}")
            raise
    
    def process(self) -> bool:
        """
        Execute the complete data processing pipeline.
        
        Returns:
            True if processing completed successfully
        """
        try:
            self.logger.info("Starting data processing pipeline")
            
            # Step 1: Read input files
            input_data = self._read_input_files()
            
            # Step 2: Apply operations
            processed_data = self._apply_operations(input_data)
            
            # Step 3: Write output
            self._write_output(processed_data)
            
            self.logger.info("Data processing pipeline completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise
    
    def _read_input_files(self) -> List[pd.DataFrame]:
        """
        Read all input files specified in configuration.
        
        Returns:
            List of DataFrames from input files
        """
        input_files = self.config['input_files']
        self.logger.info(f"Reading {len(input_files)} input files")
        
        dataframes = self.reader.read_files(input_files)
        
        # Log file information
        for i, (file_path, df) in enumerate(zip(input_files, dataframes)):
            self.logger.info(f"File {i+1}: {file_path} - {len(df)} rows, {len(df.columns)} columns")
        
        return dataframes
    
    def _apply_operations(self, input_data: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Apply all operations to the input data.
        
        Args:
            input_data: List of input DataFrames
            
        Returns:
            Processed DataFrame
        """
        operations = self.config['operations']
        self.logger.info(f"Applying {len(operations)} operations")
        
        # Start with the first DataFrame
        if not input_data:
            return pd.DataFrame()
        
        processed_data = input_data[0].copy()
        
        # Apply operations one by one, handling merge specially
        for i, operation in enumerate(operations):
            try:
                self.logger.info(f"Executing operation {i+1}/{len(operations)}: {operation.get('type', 'unknown')}")
                
                if operation.get('type') == 'merge':
                    # Handle merge operation with remaining DataFrames
                    if len(input_data) < 2:
                        self.logger.warning("Merge operation requires at least 2 input files. Skipping merge.")
                        continue
                    
                    # Handle YAML parsing issue where 'on' becomes True
                    merge_on = operation.get('on') or operation.get(True)
                    merge_how = operation.get('how', 'inner')
                    
                    if not merge_on:
                        self.logger.error("Merge operation requires 'on' parameter. Skipping merge.")
                        continue
                    
                    self.logger.info(f"Merging DataFrames on column '{merge_on}' using '{merge_how}' join")
                    # Merge the current processed data with the remaining DataFrames
                    all_dataframes = [processed_data] + input_data[1:]
                    processed_data = self.operations.merge_dataframes(all_dataframes, merge_on, merge_how)
                else:
                    # Apply regular operation
                    processed_data = self.operations.execute_operation(operation, processed_data)
                    
            except Exception as e:
                self.logger.error(f"Error in operation {i+1}: {str(e)}")
                raise
        
        self.logger.info(f"Operations completed. Final data: {len(processed_data)} rows, {len(processed_data.columns)} columns")
        return processed_data
    
    def _handle_merge_operation(self, input_data: List[pd.DataFrame], operations: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Handle merge operation if present in operations list.
        
        Args:
            input_data: List of input DataFrames
            operations: List of operations
            
        Returns:
            Merged DataFrame or None if no merge operation
        """
        merge_ops = [op for op in operations if op.get('type') == 'merge']
        
        if not merge_ops:
            return None
        
        if len(merge_ops) > 1:
            self.logger.warning("Multiple merge operations found. Using the first one.")
        
        merge_op = merge_ops[0]
        merge_on = merge_op.get('on')
        merge_how = merge_op.get('how', 'inner')
        
        if not merge_on:
            raise ValueError("Merge operation requires 'on' parameter specifying the column to merge on")
        
        if len(input_data) < 2:
            raise ValueError("Merge operation requires at least 2 input files")
        
        self.logger.info(f"Merging {len(input_data)} DataFrames on column '{merge_on}' using '{merge_how}' join")
        return self.operations.merge_dataframes(input_data, merge_on, merge_how)
    
    def _write_output(self, data: pd.DataFrame) -> None:
        """
        Write processed data to output destination.
        
        Args:
            data: Processed DataFrame
        """
        output_config = self.config['output']
        output_type = output_config['type']
        output_path = output_config['path']
        
        self.logger.info(f"Writing output to {output_type}: {output_path}")
        
        # Prepare additional parameters
        write_params = {k: v for k, v in output_config.items() if k not in ['type', 'path']}
        
        success = self.writer.write_data(data, output_type, output_path, **write_params)
        
        if success:
            self.logger.info(f"Successfully wrote {len(data)} rows to {output_path}")
        else:
            raise RuntimeError(f"Failed to write data to {output_path}")


def process_data(config_path: str, log_level: str = "INFO") -> bool:
    """
    Convenience function to process data using a configuration file.
    
    Args:
        config_path: Path to configuration file
        log_level: Logging level
        
    Returns:
        True if processing completed successfully
    """
    processor = DataProcessor(config_path, log_level)
    return processor.process()


def process_data_with_config(config: Dict[str, Any], log_level: str = "INFO") -> bool:
    """
    Process data using a configuration dictionary.
    
    Args:
        config: Configuration dictionary
        log_level: Logging level
        
    Returns:
        True if processing completed successfully
    """
    from .core.utils import validate_config
    
    # Validate configuration
    validate_config(config)
    
    # Create a temporary processor with the config
    processor = DataProcessor.__new__(DataProcessor)
    processor.logger = setup_logging(log_level)
    processor.config = config
    processor.reader = DataReader()
    processor.writer = DataWriter()
    processor.operations = DataOperations()
    
    return processor.process()
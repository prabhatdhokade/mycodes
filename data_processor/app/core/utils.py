"""
Utility functions for data processing operations.
"""

import logging
import os
import yaml
import json
from typing import Dict, Any, List, Union
from pathlib import Path


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('data_processor.log')
        ]
    )
    return logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML or JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file format is invalid
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(file)
            elif config_path.suffix.lower() == '.json':
                return json.load(file)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")
    except Exception as e:
        raise ValueError(f"Error loading configuration: {str(e)}")


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure and required fields.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    required_fields = ['input_files', 'operations', 'output']
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field in config: {field}")
    
    # Validate input_files
    if not isinstance(config['input_files'], list) or not config['input_files']:
        raise ValueError("input_files must be a non-empty list")
    
    # Validate operations
    if not isinstance(config['operations'], list):
        raise ValueError("operations must be a list")
    
    # Validate output
    output = config['output']
    if not isinstance(output, dict):
        raise ValueError("output must be a dictionary")
    
    if 'type' not in output:
        raise ValueError("output must have 'type' field")
    
    valid_output_types = ['csv', 'excel', 'sqlite']
    if output['type'] not in valid_output_types:
        raise ValueError(f"output type must be one of: {valid_output_types}")
    
    return True


def ensure_directory_exists(file_path: str) -> None:
    """
    Ensure the directory for the given file path exists.
    
    Args:
        file_path: Path to file
    """
    directory = Path(file_path).parent
    directory.mkdir(parents=True, exist_ok=True)


def get_file_extension(file_path: str) -> str:
    """
    Get file extension in lowercase.
    
    Args:
        file_path: Path to file
        
    Returns:
        File extension without dot
    """
    return Path(file_path).suffix.lower().lstrip('.')


def safe_eval(expression: str, data: Dict[str, Any]) -> Any:
    """
    Safely evaluate a mathematical expression using pandas eval.
    
    Args:
        expression: Mathematical expression string
        data: Dictionary containing variables for evaluation
        
    Returns:
        Result of expression evaluation
    """
    import pandas as pd
    
    try:
        # Create a temporary DataFrame with the data for evaluation
        df = pd.DataFrame([data])
        return df.eval(expression).iloc[0]
    except Exception as e:
        raise ValueError(f"Error evaluating expression '{expression}': {str(e)}")


def format_error_message(operation: str, error: Exception) -> str:
    """
    Format error message for operations.
    
    Args:
        operation: Name of the operation that failed
        error: Exception that occurred
        
    Returns:
        Formatted error message
    """
    return f"Error in {operation}: {type(error).__name__}: {str(error)}"
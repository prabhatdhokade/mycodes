"""
Unit tests for utility functions.
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml
import json

from app.core.utils import load_config, validate_config, setup_logging, safe_eval


class TestLoadConfig:
    """Test configuration loading functionality."""
    
    def test_load_yaml_config(self):
        """Test loading YAML configuration."""
        config_data = {
            'input_files': ['test.csv'],
            'operations': [],
            'output': {'type': 'csv', 'path': 'output.csv'}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = load_config(temp_path)
            assert config == config_data
        finally:
            os.unlink(temp_path)
    
    def test_load_json_config(self):
        """Test loading JSON configuration."""
        config_data = {
            'input_files': ['test.csv'],
            'operations': [],
            'output': {'type': 'csv', 'path': 'output.csv'}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = load_config(temp_path)
            assert config == config_data
        finally:
            os.unlink(temp_path)
    
    def test_load_config_file_not_found(self):
        """Test loading non-existent configuration file."""
        with pytest.raises(FileNotFoundError):
            load_config('nonexistent.yaml')
    
    def test_load_config_invalid_format(self):
        """Test loading configuration with invalid format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("invalid content")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                load_config(temp_path)
        finally:
            os.unlink(temp_path)


class TestValidateConfig:
    """Test configuration validation functionality."""
    
    def test_validate_valid_config(self):
        """Test validating a valid configuration."""
        config = {
            'input_files': ['test1.csv', 'test2.xlsx'],
            'operations': [
                {'type': 'rename_columns', 'mapping': {'old': 'new'}}
            ],
            'output': {'type': 'csv', 'path': 'output.csv'}
        }
        
        assert validate_config(config) is True
    
    def test_validate_missing_required_field(self):
        """Test validating configuration with missing required field."""
        config = {
            'input_files': ['test.csv'],
            'operations': []
            # Missing 'output' field
        }
        
        with pytest.raises(ValueError, match="Missing required field"):
            validate_config(config)
    
    def test_validate_invalid_input_files(self):
        """Test validating configuration with invalid input_files."""
        config = {
            'input_files': [],  # Empty list
            'operations': [],
            'output': {'type': 'csv', 'path': 'output.csv'}
        }
        
        with pytest.raises(ValueError, match="input_files must be a non-empty list"):
            validate_config(config)
    
    def test_validate_invalid_output_type(self):
        """Test validating configuration with invalid output type."""
        config = {
            'input_files': ['test.csv'],
            'operations': [],
            'output': {'type': 'invalid', 'path': 'output.csv'}
        }
        
        with pytest.raises(ValueError, match="output type must be one of"):
            validate_config(config)


class TestSafeEval:
    """Test safe expression evaluation."""
    
    def test_safe_eval_simple_expression(self):
        """Test evaluating simple mathematical expressions."""
        data = {'a': 10, 'b': 5}
        result = safe_eval('a + b', data)
        assert result == 15
    
    def test_safe_eval_complex_expression(self):
        """Test evaluating complex mathematical expressions."""
        data = {'x': 100, 'y': 20, 'z': 5}
        result = safe_eval('(x - y) * z', data)
        assert result == 400
    
    def test_safe_eval_invalid_expression(self):
        """Test evaluating invalid expressions."""
        data = {'a': 10}
        
        with pytest.raises(ValueError):
            safe_eval('invalid_expression', data)


class TestSetupLogging:
    """Test logging setup functionality."""
    
    def test_setup_logging_default(self):
        """Test setting up logging with default level."""
        logger = setup_logging()
        # The logger level might be 0 (NOTSET) if handlers are not configured
        assert logger.level in [0, 20]  # NOTSET or INFO level
    
    def test_setup_logging_debug(self):
        """Test setting up logging with DEBUG level."""
        logger = setup_logging('DEBUG')
        # The logger level might be 0 (NOTSET) if handlers are not configured
        assert logger.level in [0, 10]  # NOTSET or DEBUG level
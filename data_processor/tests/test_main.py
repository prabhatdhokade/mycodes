"""
Unit tests for main processing functionality.
"""

import pytest
import tempfile
import os
import pandas as pd
from pathlib import Path

from app.main import DataProcessor, process_data, process_data_with_config


class TestDataProcessor:
    """Test main data processor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_data = pd.DataFrame({
            'customer_id': [1001, 1002, 1003],
            'product_name': ['Laptop', 'Mouse', 'Keyboard'],
            'sale_amount': [1000, 50, 100],
            'sale_date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        
        self.customer_data = pd.DataFrame({
            'customer_id': [1001, 1002, 1003],
            'customer_name': ['John', 'Jane', 'Bob'],
            'customer_email': ['john@email.com', 'jane@email.com', 'bob@email.com']
        })
    
    def create_test_config(self, operations=None, output_type='csv'):
        """Create a test configuration file."""
        if operations is None:
            operations = [
                {'type': 'rename_columns', 'mapping': {'sale_amount': 'amount'}},
                {'type': 'filter_rows', 'condition': 'amount > 100'}
            ]
        
        config = {
            'input_files': ['test_sales.csv'],
            'operations': operations,
            'output': {
                'type': output_type,
                'path': 'test_output.csv'
            }
        }
        
        return config
    
    def test_processor_initialization(self):
        """Test processor initialization with valid config."""
        config = self.create_test_config()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config, f)
            config_path = f.name
        
        try:
            processor = DataProcessor(config_path)
            assert processor.config == config
        finally:
            os.unlink(config_path)
    
    def test_processor_invalid_config(self):
        """Test processor initialization with invalid config."""
        invalid_config = {'invalid': 'config'}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(invalid_config, f)
            config_path = f.name
        
        try:
            with pytest.raises(ValueError):
                DataProcessor(config_path)
        finally:
            os.unlink(config_path)
    
    def test_process_data_function(self):
        """Test the process_data convenience function."""
        config = self.create_test_config()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config, f)
            config_path = f.name
        
        # Create test input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.test_data.to_csv(f.name, index=False)
            input_path = f.name
        
        try:
            # Update config with actual file path
            config['input_files'] = [input_path]
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
            
            # This should work without errors
            result = process_data(config_path)
            assert result is True
        finally:
            os.unlink(config_path)
            os.unlink(input_path)
    
    def test_process_data_with_config_dict(self):
        """Test processing data with configuration dictionary."""
        config = self.create_test_config()
        
        # Create test input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.test_data.to_csv(f.name, index=False)
            input_path = f.name
        
        try:
            config['input_files'] = [input_path]
            result = process_data_with_config(config)
            assert result is True
        finally:
            os.unlink(input_path)
    
    def test_merge_operation_handling(self):
        """Test handling of merge operations."""
        config = self.create_test_config(operations=[
            {'type': 'merge', 'on': 'customer_id', 'how': 'left'}
        ])
        
        # Create test input files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1:
            self.test_data.to_csv(f1.name, index=False)
            sales_path = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            self.customer_data.to_csv(f2.name, index=False)
            customer_path = f2.name
        
        try:
            config['input_files'] = [sales_path, customer_path]
            result = process_data_with_config(config)
            assert result is True
        finally:
            os.unlink(sales_path)
            os.unlink(customer_path)
    
    def test_sqlite_output(self):
        """Test SQLite output functionality."""
        config = self.create_test_config(output_type='sqlite')
        config['output']['path'] = 'test_output.db'
        config['output']['table_name'] = 'test_table'
        
        # Create test input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.test_data.to_csv(f.name, index=False)
            input_path = f.name
        
        try:
            config['input_files'] = [input_path]
            result = process_data_with_config(config)
            assert result is True
            
            # Verify database was created
            assert Path('test_output.db').exists()
        finally:
            os.unlink(input_path)
            if Path('test_output.db').exists():
                os.unlink('test_output.db')
    
    def test_excel_output(self):
        """Test Excel output functionality."""
        config = self.create_test_config(output_type='excel')
        config['output']['path'] = 'test_output.xlsx'
        
        # Create test input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.test_data.to_csv(f.name, index=False)
            input_path = f.name
        
        try:
            config['input_files'] = [input_path]
            result = process_data_with_config(config)
            assert result is True
            
            # Verify Excel file was created
            assert Path('test_output.xlsx').exists()
        finally:
            os.unlink(input_path)
            if Path('test_output.xlsx').exists():
                os.unlink('test_output.xlsx')
"""
Unit tests for data reader functionality.
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path

from app.core.reader import DataReader


class TestDataReader:
    """Test data reader functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reader = DataReader()
        self.test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'value': [100, 200, 300]
        })
    
    def test_read_csv_file(self):
        """Test reading CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.test_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            result = self.reader.read_file(temp_path)
            pd.testing.assert_frame_equal(result, self.test_data)
        finally:
            os.unlink(temp_path)
    
    def test_read_excel_file(self):
        """Test reading Excel file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as f:
            self.test_data.to_excel(f.name, index=False)
            temp_path = f.name
        
        try:
            result = self.reader.read_file(temp_path)
            pd.testing.assert_frame_equal(result, self.test_data)
        finally:
            os.unlink(temp_path)
    
    def test_read_file_not_found(self):
        """Test reading non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.reader.read_file('nonexistent.csv')
    
    def test_read_unsupported_format(self):
        """Test reading unsupported file format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test data")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                self.reader.read_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_read_multiple_files(self):
        """Test reading multiple files."""
        # Create two test files
        file1_data = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
        file2_data = pd.DataFrame({'id': [3, 4], 'name': ['C', 'D']})
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1:
            file1_data.to_csv(f1.name, index=False)
            temp_path1 = f1.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            file2_data.to_csv(f2.name, index=False)
            temp_path2 = f2.name
        
        try:
            results = self.reader.read_files([temp_path1, temp_path2])
            assert len(results) == 2
            pd.testing.assert_frame_equal(results[0], file1_data)
            pd.testing.assert_frame_equal(results[1], file2_data)
        finally:
            os.unlink(temp_path1)
            os.unlink(temp_path2)
    
    def test_get_file_info(self):
        """Test getting file information."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.test_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            info = self.reader.get_file_info(temp_path)
            assert info['exists'] is True
            assert info['rows'] == 3
            assert info['columns'] == ['id', 'name', 'value']
            assert info['file_extension'] == '.csv'
        finally:
            os.unlink(temp_path)
    
    def test_get_file_info_not_found(self):
        """Test getting info for non-existent file."""
        info = self.reader.get_file_info('nonexistent.csv')
        assert info['exists'] is False
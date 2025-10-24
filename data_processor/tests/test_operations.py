"""
Unit tests for data operations functionality.
"""

import pytest
import pandas as pd
import numpy as np

from app.core.operations import DataOperations


class TestDataOperations:
    """Test data operations functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.operations = DataOperations()
        self.test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'Alice', 'David'],
            'value': [100, 200, 300, 100, 400],
            'category': ['A', 'B', 'A', 'A', 'C']
        })
    
    def test_rename_columns(self):
        """Test renaming columns."""
        mapping = {'id': 'customer_id', 'name': 'customer_name'}
        result = self.operations.rename_columns(self.test_data, mapping)
        
        expected_columns = ['customer_id', 'customer_name', 'value', 'category']
        assert list(result.columns) == expected_columns
    
    def test_filter_rows(self):
        """Test filtering rows based on condition."""
        result = self.operations.filter_rows(self.test_data, 'value > 200')
        
        expected_data = self.test_data[self.test_data['value'] > 200]
        pd.testing.assert_frame_equal(result, expected_data)
    
    def test_add_column(self):
        """Test adding calculated column."""
        result = self.operations.add_column(self.test_data, 'double_value', 'value * 2')
        
        expected_values = self.test_data['value'] * 2
        expected_values.name = 'double_value'
        pd.testing.assert_series_equal(result['double_value'], expected_values)
    
    def test_drop_duplicates(self):
        """Test dropping duplicate rows."""
        result = self.operations.drop_duplicates(self.test_data, subset=['name'])
        
        expected_data = self.test_data.drop_duplicates(subset=['name'])
        pd.testing.assert_frame_equal(result, expected_data)
    
    def test_drop_nulls(self):
        """Test dropping rows with null values."""
        data_with_nulls = self.test_data.copy()
        data_with_nulls.loc[2, 'value'] = np.nan
        
        result = self.operations.drop_nulls(data_with_nulls, subset=['value'])
        
        expected_data = data_with_nulls.dropna(subset=['value'])
        pd.testing.assert_frame_equal(result, expected_data)
    
    def test_merge_dataframes(self):
        """Test merging multiple DataFrames."""
        df1 = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
        df2 = pd.DataFrame({'id': [1, 3], 'value': [100, 200]})
        
        result = self.operations.merge_dataframes([df1, df2], on='id', how='inner')
        
        expected = df1.merge(df2, on='id', how='inner')
        pd.testing.assert_frame_equal(result, expected)
    
    def test_aggregate_data(self):
        """Test aggregating data."""
        aggregations = {'value': 'sum', 'id': 'count'}
        result = self.operations.aggregate_data(
            self.test_data, 
            group_by=['category'], 
            aggregations=aggregations
        )
        
        expected = self.test_data.groupby('category').agg(aggregations).reset_index()
        pd.testing.assert_frame_equal(result, expected)
    
    def test_sort_data(self):
        """Test sorting data."""
        result = self.operations.sort_data(self.test_data, by='value', ascending=False)
        
        expected = self.test_data.sort_values('value', ascending=False)
        pd.testing.assert_frame_equal(result, expected)
    
    def test_select_columns(self):
        """Test selecting specific columns."""
        columns = ['id', 'name']
        result = self.operations.select_columns(self.test_data, columns)
        
        expected = self.test_data[columns]
        pd.testing.assert_frame_equal(result, expected)
    
    def test_fill_nulls_with_value(self):
        """Test filling nulls with specific value."""
        data_with_nulls = self.test_data.copy()
        data_with_nulls.loc[2, 'value'] = np.nan
        
        result = self.operations.fill_nulls(data_with_nulls, method='value', value=999)
        
        expected = data_with_nulls.fillna(999)
        pd.testing.assert_frame_equal(result, expected)
    
    def test_fill_nulls_forward(self):
        """Test forward filling nulls."""
        data_with_nulls = self.test_data.copy()
        data_with_nulls.loc[2, 'value'] = np.nan
        
        result = self.operations.fill_nulls(data_with_nulls, method='forward')
        
        expected = data_with_nulls.fillna(method='ffill')
        pd.testing.assert_frame_equal(result, expected)
    
    def test_apply_function_upper(self):
        """Test applying upper case function."""
        result = self.operations.apply_function(self.test_data, 'name', 'upper')
        
        expected = self.test_data.copy()
        expected['name'] = expected['name'].str.upper()
        pd.testing.assert_frame_equal(result, expected)
    
    def test_apply_function_lower(self):
        """Test applying lower case function."""
        result = self.operations.apply_function(self.test_data, 'name', 'lower')
        
        expected = self.test_data.copy()
        expected['name'] = expected['name'].str.lower()
        pd.testing.assert_frame_equal(result, expected)
    
    def test_execute_operation_rename(self):
        """Test executing rename operation."""
        operation = {
            'type': 'rename_columns',
            'mapping': {'id': 'customer_id'}
        }
        
        result = self.operations.execute_operation(operation, self.test_data)
        
        expected = self.operations.rename_columns(self.test_data, {'id': 'customer_id'})
        pd.testing.assert_frame_equal(result, expected)
    
    def test_execute_operation_filter(self):
        """Test executing filter operation."""
        operation = {
            'type': 'filter_rows',
            'condition': 'value > 200'
        }
        
        result = self.operations.execute_operation(operation, self.test_data)
        
        expected = self.operations.filter_rows(self.test_data, 'value > 200')
        pd.testing.assert_frame_equal(result, expected)
    
    def test_execute_operation_add_column(self):
        """Test executing add column operation."""
        operation = {
            'type': 'add_column',
            'name': 'double_value',
            'formula': 'value * 2'
        }
        
        result = self.operations.execute_operation(operation, self.test_data)
        
        expected = self.operations.add_column(self.test_data, 'double_value', 'value * 2')
        pd.testing.assert_frame_equal(result, expected)
    
    def test_execute_operation_unknown(self):
        """Test executing unknown operation."""
        operation = {'type': 'unknown_operation'}
        
        with pytest.raises(ValueError, match="Unknown operation type"):
            self.operations.execute_operation(operation, self.test_data)
    
    def test_execute_operations_multiple(self):
        """Test executing multiple operations."""
        operations = [
            {'type': 'filter_rows', 'condition': 'value > 200'},
            {'type': 'add_column', 'name': 'double_value', 'formula': 'value * 2'},
            {'type': 'sort_data', 'by': 'double_value', 'ascending': False}
        ]
        
        result = self.operations.execute_operations(operations, self.test_data)
        
        # Apply operations manually to get expected result
        expected = self.test_data.copy()
        expected = expected[expected['value'] > 200]
        expected['double_value'] = expected['value'] * 2
        expected = expected.sort_values('double_value', ascending=False)
        
        pd.testing.assert_frame_equal(result, expected)
# Data Processor

A modular, production-ready Python application for config-driven operations on CSV/Excel files with database and file output capabilities.

## Features

- **Config-driven processing**: Define data transformations using YAML or JSON configuration files
- **Multiple input formats**: Support for CSV and Excel files
- **Multiple output formats**: CSV, Excel, and SQLite database
- **Rich operations**: Column renaming, filtering, calculated columns, merging, aggregations, and more
- **Modular architecture**: Clean, extensible codebase with separate modules for different concerns
- **CLI interface**: Easy-to-use command-line interface
- **Library support**: Import and use as a Python library
- **Comprehensive testing**: Full test coverage with pytest
- **Error handling**: Robust error handling and logging throughout

## Installation

1. Clone or download the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Basic Usage

```bash
# Process data with configuration file
python -m app.cli --config app/config/config.yaml

# Validate configuration without processing
python -m app.cli --config app/config/config.yaml --validate-only

# Use custom log level
python -m app.cli --config app/config/config.yaml --log-level DEBUG
```

### 2. Using as a Library

```python
from app import process_data, DataProcessor

# Process with configuration file
success = process_data('config.yaml')

# Process with configuration dictionary
config = {
    'input_files': ['data/input.csv'],
    'operations': [
        {'type': 'rename_columns', 'mapping': {'old_name': 'new_name'}},
        {'type': 'filter_rows', 'condition': 'amount > 1000'}
    ],
    'output': {'type': 'csv', 'path': 'output.csv'}
}
success = process_data_with_config(config)
```

## Configuration

The application uses YAML or JSON configuration files to define data processing pipelines.

### Basic Configuration Structure

```yaml
input_files:
  - data/input_sales.csv
  - data/input_customers.xlsx

operations:
  - type: rename_columns
    mapping:
      old_name: new_name
  - type: filter_rows
    condition: "amount > 5000"
  - type: add_column
    name: total_with_tax
    formula: "amount * 1.18"

output:
  type: csv
  path: data/processed_output.csv
```

### Supported Operations

#### Column Operations
- **rename_columns**: Rename columns using a mapping dictionary
- **select_columns**: Select specific columns
- **add_column**: Add calculated columns using mathematical expressions

#### Row Operations
- **filter_rows**: Filter rows based on conditions using pandas query syntax
- **drop_duplicates**: Remove duplicate rows
- **drop_nulls**: Remove rows with null values
- **fill_nulls**: Fill null values using various methods

#### Data Transformations
- **sort_data**: Sort data by specified columns
- **apply_function**: Apply string functions (upper, lower, strip, round)
- **merge**: Merge multiple input files on specified columns

#### Aggregations
- **aggregate**: Group data and apply aggregation functions (sum, count, mean, etc.)

### Output Types

#### CSV Output
```yaml
output:
  type: csv
  path: data/output.csv
  index: false
  encoding: utf-8
```

#### Excel Output
```yaml
output:
  type: excel
  path: data/output.xlsx
  sheet_name: Processed_Data
  index: false
```

#### SQLite Output
```yaml
output:
  type: sqlite
  path: data/output.db
  table_name: processed_data
  if_exists: replace
```

## Example Configurations

### Sales Data Processing
```yaml
input_files:
  - data/sales.csv
  - data/customers.xlsx

operations:
  - type: rename_columns
    mapping:
      customer_id: customer_id
      product_name: product
      sale_amount: amount
      sale_date: date

  - type: filter_rows
    condition: "amount > 5000"

  - type: add_column
    name: total_with_tax
    formula: "amount * 1.18"

  - type: merge
    on: customer_id
    how: left

  - type: drop_duplicates
    subset: ["customer_id", "product"]

  - type: sort_data
    by: ["amount"]
    ascending: false

output:
  type: csv
  path: data/processed_sales.csv
```

### Customer Analytics
```yaml
input_files:
  - data/transactions.csv

operations:
  - type: filter_rows
    condition: "amount > 1000"

  - type: add_column
    name: commission
    formula: "amount * 0.05"

  - type: aggregate
    group_by: ["customer_id"]
    aggregations:
      amount: "sum"
      commission: "sum"
      transaction_id: "count"

  - type: sort_data
    by: ["amount"]
    ascending: false

output:
  type: sqlite
  path: data/customer_analytics.db
  table_name: customer_summary
```

## Project Structure

```
data_processor/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main processing logic
│   ├── cli.py               # Command-line interface
│   ├── config/              # Example configurations
│   │   ├── config.yaml
│   │   ├── config_sqlite.yaml
│   │   └── config_excel.yaml
│   ├── core/                # Core processing modules
│   │   ├── reader.py        # File reading
│   │   ├── writer.py        # File writing
│   │   ├── operations.py    # Data transformations
│   │   └── utils.py         # Utility functions
│   └── db/                  # Database management
│       └── db_manager.py    # SQLite operations
├── data/                    # Sample data files
│   ├── input_sales.csv
│   └── input_customers.xlsx
├── tests/                   # Unit tests
│   ├── test_utils.py
│   ├── test_reader.py
│   ├── test_operations.py
│   └── test_main.py
├── requirements.txt
└── README.md
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_operations.py

# Run with verbose output
pytest -v
```

## Advanced Usage

### Custom Operations

You can extend the application by adding new operations to the `DataOperations` class:

```python
def custom_operation(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Custom operation implementation."""
    # Your custom logic here
    return processed_data
```

### Database Management

The `DatabaseManager` class provides additional database operations:

```python
from app.db.db_manager import DatabaseManager

with DatabaseManager('data.db') as db:
    # Write data
    db.write_dataframe(df, 'table_name')
    
    # Read data
    data = db.read_table('table_name')
    
    # Execute custom queries
    result = db.execute_query("SELECT * FROM table_name WHERE amount > 1000")
```

### Error Handling

The application includes comprehensive error handling and logging:

```python
import logging

# Set up custom logging
logger = logging.getLogger('data_processor')
logger.setLevel(logging.DEBUG)

# Process with custom error handling
try:
    success = process_data('config.yaml')
except Exception as e:
    logger.error(f"Processing failed: {e}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions, issues, or contributions, please open an issue on the project repository.
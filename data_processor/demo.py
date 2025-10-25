#!/usr/bin/env python3
"""
Demo script showcasing the Data Processor library usage.
"""

from app import process_data, process_data_with_config

def demo_with_config_file():
    """Demo using configuration file."""
    print("=== Demo: Processing with Configuration File ===")
    
    try:
        success = process_data('app/config/config.yaml')
        if success:
            print("✅ Successfully processed data with config file!")
            print("📁 Output saved to: data/processed_output.csv")
        else:
            print("❌ Processing failed")
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_with_config_dict():
    """Demo using configuration dictionary."""
    print("\n=== Demo: Processing with Configuration Dictionary ===")
    
    config = {
        'input_files': ['data/input_sales.csv'],
        'operations': [
            {'type': 'rename_columns', 'mapping': {'sale_amount': 'amount'}},
            {'type': 'filter_rows', 'condition': 'amount > 10000'},
            {'type': 'add_column', 'name': 'total_with_tax', 'formula': 'amount * 1.18'},
            {'type': 'sort_data', 'by': 'amount', 'ascending': False}
        ],
        'output': {'type': 'csv', 'path': 'data/demo_output.csv'}
    }
    
    try:
        success = process_data_with_config(config)
        if success:
            print("✅ Successfully processed data with config dictionary!")
            print("📁 Output saved to: data/demo_output.csv")
        else:
            print("❌ Processing failed")
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_sqlite_output():
    """Demo SQLite output."""
    print("\n=== Demo: SQLite Output ===")
    
    config = {
        'input_files': ['data/input_sales.csv', 'data/input_customers.xlsx'],
        'operations': [
            {'type': 'rename_columns', 'mapping': {'sale_amount': 'amount'}},
            {'type': 'filter_rows', 'condition': 'amount > 5000'},
            {'type': 'merge', 'on': 'customer_id', 'how': 'left'},
            {'type': 'add_column', 'name': 'total_with_tax', 'formula': 'amount * 1.18'}
        ],
        'output': {
            'type': 'sqlite', 
            'path': 'data/demo_output.db',
            'table_name': 'demo_data'
        }
    }
    
    try:
        success = process_data_with_config(config)
        if success:
            print("✅ Successfully processed data to SQLite!")
            print("📁 Database saved to: data/demo_output.db")
            print("📊 Table name: demo_data")
        else:
            print("❌ Processing failed")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    print("🚀 Data Processor Demo")
    print("=" * 50)
    
    # Run demos
    demo_with_config_file()
    demo_with_config_dict()
    demo_sqlite_output()
    
    print("\n🎉 Demo completed!")
    print("\nTo run the CLI version:")
    print("python3 -m app.cli --config app/config/config.yaml")
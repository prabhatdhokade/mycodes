"""
Command-line interface for the data processor.
"""

import argparse
import sys
import os
from pathlib import Path

from .main import process_data
from .core.utils import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """
    Create command-line argument parser.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Data Processor - Config-driven CSV/Excel data transformation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process data with configuration file
  python -m app.cli --config config/config.yaml
  
  # Process with custom log level
  python -m app.cli --config config/config.yaml --log-level DEBUG
  
  # Validate configuration without processing
  python -m app.cli --config config/config.yaml --validate-only
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        required=True,
        help='Path to configuration file (YAML or JSON)'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--validate-only', '-v',
        action='store_true',
        help='Only validate configuration file without processing data'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Data Processor 1.0.0'
    )
    
    return parser


def validate_config_file(config_path: str) -> bool:
    """
    Validate configuration file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        from .core.utils import load_config, validate_config
        
        config = load_config(config_path)
        validate_config(config)
        
        print(f"✅ Configuration file is valid: {config_path}")
        print(f"   - Input files: {len(config['input_files'])}")
        print(f"   - Operations: {len(config['operations'])}")
        print(f"   - Output type: {config['output']['type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {str(e)}")
        return False


def main():
    """
    Main CLI entry point.
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    try:
        # Check if config file exists
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"❌ Configuration file not found: {config_path}")
            sys.exit(1)
        
        # Validate configuration
        if not validate_config_file(args.config):
            sys.exit(1)
        
        # If validation only, exit here
        if args.validate_only:
            print("✅ Configuration validation completed successfully")
            sys.exit(0)
        
        # Process data
        print(f"🚀 Starting data processing with config: {args.config}")
        success = process_data(args.config, args.log_level)
        
        if success:
            print("✅ Data processing completed successfully")
            sys.exit(0)
        else:
            print("❌ Data processing failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
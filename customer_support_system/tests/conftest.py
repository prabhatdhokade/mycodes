"""Pytest configuration for the customer support system tests."""
import os
import sys

# Make `src` importable as a top-level module when running tests from the
# customer_support_system directory.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

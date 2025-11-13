import os
import sys

# Get the path to the parent directory (backend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the apps directory to the Python path
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# This file makes the apps directory a Python package

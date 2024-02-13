import unittest
import os
import sys

# sys.path mangling to make src directory visible
source_code = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, source_code)
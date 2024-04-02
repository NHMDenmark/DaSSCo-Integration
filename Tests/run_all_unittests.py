import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

loader = unittest.TestLoader()
start_dir = f"{project_root}/Tests"
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
runner.run(suite)
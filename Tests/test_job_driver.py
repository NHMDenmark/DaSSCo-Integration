import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from IntegrationServer.JobList.job_driver import JobDriver


class TestJobDriver(unittest.TestCase):
    
    def test_test(self):
        self.assertEqual(1, 1, "its working")



if __name__ == "__main__":
    unittest.main()
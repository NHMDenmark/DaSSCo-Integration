import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from fastapi.testclient import TestClient 

from IntegrationServer.StorageApi.storage_service import StorageService


class TestStorageService(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):

        # for api
        self.client = TestClient("name of imported app")

        pass

    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_test(self):
        self.assertEqual(1, 1, "its working")


if __name__ == "__main__":
    unittest.main()
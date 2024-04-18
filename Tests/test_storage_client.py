import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from IntegrationServer.StorageApi.storage_client import StorageClient
from IntegrationServer.MongoDB.mongo_connection import MongoConnection   

class TestStorageService(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.client = StorageClient()
        self.metadata = MongoConnection("metadata")

        self.guid = "test_mongo"

        self.metadata.create_metadata_entry("Tests/TestConfigFiles/test_metadata_entry2.json", self.guid)

    @classmethod
    def tearDownClass(self):
        
        self.metadata.delete_entry(self.guid)

        self.metadata.close_mdb()

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    # Cannot truly be tested since we cant delete assets later on
    """
    def test_create_asset(self):

        created = self.client.create_asset(self.guid, 9)

        self.assertTrue(created, f"Failed to create asset with guid: {self.guid}")
    """

if __name__ == "__main__":
    unittest.main()
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
    
    def test_get_status_code_from_exc(self):
        exc = Exception("Except Something Status 888: More excpetional stuff here: 555")
        
        status_code, note = self.client.get_status_code_from_exc(exc)

        self.assertEqual(status_code, 888, f"Expected 888, got {status_code}")
        self.assertEqual(note, "", f"Expected an empty string got {note}")

        exc = Exception("Except Something Status: 888: More excpetional stuff here: 555")
        
        status_code, note = self.client.get_status_code_from_exc(exc)

        self.assertEqual(status_code, -1, f"Expected -1, got {status_code}")

        exc = Exception("")
        
        status_code, note = self.client.get_status_code_from_exc(exc)

        self.assertEqual(status_code, -2, f"Expected -2, got {status_code}")
        self.assertEqual(note, f"Status code was not found and was set to -2", f"Expected: Status code was not found and was set to -2, got {note}")

        exc = Exception("Ex: 888")
        
        status_code, note = self.client.get_status_code_from_exc(exc)

        self.assertEqual(status_code, -2, f"Expected -2, got {status_code}")
        self.assertEqual(note, f"Status code was not found and was set to -2", f"Expected: Status code was not found and was set to -2, got {note}")

        exc = Exception("88: Exception")
        
        status_code, note = self.client.get_status_code_from_exc(exc)

        self.assertEqual(status_code, -2, f"Expected -2, got {status_code}")
        self.assertEqual(note, f"Status code was not found and was set to -2", f"Expected: Status code was not found and was set to -2, got {note}")


    # Cannot truly be tested since we cant delete assets later on
    """
    def test_create_asset(self):

        created = self.client.create_asset(self.guid, 9)

        self.assertTrue(created, f"Failed to create asset with guid: {self.guid}")
    """

if __name__ == "__main__":
    unittest.main()
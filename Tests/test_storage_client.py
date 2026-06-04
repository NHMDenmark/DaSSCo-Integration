import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from IntegrationServer.StorageApi.storage_client import StorageClient
from IntegrationServer.MongoDB.metadata_repository import MetadataRepository
from IntegrationServer.MongoDB.mongo_connection import MongoSharedClient   

class TestStorageService(unittest.TestCase):
# unittest library runs tests in alphabetical order (test_01_something, test_02_another_thing, etc)
    
    @classmethod
    def setUpClass(self):
        self.mongo_client = MongoSharedClient()
        self.client = StorageClient(self.mongo_client)
        self.metadata = MetadataRepository(self.mongo_client)

        self.guid = "test_mongo"

        #specimen
        self.institution = "test-institution"
        self.collection = "test-collection"
        self.barcode = "test_barcode"
        self.specimen_pid = "test_specimen_pid"
        self.preparation_types = ["sheet"]
        self.role_restrictions = []

        self.metadata.create_metadata_entry("Tests/TestConfigFiles/test_metadata_entry2.json", self.guid)

    @classmethod
    def tearDownClass(self):
        
        self.metadata.delete_entry(self.guid)

        self.mongo_client.close()

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_01_get_status_code_from_exc(self):
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

    #Specimen tests:
    def test_02_create_specimen(self):
        created, status_code, note = self.client.create_specimen(self.institution, self.collection, self.barcode, self.specimen_pid, self.preparation_types, role_restrictions=self.role_restrictions)

        self.assertTrue(created, f"Failed to create specimen with barcode: {self.barcode}, status code: {status_code}, note: {note}")

    def test_03_get_specimen(self):
        found, res, msg = self.client.get_specimen(self.institution, self.collection, self.barcode)

        self.assertTrue(found, f"Failed to find specimen with barcode: {self.barcode}, message: {msg}")
        self.assertEqual(res["data"].specimen_pid, self.specimen_pid, f"Expected specimen_pid: {self.specimen_pid}, got {res['data'].specimen_pid}")

    def test_04_update_specimen(self):
        new_preparation_types = ["pinned"]
        updated, status_code, note = self.client.update_specimen(self.institution, self.collection, self.barcode, self.specimen_pid, new_preparation_types, role_restrictions=self.role_restrictions)

        self.assertTrue(updated, f"Failed to update specimen with barcode: {self.barcode}, status code: {status_code}, note: {note}")

        found, res, msg = self.client.get_specimen(self.institution, self.collection, self.barcode)

        self.assertTrue(found, f"Failed to find specimen with barcode: {self.barcode}, message: {msg}")
        self.assertEqual(res["data"].preparation_types, new_preparation_types, f"Expected preparation_types: {new_preparation_types}, got {res["data"].preparation_types}")

    def test_05_delete_specimen(self):
        deleted, status_code, note = self.client.delete_specimen(self.institution, self.collection, self.barcode)

        self.assertTrue(deleted, f"Failed to delete specimen with barcode: {self.barcode}, status code: {status_code}, note: {note}")

        found, res, msg = self.client.get_specimen(self.institution, self.collection, self.barcode)

        self.assertFalse(found, f"Should not have found a specimen after deletion, but got: {res}, message: {msg}")

    """
    def test_06_create_asset(self):

        created, msg, exc, status = self.client.create_asset(self.guid, 9)
        print(created, msg, exc, status)

        self.assertTrue(created, f"Failed to create asset with guid: {self.guid}")
        self.assertEqual(status, 200, f"Expected status code 200, got {status}, message: {msg}, exception: {exc}")
    """
    

if __name__ == "__main__":
    unittest.main()
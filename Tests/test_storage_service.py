import unittest
import os
import sys
from datetime import datetime
import json

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from IntegrationServer.MongoDB.mongo_connection import MongoConnection
from StorageApi.api_metadata_model import ApiMetadataModel
from IntegrationServer.StorageApi.storage_service import StorageService

class TestStorageService(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.service = StorageService()
        self.metadata = MongoConnection("metadata")
        
        self.guid = "test_mongo"

        self.metadata.create_metadata_entry(f"{project_root}/Tests/TestConfigFiles/test_metadata_entry2.json", self.guid)
        

    @classmethod
    def tearDownClass(self):
        self.metadata.delete_entry(self.guid)

        self.metadata.close_mdb()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_metadata_creation_body(self):

        data = self.service.get_metadata_creation_body(self.guid)

        self.assertIsInstance(data, ApiMetadataModel, f"Failed to get metadata model for guid: {self.guid}")

        self.assertEqual(data.institution, "test-institution", f"Failed to find test-institution in institution field, found: {data.institution}")

    def test_get_metadata_json_format(self):
        
        data_json = self.service.get_metadata_json_format(self.guid)

        try:
            parsed_data = json.loads(data_json)
            is_json = True
        except Exception as e:
            is_json = False

        self.assertTrue(is_json, f"Failed to get a json from {self.guid}")

        self.assertEqual(parsed_data["status"], "WORKING_COPY", f"Failed to find WORKING_COPY as status found: {parsed_data["status"]}")


    def test_convert_str_to_datetime(self):
        
        timestring = "2000-12-24T14:14:14+02:00"

        datetime_obj = self.service.convert_str_to_datetime(timestring)

        self.assertIsInstance(datetime_obj, datetime, f"Failed to convert {timestring} to object of type datetime")

        timestring = "99999-12-24T14:14:14+02:009999"
        
        datetime_obj = self.service.convert_str_to_datetime(timestring)

        self.assertNotIsInstance(datetime_obj, datetime, f"Somehow converted {timestring} to object of type datetime")
        self.assertEqual(timestring, datetime_obj, f"Did not return {timestring} as {datetime_obj}")



if __name__ == "__main__":
    unittest.main()
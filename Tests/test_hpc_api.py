import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import json
import unittest
from fastapi.testclient import TestClient
from IntegrationServer.HpcApi.hpc_api import app
from IntegrationServer.MongoDB.track_repository import TrackRepository
from IntegrationServer.MongoDB.metadata_repository import MetadataRepository
from IntegrationServer.utility import Utility

class TestHPCApi(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @classmethod
    def setUpClass(self):
        self.track_repo = TrackRepository()
        self.metadata_repo = MetadataRepository()
        self.util = Utility()

        test_track_entry = self.util.read_json(f"{project_root}/Tests/TestConfigFiles/test_track_entry.json")
        self.track_repo.collection.insert_one(test_track_entry)

        test_metadata_entry = self.util.read_json(f"{project_root}/Tests/TestConfigFiles/test_metadata_entry.json")
        self.metadata_repo.collection.insert_one(test_metadata_entry)

    @classmethod
    def tearDownClass(self):
        self.track_repo.delete_entry("test_0001")
        self.track_repo.close_connection()
        
        self.metadata_repo.delete_entry("test_0001")
        self.metadata_repo.close_connection()

    def test_get_metadata(self):
        test_guid = "test_0001"
        response = self.client.get("/dev/api/v1/metadata_asset", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")
        response_data = response.json()
        self.assertEqual(response_data["institution"], "test-institution", f"Failed finding test-institution as institution, found: {response_data["institution"]}")
        
        test_guid = "bogus"
        response = self.client.get("/dev/api/v1/metadata_asset", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 422, f"Failed with a status {response.status_code} instead of 422")
    
    """
    deprecated not in use
    def test_receive_metadata(self):
        # can come later
        pass
    """
    
    def test_get_httplink(self):
        test_guid = "test_0001"
        response = self.client.get("/dev/api/v1/httplink", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")
        data = response.json()
        links = ["test/link/", ""]
        self.assertIn(data["link"], links, f"Failed finding link as test/link/ or "", found: {response.content}")
        

        test_guid = "bogus"
        response = self.client.get("/dev/api/v1/httplink", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 422, f"Failed with a status {response.status_code} instead of 422")
    
    def test_asset_ready(self):
        test_guid = "test_0001"
        response = self.client.post("/dev/api/v1/asset_ready", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")

        test_guid = "bogus"
        response = self.client.post("/dev/api/v1/asset_ready", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 422, f"Failed with a status {response.status_code}")
    
    def test_queue_job(self):
        test_model = {
            "guid": "test_0001",
            "job_name": "testing",
            "job_id": "-8",
            "timestamp": "1999-09-09T08:32:23.548+00:00" 
            }
        model_json = json.dumps(test_model)
        response = self.client.post("/dev/api/v1/queue_job", data= model_json)
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")

        test_model["guid"] = "bogus"
        model_json = json.dumps(test_model)
        response = self.client.post("/dev/api/v1/queue_job", data= model_json)
        self.assertEqual(response.status_code, 422, f"Failed with a status {response.status_code}")

    def test_start_job(self):
        test_model = {
            "guid": "test_0001",
            "job_name": "testing",
            "job_id": "-7",
            "timestamp": "1999-09-09T08:32:23.548+00:00" 
            }
        model_json = json.dumps(test_model)
        response = self.client.post("/dev/api/v1/start_job", data= model_json)
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")

        test_model["guid"] = "bogus"
        model_json = json.dumps(test_model)
        response = self.client.post("/dev/api/v1/start_job", data= model_json)
        self.assertEqual(response.status_code, 422, f"Failed with a status {response.status_code}")

    def test_derivative_uploaded(self):
        pass
    
    def test_asset_clean_up(self):
        test_guid = "bogus"
        response = self.client.post("/dev/api/v1/asset_clean_up", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 422, f"Expected status 422, got {response.status_code}")

        test_guid = "test_0001"
        response = self.client.post("/dev/api/v1/asset_clean_up", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 200, f"Expected status 200, got {response.status_code}")

    def test_update_asset(self):
        test_model = {
            "guid": "test_0001",
            "job": "testing",
            "status": "DONE",
            "data": {
                "funding": "triple up"
            }
        }
        model_json = json.dumps(test_model)
        response = self.client.post("/dev/api/v1/update_asset", data = model_json)
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")

        
        test_model["guid"] = "bogus"
        model_json = json.dumps(test_model)
        response = self.client.post("/dev/api/v1/update_asset", data= model_json)
        self.assertEqual(response.status_code, 422, f"Failed with a status {response.status_code}")

    def test_derivative_file_info(self):
        test_model = {
            "guid": "test_0001",
            "name": "test_0001.jpeg",
            "type": "jpeg",
            "check_sum": 12345,
            "file_size": 200
        }
        model_json = json.dumps(test_model)

        response = self.client.post("/dev/api/v1/derivative_file_info", data = model_json)
        self.assertEqual(response.status_code, 200, f"Expected status 200 got {response.status_code}")

        file_list = self.track_repo.get_value_for_key("test_0001", "file_list")
        check_sum = file_list[1]["check_sum"]
        self.assertEqual(check_sum, 12345, f"Expected check sum 12345 got {check_sum}")

        asset_size = self.track_repo.get_value_for_key("test_0001", "asset_size")
        self.assertEqual(asset_size, -191, f"Exepcted asset size to be -191 (9 + 200 - 400) got {asset_size}")

        test_model["guid"] = "bogus"
        model_json = json.dumps(test_model)
        response = self.client.post("/dev/api/v1/derivative_file_info", data = model_json)
        self.assertEqual(response.status_code, 422, f"Expected status 422 got {response.status_code}")

    def test_barcode(self):
        test_model = {
            "guid": "test_0001",
            "job": "testing",
            "status": "DONE",
            "barcodes": ["hyx-345-982"],
            "asset_subject": "specimen",
            "MSO": False,
            "MOS": True,
            "label": False,
            "disposable": "Disposable99"
        }
        model_json = json.dumps(test_model)
        
        response = self.client.post("/dev/api/v1/barcode", data = model_json)
        self.assertEqual(response.status_code, 200, f"Failed to update asset with guid: {test_model["guid"]} Got status code: {response.status_code}")
        
        test_model["guid"] = "bogus"
        model_json = json.dumps(test_model)
        response = self.client.post("/dev/api/v1/update_asset", data= model_json)
        self.assertEqual(response.status_code, 422, f"Failed with a status {response.status_code}")

if __name__ == "__main__":
    unittest.main()

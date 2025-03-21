import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import json
import unittest
from fastapi.testclient import TestClient
from IntegrationServer.HealthApi.health_api import health
from IntegrationServer.MongoDB.health_repository import HealthRepository
from IntegrationServer.MongoDB.track_repository import TrackRepository
from IntegrationServer.utility import Utility

# Testing this will create emails and slack messages also.
class TestHealthApi(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.health_repo = HealthRepository()
        self.track_repo = TrackRepository()
        self.util = Utility()

        test_track_entry = self.util.read_json(f"{project_root}/Tests/TestConfigFiles/test_track_entry.json")
        
        self.track_repo.collection.insert_one(test_track_entry)

        self.client = TestClient(health)
        self.service_name = "Test health api"
        self.test_message_model = {
            "guid": "test_0001",
            "service_name": self.service_name,
            "flag": "jobs_status",
            "flag_status": "waiting",
            "message": "Tha###TESTING###2024-06-28 10:51:57,066###Tests/test_health_api.py###Test message" 
            }
        self.test_bogus_message_model = {
            "guid": "bogus",
            "service_name": "bogus",
            "flag": "bogus",
            "flag_status": "bogus",
            "message": "bogus###bogus###bogus###bogus###bogus" 
            }
        self.test_change_status_model = {
            "service_name": self.service_name,
            "run_status": "TESTING",
            "message": "Tha###TESTING###2024-08-28 10:51:57,066###Tests/test_health_api.py###Test message for change run status"
            }
        self.test_bogus_change_status = {
            "service_name": "bogus",
            "run_status": "bogus",
            "message": "bogus###bogus###bogus###bogus###bogus"
        }
        self.test_pause_model = {
            "service_name": self.service_name,
            "run_status": "TESTING",
            "pause_counter": -1,
            "message": "Tha###TESTING###2024-09-28 10:51:57,066###Tests/test_health_api.py###Test message for attempted unpause"
        }
        self.test_bogus_pause_model = {
            "service_name": "bogus",
            "run_status": "bogus",
            "pause_counter": -99,
            "message": "bogus***bogus***bogus###bogus###bogus"
        }
        self.test_unexpected_error_model = {
            "service_name": self.service_name,
            "message": "Tha###TESTING###2024-10-28 10:51:57,066###Tests/test_health_api.py###Test message for unexpected error###Exception is a test"
        }
        self.test_bogus_unexpected_error_model = {
            "service_name": "bogus",
            "message": "bogus---bogus***bogus###bogus???bogus"
        }


    @classmethod
    def tearDownClass(self):
        # remove database test entries, the month number is the difference between them 2024 06, 07 08 etc
        self.health_repo.delete_entry("Tha_20240628105157066")
        self.health_repo.delete_entry("Tha_20240728105157066")
        self.health_repo.delete_entry("Tha_20240828105157066")
        self.health_repo.delete_entry("Tha_20240928105157066")
        self.health_repo.delete_entry("Tha_20241028105157066")
        self.track_repo.delete_entry("test_0001")
        self.track_repo.close_connection()
        self.health_repo.close_connection()
    
    def test_receive_warning(self):
        
        self.test_message_model["message"] = "Tha###TESTING###2024-06-28 10:51:57,066###Tests/test_health_api.py###Testing receive warning"

        model_json = json.dumps(self.test_message_model)
        print(model_json)
        response = self.client.post("/api/warning", data= model_json)
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")
        
        model_json = json.dumps(self.test_bogus_message_model)
        response = self.client.post("/api/warning", data= model_json)
        self.assertEqual(response.status_code, 422, f"Should have failed with a status 422 got: {response.status_code}")

    def test_receive_error(self):
        
        self.test_message_model["message"] = "Tha###TESTING###2024-07-28 10:51:57,066###Tests/test_health_api.py###Testing receive error"

        model_json = json.dumps(self.test_message_model)
        response = self.client.post("/api/error", data= model_json)
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")
        
        model_json = json.dumps(self.test_bogus_message_model)
        response = self.client.post("/api/error", data= model_json)
        self.assertEqual(response.status_code, 422, f"Should have failed with a status 422 got: {response.status_code}")

    def test_run_status_change(self):

        model_json = json.dumps(self.test_change_status_model)
        response = self.client.post("/api/run_change_status", data= model_json)
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")
        
        model_json = json.dumps(self.test_bogus_change_status)
        response = self.client.post("/api/run_change_status", data= model_json)
        self.assertEqual(response.status_code, 422, f"Should have failed with a status 422 got: {response.status_code}")

        self.test_bogus_change_status["message"] = "yoho_pirates_ahoy"

        model_json = json.dumps(self.test_bogus_change_status)
        response = self.client.post("/api/run_change_status", data= model_json)
        self.assertEqual(response.status_code, 422, f"Should have failed with a status 422 got: {response.status_code}")

    def test_attempted_unpause(self):
        
        model_json = json.dumps(self.test_pause_model)
        response = self.client.post("/api/attempt_unpause", data= model_json)
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")
        
        model_json = json.dumps(self.test_bogus_pause_model)
        response = self.client.post("/api/attempt_unpause", data= model_json)
        self.assertEqual(response.status_code, 422, f"Should have failed with a status 422 got: {response.status_code}")

    def test_unexpected_error(self):

        model_json = json.dumps(self.test_unexpected_error_model)
        response = self.client.post("/api/unexpected_error", data= model_json)
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")
        
        model_json = json.dumps(self.test_bogus_unexpected_error_model)
        response = self.client.post("/api/unexpected_error", data= model_json)
        self.assertEqual(response.status_code, 422, f"Should have failed with a status 422 got: {response.status_code}")

if __name__ == "__main__":
    unittest.main()
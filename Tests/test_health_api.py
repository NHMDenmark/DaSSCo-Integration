import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import json
import unittest
from fastapi.testclient import TestClient
from IntegrationServer.HealthApi.health_api import health
from IntegrationServer.MongoDB.health_repository import HealthRepository

class TestHPCApi(unittest.TestCase):
    def setUp(self):
        self.health_repo = HealthRepository()
        
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
        
    def tearDown(self):
        self.health_repo.delete_entry("Tha_20240628105157066")
        self.health_repo.close_connection()
    
    def test_receive_warning(self):
        
        self.test_message_model["message"] = "Tha###TESTING###2024-06-28 10:51:57,066###Tests/test_health_api.py###Testing receive warning"

        model_json = json.dumps(self.test_message_model)
        response = self.client.post("/api/warning", data= model_json)
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")
        
        model_json = json.dumps(self.test_bogus_message_model)
        response = self.client.post("/api/warning", data= model_json)
        self.assertEqual(response.status_code, 422, f"Should have failed with a status 422 got: {response.status_code}")


if __name__ == "__main__":
    unittest.main()
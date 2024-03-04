import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import unittest
from fastapi.testclient import TestClient
from IntegrationServer.HpcApi.hpc_api import app  

class TestHPCApi(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_metadata(self):
        test_guid = "test_0001"
        response = self.client.get("/api/v1/metadata_asset", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")
        response_data = response.json()
        self.assertEqual(response_data["institution"], "test-institution", f"Failed finding test-institution as institution, found: {response_data["institution"]}")
        
        test_guid = "bogus"
        response = self.client.get("/api/v1/metadata_asset", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 422, f"Failed with a status {response.status_code} instead of 422")

        response = self.client.get("/api/v1/metadata_asset")
        self.assertEqual(response.status_code, 422, f"Failed with a status {response.status_code} instead of 422")
    
    def test_get_httplink(self):
        test_guid = "test_0001"
        response = self.client.get("/api/v1/httplink", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")

        response_data = response.json()
        self.assertEqual(response_data, "test/link/", f"Failed finding link as test/link/, found: {response_data}")

        test_guid = "bogus"
        response = self.client.get("/api/v1/httplink", params = {"asset_guid": test_guid})
        self.assertEqual(response.status_code, 422, f"Failed with a status {response.status_code} instead of 422")

if __name__ == "__main__":
    unittest.main()

"""@app.get("/api/v1/metadata_asset")
def get_metadata(asset_guid: str):
    asset = service.get_metadata_asset(asset_guid)
    return asset  """
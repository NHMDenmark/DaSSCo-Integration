import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from fastapi.testclient import TestClient
from datetime import datetime
import json

from IntegrationServer.DashboardAPIs.control_api import control 
from IntegrationServer.MongoDB.track_repository import TrackRepository
from IntegrationServer.MongoDB.metadata_repository import MetadataRepository
from IntegrationServer.MongoDB.health_repository import HealthRepository
from IntegrationServer.MongoDB.service_repository import ServiceRepository
from IntegrationServer.MongoDB.mongo_connection import MongoSharedClient
from IntegrationServer.KeycloakInterface.auth import get_new_token
from IntegrationServer.utility import Utility

class TestControlApi(unittest.TestCase):
    # unittest library runs tests in alphabetical order (test_01_something, test_02_another_thing, etc)
    @classmethod
    def setUpClass(self):
        
        self.client = TestClient(control)

        self.mongo_client = MongoSharedClient()
        self.track_db = TrackRepository(self.mongo_client)
        self.metadata_db = MetadataRepository(self.mongo_client)
        self.health_db = HealthRepository(self.mongo_client)
        self.service_db = ServiceRepository(self.mongo_client)

        self.util = Utility()

        # model data, at bottom of script
        self.track_data = self.get_track_data()
        self.metadata_data = self.get_metadata_data()
        self.health_data = self.get_health_data()

        self.entry_id = "test_control_api"

        # create entries in dbs to be queried
        self.track_db.insert_entry(self.entry_id, self.track_data)
        self.metadata_db.insert_entry(self.entry_id, self.metadata_data)
        self.health_db.insert_entry(self.entry_id, self.health_data)
        self.service_db.create_micro_service_entry(self.entry_id)

        #get keycloak token for auth headers
        token = get_new_token()
        self.auth_headers = {
            "Authorization": f"Bearer {token}"
        }

    @classmethod
    def tearDownClass(self):
        
        # delete test entries
        self.track_db.delete_entry(self.entry_id)
        self.health_db.delete_entry(self.entry_id)
        self.metadata_db.delete_entry(self.entry_id)
        self.service_db.delete_entry(self.entry_id)

        # close db connections        
        self.mongo_client.close()    

    def test_01_set_all_run_status(self):

        response = self.client.put("/integration/control/set_all_run_status", params={"status":"RUNNING"}, headers=self.auth_headers)

        self.assertEqual(response.status_code, 200, f"Did not get status 200, instead got status {response.status_code}")

    def test_start_service(self):

        response = self.client.get("/integration/control/start_service", params={"service_name": "testy"}, headers=self.auth_headers)

        self.assertEqual(response.status_code, 500, f"Did not get status 500, instead got status {response.status_code}")

    def test_stop_service(self):

        response = self.client.post("/integration/control/stop_service", params={"service_name": "testy"}, headers=self.auth_headers)

        self.assertEqual(response.status_code, 500, f"Did not get status 500, instead got status {response.status_code}")

    def test_get_track_data(self):

        response = self.client.get("/integration/control/get_track_data", params={"guid":self.entry_id}, headers=self.auth_headers)

        response_data = response.json()

        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")

        self.assertEqual(response_data["files_status"], "ERROR", f"failed getting ERROR for files_status, got {response_data["files_status"]} instead")

        response = self.client.get("/integration/control/get_track_data", params={"guid":"humbug bogus"}, headers=self.auth_headers)

        response_data = response.json()

        self.assertNotEqual(response.status_code, 200, f"Should have failed but got status {response.status_code}")
        self.assertEqual(response_data["status"], "Asset does not exist", f"Found something instead of nothing.")        

    def test_get_metadata_data(self):

        response = self.client.get("/integration/control/get_metadata", params={"guid":self.entry_id}, headers=self.auth_headers)

        response_data = response.json()

        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")

        self.assertEqual(response_data["funding"][0], "Easter bunny", f"failed getting 'Easter bunny' for funding, got {response_data["funding"][0]} instead")

        response = self.client.get("/integration/control/get_metadata", params={"guid":"humbug bogus"}, headers=self.auth_headers)

        response_data = response.json()

        self.assertNotEqual(response.status_code, 200, f"Should have failed but got status {response.status_code}")
        self.assertEqual(response_data["status"], "Asset does not exist", f"Found something instead of nothing.")
        
    def test_get_health_data(self):
        
        response = self.client.get("/integration/control/get_health_data", params={"key":"guid", "value":self.entry_id}, headers=self.auth_headers)

        response_data = response.json()

        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")

        self.assertEqual(response_data[0]["message"], "Yo this is a test health entry", f"failed getting 'Yo this is a test health entry' for funding, got {response_data[0]["message"]} instead")

        response = self.client.get("/integration/control/get_health_data", params={"key":"guid", "value":"humbug bogus"}, headers=self.auth_headers)

        response_data = response.json()

        self.assertNotEqual(response.status_code, 200, f"Should have failed but got status {response.status_code}")
        self.assertEqual(response_data["status"], "No entries was found for search criterias key and value.", f"Found something instead of nothing.")

    def test_get_throttle_data(self):
        response = self.client.get("/integration/control/get_throttle_data", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200, f"Unexpected status code {response.status_code}")

    def test_get_error_lists(self):
        response = self.client.get("/integration/control/get_error_lists", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200, f"Unexpected status code {response.status_code}")

    def test_get_critical_error_lists(self):
        response = self.client.get("/integration/control/get_critical_error_lists", headers=self.auth_headers)
        response_data = response.json()
        
        self.assertEqual(response.status_code, 200, f"Unexpected status code {response.status_code}")
        self.assertGreaterEqual(response_data["critical_error_counts"][0]["available_for_services"], 1, f"Failed to find a critical error count for available_for_services to be equal or larger than 1.")

    def test_search_in_metadata(self):
        payload = {"key_values":[{"status": "CHAOS", "institution":"Mars"}], "time_key": None, "after": None, "before":None}
        response = self.client.post("/integration/control/search_in_metadata", json=payload, headers=self.auth_headers)
        response_data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["count"], 1)
        self.assertEqual(response_data["guids"][0], self.entry_id)
    
    def test_search_in_track(self):
        search_payload = {"key_values":[], "time_key": "created_timestamp", "after": None, "before": "2002-1-1" }
        response = self.client.post("/integration/control/search_in_track", json=search_payload, headers=self.auth_headers)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["count"], 1)
        self.assertEqual(response_data["guids"][0], self.entry_id)

    
    def test_search_in_health(self):
        search_payload = {"key_values":[{"guid":self.entry_id, "message": "Yo this is a test health entry"}], "time_key": None, "after": None, "before": None }
        response = self.client.post("/integration/control/search_in_health", json=search_payload, headers=self.auth_headers)
        response_data = response.json()
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["count"], 1)
        self.assertEqual(response_data["id_list"][0], self.entry_id)

    def test_update_track_data(self):
        update_payload = {
                        "key_values":{"erda_sync":"PERHAPS", "is_in_ars":"WHO_KNOWS"},
                        "job_name": "clean_up",
                        "job_key_values": {"priority":1000},
                        "asset_guids":[self.entry_id]
                    }
        response = self.client.put("/integration/control/update_track_data", json=update_payload, headers=self.auth_headers)
        response_data = response.json()
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["update_status"], True)
        self.assertEqual(response_data["message"], "Update success")

        response = self.client.get("/integration/control/get_track_data", params={"guid":self.entry_id}, headers=self.auth_headers)
        m_response_data = response.json()

        self.assertEqual(m_response_data["erda_sync"], "PERHAPS")
        self.assertEqual(m_response_data["is_in_ars"], "WHO_KNOWS")
    
    def test_update_metadata(self):
        update_payload = {
                        "key_values":{"payload_type":"firestones", "legality":{"copyright":"Green men", "license":"Blue men", "credit":None}},
                        "update_ars": False,
                        "asset_guids":[self.entry_id]
                    }
        response = self.client.put("/integration/control/update_metadata", json=update_payload, headers=self.auth_headers)
        response_data = response.json()
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["update_status"], True)
        self.assertEqual(response_data["message"], "Update success")

        response = self.client.get("/integration/control/get_metadata", params={"guid":self.entry_id}, headers=self.auth_headers)
        m_response_data = response.json()

        self.assertEqual(m_response_data["legality"]["license"], "Blue men")
        self.assertEqual(m_response_data["payload_type"], "firestones")

        update_payload = {
                        "key_values":{"payload_type":"firestones", "legality":{"copyright":"Green men", "license":"Blue men", "credit":None}},
                        "update_ars": False,
                        "asset_guids":[self.entry_id, "aber_nicht", "und_doch"]
                    }
        response = self.client.put("/integration/control/update_metadata", json=update_payload, headers=self.auth_headers)
        response_data = response.json()
    
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_data["update_status"], False)
        self.assertEqual(response_data["message"], "Failed to find assets: ['aber_nicht', 'und_doch']")

    def test_append_issue(self):
        append_payload = {            
            "issue": {
                "category": "star trek",
                "name": "pytest injection",
                "timestamp": datetime(2010, 10, 10, 10, 10, 10).isoformat(),
                "status": "CHAOS",
                "description": "automated test issue",
                "notes": "unit test note",
                "solved": False
            },
            "update_ars": False,
            "asset_guids":[self.entry_id]
        }
        response = self.client.put("/integration/control/append_issue", json=append_payload, headers=self.auth_headers)
        response_data = response.json()
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["update_status"], True)
        self.assertEqual(response_data["message"], "Update success")

        response = self.client.get("/integration/control/get_metadata", params={"guid":self.entry_id}, headers=self.auth_headers)
        m_response_data = response.json()
        
        self.assertEqual(m_response_data["issues"][1]["timestamp"], "2010-10-10T10:10:10")
        
    def test_update_issue(self):
        update_payload = {
            "issue_category": "star trek",
            "issue_name":"mars expedition",
            "key_values":{"notes":"green cheese", "description":"its made of cheese"},
            "update_ars": False,
            "asset_guids":[self.entry_id]
        }
        response = self.client.put("/integration/control/update_issue", json=update_payload, headers=self.auth_headers)
        response_data = response.json()
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["update_status"], True)
        self.assertEqual(response_data["message"], "Update success")

        response = self.client.get("/integration/control/get_metadata", params={"guid":self.entry_id}, headers=self.auth_headers)
        m_response_data = response.json()
        
        self.assertEqual(m_response_data["issues"][0]["notes"], "green cheese")
        self.assertEqual(m_response_data["issues"][0]["description"], "its made of cheese")

        update_payload = {
            "issue_category": "mixed up",
            "issue_name":"mars expedition",
            "key_values":{"notes":"green cheese", "description":"its made of cheese"},
            "update_ars": False,
            "asset_guids":[self.entry_id]
        }
        response = self.client.put("/integration/control/update_issue", json=update_payload, headers=self.auth_headers)
        response_data = response.json()
    
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_data["update_status"], False)
        self.assertEqual(response_data["message"], f"Could not find issue matching {self.entry_id}.")

    def test_get_service_data(self):
        response = self.client.get("/integration/control/get_service_data", params={"service_name": self.entry_id}, headers=self.auth_headers)
        response_data = response.json()
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["_id"], self.entry_id)
        self.assertEqual(response_data["pid"], None)

    def test_get_all_service_data(self):
        response = self.client.get("/integration/control/get_all_service_data", headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 200)   

    def get_health_data():

        health_data = {"service": "Hpc api Service",
                            "timestamp": datetime(2001, 2, 3, 12, 55, 25, 813),
                            "severity_level": "WARNING",
                            "message": "Yo this is a test health entry",
                            "guid": "test_control_api",
                            "exception": None,
                            "flag": None,
                            "sent": "No"}

        return health_data

    def get_metadata_data():

        metadata_data = {"asset_created_by":"",
                        "asset_deleted_by":"",
                        "asset_guid":"test_control_api",
                        "asset_pid":"test-pid",
                        "asset_subject":"stone",
                        "asset_updated_by":"",
                        "audited":False,
                        "audited_by":"",
                        "barcode":[],
                        "camera_setting_control":"v1",
                        "collection":"lamprey",
                        "complete_digitiser_list":[],
                        "date_asset_created_ars":None,
                        "date_asset_deleted_ars":None,
                        "date_asset_finalised":None,
                        "date_asset_taken":None,
                        "date_asset_updated_ars":None,
                        "date_audited":None,
                        "date_metadata_created_ars":None,
                        "date_metadata_ingested":None,
                        "date_metadata_updated_ars":None,
                        "date_pushed_to_specify":None,
                        "digitiser":"Bugs Bunny",
                        "external_publishers":[{"name":"Mars publication"}],
                        "file_format":"tif",
                        "funding":["Easter bunny"],
                        "institution":"Mars",
                        "issues":[{"category":"star trek", "name":"mars expedition", "status":"CHAOS", "timestamp":None, "description":"meteoritic interference", "notes":"big meteors", "solved":False}],
                        "legality":{"copyright":"Green men", "license":None, "credit":None},
                        "make_public":False,
                        "metadata_created_by":None,
                        "metadata_source":"test",
                        "metadata_updated_by":None,
                        "metadata_version":"v3.0.2",
                        "mos_id":"",
                        "multi_specimen":False,
                        "parent_guids":[],
                        "payload_type":"rocks",
                        "pipeline_name":"testpipemars",
                        "preparation_type":["cheesy"],
                        "push_to_specify":False,
                        "restricted_access":[],
                        "session_id":None,
                        "specify_attachment_remarks":None,
                        "specify_attachment_title": None,
                        "specimen_pid":None,
                        "status":"CHAOS",
                        "tags":{},
                        "workstation_name":"robotic-test-facility"
                        }

        return metadata_data

    def get_track_data():

        track_data = {"created_timestamp": datetime(2001, 11, 11, 9, 9, 9, 999999),
                        "pipeline": "PIPEPIOF0001",
                        "batch_list_name": "",
                        "job_list": [
                            {
                                "name": "uploader",
                                "status": "DONE",
                                "priority": 1,
                                "job_queued_time": datetime(2024, 11, 8, 13, 7, 29),
                                "job_start_time": datetime(2024, 11, 8, 13, 7, 29),
                                "hpc_job_id": "222222"
                            },
                            {
                                "name": "clean_up",
                                "status": "DONE",
                                "priority": 2,
                                "job_queued_time": datetime(2024, 11, 8, 13, 10, 17),
                                "job_start_time": datetime(2024, 11, 8, 13, 10, 18),
                                "hpc_job_id": "111111"
                            }
                        ],
                        "jobs_status": "DONE",
                        "file_list": [
                            {
                                "name": "test_control_api.jpeg",
                                "type": "jpeg",
                                "time_added": datetime(2024, 11, 5, 10, 43, 36, 890847),
                                "check_sum": 1254421177,
                                "file_size": 3,
                                "ars_link": "",
                                "erda_sync": "YES",
                                "deleted": False
                            }
                                ],
                        "files_status": "ERROR",
                        "asset_size": 300,
                        "proxy_path": "",
                        "asset_type": "PEST",
                        "hpc_ready": "NO",
                        "is_in_ars": "YES",
                        "has_new_file": "NO",
                        "has_open_share": "NO",
                        "erda_sync": "YES",
                        "update_metadata": "NO",
                        "available_for_services": "CRITICAL_ERROR",
                        "available_for_services_timestamp": None,
                        "available_for_services_wait_time": None
                        }
                            
        
        return track_data

if __name__ == "__main__":
    unittest.main()
import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from fastapi.testclient import TestClient
import json

from IntegrationServer.DashboardAPIs.control_api import control 
from IntegrationServer.MongoDB.track_repository import TrackRepository
from IntegrationServer.MongoDB.metadata_repository import MetadataRepository
from IntegrationServer.MongoDB.health_repository import HealthRepository
from IntegrationServer.utility import Utility

class TestControlApi(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        
        self.client = TestClient(control)

        self.track_db = TrackRepository()
        self.metadata_db = MetadataRepository()
        self.health_db = HealthRepository()

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


    @classmethod
    def tearDownClass(self):
        
        # delete test entries
        self.track_db.delete_entry(self.entry_id)
        self.health_db.delete_entry(self.entry_id)
        self.metadata_db.delete_entry(self.entry_id)

        # close db connections        
        self.track_db.close_connection()
        self.metadata_db.close_connection()
        self.health_db.close_connection()    

    def test_get_track_data(self):

        response = self.client.get("/control/get_track_data", params={"guid":self.entry_id})

        response_data = response.json()

        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")

        self.assertEqual(response_data["files_status"], "ERROR", f"failed getting ERROR for files_status, got {response_data["files_status"]} instead")

        response = self.client.get("/control/get_track_data", params={"guid":"humbug bogus"})

        response_data = response.json()

        self.assertNotEqual(response.status_code, 200, f"Should have failed but got status {response.status_code}")
        self.assertEqual(response_data["status"], "Asset does not exist", f"Found something instead of nothing.")        

    def test_get_metadata_data(self):

        response = self.client.get("/control/get_metadata", params={"guid":self.entry_id})

        response_data = response.json()

        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")

        self.assertEqual(response_data["funding"], "Easter bunny", f"failed getting 'Easter bunny' for funding, got {response_data["funding"]} instead")

        response = self.client.get("/control/get_metadata", params={"guid":"humbug bogus"})

        response_data = response.json()

        self.assertNotEqual(response.status_code, 200, f"Should have failed but got status {response.status_code}")
        self.assertEqual(response_data["status"], "Asset does not exist", f"Found something instead of nothing.")
        
    def test_get_health_data(self):
        
        response = self.client.get("/control/get_health_data", params={"guid":self.entry_id})

        response_data = response.json()

        self.assertEqual(response.status_code, 200, f"Failed with a status {response.status_code}")

        self.assertEqual(response_data[0]["message"], "Yo this is a test health entry", f"failed getting 'Yo this is a test health entry' for funding, got {response_data[0]["message"]} instead")

        response = self.client.get("/control/get_health_data", params={"guid":"humbug bogus"})

        response_data = response.json()

        self.assertNotEqual(response.status_code, 200, f"Should have failed but got status {response.status_code}")
        self.assertEqual(response_data["status"], "No entries for asset was found", f"Found something instead of nothing.")

    def get_health_data():

        health_data = {"service": "Hpc api Service",
                            "timestamp": "2001-02-03 12:55:25,813",
                            "severity_level": "WARNING",
                            "message": "Yo this is a test health entry",
                            "guid": "test_control_api",
                            "exception": None,
                            "flag": None,
                            "sent": "No"}

        return health_data

    def get_metadata_data():

        metadata_data = {"asset_created_by": "",
                            "asset_deleted_by": "",
                            "asset_guid": "test_control_api",
                            "asset_pid": "",
                            "asset_subject": "specimen",
                            "asset_updated_by": "",
                            "audited": False,
                            "audited_by": "",
                            "audited_date": None,
                            "barcode": [
                                "spoof_code"
                            ],
                            "collection": "Honey jar",
                            "date_asset_created": None,
                            "date_asset_deleted": None,
                            "date_asset_finalised": None,
                            "date_asset_taken": "2000-09-26T09:30:28+02:00",
                            "date_asset_updated": None,
                            "date_metadata_created": "2001-09-27T08:29:49+02:00",
                            "date_metadata_updated": "",
                            "date_metadata_uploaded": "",
                            "digitiser": "Billy the kid",
                            "external_publisher": [],
                            "file_format": "jpeg",
                            "funding": "Easter bunny",
                            "institution": "NHMA",
                            "metadata_created_by": "IngestionClient",
                            "metadata_updated_by": "",
                            "metadata_uploaded_by": "",
                            "multispecimen": False,
                            "parent_guid": None,
                            "payload_type": "master image",
                            "pipeline_name": "PIPEPIOF0001",
                            "preparation_type": "pinned",
                            "pushed_to_specify_date": None,
                            "restricted_access": [],
                            "specimen_pid": "",
                            "status": "MAJOR_FLOODING",
                            "tags": {
                                "metadataTemplate": "v2_1_0",
                            },
                            "workstation_name": "WORKPIOF0001"}

        return metadata_data

    def get_track_data():

        track_data = {"created_timestamp": "2001-11-11T09:09:09.999999",
                            "pipeline": "PIPEPIOF0001",
                            "batch_list_name": "",
                            "job_list": [
                                {
                                    "name": "uploader",
                                    "status": "DONE",
                                    "priority": 1,
                                    "job_queued_time": "2024-11-08T13:07:29",
                                    "job_start_time": "2024-11-08T13:07:29",
                                    "hpc_job_id": "222222"
                                },
                                {
                                    "name": "clean_up",
                                    "status": "DONE",
                                    "priority": 2,
                                    "job_queued_time": "2024-11-08T13:10:17",
                                    "job_start_time": "2024-11-08T13:10:18",
                                    "hpc_job_id": "111111"
                                }
                            ],
                            "jobs_status": "DONE",
                            "file_list": [
                                {
                                    "name": "test_control_api.jpeg",
                                    "type": "jpeg",
                                    "time_added": "2024-11-05T10:43:36.890847",
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
                            "available_for_services_wait_time": None}
        
        return track_data

if __name__ == "__main__":
    unittest.main()
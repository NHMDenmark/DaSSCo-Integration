import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)


from IntegrationServer.MongoDB.mongo_connection import MongoConnection
from IntegrationServer.Enums.status_enum import StatusEnum

class TestMongoConnection(unittest.TestCase):
    
    # Maybe change to different test dbs(?)
    @classmethod
    def setUpClass(self):
        self.track = MongoConnection("track")
        self.metadata = MongoConnection("metadata")
        self.batch = MongoConnection("batch")

        self.bogus = "bogus"
        self.guid = "test_mongo"
        self.pipeline = "EXAMPLE"
        self.job = "test"
        self.batch_list = "testy_listy"

        self.file_for_filelist = {"name": "crazy_frog.png", "type": "png", "time_added": "2002-02-22T10:59:09.870+00:00",
                                   "check_sum": 3247235, "file_size": 100, "ars_link": "fake/link", "erda_sync": False, "deleted":False}



        self.track.create_track_entry(self.guid, self.pipeline)
        
    @classmethod
    def tearDownClass(self):
        
        self.track.delete_entry(self.guid)
        self.metadata.delete_entry(self.guid)
        self.batch.delete_entry(self.batch_list)

        self.batch.close_mdb()
        self.track.close_mdb()
        self.metadata.close_mdb()

    def test_create_track_entry(self):
        
        created = self.track.create_track_entry(self.guid, self.pipeline)
        
        self.assertEqual(created, False, f"Track entry should already have been created. A new entry was created with guid {self.guid}")

    def test_delete_entry(self):

        deleted = self.track.delete_entry(self.guid)

        self.assertEqual(deleted, True, f"Failed to delete the entry with guid {self.guid}")

        self.track.create_track_entry(self.guid, self.pipeline)

    def test_get_entry(self):

        entry = self.track.get_entry("_id", self.guid)

        self.assertIsNotNone(entry, f"Failed to get the entry with guid {self.guid}")

        self.assertEqual(entry["asset_size"], -1, f"Failed to get the default value of -1 for the asset_size field, instead got {entry["asset_size"]}")

    def test_get_entry_from_multiple_key_pairs(self):

        key_value = [{"asset_size": -1, "has_open_share": "NO"}]

        entry = self.track.get_entry_from_multiple_key_pairs(key_value)

        self.assertIsNotNone(entry, f"Failed to get the entry with key/values: {key_value}")

        self.assertEqual(entry["hpc_ready"], "NO", f"Failed to get the default value of NO for the entry with key/values: {key_value}")

    def test_create_metadata_entry(self):

        path = f"{project_root}/Tests/TestConfigFiles/test_metadata_entry2.json"

        created = self.metadata.create_metadata_entry(path, self.guid)

        self.assertEqual(created, True, f"Failed to create metadata entry with guid {self.guid}")

    def test_update_entry(self):

        key = "digitiser" 
        value = "Emperor Palpatine"

        updated = self.metadata.update_entry(self.guid, key, value)

        self.assertEqual(updated, True, f"Failed to update metadata entry with guid {self.guid} and key {key} and value {value}")

        updated = self.metadata.update_entry(self.bogus, key, value)

        self.assertEqual(updated, False, f"Should have failed to update metadata entry with guid {self.bogus} and key {key} and value {value}")

    def test_update_track_job_status(self):

        updated = self.track.update_track_job_status(self.guid, self.job, StatusEnum.RUNNING.value)

        self.assertEqual(updated, True, f"Failed to update job status for guid {self.guid}")

        updated = self.track.update_track_job_status(self.guid, self.bogus, StatusEnum.RUNNING.value)

        self.assertEqual(updated, False, f"Updated job status for job: {self.bogus}")

        updated = self.track.update_track_job_status(self.bogus, self.job, StatusEnum.RUNNING.value)

        self.assertEqual(updated, False, f"Updated job status for entry with guid: {self.bogus}")
    
    def test_update_track_job_list(self):

        updated = self.track.update_track_job_list(self.guid, self.job, "priority", 9)

        self.assertEqual(updated, True, f"Failed to update job for guid {self.guid}")

        updated = self.track.update_track_job_list(self.guid, self.bogus, "priority", 8)

        self.assertEqual(updated, False, f"Updated job status for job: {self.bogus}")

        updated = self.track.update_track_job_list(self.bogus, self.job, "priority", 7)

        self.assertEqual(updated, False, f"Updated job status for entry with guid: {self.bogus}")

    def test_update_track_file_list(self):

        updated = self.track.update_track_file_list(self.guid, "self.job", "deleted", True)

        self.assertEqual(updated, False, f"Updated file for entry with guid: {self.guid}")

        updated = self.track.update_track_file_list(self.bogus, "self.job", "deleted", True)

        self.assertEqual(updated, False, f"Updated file for entry with guid: {self.bogus}")

    def test_get_value_for_key(self):
        
        key = "digitiser" 
        insert = "Emperor Palpatine"

        self.metadata.update_entry(self.guid, key, insert)

        value = self.metadata.get_value_for_key(self.guid, "digitiser")

        self.assertEqual(value, insert, f"Failed to find {insert} as digitiser for guid: {self.guid}. Found {value} instead.")

        value = self.metadata.get_value_for_key(self.bogus, "digitiser")

        self.assertIsNone(value, f"Failed to return none for the guid: {self.bogus}")

    def test_add_entry_to_list(self):

        created = self.batch.add_entry_to_list(self.guid, self.batch_list)

        self.assertTrue(created, f"Failed to create new list for guid: {self.guid}")

        updated = self.batch.add_entry_to_list(self.bogus, self.batch_list)

        self.assertTrue(updated, f"Failed to update {self.batch_list} with guid: {self.guid}" )

        list = self.batch.get_entry("_id", self.batch_list)

        self.assertEqual(len(list), 2, f"Failed to confirm 2 entries in the list: {self.batch_list}")

    def test_append_existing_list(self):
        
        appended = self.track.append_existing_list(self.guid, "file_list", self.file_for_filelist)

        self.assertTrue(appended, f"Failed to append {self.file_for_filelist} to track entry with guid: {self.guid}")

        appended = self.track.append_existing_list(self.guid, self.bogus, self.file_for_filelist)

        self.assertFalse(appended, f"Append {self.file_for_filelist} to the list {self.bogus} for track entry with guid: {self.guid}")

if __name__ == "__main__":
    unittest.main()
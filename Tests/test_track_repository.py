import unittest
from unittest.mock import MagicMock, patch
import os
import sys
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from IntegrationServer.MongoDB.track_repository import TrackRepository

class TestTrackRepository(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        # Mock the MongoDB collection
        self.track = TrackRepository()
        self.track.collection = MagicMock()
        self.guid = "test_guid"
        self.pipeline = "TEST_PIPELINE"
        self.job = "test_job"
        self.asset_type = "UNKNOWN"
        self.error_entry = {
            "_id": "error_test",
            "jobs_status": "ERROR",
            "files_status": "WAITING",
        }
        self.paused_entry = {
            "_id": "paused_test",
            "jobs_status": "PAUSED",
            "files_status": "WAITING",
        }
        self.track_entry = {
            "_id": self.guid,
            "pipeline": self.pipeline,
            "job_list": [{"name": self.job, "status": "WAITING"}],
        }
        self.guidTwo = "test_mongo"
        self.pipelineTwo = "EXAMPLE"
        self.track.create_track_entry(self.guidTwo, self.pipelineTwo)
    
    @classmethod
    def tearDownClass(self):
        self.track.delete_entry(self.guidTwo)
        self.track.close_connection()

    def test_error_get_entry(self):
        # Mock find_one to return an entry with an error
        self.track.collection.find_one.return_value = self.error_entry
        result = self.track.error_get_entry()
        self.assertEqual(result, self.error_entry)
        self.track.collection.find_one.assert_called_once()

    def test_get_error_entries(self):
        # Mock find to return a list of entries with errors
        self.track.collection.find.return_value = [self.error_entry]
        result = self.track.get_error_entries()
        self.assertEqual(result, [self.error_entry])
        self.track.collection.find.assert_called_once()

    def test_update_track_job_status_success(self):
        # Mock get_entry to return an entry with the job_list
        self.track.get_entry = MagicMock(return_value=self.track_entry)

        result = self.track.update_track_job_status(self.guid, self.job, "IN_PROGRESS")
        self.assertTrue(result)
        self.track.collection.update_one.assert_called_once_with(
            {"_id": self.guid, "job_list.name": self.job},
            {"$set": {"job_list.$.status": "IN_PROGRESS"}}
        )

    def test_update_track_job_status_failure_entry_not_found(self):
        # Simulate no entry found
        self.track.get_entry = MagicMock(return_value=None)

        result = self.track.update_track_job_status(self.guid, self.job, "IN_PROGRESS")
        self.assertFalse(result)
        self.track.collection.update_one.assert_not_called()

    def test_update_track_job_status_failure_job_not_found(self):
        # Simulate entry without the specified job in job_list
        self.track.get_entry = MagicMock(return_value={"_id": self.guid, "job_list": []})

        result = self.track.update_track_job_status(self.guid, self.job, "IN_PROGRESS")
        self.assertFalse(result)
        self.track.collection.update_one.assert_not_called()

if __name__ == "__main__":
    unittest.main()
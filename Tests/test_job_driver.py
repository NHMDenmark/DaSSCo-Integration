import unittest
import os
import sys
import shutil

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from AssetFileHandler.asset_handler import JobDriver
from IntegrationServer.MongoDB import track_repository, metadata_repository

class TestJobDriver(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        
        self.track = track_repository.TrackRepository()
        self.metadata = metadata_repository.MetadataRepository()
        self.driver = JobDriver()

        self.guid = "test_metadata_entry3"

        self.driver.input_dir = project_root + "/Tests/TestConfigFiles/test_new_files"
        self.driver.error_path = project_root + "/Tests/TestConfigFiles/test_error"
        self.driver.in_process_dir = project_root + "/Tests/TestConfigFiles/test_in_process"

        self.destination_path = project_root + "/Tests/TestConfigFiles/test_in_process/EXAMPLE/2000-12-24/test_metadata_entry3"

    @classmethod
    def tearDownClass(self):
        self.track.delete_entry(self.guid)
        self.metadata.delete_entry(self.guid)

        self.track.close_connection()
        self.metadata.close_connection()

        shutil.move(self.destination_path, self.driver.input_dir)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_process_new_directories_from_ndrive(self):

        self.driver.process_new_directories_from_ndrive()

        track_entry = self.track.get_entry("_id", self.guid)

        metadata_entry = self.metadata.get_entry("_id", self.guid)

        self.assertEqual(track_entry["pipeline"], metadata_entry["pipeline_name"], 
                         f"Failed to get entries with matching pipeline fields from track and metdata collections. Track: {track_entry["pipeline"]}, Metadata: {metadata_entry["pipeline_name"]}")

        json_path = self.destination_path + "/" + self.guid + ".json"

        json_file = open(json_path, "r")

        self.assertIsNotNone(json_file, f"Failed to find json file in {json_path}")

        json_file.close()


if __name__ == "__main__":
    unittest.main()
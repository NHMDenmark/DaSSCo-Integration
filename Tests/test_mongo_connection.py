import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)


from IntegrationServer.MongoDB.mongo_connection import MongoConnection

class TestMongoConnection(unittest.TestCase):
    
    # Maybe change to different test dbs(?)
    @classmethod
    def setUpClass(self):
        self.track = MongoConnection("track")
        self.metadata = MongoConnection("metadata")

        self.guid = "test_mongo"
        self.pipeline = "EXAMPLE"

        self.track.create_track_entry(self.guid, self.pipeline)
        
    @classmethod
    def tearDownClass(self):
        
        self.track.delete_entry(self.guid)
        self.metadata.delete_entry(self.guid)

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

        path = "Tests/TestConfigFiles/test_metadata_entry2.json"

        created = self.metadata.create_metadata_entry(path, self.guid)

        self.assertEqual(created, True, f"Failed to create metadata entry with guid {self.guid}")


if __name__ == "__main__":
    unittest.main()
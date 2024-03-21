import unittest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)


from IntegrationServer.MongoDB.mongo_connection import MongoConnection

class TestMongoConnection(unittest.TestCase):
    
    # Maybe change to test dbs(?)
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

        self.track.close_mdb()
        self.metadata.close_mdb()

    def test_create_track_entry(self):
        
        created = self.track.create_track_entry(self.guid, self.pipeline)
        
        self.assertEqual(created, False, f"Track entry should already have been created. A new entry was created with guid {self.guid}")

    def test_delete_entry(self):

        deleted = self.track.delete_entry(self.guid)

        self.assertEqual(deleted, True, f"Failed to delete the entry with guid {self.guid}")

        self.track.create_track_entry(self.guid, self.pipeline)


if __name__ == "__main__":
    unittest.main()
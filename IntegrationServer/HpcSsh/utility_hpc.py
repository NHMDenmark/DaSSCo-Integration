import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB.mongo_connection import MongoSharedClient
from MongoDB import track_repository

class UtilityHPC:
    def __init__(self, mongo_client: MongoSharedClient):
        self.mongo_track = track_repository.TrackRepository(mongo_client) 

    """ determines if asset loading can run based on a maximum limit of assets being uploaded or downloaded at the same time."""
    def can_start_load_job(self, max_assets: int) -> bool:
        # Check the current number of running assets
        current_running_assets = self.get_current_running_assets()
        
        # If the current running assets are less than the max allowed, we can run
        return current_running_assets < max_assets

    def can_start_download_job(self, max_assets: int) -> bool:
        # Check the current number of downloading assets
        current_downloading_assets = self.get_downloading_assets()
        
        # If the current downloading assets are less than the max allowed, we can run
        #print(f"Current downloading assets: {current_downloading_assets}, Max allowed: {max_assets}")
        return current_downloading_assets < max_assets
    
    def can_start_upload_job(self, max_assets: int) -> bool:
        # Check the current number of uploading assets
        current_uploading_assets = self.get_uploading_assets()
        
        # If the current uploading assets are less than the max allowed, we can run
        #print(f"Current uploading assets: {current_uploading_assets}, Max allowed: {max_assets}")
        return current_uploading_assets < max_assets

    def get_all_loading_assets(self):
        # Query the database to get the count of loading and uploading assets
        asset_count = self.mongo_track.count_assets_in_hpc_load_state()

        return asset_count
    
    def get_downloading_assets(self):
        # Query the database to get the count of downloading assets
        downloading_count = self.mongo_track.count_assets_in_download_state()

        return downloading_count
    
    def get_uploading_assets(self):
        # Query the database to get the count of uploading assets
        uploading_count = self.mongo_track.count_assets_in_upload_state()

        return uploading_count
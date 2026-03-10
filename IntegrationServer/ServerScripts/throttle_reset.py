import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB.mongo_connection import MongoSharedClient
from MongoDB import throttle_repository
import utility

class ResetThrottleService:
    """
    Resets all throttle values to 0 in the throttle database.
    """
    def __init__(self):
        self.mongo_client = MongoSharedClient()
        self.throttle_repo = throttle_repository.ThrottleRepository(self.mongo_client)
        self.util = utility.Utility()
        self.throttle_config_path = f"{project_root}/ConfigFiles/throttle_config.json"
        self.throttle_config = self.util.read_json(self.throttle_config_path)
        
        try:
            for config in self.throttle_config:
                self.throttle_repo.update_entry(config, "value", 0)
            print("Successfully reset throttle db.")  
        except Exception as e:
            print("Failed to reset throttle documents.", e)

        self.throttle_repo.close_connection()

if __name__ == "__main__":        
    try:
        ResetThrottleService()
    except Exception as e:
        print("Failed to reset throttle service.", e)
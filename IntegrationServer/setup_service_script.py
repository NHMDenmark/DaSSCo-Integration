import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB import service_repository, throttle_repository
import utility

"""
This script is part of the integration server configuration. Should be run independently before any other scripts or as part of a shell script.
Install the mongo database before running this script.  
Creates the micro services in the database for controlling their run status. 
Micro services added to the /ConfigFiles/micro_service_config.json will be created.
Insert documents based on the throttle config file /ConfigFiles/throttle_config.json to the throttle database. 
"""
class SetupServices:

    def __init__(self):
        self.service_repo = service_repository.ServiceRepository()
        self.util = utility.Utility()
        self.service_config_path = f"{project_root}/IntegrationServer/ConfigFiles/micro_service_config.json"
        self.service_config = self.util.read_json(self.service_config_path)
        self.service_names = list(self.service_config.keys())

        for name in self.service_names:
            
            created = self.service_repo.create_micro_service_entry(name)
            if created is False:
                print(f"Failed to create service {name}, in mongo micro service collection.")
                exist = self.service_repo.get_entry("_id", name)
                if exist is None:
                    print(f"Failed to find {name}, in mongo db.")
                else:
                    print(f"{name} has already been created in the mongo db.")
            else:
                print(f"{name} was created successfully.")


        self.service_repo.close_connection()

class SetupThrottleService:

    def __init__(self):
        self.throttle_repo = throttle_repository.ThrottleRepository()
        self.util = utility.Utility()
        self.throttle_config_path = f"{project_root}/IntegrationServer/ConfigFiles/throttle_config.json"
        self.throttle_config = self.util.read_json(self.throttle_config_path)
        self.throttle_configs = list(self.throttle_config.keys())

        try:
            for config in self.throttle_configs:
                if self.throttle_repo.get_entry("_id", config) is None:
                    self.throttle_repo.insert_default_value(config)
                    print(f"Inserted document: _id: {config}, value: 0 - in throttle database")
        except Exception as e:
            print("Failed to insert throttle documents to throttle database.", e)

        self.throttle_repo.close_connection()

if __name__ == "__main__":
        
    try:
        SetupServices()
        SetupThrottleService()
    except Exception as e:
        print(f"An error occurred: {e}")
    
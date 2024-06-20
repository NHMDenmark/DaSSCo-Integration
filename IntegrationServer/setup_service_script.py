import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from MongoDB import service_repository
import utility

"""
This script is part of the integration server configuration. Should be run independently before any other scripts or as part of a shell script. 
Creates the micro services in the database for controlling their run status. 
Micro services added to the /ConfigFiles/run_config.json will be created.
"""
class SetupServiceScript:

    def __init__(self):
        self.service_repo = service_repository.ServiceRepository()
        self.util = utility.Utility()
        self.service_config_path = f"{project_root}/IntegrationServer/ConfigFiles/run_config.json"
        self.service_config = self.util.read_json(self.service_config_path)
        self.service_names = list(self.service_config.keys())

        for name in self.service_names:
            print(name)

        for name in self.service_names:
            
            created = self.service_repo.create_micro_service_entry(name)
            if created is False:
                print(f"Failed to create service {name}, in mongo micro service collection.")

        self.service_repo.close_connection()

if __name__ == "__main__":
        
    try:
        SetupServiceScript()
    except Exception as e:
        print(f"An error occurred: {e}")
    
import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from HealthUtility import health_caller, run_utility
from MongoDB import track_repository, service_repository


class ControlService():

    def __init__(self):
        self.util = utility.Utility()
    
        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)

        # service name for logging/info purposes
        self.service_name = "Control service api"
        self.prefix_id= "Csa"

        self.control_service_config_path = f"{project_root}/ConfigFiles/control_api_scripts_config.json"

        self.mongo_service = service_repository.ServiceRepository()
        self.mongo_track = track_repository.TrackRepository()

        self.health_caller = health_caller.HealthCaller()
        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)
    

    def all_run(self):

        all_status = self.mongo_service.get_value_for_key("all_run", "run_status")

        if all_status == "RUNNING":
            return True, True

        all_run_path = self.util.get_value(self.control_service_config_path, "all_run")
        
        update = self.mongo_service.update_entry("all_run", "run_status", "RUNNING")

        if update is False:
            return update, False

        running = self.util.run_shell_script(all_run_path)

        return running, False
    
    def stop_all(self):

        stopped = self.mongo_service.update_entry("all_run", "run_status", "STOPPED")
        
        return stopped

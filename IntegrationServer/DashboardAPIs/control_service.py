import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from Enums import status_enum, validate_enum
from HealthUtility import health_caller, run_utility
from MongoDB import track_repository, service_repository
from DashboardAPIs import micro_service_paths

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
        self.micro_paths = micro_service_paths.MicroServicePaths()
        self.validate_enum = validate_enum.ValidateEnum
        self.status_enum = status_enum.StatusEnum

        self.health_caller = health_caller.HealthCaller()
        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)
    

    def all_run(self):

        all_status = self.mongo_service.get_value_for_key("all_run", "run_status")

        if all_status == self.status_enum.RUNNING.value:
            return True, True

        all_run_path = self.util.get_value(self.control_service_config_path, "all_run")
        
        update = self.mongo_service.update_entry("all_run", "run_status", self.status_enum.RUNNING.value)

        if update is False:
            return update, False

        running = self.util.run_shell_script(all_run_path)

        return running, False
    
    def stop_all(self):

        stopped = self.mongo_service.update_entry("all_run", "run_status", self.status_enum.STOPPED.value)
        
        return stopped
    
    def stop_service(self, service_name):

        stopped = self.mongo_service.update_entry(service_name, "run_status", self.status_enum.STOPPED.value)

        return stopped
    
    def start_service(self, service_name):

        start_service_path = self.util.get_value(self.control_service_config_path, "start_service")

        service_path = self.micro_paths.get_path_from_name(service_name)

        if service_path is False:
            return False

        # TODO check all_run status to determine if service can run

        # update database status
        updated = self.mongo_service.update_entry(service_name, "run_status", self.status_enum.RUNNING.value)

        if updated is False:
            return False

        started = self.util.run_shell_script(start_service_path, arguments = [service_path])

        return started

    def get_track_asset_data(self, guid):

        try:
            asset = self.mongo_track.get_entry("_id", guid)

            if asset is None:
                return False, "Asset does not exist"
            else:
                return True, asset
            
        except Exception as e:
            print(f"get track asset data: {e}")
            return False, "Things went wrong"
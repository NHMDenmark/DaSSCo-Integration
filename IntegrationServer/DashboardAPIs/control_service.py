import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
from Enums import status_enum, validate_enum
from HealthUtility import health_caller, run_utility
from MongoDB import track_repository, service_repository, health_repository, metadata_repository, throttle_repository
from DashboardAPIs import micro_service_paths
import json
from datetime import datetime

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
        self.mongo_health = health_repository.HealthRepository()
        self.mongo_metadata = metadata_repository.MetadataRepository()
        self.mongo_throttle = throttle_repository.ThrottleRepository()

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
        
    def get_metadata_asset_data(self, guid):

        try:
            asset = self.mongo_metadata.get_entry("_id", guid)

            if asset is None:
                return False, "Asset does not exist"
            else:                
                return True, asset
            
        except Exception as e:
            print(f"get metadata asset data: {e}")
            return False, "Things went wrong"
        
    def get_health_asset_data(self, guid):

        try:
            entries = self.mongo_health.get_entries("guid", guid)

            if entries is None or entries == []:
                return False, "No entries for asset was found"
            else:                
                return True, entries
            
        except Exception as e:
            print(f"get health asset data: {e}")
            return False, "Things went wrong"
        
    def get_throttle_data(self):

        try:
            entries = self.mongo_throttle.get_all_entries()

            if entries is None or entries == []:
                return False, "No entries found"
            else:                
                return True, entries
            
        except Exception as e:
            print(f"get throttle data: {e}")
            return False, "Things went wrong"
    
    def get_list_of_guids_with_error_flag(self):

        entries = self.mongo_track.get_error_entries()

        if not entries:  # Check if entries is None or empty list
            return False, "No entries found"
        else:                
            error_counts = {}
            error_guids = {}

            for entry in entries:
                guid = entry["_id"]

                for key, value in entry.items():
                    if value == "ERROR":
                        # Count occurrences of each error type
                        error_counts[key] = error_counts.get(key, 0) + 1
                        
                        # Store GUIDs where the error occurs
                        if key not in error_guids:
                            error_guids[key] = []
                        error_guids[key].append(guid)

            # Format output as required
            response = {
                "error_counts": [
                    error_counts,  # First object: error type counts
                    {key + "_guids": guids for key, guids in error_guids.items()}  # Second object: error GUIDs
                ]
            }

            return True, response

    def get_list_of_guids_with_critical_error_flag(self):

        entries = self.mongo_track.get_critical_error_entries()

        if not entries:  # Check if entries is None or empty list
            return False, "No entries found"
        else:                
            error_counts = {}
            error_guids = {}

            for entry in entries:
                guid = entry["_id"]

                for key, value in entry.items():
                    if value == "CRITICAL_ERROR":
                        # Count occurrences of each error type
                        error_counts[key] = error_counts.get(key, 0) + 1
                        
                        # Store GUIDs where the error occurs
                        if key not in error_guids:
                            error_guids[key] = []
                        error_guids[key].append(guid)

            # Format output as required
            response = {
                "critical_error_counts": [
                    error_counts,  # First object: error type counts
                    {key + "_guids": guids for key, guids in error_guids.items()}  # Second object: error GUIDs
                ]
            }

            return True, response
    
    def search_metadata_db(self, criteria):

        try:
            
            if criteria.time_key is not None:

                if criteria.after is not None:

                    criteria.after = datetime.strptime(criteria.after, '%Y-%m-%d')
                
                if criteria.before is not None:

                    criteria.before = datetime.strptime(criteria.before, '%Y-%m-%d')

                if criteria.after is None and criteria.before is None:

                    return True, None, "Missing date - example: 2024-03-30"

            data_list = self.mongo_metadata.get_time_based_multiple_key_list(criteria.key_values, criteria.time_key, criteria.after, criteria.before)

            if data_list == []:
                return True, data_list, None
            
            guid_list = []
            count = 0
            for entry in data_list:
                count += 1
                guid_list.append(entry["_id"])

            return_value = {"count":count, "guids":guid_list}

            return True, return_value, None
        
        except Exception as e:
            print(e)
            return False, None, ("Something went wrong while searching for metadata.")
        
    def search_track_db(self, criteria):

        try:
            
            if criteria.time_key is not None:

                if criteria.after is not None:

                    criteria.after = datetime.strptime(criteria.after, '%Y-%m-%d')
                
                if criteria.before is not None:

                    criteria.before = datetime.strptime(criteria.before, '%Y-%m-%d')

                if criteria.after is None and criteria.before is None:

                    return True, None, "Missing date - example: 2024-03-30"

            data_list = self.mongo_track.get_time_based_multiple_key_list(criteria.key_values, criteria.time_key, criteria.after, criteria.before)

            if data_list == []:
                return True, data_list, None
            
            guid_list = []
            count = 0
            for entry in data_list:
                count += 1
                guid_list.append(entry["_id"])

            return_value = {"count":count, "guids":guid_list}

            return True, return_value, None
        
        except Exception as e:
            print(e)
            return False, None, ("Something went wrong while searching for track data.")
        
    def search_health_db(self, criteria):

        try:
                
            if criteria.time_key is not None:
                    
                if criteria.after is not None:

                    criteria.after = datetime.strptime(criteria.after, '%Y-%m-%d')
                    
                if criteria.before is not None:

                    criteria.before = datetime.strptime(criteria.before, '%Y-%m-%d')

                if criteria.after is None and criteria.before is None:

                    return True, None, "Missing date - example: 2024-03-30"

            data_list = self.mongo_health.get_time_based_multiple_key_list(criteria.key_values, criteria.time_key, criteria.after, criteria.before)

            if data_list == []:
                return True, data_list, None
                
            id_list = []
            count = 0
            for entry in data_list:
                count += 1
                id_list.append(entry["_id"])

            return_value = {"count":count, "id_list":id_list}

            return True, return_value, None
            
        except Exception as e:
            print(e)
            return False, None, ("Something went wrong while searching for health data.")

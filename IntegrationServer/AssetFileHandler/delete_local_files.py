import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
import utility
from MongoDB import track_repository
from MongoDB.mongo_connection import MongoSharedClient
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum, flag_enum

"""
Service for deleting files that have been moved to the integration server as part of the pipeline. Files are first deleted after success for sync erda and job proccessing has happened. 
"""
class DeleteLocalFiles():

    def __init__(self):
        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        # service name for logging/info purposes
        self.service_name = "Delete local files"
        self.prefix_id= "Dlf"

        self.util = utility.Utility()
        
        self.mongo_client = MongoSharedClient()
        self.track_mongo = track_repository.TrackRepository(self.mongo_client)
        
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.flag_enum = flag_enum.FlagEnum
        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name, self.pid, self.mongo_client)
        
        self.run_util.service_starting_updates()
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.run = self.run_util.get_service_run_status()
        
        try:
            self.loop()
        except Exception as e:
            print("service crashed", e)
            try:
                entry = self.run_util.log_exc(self.prefix_id, f"{self.service_name} crashed.", e, self.status_enum.CRITICAL_ERROR.value)
                self.health_caller.unexpected_error(self.service_name, entry)
            except:
                print(f"failed to inform about crash")
            self.run_util.service_stopping_updates()
            self.close_all_connections()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{self.flag_enum.JOBS_STATUS.value: self.status_enum.DONE.value, self.flag_enum.IS_IN_ARS.value: self.validate_enum.YES.value,
                                                                            self.flag_enum.HAS_NEW_FILE.value: self.validate_enum.NO.value, self.flag_enum.ERDA_SYNC.value: self.validate_enum.YES.value,
                                                                              self.flag_enum.TEMPORARY_FILES_LOCAL.value:self.validate_enum.YES.value}])

            if asset is None:
                #print(f"No asset found")
                time.sleep(10)

            if asset is not None:
                guid = asset["_id"]
                try:
                    local_path = asset["temporary_path_local"]
                except Exception as e:
                    print(f"no path found {guid}: {e}")
                    entry = self.run_util.log_msg(self.prefix_id, f"No temporary_path_local found for asset {guid}.", self.status_enum.ERROR.value)
                    self.health_caller.error(self.service_name, entry, guid, self.flag_enum.TEMPORARY_FILES_LOCAL.value, self.status_enum.ERROR.value)
                    self.track_mongo.update_entry(guid, self.flag_enum.TEMPORARY_FILES_LOCAL.value, self.status_enum.ERROR.value)
                    continue
                
                try:
                    # Check if it's a directory
                    if os.path.isdir(local_path):
                        # Look for any file in the directory that starts with the GUID
                        files_to_delete = [f for f in os.listdir(local_path) if f.startswith(f"{guid}.")]

                        # Delete the files
                        if files_to_delete:
                            for file in files_to_delete:
                                file_path = os.path.join(local_path, file)
                                os.remove(file_path)
                            print(f"Deleted files: {guid}")
                            # update track
                            self.track_mongo.delete_field(guid, "temporary_path_local")
                            self.track_mongo.delete_field(guid, self.flag_enum.TEMPORARY_FILES_LOCAL.value)                        
                        else:
                            print(f"No matching files found for {guid}. Temporary_files_local set to ERROR")
                            entry = self.run_util.log_msg(self.prefix_id, f"No matching files found for {guid}. Temporary_files_local set to ERROR.", self.status_enum.ERROR.value)
                            self.health_caller.error(self.service_name, entry, guid, self.flag_enum.TEMPORARY_FILES_LOCAL.value, self.status_enum.ERROR.value)
                            self.track_mongo.update_entry(guid, self.flag_enum.TEMPORARY_FILES_LOCAL.value, self.status_enum.ERROR.value)

                        # delete empty directories
                        if not os.listdir(local_path):
                            os.rmdir(local_path)
                            print(f"Deleted empty directory: {local_path}")

                    else:
                        print(f"{local_path} is not a directory.")
                        entry = self.run_util.log_msg(self.prefix_id, f"{local_path} is not a directory. {guid}", self.status_enum.ERROR.value)
                        self.health_caller.error(self.service_name, entry, guid, self.flag_enum.TEMPORARY_FILES_LOCAL.value, self.status_enum.ERROR.value)
                        self.track_mongo.update_entry(guid, self.flag_enum.TEMPORARY_FILES_LOCAL.value, self.status_enum.ERROR.value)

                except Exception as e:
                    print(f"An error occurred for {guid}: {e}")
                    entry = self.run_util.log_msg(self.prefix_id, f"An error occurred for {guid}: {e}", self.status_enum.ERROR.value)
                    self.health_caller.error(self.service_name, entry, guid, self.flag_enum.TEMPORARY_FILES_LOCAL.value, self.status_enum.ERROR.value)
                    self.track_mongo.update_entry(guid, self.flag_enum.TEMPORARY_FILES_LOCAL.value, self.status_enum.ERROR.value)
                        
            
            # checks if service should keep running           
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.status_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()

        # out of main loop
        self.run_util.service_stopping_updates()
        self.close_all_connections()
        print("Service closed down")

    def close_all_connections(self):
        self.mongo_client.close()

if __name__ == '__main__':
    DeleteLocalFiles()
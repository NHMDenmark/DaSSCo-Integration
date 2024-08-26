import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
import utility
from MongoDB import service_repository, track_repository
from HealthUtility import health_caller, run_utility
from Enums import status_enum, validate_enum

# TODO untested
class DeleteLocalFiles():

    def __init__(self):
        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        
        # service name for logging/info purposes
        self.service_name = "Delete local files"
        self.prefix_id= "Dlf"

        self.util = utility.Utility()
        
        self.service_mongo = service_repository.ServiceRepository()
        self.track_mongo = track_repository.TrackRepository()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name)

        # set the service db value to RUNNING, mostly for ease of testing
        self.service_mongo.update_entry(self.service_name, "run_status", self.status_enum.RUNNING.value)
        
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.run = self.run_util.get_service_run_status()
        self.loop()

    def loop(self):

        while self.run == self.status_enum.RUNNING.value:
            
            asset = self.track_mongo.get_entry_from_multiple_key_pairs([{"jobs_status": self.status_enum.DONE.value, "is_in_ars": self.validate_enum.YES.value,
                                                                            "has_new_file": self.validate_enum.NO.value, "erda_sync": self.validate_enum.YES.value,
                                                                              "temporary_files_local":self.validate_enum.YES.value}])

            if asset is None:
                print(f"No asset found")
                time.sleep(10)

            if asset is not None:
                guid = asset["_id"]
                try:
                    local_path = asset["temporary_path_local"]
                except Exception as e:
                    print(f"no path found {guid}: {e}")
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
                            self.track_mongo.delete_field(guid, "temporary_files_local")                        
                        else:
                            print(f"No matching files found for {guid}. Temporary_files_local set to ERROR")
                            self.track_mongo.update_entry(guid, "temporary_files_local", self.validate_enum.ERROR.value)

                        # delete empty directories
                        if not os.listdir(local_path):
                            os.rmdir(local_path)
                            print(f"Deleted empty directory: {local_path}")

                    else:
                        print(f"{local_path} is not a directory.")

                except Exception as e:
                    print(f"An error occurred for {guid}: {e}")
                        
            
            # checks if service should keep running           
            self.run = self.run_util.check_run_changes()

            # Pause loop
            if self.run == self.status_enum.PAUSED.value:
                self.run = self.run_util.pause_loop()

        # out of main loop
        self.service_mongo.close_connection()
        self.track_mongo.close_connection()
        print("Service closed down")


if __name__ == '__main__':
    DeleteLocalFiles()
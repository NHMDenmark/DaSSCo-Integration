import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import utility
import time
from MongoDB import service_repository, health_repository
from HealthUtility import run_utility

# TODO on hold for now, i think it might be useful later on but not for the immediate error/warning handling.
class IssueDetector():

    def __init__(self):
        
        self.service_name = "Issue detector"
        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)

        self.service_config_path = f"{project_root}/ConfigFiles/"

        self.util = utility.Utility()
        self.service_mongo = service_repository.ServiceRepository()
        self.health_mongo = health_repository.HealthRepository()
        self.run_util = run_utility.RunUtility(self.service_name, self.log_filename, self.logger_name )

        
        self.service_mongo.update_entry("all_run", "run_status", "RUNNING")
        self.run_util.log_all_run_status_change("initial", "RUNNING")
        self.run = self.run_util.get_all_run()
        self.loop()

    def loop(self):

        while self.run == self.run_util.RUNNING:
            
            self.service_mongo.update_entry("all_run", "run_status", "STOPPED")
            self.run_util.check_run_changes()
            self.run = self.run_util.get_all_run()

if __name__ == '__main__':
    IssueDetector()
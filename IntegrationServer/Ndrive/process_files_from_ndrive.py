import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from JobList import job_driver
import utility
import time

"""
Class responsible for initiating the processing of new files from the ndrive. Specifically this means we have
both a json and an img file of some kind. Calls the JobDriver class for actual processing. 
"""

# TODO needs to decide if a timer or trigger system is needed here.


class ProcessNewFiles:

    def __init__(self):

        self.jobby = job_driver.JobDriver()
        self.util = utility.Utility()

        self.new_files_path = f"{project_root}/Files/NewFiles"
        self.updated_files_path = f"{project_root}/Files/UpdatedFiles"
        
        self.run = True
        self.count = 3

        self.loop()

    def loop(self):

        while self.run:

            self.jobby.process_new_directories_from_ndrive()

            time.sleep(10)

            # checks if service should keep running - configurable in ConfigFiles/run_config.json
            run_config_path = f"{project_root}/ConfigFiles/run_config.json"
            
            all_run = self.util.get_value(run_config_path, "all_run")
            service_run = self.util.get_value(run_config_path, "process_files_from_ndrive_run")

            if all_run == "STOPPED" or service_run == "False":
                self.run = False

            self.count -= 1

            if self.count == 0:
                self.run = False


if __name__ == '__main__':
    ProcessNewFiles()

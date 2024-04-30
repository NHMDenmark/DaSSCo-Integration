import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from JobList import job_driver
import time

"""
Class responsible for initiating the processing of new files from the ndrive. Specifically this means we have
both a json and an img file of some kind. Calls the JobDriver class for actual processing. 
"""

# TODO needs to decide if a timer or trigger system is needed here.


class ProcessNewFiles:

    def __init__(self):

        self.jobby = job_driver.JobDriver()

        self.new_files_path = f"{project_root}/Files/NewFiles"
        self.updated_files_path = f"{project_root}/Files/UpdatedFiles"
        
        self.run = True
        self.count = 3

        self.loop()

    def loop(self):

        while self.run:

            self.jobby.process_new_directories_from_ndrive()

            time.sleep(2)

            self.count -= 1

            if self.count == 0:
                self.run = False


if __name__ == '__main__':
    ProcessNewFiles()

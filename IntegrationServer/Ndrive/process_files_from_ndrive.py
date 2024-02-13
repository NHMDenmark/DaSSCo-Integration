
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

        self.new_files_path = "IntegrationServer/Files/NewFiles"
        self.updated_files_path = "IntegrationServer/Files/UpdatedFiles"
        
        self.run = True
        self.count = 0

        self.loop()

    def loop(self):

        while self.run:

            self.jobby.process_new_directories_from_ndrive()

            time.sleep(3)

            self.count += 1

            if self.count > 3:
                self.run = False


if __name__ == '__main__':
    ProcessNewFiles()

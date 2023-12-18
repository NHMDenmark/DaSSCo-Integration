from IntegrationServer.JobList import job_driver
import time

"""
Class responsible for initiating the processing of updated files received. Calls the JobDriver class for actual
processing. 
"""

# TODO needs to decide if a timer or trigger system is needed here.


class ProcessUpdatedFiles:

    def __init__(self):

        self.jobby = job_driver.JobDriver()

        self.updated_files_path = "./Files/UpdatedFiles/"
        self.run = True
        self.count = 0

        self.loop()

    def loop(self):

        while self.run:

            self.jobby.process_updated_directories()

            time.sleep(3)

            self.count += 1

            if self.count > 3:
                self.run = False


if __name__ == '__main__':
    ProcessUpdatedFiles()

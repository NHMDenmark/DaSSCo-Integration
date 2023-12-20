from IntegrationServer.Connections import connections
import time

"""
Class responsible for initiating the process of importing new files. 
Runs a loop that checks a remote location for previously not imported files.
"""


class NewFilesFinder:

    def __init__(self):

        self.new_files_path = "./Files/NewFiles/"
        # TODO change to actual connection_config file or make it non static, for multiple import places to run at same time maybe
        self.ssh_config_path = "ConfigFiles/ssh_connections_config.json"  # Deprecated config.json needs one that reflects reality
        self.run = True
        self.count = 0

        self.cons = connections.Connections()

        self.con = self.cons.create_ssh_connection(self.ssh_config_path)

        self.loop()

    def loop(self):

        while self.run:

            if self.con.new_import_directory_path != "":
                self.con.import_and_sort_files(self.con.new_import_directory_path, self.new_files_path)

            time.sleep(3)

            self.count += 1

            if self.count > 1:
                self.run = False


if __name__ == '__main__':
    NewFilesFinder()


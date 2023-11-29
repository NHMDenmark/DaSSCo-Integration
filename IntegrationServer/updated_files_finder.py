from IntegrationServer.Connections import connections
import time


class UpdatedFilesFinder:

    def __init__(self):

        self.updated_files_path = "./Files/UpdatedFiles/"
        self.ssh_config_path = "ConfigFiles/ssh_connections_config.json"
        self.run = True
        self.count = 0

        self.cons = connections.Connections()

        self.cons.create_ssh_connections(self.ssh_config_path)

        self.loop()

    def loop(self):

        while self.run:

            for con in self.cons.get_connections():
                con.sftp_import_directory_from_server(con.updated_import_directory_path, self.updated_files_path)

            time.sleep(3)

            self.count += 1

            if self.count > 3:
                self.run = False


if __name__ == '__main__':
    n = UpdatedFilesFinder()

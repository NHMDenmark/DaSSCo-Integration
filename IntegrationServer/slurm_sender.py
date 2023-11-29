from IntegrationServer.Connections import connections
import time


class SlurmSender:

    def __init__(self):

        self.ssh_config_path = "ConfigFiles/ssh_connections_config.json"
        self.run = True
        self.count = 0

        self.cons = connections.Connections()

        self.cons.create_ssh_connections(self.ssh_config_path)

        self.loop()

    def loop(self):

        while self.run:

            capacity = 100  # get_slurm_capacity()

            transfer_filepath_list = {"./Files/InProcess/PIPEHERB0001/phb"}  # create_transfer_filelist(capacity)

            total_expected_time = 3  # get from above as well

            for con in self.cons.get_connections():

                if not con.is_slurm:
                    continue

                for path in transfer_filepath_list:
                    print(path, con.export_directory_path)
                    con.sftp_export_directory_to_server(path, con.export_directory_path)

            time.sleep(total_expected_time)  # not sure this works or is desirable

            print(f"done sending to pipe after {total_expected_time}")

            time.sleep(3)

            self.count += 1

            if self.count > 1:
                self.run = False


if __name__ == '__main__':
    n = SlurmSender()

import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import time
from dotenv import load_dotenv
import utility
from dassco_utils.messaging.rabbitmq_client import RabbitMqClient
from MongoDB import metadata_repository, track_repository, service_repository, file_model
from Enums import status_enum, flag_enum, validate_enum, metadata_origin
from HealthUtility import health_caller, run_utility
from rabbitmq_client import RabbitMqClient as RMC

"""
Finds assets that have been created in ARS and are coming from the ingestion server. 
Publishes messages for the ingestion server to consume giving the link to the fileproxy share for the assets found.
Updates the track db that files are ready/being uploaded to ARS.
"""
class PublisherARSLink():

    def __init__(self):
        load_dotenv()

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        
        # service name for logging/info purposes
        self.service_name = "ING Publisher ARS link"
        self.prefix_id = "IPAL"

        # RabbitMQ channel name
        self.queue_channel = "ARS-link-queue"

        self.metadata_mongo = metadata_repository.MetadataRepository()
        self.mongo_track = track_repository.TrackRepository()
        self.service_mongo = service_repository.ServiceRepository()
        self.util = utility.Utility()
        self.health_caller = health_caller.HealthCaller()
        self.status_enum = status_enum.StatusEnum
        self.flag_enum = flag_enum.FlagEnum
        self.validate_enum = validate_enum.ValidateEnum
        self.metadata_origin_enum = metadata_origin.MetadataOriginEnum

        self.run_util = run_utility.RunUtility(self.prefix_id, self.service_name, self.log_filename, self.logger_name, self.pid)

        self.run_util.service_starting_updates()
        entry = self.run_util.log_msg(self.prefix_id, f"{self.service_name} status changed at initialisation to {self.status_enum.RUNNING.value}")
        self.health_caller.run_status_change(self.service_name, self.status_enum.RUNNING.value, entry)

        self.msg_url = os.getenv("rabbit_url")
        self.msg_user = os.getenv("rabbit_user")
        self.msg_pw = os.getenv("rabbit_pw")

        self.msg_client = RMC(host_name=self.msg_url, run_async=True, credentials={"username": self.msg_user, "password": self.msg_pw})

        self.run = self.run_util.get_service_run_status()
        self.run_util.service_run = self.run
        
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
            self.close_db_connections()
            self.msg_client.channel.close()

    def loop(self):
        
        while self.run == self.status_enum.RUNNING.value:
            
            asset = self.mongo_track.get_entry_key_exist_and_key_pair_values([{self.flag_enum.AVAILABLE_FOR_SERVICES.value: self.validate_enum.YES.value, self.flag_enum.HAS_OPEN_SHARE.value: self.validate_enum.YES.value,
                                                                               self.flag_enum.JOBS_STATUS.value: self.status_enum.WAITING.value, self.flag_enum.METADATA_ORIGIN.value: self.metadata_origin_enum.INGESTION_QUEUE.value,
                                                                               self.flag_enum.HAS_NEW_FILE.value: self.validate_enum.YES.value}], "temporary_tusd_id")

            if asset is None:
                time.sleep(300)
                self.end_of_loop_check()
                continue
            
            file_list = asset["file_list"]
            file_info = file_list[0]

            ars_link = file_info["ars_link"]
            tusd_id = asset["temporary_tusd_id"]

            # TODO handle if ars link and or tusd_id is None or empty string

            self.msg_client.publish(self.queue_channel, {"tusd_file_id": tusd_id, "ars_link": ars_link})
            self.mongo_track.update_entry(asset["_id", self.flag_enum.HAS_NEW_FILE.value, self.validate_enum.UPLOADING.value])

            self.end_of_loop_check()

        # out of loop
        self.run_util.service_stopping_updates()     
        self.close_db_connections()
        self.msg_client.channel.close()        
        print("service stopped")

    def end_of_loop_check(self):
        self.run = self.run_util.check_run_changes()

    def close_db_connections(self):
        try:
            self.mongo_track.close_connection()
            self.service_mongo.close_connection()
            self.metadata_mongo.close_connection()
        except Exception as e:
            print(f"Failed to close db connections: {e}")

if __name__ == "__main__":
    PublisherARSLink()
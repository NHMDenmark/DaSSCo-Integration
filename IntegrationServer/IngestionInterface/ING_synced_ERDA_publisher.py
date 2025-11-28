import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

import json
import time
from dotenv import load_dotenv
import utility
from dassco_utils.messaging.rabbitmq_client import RabbitMqClient
from MongoDB.mongo_connection import MongoSharedClient
from MongoDB import track_repository, service_repository
from Enums import status_enum, flag_enum, validate_enum, metadata_origin
from HealthUtility import health_caller, run_utility
from rabbitmq_client import RabbitMqClient as RMC

"""
Finds assets that have had their files synced with ERDA, are coming from the ingestion server and still has their tusd_file_id. 
Publishes a message for the ingestion server to consume letting it know that the sync was successfull and allowing the ingestion server to delete the asset and files.
Deletes the tusd_file_id from the track db.
"""
class SyncedERDAPublisher():

    def __init__(self):
        load_dotenv()

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        
        # service name for logging/info purposes
        self.service_name = "ING Synced ERDA publisher"
        self.prefix_id = "ISEP"

        # RabbitMQ channel name
        self.queue_channel = "ERDA-synced-queue"

        self.mongo_client = MongoSharedClient()
        self.mongo_track = track_repository.TrackRepository(self.mongo_client)
        self.service_mongo = service_repository.ServiceRepository(self.mongo_client)
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

            asset = self.mongo_track.get_entry_key_exist_and_key_pair_values([{self.flag_enum.AVAILABLE_FOR_SERVICES.value: self.validate_enum.YES.value, self.flag_enum.ERDA_SYNC.value: self.validate_enum.YES.value,
                                                                         self.flag_enum.METADATA_ORIGIN.value: self.metadata_origin_enum.INGESTION_QUEUE.value}], "temporary_tusd_id")
            
            if asset is None:
                time.sleep(300)
                self.end_of_loop_check()
                continue

            self.msg_client.publish(self.queue_channel, {"tusd_file_id": asset["temporary_tusd_id"]})
            self.mongo_track.delete_field(asset["_id"], "temporary_tusd_id")
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
        except Exception as e:
            print(f"Failed to close db connections: {e}")

if __name__ == "__main__":
    SyncedERDAPublisher()
import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from dotenv import load_dotenv
import utility
from dassco_utils.messaging.rabbitmq_client import RabbitMqClient
from MongoDB import metadata_repository, track_repository, service_repository, file_model
from Enums import status_enum, flag_enum, validate_enum, metadata_origin
from HealthUtility import health_caller, run_utility

"""
Listens for new messages from the ingestion server with metadata and file information.
Creates the metadata and track data in the integration servers databases. 
Acknowledges received data.
Sets flags for asset to be created in ARS.
"""
class ReceiveMetadata():

    def __init__(self):
        load_dotenv()

        self.log_filename = f"{os.path.basename(os.path.abspath(__file__))}.log"
        self.logger_name = os.path.relpath(os.path.abspath(__file__), start=project_root)
        self.pid = os.getpid()
        
        # service name for logging/info purposes
        self.service_name = "Ingestion communication metadata receiver"
        self.prefix_id = "Icmr"

        # RabbitMQ channel name
        self.queue_channel = "metadata_and_file_info"

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

        # TODO setup real url in env
        self.msg_url = os.getenv("ingestion_queue_url")

        self.msg_client = RabbitMqClient(host_name=self.msg_url, run_async=True, credentials={"username": "guest", "password": "guest"})
        
        self.msg_client.add_handler(self.queue_channel, handler=self.handle_msg)

        self.run = self.run_util.get_service_run_status()
        self.run_util.service_run = self.run
        
        try:
            self.consumption()
        except Exception as e:
            print("service crashed", e)
            try:
                entry = self.run_util.log_exc(self.prefix_id, f"{self.service_name} crashed.", e)
                self.health_caller.unexpected_error(self.service_name, entry)
            except:
                print(f"failed to inform about crash")
            self.run_util.service_stopping_updates()
            self.close_db_connections()

    # consuming loop
    def consumption(self):                  
        self.msg_client.start_consuming()

    def handle_msg(self, msg):
        
        # Checks if the status for running the service has changed before handling the msg. Will close/pause the service without handling the msg if so.
        self.run_status_check_and_handle()

        metadata = msg.metadata
        file_info = msg.file_info

        filename = file_info.file_filename
        crc = file_info.crc
        filesize = file_info.filesize
        tusd_id = file_info.tusd_file_id

        guid = metadata.guid
        pipeline = metadata.pipeline

        # TODO check all data is here and version is correct

        self.metadata_mongo.create_metadata_entry_from_api(guid, metadata)

        self.mongo_track.create_track_entry(guid, pipeline, self.metadata_origin_enum.INGESTION_QUEUE.value)

        file_info_model = file_model.FileModel(name = filename, type= filename[:-3], check_sum= crc, file_size= filesize)

        self.mongo_track.append_existing_list(guid, "file_list", file_info_model)
        self.mongo_track.update_entry(guid, "tusd_id", tusd_id)

    def run_status_check_and_handle(self):
        # checks if service should keep running           
        self.run = self.run_util.check_run_changes()

        # TODO figure out if any handling of pause status is necessary / also throttling here - maybe we dont want 100k assets in system from the get go

        # TODO figure out if killing the service results in a nack for the queue
        if self.run == self.status_enum.STOPPED.value:
            self.run_util.service_stopping_updates()     
            self.close_db_connections()        
            print("service stopped")
            os.kill(self.pid, 9)

    def close_db_connections(self):
        try:
            self.mongo_track.close_connection()
            self.service_mongo.close_connection()
            self.metadata_mongo.close_connection()
        except Exception as e:
            print(f"Failed to close db connections: {e}")

if __name__ == "__main__":
    ReceiveMetadata()
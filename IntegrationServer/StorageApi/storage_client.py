import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
from dasscostorageclient import DaSSCoStorageClient
from StorageApi import storage_service
import json
from dotenv import load_dotenv

class StorageClient():
     def __init__(self):
          load_dotenv()

          client_id = os.getenv("client_id")
          client_secret = os.getenv("client_secret")

          self.client = DaSSCoStorageClient(client_id, client_secret)
          self.service = storage_service.StorageService()

     def test(self):
          
          response = self.client.institutions.list()

          data = response.json()

          for item in data:
               print(item)

     def  create_asset(self, asset_guid, allocation_size = 1):

          json_data = self.service.get_metadata_json_format(asset_guid)
          data_dict = json.loads(json_data)

          # TODO WARNING THIS TAMPERING IS FOR TESTING PURPOSE
          if data_dict["payload_type"] == "":
               data_dict["payload_type"] = "INSERT_FOR_TESTING_PURPOSES"
          if data_dict["asset_pid"] == "":
               data_dict["asset_pid"] = "INSERT_FOR_TESTING_PURPOSES"


          try:
               response = self.client.assets.create(data_dict, allocation_size)
               
               status_code = response["status_code"]

               if status_code == 200:                    
                    return True
               else:
                    return False, f"Received {status_code}, while creating asset."
          except Exception as e:
               exc = f"Api or wrapper fail: {e}"
               print(exc)
               return False, "Api or wrapper fail", e
          
     
     def sync_erda(self, guid):
          try:
               response = self.client.file_proxy.synchronize_erda(guid)

               if response.status_code == 204:
                    return True
               else:
                    return False
          except Exception as e:
               print(f"Api or wrapper fail: {e}")
               return False

     def get_asset_status(self, guid):
          try:
               response = self.client.assets.get_status(guid)

               status = response["data"].status
               
               status_code = response["status_code"]

               if status_code == 200:
                    status = response["data"].status

                    return status
               else:
                    return False
          except Exception as e:
               print(f"Api or wrapper fail: {e}")
               return False

     def open_share(self, guid, institution, collection, mb_allocation):

          user_list = ["TEST_USERS"]

          try:
               response = self.client.file_proxy.open_share(institution, collection, guid, user_list, mb_allocation)

               status_code = response.status_code

               if status_code == 200:
                    data = response.json()

               allocation_status = data["http_allocation_status"]

               if allocation_status == "SUCCESS":

                    path = data["path"]
                    hostname = data["hostname"]
               
                    link = hostname + path
                    
                    return link
               else:
                    return False

          except Exception as e:
               print(f"Api or wrapper fail: {e}")
               return False
          
     def update_metadata(self, guid, update_user = "OCTOPUS"):

          json_data = self.service.get_metadata_json_format(guid)
          data_dict = json.loads(json_data)

          data_dict['updateUser'] = update_user

          # TODO WARNING THIS TAMPERING IS FOR TESTING PURPOSE
          if data_dict["payload_type"] == "":
               data_dict["payload_type"] = "INSERT_FROM_UPDATE_FROM_METADATA_TEST"
          if data_dict["asset_pid"] == "":
               data_dict["asset_pid"] = "INSERT_FROM_UPDATE_FROM_METADATA_TEST"

          try:
               response = self.client.assets.update(guid, data_dict)

               status_code = response["status_code"]
               if status_code == 200:

                    return True
               else:
                    return False

          except Exception as e:
               print(f"Api or wrapper fail: {e}")
               return False
     
     def upload_file(self, guid, institution, collection, filepath, file_size_mb):
          
          try:
               response = self.client.file_proxy.upload(filepath, institution, collection, guid, file_size_mb)

               status_code = response.status_code

               if status_code == 200:
                    return True, 200
               
               # Reponse indicates a mismatch between received crc and the expected crc
               if status_code == 507:
                    return False, 507

          except Exception as e:
               e = f"Api or wrapper fail: {e}"
               print(e)
               return False, e
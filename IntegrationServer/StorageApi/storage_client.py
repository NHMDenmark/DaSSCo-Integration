import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
from dasscostorageclient import DaSSCoStorageClient
from StorageApi import storage_service
from dotenv import load_dotenv
import json

class StorageClient():
     def __init__(self):
          
          load_dotenv()
          self.service = storage_service.StorageService()
          client_id = os.getenv("client_id")
          client_secret = os.getenv("client_secret")

          try:
               self.client = DaSSCoStorageClient(client_id, client_secret)
          except Exception as exc:
               
               self.client = None
               self.status_code, self.note = self.get_status_code_from_exc(exc)
               self.exc = exc

     def test(self):
          
          response = self.client.institutions.list()

          data = response.json()

          for item in data:
               print(item)

     def create_asset(self, asset_guid, allocation_size = 1):

          json_data = self.service.get_metadata_json_format(asset_guid)

          if json_data is None:
               return False

          data_dict = json.loads(json_data)
          
          # TODO WARNING THIS TAMPERING IS FOR TESTING PURPOSE
          if data_dict["payload_type"] == "":
               data_dict["payload_type"] = "INSERT_FOR_TESTING_PURPOSES"
          if data_dict["asset_pid"] == "":
               data_dict["asset_pid"] = "INSERT_FOR_TESTING_PURPOSES"

          print(allocation_size, data_dict)

          try:
               response = self.client.assets.create(data_dict, allocation_size)

               status_code = response["status_code"]
          
               if status_code == 200:                    
                    return True, None, None, status_code
               else:
                    return False, f"Received {status_code}, while creating asset.", None, status_code
          except Exception as exc:
                    
                    status_code, note = self.get_status_code_from_exc(exc)
                    
                    if 400 <= status_code <= 499:
                         return False, "ARS api failed to create asset.", exc, status_code
                    
                    if 500 <= status_code <= 599:

                         if note is not None:
                              return False, f"ARS api, keycloak or dassco sdk failure. {note}", exc, status_code

                         return False, "ARS api, keycloak or dassco sdk failure", exc, status_code

     # helper function that extracts the status code from the exception received from dassco-storage-client 
     def get_status_code_from_exc(self, exc):
          exc_str = exc.__str__()
          exc_split = exc_str.split(":")
          status_code = exc_split[0][-3:]
          note = None
          try:
               status_code = int(status_code)
          except Exception as e:
               status_code = 555
               note = f"Status code set to {status_code} from exception: {e}"
          return status_code, note
     
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
               # Change the above line from True to False, its a hack to work around api being broken

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
          
     def close_share(self, guid, institution = "INSERTED_VALUE", collection = "INSERTED_VALUE", users = ["OCTOPUS"], allocation_mb = 1):

          try:
               response = self.client.file_proxy.delete_share(institution, collection, guid, users, allocation_mb)

               status_code = response.status_code
               if status_code == 200:

                    return True
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
          
          print(guid, institution, collection, filepath, file_size_mb)

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

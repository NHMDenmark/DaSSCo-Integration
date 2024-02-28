import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
from dasscostorageclient import DaSSCoStorageClient
from StorageApi import storage_service

class StorageClient():
     def __init__(self):
          
          client_id = os.environ.get("client_id")
          client_secret = os.environ.get("client_secret")

          self.client = DaSSCoStorageClient(client_id, client_secret)
          self.service = storage_service.StorageService()

     def test(self):
          
          institutions = self.client.institutions.list_institutions()

          for key, value in institutions.items():
               print(key, value)

     def create_asset(self, asset_guid):

          json_data = self.service.get_metadata_json_format(asset_guid)

          response_body = self.client.assets.create_asset(json_data)

          data = response_body.get("data")
          status = response_body.get("status_code")
          


          # TODO handle response body, get the http link and save it primarily
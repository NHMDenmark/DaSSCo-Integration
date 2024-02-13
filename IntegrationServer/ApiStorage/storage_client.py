import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
from dasscostorageclient import DaSSCoStorageClient

class StorageClient():
     def __init__(self):
          
          client_id = os.environ.get("client_id")
          client_secret = os.environ.get("client_secret")

          self.client = DaSSCoStorageClient(client_id, client_secret)
     
     def test(self):
          
          institutions = self.client.institutions.list_institutions()

          for key, value in institutions.items():
               print(key, value)

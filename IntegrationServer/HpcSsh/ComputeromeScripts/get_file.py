import os
from dasscostorageclient import DaSSCoStorageClient
import json

client_id = os.environ.get("client_id")
client_secret = os.environ.get("client_secret")

client = DaSSCoStorageClient(client_id, client_secret)

response = client.institutions.list()

data = response.json()

for item in data:
    print(item)

res = client.file_proxy.get_file("test-institution", "test-collection", "test-asset-guid-10", "pic.tif")

if res.ok:
    with open("downloaded_file.tif", "wb") as f:
        f.write(res.content)
    print("File saved successfully.")
else:
    print("Failed to download the file:", res.status_code)

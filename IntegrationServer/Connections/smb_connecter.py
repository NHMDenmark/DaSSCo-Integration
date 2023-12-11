import io
from smb.SMBConnection import SMBConnection

"""
Class for connecting to smb shares and upload image files to them. Connection data is retrieved from {guid}_smb.json 
and corresponding image files TIF, RAW, JPEG etc are send there.
"""


class SmbConnecter():

    def __init__(self):
        pass

    def test_run(self):
        samba_info = {
            "port": 8015,
            "hostname": "dasscoapp02pl.unicph.domain",
            "smb_name": "share_84",
            "token": "8zN7N8R3xZl07lLS0bd8",
        }

        # Connecting to the Samba server
        conn = SMBConnection(samba_info['token'], '', 'client', samba_info['hostname'], samba_info['smb_name'])
        conn.connect(samba_info['hostname'], samba_info['port'])

        # Specify the file to transfer
        local_file_path = "path/to/local/file.txt"
        remote_file_path = "file.txt"  # Adjust the remote path as needed

        # Reading the local file
        with open(local_file_path, "rb") as local_file:
            file_contents = local_file.read()

        # Creating the remote file and writing the contents
        conn.storeFile(samba_info['smb_name'], remote_file_path, io.BytesIO(file_contents))

        # Disconnecting from the Samba server
        conn.close()

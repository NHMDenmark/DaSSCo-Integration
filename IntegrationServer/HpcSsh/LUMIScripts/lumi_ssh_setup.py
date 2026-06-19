import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from time import sleep

class LumiSshSetup:

    def __init__(self):
        pass
    
    def setup(self, con, channel):

        try:
            sleep(3)
            con.channel_command(channel, "module load LUMI")
            sleep(3)
            con.channel_command(channel, "module load lumi-container-wrapper")
            sleep(2)
            con.channel_command(channel, "set -a")
            sleep(1)
            con.channel_command(channel, "source /scratch/project_465002693/slurm_tykky/ucloud_copy/DaSSCo-Image-Refinery/.env")
            sleep(2)
            con.channel_command(channel, "set +a")
            sleep(1)
            con.channel_command(channel, "cd /scratch/project_465002693/slurm_tykky/hpc-container-wrapper")
            sleep(1)
            con.channel_command(channel, "source etc/profile.d/tykky.sh")
            sleep(3)
            con.channel_command(channel, "tykky activate venv/")
            sleep(3)
            con.channel_command(channel, "cd /scratch/project_465002693/slurm_tykky/ucloud_copy/DaSSCo-Image-Refinery/src/dasscorefinery/")
            sleep(3)
            con.channel_command(channel, "pwd")
            sleep(1)
            con.channel_command(channel, "ls -l barcodeReader.sh")
            sleep(2)
            print("LUMI SSH setup completed successfully.")
        except Exception as e:
            print(f"Error occurred while setting up LUMI SSH: {e}")
            
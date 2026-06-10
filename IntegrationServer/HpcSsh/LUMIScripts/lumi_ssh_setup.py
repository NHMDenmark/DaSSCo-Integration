import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from time import sleep


class LumiSshSetup:

    def __init__(self, connection, channel):
        self.con = connection
        self.channel = channel
    
    def setup(self):

        try:
            print("Starting LUMI SSH setup...")
            self.con.channel_command(self.channel, "module load LUMI", write_to_path="/home/dassco/lumi_setup.log")
            #print("LUMI module loaded.")
            sleep(1)
            self.con.channel_command(self.channel, "module load lumi-container-wrapper")
            #print("LUMI container wrapper module loaded.")
            sleep(2)
            self.con.channel_command(self.channel, "set -a")
            #print("Environment variable export enabled.")
            sleep(1)
            self.con.channel_command(self.channel, "source /scratch/project_465002693/slurm_tykky/ucloud_copy/DaSSCo-Image-Refinery/.env")
            #print("Environment variables sourced.")
            sleep(2)
            self.con.channel_command(self.channel, "set +a")
            sleep(1)
            self.con.channel_command(self.channel, "cd /scratch/project_465002693/slurm_tykky/hpc-container-wrapper")
            #print("Changed directory to HPC container wrapper.")        
            sleep(1)
            self.con.channel_command(self.channel, "source etc/profile.d/tykky.sh")
            #print("Tykky environment sourced.")
            sleep(2)
            self.con.channel_command(self.channel, "tykky activate venv/")
            #print("Tykky virtual environment activated.")
            sleep(2)
            self.con.channel_command(self.channel, "cd /scratch/project_465002693/slurm_tykky/ucloud_copy/DaSSCo-Image-Refinery/src/dasscorefinery/")
            #print("Changed directory to DaSSCo-Image-Refinery source.")
            sleep(1)
            print("LUMI SSH setup completed successfully.")
        except Exception as e:
            print(f"Error occurred while setting up LUMI SSH: {e}")
            
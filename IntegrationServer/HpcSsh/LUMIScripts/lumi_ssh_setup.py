import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from time import sleep


class LumiSshSetup:

    def __init__(self, ssh_con):
        self.con = ssh_con
    
    def setup(self):

        try:
            self.con.ssh_command("module load LUMI", write_to_path="/home/dassco/lumi_setup.log")
            sleep(1)
            self.con.ssh_command("module load lumi-container-wrapper")
            sleep(2)
            self.con.ssh_command("set -a")
            sleep(1)
            self.con.ssh_command("source /scratch/project_465002693/slurm_tykky/ucloud_copy/DaSSCo-Image-Refinery/.env")
            sleep(2)
            self.con.ssh_command("set +a")
            sleep(1)
            self.con.ssh_command("cd /scratch/project_465002693/slurm_tykky/hpc-container-wrapper")        
            sleep(1)
            self.con.ssh_command("source etc/profile.d/tykky.sh")
            sleep(2)
            self.con.ssh_command("tykky activate venv/")
            sleep(2)
            self.con.ssh_command("cd /scratch/project_465002693/slurm_tykky/ucloud_copy/DaSSCo-Image-Refinery/src/dasscorefinery/")
            sleep(1)
            print("LUMI SSH setup completed successfully.")
        except Exception as e:
            print(f"Error occurred while setting up LUMI SSH: {e}")
            print("Failed to complete LUMI SSH setup.")
        
#!/bin/bash

# chmod +x path/to/script

# Exit on error
set -e

# Log output to a file
LOGFILE="/var/log/server_setup.log"
exec > >(tee -i $LOGFILE)
exec 2>&1

echo "Starting server setup"

# Step 1: Update and Upgrade System
echo "Updating and upgrading the system"
apt-get update -y && apt-get upgrade -y

# Step 2: Get sendmail installed and running
echo "Install and run sendmail"
apt-get install -y sendmail
apt-get install -y mailutils
service sendmail start

# Step 3: Update .bashrc with paths to mongo db
echo "Updating .bashrc with MongoDB paths"

echo "export PATH=/work/data/lars/mongodb-linux-x86_64-ubuntu2204-7.0.6/bin:\$PATH" >> ~/.bashrc
echo "export PATH=/work/data/lars/mongosh-2.1.5-linux-x64/bin:\$PATH" >> ~/.bashrc
echo "MongoDB paths added to .bashrc"

# Step 4: Source the .bashrc file to apply changes
echo "Sourcing .bashrc to apply changes"
source ~/.bashrc

# Step 5: Install nginx and setup nginx
echo "Installing and setting up nginx"

apt-get install -y nginx

# this assumes the server running the nginx proxy has the job name added to the nginx default  
echo "server {
        listen 80;

        root /var/www/html;

        index index.html index.htm index.nginx-debian.html;
        server_name j-5051363-job-0;

        location / {
            proxy_pass http://localhost:8000;
            proxy_http_version 1.1;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
      }
}
upstream j-5051363-job-0 {
  server localhost:8000;
}" > /etc/nginx/sites-available/default

service nginx start
echo "Nginx installed and running"

# Step 6: Generate ssh key for slurm usage
echo "Generating ssh key for slurm in ~/.ssh"
ssh-keygen -N "" -f ~/.ssh/slurm
echo "Generated shh key"

# Step 7: Update venv
echo "Activate and update python venv"
source /work/data/integration/venv_integration/bin/activate
pip install -r -y /work/data/Dev-Integration/DaSSCo-Integration/IntegrationServer/requirements.txt
echo "Venv good to go"

# Step 8: Run the integration setup script for the database
echo "Setting up the database"
python /work/data/Dev-Integration/DaSSCo-Integration/IntegrationServer/setup_service_script.py
echo "Database set up"

# Step 9: Run the api endpoints
echo "Starting Health and Hpc api services"
nohup uvicorn hpc_api:app --reload --host 127.0.0.1 --port 8000 > /work/data/Dev-Integration/DaSSCo-Integration/IntegrationServer/HpcApi/nohup1.log 2>&1 &
nohup uvicorn health_api:health --reload --host 127.0.0.1 --port 8555 > /work/data/Dev-Integration/DaSSCo-Integration/IntegrationServer/HealthApi/nohup1.log 2>&1 &
echo "Endpoint services started"

# End of script messages
deactivate
echo "Exited the venv"

echo "Server setup complete! Check the log file at $LOGFILE for details."
echo "Change the ip addres in the nginx proxy to this servers ip (ifconfig)"
echo "Add the ssh key to slurm authorised keys"
echo "Start the integration server services"
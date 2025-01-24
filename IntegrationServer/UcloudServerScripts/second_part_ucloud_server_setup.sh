#!/bin/bash

# chmod +x path/to/script
# must use explicit paths in script,
# do not run with sudo
# only run after running first part and sourcing bash for new paths

# Exit on error
set -e

# Log output to a file
LOGFILE="/var/log/second_part_server_setup.log"
exec > >(tee -i $LOGFILE)
exec 2>&1

HOSTNAME=$(hostname)
IP_ADDRESS=$(hostname -I)
HOMEPATH="/home/ucloud"
INT_PATH="/work/data/Dev-Integration/DaSSCo-Integration/IntegrationServer"
DB_PATH="/work/data/lars"
DB_NAME="dev-db-1-11-2024"

echo "Starting second part of the server setup ---"

# Step 5: Install nginx and setup nginx
echo "Installing and setting up nginx"

apt-get install -y nginx

# this assumes the server running the nginx proxy has the job name added to the nginx default  
echo "server {
        listen 80;

        root /var/www/html;

        index index.html index.htm index.nginx-debian.html;
        server_name $HOSTNAME;

        location /dev/ {
            proxy_pass http://localhost:8000;
            proxy_http_version 1.1;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
      }
        location /control/ {
            proxy_pass http://localhost:8005;
            proxy_http_version 1.1;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
      }
}
upstream dev {
  server localhost:8000;
}

upstream control {
  server localhost:8005;
}" > /etc/nginx/sites-available/default

service nginx start
echo "Nginx installed and running"

# Step 6: Generate ssh key for slurm usage
echo "Generating ssh key for slurm in ~/.ssh"
ssh-keygen -N "" -f $HOMEPATH/.ssh/slurm

# Step 7: Update venv
echo "Activate and update python venv"
source /work/data/integration/venv_integration/bin/activate
pip install -r $INT_PATH/requirements.txt
echo "Venv good to go"

# Step 8: Run the integration setup script for the database

echo "Running the database"

nohup mongod --dbpath $DB_PATH/$DB_NAME > $DB_PATH/$HOSTNAME.log 2>&1 &

echo "Running setup script for database"
python $INT_PATH/setup_service_script.py
echo "Database set up"

# Step 9: Run the api endpoints
echo "Starting Hpc api service, Control api service and local Health api service."
export PYTHONPATH=$INT_PATH
nohup uvicorn HpcApi.hpc_api:app --reload --host 127.0.0.1 --port 8000 > $INT_PATH/HpcApi/$HOSTNAME.log 2>&1 &
nohup uvicorn DashboardAPIs.control_api:control --reload --host 127.0.0.1 --port 8005 > $INT_PATH/DashboardAPIs/$HOSTNAME.log 2>&1 &
nohup uvicorn HealthApi.health_api:health --reload --host 127.0.0.1 --port 8555 > $INT_PATH/HealthApi/$HOSTNAME.log 2>&1 &
echo "Endpoint services started"

# End of script messages
deactivate
echo "Exited the venv"

echo "Server setup complete! Check the log files at $LOGFILE for details."
echo "Change the ip address in the nginx proxy to this servers ip (ifconfig)"
echo "Add the ssh key to hpc(slurm) authorised keys:"
cat $HOMEPATH/.ssh/slurm.pub
echo "Start the integration server services"

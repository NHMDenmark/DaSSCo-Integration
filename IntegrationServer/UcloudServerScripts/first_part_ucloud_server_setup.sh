#!/bin/bash

# chmod +x path/to/script
# must use explicit paths in script
# run with sudo, further steps that require root user should be in this script and not in part two

# Exit on error
set -e

# Log output to a file
LOGFILE="/var/log/first_part_server_setup.log"
exec > >(tee -i $LOGFILE)
exec 2>&1

HOSTNAME=$(hostname)
IP_ADDRESS=$(hostname -I)
HOMEPATH="/home/ucloud"
INT_PATH="/work/data/Dev-Integration/DaSSCo-Integration/IntegrationServer"

echo "Starting first part of server setup ---"

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

echo "export PATH=/work/data/lars/mongodb-linux-x86_64-ubuntu2204-7.0.6/bin:\$PATH" >> $HOMEPATH/.bashrc
echo "export PATH=/work/data/lars/mongosh-2.1.5-linux-x64/bin:\$PATH" >> $HOMEPATH/.bashrc
echo "MongoDB paths added to .bashrc"

# Step 4: Install nginx and setup nginx
echo "Installing and setting up nginx"
sudo apt-get install -y nginx
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

echo "Part one has finished."
echo "Before running the second part of the setup run the command: source $HOMEPATH/.bashrc"
echo "Then run the second part without sudo - this is important"

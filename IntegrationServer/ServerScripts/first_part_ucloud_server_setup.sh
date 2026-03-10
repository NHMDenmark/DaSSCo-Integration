#!/bin/bash

# chmod +x path/to/script
# must use explicit paths in script
# run with sudo
# must have a .env file available with all necessary fields set
# assumes mongodb and mongosh is downloaded and unpacked in the mongodb directory for ucloud this should only be done once:
   # dl: wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2204-7.0.6.tgz
   # unpack: tar -xvzf mongodb-linux-x86_64-ubuntu2204-7.0.6.tgz
   # wget https://downloads.mongodb.com/compass/mongosh-2.1.5-linux-x64.tgz
   # tar -xvzf mongosh-2.1.5-linux-x64.tgz
# future steps that require root user should be in this script and not in part two

# Exit on error
set -e

# Log output to a file
LOGFILE="/var/log/first_part_server_setup.log"
exec > >(tee -i $LOGFILE)
exec 2>&1

HOSTNAME=$(hostname)
IP_ADDRESS=$(hostname -I)
HOMEPATH="/home/ucloud"
INT_PATH="/work/integration/DaSSCo-Integration/IntegrationServer"
MONOGODB_PATH="/work/mongodb"

source $INT_PATH/.env

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

echo "export PATH=$MONOGODB_PATH/mongodb-linux-x86_64-ubuntu2204-7.0.6/bin:\$PATH" >> $HOMEPATH/.bashrc
echo "export PATH=$MONOGODB_PATH/mongosh-2.1.5-linux-x64/bin:\$PATH" >> $HOMEPATH/.bashrc
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

# Step 5: Install, setup user and run rabbitmq. Makes use of the .env file.
#echo "Installing erlang and rabbitmq"
#sudo apt install -y erlang
#sudo apt install -y rabbitmq-server
#echo "Run rabbitmq, enable UI and create user"
#sudo service rabbitmq-server start
#sudo rabbitmq-plugins enable rabbitmq_management
#sudo rabbitmqctl add_user $rabbit_user $rabbit_pw
#sudo rabbitmqctl set_user_tags $rabbit_user administrator
#sudo rabbitmqctl set_permissions -p / $rabbit_user ".*" ".*" ".*"
#echo "Created user $rabbit_user as administrator for rabbitmq. Rabbitmq is running on port 15672."

echo "Part one has finished."
echo "Before running the second part of the setup run the command: source $HOMEPATH/.bashrc"
echo "Then run the second part without sudo - this is important"

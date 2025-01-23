#!/bin/bash

# chmod +x path/to/script
# must use explicit paths in script
# run with sudo

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
echo "Part one has finished."
echo "Before running the second part of the setup run the command: source $HOMEPATH/.bashrc"
echo "Please run the second part"

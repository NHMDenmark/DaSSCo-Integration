# dassco-storage-integration
This Repo will include integration between dassco storage from northtech and nifi including the initial steps for such an integration

## Overview

Consists of multiple smaller apps that share local libraries and uses an incorporated
directory structure to keep track of and update data.  
Contacts and imports image and metadata files from Ndrive. Sorts and creates separate folders for
each set of assets. Creates and assigns a list of jobs an asset set has to go through.
Contacts and persists the data via the NT api. Images eventually gets moved to the Erda database.
Moves through the list of jobs assigned to an asset set and sends data to the slurm server and initiates
jobs there. Checks for finished jobs and updates data accordingly both locally and via NT api. 

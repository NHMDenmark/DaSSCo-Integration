# dassco-storage-integration
This Repo will include integration between dassco storage, the processing of digital assets and the digitisation units. 
Work in progress.

## Overview  

The integration server is a data driven micro service infrastructure. Consists of multiple smaller apps that share local libraries and uses an incorporated
directory structure and a mongo database to keep track of and update data. Also has 3 separate APIs using 'fast api' that enables communication internally and from 3rd party services and users.  
   
Imports image and metadata files from ndrive or receives them through a rest api from the ingestion client. 
Sorts and creates separate folders for each set of assets. Creates and assigns a list of jobs an asset set has to go through.
Contacts and persists the data in ARS (NT api). 
Moves through the list of jobs assigned to an asset set and sends data to the hpc server and initiates
jobs there. 
Receives updated data for finished jobs and updates data accordingly both locally and in ARS (NT api).
Initiates syncing the assets with Specify through the ARS specify bridge.

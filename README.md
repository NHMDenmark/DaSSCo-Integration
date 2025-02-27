# dassco-storage-integration
This Repo will include integration between dassco storage, the processing of digital assets and the digitisation units. 

## Overview

Consists of multiple smaller apps that share local libraries and uses an incorporated
directory structure and a mongo database to keep track of and update data.  
Imports image and metadata files from ndrive or receives them through a rest api from the ingestion client. 
Sorts and creates separate folders for each set of assets. Creates and assigns a list of jobs an asset set has to go through.
Contacts and persists the data in ARS. 
Moves through the list of jobs assigned to an asset set and sends data to the hpc server and initiates
jobs there. 
Receives updated data for finished jobs and updates data accordingly both locally and in ARS (NT api).

## Version

This is a stable version of the integration server and is compatible to work with:

- ARS v1.7.6
- dassco-image-refinery commit 7b33673486cc7a734f483879d570948f5009083c
- metadataTemplate v2_1_0

It was deployed and tested on ucloud servers during most of 2024 and the until the end of February 2025. 
Notably this is the last version before a large overhaul of the metadata is implemented.
It is very unlikely we will return to this version and no changes/updates are expected to happen.

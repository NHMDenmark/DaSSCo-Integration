# Introduction
This document reflects the interactions between Refinery and the Integration Server.

# Sequence
Pre requisite :  An asset has been created in the ARS 
Integration server has persisted the asset in ARS and has a local copy. 

The basic prepration of HERB001 pipeline is initiated: getting the image file from the ARS

1. Integration server asks script running on HPC server to get the asset from ARS by providing the asset guid and the link to download the image file - [Hpc asset creator script](Component_write_up/hpc_asset_creator.md)
2. the pipeline script has saved the image file localaly on HPC server from ARS - [Hpc asset loader](Component_write_up\hpc_pipeline_asset_loader.md)
3. HPC server notifies the integration server that it has received files from ARS - [Hpc asset ready](Component_write_up/hpc_api_asset_ready.md)
4. Integration server updates its track database with the information that HPC has received the asset files - [Hpc asset ready](Component_write_up/hpc_api_asset_ready.md)

-- Start of Pipeline Execution --

5. Integration server asks HPC server(script) to start a pipeline job for the asset - [Hpc job caller](Component_write_up\hpc_job_caller.md)
6. HPC queues the pipeline job for the asset and notifies the integration server job_id and asset_guid - [Hpc job queued](Component_write_up/hpc_api_queue_job.md)
7. Integration server updates the track database with the new information about the queued asset - 
8. HPC server notifies the integration server when the queued job has started - [Hpc job started](Component_write_up/hpc_api_start_job.md)
9. Integration server updates the track database with the new information about the asset -
10. HPC server notifies the integration server that the job has finished and sends the output from the job to the integration server as well - [Hpc job finished](Component_write_up/hpc_api_update_asset.md) or [Hpc barcode reading finished](Component_write_up/hpc_api_barcode.md)
11. Integration server updates the databases with the new information about the asset. This includes potentially all 3 databases, but most likely just the track and metadata database -
12. Integration server sends ARS the new metadata updates and updates the track database with information that this has happened. After this step, the sequence can begin again after the Start of Pipeline Execution if there are more pipeline jobs that need to run on the HPC -

# Glossary

**Integration Server:**  
A server running microservices (apps/scripts), local databases, and API endpoints for receiving data. It is responsible for keeping track of assets and their data, initiating processes for assets as needed. Processes are initiated when certain criteria are met, and criteria are changed in the database when inputs are received through the endpoints.

**Track Database:**  
A database located on the integration server. It keeps track of most things (see MOS database) that relate to an asset's status and the status of its files (e.g., images). It gets updated when any status or files change for the asset and gets populated when the integration server receives a new asset.

**Metadata Database:**  
A database located on the integration server. It contains the metadata belonging to an asset. This gets updated when we receive new information about the asset and gets populated when the integration server receives a new asset.

**MOS Database:**  
A database located on the integration server. It keeps track of and connects MOS assets, including their labels. It gets populated when an asset has been identified as a multi-object specimen.

**Endpoint:**  
Endpoints created by us are continually running and ready to receive some information. They then update the databases on the integration server depending on the information they received.

**ARS:**  
Our permanent databases (ERDA and graphdb) for both the asset's metadata and the asset's other files. It is updated through the use of endpoints created and maintained by NorthTech.

**HPC:**  
A general name for the server(s) where we compute new data for the assets. Pipeline scripts and other helper scripts are found here. We are looking to connect and run these scripts primarily through SSH connections when possible.

**COMPUTEROME:**  
HPC server that does not allow us to connect via SSH, and therefore we are having trouble automating the process of running the pipeline/job scripts for the assets.

**DEIC/Slurm:**  
HPC server that allows us to connect via SSH.

**Rites/Slurm:**  
HPC server that allows us to connect via SSH.


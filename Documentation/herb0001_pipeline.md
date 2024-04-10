# Introduction
This document reflects the interactions between Refinery and the Integration Server.

# Sequence
Pre requisite :  An asset has been created in the ARS 
Integration server has persisted the asset in ARS and has a local copy. 

The basic prepration of HERB001 pipeline is initiated: getting the image file from the ARS

1. Integration server asks script running on HPC server to get the asset from ARS by providing the asset guid and the link to download the image file - [Hpc asset creator script](Component_write_up/hpc_asset_creator.md)
2.  HPC queues the job via [HPC_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [Hpc job queued](Component_write_up/hpc_api_queue_job.md)
3. the pipeline script has saved the image file locally on HPC server from ARS - [Hpc asset loader](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_asset_loader.md)
5. HPC server notifies the integration server that it has received files from ARS - [Hpc_pipeline asset ready](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_asset_ready.md)
6. Integration server updates its track database with the information that HPC has received the asset files - [Hpc asset ready](Component_write_up/hpc_api_asset_ready.md)

-- Start of Pipeline Execution --

_Module barcode reader_

7. Integration server asks HPC server(script) to start a barcode reader job for the asset - [HPC_pipeline_barcode_reader](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_barcode_reader.md)
8. HPC queues the job via [HPC_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [Hpc job queued](Component_write_up/hpc_api_queue_job.md)
9. Integration server updates the track database with the new information about the queued asset.
10. HPC server notifies the integration server when the queued job has started - [Hpc_pipeline_job_started]([Component_write_up/hpc_api_start_job.md](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_job_started.md)).
11. Integration server updates the track database with the new information about the asset.
12. HPC server notifies the integration server that the job has finished and sends the output from the job to the integration server as well via [Hpc barcode reading finished](Component_write_up/hpc_api_barcode.md)
13. Integration server updates the metadata and track databases with the new information about the asset. Integration server updates the MOS database if the asset is a MOS.
14. Integration server sends ARS the new metadata updates and updates the track database with information that this has happened.

_Module OCR_

15. Integration server asks HPC server(script) to start a OCR  job for the asset - [HPC_pipeline_OCR]()
16. HPC queues the job via [HPC_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [Hpc job queued](Component_write_up/hpc_api_queue_job.md)
17. Integration server updates the track database with the new information about the queued asset.
18. HPC server notifies the integration server when the queued job has started - [Hpc_pipeline_job_started]([Component_write_up/hpc_api_start_job.md](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_job_started.md)).
19. Integration server updates the track database with the new information about the asset.
20. HPC server notifies the integration server that the job has finished and sends the output from the job to the integration server as well via [Hpc job finished](Component_write_up/hpc_api_update_asset.md)
21. Integration server updates the metadata and track databases with the new information about the asset.
22. Integration server sends ARS the new metadata updates and updates the track database with information that this has happened. 

_Module Cropping & Derivative_

23. Integration server asks HPC server(script) to start a cropping and derivative job for the asset - [HPC_pipeline_cropping&derivatives]()
24. HPC queues the job via [HPC_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [Hpc job queued](Component_write_up/hpc_api_queue_job.md)
25. Integration server updates the track database with the new information about the queued asset.
26. HPC server notifies the integration server when the queued job has started - [Hpc_pipeline_job_started]([Component_write_up/hpc_api_start_job.md](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_job_started.md)).
27. Integration server updates the track database with the new information about the asset.
28. HPC server notifies the integration server that the job has finished and sends the output from the job to the integration server as well via [Hpc_api_new asset]()
29. All jobs are done and the integration server updates the track database.

_Clean_up_script_

30. NOT IMPLEMENTED. Integration server asks HPC server(script) to start the clean up job for the asset - [HPC_pipeline_clean_up]()


# Glossary

**Integration Server:**  
A server running microservices (apps/scripts), local databases, and API endpoints for receiving data. It is responsible for keeping track of assets and their data, initiating processes for assets as needed. Processes are initiated when certain criteria are met, and criteria are changed in the database when inputs are received through the endpoints.

**Track Database:**  
A database located on the integration server. It keeps track of most things (see MOS database) that relate to an asset's status and the status of its files (e.g., images). It gets updated when any status or files change for the asset and gets populated when the integration server receives a new asset.

**Metadata Database:**  
A database located on the integration server. It contains the metadata belonging to an asset. This gets updated when we receive new information about the asset and gets populated when the integration server receives a new asset.

**MOS Database:**  
Multi object speciment. A database located on the integration server. It keeps track of and connects MOS assets, including their labels. It gets populated when an asset has been identified as a multi-object specimen.

**Endpoint:**  
Endpoints created by us are continually running and ready to receive some information. They then update the databases on the integration server depending on the information they received.

**ARS:**  
Our permanent databases (ERDA and graphdb) for both the asset's metadata and the asset's other files. It is updated through the use of endpoints created and maintained by NorthTech.

**HPC:**  
High performance computing. A general name for the server(s) where we compute new data for the assets. Pipeline scripts and other helper scripts are found here. We are looking to connect and run these scripts primarily through SSH connections when possible.

**COMPUTEROME:**  
HPC server that does not allow us to automatically connect via SSH, and therefore we are having trouble automating the process of running the pipeline/job scripts for the assets. We will be using periodic api calls to check if any jobs needs to run. Makes it require more infrastructure on both the integrationserver and on computerome server.
Uses torque for scheduling.

**DEIC/Slurm:**  
HPC server that allows us to connect via SSH and directly start jobs.
Uses slurm for scheduling.

**Rites/Slurm:**  
HPC server that allows us to connect via SSH and directly start jobs.
Uses slurm for scheduling.


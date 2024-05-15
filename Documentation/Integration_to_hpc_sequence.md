# Introduction
This document reflects the digitization process from workstation to storage in ARS.

# Part I: Ingesting assets to the N-Drive
This part takes care of uploading locally created assets from workstations to a centrally accessible temporary storage, the N-Drive.

Pre requisite :  A digitization session has been successfully finished by a digitizer. This means that there exists a local folder on a workstation containing at least 2 images for each digitized specimen of this session. These 2 images are a _raw_ image (saved in a proprietary image format such as .raf or .CR3) and a _converted_ image (saved in a standardized format such as .tif)  
1. The digitizer starts the IngestionClient on the workstation.
2. The digitizer authenticates themselves with their credentials in the IngestionClient. This is done by contacting [uploadapi_verify endpoint](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/uploadapi_verify.md ). If the digitizer is registered, a positive answer will be sent to the IngestionClient.
3. The digitizer selects the digitization session folder LINK CHELSEA DOCUMENT.
4. The digitizer fills in all necessary data regarding the digitization session, fx institution, collection, preparation type, ....
5.  The digitizer triggers the IngestionClient to execute the automated checks and upload sequence.
6.  First, the IngestionClient checks if every _raw_ image has a corresponding _converted_ image and vice versa.
7. The IngestionClient creates a _metadata file_ (.json format) that contains all metadata information input by the digitizers, see [example](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/metadata_example.json).
8. The IngestionClient checks if any images contain no information data ( 0 MB files).
9. The IngestionClient reads the time each image was taken.
10. The IngestionClient creates a GUID for each image from the supplied information and renames all _converted_ images and the _metdata files_ to their GUID.
11. The IngestionClient sends each _converted_ image, its corresponding _metadata file_, and the image size and image checksum to the [uploadapi_upload endpoint](https://github.com/NHMDenmark/DaSSCo-Integration/edit/main/Documentation/Component_write_up/uploadapi_upload.md). 
12. If the return message is positive, the _raw_ image, _converted_ image and _metadata file_ are deleted from the workstation.
13. If any error occured in the preceeding processes, an issue is created in the [github repository](https://github.com/NHMDenmark/DaSSCo-Image-IngestionClient/issues) with workstation information.


# Part II: Ingesting assets to ARS
This part is repsonsible for uploading assets from the N-Drive to our persistent image and metadata storage, ARS.
N-Drive is mounted on the intergration server.

1. The integration API continuously checks the N-Drive for new uploads. It checks only directory paths that are specified in a config LINK LIST OF WORKSTATIONS file (fx only registered and approved workstation folders are checked). Timestamped digitization folder under the respective workstation are considered new uploads if they don't have a _imported_ prefix.
2. Every asset in a new upload folder is copied to the local storage of the integration server.
3. The metadata file is kept and the information is added to the Metadata Database LINK.
4. For every asset a new entry is created in the Track Database. This entry contains a variety of information about processing, some derived from the metadata. A full overview can be found [Track Database](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Track_fields.md).
5. Depending on the entry of the metadata field _pipeline_, a job list with a fixed sequence is created in the track database. See [Config files README](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/IntegrationServer/ConfigFiles/README.md)
6. The ARS endpoint [create_asset] is contacted to create an asset on ARS. Only a subset of metadata is passed onto ARS. For ARS documentation see [here](https://northtech.atlassian.net/wiki/spaces/DAS/pages/2188902401/Web+API).
7. If the asset has been created succesfully, the image is uploaded to the respective assets file share. The file share is a temporary storage space where the image is available for acessing, but also deletable.
8. When the image has been uploaded, the ARS endpoint [syncronize_ERDA] is called to push the image to the persistent storage on ERDA. This closes the file share, i.e. the file is not accessible anymore.
9. Now, the synronization is validated by contacting the ARS endpoint [get_asset_status] and checking the asset status.

# Part III: Preparing asset for processing
This part prepares syncronized assets for processing.

1. The integration API checks the track database for assets that have the following properties:
   _jobs_status_: WAITING, means that the asset has jobs that have not been started yet
   _synced_with_erda_: YES, means that the asset is already persisted in ARS
   _open_share_: NO, means that the asset has no open share yet for processing
   _is_in_ARS_: YES, means that the metadata for the asset is accesible
   _has_new_file_:NO, means that there is no new file belonging to the asset that needs to be persisted with ERDA first
   _hpc_ready_:NO, means the asset is not already on the HPC
3. Integration API is calling the RS endpoint [open_share] to reopen the file share for the asset. This means that the persisted version of the image if downloaded into the file share from ERDA.

# Part VI: Processing assets on HPC
This part executes the processing of the respective pipeline.

Pre requisite :  An asset has been created in the ARS, the Integration server has persisted the asset in ARS and the asset has an open share. 

-- Start of Pipeline Execution --

_Module: Asset Loader_

1. Integration server asks script running on HPC server to get the asset from ARS by providing the asset guid and the link to download the image file - [hpc asset creator script](Component_write_up/hpc_asset_creator.md)
2.  HPC queues the job via [hpc_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [hpc job queued](Component_write_up/hpc_api_queue_job.md)
3. the pipeline script has saved the image file locally on HPC server from ARS - [hpc asset loader](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_asset_loader.md)
5. HPC server notifies the integration server that it has received files from ARS - [hpc_pipeline asset ready](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_asset_ready.md)
6. Integration server updates its track database with the information that HPC has received the asset files - [hpc asset ready](Component_write_up/hpc_api_asset_ready.md)



_Module: Barcode reader_

7. Integration server asks HPC server(script) to start a barcode reader job for the asset - [hpc_pipeline_barcode_reader](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_barcode_reader.md)
8. HPC queues the job via [hpc_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [hpc job queued](Component_write_up/hpc_api_queue_job.md)
9. Integration server updates the track database with the information it received in the previous step about the queued asset - [hpc job queued](Component_write_up/hpc_api_queue_job.md)
10. HPC server notifies the integration server when the queued job has started - [hpc_pipeline_job_started]([Component_write_up/hpc_api_start_job.md](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_job_started.md)).
11. Integration server updates the track database with the information it received in the previous step about the asset.
12. HPC server notifies the integration server that the job has finished and sends the output from the job  [hpc_pipeline_barcode_reader](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_barcode_reader.md) to the integration server as well via [hpc barcode reading finished](Component_write_up/hpc_api_barcode.md). 
14. Integration server updates the metadata (asset_subject, barcode, multispecimen) and track databases with the information it received in the previous step about the asset. Integration server updates the MOS database if the asset is a MOS.
15. Integration server sends ARS the new metadata updates and updates the track database with information that this has happened.

_Module: OCR_

15. Integration server asks HPC server(script) to start a OCR  job for the asset - [hpc_pipeline_OCR](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_ocr.md)
16. HPC queues the job via [hpc_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [hpc job queued](Component_write_up/hpc_api_queue_job.md)
17. Integration server updates the track database with the information it received in the previous step about the queued asset.
18. HPC server notifies the integration server when the queued job has started - [hpc_pipeline_job_started]([Component_write_up/hpc_api_start_job.md](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_job_started.md)).
19. Integration server updates the track database with the information it received in the previous step about the asset.
20. HPC server notifies the integration server that the job has finished and sends the output from the job [hpc_pipeline_OCR](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_ocr.md) to the integration server as well via [hpc job finished](Component_write_up/hpc_api_update_asset.md)
21. Integration server updates the metadata (tags:ocr) and track databases with the information it received in the previous step about the asset.
22. Integration server sends ARS the new metadata updates and updates the track database with information that this has happened. 

_Module: Cropping & Derivative_

23. Integration server asks HPC server(script) to start a cropping and derivative job for the asset - [hpc_pipeline_cropping&derivatives](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_cropping%26derivatives.md)
24. HPC queues the job via [hpc_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [hpc job queued](Component_write_up/hpc_api_queue_job.md)
25. Integration server updates the track database with the information it received in the previous step about the queued asset.
26. HPC server notifies the integration server when the queued job has started - [hpc_pipeline_job_started]([Component_write_up/hpc_api_start_job.md](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_job_started.md)).
27. Integration server updates the track database with the information it received in the previous step about the asset.
28. HPC server notifies the integration server that the job has finished and sends the output from the job [hpc_pipeline_cropping&derivatives](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_cropping%26derivatives.md) to the integration server as well via [hpc_api_new asset]()
29. All jobs are done and the integration server updates the track database.

_Derivative upload_

30. Integration server asks HPC server(script) to start upload the derivative of the asset - [hpc_pipeline_derivative_upload](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_derivative_upload.md)
31.  HPC queues the job via [hpc_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [hpc job queued]
32. Integration server updates the track database with the information it received in the previous step about the queued asset.
33. HPC server notifies the integration server when the queued job has started - [hpc_pipeline_job_started]([Component_write_up/hpc_api_start_job.md](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_job_started.md)).
34.  Integration server updates the track database with the information it received in the previous step about the asset.
35.  HPC server notifies the integration server that the job has finished and sends the output from the job [hpc_pipeline_derivative_upload](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_derivative_upload.md) to the integration server.

_Clean_up_script_

31. NOT TESTED. Integration server asks HPC server(script) to start the clean up job for the asset - [hpc_pipeline_clean_up]()

# Part V: Finalizing asset
* Closing share
# Glossary

**ARS:**  
Our permanent databases (ERDA and graphdb) for both the asset's metadata and the asset's other files. It is updated through the use of endpoints created and maintained by NorthTech.

**COMPUTEROME:**  
HPC server that does not allow us to automatically connect via SSH, and therefore we are having trouble automating the process of running the pipeline/job scripts for the assets. We will be using periodic api calls to check if any jobs needs to run. Makes it require more infrastructure on both the integrationserver and on computerome server.
Uses torque for scheduling.


**DEIC/Slurm:**  
HPC server that allows us to connect via SSH and directly start jobs.
Uses slurm for scheduling.

**Endpoint:**  
Endpoints created by us are continually running and ready to receive some information. They then update the databases on the integration server depending on the information they received.

**IngestionClient** 
The IngestionClient is a software program that is installed on the workstation. It is used manually by digitizers. Simplified, it is responsible for sending standardized assets to the N-Drive.
It is responsible for:
* creating metadata files for digitized specimen according to our standards
*  preforming simple quality checks
* authenticating the digitizers' credentials via connecting to our database on the Refinery Server
* Sent the digitized specimen and their metadata files to the UploadAPI
* Track errors of the tasks above

**Integration Server:**  
A server running microservices (apps/scripts), local databases, and API endpoints for receiving data. It is responsible for keeping track of assets and their data, initiating processes for assets as needed. Processes are initiated when certain criteria are met, and criteria are changed in the database when inputs are received through the endpoints.

**HPC:**  
High performance computing. A general name for the server(s) where we compute new data for the assets. Pipeline scripts and other helper scripts are found here. We are looking to connect and run these scripts primarily through SSH connections when possible.

**Metadata Database:**  
A database located on the integration server. It contains the metadata belonging to an asset. This gets updated when we receive new information about the asset and gets populated when the integration server receives a new asset.

**MOS Database:**  
Multi object speciment. A database located on the integration server. It keeps track of and connects MOS assets, including their labels. It gets populated when an asset has been identified as a multi-object specimen.

**N-Drive**
Shared drive administered by KU-IT.

**Refinery Server**
The Refinery Server is a server in the KU intranet that is running the UploadAPI. The N-Drive is also mounted on the server, meaning that files stored there can be access from the Refinery Server and new files can be uploaded.

**Rites/Slurm:**  
HPC server that allows us to connect via SSH and directly start jobs.
Uses slurm for scheduling.

**SSH:**
SSH (Secure Shell Protocol) is a protocol that allows users to remotely login into servers/computers and use the command line for task execution while ensuring certain safety standards.

**Track Database:**  
A database located on the integration server. It keeps track of most things (see MOS database) that relate to an asset's status and the status of its files (e.g., images). It gets updated when any status or files change for the asset and gets populated when the integration server receives a new asset.

**UploadAPI**
Software program that runs continuously on the Refinery Server. Simplified, it is responsible for receiving asset from the IngestionClient and administering them on the N-Drive.
 Its task are to authenticate connection requests/users, receive & save  assets (digitized specimen and metadata files) to the N-Drive, and log every asset into a database.  

**Workstation**
A workstation consists of a computer and a digitization setup (fx camera with scaffolding) that is deployed and operated in one of our institutions. 













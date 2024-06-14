
# Introduction to PIPEHERB0001
This document reflects the digitization process from workstation to storage in ARS for NHMD Herbarium pipeline 1.

# Part I: Ingesting assets to the N-Drive
This part takes care of uploading locally created assets from workstations to a centrally accessible temporary storage, the N-Drive.

Pre requisite :  A digitization session has been successfully finished by a digitizer. This means that there exists a local folder on a workstation containing at least 2 images for each digitized specimen of this session. These 2 images are a _raw_ image (saved in a proprietary image format such as .raf or .CR3) and a _converted_ image (saved in a standardized format such as .tif)  
1. The digitizer starts the IngestionClient on the workstation.
2. The digitizer authenticates themselves with their credentials in the IngestionClient. This is done by contacting [uploadapi_verify endpoint](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/uploadapi_verify.md ). If the digitizer is registered, a positive answer will be sent to the IngestionClient.
3. The digitizer selects the digitization session folder [see documentation](N:/SCI-SNM-DigitalCollections/DaSSCo/Workflows and workstations/GUIDES/2 Masters/Herbarium Guides/Herbarium Imaging Guide 2nd edit 20240411.docx).
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
3. The metadata file is kept and the information is added to the ]Metadata Database] (https://github.com/NHMDenmark/DaSSCo-Integration/tree/main/Documentation/Data_field_descriptions).
4. For every asset a new entry is created in the Track Database. This entry contains a variety of information about processing, some derived from the metadata. A full overview can be found [Track Database](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Track_fields.md). Here, each asset is also asigned a batchID saved under [list](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Track_field_descriptions/batch_list_name.md). This batchID groups images by the workstation they were digitised on and the date they were digitised. This is required for our current MOS system to work. 
5. Depending on the entry of the metadata field _pipeline_, a job list with a fixed sequence is created in the track database. See [Config files README](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/IntegrationServer/ConfigFiles/README.md)
6. The ARS endpoint [create_asset] is contacted to create an asset on ARS. The [metadata](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/metadata_example.json) is passed onto ARS. Additionally, some required dummy data is filled in (asset_pid). For ARS documentation see [here](https://northtech.atlassian.net/wiki/spaces/DAS/pages/2188902401/Web+API).
7. If the asset has been created succesfully, the image is uploaded to the respective assets file share. The file share is a temporary storage space where the image is available for acessing, but also deletable.
8. When the image has been uploaded to the file share, the ARS endpoint [syncronize_ERDA] is called to push the image to the persistent storage on ERDA. This closes the file share, i.e. the file is not accessible anymore.
9. Now, the syncronization is validated by contacting the ARS endpoint [get_asset_status] and checking the asset status.
10. If the validation fails, error processes need to be executed (DEFINE ERROR PROCESSES).
11. At this stage, no files have been deleted from the Integration server.

# Part III: Preparing asset for processing
This part prepares syncronized assets for processing.

1. The integration API checks the Track Database for assets that have the following properties:
   * _jobs_status_: WAITING, means that the asset has jobs that have not been started yet
   * _synced_with_erda_: YES, means that the asset is already persisted in ARS
   * _open_share_: NO, means that the asset has no open share yet for processing
   * _is_in_ARS_: YES, means that the metadata for the asset is accessible
   * _has_new_file_:NO, means that there is no new file belonging to the asset that needs to be persisted with ERDA first
   * _hpc_ready_:NO, means the asset is not already on the HPC
3. Integration API calls the ARS endpoint [open_share] to reopen the file share in the ARS for the asset. This means that the persisted version of the image is downloaded into the file share from ERDA. 

# Part VI: Processing assets on HPC
This part executes the processing of the respective pipeline. The processing has to happen in this order, no parallelization possible.

Pre requisite :  An asset has been created in the ARS, the Integration server has persisted the asset in ARS and the asset has an open file share. 

-- Start of Pipeline Execution --

_Module: Asset Loader_

1. Integration server invokes script on HPC server to get the asset from ARS by providing the asset guid and the link to download the image file - [hpc asset creator script](Component_write_up/hpc_asset_creator.md)
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
14. Integration server updates the metadata (asset_subject, barcode, multispecimen) and track databases with the information it received in the previous step about the asset.
15. In case the asset is part of a MOS, the Integration server updates the MOS database. It searches the database for assets already processed that match the batchID and disposable barcode (see **MOS** in glossary). It then links the assets of the MOS by updating the "barcode" metadata field.
16. Integration server sends ARS the new metadata updates and updates the track database with information that this has happened.

_Module: OCR_ in development

NOTE: This script is not tested yet. This script is not deployed yet.

15. Integration server asks HPC server(script) to start a OCR  job for the asset - [hpc_pipeline_OCR](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_ocr.md)
16. HPC queues the job via [hpc_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [hpc job queued](Component_write_up/hpc_api_queue_job.md)
17. Integration server updates the track database with the information it received in the previous step about the queued asset.
18. HPC server notifies the integration server when the queued job has started - [hpc_pipeline_job_started]([Component_write_up/hpc_api_start_job.md](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_job_started.md)).
19. Integration server updates the track database with the information it received in the previous step about the asset.
20. HPC server notifies the integration server that the job has finished and sends the output from the job [hpc_pipeline_OCR](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_ocr.md) to the integration server as well via [hpc job finished](Component_write_up/hpc_api_update_asset.md)
21. Integration server updates the metadata and track databases with the information it received in the previous step about the asset.
22. Integration server sends ARS the new metadata updates and updates the track database with information that this has happened. 

_Module: Cropping & Derivative_


23. Integration server asks HPC server(script) to start a cropping and derivative job for the asset - [hpc_pipeline_cropping&derivatives](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_cropping%26derivatives.md)
24. HPC queues the job via [hpc_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [hpc job queued](Component_write_up/hpc_api_queue_job.md)
25. Integration server updates the track database with the information it received in the previous step about the queued asset.
26. HPC server notifies the integration server when the queued job has started - [hpc_pipeline_job_started]([Component_write_up/hpc_api_start_job.md](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_job_started.md)).
27. Integration server updates the track database with the information it received in the previous step about the asset.
28. The asset metadata file is requested from the Integration server again and overwrites the old metadata file. This way all prior changes are persisted. 
32. HPC server notifies the integration server that the job has finished and sends the output from the job[hpc_pipeline_cropping&derivatives_nhmd_herbarium](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_cropping%26derivatives_nhmd_herbarium.md) to the integration server as well via [hpc_api_new asset]()
33. A copy of the original image is cropped, meaning that unimportant areas are excluded form the image. Unimportant areas are defined as areas neither containing herbarium sheet, specimen, side ruler. This way, we reduce storage space needed. A failure to crop can be that 1) important areas are cropped out or 2) unimportant areas are left in the image. In both cases, no reports are made and the images haveto be inspected manually.
34. Next, the cropped image's resolution is downsampled. This way, we reduce storage space needed and images can be served on our websites faster. Currently, only a 400 PPI image is created. The derivative metadata is a copy of the original metadat with the field "parent_guid" updated and linking to the original asset guid.
35. All jobs are done and the integration server updates the track database.

_Module: Derivative upload_

30. Integration server asks HPC server(script) to start upload the derivative of the asset - [hpc_pipeline_derivative_upload](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_derivative_upload.md)
31.  HPC queues the job via [hpc_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [hpc job queued]
32. Integration server updates the track database with the information it received in the previous step about the queued asset.
33. HPC server notifies the integration server when the queued job has started - [hpc_pipeline_job_started]([Component_write_up/hpc_api_start_job.md](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_job_started.md)).
34.  Integration server updates the track database with the information it received in the previous step about the asset.
35.  HPC server notifies the integration server that the job has finished and sends the output from the job [hpc_pipeline_derivative_upload](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_derivative_upload.md) to the integration server.

_Clean_up_script_

NOTE: This script is not tested yet. This script is not deployed yet.

36. Integration server asks HPC server(script) to start the clean up job for the asset - [hpc_pipeline_clean_up]()
37. HPC queues the job via [hpc_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and notifies the integration server job_id and asset_guid - [hpc job queued](Component_write_up/hpc_api_queue_job.md)
38. Integration server updates the track database with the information it received in the previous step about the queued asset.
39. HPC server notifies the integration server when the queued job has started - [hpc_pipeline_job_started]([Component_write_up/hpc_api_start_job.md](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_job_started.md)).
40. Integration server updates the track database with the information it received in the previous step about the asset.
41. The asset is deleted form the HPC
42. HPC server notifies the integration server that the job has finished.

# Part V: Finalizing asset
* Closing share
* date asset finalized
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

**File share/proxy/cache DECIDE ON NAME**

**IngestionClient** 
The IngestionClient is a software program that is installed on the workstation. It is used manually by digitizers. Simplified, it is responsible for sending standardized assets to the N-Drive.
It is responsible for:
* creating metadata files for digitized specimen according to our standards
*  preforming simple quality checks
* authenticating the digitizers' credentials via connecting to our database on the Refinery Server
* Sent the digitized specimen and their metadata files to the UploadAPI
* Track errors of the tasks above

**Integration HPC API**


**Integration Server:**  
A server running microservices (apps/scripts), local databases, and API endpoints for receiving data. It is responsible for keeping track of assets and their data, initiating processes for assets as needed. Processes are initiated when certain criteria are met, and criteria are changed in the database when inputs are received through the endpoints.


**HPC:**  
High performance computing. A general name for the server(s) where we compute new data for the assets. Pipeline scripts and other helper scripts are found here. We are looking to connect and run these scripts primarily through SSH connections when possible.

**Metadata Database:**  
A database located on the integration server. It contains the metadata belonging to an asset. This gets updated when we receive new information about the asset and gets populated when the integration server receives a new asset.

**MOS Database:**  
A database located on the integration server. It keeps track of and connects MOS assets, including their labels. It gets populated when an asset has been identified as a multi-object specimen.

**MOS:**  
Multi object speciment. See [explanation](https://github.com/NHMDenmark/DaSSCo-Image-Refinery/blob/main/Documentation/MOS_label_detection.md).

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













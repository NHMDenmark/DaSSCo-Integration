# Table of Contents
1. [job_detail_config.json](#job_detail_configjson)
2. [mail_config.json](#mail_configjson)
3. [metadata_issues_config.json](#metadata_issues_configjson)
4. [micro_service_config.json](#micro_service_configjson)
5. [mongo_connection_config.json](#mongo_connection_configjson)
6. [ndrive_path_config.json](#ndrive_path_configjson)
7. [pipeline_job_config.json](#pipeline_job_configjson)
8. [slurm_config.json](#slurm_configjson)
9. [workstations_config.json](#workstations_configjson)
10. [throttle_config.json](#throttle_configjson)
11. [control_api_scripts_config.json](#control_api_scripts_configjson)

## Configurations
This document holds guides for necessary configuration and settings for the integration server.


## job_detail_config.json
Job names followed by a time estimate of running them on HPC cluster and the path to the script that needs to be called to run the job on the HPC cluster.

Note: the time_est has not been implemented with slurm scripts.

```bash
{
  "create_asset":{
  "time_est": "00:00:00",
  "script": "path/to/script/or/key/to/script?"
  },
  "update_asset":{
  "time_est": "01:00:00",
  "script": "path/to/script"
  },
  "test":{
  "time_est": "00:00:05",
  "script": "/work/dassco_23_request/lars/test_job.sh"
  },
  "spoof":{
  "time_est": "01:00:00",
  "script": "path/to/script"
  }
}
```

## mail_config.json
Mail configuration file. Test is setup using gmail as a host here. If we are using a linux setup for runnign the integration server then there is no need to configure this.
```bash
  {
    "{name}":{
          "server_host": "localhost",
          "server_port": 587,
          "sender_address": "example@dassco.dk",
          "receiver_address": "maintenance@dassco.dk"
      },
      "test":{
          "server_host": "smtp.gmail.com",
          "server_port": 587,
          "sender_address": "",
          "receiver_address": ""
      }
    }
```

## metadata_issues_config.json
Issues configuration file. This is where issues issued by the integration should be written. Each issue category has its own list of issues. New issue categories should also be created in ARS via the api, before they can be used by the integration server.  
"test" is the category. The issue writer will use this to find the issue.  
Category is the same as the overall category.   
Name is issue name. Issue writer will use this to find the issue.  
Timestamp will be automatically set by the issue writer when an issue is created.   
Status can be added by the integration server or if not then the value set here will be used.  
Description can be added by the integration server or if not then the value set here will be used.  
Notes can be added by the integration server or if not then the value set here will be used.  
Solved should be set to false in the config file and the integration server can change that to true if needed.  
```bash
{
  "test":[{
    "category": "test",
    "name": "example",
    "timestamp": null,
    "status": "BEING_PROCESSED",
    "description": "Example issue for testing purposes.",
    "notes": "No additional notes.",
    "solved": false
    }]
}
```

## micro_service_config.json
Service configuration file. Each service has its own block of configuration values.  
The name is the name the service_name defined in its script. Used to identify the service in logs, mails and between services.  
Module is the module each service belongs to. It is used for defining steps the service should go through when attempting to handle errors/warnings/pause status.
Run_service lets us have services that doesnt have to run by themself, but still could want the rest of the configuration settings available. Rest api services fall into this category.    
Pause_time is the length in seconds each loop in the pause mode should wait.
Pause_check_list is a list of numbers that tells the service at which initial pause loops it should attempt to run again.   
Pause_loop_count is used to define the ongoing attempts to unpause. If set to 100 that means the service will attempt to unpause every 100 loops. This number should be higher than any numbers in the pause_check_list.
Error_tolerance is the amount of errors we tolerate in within the error_time_span before going into pause mode.   
Error_time_span is the time in seconds that combines with error_tolerance to give us the max amount of erorrs in a timeframe before a service enters pause mode.  
Mail_wait_time is the amount of time in seconds that needs to pass before the service will send out a new mail with the same severity level(ERROR, WARNING). This does not block sending out mails that will always be sent such as when a service changes its run status. However it will block mails that would come immediately after such an event.  
Max_sync_erda_attempt_wait_time only matters for the "Validate erda sync ARS service". It sets the time in seconds we allow an asset to have the ASSET_RECEIVED status before we try and sync it again.
```bash
{
  "Asset creator ARS": {
    "module": "storage updater",
    "run_service": true,
    "pause_time": 5,
    "pause_check_list": [2, 7],
    "pause_loop_count": 4,
    "error_tolerance": 2,
    "error_time_span": 10,
    "mail_wait_time": 20,
    "max_sync_erda_attempt_wait_time": 900
  } 
}
```

## mongo_connection_config.json
Overall connection structure for a mongodb instance. Port can be changed but 27017 is standard for a MongoDB. Host will likely be "localhost" but can be set as a remote host. The data_base can be the same for all the collections we need. Collections (the name tag and the collection) that should be available are: metadata, track, MOS, batch, health, throttle and micro_service.

```bash
    "{name}":
    {
    "host": "{hostname}",
    "port": 27017,
    "data_base": "dev_db",
    "collection": "CollectionTestName"
    }
```

## ndrive_path_config.json
Path to the folder on the ndrive where we keep the workstation name folders. Or any other folder from which the integration server should find new assets. 
```bash
  "ndrive_path": "N:/something/that/leads/to/the/path/with/the/workstation/names"
```

## pipeline_job_config.json
List of pipeline names with their associated jobs in order. Each job should be found in the job_detail_config.json file.  
The idea is to setup a list of processes(jobs) that fits everything that comes out of a specific digitisation pipeline.
```bash
{
   "EXAMPLE":{
   "job_1": "test",
   "job_2": "ocr",
   "job_3": "label",
   "job_4": "spoof"
 },
 "PIPEHERB0001":{
   "job_1": "label",
   "job_2": "ocr"
 }
}
```

## slurm_config.json
max_queued_jobs : Sets the maximum amount of jobs we want to have queued up at the same time.
parallel_jobs : Sets the maximum number of jobs we want running at the same time.  
max_expected_time : Sets the maximum total expected amount of time in hours we want to have queued up at the same time.  
max_expected_time_in_queue : Sets the timer(hours) for how long we will wait before checking on a job that has been queued but not returned with a DONE status.  
job_list_script_path : Path to the job list script that gets data for jobs being processed.
export_to_path : Path where assets are delivered.  
temporary_persist_path : Path where we put assets that have finished parts of their pipeline but still needs further processing.  
initiate_script : Path to the script that will be called when a new asset is ready to start being processed by the HPC.  
clean_up_script : Path to the clean up script for when all jobs are DONE for an asset. Should delete files pertaining to the asset on the HPC.

Note: aside from the paths none of these configurations are in use currently.

```bash
{
  "max_queued_jobs": 6,
  "parallel_jobs": 3,
  "max_expected_time": 2000,
  "max_expected_time_in_queue": 1,
  "job_list_script_path": "/work/dassco_23_request/ldam/job_list.sh",
  "export_to_path": "/work/dassco_23_request/ldam/received",
  "temporary_persist_path": "/work/dassco_23_request/ldam/waiting",
  "initiate_script": "/work/dassco_23_request/ldam/test_init.sh",
  "clean_up_script": "path/to/script"
}
```

## workstations_config.json
List of workstations names. Used for recognising which folders on the ndrive to look for assets. 
```bash
{
    "WORKHERB0001": "",
    "WORKHERB0002": "",
    "WORKHERB0003": "",
    "WORKPIOF0001": ""
}
```

## throttle_config.json
Throttle configuration. Sets the max values allowed before the system pauses. The first two are a set number of assets allowed. The last 3 is the max amount of space(in mb) we allow the assets to use in ARS. Total reopened share size is amount shares that have been opened after syncing at least once take up. There is no limit implementation for this amount its just to keep track of it.

Note: assets_in_flight is not implemented in the code to limit the applications, it is implemented at counting assets in flight.

```bash
  {
    "assets_in_flight": 30,
    "await_sync_asset_count": 30,
    "total_asset_size_mb": 45000,
    "total_new_asset_size_mb": 20000,
    "total_derivative_size_mb": 30000,
    "total_reopened_share_size_mb": 1000000
  }
```

## control_api_scripts_config.json
Paths to the callable run scripts for services from the control/dashboard api.
```bash
  {
    "all_run": "path/path/DaSSCo-Integration/IntegrationServer/ServerScripts/all_run.sh",
    "start_service": "/path/path/DaSSCo-Integration/IntegrationServer/ServerScripts/start_service.sh"
  }
```

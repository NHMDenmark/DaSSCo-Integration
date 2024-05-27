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
## job_detail_config.json
Job names followed by a time estimate of running them on HPC cluster and the path to the script that needs to be called to run the job on the HPC cluster.

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
temporary_persist_path : Path where we put assets that have finished parts of their pipeline but still needs further
processing.
initiate_script : Path to the script that will be called when a new asset is ready to start being processed by the HPC.
clean_up_script : Path to the clean up script for when all jobs are DONE for an asset. Should delete files pertaining to the asset on the HPC. 
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

## {name}_connection_config.json

First key is the name of the connection. A connection file must start with the name of the connection. Password and
username should be stored as environment variables named {connection_name}_PWD and {connection_name}_USER 
(example: UCLOUD_PWD).
is_slurm refers to whether the connection connects to the slurm cluster that runs the pipeline jobs. 
Directory paths defines where files end up or are coming from. 
```bash
    "ucloud": {
      "host": "hpc-type3.sdu.dk",
      "is_slurm": "true",
      "password": "put/in/environment/variable",
      "port": "22",
      "status": "closed",
      "username": "put/in/environment/variable"
      }
```

## mongo_connection_config.json
Overall connection structure for a mongodb instance. Port can be changed also but 27017 is standard for a MongoDB.

```bash
    "{name}": {
    "host": "{hostname}",
    "port": 27017,
    "data_base": "FirstTest",
    "collection": "CollectionTestName"
  }
```
## ndrive_path_config.json
Path to the folder on the ndrive where we keep the workstation name folders.
```bash
  "ndrive_path": "N:/something/that/leads/to/the/path/with/the/workstation/names"
```

## mail_config.json
Mail configuration file. Test is setup using gmail as a host here.
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

## run_config.json
Service run configuration file. Sets the state for each service running to either true or false. 
Also can set the status for all services (all_run) at once. Basically a on/off button for the entire integration server. 
```bash
{
    "all_run":"False",
    "file_uploader_run":"True",
    "asset_creator_run":"True",
    "sync_erda_run":"True",
    "update_metadata_run":"True",
    "validate_erda_sync_run":"True",
    "ndrive_new_files_run":"True",
    "process_files_from_ndrive_run":"True",
    "hpc_asset_creator_run":"True",
    "hpc_clean_up_run":"True",
    "hpc_job_caller_run":"True",
    "hpc_open_share_run":"True",
    "hpc_uploader_run":"True"
}
```
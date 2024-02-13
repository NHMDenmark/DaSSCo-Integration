## job_detail_config.json
Jobs here can consist of multiple processes. Each job has to have the total time it takes estimated since that
matters for the slurm queueing system. Each job needs its own sbatch script setup on the slurm server.
Jobs are then added in the order we want them done to each pipeline in the pipeline_job_config.json file.
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
parallel_jobs : Sets the maximum number of jobs the slurm server will process at the same time.
max_expected_time : Sets the maximum total expected amount of time in hours we want to have queued up at the same time.
job_list_script_path : Path to the job list script that gets data for jobs being processed.
import_updates_from_path : Path to get updated data files from once pipeline has finished.
export_to_path : Path where assets are delivered to on the slurm server.
import_new_derivatives_path : Path where new assets that are derivatives should be put. 
temporary_persist_path : Path where we put assets that have finished parts of their pipeline but still needs further
processing. 
```bash
    {
  "max_queued_jobs": 1,
  "parallel_jobs": 3,
  "max_expected_time": 2000,
  "job_list_script_path": "/work/dassco_23_request/lars/job_list.sh",
  "import_updates_from_path": "/home/ldam/updated_data",
  "export_to_path": "/home/ldam/from_integration",
  "import_new_derivatives_path": "/home/ldam/new_created_data",
  "temporary_persist_path": "/home/ldam/waiting"
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
Path to the folder on the ndrive where we keep the pipeline folders.
```bash
  "ndrive_path": "N:/something/that/leads/to/the/path/with/the/pipelines"
```
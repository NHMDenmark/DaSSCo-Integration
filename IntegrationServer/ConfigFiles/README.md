## job_detail_config.json

## pipeline_job_config.json

## slurm_config.json
Sets the maximum amount of jobs we want to have queued up at the same time.
```bash
    "max_queued_jobs": 10
```
Sets the maximum number of jobs the slurm server will process at the same time. 
```bash
    "parallel_jobs": 3
```
Sets the maximum total expected amount of time in hours we want to have queued up at the same time.
```bash
    "total_expected_time": 30
```
Path to the job list script that gets data for jobs being processed. 
```bash
    "job_list_script_path": "/work/dassco_23_request/lars/job_list.sh"
```

## {name}_connection_config.json

First key is the name of the connection. A connection file must start with the name of the connection.
```bash
    "ucloud": {
      "export_directory_path": "/home/ldam/from_integration",
      "host": "hpc-type3.sdu.dk",
      "is_slurm": "true",
      "new_import_directory_path": "",
      "password": "_pwd",
      "port": "22",
      "status": "closed",
      "updated_import_directory_path": "/home/ldam/updated_data",
      "username": "_user"
      }
```

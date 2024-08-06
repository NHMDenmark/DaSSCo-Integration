#!/bin/bash

root="/work/data/DaSSCo-Integration/IntegrationServer"

nohup python "$root/Ndrive/ndrive_new_files.py" > "$root/Ndrive/ndrive_new_files.out" 2>&1 &
nohup python "$root/Ndrive/process_files_from_ndrive.py" > "$root/Ndrive/process_files_from_ndrive.out" 2>&1 &

nohup python "$root/HpcSsh/hpc_asset_creator.py" > "$root/HpcSsh/asset_creator.out" 2>&1 &
nohup python "$root/HpcSsh/hpc_job_caller.py" > "$root/HpcSsh/job_caller.out" 2>&1 &
nohup python "$root/HpcSsh/hpc_uploader.py" > "$root/HpcSsh/uploader.out" 2>&1 &

nohup python "$root/StorageUpdater/asset_creator.py" > "$root/StorageUpdater/asset_creator.out" 2>&1 &
nohup python "$root/StorageUpdater/file_uploader.py" > "$root/StorageUpdater/file_uploader.out" 2>&1 &
nohup python "$root/StorageUpdater/sync_erda.py" > "$root/StorageUpdater/sync_erda.out" 2>&1 &
nohup python "$root/StorageUpdater/update_metadata.py" > "$root/StorageUpdater/update_metadata.out" 2>&1 &
nohup python "$root/StorageUpdater/validate_erda_sync.py" > "$root/StorageUpdater/validate_erda.out" 2>&1 &
nohup python "$root/StorageUpdater/open_share.py" > "$root/StorageUpdater/open_share.out" 2>&1 &
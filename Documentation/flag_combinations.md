| Process | "jobs_status" | "files_status" | "asset_size" | "hpc_ready" | "is_in_ars" | "has_new_file" | "has_open_share" | "erda_sync" | Update_metadata" |
|-------------|--------|----|----|----|---|----|----|-----------|------|
| Ndrive\process_new_files_from_ndrive | -> WAITING | -> NONE | -> file size | -> NO | -> AWAIT -> NO | -> YES | -> NO | -> NO | -> NO |
| StorageUpdater\asset_creator | - | - | not -1 | - | NO -> YES | -> YES | -> YES | - | - |
| StorageUpdater\file_uploader | WAITING | - | not -1 | - | - | YES -> AWAIT | YES | -> NO | - |
| StorageUpdater\sync_erda | - | - | - | - | - | AWAIT | - | NO -> AWAIT | - |
|  StorageUpdater\validate_sync_erda | - | - | - | - | - | -> NO | -> NO | AWAIT -> YES | - |
| StorageUpdater\update_metadata | - | - | - | - | - | - | - | - | YES -> NO |
| HpcSsh\hpc_open_share | WAITING | - | - | NO | YES | NO | NO -> YES | YES | - |
| HpcSsh\hpc_asset_creator | WAITING | - | - | NO -> AWAIT | YES | NO | YES | YES | - |
| HpcSsh\hpc_job_caller | WAITING -> STARTING | - | - | YES | - | - | - | - | - |
| HpcSsh\hpc_clean_up | DONE | - | - | YES -> NO | YES | - | - | - | - |
| HpcSsh\hpc_uploader | DONE | - | - | NO | YES | YES -> UPLOADING | YES | NO | - |
| HpcApi\hpc_api barcode | -> relevant status | - | - | - | - | - | - | - | -> YES |
| HpcApi\hpc_api derivative | -> DONE | -> NONE | -> parent size + estimate size | -> NO | -> AWAIT -> NO | -> NO | -> NO | -> NO | -> NO |
| HpcApi\hpc_api update_asset | -> relevant status | - | - | - | - | - | - | - | -> YES |
| HpcApi\hpc_api queue_job | -> QUEUED | - | - | - | - | - | - | - | - |
| HpcApi\hpc_api start_job | -> RUNNING| - | - | - | - | - | - | - | - |
| HpcApi\hpc_api asset_ready | - | - | - | -> YES | - | - | - | - | - |
| HpcApi\hpc_api derivative_files_uploaded | - | - | - | - | - | -> AWAIT | - | - | - |

| P | js | fs | a s | ready | ars | n file | open sha | e sync | upd mdata |

Updated with status going through AWAIT before NO for is_in_ars. Update asset_size to include estimate for derivatives.

| Process | "jobs_status" | "files_status" | "asset_size" | "hpc_ready" | "is_in_ars" | "has_new_file" | "has_open_share" | "erda_sync" | "update_metadata" | "asset_type" | "temporary_files_ndrive" | "temporary_files_local" | "available_for_services" |
|-------------|--------|------|------|------|------|------|------|-----|------|------|------|------|------|
| Ndrive\process_new_files_from_ndrive | -> WAITING | -> NONE | -> file size | -> NO | -> AWAIT -> NO | -> YES | -> NO | -> NO | -> NO | -> UNKNOWN | -> YES | -> YES | -> YES |
| Ndrive\delete_files_ndrive | DONE | - | - | NO | YES | NO | - | YES | - | - | YES -> remove field | - | YES |
| AssetFileHandler\delete_local_files | DONE | - | - | - | YES | NO | - | YES | - | - | - | YES -> remove field | - |
| StorageUpdater\asset_creator | - | - | not -1 | - | NO -> YES | -> YES | -> YES | - | - | - | - | - | YES |
| StorageUpdater\close_share | - | - | - | YES | - | NO | YES -> NO | YES | - | - | - | - | YES |
| StorageUpdater\file_uploader | WAITING | - | not -1 | - | - | YES -> AWAIT | YES | -> NO | - | - | - | - | YES |
| StorageUpdater\sync_erda | - | - | - | - | - | AWAIT | - | NO -> AWAIT | - | - | - | - | YES |
| StorageUpdater\validate_sync_erda | - | - | - | - | - | -> NO | YES -> NO | AWAIT -> YES | - | - | - | - | YES |
| StorageUpdater\update_metadata | - | - | - | - | - | - | - | - | YES -> NO | - | - | - | YES |
| HpcSsh\hpc_open_share | WAITING | - | - | NO | YES | NO | NO -> YES | YES | - | - | - | - | YES |
| HpcSsh\hpc_asset_creator | WAITING | - | - | NO -> AWAIT | YES | NO | YES | YES | - | - | - | - | YES |
| HpcSsh\hpc_job_caller | WAITING -> STARTING | - | - | YES | - | - | - | - | - | not DEVICE_TARGET | - | - | YES |
| HpcSsh\hpc_clean_up | DONE | - | - | YES | YES | - | - | YES | - | - | - | - | YES |
| HpcSsh\hpc_uploader | DONE | - | - | NO | YES | YES -> UPLOADING | YES | NO | - | - | - | - | YES |
| HpcApi\hpc_api barcode | -> relevant status | - | - | - | - | - | - | - | -> YES | UNKNOWN -> type status | - | - | - |
| HpcApi\hpc_api derivative | -> DONE | -> NONE | -> parent size + estimate size | -> YES | -> AWAIT -> NO | -> NO | -> NO | -> NO | -> NO | - | - | - | - |
| HpcApi\hpc_api update_asset | -> relevant status | - | - | - | - | - | - | - | -> YES | - | - | - | - |
| HpcApi\hpc_api queue_job | -> QUEUED | - | - | - | - | - | - | - | - | - | - | - | - |
| HpcApi\hpc_api start_job | -> RUNNING| - | - | - | - | - | - | - | - | - | - | - | - |
| HpcApi\hpc_api asset_ready | - | - | - | -> YES | - | - | - | - | - | - | - | - | - |
| HpcApi\hpc_api derivative_files_uploaded | - | - | - | - | - | -> AWAIT | - | - | - | - | - | - | - |
| HpcApi\hpc_api asset_clean_up | - | - | - | -> NO | - | - | - | - | - | - | - | - | - |
| HealthUtility\asset_paused_status_handler | - | - | - | - | - | - | - | - | - | - | - | - | PAUSED -> YES |
| HealthUtility\flag_paused_status_handler | - | - | - | (PAUSED) -> previous | (PAUSED) -> previous | (PAUSED) -> previous | (PAUSED) -> previous | (PAUSED) -> previous | (PAUSED) -> previous | - | - | - | - |
| HealthUtility\hpc_job_retry_handler | RETRY -> WAITING | - | - | - | - | - | - | - | - | - | - | - | - |
| HealthUtility\asset_error_status_handler | (ERROR) -> ? | (ERROR) -> ? | - | (ERROR) -> ? | (ERROR) -> ? | (ERROR) -> ? | (ERROR) -> ? | (ERROR) -> ? | (ERROR) -> ? | - | (ERROR) -> ? | (ERROR) -> ? | (ERROR) -> ? |

| P | js | fs | a s | ready | ars | n file | open sha | e sync | upd mdata | asset type | temp f N | temp file l | available |

empty doesnt concern this service   
(status) is when its a possibility for triggering

required status -> change in status
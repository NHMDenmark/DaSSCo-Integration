## Protocol
URL: <asset-service-url>/api/v1/assetmetadata/?allocation_mb=20

Method: GET

#### Create Metadata
This endpoint is the same as you’ve been using before, with only changes being: Instead of a SMB Info Object you get info about HTTPS/Storage and you can allocate storage for the asset you’re working on.

Response Body
{  
    "asset_pid": "asdf-12346-3333-100a21",  
    "asset_guid": "testAsset_10",  
    "status": "WORKING_COPY",  
    ...  
    "httpInfo": {  
        "path": "/assetfiles/<institution>/<collection>/<asset_guid>/",  
        "hostname": "https://storage.test.dassco.dk/file_proxy/api",  
        "total_storage_mb": 90000,  
        "cache_storage_mb": 20000,  
        "remaining_storage_mb": 60000,  
        "allocated_storage_mb": 5000,  
        "http_allocation_status": SUCCESS,  
        "http_allocation_status_text": null  
    },  
    "internal_status": "METADATA_RECEIVED",  
}  

| Field | Unit | Description |
|--|--|--|
| total_storage_mb | MB | The total storage of the server where the FileProxy is deployed. |
| cache_storage_mb | MB | The total amount of storage dedicated for “caching” files for external linking and other use. |
| remaining_storage_mb | MB | The remaining storage on the server: total - cache - all_allocated = remaining |
| allocated_storage_mb | MB | The amount of storage allocated on the server to the new asset |
| http_allocation_status | String enumeration:  SUCCESS, DISK_FULL, ILLEGAL_STATE, UPSTREAM_ERROR, SHARE_NOT_FOUND, INTERNAL_ERROR |  |
| http_allocation_text | An detailed error message if an error happens |  |

#### http_allocation_status descriptions 
|  |  | 
|--|--|  
| SUCCESS  | A share was successfully created or allocation was successfully changed. |
| DISK_FULL | There is not enough disk space for the requested allocation. |
| BAD_REQUEST | Changing the storage allocation to a lower amount than than is already used. |
| UPSTREAM_ERROR | An issue with an external system happened. It could be a failure to download the parent asset from ERDA or a call to asset service from the file-proxy that fails. |
| SHARE_NOT_FOUND | The share you are trying to update doesnt exist. |
| INTERNAL_ERROR | Some unexpected internal error happened. |

#### Change Allocated Storage
URL: <file-proxy-url>/api/shares/assets/<asset_guid>/changeAllocation

Method: POST

Makes it possible to increase/decrease the allocated storage for a given asset, in case you didn’t provide enough or too much initially. 

Response Body  
{  
    "path": "/assetfiles/file_proxy/<institution>/<collection>/<asset_guid>",  
    "hostname": "https://storage.test.dassco.dk/file_proxy/api",  
    "total_storage_mb": 90000,  
    "cache_storage_mb": 20000,  
    "all_allocated_storage_mb": 35000,  
    "remaining_storage_mb": 55000,  
    "allocated_storage_mb": 10000,  
    "http_allocation_status_text": null,  
    "http_allocation_status": "SUCCESS",  
}  
| Field | Unit | Description |
|--|--|--|
| total_storage_mb | MB | The total storage of the server where the FileProxy is deployed. |
| cache_storage_mb | MB | The total amount of storage dedicated for “caching” files for external linking and other use. |
| all_allocated_storage_mb | MB | To make sure there is enough storage for the Assets that is currently being worked on, we’ve added the concept of “storage allocation”.  
This field returns how much is being allocated by all “active” assets |
| remaining_storage_mb | MB | The remaining storage on the server: total - cache - all_allocated = remaining |
| allocated_storage_mb | MB | The amount of storage allocated on the server to the new asset |
| http_allocation_status |  |  |
| http_allocation_text |  | An error message can be displayed here, example: “Allocation failed, no more disk space“ |

#### Upload File
Method: PUT

URL: <file-proxy-url>/api/assetfiles/<institution_name>/<collection_name>/<asset_guid>/folder1/test.txt?crc=123&file_size_mb=2

Here you can upload a single file, but you can call it multiple times to upload multiple files to 1 asset, can also be done concurrently, just make sure to use different file_names when uploading.

If a file already exists on the upload path it will be overwritten by the new file.

Request

content-type: application/octet-steam

| Path Param | Description |
|--|--|
| file_name | The name of the file you’re trying to save, it must be unique for the assets files. (not across all assets) This can also contain folders: https://storage.test.dassco.dk/file_proxy/api/assetfiles/<institution>/<collection>/<asset_guid>/folder_1/folder_2/file.jpg |

| Request Param | Unit | |
|--|--|--|
| file_size_mb | MB | The size of the file, then we can quickly determine whether or not there is allocated enough storage for the file, instead of waiting for an error when saving. |
| file_checksum | long | The “CRC” (Cyclic redundancy check) checksum of the file, it’s used to validate if the file was transfered correctly. Returns 507 if there is a mismatch between the file_checksum and the uploaded file’s checksum  |

Response Body
| Field | Description |
|--|--|
| file_checksum | Returns the checksum we have generated for the file on our system. |

#### Delete File
URL: <file-proxy-url>/api/assetfiles/<institution_name>/<collection_name>/<asset_guid>/folder1/test.txt

Method: DELETE

Delete resource at given path.

If resource is a directory it will be deleted along with its content.

If resource is the base directory for an asset the directory will not be deleted, only the content.

Request 

| Path Param | Description | 
|--|--| 
| file_name | The name of the resource you are trying to delete. File: https://<hostname>/<path>/folder_1/folder_2/file.jpg Entire folder and sub-folders: https://<hostname>/<path>/folder_1/folder_2/ |

Response 

204 on success

404 on if resource is not found

#### Get File
URL: <file-proxy-url>/api/assetfiles/<institution_name>/<collection_name>/<asset_guid>/folder1/test.txt

Method: GET

Here you can download a file. Only shared files can be downloaded. 

Request

content-type: application/octet-steam

| Path Param | Description | 
|--|--| 
| file_name | The name of the file you are trying to fetch. |

#### List File Info
You can list the files uploaded to an asset, and get a list of {name, checksum}, so you can validate if all files have been successfully uploaded.

URL: <file-proxy-url>/api/assets/<asset_guid>/files

Request

| Path Param | Description | 
|--|--| 
| asset_guid | In the url add /<asset_guid>, so we know which asset you to list the files from. |

Response Body

A list of

| Field | Description | 
|--|--|
| file_name | The name of the file we have on our filesystem. |
| path | The path to the file relative from the asset folder |
| file_size | The size of the file MB. |
| file_checksum | The checksum of the file on our filesystem, can be used to check if you have uploaded the newest version. |
| deleteAfterSync | Set if the file have been deleted from the share and will have its info deleted from the file proxy database when synchronisation happens. |

Async Job (Not an API, but a schedule)  
Every 5 min (can be adjusted after need), an async job will run and start to upload all the files that has been scheduled for upload, to their assigned asset.

#### Get Asset Status
URL: <asset-service-url>/api/v1/assets/status/<asset_guid>

Method: GET

This endpoint can return the status of an asset, so you know what stage the asset is in. It can be: scheduled for ERDA, persisted on ERDA, failed to upload to ERDA etc.

Response Body

| Field | Description | 
|--|--|
| asset_guid | The guid of an asset we have registered in the Asset Service. |
| parent_guid | The guid of the parent to the asset we have registered in the Asset Service. |
| error_timestamp | The timestamp when the error occurred, only sent if an error occurred |
| status | The asset status can be one of the following: METADATA_RECEIVED, ASSET_RECEIVED, ERDA_ERROR, COMPLETED |
| error_message | The error we received while working with the asset, for example: “Connection Reset, while uploading to ERDA”, only sent if  an error occurred | 

#### Sync to ERDA
URL: <file-proxy-url>/api/shares/assets/<asset_guid>/synchronize?workstation=ti-ws-01&pipeline=ti-p1

Method: POST

Close for further uploads to the asset, and schedules the asset files for ERDA. Once this has been called the asset is “closed” for now and awaits upload to ERDA.

Request

| Path Param | Description | 
|--|--|
| asset_guid | In the url add /<asset_guid>, so we know which asset you want to sync to ERDA. |

Retry Sync to ERDA
The File Proxy will only try to upload a set amount of times, and after that, the asset will enter an “error” state. To retry synchronisation simply call the Sync to ERDA endpoint again as this will reset the amount of tries that has been used on the syncing the asset.

This can come in handy, when issues turns out to network issues or downtime on ERDA. Because then retrying should be enough. 

#### Get All “Work in progress” Assets
URL: <asset-service-url>/api/v1/assets/inprogress/?onlyFailed=true

Method: GET

This endpoint will return a list of all assets that is currently being worked on.

This includes assets with the following internal_asset_statuses: METADATA_RECEIVED, ASSET_RECEIVED and ERDA_FAILED

The query parameter onlyFailed filters the result so only assets with ERDA_FAILED are returned.

Response Body

A list of

| Field | Description | 
|--|--|
| asset_guid | The guid of an asset we have registered in the Asset Service. |
| parent_guid | The guid of the parent to the asset we have registered in the Asset Service. |
| error_timestamp | If an error occured when did it happen |
| status | The asset status can be one of the following: METADATA_RECEIVED(work in progress), ASSET_RECEIVED(work in progress), ERDA_ERROR(failed) |
| allocated_storage | How much storage has been allocated to the individuel asset |
| error_message | The error we received while working with the asset, for example: “Connection Reset, while uploading to ERDA”, only sent if  an error occurred |

#### List available files on file-proxy
URL: <file-proxy-url>/api/assetfiles/test-institution/test-collection/<asset_guid>/

Method: GET

This endpoint returns a list of files available for the given asset_guid. This endpoint can be used to check available files for the parent asset after opening af new http share.

Response Body

A list of urls

[  
    "<file_proxy_url>/api/assetfiles/test-institution/test-collection/a12/file.png",  
    "<file_proxy_url>/api/assetfiles/test-institution/test-collection/a12/parent/parent_file.png"  
]   

#### Open share  
URL: <file-proxy-url>/api/assets/{assetGuid}/createShare

Method: POST

Here you can open a share of an existing asset. The post body consists of a list of assets to be shared and a list of usernames of users that should have access to the share. The amount of space needed to be allocated also needs to be specified. The list of assets can only contain one asset when using this endpoint.

Post body:

{  
    "assets": [{  
        "asset_guid": "asset_8",  
        "institution": "test-institution",  
        "collection": "test-collection"  
    }],  
    "users": [  
        "thbo"  
    ],  
        "allocation_mb": 10  
}  

Response body

| Field | Unit | Description | 
|--|--|--|
| path | | The path to the asset. |
| hostname | | Where the asset files can be posted to. The hostname can be combined with the asset path to form an url where asset files can be posted og downloaded. |
| total_storage_mb | MB | The total storage of the server where the FileProxy is deployed. |
| cache_storage_mb | MB | The total amount of storage dedicated for “caching” files for external linking and other use. |
| all_allocated_storage_mb | MB | To make sure there is enough storage for the Assets that is currently being worked on, we’ve added the concept of “storage allocation”. This field returns how much is being allocated by all “active” assets |
| remaining_storage_mb | MB | The remaining storage on the server: total - cache - all_allocated = remaining |
| allocated_storage_mb | MB | The amount of storage allocated on the server to the new asset |
| http_allocation_status | | |
| http_allocation_text | | An error message can be displayed here, example: “Allocation failed, no more disk space“ |

#### Delete share
URL: <file-proxy-url>/api/shares/assets/{assetGuid}/deleteShare

Method: DELETE

This service deletes a share and all files in the share without synchronizing ERDA.

Files already persisted in ERDA will not be deleted.

### HealthChecks
#### Health API
/actuator/health on Asset Service

Response

| Field | Values | Description |  
|--|--|--|
| erda_status | UP / DOWN / UNKNOWN | On a schedule, we will try to create and delete a file, to see if ERDA is working as intended. |
| file_proxy_status | UP / DOWN / UNKNOWN | On a schedule, we will contact the File Proxy and test if its running as intended. |
| asset_service_status | UP / DOWN / UNKNOWN | On a schedule, we will check if all the dependencies that Asset Service needs are available. Database etc. |
| keycloak | UP / DOWN / UNKNOWN | On a schedule, if Keycloak is up and running. |

### Asset status field
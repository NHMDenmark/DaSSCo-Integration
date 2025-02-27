## APIs

This page contains a list of the different API that is available on the Dassco service

URL: 
https://storage.test.dassco.dk/api

#### Upload asset sequence
This diagram shows the sequence in which you call the different services in order to upload an asset. [Diagram](/documentation/diagrams/Unavngivet%20diagram-1692177041694.drawio)

The numbers on the boxes corrosponds to a webservice that can help accomplish the action described in the box. [Diagram](/documentation/diagrams/Unavngivet%20diagram-1694075843443.drawio)


### Table of Contents
1. [Create Institution](#create-institution-1)
2. [List Institutions](#list-institutions-2)
3. [Create Workstation](#create-workstation-3)
4. [List Workstations](#list-workstations-4)
5. [Update Workstation](#update-workstation-5)
6. [Create Pipeline](#create-pipeline-6)
7. [List Pipelines](#list-pipelines-7)
8. [Create Collection](#create-collection-8)
9. [List Collections](#list-collections-9)
10. [Create Asset](#create-asset-10)
11. [Get Asset](#get-asset-11)
12. [Update Asset](#update-asset-12)
13. [Complete Asset](#complete-asset-13)
14. [Open Share](#open-share-14)
15. [Disconnect Share](#disconnect-share-15)
16. [Reopen Share](#reopen-share-16)
17. [Close Share](#close-share-17)
18. [List Events](#list-events-18)

### Create institution (1)
Creates an institution.

Method: POST

Path: /v1/institutions/

Body
{  
    "name":"test-institution"  
}  
### List institutions (2)  
Method: GET

Path: /v1/Institutions/

Returns a list of institutions

### Create workstation (3)
Register a workstation in an institution

Method: POST

Path: /v1/institutions/{institutionName}/workstations/

Body:
{  
    "name":"ti-ws-01",  
    "status":"IN_SERVICE"  
}  

### List workstations (4)
List workstations belonging to an institution

Method: GET

Path: /v1/institutions/{institutionName}/workstations

### Update workstation (5)
Updates the status on a workstation. Valid statuses: IN_SERVICE, OUT_OF_SERVICE

Method: PUT

Path: /v1/institutions/{institutionName}/workstations/{workstationName}

Body: 
{  
    "name":"ti-ws-01",  
    "status":"IN_SERVICE"  
}  
### Create pipeline (6)
Register a pipeline

Method: POST

Path: /v1/institutions/{institutionName}/pipelines/

Body:
{  
    "name":"ti-p1"  
}  
### List pipelines (7)
List all pipelines belonging to an institution

Method: GET

Path: /v1/institutions/{institutionName}/pipelines/

### Create collection (8)
Creates a new collections under an institution

Method: POST

Path: /v1/institutions/{institutionName}/collections/

Body:
{  
    "name":"test-collection"  
}  

### List collections (9)
Lists collections under a given institution

Method: GET

Path: /v1/institutions/{institutionName}/collections/

### Create asset (10)
Creates asset metadata. This initialises the file upload by opening a SMB share where files belonging to the asset can be uploaded. The endpoint returns the created asset metadata with an additional field called sambaInfo that provides the connection parameters for the share.

If the service fails to create the share the metadata is still persisted and a share can be opened manually using the open share endpoint.

Method: POST

Path: /v1/assetmetadata/{assetGuid}

Body:  
{  
  "asset_pid": "asdf-12346-3333-100a21",  
  "asset_guid": "asset_3",  
  "status": "WORKING_COPY",  
  "multi_specimen": true,  
  "specimens": [{  
      "barcode": "barcode-123",  
      "specimen_pid": "tezt_pid",  
      "preparation_type": "pinning"  
  }  
  ],  
  "funding": "hundredetusindvis af dollars",  
  "subject": "folder",  
  "payload_type": "ct scan",  
  "file_formats": [  
    "TIF"  
  ],  
  "asset_locked": false,  
  "restricted_access": [  
    "USER"  
  ],  
  "audited": false,  
  "asset_taken_date": "1998-11-15T16:00:00.000Z",  
  "institution": "test-institution",  
  "collection": "test-collection",  
  "pipeline": "ti-p1",  
  "workstation": "ti-ws-02",  
  "parent_guid": null,  
  "digitizer" : "thbo",  
  "tags": {  
      "testtag2": "et håndtag i form af en springende hjort"  
  }  
}  
Response body (Only the sambainfo part)  
{  
    "pid": "asdf-12346-3333-100a21",  
    "guid": "testAsset_10",  
    "status": "WORKING_COPY",  
    ...  
    "sambaInfo": {  
        "port": null,  
        "hostname": null,  
        "smb_name": null,  
        "token": null,  
        "sambaRequestStatus": "INTERNAL_ERROR",  
        "sambaRequestStatusMessage": "Failed to get samba share, please try manually checking out the asset"  
    },  
    "internal_status": "METADATA_RECEIVED",  
    ..  
}  
### Get asset (11)
Get the metadata on an assset

Method: GET

Path: /v1/assetmetadata/{assetGuid}

Update asset (12)
Updates asset metadata

Method: PUT

Path: /v1/assetmetadata/{assetGuid}/

Body:  
{  
  "asset_pid": "asdf-12346-3333-100a21",  
  "asset_guid": "asset_3",  
  "status": "WORKING_COPY",  
  "multi_specimen": true,  
  "specimens": [{  
      "barcode": "barcode-123",  
      "specimen_pid": "tezt_pid",  
      "preparation_type": "pinning"  
  }  
  ],  
  "funding": "hundredetusindvis af dollars",  
  "subject": "folder",  
  "payload_type": "ct scan",  
  "file_formats": [  
    "TIF"  
  ],  
  "asset_locked": false,  
  "restricted_access": [  
    "USER"  
  ],  
  "audited": false,  
  "asset_taken_date": "1998-11-15T16:00:00.000Z",  
  "institution": "test-institution",  
  "collection": "test-collection",  
  "pipeline": "ti-p1",  
  "workstation": "ti-ws-02",  
  "parent_guid": null,  
  "digitizer" : "thbo",  
  "tags": {  
      "testtag2": "et håndtag i form af en springende hjort"  
  }  
}  
 

### Complete asset (13)
Mark asset as completed.

Description
This is used to manually mark an asset as complete in the metadata.

The only case where this endpoint should be used is when all files belonging to an asset has been uploaded but the metadata dont have the completed status. The status should be set automatically when closing a share and syncing ERDA.

Method: PUT

Path: /v1/assetmetadata/{assetGuid}/complete

Body: none

### Open share (14)
Opens a smb share with the given assetIds.

Description
This endpoint is used to open a share  to view and upload assets. 

Method: POST

Path: /v1/shares/open

Body:  
{  
    "users": [  
    ],  
    "assets": [  
        {  
            "asset_guid": "asset_1"  
        }  
    ]  
}  

### Disconnect share (15)
Disconnects the share but keeps the file in temp storage.

Description
This method is used in cases where you want to temporarely close a share and want to access it at a later time. Using this endpoint helps performance by releasing resources that would otherwise has been wasted by the idling shares.

The share can be reopened with the reopen share endpoint(16)

Method: POST

Path: /v1/shares/disconnect

Body:  
{  
    "shareName": "share_1",  
    "assetGuid": ""  
}  

### Reopen share (16)
Reopen a share that was disconnected.

Method: POST

Path: /v1/shares/reopen

Body:
{  
    "shareName": "share_60"  
}  
 

### Close share (17)
Closes the share, and synchronizes ERDA if the share contains the files of a single asset and the syncERDA option is selected.

Method: POST

Path: /v1/shares/close

Query params: 

syncERDA

type: boolean

default: false

Body:  
{     
    "minimalAsset": {  
        "asset_guid": "asset_1"  
    },  
    "shareName": "share_66"  
}  

### List events(18)
Return list of events belonging to an asset guid.

Method: GET

Path: /v1/assetmetadata/{assetGuid}/events/

{  
  "pipeline": "pl1",  
  "user": "user_1",  
  "workstation": "ws1",  
  "event": "CREATE_ASSET",  
  "timestamp": "2023-07-24 09:12:33"  
}  
# Table of content

1. [Description](#description)
2. [Field folders](#field-folders)
3. [xx_fields.md](#xx_fieldsmd)
4. [xx_overview.md](#xx_overviewmd)
5. [Flag Combinations in Track](#flag_combinations_in_trackmd)
6. [Herb0001 Pipeline](#herb0001_pipelinemd)
7. [Integration_to_hpc_sequence.md](#integration_to_hpc_sequencemd)
8. [Components Write Up](#components-write-up)
9. [Metadata Example jsons](#Metadata_example_jsons)
10. [Python Scripts](#python-scripts)
11. [Potential XLSX Files](#potential-xlsx-files)
12. [Confluence documentation](#Confluence_documentation_-_ARS)

## Description  
Field documentation for databases and metadata pertaining to the integration server and ingestion client can be found in this part of the repository. Furthermore it contains auxiliary documentation related to the datafields. It includes a write up document for a pipeline workflow and writeups for each component necessary for the workflow.  
It contains a small collection of python scripts meant for making maintaining and updating the documentation easier. This means that changes made in f.ex. an excel sheet can easily be updated and added to all the other documentation. It is important to note that this updating doesnt happen automatically and if you make changes it is your responsibility to either update the rest of the documentation accordingly or get help from someone who can.  
The repository should not change directory since we are linking from github issues directly to part of it.  

## Field folders  
Contains in depth descriptions of each field in the corresponding database. The information is repeated in the overview.md document. Each document in these folders is linked in the corresponding _fields.md document.  
The documents can be created from the overview document by one of the python scripts and vice versa.   
[Asset metadata field docs](/Documentation/Metadata_field_descriptions/)  
[Health db field docs](/Documentation/Health_field_descriptions/)  
[MOS db field docs](/Documentation/MOS_field_descriptions/)  
[Track db field docs](/Documentation/Track_field_descriptions/)
[ARS metadata field descriptions](/Documentation/ARS_metadata_field_descriptions/)    
[]()  

## xx_fields.md  
Tables that show the where, when and sometimes why for database and metadata fields. Each field in the document is linked to another document in the corresponding field folder to more in depth description of the field.  
[Metadata fields](/Documentation/Metadata_fields.md)  
[Health fields](/Documentation/Health_fields.md)  
[MOS fields](/Documentation/MOS_fields.md)  
[Track fields](/Documentation/Track_fields.md)  
[ARS metadata fields](/Documentation/ARS_metadata_fields.md)  

## xx_overview.md  
Tables showing the description for each database and metadata field. This is the exact same information found in the documents in the fields folder. 
Updates here or in the fields folder can be synced by using the python scripts.  
[Metadata fields](/Documentation/Metadata_overview.md)  
[Health fields](/Documentation/Health_overview.md)  
[MOS fields](/Documentation/MOS_overview.md)  
[Track fields](/Documentation/Track_overview.md)  
[ARS metadata fields](/Documentation/ARS_metadata_overview_15_08_24.md)  

## flag_combinations_in_track.md  
Gives an overview of the specific flag combinations needed for a service to start working with an asset. Also shows the changes upon a successfull interaction with the flag.   
[flag combos](/Documentation/flag%20combinations_in_track.md)

## herb0001_pipeline.md 
Write up for the herb0001 pipeline. It describes each step of the pipeline in detail and links to corresponding the components for even more technical details.   
[herb0001 pipeline](/Documentation/herb0001_pipeline.md)

## Integration_to_hpc_sequence.md
Generic write up for the pipeline workflow from integration server to hpc. It describes each step of the pipeline in detail and links to corresponding the components for even more technical details.  
[Integration to hpc](/Documentation/Integration_to_hpc_sequence.md)


## Components write up  
Contains pipeline component detailed documents.  
[Components folder](/Documentation/Component_write_up/) 

## Metadata_Example_jsons
This contains examples of metadata json file as they look at various stages.  
[Example](/Documentation/Metadata_example_jsons/metadata_example.json)

## Python Scripts  
Contains python scripts that are not part of the main functionalities of the integration server. They are meant to supplement, update and help maintain the documentation found in this area. There are scripts for converting changes for fields across multiple documents. They are not meant to be run often and each requires a bit of configuration before being run.
The scripts should contain enough information to be "easily" modified and run.  
[Python scripts](/Documentation/Python_Scripts/)

## Potential xlsx files  
Excel files can be created with one of the python scripts. Github does not support opening or working with excel files so the files has to be downloaded and used locally. It is possible to update the fields through updated excel sheets added to the Documentation folder in github.  

## Confluence-documentation-ARS  
This contains the documentation from the DaSSCo-asset-service repository. The documentation originally was transferred from the confluence repository used by NorthTech while collaborating with DaSSCo.  
[Confluence documentation](/Documentation/Confluence_documentation_ARS/)

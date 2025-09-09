### Adding new services to the integration server  
- Create a module or add the new service to an already existing one. Use the [service_skeleton](service_skeleton.py) as a template.
- Fill out all the name fields in the new service. Class name (+ main call), service name and prefix_id.
- Update the [all_run script](../../IntegrationServer/UcloudServerScripts/all_run.sh)
- Update the [micro service config file](../../IntegrationServer/ConfigFiles/micro_service_config.json)
- Update the [micro service paths](../../IntegrationServer/DashboardAPIs/micro_service_paths.py) for the dashboard api.
- Add logic to the service.
- Run [setup service script](../../IntegrationServer/setup_service_script.py) to add the service to the database.
- Restart or start the dashboard api.
- Update documentation where its required. Typically if new fields are added to the databases or a new set of flags is being used.


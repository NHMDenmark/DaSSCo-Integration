## Mocked servers

### Slurm server
The slurm ucloud server is mocked in connections.py.
This is a mocked interpretation of the slurm server on ucloud and all the ssh connection classes. It is named the same as the "connections" in the Connections module to make it easy to switch to the mock setup and back.
Change the import "from Connection import connections" in all the HpcSsh services to "from Tests.MockServers import connections".
Naming it the same means no other changes needs to happen to run tests with the mock setup.
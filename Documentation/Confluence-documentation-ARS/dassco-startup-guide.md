Here I will explain how you can start, stop and restart the DaSSCo Storage System. 

### Startup  
If you have to boot the DaSSCo Storage System after an unwanted shutdown, for example that the cluster has to be reinitialised. Then you can follow the steps below:

Find out which of the app servers that is the “leader” of the cluster

I usually just run the command “sudo docker node ls“ on the different app servers

If it’s not the leader it will return: “Error response from daemon: This node is not a swarm manager.”

If it’s the leader, then it will return a list of all the machines

On the Leader app server run this command:

```bash
sudo docker stack deploy -c /docker-swarm/stack/docker-compose.yaml test 
```
The folder “docker-swarm” contains the same files on all the app servers

At the end it says “test” that can just be a random “name”, but this is the test environment, so I’ve called it “test”.

It should start booting all the containers, you can check the status with:

```bash
sudo docker service ls
```
| ID |              NAME |                 MODE |         REPLICAS |   IMAGE |        PORTS |
|---|---|---|---|---|---|
| j68xiq4x9zl7 |   test_asset_service |   replicated |   1/1   |      nhmdenmark/dassco-asset-service:1.0.4 |  |
| kjwhxvahw781 |   test_file_proxy    |   replicated |   1/1                 |    nhmdenmark/dassco-file-proxy:1.0.10 | |
| qifem04x5n5u |   test_keycloak    |     replicated |   1/1                 |    quay.io/keycloak/keycloak:21.1.1 | |
| ptx6lhik72q6  |  test_loadbalancer  |   replicated |   3/3 (max 1 per node) |   nginx:latest | |                        
| fo2t3y0kvbeb  |  test_postgres  |       replicated |   1/1       |              apache/age:v1.1.0 | |

Once they are all ready, then you will be able to contact the different services.

### Shutdown  
If you want to shutdown the service, you can do so with the steps bellow:

Find out which of the app servers that is the “leader” of the cluster

I usually just run the command “sudo docker node ls“ on the different app servers

If it’s not the leader it will return: “Error response from daemon: This node is not a swarm manager.”

If it’s the leader, then it will return a list of all the machines

On the Leader app server run this command:
```bash
sudo docker stack rm test
``` 
At the end it says “test” that can just be a random “name”, but it is set when you deploy the stack. check step 2 in “Startup”.

It should start deleting all the services, you can check the status with:
```bash
sudo docker service ls
```
| ID |  NAME  |  MODE | REPLICAS  |  IMAGE  |      PORTS |
|--|--|--|--|--|--|
| x |  |  |  | | |

### Reboot
If you want to reboot / restart the system, we suggest you run the “Shutdown” step and then the “Startup” step after all the services has been removed. 
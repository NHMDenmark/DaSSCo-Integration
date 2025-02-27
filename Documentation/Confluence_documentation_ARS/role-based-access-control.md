### Role Based Access Control


| ENV | URL | 
|--|--|
| TEST | https://idp.test.dassco.dk  |
| PROD | xx |

When working you’re with Keycloak, there’s a few terms that are important to know:

Realms

Client

Realm Roles vs Client Roles

 

Realms are a way to have multiple systems and user databases on your Keycloak, for DaSSCo we have 2 realms: dassco and master. The dassco realm is used for the whole dassco environment, and it is where you will add new users you want to access the DaSSCo Storage. The master realm is a default realm that keycloak comes with, and is used for the Keycloak admin console. So if you want a different user than the DaSSCo Admin to configure the keycloak with, then this is where you will have to created the account and give it the proper roles: Server Administration Guide 

Client are a way to split the realm into sections, these sections can all talk with each other, but it’s best practice to create a client per app in the realm. So for example in DaSSCo we have a client for the DaSSCo Storage, and if we were to setup Specify to use the same IDP then it would makes sense to give it its own client. It would still be able to use the same users as the DaSSCo Storage system (users are realm bound).

You can see the realm as an organisation and clients as apps, in our case the realm dassco, and the clients could be DaSSCo Storage or Specify. If we want create a global role that can be used in both apps, then it makes sense to create them as a realm role. If it’s specific for that app, then you should client roles instead. We’ve used realm roles in this system.

### Keycloak Access
Realm: master
The admin console users and the DaSSCo Storage users are not the same users, if you want to manage your Keycloak settings you need to create your user on the master realm and set your after Keycloak recommendations:

Current role guide:  [Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/#_admin_permissions) 

### DaSSCo Storage Access
Realm: dassco
If you want to add users to the DaSSCo Storage then you have to create the users on the dassco realm, and assign them the roles needed for this users' requirements:

| Role | Access | Use Case | 
|--|--|--|  
| dassco-admin | You have full access to all endpoints | If you’re the administrator for the DaSSCo system, this is the role for you. It will allow you to add new Institutions, workstations and pipelines. Plus list all data and monitoring on the UI. |
| dassco-developer | You will have access to most endpoints, focusing on what is needed for the asset creation process. You will also be able to access the docs on the Storage System. | This should be used when working you’re developing on the project. |
| dassco-user | This is the “normal” access, you can get and list assets |
| service-user | This is the role that gives access to upload, read and list from the DaSSCo Storage. | This is for the service users running on the Refinery |


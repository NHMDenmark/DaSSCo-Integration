## UploasAPI verify script

**Where:**  
Runs on the refinery server under the url https://refinery.dassco.dk/verify.

**Inputs/conditions:**  
The input is either a https GET request with default information or a POST request with 
* Username
* Password
* CSRF token

**Description:**  
This script has two tasks:
1. if contacted by a GET request, it will send a CSRF token back so a secure connection can be established.
2. if contacted by a POST request, the user credentials are checked with our database to verify whether that user exists and the password is correct

**Outputs/Updates:**  
The output of the GET contact is a CSRF token.
The output of the POST contact is a status code:
* 200 for successful authentication
* everything else for no success in authentcating the user

**Calls:**  
N/A


# Author : Graham Land
# Date:    03/10/2016
#
# Purpose: Simple python 2.7 script to demonstrate how to use the Fujitsu K5 IaaS API
#          The script creates a security group in a project
#
# blog:    https://allthingscloud.eu
# twitter: @allthingsclowd

import requests

# get a project scoped auth token
def get_scoped_token(uname,upassword,uproject,udomain):
    identityURL = 'https://identity.uk-1.cloud.global.fujitsu.com/v3/auth/tokens'
    response = requests.post(identityURL, 
    	                     headers={'Content-Type': 'application/json','Accept':'application/json'}, 
    	                     json={"auth":
    	                            {"identity":
    	                              {"methods":["password"],"password":
    	                                {"user":
    	                                   {"domain":
    	                                      {"name":udomain}, "name":uname, "password": upassword}}}, 
    	                                      "scope": { "project": {"id":uproject}}}})
    return response.headers['X-Subject-Token']

# create security group
def create_security_group(k5token,sgname,sgdescription):
    sgURL = 'https://networking.uk-1.cloud.global.fujitsu.com/v2.0/security-groups'
    response = requests.post(sgURL,
                            headers={'X-Auth-Token':k5token,'Content-Type': 'application/json','Accept':'application/json'},
                            json={"security_group":
                                   {"name": sgname,
                                    "description": sgdescription
                                   }
                                 })
    return response.json()

def list_security_groups(k5token):
    sgURL = 'https://networking.uk-1.cloud.global.fujitsu.com/v2.0/security-groups'
    response = requests.get(sgURL,
                            headers={'X-Auth-Token':k5token,'Content-Type': 'application/json','Accept':'application/json'})
    return response.json()

def create_security_group_rule(k5token,direction,pmin,pmax,protocol,sgid):
    sgURL = 'https://networking.uk-1.cloud.global.fujitsu.com/v2.0/security-group-rules'
    response = requests.post(sgURL,
                            headers={'X-Auth-Token':k5token,'Content-Type': 'application/json','Accept':'application/json'},
                            json={"security_group_rule": 
                                   {"direction": direction,
                                    "port_range_min": pmin,
                                    "ethertype": "IPv4",
                                    "port_range_max": pmax,
                                    "protocol": protocol,
                                    "security_group_id": sgid
                                    }
                                  })
    return response.json()

# Define contract parameters
adminUser = 'username'
adminPassword = 'password'
contract = 'contractname'
contractid = 'contractid'
myproject = 'myprojectid'

# Get a project scoped token
k5token = get_scoped_token(adminUser,adminPassword,myproject,contract)

# Display scoped token
print "\n\nToken : " + k5token

# Create a security group
result = create_security_group(k5token,"Demo_SG","This SG will permit SSH")

# Display the result
print "\n\nResponse from Security Group Creation : \n" + str(result) + "\n"

# Capture security id from above result
security_group_id = result['security_group'].get('id')

# Create a security group rule and assign to security group
result = create_security_group_rule(k5token,'ingress','22','22','tcp',security_group_id)

# Display the result
print "\n\nResponse from Security Group Rule Creation : \n" + str(result) + "\n"

# Get all security group details
result = list_security_groups(k5token)

# Display the result
print "\n\nList of All Security Group Details : \n" + str(result) + "\n\n"







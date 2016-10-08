#!/usr/bin/python


import sys
import os
import requests
import uuid
import base64
import time
import getopt
import ntpath
# load your K5 contract details from k5contractsettings.py file
from k5contractsettings import *



# get a scoped auth token
def get_scoped_token(uname,upassword,uproject,udomain,uregion):
    identityURL = 'https://identity.' + uregion + '.cloud.global.fujitsu.com/v3/auth/tokens'
    response = requests.post(identityURL,
                             headers={'Content-Type': 'application/json','Accept':'application/json'},
                             json={"auth":
                               {"identity":
                                 {"methods":["password"],"password":
                                   {"user":
                                     {"domain":
                                       {"name":udomain},
                                        "name":uname,
                                        "password": upassword
                                }}}, 
                                "scope": 
                                  { "project": 
                                    {"id":uproject
                            }}}})

    return response.headers['X-Subject-Token']


def get_unscoped_token(uname,upassword,udomain,uregion):
    identityURL = 'https://identity.' + uregion + '.cloud.global.fujitsu.com/v3/auth/tokens'
    response = requests.post(identityURL, 
                            headers={'Content-Type': 'application/json','Accept':'application/json'},
                            json={"auth":
                              {"identity":
                                {"methods":["password"],"password":
                                  {"user":
                                    {"domain":
                                      {"name":udomain},
                                       "name":uname,
                                       "password": upassword
                            }}}}})

    return response.headers['X-Subject-Token']

# get a central identity portal token
def get_unscoped_idtoken(uname,upassword,udomain):
    response = requests.post('https://auth-api.jp-east-1.paas.cloud.global.fujitsu.com/API/paas/auth/token',
                             headers={'Content-Type': 'application/json'},
                             json={"auth":
                               {"identity":
                                 {"password":
                                   {"user":
                                     {"contract_number":udomain,
                                      "name":uname,
                                      "password": upassword
                            }}}}})

    return response.headers['X-Access-Token']

def share_image_with_project(adminUser,adminPassword,defaultid,projectid,image_id,contract,region):

    # get a regional domain scoped token to make queries to facilitate conversion of object names to ids
    scoped_k5token = get_scoped_token(adminUser,adminPassword,defaultid,contract,region)

    imageURL = 'https://image.' + region + '.cloud.global.fujitsu.com/v2/images/' + image_id + '/members'
    response = requests.post(imageURL, 
                            headers={'X-Auth-Token':scoped_k5token,'Content-Type': 'application/json','Accept':'application/json'},
                            json={"member": projectid})

    print response.json()
    return response.json()['status']

def accept_image_share_from_default_project(adminUser,adminPassword,defaultid,projectid,image_id,contract,region):
    
    # get a regional domain scoped token to make queries to facilitate conversion of object names to ids
    scoped_k5token = get_scoped_token(adminUser,adminPassword,projectid,contract,region)

    imageURL = 'https://image.' + region + '.cloud.global.fujitsu.com/v2/images/' + image_id + '/members/' + projectid
    response = requests.put(imageURL, 
                            headers={'X-Auth-Token':scoped_k5token,'Content-Type': 'application/json','Accept':'application/json'},
                            json={"status": "accepted"})

    print response.json()
    return response.json()['status']

def main():
    
    try:
    # define global variables from the command line parameters

        global image_id
        global projects
        global status

        # ensure minimium commandline paramaters have been supplied
        if (len(sys.argv)<4):
            print("Usage1: %s -i 'image_id' -p 'project_id'" % sys.argv[0])
            sys.exit(2)
        
        # load the command line parameters
        myopts, args = getopt.getopt(sys.argv[1:],"i:p:",["imageid=","projects="])
    except getopt.GetoptError:
        # if the parameters are incorrect display error message
        print("Usage1: %s -i 'image_id' -p 'project_id'" % sys.argv[0])
        sys.exit(2)
    


    ###############################
    # o == option
    # a == argument passed to the o
    ###############################
    for o, a in myopts:
        if o in ('-i','--imageid'):
            image_id=a
        elif o in ('-p','--projects'):
            projects=a 
        else:
            print("Usage1: %s -i 'image_id' -p 'project_id'" % sys.argv[0])


    # enable sharing from primary project to member project
    print "\nSharing image " + image_id + " from default tenant " + defaultid + " with " + projects    
    result = share_image_with_project(adminUser,adminPassword,defaultid,projects,image_id,contract,region)
    print result
    print "\nShared image " + image_id + " from default tenant " + defaultid + " with " + projects 

    # activate sharing within member project to complete process
    print "\nAccepting image " + image_id + " from default tenant " + defaultid + " with " + projects
    result = accept_image_share_from_default_project(adminUser,adminPassword,defaultid,projects,image_id,contract,region)
    print result
    print "\nAccepted image " + image_id + " from default tenant " + defaultid + " with " + projects 


if __name__ == "__main__":
    main()
    
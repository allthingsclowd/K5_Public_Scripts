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

# create a container
def create_new_storage_container(adminUser,adminPassword,project,container_name,contract,region):

    # get a regional domain scoped token to make queries to facilitate conversion of object names to ids
    scoped_k5token = get_scoped_token(adminUser,adminPassword,project,contract,region)
    print scoped_k5token    
    identityURL = 'https://objectstorage.' + region + '.cloud.global.fujitsu.com/v1/AUTH_' + project + '/' + container_name
    print identityURL
    response = requests.put(identityURL,
                             headers={'X-Auth-Token':scoped_k5token,'Content-Type': 'application/json'})
    
    return response

def upload_file_to_container(adminUser,adminPassword,project,container_name,file_name,file_path,contract,region):

    # get a regional domain scoped token to make queries to facilitate conversion of object names to ids
    scoped_k5token = get_scoped_token(adminUser,adminPassword,project,contract,region) 

    uploadfile = open(file_path, 'rb')
    data = uploadfile.read()
    identityURL = 'https://objectstorage.' + region + '.cloud.global.fujitsu.com/v1/AUTH_' + project + '/' + container_name + '/' + file_name
    
    response = requests.put(identityURL,
    	                      data=data,
    	                      headers={'X-Auth-Token':scoped_k5token,'Content-Type': 'application/octet-stream'})
    
    uploadfile.close
    return response	

def import_from_container_to_k5(adminUser,adminPassword,project,container_name,file_name,display_name,file_path,os_type,contract,region):

    # get a regional domain scoped token to make queries to facilitate conversion of object names to ids
    scoped_k5token = get_scoped_token(adminUser,adminPassword,project,contract,region) 

    k5ContainerURL = '/v1/AUTH_' + project + '/' + container_name + '/' + file_name
    image_id = str(uuid.uuid4())
    encodedPassword = base64.b64encode(adminPassword)

    vmimportURL = 'https://vmimport.' + region + '.cloud.global.fujitsu.com/v1/imageimport'
    
    response = requests.post(vmimportURL,
    	                      headers={'X-Auth-Token':scoped_k5token},
    	                      json={"name":display_name,
    	                            "location":k5ContainerURL,
    	                            "id":image_id,
    	                            "conversion": True,
    	                            "os_type":os_type,
    	                            "user_name":adminUser,
    	                            "password":encodedPassword,
    	                            "domain_name":contract})
    
    return response.json()

def verify_image_import_status(adminUser,adminPassword,project,image_id,contract,region):

    # get a regional domain scoped token to make queries to facilitate conversion of object names to ids
    scoped_k5token = get_scoped_token(adminUser,adminPassword,project,contract,region) 

    vmimportURL = 'https://vmimport.' + region + '.cloud.global.fujitsu.com/v1/imageimport/' + image_id + '/status'
    
    response = requests.get(vmimportURL,
    	                    headers={'X-Auth-Token':scoped_k5token})
    
    return response.json()

def upload_manifest_to_container(adminUser,adminPassword,project,container_name,file_name,prefix,contract,region):

    # get a regional domain scoped token to make queries to facilitate conversion of object names to ids
    scoped_k5token = get_scoped_token(adminUser,adminPassword,project,contract,region) 

    identityURL = 'https://objectstorage.' + region + '.cloud.global.fujitsu.com/v1/AUTH_' + project + '/' + container_name + '/' + file_name
    
    response = requests.put(identityURL,
    	                    headers={'X-Auth-Token':scoped_k5token,'X-Object-Manifest': container_name + '/' + prefix})
    
    return response	


# list items in a container
def view_items_in_storage_container(adminUser,adminPassword,project,container_name,contract,region):

    # get a regional domain scoped token to make queries to facilitate conversion of object names to ids
    scoped_k5token = get_scoped_token(adminUser,adminPassword,project,contract,region)    
    identityURL = 'https://objectstorage.' + region + '.cloud.global.fujitsu.com/v1/AUTH_' + project + '/' + container_name + '?format=json'
    response = requests.get(identityURL,
                             headers={'X-Auth-Token':scoped_k5token,'Content-Type': 'application/json'})
    
    return response

# download item in a container
def download_item_in_storage_container(adminUser,adminPassword,project,container_name,contract,region):

    # get a regional domain scoped token to make queries to facilitate conversion of object names to ids
    scoped_k5token = get_scoped_token(adminUser,adminPassword,project,contract,region)    
    identityURL = 'https://objectstorage.' + region + '.cloud.global.fujitsu.com/v1/AUTH_' + project + '/' + container_name + '/manifest'
    print identityURL
    response = requests.get(identityURL,
                             headers={'X-Auth-Token':scoped_k5token,'Content-Type': 'application/json'})
    
    return response

def make_out_filename(prefix, idx):
    '''Make a filename with a serial number suffix.'''
    return prefix + str(idx).zfill(4)

def bsplit(in_filename, bytes_per_file,os_type):
    '''Split the input file in_filename into output files of 
    bytes_per_file bytes each. Last file may have less bytes.'''

    in_fil = open(in_filename, "rb")
    outfil_idx = 1
    out_filename = make_out_filename(os_type, outfil_idx)
    out_fil = open(out_filename, "wb")

    byte_count = tot_byte_count = file_count = 0
    c = in_fil.read(1)

    # Loop over the input and split it into multiple files 
    # of bytes_per_file bytes each (except possibly for the 
    # last file, which may have less bytes.
    while c != '':
        byte_count += 1
        out_fil.write(c)
        # Bump vars; change to next output file.
        if byte_count >= bytes_per_file:
            tot_byte_count += byte_count
            byte_count = 0
            file_count += 1
            out_fil.close()
            result = upload_file_to_container(adminUser,adminPassword,defaultid,container_name,out_filename,out_filename,contract,region)

            print "Uploaded Package - " + str(file_count)
            os.remove(out_filename)

            outfil_idx += 1
            out_filename = make_out_filename(os_type, outfil_idx)
            out_fil = open(out_filename, "wb")
        c = in_fil.read(1)
    # Clean up.
    in_fil.close()
    if not out_fil.closed:
        out_fil.close()
        result = upload_file_to_container(adminUser,adminPassword,defaultid,container_name,out_filename,out_filename,contract,region)
        print "\nUploaded Package - " + str(file_count)
        os.remove(out_filename)
    if byte_count == 0:
        os.remove(out_filename)

    # now create manifest file
    result = upload_manifest_to_container(adminUser,adminPassword,defaultid,container_name,file_name,os_type,contract,region)
    return result

def main():
    
    try:


        # ensure minimium commandline paramaters have been supplied
        if (len(sys.argv)<6):
            print("Usage1: %s -i 'path_to_image' -c 'container_name' -n 'image_display_name' -p '{project1,project2,project3}' -t [ubuntu|centos|rehhat|win2008SE] [-s 'chunk size in bytes'] " % sys.argv[0])
            sys.exit(2)
        
        # load the command line parameters
        myopts, args = getopt.getopt(sys.argv[1:],"i:c:n:p:t:s:",["imagepath=","container=","name=","projects=","type=","size="])
    except getopt.GetoptError:
        # if the parameters are incorrect display error message
        print("Usage2: %s -i 'path_to_image' -c 'container_name' -n 'image_display_name' -p '{project1,project2,project3}' -t [ubuntu|centos|rehhat|win2008SE] [-s 'chunk size in bytes'] " % sys.argv[0])
        sys.exit(2)
    
    # define global variables from the command line parameters

    global container_name
    global display_name
    global bytes_per_file
    global os_type
    global file_path
    global file_name

    # set default chunk size for large images that needs to be broken up must be below 5GB for Swift Object Storage
    bytes_per_file = 1048576000       #5242880 #1048576000 #262144000 # 250Mb chunks    

    ###############################
    # o == option
    # a == argument passed to the o
    ###############################
    for o, a in myopts:
        if o in ('-i','--imagepath'):
            file_path=a
        elif o in ('-c','--container'):
            container_name=a
        elif o in ('-n','--name'):
            display_name=a
        elif o in ('-p','--projects'):
            projects=a
        elif o in ('-t','--type'):
            os_type=a
        elif o in ('-s','--size'):
            bytes_per_file=int(a)            
        else:
            print("Usage3: %s -i 'path_to_image' -c 'container_name' -n 'image_display_name' -p '{project1,project2,project3}' -t [ubuntu|centos|rehhat|win2008SE] [-s 'chunk size in bytes'] " % sys.argv[0])

    # extract filename from file path suplied at cli
    file_name = ntpath.basename(file_path)
 
    # attempt to read the contents of the container to see if it already exists
    result = view_items_in_storage_container(adminUser,adminPassword,defaultid,container_name,contract,region)

    # check to see if container already exists, if not then create it
    if (result.status_code == 404):
    	# create container
        print "\nCreating new container : " + container_name
        result = create_new_storage_container(adminUser,adminPassword,defaultid,container_name,contract,region)
        print "\nCreated new container : " + container_name

    # check size of file to be uploaded is less than 250GB, if not split into smaller chunks for upload
    if (os.path.getsize(file_path) > bytes_per_file):

        # loop through image file for multi-part upload
        print "\n---------- Starting multi-part file upload  to K5 object storage ------ \n"
        result = bsplit(file_path, bytes_per_file,os_type)
        print "\n---------- Finished multi-part file upload to K5 object storage ------ \n"

    else:
    	# simple file upload to container
        print "\n---------- Starting simple file upload  to K5 object storage ------ \n"
        result = upload_file_to_container(adminUser,adminPassword,defaultid,container_name,file_name,file_path,contract,region)
        print "\n---------- Finished simple file upload  to K5 object storage ------ \n"

    # list container
    print "\n---------- List container contents K5 object storage start ------ \n"
    result = view_items_in_storage_container(adminUser,adminPassword,defaultid,container_name,contract,region)
    print result
    print "\n---------- List container contents K5 object storage end ------ \n"


    # Register image with K5
    print "\n---------- Registering image with K5 ------ \n"
    result = import_from_container_to_k5(adminUser,adminPassword,defaultid,container_name,file_name,display_name,file_path,os_type,contract,region)
    image_id = result['import_id']
    print result
    print "\n---------- K5 Image import_id : " + image_id + "\n"

    # Get import status
    print "\n---------- Check import status ---------- \n\n"
    result = verify_image_import_status(adminUser,adminPassword,defaultid,image_id,contract,region)
    print result

    while ((result['import_status'] != "succeeded") and (result['import_status'] != "failed")):

        time.sleep(300)
        print "\n---------- Check import status ---------- \n"
        result = verify_image_import_status(adminUser,adminPassword,defaultid,image_id,contract,region)
        print result


    print "End of Import Process - Import status >>>  " + result['import_status']

if __name__ == "__main__":
    main()
    

#!/usr/bin/python

import sys

if sys.version_info < (2, 4):
    print "Your python interpreter is too old. Please consider upgrading."
    sys.exit(1)

import re
import os
import logging
import optparse
import hashlib
import datetime
import time
import commands
import uuid
from subprocess import *


time_format_definition = "%Y-%m-%dT%H:%M:%SZ"
log = logging.getLogger("OpenNebula")

def run_cmd(cmd):
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return output


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")


command = "ls"
print "Running VMpublisher..."

VM_NAME = "test11_marketplace_SL6"
IMAGE_NAME = "VMpublisher-UI"


#command = "onetemplate instantiate 165 -n " + VM_NAME
log.info("Running VM instantiation: "+command)
os.system(command)

print "Generating new image into datastore..."
#command = "onevm saveas " + VM_NAME + " 0 " + IMAGE_NAME
log.info("VM image backup: "+command)
os.system(command)

if query_yes_no("Have you received ON email notification?") == True:
	print "Ok, we will continue..."
	print "Shutting down "+ VM_NAME
	#command = "onevm shutdown " + VM_NAME
	log.info("Shutting down VM image: "+command)
	os.system(command)
	print "Please wait, this will take some time..."


	while True:
		command = "oneimage show " + IMAGE_NAME + "|grep STATE|awk '{print $3}'"
		IMAGE_STATUS = run_cmd(command).strip()
		if IMAGE_STATUS == 'rdy':
			print "Image ready from datastore. Image status: " + IMAGE_STATUS
			log.info("VM image is available from repository: "+command)
			command = "oneimage show " + IMAGE_NAME + "|grep SOURCE|awk '{print $3}'"
			IMAGE_SOURCE = run_cmd(command).strip()
			print "This is the image source path: " + IMAGE_SOURCE 
			break
		else:
			print "Not available yet. Image status: " + IMAGE_STATUS 
			time.sleep(30)

	# VMcaster: publishing new SA2 VM image
	# Create a new random UUID for thie image 
	IMAGE_UUID = str(uuid.uuid4())
	print "This is the new image UUID: " + IMAGE_UUID

	# DEBUG: UUID hardcoded
	IMAGE_UUID = "e7782819-da91-489b-b9ec-81a6732ec426"

	# Generate VMcaster template for the new image
	command = "vmcaster --select-image " + IMAGE_UUID + " --add-image_list_template"
	log.info("Generating new image template into image list: "+command)
	os.system(command)

	# DEBUG: VMcaster fields (hardcoded)
	IMAGE_DESCRIPTION = "UI-UMD3.0.0"
	IMAGE_TITLE = "EMI-UI"
	IMAGE_HYPERVISOR = "QEMU,KVM"
	IMAGE_FORMAT = "QCOW2"
	IMAGE_COMMENTS = "UMD3 testing image. login:root pass:umdtest"
	IMAGE_ARCH = "x86_64"
	IMAGE_OS = "Linux"
	IMAGE_OSVERSION = "Scientific Linux release 6.4 (Carbon)"
	# CESGA internal image list
	IMAGE_LIST = "2204eed5-f37e-45b9-82c6-85697356109c"

	# Add the new template to CESGA image list
	command = "vmcaster --select-imagelist " + IMAGE_LIST + " --imagelist-add-image --select-image " + IMAGE_UUID
	log.info("Including the new image into internal image list: "+command)
	os.system(command)

	# Filling image fields
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "dc:description"  --key-value-image' + IMAGE_DESCRIPTION
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "dc:title"  --key-value-image ' + IMAGE_TITLE 
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "hv:hypervisor"  --key-value-image ' + IMAGE_HYPERVISOR
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "hv:format"  --key-value-image ' + IMAGE_FORMAT 
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "sl:comments"  --key-value-image ' + IMAGE_COMMENTS
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "sl:arch"  --key-value-image ' + IMAGE_ARCH
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "sl:os"  --key-value-image ' + IMAGE_OS
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "sl:osversion"  --key-value-image ' + IMAGE_OSVERSION
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "hv:uri"  --key-value-image "http://cloud.cesga.es/images/test.qcow2"'
	os.system(command)


	# Upload the new image from ON datastore to web service
	command = 'vmcaster --upload-image ' + IMAGE_SOURCE + ' --select-image ' + IMAGE_UUID + ' --verbose --verbose'
	print "Uploading the new image to web service. Please wait..."
	log.info("Uploading new image to cloud.cesga.es web service: "+command)
	os.system(command)

	# Publish the new image list
	#command = 'vmcaster --select-imagelist ' + IMAGE_LIST + ' --upload-imagelist'
	#os.system(command)
	
else:
	print "Removing temp file image and VM..."
	print "See ya"
        sys.exit(1)

print "This is the end my only friend, the end..."

#!/usr/bin/python

import sys
import getopt

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
from xml.dom.minidom import parseString


time_format_definition = "%Y-%m-%dT%H:%M:%SZ"
log = logging.getLogger("VMpublisher")
hdlr = logging.FileHandler('/tmp/VMpublisher.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
#log.setLevel(logging.WARNING)


# DEBUG: Use a predefined ON OS template
IMAGE_HYPERVISOR = "QEMU,KVM"
IMAGE_COMMENTS = "UMD testing image. login:root pass:umdtest"
IMAGE_ARCH = "x86_64"
IMAGE_OS = "Linux"
IMAGE_OSVERSION = "Scientific Linux release 6.4 (Carbon)"
VM_NAME = ''
IMAGE_LIST = ''
IMAGE_NAME = ''
IMAGE_TITLE = ''
IMAGE_DESCRIPTION = ''
IMAGE_FORMAT = ''




def main(argv):
   global VM_NAME
   global IMAGE_LIST
   if not argv or len(sys.argv) < 2:
      print 'ERROR: unhandled option'
      print 'USAGE: vmpublisher.py -i <image list ID> -t <OpenNebula OS template>'
      print 'Example: vmpublisher.py --image-list 2204eed5-f37e-45b9-82c6-85697356109c --on-template test11.egi.cesga.es_market'
      sys.exit(2)
   try:
      opts, args = getopt.getopt(argv,'hi:t:',['help','image-list=','on-template='])
   except getopt.GetoptError:
      print 'vmpublisher.py -i <image list ID> -t <OpenNebula OS template>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h','--help'):
         print 'vmpublisher.py -i <image list ID> -t <OpenNebula OS template>'
         sys.exit()
      elif opt in ("-i", "--image-list"):
         IMAGE_LIST = arg
      elif opt in ("-t", "--on-template"):
         VM_NAME = arg


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

def xml_on_parse(tagname,VM_NAME):
	# Getting templates values from ON xml
	command = "onetemplate show " + VM_NAME + " -x"
	template_xml = run_cmd(command)
	dom = parseString(template_xml)

	#retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
	xmlTag = dom.getElementsByTagName(tagname)[0].toxml()
	#strip off the tag (<tag>data</tag>  --->   data):
	xmlData=xmlTag.replace('<'+tagname+'><![CDATA[','').replace(']]></'+tagname+'>','')
	data  = xmlData.upper()
	return data


if __name__ == "__main__":
	main(sys.argv[1:])

command = "ls"
print 'Running VMpublisher...'

IMAGE_TITLE = xml_on_parse("PRODUCT",VM_NAME)
IMAGE_NAME = "VMpublisher-" + IMAGE_TITLE
IMAGE_DESCRIPTION = IMAGE_TITLE + "-UMD-" + xml_on_parse("VERSION",VM_NAME)
IMAGE_FORMAT = xml_on_parse("DRIVER",VM_NAME)


command = "onetemplate instantiate " + VM_NAME + " -n " + VM_NAME
log.info("Running VM instantiation: "+command)
os.system(command)

print "Generating new image into datastore..."
command = "onevm saveas " + VM_NAME + " 0 " + IMAGE_NAME
log.info("VM image backup: "+command)
os.system(command)



if query_yes_no("Have you received ON email notification?") == True:
	print "Ok, we will continue..."
	print ('Shutting down {0}'.format(VM_NAME))
	command = "onevm shutdown " + VM_NAME
	log.info("Shutting down VM image: "+command)
	os.system(command)
	print "Please wait, this will take some time..."


	while True:
		command = "oneimage show " + IMAGE_NAME + "|grep STATE|awk '{print $3}'"
		IMAGE_STATUS = run_cmd(command).strip()
		if IMAGE_STATUS == 'rdy':
			print ('Image ready from datastore. Image status: {0}'.format(IMAGE_STATUS))
			log.info("VM image is available from repository: "+command)
			command = "oneimage show " + IMAGE_NAME + "|grep SOURCE|awk '{print $3}'"
			IMAGE_SOURCE = run_cmd(command).strip()
			print ('This is the image source path: {0}'.format(IMAGE_SOURCE))
			break
		else:
			print ('Not available yet. Image status: {0}'.format(IMAGE_STATUS))
			time.sleep(30)

	# VMcaster: publishing new SA2 VM image
	# Create a new random UUID for thie image 
	IMAGE_UUID = str(uuid.uuid4())
	print ('This is the new image UUID:{0} '.format(IMAGE_UUID))


	# Generate VMcaster template for the new image
	command = "vmcaster --select-image " + IMAGE_UUID + " --add-image"
	log.info("Generating new image template into image list: "+command)
	os.system(command)


	# Add the new template to CESGA image list
	command = "vmcaster --select-imagelist " + IMAGE_LIST + " --imagelist-add-image --select-image " + IMAGE_UUID
	log.info("Including the new image into internal image list: "+command)
	os.system(command)

	# Filling image fields
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "dc:description"  --key-value-image "' + IMAGE_DESCRIPTION + '"'
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "dc:title"  --key-value-image "' + IMAGE_TITLE + '"'
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "hv:hypervisor"  --key-value-image "' + IMAGE_HYPERVISOR + '"'
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "hv:format"  --key-value-image "' + IMAGE_FORMAT + '"'
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "sl:comments"  --key-value-image "' + IMAGE_COMMENTS + '"'
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "sl:arch"  --key-value-image "' + IMAGE_ARCH + '"'
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "sl:os"  --key-value-image "' + IMAGE_OS + '"'
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "sl:osversion"  --key-value-image "' + IMAGE_OSVERSION + '"'
	os.system(command)
	command = 'vmcaster --select-image ' + IMAGE_UUID + ' --key-set-image "hv:uri"  --key-value-image "http://cloud.cesga.es/images/test.qcow2"'
	os.system(command)
	log.info("Filling image list fields...")


	# Upload the new image from ON datastore to web service
	#command = 'vmcaster --upload-image ' + IMAGE_SOURCE + ' --select-image ' + IMAGE_UUID + ' --verbose --verbose'
	command = 'vmcaster --upload-image ' + IMAGE_SOURCE + ' --select-image ' + IMAGE_UUID
	print "Uploading the new image to web service. This will take a while please wait..."
	log.info("Uploading new image to cloud.cesga.es web service: "+command)
	if os.system(command) != 0:
    		print "Error uploading ON image!"
		log.error("IMAGE UPLOAD ERROR: "+command)
		sys.exit(1)
	else:
		command = "oneimage delete " + IMAGE_NAME
		print ('Removin ON image {0} from datastore'.format(IMAGE_NAME))
		os.system(command)

	# Publish the new image list
	command = 'vmcaster --select-imagelist ' + IMAGE_LIST + ' --upload-imagelist'
	print 'Uploading the new image list version to cloud.cesga.es...'
	log.info("Uploading image list to cloud.cesga.es: "+command)
	os.system(command)
	
else:
	print "Removing temp file image and VM..."
	print "See ya"
	log.info("Exiting....")
        sys.exit(1)

print "This is the end my only friend, the end..."

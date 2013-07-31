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
command = "onetemplate instantiate 165 -n " + VM_NAME
log.info("Running VM instantiation: "+command)
os.system(command)

print "Generating new image into datastore..."
command = "onevm saveas " + VM_NAME + " 0 " + IMAGE_NAME
log.info("VM image backup: "+command)
os.system(command)

if query_yes_no("Have you received ON email notification?") == True:
	print "Ok, we will continue..."
	print "Shutting down "+ VM_NAME
	command = "onevm shutdown " + VM_NAME
	log.info("Shutting down VM image: "+command)
	os.system(command)
	print "Please wait, this will take some time..."
	command = "oneimage show " + IMAGE_NAME + "|grep STATE|awk '{print $3}'"
	image_status = "lock"
	while image_status != "rdy":
		image_status = run_cmd(command)
		time.sleep(60)
	print "DONE! the final status: " + image_status
	
else:
	print "See ya"
        sys.exit(1)

print "Done"

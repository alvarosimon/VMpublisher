VMpublisher
===========

_SA2.3 VM publisher script allows to publish OpenNebula VM images into VMcaster virtual machines image lists._
_This script it's used by EGI SA2.3 team to publish new software after UMD verification process._

* SA2.3 Verification wiki page -- https://wiki.egi.eu/wiki/EGI_Quality_Criteria_Verification
* EGI UMD repository -- http://repository.egi.eu/

Requirements
------------

* OpenNebula 3.x
* VMcaster (https://github.com/hepix-virtualisation/vmcaster)
* Python 2.4

### Examples
To publish OpenNebula VM template myVM into Image List UUID 2204eed5-f37e-45b9-82c6-85697356109c
~~~
vmpublisher.py --image-list 2204eed5-f37e-45b9-82c6-85697356109c --on-template myVM
~~~





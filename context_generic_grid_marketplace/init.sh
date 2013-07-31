#!/bin/bash
 
LOGFILE=/tmp/log_boot
touch $LOGFILE

if [ -f /mnt/context.sh ]; then
  . /mnt/context.sh

	echo "Running contextualization script"
	date

 
	# Network configuration
	hostname $HOSTNAME
	ifconfig eth0 $IP_PUBLIC netmask $NETMASK
	route add default gw $GATEWAY


mount -a

## root SSH keys
# cp /mnt/authorized_keys /root/.ssh/

# if [ -n "$SSH_PUB" ]; then
#         echo $SSH_PUB >> /root/.ssh/authorized_keys
# fi


## Setting  iptables
 mv /etc/sysconfig/iptables /root/iptables.orig
 cp /mnt/iptables /etc/sysconfig/iptables
 chmod 600 /etc/sysconfig/iptables
 service iptables restart


## grid configuration templates
 cp -aprx /mnt/configuration_templates /root
 chown -R root.root /root/configuration_templates

## Configure UMD testing repo
wget -O /etc/yum.repos.d/umdtest.repo $UMDREPO

rm -rf /root/.bash_history
rm -rf /var/log/yum.log

/etc/init.d/ntpd stop 
/etc/init.d/ntpd stop 
/etc/init.d/ntpd stop 
/usr/sbin/ntpdate ntpdate hora.rediris.es 
/usr/sbin/ntpdate ntpdate hora.rediris.es 
/usr/sbin/ntpdate ntpdate hora.rediris.es 
/etc/init.d/ntpd start

#newpswd=`cat /dev/urandom | tr -dc "a-zA-Z0-9-_\$\?" | head -c 8`
newpswd="umdtest"
passwd root <<EOF
$newpswd
$newpswd
EOF

## Install product
yum clean all
yum update -y
yum -y install $PRODUCT

	if [[ $? -eq 0  ]] ; then
        	echo "$PRODUCT installation finished correctly and ready to be published."|mail -s"Installation Finished: $PRODUCT" $MAIL
        	yum clean all
	else
        	echo "$PRODUCT ERROR. Please check log files."|mail -s"Installation ERROR: $PRODUCT" $MAIL
	fi

# Configuration
if [ "$PRODUCT" == "emi-ui" ]
then
	/opt/glite/yaim/bin/yaim -c -s /root/configuration_templates/EMI/UI/site-info.def -n UI
	echo "$PRODUCT Configuration finished."|mail -s"Configuration Finished: $PRODUCT" $MAIL
fi



fi #main if

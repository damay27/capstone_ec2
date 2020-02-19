#!/bin/bash

#Install the qemu tools
apt install qemu-guest-agent

#Make sure new ssh keys are generated
apt purge openssh-server
apt install openssh-server

#Generate a new pair of ssh keys
ssh-keygen

#Uninstall the qemu tools
apt purge qemu-guest-agent



import getpass
import logging
import json

import proxmox_api

HOSTNAME = "128.4.26.241"

# def make_new_vm(proxmox, node_name, vm_type, vm_password, vm_name):

    #Clone vm from template

    #Run vm setup script

    #Set vm password

    #Get ssh fingerprint

    #Get ssh private key

    # next_id = proxmox.get_next_vm_id()

    # if vm_type == "York":
    #     proxmox.clone_vm(node_name, 300, next_id)
    # elif vm_type == "Carolina":
    #     proxmox.clone_vm(node_name, 300, next_id)
    # elif vm_type == "Tex":
    #     proxmox.clone_vm(node_name, 300, next_id)



#Configuration file with information about the cluster
config_json = None

def main():

    logging.basicConfig(filename="/var/log/managment_server.log")

    #Setup the proxmox api object and get the user to sign in
    proxmox = proxmox_api.ProxmoxAPI(HOSTNAME, False)

    print("Starting test...")
    print("Enter username: ", end="")
    username = input()

    password = getpass.getpass()

    if not proxmox.get_cookies(username, password):
        print("Could not get cookies for proxmox....")
        logging.error("Proxmox sign in failed")
        exit(-1)

    username = None
    password = None

    #Load the configuration file
    try:
        config_file = open("./config.json", "r")
    except:
        print("Could no open configuration file")
        logging.error("Could no open configuration file")
        exit(-1)

    config_json = json.load(config_file)
    config_file.close()





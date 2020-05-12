import proxmox_api
import time
import paramiko
import json
import pexpect
# import subprocess
# from subprocess import Popen, PIPE, check_call


def vm_copy_and_setup(public_key, proxmox, vm_id):

    proxmox.clone_vm("pve", 102, vm_id)

    ready = False
    #Wait until the vm is done cloning before continuing
    while(not ready):
        data = proxmox.get_vm_status("pve", vm_id)
        if data is not None:
            data = data["data"]
            if "lock" in data:
                ready = True
        time.sleep(20)
    
    #standard login info for the vm template
    username = "test"
    password = b"testpassword"

    time.sleep(150)
    ready = False
    proxmox.start_vm("pve", vm_id)

    while(not ready):
        proxmox.start_vm("pve", vm_id)
        data = proxmox.get_vm_status("pve", vm_id)
        if data is not None and data["data"] is not None:
            data = data["data"]
            if data["status"] == "running":
                ready = True
        time.sleep(20)

    vm_ip = proxmox.get_vm_ip_addr("pve", vm_id)
    while vm_ip == False:
        time.sleep(10)
        vm_ip = proxmox.get_vm_ip_addr("pve", vm_id)

    time.sleep(100)

    ssh_session = paramiko.SSHClient()
    ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_session.connect(vm_ip, username=username, password=password)

    ready = False
    while(not ready):
        ssh_session.connect(vm_ip, username=username, password=password)
        time.sleep(20)

        if ssh_session.get_transport() is not None:
            if ssh_session.get_transport().is_active():
                ready = True


    ssh_session.exec_command("mkdir -p ~/.ssh/")
    ssh_session.exec_command("chown -R test:test .ssh")


    key_file = open("authorized_keys", "w")
    key_file.write(public_key)
    key_file.close()

    #Copy ssh key
    p = pexpect.spawn("scp -o StrictHostKeyChecking=no authorized_keys test@%s:/home/test/.ssh/authorized_keys"%vm_ip)
    p.expect("test@.*'s password:.*")
    p.sendline(password)
    time.sleep(10)
    p.close()

    ssh_session.exec_command("sudo sed -i -e 's/PasswordAuthentication yes/PasswordAuthentication no/g' /etc/ssh/sshd_config")

    ssh_session.close()

    #Switch to the external internet facing network
    proxmox.change_network("pve", vm_id, "vmbr0")

    time.sleep(30)
    proxmox.stop_vm("pve", vm_id)

    while proxmox.get_vm_status("pve", vm_id)["data"]["status"] != "stopped":
        time.sleep(10)

    proxmox.start_vm("pve", vm_id)


def get_info(proxmox, vm_id):
    
    vm_status = ""
    status_data = proxmox.get_vm_status("pve", vm_id)
    if "data" in status_data:
        if "status" in status_data["data"]:
            vm_status = status_data["data"]["status"]

    vm_ip = proxmox.get_vm_ip_addr("pve", vm_id)

    if vm_ip == False:
        return False
    else:
        data = {"status" : vm_status, "ip" : vm_ip}
        return json.dumps(data)


def delete_vm(proxmox, vm_id):

    proxmox.stop_vm("pve", vm_id)

    while proxmox.get_vm_status("pve", vm_id)["data"]["status"] != "stopped":
        time.sleep(10)

    return proxmox.delete_vm("pve", vm_id)



import proxmox_api
import time
import paramiko
import json


def vm_copy_and_setup(public_key, proxmox, vm_id):

    proxmox.clone_vm("pve", 101, vm_id)

    #Wait until the vm is done cloning before continuing
    while("lock" in proxmox.get_vm_status("pve", vm_id)["data"]):
        print("x")
        time.sleep(20)
    proxmox.start_vm("pve", vm_id)

    #standard login info for the vm template
    username = "test"
    password = "testpassword"

    time.sleep(120)

    # ready = False
    # while(not ready):
    #     time.sleep(20)
    #     data = proxmox.get_vm_status("pve", vm_id)["data"]
    #     if "status" in data and data["status"] == "running"
    # proxmox.start_vm("pve", vm_id)

    vm_ip = proxmox.get_vm_ip_addr("pve", vm_id)
    print("ip: %s" % vm_ip)

    ssh_session = paramiko.SSHClient()
    ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_session.connect(vm_ip, username=username, password=password)
    print("777777777777777777777777777777777777")

    ready = False
    while(not ready):
        ssh_session.connect(vm_ip, username=username, password=password)
        time.sleep(20)
        print("*")

        if ssh_session.get_transport() is not None:
            print("@")
            if ssh_session.get_transport().is_active():
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                ready = True
    print("3333333333333333333333333333333333333333")


    script = '''mkdir -p ~/.ssh/ \ntouch -p ~/.ssh/authorized_keys \necho "%s" > ~/.ssh/authorized_keys \napt purge -y openssh-server \napt install -y openssh-server \nsed -i -e 's/PasswordAuthentication yes/PasswordAuthentication no/g' /etc/ssh/sshd_config'''

    script_inst = script % (public_key)
    print(script_inst)
    ssh_session.exec_command("printf '%s' > script.sh; chmod +x script.sh" % script_inst)
    ssh_session.exec_command("sudo ./script.sh")
    ssh_session.exec_command("sudo rm script.sh")
    print("here")

    #Add the key to the authormized keys file
    # stdin, stdout, stderr = ssh_session.exec_command("mkdir -p ~/.ssh/")
    # print(stderr.read())
    # print("-------------------------------------------")
    # print(stdout.read())
    # stdin, stdout, stderr = ssh_session.exec_command("touch -p ~/.ssh/authorized_keys")
    # print(stderr.read())
    # print("-------------------------------------------")
    # print(stdout.read())
    # stdin, stdout, stderr = ssh_session.exec_command("touch -p ~/AAABBBCCCXXX")
    # print(stderr.read())
    # print("-------------------------------------------")
    # print(stdout.read())
    # stdin, stdout, stderr = ssh_session.exec_command("echo '%s' > ~/.ssh/authorized_keys" % public_key)
    # print(stderr.read())
    # print("-------------------------------------------")
    # print(stdout.read())

    # #Re-install openssh so that a new fingerprint will be generated
    # stdin, stdout, stderr = ssh_session.exec_command("sudo -S apt purge openssh-server")
    # stdin.write(password+'\n')
    # print(stderr.read())
    # print("-------------------------------------------")
    # print(stdout.read())

    # stdin, stdout, stderr = ssh_session.exec_command("sudo -S apt install openssh-server")
    # stdin.write(password+'\n')
    # print(stderr.read())
    # print("-------------------------------------------")
    # print(stdout.read())

    # #Change the password
    # stdin, stdout, stderr = ssh_session.exec_command("sudo -S passwd test")
    # stdin.write(password+'\n'+new_password+'\n'+new_password+'\n')
    # print(stderr.read())
    # print("-------------------------------------------")
    # print(stdout.read())

    ssh_session.close()

    #Switch to the external internet facing network
    proxmox.change_network("pve", vm_id, "vmbr0")

    time.sleep(30)
    proxmox.stop_vm("pve", vm_id)

    while proxmox.get_vm_status("pve", vm_id)["data"]["status"] != "stopped":
        time.sleep(10)

    proxmox.start_vm("pve", vm_id)

    print("done")


def get_info(proxmox, vm_id):
    
    vm_status = ""
    status_data = proxmox.get_vm_status("pve", vm_id)
    if "data" in status_data:
        if "status" in status_data["data"]:
            vm_status = status_data["data"]["status"]

    vm_ip = proxmox.get_vm_ip_addr("pve", vm_id)

    data = {"status" : vm_status, "ip" : vm_ip}

    return json.dumps(data)


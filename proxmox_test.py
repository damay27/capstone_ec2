
import getpass
import proxmox_api
import time
import paramiko
# password = ""

# resp = requests.post(url = "https://192.168.150.138:8006/api2/json/access/ticket", data="username=root@pam&password="+password, verify = False)
# jsonResp = json.loads(resp.text)
# cookies = {"PVEAuthCookie" : jsonResp["data"]["ticket"]}
# ticket = {"CSRFPreventionToken" : jsonResp["data"]["CSRFPreventionToken"]}
# print(cookies)
# resp = requests.post("https://192.168.150.138:8006/api2/json/nodes/pve/qemu/100/status/start", cookies = cookies, headers = ticket, verify = False)
# print(resp)

proxmox_ip = "192.168.254.137"
proxmox_user = "root"
proxmox_password = "ZAQ!2wsx"



p = proxmox_api.ProxmoxAPI(proxmox_ip, False)
if not p.get_cookies(proxmox_user, proxmox_password):
    print("Could not get cookies for proxmox....")
    exit(-1)

# p = proxmox_api.ProxmoxAPI("128.4.26.241", False)
# print("Starting test...")
# print("Enter username: ", end="")
# username = input()
# # print("Enter password: ", end="")
# password = getpass.getpass()

# if not p.get_cookies(username, password):
#     print("Could not get cookies for proxmox....")
#     exit(-1)

# username = None
# password = None

#NOTE:Fix return types in the api

# print(p.start_vm("pve", 101))
# print("clone")
# print(p.clone_vm("cluster", 100, 700).content)
# print(p.stop_vm("cluster", 100))

# p.get_network_info("cluster", 300)
# p.run_command("cluster", 300, "/opt/setup/vm_setup.sh")

# print(p.get_vm_ip_addr("pve", 101))

# print(p.get_next_vm_id())

def vm_copy_setup(new_password, public_key, proxmox, vm_id):

    proxmox.clone_vm("pve", 101, vm_id)

    #Wait until the vm is done cloning before continuing
    while("lock" in proxmox.get_vm_status("pve", vm_id)["data"]):
        time.sleep(20)
        print("*")
    proxmox.start_vm("pve", vm_id)

    #standard login info for the vm template
    username = "test"
    password = "testpassword"

    time.sleep(120)

    vm_ip = proxmox.get_vm_ip_addr("pve", vm_id)
    print("ip: %s" % vm_ip)

    ssh_session = paramiko.SSHClient()
    ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_session.connect(vm_ip, username=username, password=password)

    ssh_session.exec_command("mkdir -p ~/.ssh/")
    ssh_session.exec_command("touch -p ~/.ssh/authorized_keys")
    ssh_session.exec_command("echo '%s' > ~/.ssh/authorized_keys" % public_key)
    stdin, stdout, stderr = ssh_session.exec_command("sudo -S apt purge openssh-server")
    stdin.write(password+'\n')
    # print(stdout.readlines())
    # print(stderr.readlines())
    stdin, stdout, stderr = ssh_session.exec_command("sudo -S apt install openssh-server")
    stdin.write(password+'\n')
    # print(stdout.readlines())
    # print(stderr.readlines())

    stdin, stdout, stderr = ssh_session.exec_command("sudo -S passwd test")
    stdin.write(password+'\n'+new_password+'\n'+new_password+'\n')
    print(stdout.readlines())
    print(stderr.readlines())


    # ssh_session.exec_command("chmod +x setup.sh")
    # ssh_session.exec_command("printf '%s' | sudo -S ./setup.sh" % password)
    # ssh_session.exec_command("rm setup.sh")

    #Switch to the external internet facing network
    proxmox.change_network("pve", vm_id, "vmbr2")


# p.change_network("pve", 700, "vmbr2")
# print(p.get_vm_status("pve", 700))
vm_copy_setup("capstone", "public key blah blah blah", p, 700)
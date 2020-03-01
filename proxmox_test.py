
import getpass
import proxmox_api
# password = ""

# resp = requests.post(url = "https://192.168.150.138:8006/api2/json/access/ticket", data="username=root@pam&password="+password, verify = False)
# jsonResp = json.loads(resp.text)
# cookies = {"PVEAuthCookie" : jsonResp["data"]["ticket"]}
# ticket = {"CSRFPreventionToken" : jsonResp["data"]["CSRFPreventionToken"]}
# print(cookies)
# resp = requests.post("https://192.168.150.138:8006/api2/json/nodes/pve/qemu/100/status/start", cookies = cookies, headers = ticket, verify = False)
# print(resp)


p = proxmox_api.ProxmoxAPI("128.4.26.241", False)

print("Starting test...")
print("Enter username: ", end="")
username = input()
# print("Enter password: ", end="")
password = getpass.getpass()

if not p.get_cookies(username, password):
    print("Could not get cookies for proxmox....")
    exit(-1)

username = None
password = None

#NOTE:Fix return types in the api

# print(p.start_vm("cluster", 100))
# print("clone")
# print(p.clone_vm("cluster", 100, 700).content)
# print(p.stop_vm("cluster", 100))

# p.get_network_info("cluster", 300)
# p.run_command("cluster", 300, "/opt/setup/vm_setup.sh")

# print(p.get_vm_ip_addr("cluster", 300))

# print(p.get_next_vm_id())

p.read_file_on_vm("cluster", 101, "/home/user/test.txt")


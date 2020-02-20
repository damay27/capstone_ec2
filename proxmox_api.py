import requests
import json
import logging

class ProxmoxAPI(object):

    def __init__(self, hostname, ssl = True, log_file_path = "./ProxmoxAPI.log"):

        logging.basicConfig(filename=log_file_path)

        self._hostname = hostname
        self._verify_ssl = ssl

        self._PVEAuthCookie = None
        self._CSRFPreventionToken = None



    def get_cookies(self, username, password):
        '''
        Connects to proxmox server and obtains the cookies and tokens needed
        to connect in the future.
        username : The username needed to login to proxmox. Type String.
        password : The password needed to login to proxmox. Type String.
        '''
        url = "https://"+self._hostname+":8006/api2/json/access/ticket"
        data = "username="+username+"@pam&password="+password
        response = requests.post(url = url, data=data, verify = self._verify_ssl)
        jsonResponse = json.loads(response.text)

        try:
            self._PVEAuthCookie = {"PVEAuthCookie" : jsonResponse["data"]["ticket"]}
            self._CSRFPreventionToken = {"CSRFPreventionToken" : jsonResponse["data"]["CSRFPreventionToken"]}
        except KeyError:
            return False

        return True

    
    def start_vm(self, node_name, vm_id):
        '''
        Starts a vm on the cluster
        node_name : Name of  the node to start the vm on.
        vm_id : ID number of the vm to be started.
        '''
        url = "https://"+self._hostname+":8006/api2/extjs/nodes/"+node_name+"/qemu/"+str(vm_id)+"/status/start"
        resp = requests.post(url, cookies = self._PVEAuthCookie, headers = self._CSRFPreventionToken, verify = self._verify_ssl)
        
        if resp.ok:
            return True
        else:
            msg = "stop_vm: %s\n%s" % (resp, resp.content)
            logging.error(msg)
            return False


    def stop_vm(self, node_name, vm_id):
        '''
        Stops a vm on the cluster
        node_name : Name of  the node to stop the vm on.
        vm_id : ID number of the vm to be stopped.
        '''
        url = "https://"+self._hostname+":8006/api2/extjs/nodes/"+node_name+"/qemu/"+str(vm_id)+"/status/stop"
        resp = requests.post(url, cookies = self._PVEAuthCookie, headers = self._CSRFPreventionToken, verify = self._verify_ssl)

        if resp.ok:
            return True
        else:
            msg = "stop_vm: %s\n%s" % (resp, resp.content)
            logging.error(msg)
            return False  


    def clone_vm(self, node_name, vm_id, clone_id):
        '''
        Clone an existing vm on the cluster
        node_name : Name of  the node to start the vm on.
        vm_id : ID number of the vm to be started.
        clone_id : The ID number that the new vm will have.
        '''
        url = "https://"+self._hostname+":8006/api2/extjs/nodes/"+node_name+"/qemu/"+str(vm_id)+"/clone"
        data = {"newid" : clone_id, "full" : 1}

        resp = requests.post(url, cookies = self._PVEAuthCookie, headers = self._CSRFPreventionToken, verify = self._verify_ssl, data = data)
        
        if resp.ok:
            return True
        else:
            msg = "stop_vm: %s\n%s" % (resp, resp.content)
            logging.error(msg)
            return False


    def get_vm_config(self, node_name, vm_id):
        '''
        Gets the configuration info about a VM.
        node_name : Name of the node in the cluster that the VM is on. String.
        vm_id : The id of the VM being used. int.
        Returns : json structure containing configuration data. On failure returns None
        '''

        url = "https://%s:8006/api2/extjs/nodes/%s/qemu/%d/config" % (self._hostname, node_name, vm_id)
        resp = requests.get(url, cookies = self._PVEAuthCookie, headers = self._CSRFPreventionToken, verify = self._verify_ssl)

        if resp.ok:
            return resp.content
        else:
            msg = "get_vm_config: %s\n%s" % (resp, resp.content)
            logging.error(msg)
            return None


    def get_vm_mac_addr(self, node_name, vm_id):
        '''
        Uses the get_vm_config function to retreive the VM's MAC address
        node_name : Name of the node in the cluster that the VM is on. String.
        vm_id : The id of the VM being used. int.
        Returns : MAC address string on success. None otherwise.
        '''
        vm_config = self.get_vm_config(node_name, vm_id)
        if vm_config is None:
            return None

        vm_config = json.loads(vm_config)

        network_string = vm_config["data"]["net0"]
        mac_addr = network_string.split(",")[0]
        mac_addr = mac_addr.split("=")[1]

        return mac_addr

    
    def get_vm_ip_addr(self, node_name, vm_id):
        '''
        Returns the ip address of the VM.
        node_name : Name of the node in the cluster that the VM is on. String.
        vm_id : The id of the VM being used. int.
        Returns : IP address as a String. If an IP address cannot be found returns False
        '''
        
        #Get all the network info about the VM
        network_info = self.get_network_info(node_name, vm_id)
        ip_addrs = network_info["data"]["result"]

        #Get the MAC address of the VM
        mac_addr = self.get_vm_mac_addr(node_name, vm_id)
        mac_addr = mac_addr.lower()

        #Parse out the IP address
        for addr in ip_addrs:
            
            #Find the entry that matches the VM's MAC address
            if addr["hardware-address"] == mac_addr:
                ip = addr["ip-addresses"][0]["ip-address"]
                return ip

        return False


    def toggle_vm_agent(self, node_name, vm_id, agent_active):
        '''
        Allows you to turn on or off the VM's QEMU agent.
        node_name : Name of the node in the cluster that the VM is on. String.
        vm_id : The id of the VM being used. int.
        agent_active : True to turn the agent on and False to turn int off. bool.
        '''

        url = "https://%s:8006/api2/json/nodes/%s/qemu/%d/config" % (self._hostname, node_name, vm_id)

        data = {"agent" : int(agent_active)}

        resp = requests.post(url, cookies = self._PVEAuthCookie, headers = self._CSRFPreventionToken, data = data, verify = self._verify_ssl)

        if resp.ok:
            return True

    def get_network_info(self, node_name, vm_id):
        '''
        Gets the network a vm on the cluster
        node_name : Name of  the node to stop the vm on.
        vm_id : ID number of the vm to be stopped.
        Returns : The netowrk info as a json object on success. False otherwise.
        '''

        url = "https://"+self._hostname+":8006/api2/extjs/nodes/"+node_name+"/qemu/"+str(vm_id)+"/agent/network-get-interfaces"
        resp = requests.get(url, cookies = self._PVEAuthCookie, headers = self._CSRFPreventionToken, verify = self._verify_ssl)

        if not resp.ok:
            msg = "get_network_info: %s\n%s" % (resp, resp.content)
            logging.error(msg)
            return False
        else:
            return json.loads(resp.text)


    def run_command(self, node_name, vm_id, command):
        '''
        Runs the given command on the VM.
        node_name : Name of  the node to stop the vm on.
        vm_id : ID number of the vm to be stopped.
        command : The command or path to the command to be run.
        Retunrs : True on success. False on failure.
        '''
        url = "https://%s:8006/api2/extjs/nodes/%s/qemu/%d/agent/exec" % (self._hostname, node_name, vm_id)
        
        data = {"command" : command}
        resp = requests.post(url, cookies = self._PVEAuthCookie, headers = self._CSRFPreventionToken, data = data, verify = self._verify_ssl)
    
        if not resp.ok:
            msg = "run_command: %s\n%s" % (resp, resp.content)
            logging.error(msg)
            return False
        else:
            return True
    

    def get_next_vm_id(self):
        '''
        Gets the next unused VM id.
        Returns the VM id on success and False on failure
        '''

        url = "https://%s:8006/api2/extjs/cluster/nextid" % (self._hostname)
        
        resp = requests.get(url, cookies = self._PVEAuthCookie, headers = self._CSRFPreventionToken, verify = self._verify_ssl)

        if not resp.ok:
            msg = "get_next_vm_id: %s\n%s" % (resp, resp.content)
            logging.error(msg)
            return False
        else:
            return json.loads(resp.text)["data"]
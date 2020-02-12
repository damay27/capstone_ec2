import requests
import json
import logging

class ProxmxoAPI(object):

    def __init__(self, hostname, ssl = True):

        logging.basicConfig(filename="/var/log/ProxmoxAPI.log")

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
        
        if not resp.ok:
            msg = "stop_vm: %s\n%s" % (resp, resp.content)
            logging.error(msg)
            return False
        else:
            return True


    def stop_vm(self, node_name, vm_id):
        '''
        Stops a vm on the cluster
        node_name : Name of  the node to stop the vm on.
        vm_id : ID number of the vm to be stopped.
        '''
        url = "https://"+self._hostname+":8006/api2/extjs/nodes/"+node_name+"/qemu/"+str(vm_id)+"/status/stop"
        resp = requests.post(url, cookies = self._PVEAuthCookie, headers = self._CSRFPreventionToken, verify = self._verify_ssl)

        if not resp.ok:
            msg = "stop_vm: %s\n%s" % (resp, resp.content)
            logging.error(msg)
            return False
        else:
            return True  


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
        
        if not resp.ok:
            msg = "stop_vm: %s\n%s" % (resp, resp.content)
            logging.error(msg)
            return False
        else:
            return True

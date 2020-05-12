import proxmox_api
import rpyc
import ec2_functions
import sys
import getpass
import multiprocessing

class EC2Service(rpyc.Service):

    def on_connect(self, conn):
        # code that runs when a connection is created
        # (to init the service, if needed)
        pass

    def on_disconnect(self, conn):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_make_vm_instance(self, public_key):
        global proxmox
        vm_id = proxmox.get_next_vm_id()
        p = multiprocessing.Process( target = ec2_functions.vm_copy_and_setup, args = (public_key, proxmox, vm_id ) )
        p.start()
        # ec2_functions.vm_copy_and_setup(new_password, public_key, proxmox, vm_id )
        return vm_id

    def exposed_get_info(self, vm_id):
        global proxmox
        return ec2_functions.get_info(proxmox, vm_id)

    def exposed_stop_vm(self, vm_id):
        global proxmox
        if proxmox.stop_vm("pve", vm_id) == True:
            return "OK"
        else:
            return "ERROR"

    def exposed_start_vm(self, vm_id):
        global proxmox
        if proxmox.start_vm("pve", vm_id) == True:
            return "OK"
        else:
            return "ERROR"

    def exposed_delete_vm(self, vm_id):
        global proxmox
        if ec2_functions.delete_vm(proxmox, vm_id) == True:
            return "OK"
        else:
            return "ERROR"

proxmox = None

if __name__ == "__main__":

    proxmox_ip = ""

    if len( sys.argv ) < 2:
        print("Must specify host name or IP of the proxmox server...")
        exit(0)
    else:
        proxmox_ip = sys.argv[1]

    proxmox = proxmox_api.ProxmoxAPI(proxmox_ip, False)

    print("The beast slowly wakes up...")

    print("Enter username: ", end="")
    username = input()
    print("Enter password: ", end="")
    password = getpass.getpass()

    if not proxmox.get_cookies(username, password):
        print("Could not get cookies for proxmox....")
        exit(-1)

    username = None
    password = None

    print("")
    print("Starting service...")
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(EC2Service, port=18861)
    t.start()
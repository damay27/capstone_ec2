# import pdb; pdb.set_trace()
import flask
import rpyc

app = flask.Flask("cluster")

@app.route("/create_vm/", methods = ["POST"])
def create_vm():
    if flask.request.method == "POST":
        if "public_key" in flask.request.form:
            service = rpyc.connect("localhost", 18861)
            public_key = flask.request.form["public_key"]
            vm_id = service.root.make_vm_instance(public_key)

            return {"vm_id" : vm_id}
        else:
            return "ERROR"

@app.route("/get_info/", methods = ["POST"])
def get_info():
    if flask.request.method == "POST":
        if "vm_id" in flask.request.form:
            service = rpyc.connect("localhost", 18861)
            vm_id = flask.request.form["vm_id"]
            return service.root.get_info(int(vm_id))
    else:
        return "ERROR"

@app.route("/stop_vm/", methods = ["POST"])
def stop_vm():
    if flask.request.method == "POST":
        if "vm_id" in flask.request.form:
            service = rpyc.connect("localhost", 18861)
            vm_id = flask.request.form["vm_id"]
            return service.root.stop_vm(int(vm_id))
    else:
        return "ERROR"

@app.route("/start_vm/", methods = ["POST"])
def start_vm():
    if flask.request.method == "POST":
        if "vm_id" in flask.request.form:
            service = rpyc.connect("localhost", 18861)
            vm_id = flask.request.form["vm_id"]
            return service.root.start_vm(int(vm_id))
    else:
        return "ERROR"



if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.run(host='0.0.0.0')
from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit 
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
sio = SocketIO(app)

run_stop_nginx = """echo vagrant | sudo -S ./stop_nginx.sh """
run_start_nginx = """echo vagrant | sudo -S ./start_nginx.sh """
run_reload_nginx = """echo vagrant | sudo -S ./reload_nginx.sh """

config_file = "/vagrant/config/nginx.conf"
# config_file = "/home/mint/vagrant_streamer/home_network/config/nginx.conf"
# indent = "            "
 

class Endpoint:
    def __init__(self, index):
        self.index = index
        self.indent = "            " 
        self.name = ""
        self.url = ""
        self.key = ""

    def get_comment(self):
        return f"{self.indent}# Push to: {self.name}\n"

    def get_line(self):
        return f"{self.indent}push {self.url}/{self.key};\n"

def create_endpoint(comment, endpoint):
    with open(config_file, 'r') as file:
        data = file.readlines()

    index = 0
    for i, line in enumerate(data):
        if "# INSERTION POINT" in line:
            index = i-1

    # These are inserted into the file in reverse order      
    #data.insert(index, "\n")
    data.insert(index, endpoint.get_line())
    data.insert(index, endpoint.get_comment())
    data.insert(index, "\n")
  
    with open(config_file, 'w') as file:
        file.writelines(data)

def read_endpoints(config_file):
    """returns a list of endpoint objects parsed from the config file"""
    endpoints = []

    with open(config_file, 'r') as file:
        data = file.readlines()

    for i, line in enumerate(data):
        if "# Push to" in line:
            endpoint = Endpoint(i)
            endpoints.append(endpoint)

    for e in endpoints:
        key = e.index
        e.name = data[key].rsplit(":", 1)[1].strip(" ")
        e.url = data[key+1].rsplit("/", 1)[0].strip(" ")[5:]
        e.key = data[key+1].rsplit("/", 1)[1].strip(" ")[:-2]

    return endpoints

def update_endpoint(config_file, endpoint):
    with open(config_file, 'r') as file:
        data = file.readlines()

    i = int(endpoint.index)
    data[i] = endpoint.get_comment()
    data[i+1] = endpoint.get_line()

    with open(config_file, 'w') as file:
        file.writelines(data)

def delete_endpoint(config_file, index):
    with open(config_file, 'r') as file:
        data = file.readlines()

    i = int(index)
    del data[(i-1):(i+2)]

    with open(config_file, 'w') as file:
        file.writelines(data)

@app.route('/')
def index():
    print("rendering template")
    return render_template('w3-client.html', endpoints = read_endpoints(config_file))

@app.route('/add_endpoint', methods=["POST"])
def create():
    try:
        name = request.form.get("endpoint_name")
        url = request.form.get("endpoint_url") 
        key = request.form.get("endpoint_key")

        endpoint = Endpoint(0)
        endpoint.name = name
        endpoint.url = url
        endpoint.key = key
        create_endpoint(config_file, endpoint)

    except Exception as e:
        print("add_endpoint function failed")
        print(e)
    return redirect("/")

@app.route('/update_endpoint', methods=["POST"])
def update():
    try:
        index = int(request.form.get("endpoint_index"))
        name = request.form.get("endpoint_name")
        url = request.form.get("endpoint_url") 
        key = request.form.get("endpoint_key")

        endpoints = read_endpoints(config_file)

        for idx, elem in enumerate(endpoints):
            if elem.index == index:
                endpoint = endpoints[idx]
                break

        endpoint.name = name
        endpoint.url = url
        endpoint.key = key
        update_endpoint(config_file, endpoint)
    except Exception as e:
        print("update function failed")
        print(e)
    return redirect("/")

@app.route('/delete_endpoint', methods=["POST"])
def delete():
    try:
        index = int(request.form.get("endpoint_index"))
        delete_endpoint(config_file, index)
    except Exception as e:
        print("delete_endpoint function failed")
        print(e)
    return redirect("/")

@sio.on('ui_stop')
def stop_server():
    print("Stopping Server")
    subprocess.Popen(["sh", "-c", run_stop_nginx])

@sio.on('ui_start')
def start_server():
    print("Starting Server")
    subprocess.Popen(["sh", "-c", run_start_nginx])

@sio.on('ui_reload')
def reload_server():
    print("Reloading Server")
    subprocess.Popen(["sh", "-c", run_reload_nginx])

@sio.on('ui_trigger')
def trigger():
    print("trigger received")
    sio.emit('frame', {'count': 1}, broadcast=True)


if __name__ == "__main__":
    print("Starting Flask")
    sio.run(app, host='0.0.0.0', port=8000, debug=True)
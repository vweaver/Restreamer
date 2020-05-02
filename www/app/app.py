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

# untested
def backup_config_file(config_file='/usr/local/nginx/conf', backup_file='/usr/local/nginx/conf.bak'):
    '''Copies config_file to backup_file'''
    print('backing up config file')
    subprocess.run(['sudo', 'cp', config_file, backup_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# untested
def revert_config_file(config_file='/usr/local/nginx/conf', backup_file='/usr/local/nginx/conf.bak'):
    '''Copies backup_file to config_file'''
    print('reverting up config file')
    subprocess.run(['sudo', 'cp', backup_file, config_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# untested
def copy_config_file(source='/vagrant/config/nginx.conf', dest='/usr/local/nginx/conf'):
    '''Copies file from source to destination'''
    print("copying config file")
    try:
        subprocess.run(['sudo', 'cp', '/vagrant/config/nginx.conf', '/usr/local/nginx/conf'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except Exception as e:
        print(e)

#untested
def test_config_file():
    '''Tests the current config file with nginx, returns True if successful, False otherwise'''
    try:
        output = subprocess.run(('sudo /usr/local/nginx/sbin/nginx -t'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode('utf-8')
        if "test is successful" in output:
            print("TEST PASSED")
            return True
        else:
            print("TEST FAILED") 
            return False
    except Exception as e:
        print(e)
        return False

# untested
def activate_config_file():
    print("activating config file")
    '''Activates the current config file with nginx'''
    try:
        output = subprocess.run(('sudo /usr/local/nginx/sbin/nginx -s' 'reload'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode('utf-8')
        print(output)
    except Exception as e:
        print(e)

#untested
def try_new_config_file():
    backup_config_file()
    copy_config_file()

    if test_config_file():
        activate_config_file()
        sio.emit('server_msg', {'status': 'true', 'text': "Endpoints Updated"}, broadcast=True)
    else:
        revert_config_file()
        sio.emit('server_msg', {'status': 'false', 'text': "Invalid Endpoint. Check and try again"}, broadcast=True)

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
        try_new_config_file()

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
        try_new_config_file()
    except Exception as e:
        print("update function failed")
        print(e)
    return redirect("/")

@app.route('/delete_endpoint', methods=["POST"])
def delete():
    try:
        index = int(request.form.get("endpoint_index"))
        delete_endpoint(config_file, index)
        try_new_config_file()
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
    try_new_config_file()


@sio.on('ui_trigger')
def trigger():
    print("trigger received")
    sio.emit('frame', {'count': 1}, broadcast=True)


if __name__ == "__main__":
    print("Starting Flask")
    sio.run(app, host='0.0.0.0', port=8000, debug=True)
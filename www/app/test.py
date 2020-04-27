config_file = "/home/mint/vagrant_streamer/home_network/config/nginx.conf"

class Endpoint:
    def __init__(self, index):
        self.index = index
        self.indent = "			" 
        self.name = ""
        self.url = ""
        self.key = ""

    def get_comment(self):
        return f"{self.indent}# Push to {self.name}"

    def get_line(self):
        return f"{self.indent} push {self.url}/{self.key};"


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
        e.name = data[key].rsplit(" ", 1)[1][:-1]
        e.url = data[key+1].rsplit("/", 1)[0].strip(" ")[5:]
        e.key = data[key+1].rsplit("/", 1)[1].strip(" ")[:-2]

    return endpoints


if __name__ == "__main__":
    endpoints = read_endpoints(config_file)
    for e in endpoints:
        print(e.get_comment())
        print(e.get_line())

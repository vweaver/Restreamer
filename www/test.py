import re

new_ip =  "192.168.1.102" # "10.1.10.234" 
ip_pattern = re.compile( "(\d+.\d+.\d+.\d+)" )

with open("index.html", "r") as file:
    data = file.readlines()

comment = False
for i, line in enumerate(data):
    # discard comments
    if "<!--" in line:
        comment = True  
    if comment:
        if "-->" in line:
            comment = False
            line = line.rsplit("-->")[1]
        else:
            continue

    # update the ip address
    if not comment and "application/x-mpegURL" in line:
        ip = ip_pattern.search(line).group()
        data[i] = line.replace(ip, new_ip)
        break

with open("index.html", 'w') as file:
        file.writelines(data)
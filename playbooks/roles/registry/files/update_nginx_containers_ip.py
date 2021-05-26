#!/usr/bin/env python3
"""
  update_nginx_containers_ip.py
  this script updates nginx configuration with correct container IP address in upstreams
"""

import re
import os
import fileinput
import sys
import docker
from pystemd.systemd1 import Unit

nginx_site_enabled = "/opt/data/nginx/conf/sites-enabled"
if not os.path.isdir(nginx_site_enabled):
  sys.exit(0)

timeout = 5
retries = 5

client = docker.from_env()
ready = False
count = 0
# Loop until client is ready
while count < retries and not ready:
    try:
        client.ping()
        ready = True
        break
    except:
        count += 1
        print("Retrying..." + str(count))
        time.sleep(timeout)

if not ready:
    print('Docker not ready')
    exit(1)
else:
    print('Docker ready')

# For each container, check all files
for container in client.containers.list(all=True):
    print("Container: " + container.name + " (" + container.short_id + ")")
    for filename in os.listdir(nginx_site_enabled):
        file = os.path.join(nginx_site_enabled,filename)
        uid = os.stat(file).st_uid
        gid = os.stat(file).st_gid

        realpathfile = os.path.realpath(file)

        actions = ""
        if os.path.exists(file):
            with open(file,'r') as f:
                for line in fileinput.input(realpathfile, inplace=1):
                    m = re.search(r"server ([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}):[0-9]+ .*" + container.short_id, line)
                    
                    # We found a line with IP and container ID
                    if m:
                        # ensure container is started
                        if container.status != 'running':
                            container.start()
                        # Get container IP
                        ip_addr = container.attrs['NetworkSettings']['IPAddress']
                        
                        # IP is different, update it
                        if m.group(1) != ip_addr:
                            actions = "\nReplace " + m.group(1) + " by "+ ip_addr
                            # Change IP
                            line = re.sub(m.group(1), ip_addr, line)

                    print (line.rstrip())

        # Restore original owner and group (as the copy is owned by root)
        os.chown(file, uid, gid)

if actions:
    # Reload nginx
    print ("\n=> reload nginx")
    unit = Unit(b'nginx.service')
    unit.load()
    unit.Unit.Reload(b'replace')

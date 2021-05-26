#!/usr/bin/env python3
"""
  Remove containers and images that are not the current release
"""

import re
import argparse
import docker

def get_args():
    '''This function parses and return arguments passed in'''
    # Assign description to the help doc
    parser = argparse.ArgumentParser(
        description='Remove old containers from different releases')
    # Add arguments
    parser.add_argument('-s', '--server', type=str, help='Container names', required=True)
    parser.add_argument('-r', '--release', type=str, help='Release number', required=True)
    args = parser.parse_args()
    server = args.server
    release = args.release
    # Return all variable values
    return server, release

def main():
    server, release = get_args()

    if server == "" or release == "":
        exit(1)

    client = docker.from_env()
    for container in client.containers.list(all=True):

        m = re.search( r"^" + server +  "_.*", container.name )
        if m:
            current = re.search( r"^" + server + "_[0-9]*_" + release , container.name )
            if not current:
                print ("Remove container " + container.name )
                container.remove(force=True)
                print ("Remove image " + container.image.short_id )
                client.images.remove(image=container.image.short_id, force=True)

if __name__ == "__main__":
    main()

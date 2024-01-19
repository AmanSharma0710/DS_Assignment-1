from flask import Flask, request, jsonify
import json
import requests
from flask_cors import CORS
import os
import docker
from utils.hashring import HashRing
import string
import random

app = Flask(__name__)
CORS(app)


config = json.load(open('../config.json', 'r'))
hr = HashRing(hashtype = config.hashring.function)
endpoints = config['endpoints']
    
@app.route('/rep', methods=['GET'])
def rep():
    # This endpoint only returns the status of the replicas managedby the loadbalancer. 
    # The response contains the number of replicas and their hostname in the docker internal 
    # network:n1 
    client = docker.from_env()
    containers = client.containers.list(filters={'network: mynet'})
    replicas = []
    for container in containers:
        replicas.append(container.name)
    message = {
        "N": len(replicas),
        "replicas": replicas
    }
    return jsonify({'message': message, 'status': 'successful'}), 200

'''
(/add,method=POST): This endpoint adds newserver instances in the loadbalancer to scale upwith increasing client numbers in the system. The endpoint expects a JSONpayload thatmentions the number of new instances and their preferredhostnames (same as the container name indocker) ina list.Anexample request and responseisbelow.
'''
@app.route('/add', methods=['POST'])
def add(payload):
    # This endpoint adds newserver instances in the loadbalancer to scale upwith increasing client numbers in the system.
    # The endpoint expects a JSONpayload thatmentions the number of new instances and their preferredhostnames (same as the container name indocker) ina list.Anexample request and responseisbelow.
    n = payload['n']
    hostnames = payload['hostnames']
    client = docker.from_env()
    
    # sanity check
    if n > len(hostnames):
        message = '<ERROR> Length of hostname list is more than newly added instances'
        return jsonify({'message': message, 'status': 'failure'}), 400
    
    containers = client.containers.list(filters={'network: mynet'})
    current_hosts = []
    for container in containers:
        current_hosts.append(container.name)

    # We go through the list of preferred hostnames and check if the hostname already 
    # exists. If it does, we return an error message. If it does not, we add the hostname
    # For the hosts without any host name, we generate a random string
    for i in range(n):
        hostname = ''
        if i < len(hostnames):
            hostname = hostnames[i]
            if hostname in current_hosts: 
                message = '<ERROR> Hostname already exists'
                return jsonify({'message': message, 'status': 'failure'}), 400
        else:
            while True:
                hostname = random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10)
                if hostname not in current_hosts:
                    break
            hostnames.append(hostname)
        
        current_hosts.append(hostname)

    # Spawn the containers from the load balancer
    for i in range(n):
        # TODO: check the environment vars
        container = os.popen(f'sudo docker run --name {hostnames[i]} --network mynet -d --network-alias {hostnames[i]} -e SERVER_ID=2 -d ImageName:latest').read()
        if len(container) == 0:
            hr.add_server(hostnames[i])
        else:
            message = '<ERROR> Could not add server'
            return jsonify({'message': message, 'status': 'failure'}), 400
    
    message = {
        "N": len(current_hosts),
        "replicas": current_hosts
    }
        
    return jsonify({'message': message, 'status': 'successful'}), 200

@app.route('/rm', methods=['DELETE'])
def remove(payload):
    # This endpoint removes server instances in the loadbalancer to scale down with decreasing client numbers in the system.
    # The endpoint expects a JSONpayload thatmentions the number of instances to be removed and their preferred hostnames (same as the container name indocker) ina list.Anexample request and responseisbelow.
    n = payload['n']
    hostnames = payload['hostnames']
    client = docker.from_env()

    # sanity check
    if n > len(hostnames):
        message = '<ERROR> Length of hostname list is more than newly added instances'
        return jsonify({'message': message, 'status': 'failure'}), 400
    
    containers = client.containers.list(filters={'network: mynet'})
    current_hosts = []
    for container in containers:
        current_hosts.append(container.name)
    
    # sanity check
    if n > len(current_hosts):
        message = '<ERROR> Number of containers to be removed is more than the number of containers present'
        return jsonify({'message': message, 'status': 'failure'}), 400
    
    # We will first delete the named containers, then move on to delete the rest of the containers
    # We will also remove the hostnames from the list of hostnames
    for i in range(len(hostnames)):
        if hostnames[i] in current_hosts:
            container = client.containers.get(hostnames[i])
            os.system(f'sudo docekr stop {hostnames[i]} && sudo docker rm {hostnames[i]}')
            hr.remove_server(hostnames[i])
            current_hosts.remove(hostnames[i])
            n -= 1
        else:
            message = '<ERROR> Hostname does not exist'
            return jsonify({'message': message, 'status': 'failure'}), 400
    
    # We will now delete the rest of the containers randomly chooosing from the list of containers
    while n > 0:
        container = random.choice(current_hosts)
        os.system(f'sudo docekr stop {container} && sudo docker rm {container}')
        hr.remove_server(container)
        current_hosts.remove(container)
        n -= 1

    message = {
        "N": len(current_hosts),
        "replicas": current_hosts
    }

    return jsonify({'message': message, 'status': 'successful'}), 200

@app.route('/<path>', methods=['GET'])
def forward_request(path):
    # This forwards the request to the backend server if it is a registered endpoint, else returns an error
    if path in endpoints:
        server = hr.get_server(path)
        if server != None:
            reply = requests.get(f'http://{server}:5000/{path}')
            return reply.json(), reply.status_code
        else:
            message = '<ERROR> Server unavailable'
            return jsonify({'message': message, 'status': 'failure'}), 400
    else:
        message = '<ERROR> \'{}\' endpoint does not exist in server replicas'.format(path)
        return jsonify({'message': message, 'status': 'failure'}), 400
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
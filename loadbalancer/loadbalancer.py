from flask import Flask, request, jsonify
import json
import requests
from flask_cors import CORS
import os
import string
import random
import sys
import threading
import time

sys.path.append('../utils')
from hashring import HashRing

app = Flask(__name__)
CORS(app)
lock = threading.Lock()

@app.route('/rep', methods=['GET'])
def rep():
    # This endpoint only returns the status of the replicas managed by the loadbalancer. 
    # The response contains the number of replicas and their hostname in the docker internal 
    # network:n1 
    lock.acquire()
    replica_names = []
    for replica in replicas:
        replica_names.append(replica[0])
    message = {
        "N": len(replicas),
        "replicas": replica_names
    }
    lock.release()
    return jsonify({'message': message, 'status': 'successful'}), 200

'''
(/add,method=POST): This endpoint adds newserver instances in the loadbalancer to scale upwith increasing client numbers in the system. The endpoint expects a JSONpayload thatmentions the number of new instances and their preferredhostnames (same as the container name indocker) ina list.Anexample request and responseisbelow.
'''
@app.route('/add', methods=['POST'])
def add():
    # This endpoint adds newserver instances in the loadbalancer to scale upwith increasing client numbers in the system.
    # The endpoint expects a JSONpayload thatmentions the number of new instances and their preferredhostnames (same as the container name indocker) ina list.Anexample request and responseisbelow.
    content = request.get_json(force=True)
    n = content['n']
    hostnames = content['hostnames']
    
    # sanity check
    if n < len(hostnames):
        message = '<ERROR> Length of hostname list is more than newly added instances'
        return jsonify({'message': message, 'status': 'failure'}), 400
    lock.acquire()
    global replicas

    replica_names = []
    for replica in replicas:
        replica_names.append(replica[0])
    
    # We go through the list of preferred hostnames and check if the hostname already exists.    
    for i in range(n):
        if (i >= len(hostnames)) or (hostnames[i] in replica_names):
            for j in range(len(replica_names)+1):
                new_name = 'S'+ str(j)
                if new_name not in replica_names:
                    hostnames.append(new_name)
                    replica_names.append(new_name)
                    break
        elif hostnames[i] not in replica_names:
            replica_names.append(hostnames[i])

    # Spawn the containers from the load balancer
    for i in range(n):
        container_name = "Server_"
        serverid = -1
        if len(server_ids) == 0:
            global next_server_id
            serverid = next_server_id
            next_server_id += 1
        else:
            serverid = min(server_ids)
            server_ids.remove(min(server_ids))
        container_name += str(serverid)
        container = os.popen(f'docker run --name {container_name} --network mynet --network-alias {container_name} -e SERVER_ID={serverid} -d serverim:latest').read()
        if len(container) != 0:
            hr.add_server(container_name)
            replicas.append([hostnames[i], container_name])
        else:
            message = '<ERROR> Could not add server'
            lock.release()
            return jsonify({'message': message, 'status': 'failure'}), 400

    message = {
        "N": len(replicas),
        "replicas": replica_names
    }
    lock.release()
    return jsonify({'message': message, 'status': 'successful'}), 200

@app.route('/rm', methods=['DELETE'])
def remove():
    # This endpoint removes server instances in the loadbalancer to scale down with decreasing client numbers in the system.
    # The endpoint expects a JSONpayload thatmentions the number of instances to be removed and their preferred hostnames (same as the container name indocker) ina list.Anexample request and responseisbelow.
    content = request.get_json(force=True)
    n = content['n']
    hostnames = content['hostnames']

    # sanity check
    if n < len(hostnames):
        message = '<ERROR> Length of hostname list is more than newly added instances'
        return jsonify({'message': message, 'status': 'failure'}), 400
    lock.acquire()
    global replicas
    replica_names = []
    for replica in replicas:
        replica_names.append(replica[0])
    
    # sanity check
    if n > len(replica_names):
        message = '<ERROR> Number of containers to be removed is more than the number of containers present'
        lock.release()
        return jsonify({'message': message, 'status': 'failure'}), 400
    
    for hostname in hostnames:
        if hostname not in replica_names:
            message = '<ERROR> Hostname not found'
            lock.release()
            return jsonify({'message': message, 'status': 'failure'}), 400

    # We will first delete the named containers, then move on to delete the rest of the containers
    # We will also remove the hostnames from the list of hostnames

    new_replicas = []
    for replica in replicas:
        if replica[0] in hostnames:
            os.system(f'docker stop {replica[1]} && docker rm {replica[1]}')
            server_ids.add(int(replica[1][7:]))
            hr.remove_server(replica[1])
            n -= 1
        else:
            new_replicas.append(replica)
    
    replicas = new_replicas
    replicas_tobedeleted = replicas.copy()
    # shuffle replicas deleted
    random.shuffle(replicas_tobedeleted)
    while len(replicas_tobedeleted) > n:
        replicas_tobedeleted.pop()
    # We will now delete the rest of the containers randomly chooosing from the list of containers
    for i in range(n):
        container = replicas_tobedeleted[i][1]
        os.system(f'docker stop {container} && docker rm {container}')
        hr.remove_server(container)
        server_ids.add(int(container[7:]))
    new_replicas = []
    replica_names = []
    for replica in replicas:
        if replica not in replicas_tobedeleted:
            new_replicas.append(replica)
    replicas = new_replicas
    for replica in replicas:
        replica_names.append(replica[0])

    message = {
        "N": len(replicas),
        "replicas": replica_names
    }
    lock.release()
    return jsonify({'message': message, 'status': 'successful'}), 200

@app.route('/<path>', methods=['GET'])
def forward_request(path):
    # This forwards the request to the backend server
    server = hr.get_server(random.randint(0, 999999))
    if server != None:
        reply = requests.get(f'http://{server}:{serverport}/{path}')
        return reply.json(), reply.status_code
    else:
        message = '<ERROR> Server unavailable'
        return jsonify({'message': message, 'status': 'failure'}), 400

def manage_replicas():
    # This function is responsible for managing the replicas
    # It periodically checks the health of the replicas and if a replica is down, it replaces it with a new replica
    while True:
        lock.acquire()
        for replica in replicas:
            serverdown = False
            try:
                reply = requests.get(f'http://{replica[1]}:{serverport}/heartbeat')
            except:
                serverdown = True
            finally:
                if reply.status_code != 200 or serverdown:
                    # Replica is down
                    print(f'Replica {replica[1]} is down')
                    # Ensure that the replica container is stopped and removed
                    os.system(f'docker stop {replica[1]} && docker rm {replica[1]}')
                    # Replace the replica with a new replica
                    serverid = replica[1][7:]
                    os.system(f'docker run --name {replica[1]} --network mynet --network-alias {replica[1]} -e SERVER_ID={serverid} -d serverim:latest')
        lock.release()
        # Sleep for 10 seconds
        time.sleep(10)
    
if __name__ == '__main__':
    hr = HashRing(hashtype = "sha256")
    serverport = 5000
    replicas = []
    server_ids = set()
    next_server_id = 1
    thread = threading.Thread(target=manage_replicas)
    thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
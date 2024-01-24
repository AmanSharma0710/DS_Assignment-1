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

'''
(/rep,method=GET): This endpoint returns the current number of replicas and their hostnames.
Sample response:
{
    "message": {
        "N": 3,
        "replicas": [
            "S1",
            "S2",
            "S3"
        ]
    },
    "status": "successful"
}
'''
@app.route('/rep', methods=['GET'])
def rep():
    # Acquire the lock on the replicas list since we are sharing it between threads
    lock.acquire()
    replica_names = []
    for replica in replicas:
        replica_names.append(replica[0])
    message = {
        "N": len(replicas),
        "replicas": replica_names
    }
    # Release the lock
    lock.release()
    return jsonify({'message': message, 'status': 'successful'}), 200

'''
(/add,method=POST): This endpoint allows adding new server instances in the loadbalancer to scale up with increasing client numbers in the system.
The endpoint expects a JSON payload that mentions the number of new instances and their preferred hostnames.
Sample request:
{
    "n": 2,
    "hostnames": ["S1", "S2"]   # needs to have atmost n elements
}
Sample response:
{
    "message": {
        "N": 5,
        "replicas": [
            "S1",
            "S2",
            "S3",
            "S4",
            "S5"
        ]
    },
    "status": "successful"
}
'''
@app.route('/add', methods=['POST'])
def add():
    content = request.get_json(force=True)
    n = content['n']
    hostnames = content['hostnames']
    
    # Sanity check
    if n < len(hostnames):
        message = '<ERROR> Length of hostname list is more than newly added instances'
        return jsonify({'message': message, 'status': 'failure'}), 400

    # Acquiring the lock
    lock.acquire()
    global replicas

    replica_names = []
    for replica in replicas:
        replica_names.append(replica[0])
    
    # We go through the list of preferred hostnames and check if the hostname already exists, or if no hostname is provided, we generate a random hostname   
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
        # Allocate the first free server ID between 1 and num_servers
        if len(server_ids) == 0:
            global next_server_id
            serverid = next_server_id
            next_server_id += 1
        else:
            serverid = min(server_ids)
            server_ids.remove(min(server_ids))
        # Generate the container name: Server_<serverid>
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


'''
(/rm,method=DELETE): This endpoint allows removing server instances from the loadbalancer to scale down with decreasing client numbers in the system.
The endpoint expects a JSON payload that mentions the number of instances to be removed and their hostnames.
Sample request:
{
    "n": 2,
    "hostnames": ["S1", "S2"]   # needs to have atmost n elements
}
Sample response:
{
    "message": {
        "N": 3,
        "replicas": [
            "S1",
            "S2",
            "S3"
        ]
    },
    "status": "successful"
}
'''
@app.route('/rm', methods=['DELETE'])
def remove():
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
    
    replicas = new_replicas # We add to new list and swap to keep code efficient
    replicas_tobedeleted = replicas.copy()
    # shuffle replicas deleted to ensure randomness
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

'''
(/<path>,method=GET): This endpoint is the main endpoint that forwards the request to the backend server.
'''
@app.route('/<path>', methods=['GET'])
def forward_request(path):
    # Generate a random 6 digit request ID and get hostname of a replica from the hashring
    server = hr.get_server(random.randint(0, 999999))
    if server != None:
        # Forward the request and return the response
        reply = requests.get(f'http://{server}:{serverport}/{path}')
        return reply.json(), reply.status_code
    else:
        message = '<ERROR> Server unavailable'
        return jsonify({'message': message, 'status': 'failure'}), 400

'''
Entrypoint for thread that checks the replicas for heartbeats every 10 seconds.
'''
def manage_replicas():
    # This function is responsible for managing the replicas
    # It periodically checks the health of the replicas and if a replica is down, it replaces it with a new replica
    while True:
        lock.acquire()
        for replica in replicas:
            serverdown = False
            try:
                reply = requests.get(f'http://{replica[1]}:{serverport}/heartbeat')
            except requests.exceptions.ConnectionError:
                # Replica is down
                print(f'Replica {replica[1]} is down')
                # Ensure that the replica container is stopped and removed
                os.system(f'docker stop {replica[1]} && docker rm {replica[1]}')
                # Replace the replica with a new replica
                serverid = replica[1][7:]
                # We use the same name instead of generating a new name to keep the naming consistent
                os.system(f'docker run --name {replica[1]} --network mynet --network-alias {replica[1]} -e SERVER_ID={serverid} -d serverim:latest')
            else:
                if reply.status_code != 200:
                    # Replica is not heartbeating, so it is assumed to be down
                    print(f'Replica {replica[1]} is not responding to heartbeat, killing it')
                    # Ensure that the replica container is stopped and removed
                    os.system(f'docker stop {replica[1]} && docker rm {replica[1]}')
                    # Replace the replica with a new replica
                    serverid = replica[1][7:]
                    os.system(f'docker run --name {replica[1]} --network mynet --network-alias {replica[1]} -e SERVER_ID={serverid} -d serverim:latest')
        lock.release()
        # Sleep for 10 seconds
        time.sleep(10)
    
if __name__ == '__main__':
    # Create an object of the HashRing class. This is where we add servers by their hostname and 
    # on getting a new request, we generate a random 6 digit request id and get the server
    hr = HashRing(hashtype = "sha256")
    serverport = 5000

    # Replicas is a list of lists. Each list has two entries: the External Name (user-specified or randomly generated) and the Container Name
    # The Container Name is the name of the container, and is the same as the hostname of the container. It is always of the form Server_<serverid>
    replicas = []
    # Bookkeeping for server IDs
    server_ids = set()
    next_server_id = 1

    # Setting up and spawning the thread that manages the replicas
    thread = threading.Thread(target=manage_replicas)
    thread.start()
    
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=False)
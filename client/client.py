import requests
import json
import time

load_balancer_url = None

def get_replica_status():
    response = requests.get('http://localhost:5000/rep')
    return response.json()

def add_replicas(n, hostnames):
    payload = {"n": n, "hostnames": hostnames}
    response = requests.post(f"{load_balancer_url}/add", json=payload)
    return response.json()

def remove_replicas(n, hostnames):
    payload = {"n": n, "hostnames": hostnames}
    response = requests.delete(f"{load_balancer_url}/rm", json=payload)
    return response.json()

def make_request(endpoint_path):
    response = requests.get(f"{load_balancer_url}/{endpoint_path}")
    return response.json()

if __name__ == "__main__":
    # load balancer port from config.json
    config = json.load(open("../config.json", "r"))
    load_balancer_port = config["loadbalancerport"]
    load_balancer_url = "http://localhost:5000"
    print(load_balancer_url)


    # Example usage:
    print("Current Replica Status:")
    print(get_replica_status())

    # Add new replicas
    # print("\nAdding 2 new replicas:")
    # added_replicas = add_replicas(2, ["NewServer1", "NewServer2"])
    # print(added_replicas)


    # # Remove replicas
    # print("\nRemoving 1 replica:")
    # removed_replicas = remove_replicas(1, [])
    # print(removed_replicas)

    # # Check updated Replica Status:
    # print("\nUpdated Replica Status:")
    # print(get_replica_status())

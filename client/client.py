import requests
import json
import time

load_balancer_url = None

def get_replica_status():
    response = requests.get(load_balancer_url + "/rep")
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
    load_balancer_port = 5000
    load_balancer_url = f"http://localhost:{load_balancer_port}"
    print(load_balancer_url)

    while(1):
        print("1. Get replica status")
        print("2. Add replicas")
        print("3. Remove replicas")
        print("4. Make request")
        print("5. Exit")

        choice = int(input("Enter choice: "))

        if choice == 1:
            print(get_replica_status())
        elif choice == 2:
            n = int(input("Enter number of replicas to add: "))
            hostnames = []
            for i in range(n):
                hostnames.append(input("Enter hostname: "))
                if hostnames[i] == "":
                    hostnames.pop()
            print(add_replicas(n, hostnames))
        elif choice == 3:
            n = int(input("Enter number of replicas to remove: "))
            hostnames = []
            for i in range(n):
                hostnames.append(input("Enter hostname: "))
                if hostnames[-1] == "":
                    hostnames.pop()
            print(remove_replicas(n, hostnames))
        elif choice == 4:
            endpoint_path = input("Enter endpoint path: ")
            print(make_request(endpoint_path))
        elif choice == 5:
            break
        else:
            print("Invalid choice")

    # Example usage:
    # print("Current Replica Status:")
    # print(get_replica_status())

    # Add new replicas
    print("\nAdding 2 new replicas:")
    added_replicas = add_replicas(2, ["S3", "S4"])
    print(added_replicas)


    # # Remove replicas
    # print("\nRemoving 1 replica:")
    # removed_replicas = remove_replicas(1, [])
    # print(removed_replicas)

    # # Check updated Replica Status:
    # print("\nUpdated Replica Status:")
    # print(get_replica_status())

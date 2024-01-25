# Assignment-1: Customizable Load Balancer

## Instructions

The Makefile lists all the commands required for deploying the load balancer network as well as for deploying the client.

* `make all`: build the server image deploy the docker compose
* `make client`: build the client image and run the client container
* `make clean_client`: stop and remove the client container and remove the client image
* `make clean`: bring the compose down and remove the load balancer and server images from the server

`curl` command can also be used to send requests to the load balancer from the host machine without using a separate client container in the following format:

```bash
curl --request <request-type> [-d @payload.json] http://localhost:5000/<endpoint>
```

Here the `request-type` can be `GET, POST, or DELETE`. For the ease of sending payload data in case of /add and /rm, a separate `payload.json` file can be used

## Server

The servers have a hostname which is what is received by the client and can be set by the client. However, the container name of the server follows the format `Server_{SERVER_ID}`. This container name is used in all the internal workings and can not be set by the client.

The server accepts HTTP requests on port 5000 in the endpoints:

<font size="3">_/home (method = GET)_</font>  
This returns a hello message with server ID along with relevant response code. The server ID returned here is the internal server ID and is in no way related to number (if exists) in the server's hostname.

<font size="3">_/heartbeat (method = GET)_</font>  
This endpoints sends heartbeat (empty) responses upon request. This endpoint serves to identify failures in the set of containers maintained by the load balancer which would be indicated by the error response received by the load balancer

## HashRing

The `HashRing` class implements a distributed hash ring using consistent hashing. It provides a way to map keys or request IDs to servers in a distributed system. Consistent hashing is a technique that allows for dynamic scaling and load balancing in distributed systems.

### Usage

To use the `HashRing` class, follow these steps:

1. **Initialization**: Create an instance of the `HashRing` class by providing the number of virtual nodes, size of the ring (`M`) and a hash function (`H`) as parameters.

2. **Adding Servers**: Add servers to the hash ring using the `add_server` method. Each server is identified by a unique server ID. The server is hashed and placed on the ring at multiple points corresponding to its virtual nodes.

3. **Mapping Requests**: Map a request ID to a server using the `get_server` method. This method takes a request ID as an argument and returns the name of the server to which the request is mapped. If the initial position of the request ID on the hash ring is already occupied by another server, linear probing is used to find the next available position.

4. **Removing Servers**: Remove a server from the hash ring using the `remove_server` method. This method takes a server ID as an argument and removes all the virtual nodes of that server from the hash ring.

### Design Choices

The `HashRing` class makes the following design choices:

- **Consistent Hashing**: Consistent hashing is used to distribute keys or request IDs across the servers in a balanced manner. This ensures that the load is evenly distributed and allows for easy addition or removal of servers without causing significant remapping of keys.

- **Virtual Nodes**: The hash ring uses virtual nodes to improve the distribution of keys. Each server is represented by multiple virtual nodes on the hash ring, which helps to balance the load even further.

- **Linear Probing**: In the `get_server` method, if the initial position of the request ID on the hash ring is already occupied by another server, linear probing is used to find the next available position. This ensures that the request is always mapped to a server, even if collisions occur.

- **Null Return**: If no server is found for a given request ID, the `get_server` method returns `None`. Similarly, if a server to be removed does not exist in the hash ring, the `remove_server` method does nothing.

Please refer to the code documentation for more details on the implementation.

## Load Balancer

The load balancer uses the HashRing data structure to manage a set of N web server containers. 

The load balancer is a multi-threaded process. The main thread handles all the requests to the various endpoints (which have been described below). The secondary thread is responsible for maintaining the number of servers. This thread periodically (set to 10 seconds) requests heartbeat from each server (maintained in a global list). If it finds a non-responsive server, it will first remove the container from the docker and then spawn another container with the same hostname and container name as the deleted server.

The load balancer endpoints are exposed at port 5000. We have exposed the following endpoints:

<font size="3">_/rep (method = GET)_</font>  
This endpoint returns the status of the replicas managed by the load balancer. We store a global list `replicas` which stores the currently deployed servers in the format: `[hostname, container_name]`. We return the number of servers deployed (n) after the addition and their hostnames (not the container names).

<font size="3">_/add (method = POST)_</font>  
This endpoint adds a server instance in the load balancer. It expects a JSON payload that mentions the number of new instances and their preferred hostnames. In response we send the complete list of currently deployed servers with their hostnames. If the preferred hostname can not be set, we set the hostname as `S<number>` with number being a non-used number from 0 to the number of servers.

To spawn a new container, `SERVER_ID` is required. This is found from a global set `server_ids` which keeps track of the free server ids. The lowest available id is chosen. If the set is empty, we choose the value of the global variable `next_server_id` which is then incremented. This `SERVER_ID` is also set as an environment variable when this new container is spawned by the load balancer.

<font size="3">_/rm (method = DELETE)_</font>  
This endpoint adds a server instance in the load balancer. It expects a JSON payload that mentions the number of new instances and their hostnames. We return the number of servers deployed (n) after the deletion and their hostnames (not the container names).

We first choose to delete the containers whose hostnames have been given. If the number of hostnames is less than the required number, we choose the rest servers to be deleted randomly. For this we shuffle the list of servers and choose the servers from the start of this shuffled list and delete them. We stop these containers and remove them from the docker.

<font size="3">_/&lt;path> (method = GET)_</font>  
Requests to this endpoint gets routed to a server replica as scheduled by the HashRing. Only endpoints registered with the web server would give a valid response. Currently only `home` is registered. Any other request gives out an error response.

## Analysis

## Client

This client has been set up for ease of testing and verification of the program. `client.py` file gives a text-based interface to send requests to the load balancer. It runs an infinite loop with 5 options to choose from on each iteration - `/rep, /add, /rm, /path, Exit`. This will be run as a separate container on the same network as the load balancer. The commands for the same can be found in the Makefile section.

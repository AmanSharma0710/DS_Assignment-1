# Description: This file contains the implementation of the consistent hashing algorithm
#              used by the load balancer to map requests to server containers.


class HashRing:
    def __init__(self, irtual_nodes=9, M=512):
        self.virtual_nodes = virtual_nodes
        self.M = M
        self.server_alloc = [None] * M
        self.serverid = {}
        self.used_serverids = set()

    def H(i):
        return (i**2 + 2*i + 17) % M

    def Phi(i, j):
        return (i**2 + j**2 + 2*j + 25) % M

    def add_server(server_name):
        # Allocate a server ID
        if server_name in serverid:
            print("Error: Server already exists")
            return False
        server_id = -1
        for i in range(M):
            if i not in used_serverids:
                server_id = i
                used_serverids.add(i)
                break
        if server_id == -1:
            print("Error: No space for server", server_name)
            return False
        
        serverid[server_name] = server_id
        # Allocate virtual nodes
        for j in range(virtual_nodes):
            pos = Phi(server_id, j)
            allocated = False
            for i in range(M):
                if server_alloc[pos] == None:
                    server_alloc[pos] = server_id
                    allocated = True
                    break
                else:
                    # Linear probing
                    pos = (pos + 1) % M
            if not allocated:
                print("Error: No space for server", server_id)
                return False
        return True
            
    def remove_server(server_name):
        if server_name not in serverid:
            print("Error: Server does not exist")
            return False
        server_id = serverid[server_name]
        # Remove virtual nodes
        for j in range(M):
            if server_alloc[j] == server_id:
                server_alloc[j] = None
        # Remove server ID
        used_serverids.remove(server_id)
        serverid.pop(server_name)
        return True

    def get_server(request_id):
        pos = H(request_id)
        for i in range(M):
            if server_alloc[pos] != None:
                return server_alloc[pos]
            else:
                # Linear probing
                pos = (pos + 1) % M
        return None


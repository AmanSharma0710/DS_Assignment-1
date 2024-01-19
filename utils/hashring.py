# Description: This file contains the implementation of the consistent hashing algorithm
#              used by the load balancer to map requests to server containers.


class HashRing:
    def __init__(self, virtual_nodes=9, M=512):
        self.virtual_nodes = virtual_nodes
        self.M = M
        self.server_alloc = [None] * M
        self.serverid = {}
        self.used_serverids = set()

    def H(self, i):
        return (i**2 + 2*i + 17) % self.M

    def Phi(self, i, j):
        return (i**2 + j**2 + 2*j + 25) % self.M

    def add_server(self, server_name):
        # Allocate a server ID
        if server_name in self.serverid:
            print("Error: Server already exists")
            return False
        server_id = -1
        # Allocate the first free server ID between 1 and M
        for i in range(1, self.M+1):
            if i not in self.used_serverids:
                server_id = i
                self.used_serverids.add(i)
                break
        if server_id == -1:
            print("Error: No space for server", server_name)
            return False
        
        self.serverid[server_name] = server_id
        # Allocate virtual nodes
        for j in range(1, self.virtual_nodes+1):
            pos = self.Phi(server_id, j)
            allocated = False
            for i in range(self.M):
                if self.server_alloc[pos] == None:
                    self.server_alloc[pos] = server_id
                    allocated = True
                    break
                else:
                    # Linear probing
                    pos = (pos + 1) % self.M
            if not allocated:
                print("Error: No space for server", server_id)
                return False
        return True
            
    def remove_server(self, server_name):
        if server_name not in self.serverid:
            print("Error: Server does not exist")
            return False
        server_id = self.serverid[server_name]
        # Remove virtual nodes
        for j in range(self.M):
            if self.server_alloc[j] == server_id:
                self.server_alloc[j] = None
        # Remove server ID
        self.used_serverids.remove(server_id)
        self.serverid.pop(server_name)
        return True

    def print_serveralloc(self):
        for i in range(self.M):
            if self.server_alloc[i]!=None:
                print(str(i) + ": " + str(self.server_alloc[i]))

    def get_server(self, request_id):
        pos = self.H(request_id)
        for i in range(self.M):
            if self.server_alloc[pos] != None:
                return self.server_alloc[pos]
            else:
                # Linear probing
                pos = (pos + 1) % self.M
        return None


# Description: This file contains the implementation of the consistent hashing algorithm
#              used by the load balancer to map requests to server containers.

import hashlib

class HashRing:
    def __init__(self, virtual_nodes=9, M=512, hashtype = "default"):
        self.virtual_nodes = virtual_nodes
        self.M = M
        self.server_alloc = [None] * (M+1)
        self.name_to_serverid = {}
        self.serverid_to_name = [None] * (M+1)
        self.hashtype = hashtype

    def H(self, i):
        return (i**2 + 2*i + 17) % self.M

    def Phi(self, i, j, type = "default"):
        if type == "default":
            return (i**2 + j**2 + 2*j + 25) % self.M
        elif type == "md5":
            return int(hashlib.md5((str(i) + str(j)).encode('utf-8')).hexdigest(), 16) % self.M
        elif type == "sha256":
            return int(hashlib.sha256((str(i) + str(j)).encode('utf-8')).hexdigest(), 16) % self.M
        elif type == "custom":
            return (((i**2)%self.M) * ((j**2)%self.M) + 2*j + 25) % self.M
        else:
            print("Error: Invalid type")
            return None

    def add_server(self, server_name):
        # Allocate a server ID
        if server_name in self.name_to_serverid:
            print("Error: Server already exists")
            return False
        server_id = -1
        # Allocate the first free server ID between 1 and M
        for i in range(1, self.M+1):
            if self.serverid_to_name[i]==None:
                server_id = i
                self.serverid_to_name[i] = server_name
                break
        if server_id == -1:
            print("Error: No space for server", server_name)
            return False
        
        self.name_to_serverid[server_name] = server_id
        # Allocate virtual nodes
        for j in range(1, self.virtual_nodes+1):
            pos = self.Phi(server_id, j, self.hashtype)
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
        print("Removing server", server_name)
        if server_name not in self.name_to_serverid.keys():
            print("Error: Server does not exist")
            return False
        server_id = self.name_to_serverid[server_name]
        print("Server ID:", server_id)
        # Remove virtual nodes
        for j in range(self.M):
            if self.server_alloc[j] == server_id:
                self.server_alloc[j] = None
        # Remove server ID
        self.serverid_to_name[server_id] = None
        self.name_to_serverid.pop(server_name)
        return True

    def print_serveralloc(self):
        for i in range(self.M):
            if self.server_alloc[i]!=None:
                print(str(i) + ": " + str(self.server_alloc[i]))

    def get_server(self, request_id):
        pos = self.H(request_id)
        for i in range(self.M):
            if self.server_alloc[pos] != None:
                return self.serverid_to_name[self.server_alloc[pos]]
            else:
                # Linear probing
                pos = (pos + 1) % self.M
        return None


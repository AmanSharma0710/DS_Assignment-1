from hashring import HashRing

hashring = HashRing()

hashring.add_server("smd")
hashring.add_server("smd1")
hashring.add_server("smd2")
hashring.add_server("smd3")
hashring.add_server("smd13")
hashring.add_server("smd23")
hashring.add_server("md")
hashring.add_server("md1")
hashring.add_server("md2")
hashring.add_server("md3")
hashring.add_server("md13")
hashring.add_server("md23")
print(hashring.server_alloc)
hashring.print_serveralloc()
for i in range(20):
    print(hashring.get_server(i))
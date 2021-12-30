from socket import inet_ntoa, socket, AF_INET, SOCK_DGRAM
from sys import byteorder
from random import getrandbits
from bencodepy import encode, decode

node_id = getrandbits(160).to_bytes(20, byteorder)
info_hash = bytes.fromhex("5A6194C4E92A459A1313B7A4E9F7A9EB18FB9205")
K = 8 # can be 16

get_peers= {
    "t":"aa",
    "y":"q",
    "q":"get_peers",
    "a":{
        "id": node_id,
        "info_hash" : info_hash
        }
    }
query = encode(get_peers)
s = socket(AF_INET, SOCK_DGRAM)

initial = ('87.98.162.88', 6881)   ## try out the other initial nodes too 

s.sendto(query,initial)
r = s.recvfrom(1024)
nodes_info = decode(r[0])[b'r'][b'nodes']
###

nodes_array = bytearray(nodes_info)
nodes = [[nodes_array[(26*i):(26*i)+20], nodes_array[(26*i)+20:(26*(i+1))]] for i in range(8)]
nodes_addresses = list(set([(inet_ntoa(bytes(node[1][:4])), int.from_bytes(bytes(node[1][4:6]),'big')) for node in nodes])) # removing duplicates with set  # big byte order! idk why 
print(nodes_addresses)




for address in nodes_addresses:
    s.sendto(query,address)
    r = s.recvfrom(1024)
    print(decode(r[0]))
    nodes_info = decode(r[0])[b'r'][b'nodes'] ## this would be branching in the main file

## ok at this point it has already branched out and i need a routing table and a terminating condition

nodes_array = bytearray(nodes_info)
nodes = [[nodes_array[(26*i):(26*i)+20], nodes_array[(26*i)+20:(26*(i+1))]] for i in range(8)]
nodes_addresses = list(set([(inet_ntoa(bytes(node[1][:4])), int.from_bytes(bytes(node[1][4:6]),'big')) for node in nodes])) # removing duplicates with set  # big byte order! idk why 
print(nodes_addresses)

for address in nodes_addresses:
    s.sendto(query,address)
    r = s.recvfrom(1024)
    print(decode(r[0]))

s.close()

## repeat until find peers


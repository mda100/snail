import socket
from random import getrandbits
from bencodepy import encode, decode
import sys

## testing the bootstrap nodes ##

node_id = getrandbits(160).to_bytes(20, sys.byteorder)
info_hash = bytes.fromhex("5A6194C4E92A459A1313B7A4E9F7A9EB18FB9205")

# ping = {
#     "t":"aa",
#     "y":"q",
#     "q":"ping",
#     "a":{"id": node_id}
#     }
# query = encode(ping)


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


bufferSize = 1024
s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

BOOTSTRAP_NODES = [(socket.gethostbyname("dht.libtorrent.org"), 25401), #success
(socket.gethostbyname("router.bittorrent.com"), 6881), #success
(socket.gethostbyname("router.utorrent.com"), 6881), #timed out
(socket.gethostbyname("dht.transmissionbt.com"), 6881), #success
(socket.gethostbyname("dht.aelitis.com"), 6881), #timed out
('87.98.162.88', 6881) #success -> repeat 
]


for address in BOOTSTRAP_NODES:
    try:
        s.settimeout(1)
        s.sendto(query, address)
        response = s.recvfrom(bufferSize)
        print(address,'success')
    except socket.timeout as e:
        print(address,e)

s.close()
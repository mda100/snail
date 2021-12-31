from ctypes import sizeof
import socket
from random import getrandbits
from bencodepy import encode, decode
import sys

node_id = getrandbits(160).to_bytes(20, sys.byteorder)
info_hash = info_hash = bytes.fromhex("5A6194C4E92A459A1313B7A4E9F7A9EB18FB9205")

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

server = ('87.98.162.88', 6881)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(query,server)
r = s.recvfrom(1024)
print(decode(r[0]))
s.close()


## HELL YEAH!
## worked instantly one try

## still unclear what v is ? did they update krpc responses? 

## ok the nodes are one byte string 

## try these as initial nodes "dht.libtorrent.org:25401,router.bittorrent.com:6881,router.utorrent.com:6881,dht.transmissionbt.com:6881,dht.aelitis.com:6881");
##  i know transmission's works
## if this works, it's a enough to start building 
## will need to refactor a lot but thats fine

## A key "v" should be included in every message with a client version string. The string should be a two character client identifier registered in BEP 20 [3] followed by a two character version identifier. Not all implementations include a "v" key so clients should not assume its presence.

## Contact information for nodes is encoded as a 26-byte string. Also known as "Compact node info" the 20-byte Node ID in network byte order has the compact IP-address/port info concatenated to the end
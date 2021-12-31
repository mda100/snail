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

server = ('207.204.65.155', 895)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(query,server)
r = s.recvfrom(1024)
print(decode(r[0]))


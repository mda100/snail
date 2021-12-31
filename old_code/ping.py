# https://pythontic.com/modules/socket/udp-client-server-example
# saying hello to the bittorrent bootstrap node

from ctypes import sizeof
import socket
from random import getrandbits
from bencodepy import encode, decode
import sys

node_id = getrandbits(160).to_bytes(20, sys.byteorder)
print(node_id)
ping = {
    "t":"aa",
    "y":"q",
    "q":"ping",
    "a":{"id": node_id}
    }
query = encode(ping)
print(query)
server  = ('dht.transmissionbt.com', 6881)
bufferSize = 1024
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.sendto(query, server)
response = UDPClientSocket.recvfrom(bufferSize)
print(response)
UDPClientSocket.close()
# querying the bittorrent bootstrap node
# querying the nodes return by the bootstrap node
# repeat recursively in command line until get peers response
from os import error
from socket import inet_ntoa, socket, AF_INET, SOCK_DGRAM, timeout, gethostbyname
from sys import byteorder
from random import getrandbits
from typing import final
from bencodepy import encode, decode
from bencodepy.exceptions import BencodeDecodeError

## GLOBALS ##

node_id = getrandbits(160).to_bytes(20, byteorder)
info_hash = bytes.fromhex("5A6194C4E92A459A1313B7A4E9F7A9EB18FB9205")
K = 8 # this is inconsistent, better to dynamically calculate 
s = socket(AF_INET, SOCK_DGRAM)
BOOTSTRAP_NODES = [(gethostbyname("dht.libtorrent.org"), 25401), 
(gethostbyname("router.bittorrent.com"), 6881), 
(gethostbyname("dht.transmissionbt.com"), 6881), 
]

routing_table = []
peers_table = []

### GET PEERS QUERY  ###

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



def parse_node_addresses(nodes_info: bytes):
    nodes_array = bytearray(nodes_info)
    if (len(nodes_array) % 26 == 0):
        nodes = [[nodes_array[(26*i):(26*i)+20], nodes_array[(26*i)+20:(26*(i+1))]] for i in range(int(len(nodes_array)/26))]
        nodes_addresses = list(set([(inet_ntoa(bytes(node[1][:4])), int.from_bytes(bytes(node[1][4:6]),'big')) for node in nodes]))
    else:
        raise Exception('buffer length of nodes is not divisible by 26')
    return nodes_addresses


# pretty good error handling! it keeps runnning but prints exceptions 

def get_peers_utility(r: bytes) -> None:
    try:
        results = decode(r[0])
        if results[b'y'] == b'r':
            if b'nodes' in results[b'r']:
                new_addresses = parse_node_addresses(results[b'r'][b'nodes'])
                routing_table.extend(new_addresses)
            elif b'values' in results[b'r']:
                peers_table.extend(results[b'r'][b'values']) # may need to parse this
            else:
                print('unexpected response content')
        elif results[b'y'] == b'e':
            print(results[b'e'])
        else:
            print('unexpected response')
    except BencodeDecodeError as e:
        print(e)
        

def get_peers_query(address: tuple, query: bytes = query) -> None:
    try:
        s.settimeout(1)
        s.sendto(query, address)
        r = s.recvfrom(1024)
        get_peers_utility(r)
    except timeout as e:
        print(address,e)



def one_pass(address_list: list = routing_table):
    for address in address_list:
        try:
            get_peers_query(address)
            break
        except:
            pass

## getting a big batch from the bootstrap noodes##

one_pass(address_list=BOOTSTRAP_NODES)
print(routing_table)
one_pass(address_list=BOOTSTRAP_NODES)
print(routing_table)
one_pass(address_list=BOOTSTRAP_NODES)
print(routing_table)
one_pass(address_list=BOOTSTRAP_NODES)
print(routing_table)
one_pass(address_list=BOOTSTRAP_NODES)
print(routing_table)
one_pass(address_list=BOOTSTRAP_NODES)
print(routing_table)
one_pass(address_list=BOOTSTRAP_NODES)
print(routing_table)
one_pass(address_list=BOOTSTRAP_NODES)
print(routing_table)
one_pass(address_list=BOOTSTRAP_NODES)
print(routing_table)
one_pass(address_list=BOOTSTRAP_NODES)
print(routing_table)
## run on loop until terminate ##
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
one_pass()
print(len(routing_table))
print(peers_table)
s.close()


## once somebody times out - it gets stuck! im not sure why 
## there's some weird inconsistencies with the timeouts 
## but this is enough to get started
## create a method for managing the routing table
## create a terminating condition
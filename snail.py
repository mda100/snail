from os import error
from socket import inet_ntoa, socket, AF_INET, SOCK_DGRAM, timeout, gethostbyname
from sys import byteorder
from random import getrandbits
from typing import final
from bencodepy import encode, decode
from bencodepy.exceptions import BencodeDecodeError
from operator import attrgetter
from typing import List

## GLOBALS ##

node_id = getrandbits(160).to_bytes(20, byteorder)
info_hash = bytes.fromhex("F5E058892444A1464367AFB1876DE80D68A085DE") #avatar way of water
K = 8 # this is inconsistent, better to dynamically calculate 
MAX_PEERS = 20
s = socket(AF_INET, SOCK_DGRAM)
BOOTSTRAP_NODES = [(gethostbyname("dht.libtorrent.org"), 25401), 
(gethostbyname("router.bittorrent.com"), 6881), 
(gethostbyname("dht.transmissionbt.com"), 6881), 
(gethostbyname("router.utorrent.com"), 6881),
(gethostbyname("dht.aelitis.com"), 6881)
]


## data ##

new_nodes = []
routing_table = []  # the routing table i'm maintaining is different then the query table
peers_table = []


## utilities ##

def distance(node: bytes, target: bytes = info_hash) -> int:
    return int.from_bytes(node, 'big')^int.from_bytes(target, 'big')

class Node:
    def __init__(self, id: bytearray, address: bytearray) -> None:
        self.id = bytes(id)
        self.address = (inet_ntoa(bytes(address[:4])), int.from_bytes((address[4:6]),'big'))
        self.closeness = distance(self.id)
        self.alive = True
        pass

    def __eq__(self, other):
        return self.id==other.id
    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return 'id: %s\naddress: %s\ndistance: %s\nalive: %s' % (self.id, self.address, self.closeness, self.alive)


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

## UTILITY FUNCTIONS ##

# returns updated COPY of routing table
# removes "dead" nodes, duplicates, sorts by distance, prunes top K closest

def update_routing_table(routing_table: list = routing_table) -> list:
    return sorted(list(set([node for node in routing_table if node.alive])), key=lambda node: node.closeness)[:K]

def parse_nodes(nodes_info: bytes):
    nodes_array = bytearray(nodes_info)
    if (len(nodes_array) % 26 == 0):
        nodes = [Node(id=nodes_array[(26*i):(26*i)+20], address=nodes_array[(26*i)+20:(26*(i+1))]) for i in range(int(len(nodes_array)/26))]
        return nodes
    else:
        raise Exception('buffer length of nodes is not divisible by 26')


def get_peers_utility(r: bytes) -> None:
    try:
        results = decode(r[0])
        if results[b'y'] == b'r':
            if b'nodes' in results[b'r']:
                new_nodes.extend(parse_nodes(results[b'r'][b'nodes']))
            if b'values' in results[b'r']: #libtorrent includes both values and peers and keeps traversing until len(peers) == 8
                peers_table.extend(results[b'r'][b'values']) # may need to parse this
        elif results[b'y'] == b'e':
            print(results[b'e'])
        else:
            print('unexpected response')
    except BencodeDecodeError as e:
        print(e)
        
## QUERY FUNCTIONS ## 

def get_peers_query(node: Node, query: bytes = query) -> None:
    try:
        s.settimeout(1)
        s.sendto(query, node.address)
        r = s.recvfrom(1024)
        get_peers_utility(r)
    except timeout as e:
        node.alive = False
        print(node.id,e)

def get_peers_query_bootstrap(address: tuple, query: bytes = query) -> None:
    try:
        s.settimeout(1)
        s.sendto(query, address)
        r = s.recvfrom(1024)
        get_peers_utility(r)
    except timeout as e:
        print(address,e)


def one_pass(nodes_list: List[Node] = routing_table) -> None:
    i = 0 
    for node in nodes_list:
        get_peers_query(node)
        i+=1

def one_pass_bootstrap(address_list: list = BOOTSTRAP_NODES) -> None:
    for address in address_list:
        get_peers_query_bootstrap(address)

one_pass_bootstrap()
routing_table.extend(new_nodes)
new_nodes.clear()

i = 0
while len(peers_table) < MAX_PEERS:
    one_pass()
    routing_table.extend(new_nodes)
    routing_table = update_routing_table()
    new_nodes.clear()
    i+=1
    if i%10 == 0:
        print('peers table at iteration ', i, ' :\n', peers_table)

print('peers table:\n', peers_table)
print('total numer of iterations: ', i)
s.close()

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

#magnet:?xt=urn:btih:D7F1A872C0A936F2E79DAD3060DB6D72A90BCB55&dn=Spider-Man+No+Way+Home+%282021%29+1080p+CAM+NO+ADS+Includes+Both+POS&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.dler.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&tr=udp%3A%2F%2F47.ip-51-68-199.eu%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2920%2Fannounce&tr=udp%3A%2F%2Ftracker.pirateparty.gr%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce

node_id = getrandbits(160).to_bytes(20, byteorder)
info_hash = bytes.fromhex("D7F1A872C0A936F2E79DAD3060DB6D72A90BCB55")
K = 8 # this is inconsistent, better to dynamically calculate 
s = socket(AF_INET, SOCK_DGRAM)
BOOTSTRAP_NODES = [(gethostbyname("dht.libtorrent.org"), 25401), 
(gethostbyname("router.bittorrent.com"), 6881), 
(gethostbyname("dht.transmissionbt.com"), 6881), 
(gethostbyname("router.utorrent.com"), 6881),
(gethostbyname("dht.aelitis.com"), 6881)
]


## data ##

new_nodes = []
routing_table = []  # so the "routing table i'm maintaining is different then the query table "
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
# there's some redundancy here, but i can worry about abstraction later

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
while len(peers_table) < 20:
    one_pass()
    routing_table.extend(new_nodes)
    routing_table = update_routing_table()
    new_nodes.clear()
    i+=1

print(peers_table)
print(i)
s.close()

## 100 is too many -> smarter !
## this is a solid working example
## i should rewrite this in cython
## refactor it to be simpler and more efficient
## take care of use cases and errors
## once this is a tight module ill be gucci 
## i'm not going to add seeding -> making a mobile p2p file sharer is enoguh work 

##  read through issues on open source bittorrents 
## a more intelligent way to do this is to "find_node" until K=20 nodes that have no closer distance 
## no that's not it - there IS a smarter way to terminate this, but rn # limit it! 

# i truly don't know hwy it gets caught in a loop   
# maybe i slice the nodes to 64 but i only do a pass on the first 8 -> that way if they time out no problem

## it's converging to one number which isn't great 
## do i have any peers??? -> maybe that is the closest distance ??
## as soon as i have a terminating condition i have my minimum working example for the crawler
## at that point i can clean up this file and make it robust 
## maybe rewrite in cython
## and port into a new file 
## work on the handshake until i download 
## then make this very basic backage very robust 
## then work on link opening, a web server, a mobile app , etc. 

## yeah it's converging so my first question is -> do peers exist ?? maybe this IS the closest number 

## do the 64 -> 8 thing
## if it's getting stuck in a loop -> the 8 closest reference eachother or something
## maybe hve a 

## OH SHIT YEAH BB WE GOT PEERS
## NOPE IT GOES ON AND ON BC NO TERMINATING CONDIITON WE GOT PEERS


### ok yeah so it converges on a number and then is hitting the same ones and then keeps adding peers
### how to terminate ?


## how did i write this? should this be my side project or something else ##


### hmm it looks like this works still! if i get bored i can copy this folder, chop this up into components i understand with a little better
## design pattern and cleaner code then extend this to do the handshake i think
## this is a sick project 

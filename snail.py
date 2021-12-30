from socket import inet_ntoa, socket, AF_INET, SOCK_DGRAM
from sys import byteorder
from random import getrandbits
from bencodepy import encode, decode

## GLOBALS ##

node_id = getrandbits(160).to_bytes(20, byteorder)
info_hash = bytes.fromhex("5A6194C4E92A459A1313B7A4E9F7A9EB18FB9205")
K = 8 # can be 16
s = socket(AF_INET, SOCK_DGRAM)
BOOTSTRAP_NODES = [('87.98.162.88', 6881)] ## add the other bootstrap nodes
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

def get_peers_query(address: tuple, query: bytes = query) -> None:
    try: 
        s.sendto(query, address)
        s.settimeout(1)
        r = s.recvfrom(1024)
        results = decode(r[0])
        print(results)
        if results[b'y'] == b'r':
            if b'nodes' in results[b'r']:
                new_addresses = parse_node_addresses(results[b'r'][b'nodes'])
                routing_table.extend(new_addresses)
            elif b'values' in results[b'r']:
                peers_table.extend(results[b'r'][b'values'])
            else:
                raise Exception('unexpected response content')
        elif results[b'y'] == b'e':
            raise Exception(results[b'e'])
        else:
            raise Exception('unexpected response type')
    except:
        raise Exception('udp query failed')


def parse_node_addresses(nodes_info: bytes):
    nodes_array = bytearray(nodes_info)
    nodes = [[nodes_array[(26*i):(26*i)+20], nodes_array[(26*i)+20:(26*(i+1))]] for i in range(K)]
    nodes_addresses = list(set([(inet_ntoa(bytes(node[1][:4])), int.from_bytes(bytes(node[1][4:6]),'big')) for node in nodes]))
    return nodes_addresses

def one_pass(address_list: list = routing_table):
    for address in address_list:
        get_peers_query(address)
        print(routing_table)


one_pass(address_list=BOOTSTRAP_NODES)
one_pass()
one_pass()
s.close()

# once this works -> do error handling and edge cases, abstractions -> then make this a module: info hash+ ID -> peers
# then that module exists as part of a larger project which includes seeding, announce, downloading, opening urls, file writing



## the bootstrap node poops out one at a time
## some of those are bad and timeout!!
## so multipe things
## 1. try multiple bootstrap node
## 2. try the bootstrap node query several times (20 ?) until there are substantial nodes
## 3. prune "bad nodes" that time out (or put them in a separate list)
## 4. udp failures should not end the program 

## yeah bootstrap returns one node which can be bad so
## need multiple initial nodes
## need to run initial pass several times until routing table is big
## need pruning of routing table
## exception's shouldnt close function! 
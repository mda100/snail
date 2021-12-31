from random import getrandbits
from bencodepy import encode, decode

## Step 1. - Crawling to Find Peers ##

# open magnet link : magnet:?xt=urn:btih:5A6194C4E92A459A1313B7A4E9F7A9EB18FB9205&dn=Spider-Man+No+Way+Home+%282021%29+720p+English+Pre-DVDRip+x264+AAC+2&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.dler.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fopentracker.i2p.rocks%3A6969%2Fannounce&tr=udp%3A%2F%2F47.ip-51-68-199.eu%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2920%2Fannounce&tr=udp%3A%2F%2Ftracker.pirateparty.gr%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce
# parse magnet uri 
info_hash = bytes.fromhex("5A6194C4E92A459A1313B7A4E9F7A9EB18FB9205") # 40 characters in hex from url which is in the 2**160 space -> convert to bytes

BOOTSTRAP_NODES = [
  'router.bittorrent.com:6881',
  'router.utorrent.com:6881',
  'dht.transmissionbt.com:6881'
  ]

intial_nodes = [[node[:-4],int(node[-4:])] for node in BOOTSTRAP_NODES] #format [["<host>", <port>], ["<host>", <port>], ...]

node_id = getrandbits(160)

peers = []
## set up UDP connection 
## distance metric


for node in intial_nodes:
    t = "aa" # add produce transaction id number
    q = "get_peers"
    a = {
        "id" : node_id,
        "info_hash" : info_hash
        }
    ping = build_query(q="ping",a={"id":node_id},t=t)
    #response = send(node, ping) -> maybe use this to initiate contact with node, def as a paramter for routing table
    query = build_query(q=q, a=a, t=t)
    # response = send(node, query)
    # if yes -> add peers to peer list and begin handshake // end this program and print peer list 
    # if no -> add nodes to routing table and do next 




## KRPC messages
#  review this code carefully and type check it 
# Queries 
def build_query( q: str, a: dict, t: str = "aa", y: str = "q") -> str:
    if y != 'q':
        raise Exception('y parameter of query must be q')
    def ping_query (id: str) -> dict:
        arguments = {
            "id" : id #"<querying nodes id> ex: abcdefghij0123456789"
            }
        return arguments
    def find_node_query (id: str, target: str) -> dict:
        arguments = {
            "id" : id, #"<querying nodes id>"
            "target" : target #"<id of target node>"
            }
        return arguments
    def get_peers_query (id: str, info_hash: str) -> dict:
        arguments = {
            "id" : id, #"<querying nodes id>",
            "info_hash" : info_hash #"<20-byte infohash of target torrent>"
            }
        return arguments
    def announce_peer_query (id: str, implied_port: int, info_hash: str, port: int, token: str) -> dict:
        arguments = {
            "id" : id, #"<querying nodes id>"
            "implied_port": implied_port, #"<0 or 1> - binary literal",
            "info_hash" : info_hash, #"<20-byte infohash of target torrent>",
            "port" : port, #"<port number> -interger literal",
            "token" : token, #"<opaque token>"
            }
        return arguments
    if q == "ping":
        arguments = ping_query(a)
    elif q == "find_node":
        arguments = find_node_query(a)
    elif q == "get_peers":
        arguments = get_peers_query(a)
    elif q == "announce_peer":
        arguments = announce_peer_query(a)
    else:
        arguments = 0
        raise Exception('q parameter must be "ping", "find_node", "get_peers", or "announce_peer"')
    query = {
        "t":t,
        "y":y,
        "q":q,
        "a":arguments
        }
    return encode(query)
    
arguments =  {"id" : "<querying nodes id> ex: abcdefghij0123456789"}
response = {"id" : "<queried nodes id> ex: mnopqrstuvwxyz123456"}
Query = {
    "t":"aa",
    "y":"q",
    "q":"ping",
    "a":arguments
    }
benconded_query = encode(Query)
Response = {
    "t":"aa",
     "y":"r",
    "r": response}
bencoded_response = encode(Response)

# Responses 
def build_response (query: str, r: dict, t: str = "aa", y: str = "r") -> str:
    if y != 'r':
        raise Exception('y parameter of response must be r')
    def ping_response (id: str) -> dict:
        response = {
            "id" : id #"<queried nodes id>"
            }
        return response
    def find_node_response (id: str, nodes: str) -> dict:
        response = {
            "id" : id, #"<queried nodes id>"
            "nodes" : nodes#"<compact node info> ex: def456..."
            }
        return response
    def get_peers_response_yes_peers (id: str, token: str, values: list) -> dict:
        response = {
            "id" : id, #"<queried nodes id>",
            "token" : token, #"<opaque write token>",
            "values" : values #[ "<peer 1 info string>","<peer 2 info string>"]
            }
        return response
    def get_peers_response_no_peers (id: str, token: str, nodes: str) -> dict:
        response = {
            "id" : id, #"<queried nodes id>",
            "token" : token, #"<opaque write token>",
            "nodes" : nodes #"<compact node info>"
            }
        return response
    def announce_peer_response (id: str) -> dict:
        response = {"id" : id} #"<queried nodes id>"}
        return response

    if query == "ping":
        response = ping_response(r)
    elif query == "find_node":
        response = find_node_response(r)
    elif query == "get_peers" and r["values"]:
        response = get_peers_response_yes_peers(r)
    elif query == "get_peers" and not r["values"]:
        response = get_peers_response_no_peers(r)
    elif query == "announce_peer":
        response = announce_peer_response(r)
    else:
        response = 0
        raise Exception('query must be a "ping", "find_node", "get_peers", or "announce_peer"')
    response = {
        "t":t,
        "y":y,
        "r": response
        }
    return encode(response)

# Errors
def build_error(e: int, t: str = "aa", y: str = "e") -> str:
    if y != 'e':
        raise Exception('y parameter of error must be e')
    if e == 201:
        mssg = 'Generic Error'
    if e == 202:
        mssg = 'Server Error'
    if e == 203:
        mssg = 'Protocol Error'
    if e == 204:
        mssg = 'Method Unknown'
    else:
        mssg = 0
        raise Exception('e parameter must be 201, 202, 203, or 204')
    error = {
        "t": t,
        "y": y,
        "e": [e, mssg]
        }
    return encode(error)





## routing table 
## routing table updater 
## main loop

## Step 2. - Query Peers for File Pieces ##
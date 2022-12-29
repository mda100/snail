from socket import inet_ntoa, socket, AF_INET, SOCK_DGRAM, timeout, gethostbyname
from sys import byteorder
from random import getrandbits
from bencodepy import encode, BencodeDecoder, BencodeDecodeError
import logging

## GLOBALS ##
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
TIMEOUT = 0.1

# TODO: class for krpc message - packing and unpacking, all server requests and responses
# TODO: implement routing table
# TODO: protocol for finding peers for a target hash
# TODO: protocol for node joining the DHT and staying alive, provividing info 
# TODO: ensure good error logging and handling, dry simple code
# TODO: create test cases, set up github actions
# TODO: make the node requests asynchronous 

class Node:
    def __init__ (self, buffer: bytearray) -> None:
        if len(buffer) is not 26:
            logging.warning(BufferError, 'bytes buffer of node instantiation is wrong size')
            raise BufferError
        self.compact_info = bytes(buffer)
        self.id = bytes(buffer[0:20])
        self.address = (inet_ntoa(bytes(buffer[20:24])), int.from_bytes((buffer[24:26]),'big'))
        self.alive = True

class Bucket:
    def __init__ (self, nodes: list[Node], range: list[int, int]) -> None:
        self.range = range
        self.nodes = nodes

    def add_node(self, node: Node) -> None:
        self.nodes.append(node)

    def delete_bucket(self) -> None:
        del self

class RoutingTable:
    def __init__ (self, nodes: list[Node], id: bytearray) -> None:
        self.parent_id = id
        self.buckets = [nodes]
    
    def add_node(self, node: Node) -> None:


class SelfNode:
    def __init__ (self, bootstrap_nodes: list = []):
        self.id = getrandbits(160).to_bytes(20, byteorder)
        self.routing_table = bootstrap_nodes

    def ping (self):
        query = {
            "t":"aa",
            "y":"q",
            "q":"ping",
            "a":{
                "id": self.id
                }
            }
        return encode(query)

    def find_node (self, target: bytes):
        query = {
            "t":"aa",
            "y":"q",
            "q":"find_node",
            "a": {
                "id": self.id,
                "target": target
                }
            }
        return encode(query)


    def get_peers (self, info_hash: bytes):
        query = {
            "t":"aa",
            "y":"q",
            "q":"get_peers",
            "a":{
                "id": self.id,
                "info_hash" : info_hash
                }
            }
        return encode(query)
    
    def request(s: socket, address: tuple, query: bytes) -> tuple or TimeoutError:
        try:
            s.settimeout(TIMEOUT)
            s.sendto(query, address)
            r = s.recvfrom(1024)
            return r
        except timeout as e:
            logging.info(address,e)
            return e
    
    def parse(r: tuple) -> dict or None:
        try:
            results = BencodeDecoder(encoding='utf-8').decode(r[0])
            match results['y']:
                case 'r':
                    return results['r']
                case 'e':
                    logging.info('request error: ', results['e'][0], results['e'][1])
                    return None
                case _:
                    logging.info('unexpected response key - y: ', results['y'])
                    return None
        except BencodeDecodeError or UnicodeError as e:
            logging.info('decoding error: ', e)
            return None
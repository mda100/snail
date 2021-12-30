# ping1 didn't work so heres the sequel from https://stackoverflow.com/questions/6123263/hello-world-for-an-existing-dht

from bencodepy import encode, decode
import random
import socket


# Generate a 160-bit (20-byte) random node ID.
my_id = ''.join([chr(random.randint(0, 255)) for _ in range(20)])

# Create ping query and bencode it.
# "'y': 'q'" is for "query".
# "'t': '0f'" is a transaction ID which will be echoed in the response.
# "'q': 'ping'" is a query type.
# "'a': {'id': my_id}" is arguments. In this case there is only one argument -
# our node ID.
ping_query = {'y': 'q',
              't': '0f',
              'q': 'ping',
              'a': {'id': my_id}}
ping_query_bencoded = encode(ping_query)

server = ('87.98.162.88', 6881) # works (dht transmission)
# server = ('67.215.246.10', 6881) ## doesn't work
print(server)
# Send a datagram to a server and recieve a response.
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(ping_query_bencoded,
         server)
r = s.recvfrom(1024)
print(decode(r[0]))


# pinging 67.215.246.10:6881 works on checkhost . net
# something is not write with this 

# ohhhhhhhhhhh https://stackoverflow.com/questions/35645559/ping-a-bittorent-dht-bootstrap-node-could-not-get-a-answer
# my firewall is blocking udp traffic!! hmm


## ooohhhh shit 
## maybe those bootstrap nodes are out of date ??

# 87.98.162.88 (dht.transmissionbt.com) worked instantly
# i can also pull nodes from my utorrent! or whatever 

## cool so dht. transmission worked
## it pinged back 
## what is this v character?

## and these are the ones in qbittorrent source code! settingsPack.set_str(lt::settings_pack::dht_bootstrap_nodes, "dht.libtorrent.org:25401,router.bittorrent.com:6881,router.utorrent.com:6881,dht.transmissionbt.com:6881,dht.aelitis.com:6881");
##all thanks to https://www.reddit.com/r/torrents/comments/p9vfsa/cant_get_a_response_from_dht_bootstrap_server/
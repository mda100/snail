from bencodepy import encode, decode
## contactings for meta info files

## i have a ip and port from snail
## i set up a tcp connection (just like udp or http)

## extension messages 

request = encode({
    'msg_type': 0,
    'piece': 0
})

data = encode({
    'msg_type': 1,
    'piece': 0,
    'total_size': 3425
})

reject = encode({
    'msg_type': 2,
    'piece': 0,
})

# The metadata extension uses the extension protocol (specified in BEP 0010 ) to advertize its existence.
#  It adds the "ut_metadata" entry to the "m" dictionary in the extension header hand-shake message.
#  This identifies the message code used for this message. It also adds "metadata_size" to the 
#  handshake message (not the "m" dictionary) specifying an integer value of the number of bytes 
#  of the metadata.

# Example extension handshake message:

extension_header = encode({
    'm': {'ut_metadata', 3},
    'metadata_size': 31235
})

# standard handhake
# extension header
# request data


## tcp connection -> dial
## handshake string : \x13BitTorrent protocol\x00\x00\x00\x00\x00\x00\x00\x00\x86\xd4\xc8\x00\x24\xa4\x69\xbe\x4c\x50\xbc\x5a\x10\x2c\xf7\x17\x80\x31\x00\x74-TR2940-k8hj0wgej6ch
## 1. x13 
## 2. BitTorrent protocol
## 3. 8 reserved bytes set to 0 => see BEP 10 for extension
## 4. info hash 
## 5. peer_id => generate according to convention
##

## check if returned handshake has matching info hash

## copy the "message serializer" from jessii li

## https://stackoverflow.com/questions/7986672/bittorrent-extension-for-peers-to-send-metadata-files-clarifing
# https://stackoverflow.com/questions/52970941/download-the-metadata-from-peers-failed-by-bep-0009-golang
## copying the meta info connection thing because i don't really understand it

## given peer


## handshake string : \x13BitTorrent protocol\x00\x00\x00\x00\x00\x00\x00\x00\x86\xd4\xc8\x00\x24\xa4\x69\xbe\x4c\x50\xbc\x5a\x10\x2c\xf7\x17\x80\x31\x00\x74-TR2940-k8hj0wgej6ch

from bencodepy import encode, decode


BT_HEADER = b'\x13BitTorrent protocol\x00\x00\x00\x00\x00\x10\x00\x01'

EXT_ID = 20
EXT_HANDSHAKE_ID = 0
EXT_HANDSHAKE_MESSAGE = bytes([EXT_ID, EXT_HANDSHAKE_ID]) + encode({"m": {"ut_metadata": 1}})

import asyncio
import os
import struct
## refactoring of "mala"

class PeerConnection:
    def __init__(self, infohash):
        self.infohash = infohash
        self.peer_id = os.urandom(20) #may need different convention
        self.writer = None
        self.reader = None
        self.handshaked = False

    async def connect(self, ip, port, loop):
            self.reader, self.writer = await asyncio.open_connection(
                ip, port, loop=loop
            )

    def close(self):
            try:
                self.writer.close()
            except:
                pass

    def check_handshake(self, data):
            # Check BT Protocol Prefix
            if data[:20] != BT_HEADER[:20]:
                return False
            # Check InfoHash
            if data[28:48] != self.infohash:
                return False
            # Check support metadata exchange
            if data[25] != 16:
                return False
            return True

    def write_message(self, message):
        length = struct.pack(">I", len(message))
        self.writer.write(length + message)

    async def work(self):
        self.writer.write(BT_HEADER + self.infohash + self.peer_id)
        while True:
            if not self.handshaked:
                if self.check_handshake(await self.reader.readexactly(68)):
                    self.handshaked = True
                    self.write_message(EXT_HANDSHAKE_MESSAGE)
                else:
                    return self.close()

            total_message_length, msg_id = struct.unpack("!IB", await self.reader.readexactly(5))
            # Total message length contains message id length, remove it
            payload_length = total_message_length - 1
            payload = await self.reader.readexactly(payload_length)
            
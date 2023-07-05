from .Common import *

class DHTHeader(Serializer):
    __endian__: BIG_ENDIAN
    magic: DATA(2)
    format: BYTE
    reversed1: DATA(3)
    version: WORD
    mtime: Time64
    reversed2: DATA(8)
    localNodeID: DATA(20)
    reversed3: DATA(4)
    numNode: DWORD
    reversed4: DATA(4)

class CompactPeerInfo(Serializer):
    length: BYTE
    reversed: DATA(7)
    address: DATA(24)

    def __repr__(self):
        repr_str = f'{self.__class__.__name__}{{length={self.length}, '
        repr_str += f'reversed={self.reversed}, '
        if self.length == 18:
            ip_str = ':'.join(self.address[i:i+2].hex() for i in range(0, 16, 2))
            port_str = int.from_bytes(self.address[16:18], 'big')
        elif self.length == 6:
            ip_str = '.'.join(str(i) for i in self.address[:4])
            port_str = int.from_bytes(self.address[4:6], 'big')
        address_str = f'{ip_str}:{port_str}'
        repr_str += f'address={address_str}}}'
        return repr_str

class DHTContent(Serializer):
    info: CompactPeerInfo
    nodeID: DATA(20)
    reversed: DATA(4)

def parse(stream: FileReader):
    start_pos = stream.tell()
    _header = DHTHeader.parse(stream)
    class DHT(Serializer):
        header: DHTHeader
        contents: ARRAY(DHTContent, _header.numNode)
    stream.seek(start_pos)
    return DHT.parse(stream)
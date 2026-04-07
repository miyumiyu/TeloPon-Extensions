"""
Length-Delimited Protobuf Stream Reader
NDGRClient (MIT License) より移植
ref: https://github.com/tsukumijima/NDGRClient
"""


class ProtobufStreamReader:
    """NDGR メッセージサーバーの Length-Delimited Protobuf Streams を読み取る"""

    def __init__(self):
        self.buffer = bytearray()

    def add_chunk(self, chunk: bytes) -> None:
        self.buffer.extend(chunk)

    def _read_varint(self) -> tuple[int, int] | None:
        offset = 0
        result = 0
        i = 0
        while True:
            if offset >= len(self.buffer):
                return None
            current = self.buffer[offset]
            result |= (current & 0x7F) << i
            offset += 1
            i += 7
            if not (current & 0x80):
                break
        return offset, result

    def next_message(self) -> bytes | None:
        varint_result = self._read_varint()
        if varint_result is None:
            return None
        offset, varint = varint_result
        if offset + varint > len(self.buffer):
            return None
        message = bytes(self.buffer[offset:offset + varint])
        del self.buffer[:offset + varint]
        return message

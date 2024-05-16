import zlib
from enum import Enum
from typing import IO

from pygit.client import Client


class ObjectType(Enum):
    OBJ_COMMIT = 1
    OBJ_TREE = 2
    OBJ_BLOB = 3
    OBJ_TAG = 4
    OBJ_OFS_DELTA = 5
    OBJ_REF_DELTA = 1


def decode_pack_object(stream: IO[bytes]) -> bytes:

    next_val = reader.read(1)
    bits = bin(int.from_bytes(next_val, byteorder="big"))[2:].zfill(8)
    is_msb_set = bits[0]
    object_type = int(bits[1:4], 2)
    object_size = bits[4:]

    while is_msb_set == "1":
        next_val = reader.read(1)
        bits = bin(int.from_bytes(next_val, byteorder="big"))[2:].zfill(8)
        is_msb_set = bits[0]
        object_size += bits[1:]

    object_size = int(object_size, 2)
    data = zlib.decompress(reader.read(object_size))

    return data


if __name__ == "__main__":
    client = Client.ref_discovery("JonoKumarich", "pygit")

    reader = client.compute()

    response, header = reader.read(20).splitlines()
    assert response == b"0008NAK"

    magic_byte = header[0:4]
    version = int.from_bytes(header[4:8])
    num_objects = int.from_bytes(header[8:12])
    assert magic_byte == b"PACK"

    print(decode_pack_object(reader))

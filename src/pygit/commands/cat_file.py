from pathlib import Path
import zlib
from enum import Enum


class ObjectKind(Enum):
    TREE = 'tree'
    COMMIT = 'commit'
    BLOB = 'blob'


def cat_file(sha: str):

    if len(sha) != 40:
        raise NotImplementedError("Currently only supporting exact 40 byte SHA's.")

    folder_name = Path(".git") / "objects" / sha[0:2]

    # TODO: This currently holds the whole file in memory. We should probably stream the decode.
    # don't we kinda need to have everything in mem to print it out though?
    with open(folder_name / sha[2:], 'rb') as file:
        decoded = zlib.decompress(file.read())

    header, contents = decoded.split(b'\x00')
    object_type, size = header.split(b' ')

    object_type = object_type.decode()
    contents = contents[:-1].decode()
    size = int(size.decode())

    match object_type:
        case ObjectKind.BLOB.value:
            print(contents)
        case _:
            print(f"Object type of {object_type} not supported")




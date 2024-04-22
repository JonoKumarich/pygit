from typing import Protocol
from pathlib import Path
import zlib
from enum import Enum
from hashlib import sha1


class Kind(Enum):
    BLOB = "blob"
    TREE = "tree"
    COMMIT = "commit"


class Object:
    def __init__(self, body: bytes, kind: Kind) -> None:
        self.body = body
        self.kind = kind
        
    def size(self) -> int:
        return len(self.body)

    def header(self) -> bytes:
        return f"{self.kind.value} {self.size()}".encode()

    def content(self) -> bytes:
        return self.header() + b'\x00' + self.body

    def sha(self) -> str:
        return sha1(self.content()).hexdigest()

    def write(self):
        compressed = zlib.compress(self.content())
        sha = self.sha()
        output_file = Path(".git") / "objects" / sha[:2] / sha[2:]
        output_file.parent.mkdir(exist_ok=True, parents=True)
        output_file.write_bytes(compressed)

        # TODO: When to property vs method


def create_blob_from_file(path: str | Path) -> Object:
    # TODO: We should stream this through instead of reading all into memory
    with open(path, 'r') as f:
        contents = f.read().encode('utf-8')

    return Object(contents, Kind.BLOB)






from pathlib import Path
import zlib
from hashlib import sha1
import os



def hash_object(file: str | Path, write: bool):

    # TODO: We should definitely stream this through instead of reading all into memory
    with open(file, 'r') as f:
        contents = f.read().encode('utf-8')

    size = len(contents)

    unhashed = f"blob {size}".encode("utf-8")
    unhashed += b'\x00'
    unhashed += contents

    compressed = zlib.compress(unhashed)
    sha = sha1(unhashed).hexdigest()
    print(sha)

    if write:
        output_file = Path(".git") / "objects" / sha[:2] / sha[2:]
        output_file.parent.mkdir(exist_ok=True, parents=True)
        output_file.write_bytes(compressed)


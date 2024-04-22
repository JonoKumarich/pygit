from pathlib import Path
import zlib
from hashlib import sha1
from pygit.object import create_blob_from_file



def hash_object(file: str | Path, write: bool) -> None:

    blob = create_blob_from_file(file)

    if write:
        blob.write()

    print(blob.sha())


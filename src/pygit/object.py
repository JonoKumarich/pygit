from pathlib import Path
import zlib
from enum import Enum
from hashlib import sha1
from typing import Self
import os


class Kind(Enum):
    BLOB = "blob"
    TREE = "tree"
    COMMIT = "commit"


class Object:
    # TODO: When to property vs method
    def __init__(self, body: bytes, kind: Kind) -> None:
        self.body = body
        self.kind = kind
        
    def size(self) -> int:
        return len(self.body)

    def header(self) -> bytes:
        return f"{self.kind.value} {self.size()}".encode()

    def content(self) -> bytes:
        return self.header() + b'\x00' + self.body

    def sha(self) -> bytes:
        return sha1(self.content()).digest()

    def cat(self) -> str:
        return self.body.decode()[:-1]

    def write(self) -> None:
        compressed = zlib.compress(self.content())
        sha = self.sha().hex()
        output_file = Path(".git") / "objects" / sha[:2] / sha[2:]

        # Had some permission issues with python where it couldn't overwrite the files, so we just rm them instead
        try:
            os.remove(output_file)
        except OSError:
            pass

        output_file.parent.mkdir(exist_ok=True, parents=True)
        output_file.write_bytes(compressed)

    @classmethod
    def from_git(cls, sha: str) -> Self:
        if len(sha) != 40:
            raise NotImplementedError("Currently only supporting exact 40 byte SHA's.")

        folder_name = Path(".git") / "objects" / sha[0:2]

        # TODO: This currently holds the whole file in memory. We should probably stream the decode.
        # don't we kinda need to have everything in mem to print it out though?
        with open(folder_name / sha[2:], 'rb') as file:
            decoded = zlib.decompress(file.read())

        return cls.from_bytes(decoded)

    @classmethod
    def from_bytes(cls, input: bytes) -> Self:
        header, body = input.split(b'\x00', 1)
        kind, size = header.split(b' ', 1)

        assert int(size) == len(body), f"fatal: too-short {kind.decode()} object"

        return cls(body, Kind[kind.decode().upper()])

    @classmethod
    def from_file(cls, path: str | Path) -> Self:
        # TODO: We should stream this through instead of reading all into memory
        with open(path, 'r') as f:
            contents = f.read().encode('utf-8')

        return cls(contents, Kind.BLOB)

class Tree(Object):
    def __init__(self, body: bytes, kind: Kind) -> None:
        super().__init__(body, kind)

    def list_files(self) -> str:
        content = self.body
        files = []

        while True:
            next_null = content.find(b'\x00')
            file_code_length = content.find(b' ')
            if next_null == -1:
                break

            item_content = content[:next_null+21]
            content = content[next_null+21:]

            file_name = item_content[file_code_length+1:next_null].decode()

            files.append(file_name)

        return '\n'.join(files)

    @classmethod
    def from_path(cls, root: Path = Path('.')) -> Self:
        dirs = sorted(os.listdir(root))
        body = b''

        for name in dirs:
            # TODO: Apply the gitignore exclusions properly. Currently hardcoded
            if name in ['.git', 'venv', '.python-version', 'test', 'venv', '__pycache__', 'pygit.egg-info']:
                continue

            dir = root / name
            if os.path.isdir(dir):
                mode = '40000'
                next_tree = Tree.from_path(dir)
                sha = next_tree.sha()
            else:
                # FIXME: This is duplicate of hash_object, which was causing a circular import
                blob = Object.from_file(dir)
                blob.write()
                sha = blob.sha()
                mode = str(oct(os.stat(dir).st_mode))[2:]

            body += f'{mode} {name}'.encode()
            body += b'\x00'
            body += sha

        current_tree = cls(body=body, kind=Kind.TREE)
        current_tree.write()
        print(root, current_tree.sha().hex(), current_tree.content())

        return current_tree


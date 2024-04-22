from pathlib import Path
from typing import Optional
import zlib


def ls_tree(sha: str):
    filename = Path(".git") / "objects" / sha[:2] / sha[2:]
    
    with open(filename, 'rb') as file:
        decoded = zlib.decompress(file.read())

    header_end = decoded.find(b'\x00')
    header = decoded[:header_end]
    content = decoded[header_end+1:]

    object_type, size = header.split(b' ')

    if object_type != b'tree':
        raise ValueError("Can't ls-tree on non tree object")

    while True:
        next_null = content.find(b'\x00')
        file_code_length = content.find(b' ')
        if next_null == -1:
            break

        item_content = content[:next_null+21]
        content = content[next_null+21:]
        file_code = item_content[:file_code_length]

        file_name = item_content[file_code_length+1:next_null].decode()

        print(file_name)


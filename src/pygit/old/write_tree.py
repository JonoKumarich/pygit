import os
from pathlib import Path
from typing import Optional

from pygit.commands.hash_object import hash_object


def write_tree(home_dir: Path = Path('.')) -> str:
    dirs = sorted(os.listdir(home_dir))

    body = b''

    for name in dirs:
        # TODO: Apply the gitignore exclusions here. Currently hardcoded
        if name in ['.git', 'venv', '.python-version', 'test', 'venv', '__pycache__', 'pygit.egg-info']:
            continue

        dir = home_dir / name

        if os.path.isdir(dir):
            # sha = write_tree(dir)
            mode = '040000'
        else:
            sha = hash_object(dir, write=False)
            mode = str(oct(os.stat(dir).st_mode))[2:]

        body += f'{mode} {name}'.encode()
        body += b'\x00'
        body += sha.encode()

    size = str(len(body)).encode()
    contents = b'tree '
    contents += size
    contents += b'\x00'
    contents += body

    print(contents)




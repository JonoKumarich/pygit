from pathlib import Path
import os
import shutil

from pygit.object import Object, Tree

def init() -> None:
    home_path = Path(".git")

    test_path_exists = os.path.exists(home_path) and os.path.isdir(home_path)
    if test_path_exists:
        shutil.rmtree(home_path)
    
    os.mkdir(home_path)
    os.mkdir(home_path / "objects")
    os.mkdir(home_path / "refs")

    with open(home_path / "HEAD", 'x') as f:
        f.write("ref: refs/heads/main\n")


def hash_object(file: str | Path, write: bool) -> str:

    blob = Object.from_file(file)

    if write:
        blob.write()

    sha = blob.sha()
    print(sha)
    return sha.hex()


def cat_file(sha: str) -> str:

    file = Object.from_git(sha)
    output = file.cat()
    print(output)
    return output


def ls_tree(sha: str) -> str:
    tree = Tree.from_git(sha)
    files = tree.list_files()
    print(files)
    return files

def write_tree() -> str:
    tree = Tree.from_path()
    tree.write()
    sha = tree.sha().hex()
    print(sha)
    return sha


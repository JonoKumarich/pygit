from pathlib import Path
import os
import shutil

from pygit.object import Object, Kind, Tree

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


def hash_object(file: str | Path, write: bool) -> None:

    blob = Object.from_file(file)

    if write:
        blob.write()

    print(blob.sha())


def cat_file(sha: str) -> None:

    file = Object.from_git(sha)
    output = file.cat()
    print(output)


def ls_tree(sha: str) -> None:
    tree = Tree.from_git(sha)
    print(tree.list_files())



    

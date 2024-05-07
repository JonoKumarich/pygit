import os
import shutil
from pathlib import Path
from typing import Optional

from pygit import utils
from pygit.object import Commit, Object, Tree


def init() -> None:
    home_path = Path(".git")

    test_path_exists = os.path.exists(home_path) and os.path.isdir(home_path)
    if test_path_exists:
        shutil.rmtree(home_path)

    os.mkdir(home_path)
    os.mkdir(home_path / "objects")
    os.mkdir(home_path / "refs")
    os.mkdir(home_path / "refs" / "heads")

    with open(home_path / "HEAD", "x") as f:
        f.write("ref: refs/heads/main\n")


def hash_object(file: str | Path, write: bool) -> str:

    blob = Object.from_file(file)

    if write:
        blob.write()

    sha = blob.sha.hex()
    print(sha)
    return sha


def cat_file(sha: str) -> str:

    file = Object.from_git(sha)
    output = file.cat
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
    sha = tree.sha.hex()
    print(sha)
    return sha


def commit_tree(sha: str, message: str, parent: Optional[str]) -> str:
    commit = Commit.from_tree(sha, message, parent)
    commit.write()
    sha = commit.sha.hex()
    print(sha)
    return sha


def commit(message: str) -> str:
    sha = write_tree()

    ref_path = utils.head_ref()
    parent = utils.ref_sha(ref_path)

    commit_sha = commit_tree(sha, message, parent)

    with open(Path(".git") / ref_path, "w") as f:
        f.write(commit_sha)

    return commit_sha


def branch(name: str) -> None:
    ref_path = utils.head_ref()
    commit_sha = utils.ref_sha(ref_path)

    with open(Path(".git") / "refs" / "heads" / name, "w") as f:
        f.write(commit_sha)


def checkout(branch: str) -> None:
    new_head = f"ref: refs/head/{branch}"
    with open(Path(".git") / "HEAD", "w") as f:
        f.write(new_head)


def clone(url: str) -> str:
    raise NotImplementedError

from pathlib import Path


def head_ref() -> str:
    with open(Path(".git") / "HEAD", "r") as f:
        ref_path = f.read().split()[1]

    return ref_path


def ref_sha(ref_path: str) -> str:
    with open(Path(".git") / ref_path, "r") as f:
        sha = f.read().strip()

    return sha

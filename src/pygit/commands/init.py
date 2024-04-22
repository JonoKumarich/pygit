from pathlib import Path
import shutil
import os

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


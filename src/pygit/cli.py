import os
from pathlib import Path
import shutil

import typer

app = typer.Typer()


@app.command()
def init(dry_run: bool = False):
    home_path = Path('test' if dry_run else '.git')

    test_path_exists = os.path.exists(home_path) and os.path.isdir(home_path)
    if dry_run and test_path_exists:
        shutil.rmtree(home_path)
    
    os.mkdir(home_path)
    os.mkdir(home_path / "objects")
    os.mkdir(home_path / "refs")

    with open(home_path / "HEAD", 'x') as f:
        f.write("ref: refs/heads/main\n")

@app.command()
def cat_file():
    raise NotImplementedError


def main():
    app()


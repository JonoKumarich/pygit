from typing_extensions import Annotated
from typing import Optional

import typer

from pygit import commands


app = typer.Typer()


@app.command()
def init():
    commands.init()

@app.command()
def cat_file(
    sha: str, 
    pretty: Annotated[
        Optional[bool], 
        typer.Option(
            "--pretty", "-p", 
            help="Pretty-print the contents of <object> based on its type."
        )] = False
    ):

    if not pretty:
        raise NotImplementedError("Currently only -p supported")

    commands.cat_file(sha)

@app.command()
def hash_object(
        file: str,
        write: Annotated[bool, typer.Option("--write", "-w", help="Actually write the object into the object database.")] = False
    ):

    commands.hash_object(file, write)

@app.command()
def ls_tree(
        sha: str,
        name_only: Annotated[bool, typer.Option("--name-only", help="List only filenames (instead of the \"long\" output), one per line.")] = False
    ):

    if not name_only:
        raise NotImplementedError("Currently only name-only supported")

    commands.ls_tree(sha)

@app.command()
def write_tree():
    commands.write_tree()


def main():
    app()


import os
from pathlib import Path
import shutil
from typing_extensions import Annotated
from typing import Optional

import typer

from pygit import commands


app = typer.Typer()


@app.command()
def init(dry_run: bool = False):
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


def main():
    app()


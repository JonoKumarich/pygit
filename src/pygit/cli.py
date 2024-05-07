from typing import Optional

import typer
from typing_extensions import Annotated

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
            "--pretty",
            "-p",
            help="Pretty-print the contents of <object> based on its type.",
        ),
    ] = False,
):

    if not pretty:
        raise NotImplementedError("Currently only -p supported")

    commands.cat_file(sha)


@app.command()
def hash_object(
    file: str,
    write: Annotated[
        bool,
        typer.Option(
            "--write", "-w", help="Actually write the object into the object database."
        ),
    ] = False,
):

    commands.hash_object(file, write)


@app.command()
def ls_tree(
    sha: str,
    name_only: Annotated[
        bool,
        typer.Option(
            "--name-only",
            help='List only filenames (instead of the "long" output), one per line.',
        ),
    ] = False,
):

    if not name_only:
        raise NotImplementedError("Currently only name-only supported")

    commands.ls_tree(sha)


@app.command()
def write_tree():
    commands.write_tree()


@app.command()
def commit_tree(
    sha: str,
    message: Annotated[
        str,
        typer.Option("--message", "-m", help="A paragraph in the commit log message."),
    ],
    parent: Annotated[
        Optional[str],
        typer.Option("--parent", "-p", help="The 40 char sha of the parent commit"),
    ] = None,
):

    commands.commit_tree(sha, message, parent)


@app.command()
def commit(
    message: Annotated[
        str,
        typer.Option("--message", "-m", help="A paragraph in the commit log message."),
    ],
):
    if message is None:
        raise NotImplementedError("Message must be provided")

    commands.commit(message)


@app.command()
def clone(url: str):
    commands.clone(url)


def main():
    app()

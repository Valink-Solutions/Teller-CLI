import os
from typing import Union
import typer

from teller_cli.core.config import create_or_load_config_file
from teller_cli.core.utils import check_for_shared_url
from teller_cli.core.world import (
    chunk_and_upload,
    compress_folder,
    create_world,
    expand_downloaded,
    get_deep_info,
    get_info,
    grab_world,
)

from rich import print

from teller_cli.core.world import download

app = typer.Typer()


@app.command(
    name="upload",
    help="""
Takes a world's folder name or an absolute path to a world,
compresses and uploads it to ChunkVault-Lite.
""",
)
def upload_v2(folder_path: str = typer.Argument(...)):
    api_url, api_token, default_saves_folder = create_or_load_config_file("teller.toml")

    if not os.path.isabs(folder_path):
        folder_path = os.path.join(default_saves_folder, folder_path)

    if not os.path.exists(folder_path):
        print("> [bold red]World does not exist.")
        raise Exception

    _, _, _, vault_id = get_info(folder_path)

    world_id = grab_world(api_token, api_url, vault_id)

    if not world_id:
        world_id = create_world(api_token, api_url, folder_path)
    try:
        zip_file = compress_folder(folder_path)
    except Exception:
        print("> [bold red]Error compressing world.")

    try:
        chunk_and_upload(zip_file, world_id, api_url, api_token)
    except Exception:
        print("> [bold red]Error uploading snapshot of world!")

    os.remove(zip_file)


@app.command()
def config():
    print("not added yet!")
    pass


@app.command(help="""
Dumps all of the world info to the terminal. (and I mean all, It is unread-able)
""")
def info(world_path: str = typer.Argument(...)):
    _, _, default_saves_folder = create_or_load_config_file("teller.toml")

    print("> Grabbing world.")

    if not os.path.isabs(world_path):
        world_path = os.path.join(default_saves_folder, world_path)

    try:
        get_deep_info(world_path)
    except Exception as e:
        print(e)
        print("> Error grabbing world info.")


@app.command(
    name="download",
    help="""
Allows you to download a snapshot from either an ID or a shared URL    
"""
)
def download_snapshot(
    vault_item: str = typer.Argument(...),
    save_path: Union[str, None] = typer.Argument(default=None),
    replace: Union[bool, None] = typer.Option(default=False),
    save: Union[bool, None] = typer.Option(default=False),
):
    api_url, api_token, default_saves_folder = create_or_load_config_file("teller.toml")

    final_save_path = save_path if save_path else default_saves_folder

    if check_for_shared_url(vault_item):
        world_name, snapshot_id, file_name = download.from_owned(
            snapshot_id=vault_item, url=api_url, token=api_token
        )
    else:
        # file_name = download.from_shared(
        #     url=vault_item,
        #     save_folder=final_save_path
        # )
        file_name = "oopsie.zip"

    print("> Extracting snapshot into saves folder")

    try:
        expand_downloaded(
            world_name=world_name,
            file_name=file_name,
            save_path=final_save_path,
            snapshot_id=snapshot_id,
            replace=replace,
        )
    except Exception:
        print("> [bold red]Error downloading world.")

    if not save:
        os.remove(file_name)


__version__ = "0.3.2"

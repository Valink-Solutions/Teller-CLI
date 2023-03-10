import os
from typing import Union
import typer

from teller_cli.core import (
    chunk_and_upload,
    compress_folder,
    create_world,
    get_world,
    update_world_image,
)
from teller_cli.core.config import create_or_load_config_file
from teller_cli.core.utils import check_for_shared_url
from teller_cli.core.world import (
    chunk_and_upload_v2,
    compress_folder_v2,
    create_world_v2,
    expand_downloaded,
    get_deep_info,
    get_info,
    grab_world,
)

from rich import print

from teller_cli.core.world import download

app = typer.Typer()


@app.command()
def upload(folder_path: str = typer.Argument(...)):
    api_url, api_token, _ = create_or_load_config_file("teller.toml")

    try:
        file, size, name = compress_folder(folder_path)
    except Exception as e:
        print("Error Compressing and finding Folder\n\n")
        print(e)
        exit()

    world_id = get_world(api_token, api_url, name)

    if not world_id:
        world_id = create_world(api_token, api_url, name, size)

    try:
        update_world_image(folder_path, world_id, api_url, api_token)
    except Exception as e:
        print(e)
        print("Error updating world icon")

    try:
        chunk_and_upload(file, world_id, api_url, api_token)
        os.remove(file)
    except Exception as e:
        print(e)
        print("Error uploading snapshot of world!")


@app.command(name="uploadV2")
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
        world_id = create_world_v2(api_token, api_url, folder_path)
    try:
        zip_file = compress_folder_v2(folder_path)
    except Exception:
        print("> [bold red]Error compressing world.")

    try:
        chunk_and_upload_v2(zip_file, world_id, api_url, api_token)
    except Exception:
        print("> [bold red]Error uploading snapshot of world!")

    os.remove(zip_file)


@app.command()
def config():
    print("not added yet!")
    pass


@app.command()
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


@app.command(name="download")
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
        



__version__ = "0.2.0"

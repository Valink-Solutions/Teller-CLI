import typer

from teller_cli.core import chunk_and_upload, compress_folder, create_world, get_world
from teller_cli.core.config import create_or_load_config_file

app = typer.Typer()

@app.command()
def upload(folder_path: str = typer.Argument(...)):
    
    api_url, api_token = create_or_load_config_file("teller.toml")
    
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
        chunk_and_upload(file, world_id, api_url, api_token)
    except Exception as e:
        print(e)
        print("Error uploading snapshot of world!")
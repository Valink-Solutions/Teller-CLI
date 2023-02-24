import os
import shutil
import time
import base64

from rich.console import Console
from rich.table import Table
from rich.progress import Progress

import httpx

def format_bytes(bytes: int) -> str:
    if bytes < 1024:
        return f"{bytes} bytes"
    elif bytes < 1048576:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1073741824:
        return f"{bytes / 1048576:.2f} MB"
    else:
        return f"{bytes / 1073741824:.2f} GB"

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def compress_folder(folder_path):
    if not os.path.exists(folder_path):
        raise Exception(f"The folder {folder_path} does not exist.")

    # Get the name of the folder and its byte size
    folder_name = os.path.basename(folder_path)
    folder_size = get_folder_size(folder_path)

    # Compress the folder
    shutil.make_archive(folder_name, 'zip', folder_path)
    compressed_file = folder_name + '.zip'

    return compressed_file, folder_size, folder_name


def get_world(token: str, url: str, world_name: str):
    response = httpx.get(url=f"{url}/worlds/find/{world_name}", headers={"X-Space-App-Key": token})
        
    if not response.status_code == 200:
        return None
        
    data = response.json()
    
    world_id = data.get("key")
        
    return world_id

def encode_image(image_path: str):

    # Read the contents of the PNG file into a bytes object
    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    # Encode the image bytes as Base64 using the standard Base64 alphabet and no line breaks
    base64_str = base64.b64encode(image_bytes).decode('ascii')

    # Create a data URI using the Base64-encoded string and the PNG media type
    data_uri = f'data:image/png;base64,{base64_str}'
    
    return data_uri

def update_world_image(folder_path: str, world_id: str, url: str, token: str):
    
    icon_path = os.path.join(folder_path, "icon.png")
    
    response = httpx.patch(url=f"{url}/worlds/{world_id}", headers={"X-Space-App-Key": token, "Content-Type": "application/json"}, json={
        "image": encode_image(icon_path)
    })
    
    response.raise_for_status()

def create_world(token: str, url: str, world_name: str, world_size: int):
    
    response = httpx.post(url=f"{url}/worlds/", headers={"X-Space-App-Key": token, "Content-Type": "application/json"}, json={
        "name": world_name,
        "size": world_size
    })
    
    if not response.status_code == 200:
        print("Error Creating new world")
        exit()
        
    world_id = response.json()["world_id"]
    
    return world_id


def chunk_and_upload(file_path: str, world_id: str, url: str, token: str):
    
    chunk_size = 4194304 # 4mb LIMIT! ANY HIGHER CHUNKVAULT-LITE WILL THROW ERRORS!
    
    current_chunk = 0
    
    client = httpx.Client()
    
    total_size = os.path.getsize(file_path)
    
    file_name = os.path.basename(file_path)
    
    session_response = client.post(f"{url}/snapshots/upload", params={"file_name": file_name, "world_id": world_id}, headers={"X-Space-App-Key": token})
    
    session_response.raise_for_status()
    
    session_id = session_response.json()["session_id"]
        
    failed = 0    
    
    finished = False
    
    file_table = Table(title="[bold]ChunkVault-[bold purple]Lite [white]Upload", min_width=200)
    file_table.add_column("World ID", justify="left", style="cyan", no_wrap=True)
    file_table.add_column("Session ID", justify="left", style="cyan", no_wrap=True)
    file_table.add_column("Size", no_wrap=True)
    file_table.add_column("Name")
    
    progress = Progress(expand=True)
    
    file_table.add_row(world_id, session_id, format_bytes(total_size), file_name)
    
    console = Console()
    console.print(file_table)
    
    with progress:
        
        upload_task = progress.add_task("[cyan]Uploading...", total=total_size)
        
        with open(file_path, "rb") as f:
            while finished == False:
                
                if failed >= 3:
                    raise Exception
                
                f.seek(current_chunk)
                chunk = f.read(chunk_size)
                
                # print(f"\n\n content-range: bytes {current_chunk}-{current_chunk+chunk_size-1}/{total_size}")
            
                headers = {
                    "X-Space-App-Key": token,
                    "content-range": f"bytes {current_chunk}-{current_chunk+chunk_size-1}/{total_size}"
                }
                
                params = {
                    "file_name": file_name
                }
                
                looped_response = client.post(url=f"{url}/snapshots/upload/{session_id}", params=params, headers=headers, files={"file": chunk})
                
                if looped_response.status_code == 208:
                    current_chunk += chunk_size
                    continue
                    
                if not looped_response.status_code == 200:
                    f.seek(-chunk_size)
                    failed += 1
                    continue
                
                finished = looped_response.json()["finished"]
                
                current_chunk += chunk_size
                
                progress.update(upload_task, advance=chunk_size)
                
                if current_chunk >= total_size:
                    progress.update(upload_task, description="[green]Uploaded.")
                    finished = True
            
            
                
                
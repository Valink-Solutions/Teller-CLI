import base64
import os
import shutil
import httpx
import nbtlib
import zipfile

from rich import print
from rich.progress import Progress
from slugify import slugify


def chunk_and_upload_v2(file_path: str, world_id: str, url: str, token: str):
    if not os.path.exists(file_path):
        raise Exception

    client = httpx.Client()

    chunk_size = 4194304

    file_size = os.path.getsize(file_path)

    file_name = os.path.basename(file_path)

    # num_parts = math.ceil(file_size / chunk_size)

    snapshot_response = client.post(
        url=f"{url}/snapshots",
        json={"world_id": world_id, "size": file_size},
        headers={"X-Space-App-Key": token},
    )

    if snapshot_response.status_code != 200:
        print(snapshot_response.text)
        raise Exception

    snapshot = snapshot_response.json()

    print("> Grabbing session info.")

    session_response = client.post(
        url=f"{url}/snapshots/{snapshot.get('key')}/session",
        params={"name": file_name},
        headers={"X-Space-App-Key": token},
    )

    if session_response.status_code != 200:
        print(session_response.text)
        raise Exception

    session_id = session_response.json()["key"]

    print(f"> Session grabbed: [cyan]{session_id}")

    failed = 0

    finished = False

    current_chunk = 0

    part = 1

    print("> [bold green]Starting chunked upload.")
    
    progress = Progress(expand=True)
    
    with progress:
        try:
            upload_task = progress.add_task(
                f"[cyan]Uploading part: {part}...",
                total=file_size
            )
            
            with open(file_path, "rb") as f:
                while finished is False:
                    if failed >= 3:
                        raise Exception

                    f.seek(current_chunk)
                    chunk = f.read(chunk_size)

                    looped_response = client.post(
                        url=f"{url}/snapshots/{snapshot.get('key')}/session/{session_id}/upload",
                        files={"file": chunk},
                        params={"name": file_name, "part": part},
                        headers={"X-Space-App-Key": token},
                    )

                    if looped_response.status_code == 208:
                        print(f"> [bold orange]Request Failed: {looped_response.text}")
                        current_chunk += chunk_size
                        part += 1
                        continue

                    if not looped_response.status_code == 200:
                        print(f"> [bold red]Request Failed: {looped_response.text}")
                        f.seek(0)
                        failed += 1
                        continue

                    current_chunk += chunk_size
                    part += 1

                    progress.update(
                        upload_task,
                        advance=chunk_size,
                        description=f"[cyan]Uploading part: {part}..."
                    )

                    if current_chunk >= file_size:
                        finished = True
                        progress.update(upload_task, description="[green]Finsihed.")

                        print("> [bold green]All parts uploaded.")

        except Exception or KeyboardInterrupt as e:
            
            if e == KeyboardInterrupt:
                print("> [bold red]Canceled file upload, removing snapshot.")
            else:
                print("> [bold red]Upload failed removing snapshot.")
            
            progress.update(upload_task, description="[bold red]Failed.")
            
            delete_response = client.delete(
                url=f"{url}/snapshots/{snapshot.get('key')}/session/{session_id}/upload",
                params={"name": file_name},
                headers={"X-Space-App-Key": token},
            )
            
            if delete_response.status_code != 200:
                print(delete_response.text)

            raise Exception

    print("> Finishing session with backend.")

    try:
        finished_resposne = client.patch(
            url=f"{url}/snapshots/{snapshot.get('key')}/session/{session_id}/upload",
            params={"name": file_name},
            headers={"X-Space-App-Key": token},
        )
        finished_resposne.raise_for_status()
    except Exception:
        print(finished_resposne.text)
        raise Exception

    print("> [bold green]Snapshot upload finished.")


def compress_folder_v2(folder_path):
    print(f"> Finding folder '{folder_path}'")

    if not os.path.exists(folder_path):
        raise Exception(f"The folder {folder_path} does not exist.")

    # Get the name of the folder and its byte size
    folder_name = os.path.basename(folder_path)

    print(f"> Found folder: [cyan]{folder_name}")

    print(f"> Compressing folder: [cyan]{folder_name}")

    # Create a zip file for the folder
    zip_filename = folder_name + ".zip"

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add all files in the folder to the zip file
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

    return zip_filename


def encode_icon(world_path: str):
    icon_path = os.path.join(world_path, "icon.png")

    if not os.path.exists(icon_path):
        raise Exception

    # Read the contents of the PNG file into a bytes object
    with open(icon_path, "rb") as f:
        image_bytes = f.read()

    # Encode the image as Base64 using the standard Base64 alphabet and no line breaks
    base64_str = base64.b64encode(image_bytes).decode("ascii")

    # Create a data URI using the Base64-encoded string and the PNG media type
    data_uri = f"data:image/png;base64,{base64_str}"

    return data_uri


def get_info(world_path: str):
    if not os.path.exists(world_path):
        raise Exception

    world_data = nbtlib.load(os.path.join(world_path, "level.dat"))

    level_name = world_data["Data"]["LevelName"]
    seed = nbtlib.serialize_tag(world_data["Data"]["WorldGenSettings"]["seed"]).split(
        "L"
    )[0]
    difficulty = nbtlib.serialize_tag(world_data["Data"]["Difficulty"]).split("b")[0]

    vault_id = f"{seed}-{slugify(level_name, max_length=15)}"

    # print(f"World Vault ID: {vault_id}")

    return level_name, seed, difficulty, vault_id


def get_deep_info(world_path: str):
    if not os.path.exists(world_path):
        print(f"> [bold red]Error finding world at: [cyan]'{world_path}'")
        raise Exception

    print(f"> World {world_path} found.")
    try:
        world_data = nbtlib.load(os.path.join(world_path, "level.dat"))
    except Exception as e:
        print(e)
        raise Exception
    # json_str = json.dumps(nbtlib.serialize_tag(world_data['Data']), ensure_ascii=False)
    # json_obj = json.loads(json_str)

    # print_json(json_obj)
    print(world_data["Data"])


def get_folder_size(world_path: str):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(world_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    return total_size


def grab_world(token: str, url: str, vault_id: str):
    print(f"> Attempting to grab world: [cyan]{vault_id}")

    response = httpx.get(
        url=f"{url}/worlds/{vault_id}", headers={"X-Space-App-Key": token}
    )

    if not response.status_code == 200:
        print(f"> [bold orange]World: {vault_id} doesnt seem to exist yet.")
        return None

    return response.json()["key"]


def create_world_v2(token: str, url: str, world_path: str):
    name, seed, difficulty, vault_id = get_info(world_path)

    print(f"> Attempting to create new world: [cyan]{name}")

    total_size = get_folder_size(world_path)

    try:
        icon_data = encode_icon(world_path)
    except Exception as e:
        print(e)
        icon_data = None

    response = httpx.post(
        url=f"{url}/worlds",
        params={"suggested_key": vault_id},
        headers={"X-Space-App-Key": token},
        json={
            "name": name,
            "seed": seed,
            "difficulty": difficulty,
            "size": total_size,
            "image": icon_data,
        },
    )

    if not response.status_code == 200:
        print(response.text)
        print("[bold red]Error Creating new world!")
        exit()

    world_id = response.json()["key"]

    return world_id


def expand_downloaded(
    world_name: str,
    file_name: str,
    save_path: str,
    snapshot_id: str,
    replace: bool = False,
):
    
    try:
        _, _, _, vault_id = get_info(os.path.join(save_path, world_name))

        if vault_id == snapshot_id and not replace:
            print("> [orange]Found similar world, altering name.")
            world_name = f"{world_name}-chunkvault"
            if os.path.exists(os.path.join(save_path, world_name)):
                world_name = f"{world_name} (1)"
    except Exception:
        pass

    final_save_path = os.path.join(save_path, world_name)
    try:

        if replace:
            print("> [orange]Removing old version of world.")
            shutil.rmtree(final_save_path)
            
        os.mkdir(final_save_path)

        shutil.unpack_archive(file_name, final_save_path, "zip")

    except Exception as e:
        print(e)
        raise Exception

    print("> [bold green]Finished extracting world")

    print("> [bold green]Happy playing :)")

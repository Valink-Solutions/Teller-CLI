import os
import httpx

from rich import print


def from_owned(snapshot_id: str, url: str, token: str):
    client = httpx.Client()

    print(f"> Grabbing snapshot: [cyan]{snapshot_id}")

    snapshot_response = client.get(
        url=f"{url}/snapshots/{snapshot_id}", headers={"X-Space-App-Key": token}
    )

    if snapshot_response.status_code != 200:
        print(f"> [bold red]Server Error: {snapshot_response.text}")
        raise Exception

    snapshot = snapshot_response.json()

    world_id = snapshot["world_id"]

    print(f"> Grabbing world: [cyan]{world_id}")

    world_response = client.get(
        url=f"{url}/worlds/{world_id}", headers={"X-Space-App-Key": token}
    )

    if world_response.status_code != 200:
        print(f"> [bold red]Server Error: {world_response.text}")
        raise Exception

    world = world_response.json()

    all_parts = snapshot.get("parts")

    filename = f"{snapshot.get('name')}.zip"

    part = 1

    print("> Attempting to start download.")

    try:
        while part <= all_parts:
            print(f"> Attempting download of part: [cyan]{part}")

            response = client.get(
                url=f"{url}/snapshots/{snapshot_id}/download",
                params={"part": part},
                headers={"X-Space-App-Key": token},
                timeout=None,
            )

            if response.status_code == 204:
                break

            if not response.status_code == 200:
                print(f"> [bold red]Download failed: {response.text}")
                raise Exception

            with open(filename, "ab") as f:
                f.write(response.content)

            part += 1
    except Exception:
        
        if os.path.exists(filename):
            print("> [bold red]Removing temp file.")
            os.remove(filename)

        print("> [bold red]Please try again later.")
        exit()

    print("> World downloaded successfully.")

    return world["name"], snapshot["key"], filename


def from_shared():
    pass

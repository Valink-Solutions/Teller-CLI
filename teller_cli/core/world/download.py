import math
import os
import httpx

from rich import print
from rich.progress import Progress
from urllib.parse import urlparse


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

    print("> [bold green]Starting chunked download.")

    finished = False

    failed = 0

    try:
        progress = Progress(expand=True)

        with progress:
            download_task = progress.add_task(
                f"> [cyan]Downloading part: {part}/{all_parts}...", total=int(all_parts)
            )
            while finished is False:
                try:
                    if failed >= math.ceil(all_parts / 3):
                        raise Exception

                    if part >= all_parts:
                        finished = True

                    response = client.get(
                        url=f"{url}/snapshots/{snapshot_id}/download",
                        params={"part": part},
                        headers={"X-Space-App-Key": token},
                        timeout=None,
                    )

                    if response.status_code == 204:
                        break

                    if not response.status_code == 200:
                        print(f"> [bold red]Download failed: part {part} error.")
                        failed += 1
                        # raise Exception
                        continue

                    with open(filename, "ab") as f:
                        f.write(response.content)

                    progress.update(
                        download_task,
                        advance=1,
                        description=f"> [cyan]Downloading part: {part}/{all_parts}...",
                    )

                    part += 1
                except Exception:
                    progress.update(download_task, description="> [bold red]Failed.")

                    if os.path.exists(filename):
                        print("> [bold red]Removing temp file.")
                        os.remove(filename)

                    print("> [bold red]Please try again later.")
                    exit()

            progress.update(download_task, description="> [green]Finsihed.")

    except KeyboardInterrupt:
        progress.update(download_task, description="> [bold red]Stopped.")

        print("> [red bold]Download Stopped.")

        if os.path.exists(filename):
            print("> [bold red]Removing temp file.")
            os.remove(filename)

        print("> [bold red]Please try again later.")
        exit()

    print("> World downloaded successfully.")

    return world["name"], snapshot["world_id"], filename


def from_shared(url: str):
    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc
    world_id = parsed_url.path.split("/")[-1]

    client = httpx.Client()

    print(f"> Grabbing world: [cyan]{world_id}")

    world_response = client.get(url=f"{base_url}/api/public/worlds/{world_id}")

    if world_response.status_code != 200:
        print(f"> [bold red]Server Error: {world_response.text}")
        raise Exception

    world = world_response.json()

    all_parts = world.get("parts")

    filename = f"{world.get('name')}.zip"

    part = 1

    print("> [bold green]Starting chunked download.")

    finished = False

    failed = 0

    try:
        progress = Progress(expand=True)

        with progress:
            try:
                download_task = progress.add_task(
                    f"> [cyan]Downloading part: {part}/{all_parts}...",
                    total=int(all_parts),
                )

                while finished is False:
                    if failed >= math.ceil(all_parts / 3):
                        raise Exception

                    if part >= all_parts:
                        finished = True

                    response = client.get(
                        url=f"{base_url}/api/public/worlds/{world_id}/download",
                        params={"part": part},
                        timeout=None,
                    )

                    if response.status_code == 204:
                        break

                    if not response.status_code == 200:
                        print(f"> [bold red]Download failed: {response.text}")
                        raise Exception

                    with open(filename, "ab") as f:
                        f.write(response.content)

                    progress.update(
                        download_task,
                        advance=1,
                        description=f"> [cyan]Downloading part: {part}/{all_parts}...",
                    )

                    part += 1
            except Exception:
                progress.update(download_task, description="> [bold red]Failed.")

                if os.path.exists(filename):
                    print("> [bold red]Removing temp file.")
                    os.remove(filename)

                print("> [bold red]Please try again later.")
                exit()

            progress.update(download_task, description="> [green]Finsihed.")
    except KeyboardInterrupt:
        progress.update(download_task, description="> [bold red]Stopped.")

        print("> [red bold]Download Stopped.")

        if os.path.exists(filename):
            print("> [bold red]Removing temp file.")
            os.remove(filename)

        print("> [bold red]Please try again later.")
        exit()

    print("> World downloaded successfully.")

    return world["name"], world_id, filename

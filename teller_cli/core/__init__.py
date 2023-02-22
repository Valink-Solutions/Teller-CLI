import os
import shutil
import time

import httpx

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

# def chunk_and_upload(file_path: str, world_id: str, url: str, token: str):
    
#     client = httpx.Client()
    
#     # Set the chunk size in bytes
#     chunk_size = 2048 * 1024
    
#     current_chunk = 0
    
#     if "/" in file_path:
#         name = file_path.split("/")
#     else:
#         name = file_path

#     # Open the file and read the total size
#     with open(file_path, "rb") as file:
#         session_id = None
#         total_size = len(file.read())
#         file.seek(current_chunk)
#         while True:

#             # If this is the first chunk, create a new upload session
#             if session_id is None:
#                 # Read the next chunk of data
#                 chunk = file.read(chunk_size)

#                 # If there is no more data, break out of the loop
#                 if not chunk:
#                     break
                
#                 print(f"\nCurrent range: {current_chunk}-{current_chunk+chunk_size-1}/{total_size}\n")
                
#                 headers = {
#                     "world-id": world_id,
#                     "file-name": name,
#                     "X-Space-App-Key": token,
#                     "content-range": f"bytes {current_chunk}-{current_chunk+chunk_size-1}/{total_size}"
#                 }
#                 files = {"file": chunk}
#                 response = client.post(f"{url}/snapshots/", headers=headers, files=files)
                
#                 if not response.status_code == 200:
#                     raise Exception
                
#                 session_id = response.json()["session_id"]
#                 current_chunk += chunk_size
#                 time.sleep(1)
#             else:
#                 # Read the next chunk of data
#                 chunk = file.read(chunk_size)

#                 # If there is no more data, break out of the loop
#                 if not chunk:
#                     break
                
#                 print("session_id call")
#                 print(f"\nCurrent range: {current_chunk}-{current_chunk+chunk_size-1}/{total_size}\n")
#                 success = False
#                 while not success:
#                     try:
#                         headers = {
#                             "world-id": world_id,
#                             "file-name": name,
#                             "session-id": session_id,
#                             "X-Space-App-Key": token,
#                             "content-range": f"bytes {current_chunk}-{current_chunk+chunk_size-1}/{total_size}"
#                         }
#                         files = {"file": chunk}
#                         session_response = client.post(f"{url}/snapshots/", headers=headers, files=files)
                        
#                         if not session_response.status_code == 200:
#                             print("\n\n IM BROKEN (SECOND UPLOAD) \n\n")
#                             print(session_response.text)
                        
#                             if session_response.status_code == 208:
#                                 continue
                        
#                             if session_response.json()["finsihed"] == False:
#                                 break
                            
#                             raise Exception
                        
#                         if session_response.json()["finsihed"] == True:
#                             success = True
                        
#                         session_id = session_response.json()["session_id"] # update session_id after successful upload
#                         current_chunk += chunk_size
#                         time.sleep(1)
#                     except:
#                         # Wait for a short time before retrying
#                         time.sleep(1)
#                         pass


def chunk_and_upload(file_path: str, world_id: str, url: str, token: str):
    
    chunk_size = 2048 * 1024
    
    current_chunk = 0
    
    client = httpx.Client()
    
    total_size = os.path.getsize(file_path)
    
    file_name = os.path.basename(file_path)
    
    with open(file_path, "rb") as f:
        chunk = f.read(chunk_size)
            
        print(f"\n\n content-range: bytes {current_chunk}-{current_chunk+chunk_size-1}/{total_size}")
        
        headers = {
            "world-id": world_id,
            "file-name": file_name,
            "X-Space-App-Key": token,
            "content-range": f"bytes {current_chunk}-{current_chunk+chunk_size-1}/{total_size}"
        }
        
        initial_response = client.post(url=f"{url}/snapshots/", headers=headers, files={"file": chunk})
        
        if not initial_response.status_code == 200:
            raise Exception
        
        session_id = initial_response.json()["session_id"]
        
        current_chunk += chunk_size
        
    finished = False
    with open(file_path, "rb") as f:
        while finished == False:
            f.seek(current_chunk)
            chunk = f.read(chunk_size)
            
            print(f"\n\n content-range: bytes {current_chunk}-{current_chunk+chunk_size-1}/{total_size}")
        
            headers = {
                "world-id": world_id,
                "file-name": file_name,
                "session-id": session_id,
                "X-Space-App-Key": token,
                "content-range": f"bytes {current_chunk}-{current_chunk+chunk_size-1}/{total_size}"
            }
            
            looped_response = client.post(url=f"{url}/snapshots/", headers=headers, files={"file": chunk})
            
            if looped_response.status_code == 208:
                continue
                
            if not looped_response.status_code == 200:
                raise Exception
            
            finished = looped_response.json()["finished"]
            
            current_chunk += chunk_size
            
            if current_chunk >= total_size:
                finished = True
    
    os.remove(file_path)
            
            
                
                
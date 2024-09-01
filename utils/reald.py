# from dotenv import load_dotenv
# load_dotenv()
# from rdapi import RD
# from requests import get
# rd = RD()
# def shot_bird(link,dir=None):
#     dir=dir if dir else "."
#     ba=rd.unrestrict.link(link=link).json()
#     print("Downloading: {ba['filename']} \n Size: {ba['size']}\nlink: {ba['download']}")
#     ln = ba["download"].replace("http://", "https://")
#     bt=get(ln,stream=True)
#     with open(f"{dir}/{ba['filename']}","wb") as f:
#         f.write(bt.content)
#     return f"{dir}/{ba['filename']}"

###########################
from dotenv import load_dotenv
load_dotenv()
from rdapi import RD
from requests import get
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

rd = RD()

def download_chunk(url, start, end, dir, filename, part_num):
    headers = {'Range': f'bytes={start}-{end}'}
    response = get(url, headers=headers, stream=True)
    chunk_path = f"{dir}/{filename}.part{part_num}"
    print(f"Downloading chunk: {chunk_path}")
    with open(chunk_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return chunk_path

def merge_chunks(filename, dir, num_chunks):
    with open(f"{dir}/{filename}", "wb") as outfile:
        for i in range(num_chunks):
            chunk_path = f"{dir}/{filename}.part{i}"
            print(f"Merging chunk: {chunk_path}")
            with open(chunk_path, "rb") as infile:
                outfile.write(infile.read())
            os.remove(chunk_path)

def shot_bird(link, dir=None, num_chunks=4):
    print(f"Generating link for: {link}")
    dir = dir if dir else "."
    if not os.path.exists(dir):
        os.makedirs(dir)
    try:
        ba = rd.unrestrict.link(link=link).json()
    except Exception as e:
        print(f"Failed to generate download link for {link}. Error: {e}")
        return None
    print(f"Download link generated: {ba['download']}")
    print(f"Downloading: {ba['filename']} \n Size: {ba['filesize']}\nlink: {ba['download']}")
    ln = ba["download"].replace("http://", "https://")
    
    file_size = int(ba['filesize'])
    if file_size == 0:
        print(f"File size is zero for {ba['filename']}. Downloading as a single chunk.")
        response = get(ln, stream=True)
        file_path = f"{dir}/{ba['filename']}"
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return file_path
    
    chunk_size = file_size // num_chunks
    
    with ThreadPoolExecutor(max_workers=num_chunks) as executor:
        futures = []
        for i in range(num_chunks):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < num_chunks - 1 else file_size - 1
            futures.append(executor.submit(download_chunk, ln, start, end, dir, ba['filename'], i))
        
        for future in as_completed(futures):
            future.result()
    
    merge_chunks(ba['filename'], dir, num_chunks)
    return f"{dir}/{ba['filename']}"


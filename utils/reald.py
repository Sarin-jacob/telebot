
import asyncio
import re
from time import sleep
from info import PARALLEL_DOWNLOADS
from dotenv import load_dotenv
load_dotenv()
from rdapi import RD
from requests import get
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from urllib.parse import unquote, urlparse

rd = RD()

def humanize_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f}{unit}" if unit == "GB" else f"{size:.0f}{unit}"
        size /= 1024

def get_unique_filename(filename, filesize):
    base, ext = os.path.splitext(filename)
    humanized_size = humanize_size(filesize)
    new_filename = f"{base}o.o{humanized_size}{ext}"
    return new_filename


def download_chunk(url, start, end, dir, filename, part_num, retries=6):
    headers = {'Range': f'bytes={start}-{end}'}
    chunk_path = f"{dir}/{filename}.part{part_num}"
    for attempt in range(retries):
        try:
            response = get(url, headers=headers, stream=True, verify=False)
            print(f"Downloading chunk: {chunk_path}")
            with open(chunk_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return chunk_path
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Max retries exceeded for chunk: {chunk_path}")
                raise MaxRetryError(dir, filename)
            
class MaxRetryError(Exception):
    def __init__(self, dir, filename):
        self.message = f"Max Retry reached for {dir}/{filename}. Download failed!!"
        super().__init__(self.message)


def merge_chunks(filename, dir, num_chunks):
    with open(f"{dir}/{filename}", "wb") as outfile:
        for i in range(num_chunks):
            chunk_path = f"{dir}/{filename}.part{i}"
            print(f"Merging chunk: {chunk_path}")
            with open(chunk_path, "rb") as infile:
                outfile.write(infile.read())
            os.remove(chunk_path)
    return f"{dir}/{filename}"

def debird(link):
    try:
        ba = rd.unrestrict.link(link=link).json()
        print(ba)
    except Exception as e:
        print(f"Failed to generate download link for {link}. Error: {e}")
        return None
    return shot_bird(ba['download'])

def shot_bird(link, dir=None, num_chunks=PARALLEL_DOWNLOADS):
    dir = dir if dir else "downloads"
    os.makedirs(dir, exist_ok=True)
    ba=dict()   
    r = get(link, allow_redirects=True, stream=True)
    ba['download']=link
    ba['filename']=unquote(os.path.basename(urlparse(link).path))
    ba['filesize']=int(r.headers.get("Content-Length", 0))  
    print(f"Downloading: {ba['filename']} \n Size: {ba['filesize']}\nlink: {ba['download']}")
    # ln = ba["download"].replace("http://", "https://")
    ln=ba['download']
    filename = get_unique_filename(ba['filename'], ba['filesize']).replace("+", " ")
    file_size = int(ba['filesize'])
    if file_size == 0:
        print(f"File size is zero for {ba['filename']}. Downloading as a single chunk.")
        response = get(ln, stream=True,verify=False)
        file_path = f"{dir}/{filename}"
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
            futures.append(executor.submit(download_chunk, ln, start, end, dir, filename, i))
        
        for future in as_completed(futures):
            future.result()
    
    file=merge_chunks(filename, dir, num_chunks)
    asiz=os.path.getsize(file)
    file=re.sub(r'o\.o.*\.', f' - [{humanize_size(asiz)}].', file)
    os.rename(f"{dir}/{filename}", file)
    return file

async def async_shot_bird(link, dir=None):
    return await asyncio.to_thread(shot_bird, link, dir)
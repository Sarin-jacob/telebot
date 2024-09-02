from os import path,remove,listdir,walk
import re
try:
    import zipfile
    import rarfile
    import tarfile
except ImportError:
    print("Please install the required packages: rarfile, zipfile, and tarfile")

def walker(directory):
    files_list = []
    for root, dirs, files in walk(directory):
        for file in files:
            files_list.append(path.join(root, file))
    return files_list

def extract_file(file_path):
    dots=file_path.split('.')
    extracted_file_path='.'.join(dots[:-1])
    extt = dots[-1].lower()
    folder_path = path.dirname(file_path)
    
    if extt in ['zip', 'rar', 'tar']:
        if extt == 'zip':
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(folder_path)
        elif extt == 'rar':
            with rarfile.RarFile(file_path, 'r') as rar_ref:
                rar_ref.extractall(folder_path)
        elif extt == 'tar':
            with tarfile.open(file_path, 'r') as tar_ref:
                tar_ref.extractall(folder_path)
        
        # Remove the original archive file
        remove(file_path)
        if path.isfile(extracted_file_path):
            return extracted_file_path
        elif path.isdir(extracted_file_path):
            a=walker(extracted_file_path)
            for i,j in enumerate(a):
                if j.split('.')[-1] in ['url','txt']:
                    remove(j)
                    a.pop(i)
            return a
        return None
    else:
        return None

def read_config(file_path):
    config = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error reading config file: {e}")
    return config

async def sendHelloMessage(client, peerChannel):
    entity = await client.get_entity(peerChannel)
    print("Telebot Daemon running using Telethon ")
    await client.send_message(entity, "Telebot is up n Running")

async def log_reply(message, reply):
    chunk_size=4096
    chunks = [reply[i:i+chunk_size] for i in range(0, len(reply), chunk_size)]
    for chunk in chunks:
        print(chunk)
        fm=await message.reply(chunk,link_preview=False)
    return fm

async def log_edit(message, reply):
    print(reply)
    await message.edit(reply)

def finddetails(input_string):
    pattern = r'(\w+):((?:\w+://)?.*?)\s*(?=\w+:|$)'
    matches = re.findall(pattern, input_string)
    return matches

# Helper function to load data from a text file
def load_data(file_path):
    if path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.readlines()
    return []

# Helper function to save data to a text file
def save_data(file_path, data):
    with open(file_path, 'w') as file:
        file.writelines(data)

# Function to add a new entry and save it in alphabetical order without duplicates
def add_entry(file_path, entry):
    data = load_data(file_path)
    entry_with_newline = entry + '\n'
    if entry_with_newline not in data:
        data.append(entry_with_newline)
        data.sort(key=lambda x: x.lower())
        save_data(file_path, data)


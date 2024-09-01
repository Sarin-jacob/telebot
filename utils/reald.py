from dotenv import load_dotenv
load_dotenv()
from rdapi import RD
from requests import get
rd = RD()
def shot_bird(link,dir=None):
    dir=dir if dir else "."
    ba=rd.unrestrict.link(link=link).json()
    print("Downloading: {ba['filename']} \n Size: {ba['size']}\nlink: {ba['download']}")
    bt=get({ba["download"]},stream=True)
    with open(f"/{ba['filename']}","wb") as f:
        f.write(bt.content)
    return f"{dir}/{ba['filename']}"
import sys
from dotenv import load_dotenv
load_dotenv()
from rdapi import RD
from requests import get
rd = RD()
def shot_bird(link):
    ba=rd.unrestrict.link(link=link).json()
    print(ba)
    print(f"Downloading: {ba['filename']} \n Size: {ba['filesize']}\nlink: {ba['download']}")
    return ba['download']
if len(sys.argv) > 1:
    print(shot_bird(sys.argv[-1]))
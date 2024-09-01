import os
import time
from dotenv import load_dotenv
load_dotenv()
from rdapi import RD
rd = RD()
try:
    os.system("warp-cli connect")
    time.sleep(5)
    a=rd.unrestrict.link(link="https://www.youtube.com/watch?v=xvFZjo5PgG0").json()
    ba=rd.unrestrict.link(link="https://1fichier.com/?ophpf2bhyp7cqgu0zmik").json()
except Exception as e:
    a="Error"
    ba=f"{e}"
with open("reald.txt", "w") as f:
    if a and ba:
        f.write(f"Youtube: {a}\n1Fichier: {ba}")
        
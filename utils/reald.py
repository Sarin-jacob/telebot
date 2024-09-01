import os
from dotenv import load_dotenv
load_dotenv()
try:
    from rdapi import RD
except ImportError:
    print("run `pip install rdapi`")
    exit(1)
rd = RD()
print(rd.unrestrict.link(link="https://www.youtube.com/watch?v=xvFZjo5PgG0").json())
print(rd.unrestrict.link(link="https://1fichier.com/?ophpf2bhyp7cqgu0zmik").json())
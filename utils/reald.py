import os
try:
    from rdapi import RD
except ImportError:
    print("run `pip install rdapi`")
    exit(1)
print(os.environ)
rd = RD()
print(rd.unrestrict.link(link="https://1fichier.com/?ophpf2bhyp7cqgu0zmik").json())
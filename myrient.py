import re
from itertools import chain
from pathlib import Path
from urllib import request


rom_dir = "./RomRoot"
complete_dir = "./RomRoot/completed"


url = "https://myrient.erista." + "me/upload/MyrientFileDropList.txt"
pw_mgr = request.HTTPPasswordMgrWithDefaultRealm()
pw_mgr.add_password(None, url, "myrient", "list")
auth_handler = request.HTTPBasicAuthHandler(pw_mgr)
opener = request.build_opener(auth_handler)
with opener.open(url) as r:
    p = re.compile(r"^ *(\d+) +(.+)$")
    matches = (p.match(l) for l in r.read().decode().split("\n"))
    remote_roms = set((Path(m[2]).name, int(m[1])) for m in matches if m)

local_roms = (p for p in chain(Path(rom_dir).glob("*"),
                               Path(rom_dir).glob("**/*"))
              if p.is_file() and not p.is_relative_to(complete_dir))
matching_roms = (p for p in local_roms
                 if (p.name, p.stat().st_size) in remote_roms)

for path in matching_roms:
    newpath = complete_dir / path.relative_to(rom_dir)
    if newpath.exists():
        raise Exception(newpath)
    print(f"Moving {path}")
    newpath.parent.mkdir(parents=True, exist_ok=True)
    path.rename(newpath)

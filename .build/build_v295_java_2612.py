from pathlib import Path
import subprocess, zipfile, json, hashlib

ROOT=Path(".build/generated-v291-java")
OUT=Path("LegendaryRais-Java-26.1.2-v2.9.5-FIX.zip")
SHA=Path("LegendaryRais-Java-26.1.2-v2.9.5-FIX.sha1")

subprocess.run(["python3",".build/build_v291_java_fix.py"],check=True)

pack_meta={
  "pack":{
    "description":"LegendaryRais v2.9.5 • Minecraft/Paper 26.1.2 • Sovereign Blade + Leviathan Trident + ItemDisplay Skill FX",
    "min_format":[84,0],
    "max_format":[84,0]
  }
}
(ROOT/"pack.mcmeta").write_text(json.dumps(pack_meta,separators=(",",":")),encoding="utf-8")

required=[
 "assets/soultide/models/item/soul_tide_sovereign_blade.json",
 "assets/soultide/items/soul_tide_sovereign_blade.json",
 "assets/legendaryrais/models/item/abyss_leviathan_trident.json",
 "assets/legendaryrais/items/abyss_leviathan_trident.json",
 "assets/legendaryrais/models/item/fx_soul_slash.json",
 "assets/legendaryrais/models/item/fx_tidal_crescent.json",
 "assets/legendaryrais/models/item/fx_undertow_ring.json",
 "assets/legendaryrais/models/item/fx_domain_sigil.json",
 "assets/legendaryrais/models/item/fx_leviathan_fang.json",
 "assets/legendaryrais/models/item/fx_maelstrom.json",
 "assets/legendaryrais/models/item/fx_leviathan_impact.json",
 "assets/legendaryrais/models/item/fx_lightning_spear.json",
 "assets/minecraft/items/netherite_sword.json",
 "assets/minecraft/items/trident.json",
 "assets/minecraft/items/paper.json"
]
for rel in required:
    p=ROOT/rel
    if not p.is_file():
        raise RuntimeError("missing required pack asset: "+rel)

for p in ROOT.rglob("*.json"):
    json.loads(p.read_text(encoding="utf-8"))
json.loads((ROOT/"pack.mcmeta").read_text(encoding="utf-8"))

if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file():
            z.write(p,p.relative_to(ROOT).as_posix())

with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad:
        raise RuntimeError("corrupt zip entry: "+bad)
    names=set(z.namelist())
    if "pack.mcmeta" not in names:
        raise RuntimeError("pack.mcmeta is not at zip root")
    meta=json.loads(z.read("pack.mcmeta"))
    assert meta["pack"]["min_format"] == [84,0]
    assert meta["pack"]["max_format"] == [84,0]

sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n",encoding="utf-8")
print("PACK_OK",OUT.stat().st_size,sha,"FORMAT=84.0","REQUIRED_ASSETS",len(required))

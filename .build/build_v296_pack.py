from pathlib import Path
import zipfile, json, shutil, hashlib, math

BASE=Path("LegendaryRais-Java-26.1.2-v2.9.5-FIX.zip")
OUT=Path("LegendaryRais-Java-26.1.2-v2.9.6-ABSOLUTE-WATER.zip")
SHA=Path("LegendaryRais-Java-26.1.2-v2.9.6-ABSOLUTE-WATER.sha1")
ROOT=Path(".build/generated-v296-pack")
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))
def save(rel,obj):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")
def cube(fr,to,tex,rot=None):
    faces={k:{"texture":"#"+tex} for k in ("north","south","east","west","up","down")}
    d={"from":[round(x,3) for x in fr],"to":[round(x,3) for x in to],"faces":faces}
    if rot: d["rotation"]={"origin":rot[0],"axis":rot[1],"angle":rot[2],"rescale":True}
    return d

# Existing textures are already 1024px HD. Add more real 3D geometry/details.
sword=load("assets/soultide/models/item/soul_tide_sovereign_blade.json")
els=sword.setdefault("elements",[])
# blade spine + bevel ribs
for y in [8.0,10.5,13.0,15.5,18.0,20.5,23.0,25.5,28.0]:
    els.append(cube([7.55,y,6.75],[8.45,y+0.42,9.25],"cyan"))
    els.append(cube([6.25,y+0.12,7.55],[9.75,y+0.32,8.45],"water"))
# guard fins / gemstone depth
els += [
 cube([1.0,4.6,6.55],[6.2,5.6,9.45],"dark",([5.6,5.1,8],"z",-22.5)),
 cube([9.8,4.6,6.55],[15.0,5.6,9.45],"dark",([10.4,5.1,8],"z",22.5)),
 cube([6.9,5.0,6.1],[9.1,7.2,9.9],"cyan",([8,6.1,8],"z",45)),
 cube([7.35,-8.7,6.55],[8.65,-6.4,9.45],"water")
]
sword["credit"]="LegendaryRais v2.9.6 HD Sovereign Blade • 1024px"
save("assets/soultide/models/item/soul_tide_sovereign_blade.json",sword)
save("assets/soultide/models/item/soul_tide_katana.json",sword)

tri=load("assets/legendaryrais/models/item/abyss_leviathan_trident.json")
te=tri.setdefault("elements",[])
# segmented shaft ribs, prong bevels and abyss runes
for y in [-12,-9,-6,-3,0,3,6,9,12,15,18]:
    te.append(cube([6.95,y,6.95],[9.05,y+0.34,9.05],"cyan"))
for x in [2.0,3.4,8.0,12.6,14.0]:
    te.append(cube([x-0.22,22.0,6.65],[x+0.22,31.3,9.35],"water"))
te += [
 cube([5.0,18.2,6.25],[11.0,20.4,9.75],"dark"),
 cube([6.6,19.0,6.0],[9.4,22.2,10.0],"cyan",([8,20.6,8],"z",45)),
 cube([7.45,-15.4,6.55],[8.55,-12.6,9.45],"water")
]
tri["credit"]="LegendaryRais v2.9.6 HD Abyss Leviathan • 1024px"
save("assets/legendaryrais/models/item/abyss_leviathan_trident.json",tri)

# Dedicated flying spear model uses the same HD geometry, rendered on a PAPER ItemDisplay.
save("assets/legendaryrais/models/item/fx_leviathan_projectile.json",tri)
save("assets/legendaryrais/items/fx_leviathan_projectile.json",{
 "oversized_in_gui":True,
 "model":{"type":"minecraft:model","model":"legendaryrais:item/fx_leviathan_projectile"}
})

# Heavier water FX models: reuse existing water ring/slash with more display scale driven by plugin.
for dst,src in [
 ("fx_soul_slash","fx_soul_slash"),
 ("fx_tidal_crescent","fx_tidal_crescent"),
 ("fx_undertow_ring","fx_undertow_ring"),
 ("fx_maelstrom","fx_maelstrom"),
 ("fx_leviathan_impact","fx_leviathan_impact")
]:
    d=load(f"assets/legendaryrais/models/item/{src}.json")
    d["credit"]="LegendaryRais v2.9.6 Absolute Water FX"
    save(f"assets/legendaryrais/models/item/{dst}.json",d)

paper=load("assets/minecraft/items/paper.json")
entries=paper["model"]["entries"]
# remove old terminal vanilla threshold if present, then append projectile and new terminal fallback.
entries=[e for e in entries if float(e.get("threshold",-1)) not in (910109.0,910110.0)]
entries.append({"threshold":910109.0,"model":{"type":"minecraft:model","model":"legendaryrais:item/fx_leviathan_projectile"}})
entries.append({"threshold":910110.0,"model":{"type":"minecraft:model","model":"minecraft:item/paper"}})
entries.sort(key=lambda e:float(e["threshold"]))
paper["model"]["entries"]=entries
save("assets/minecraft/items/paper.json",paper)

save("pack.mcmeta",{"pack":{
 "description":"LegendaryRais v2.9.6 ABSOLUTE WATER • HD 3D weapons • custom Leviathan projectile • Paper/MC 26.1.2",
 "min_format":[84,0],"max_format":[84,0]
}})

# Validate every JSON and all critical assets.
required=[
 "assets/soultide/models/item/soul_tide_sovereign_blade.json",
 "assets/legendaryrais/models/item/abyss_leviathan_trident.json",
 "assets/legendaryrais/models/item/fx_leviathan_projectile.json",
 "assets/legendaryrais/items/fx_leviathan_projectile.json",
 "assets/minecraft/items/netherite_sword.json",
 "assets/minecraft/items/trident.json",
 "assets/minecraft/items/paper.json"
]
for r in required:
    if not (ROOT/r).is_file(): raise RuntimeError("missing "+r)
for p in ROOT.rglob("*.json"): json.loads(p.read_text(encoding="utf-8"))
if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n")
print("PACK_OK",OUT.stat().st_size,sha,"SWORD_ELEMENTS",len(sword["elements"]),"TRIDENT_ELEMENTS",len(tri["elements"]))

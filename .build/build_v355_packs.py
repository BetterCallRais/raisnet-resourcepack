from pathlib import Path
import base64,gzip,hashlib,importlib.util,json,shutil,zipfile
from PIL import Image

ROOT=Path(".build/generated-v355")
ASSETS=ROOT/"assets"
JAVA_ROOT=ROOT/"java"
BED_ROOT=ROOT/"bedrock"
NS="legendaryv34"

JAVA_BASE=Path("LegendaryRais-Java-26.1.2-v3.5.4-VISUAL-INTEGRITY.zip")
BED_BASE=Path("LegendaryRais-Bedrock-v3.5.4-VISUAL-INTEGRITY.mcpack")
MAP_BASE=Path("LegendaryRais-Geyser-v3.5.4-mappings.json")

JAVA_OUT=Path("LegendaryRais-Java-26.1.2-v3.5.5-ART-REBUILD.zip")
JAVA_SHA=Path("LegendaryRais-Java-26.1.2-v3.5.5-ART-REBUILD.sha1")
BED_OUT=Path("LegendaryRais-Bedrock-v3.5.5-ART-REBUILD.mcpack")
BED_SHA=Path("LegendaryRais-Bedrock-v3.5.5-ART-REBUILD.sha1")
MAP_OUT=Path("LegendaryRais-Geyser-v3.5.5-mappings.json")

shutil.rmtree(ROOT,ignore_errors=True)
ROOT.mkdir(parents=True)

# Decode the compressed art generator committed to the repository.
payload=Path(".build/v355_art_assets.py.gz.b64").read_text(encoding="utf-8").strip()
gen_py=ROOT/"v355_art_assets.py"
gen_py.write_bytes(gzip.decompress(base64.b64decode(payload)))
spec=importlib.util.spec_from_file_location("v355_art_assets",gen_py)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
mod.generate(ASSETS)

WEAPONS=["emberfall_claymore","noctis_longsword","stormpiercer_recurve_bow","gaia_war_spear","astral_twin_daggers"]
SETS=["phoenix","voidwalker","titan","celestial","water_sovereign"]
PIECES=["helmet","chest","legs","boots"]

def wr(root,rel,obj):
    p=root/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def sha1_file(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()

# ---------------- Java pack ----------------
if not JAVA_BASE.is_file(): raise FileNotFoundError(JAVA_BASE)
JAVA_ROOT.mkdir(parents=True)
with zipfile.ZipFile(JAVA_BASE) as z: z.extractall(JAVA_ROOT)

DISPLAY={
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,4,1],"scale":[0.82,0.82,0.82]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,4,1],"scale":[0.82,0.82,0.82]},
 "firstperson_righthand":{"rotation":[0,-90,24],"translation":[1.0,3.3,1.1],"scale":[0.92,0.92,0.92]},
 "firstperson_lefthand":{"rotation":[0,90,-24],"translation":[1.0,3.3,1.1],"scale":[0.92,0.92,0.92]},
 "gui":{"rotation":[25,-35,0],"translation":[0,0,0],"scale":[0.90,0.90,0.90]},
 "ground":{"rotation":[0,0,0],"translation":[0,2,0],"scale":[0.55,0.55,0.55]},
 "fixed":{"rotation":[0,180,0],"translation":[0,0,0],"scale":[0.70,0.70,0.70]}
}

for name in WEAPONS:
    dst=JAVA_ROOT/f"assets/{NS}/textures/item/v355/{name}.png"; dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ASSETS/f"{name}.png",dst)
    wr(JAVA_ROOT,f"assets/{NS}/models/item/{name}.json",{
        "parent":"minecraft:item/handheld","gui_light":"front",
        "textures":{"layer0":f"{NS}:item/v355/{name}"},"display":DISPLAY})
    wr(JAVA_ROOT,f"assets/{NS}/items/{name}.json",{
        "model":{"type":"minecraft:model","model":f"{NS}:item/{name}"}})

for setn in SETS:
    for layer,sub in ((1,"humanoid"),(2,"humanoid_leggings")):
        dst=JAVA_ROOT/f"assets/{NS}/textures/entity/equipment/{sub}/{setn}_set.png"
        dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ASSETS/f"{setn}_{layer}.png",dst)
    wr(JAVA_ROOT,f"assets/{NS}/equipment/{setn}_set.json",{"layers":{
        "humanoid":[{"texture":f"{NS}:{setn}_set"}],
        "humanoid_leggings":[{"texture":f"{NS}:{setn}_set"}]}})
    for piece in PIECES:
        dst=JAVA_ROOT/f"assets/{NS}/textures/item/armor/{setn}_{piece}.png"
        dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ASSETS/f"icon_{setn}_{piece}.png",dst)
        wr(JAVA_ROOT,f"assets/{NS}/models/item/armor/{setn}_{piece}.json",{
            "parent":"minecraft:item/generated","textures":{"layer0":f"{NS}:item/armor/{setn}_{piece}"}})
        wr(JAVA_ROOT,f"assets/{NS}/items/armor/{setn}_{piece}.json",{
            "model":{"type":"minecraft:model","model":f"{NS}:item/armor/{setn}_{piece}"}})

mc=JAVA_ROOT/"pack.mcmeta"
md=json.loads(mc.read_text(encoding="utf-8"))
md["pack"]["description"]="LegendaryRais v3.5.5 ART REBUILD | HD silhouette weapons | forged armor | Soul Tide + Leviathan frozen"
mc.write_text(json.dumps(md,separators=(",",":")),encoding="utf-8")

for p in JAVA_ROOT.rglob("*.json"): json.loads(p.read_text(encoding="utf-8"))
for name in WEAPONS:
    model=json.loads((JAVA_ROOT/f"assets/{NS}/models/item/{name}.json").read_text())
    tex=model["textures"]["layer0"]; nsp,path=tex.split(":",1)
    assert (JAVA_ROOT/f"assets/{nsp}/textures/{path}.png").is_file()
for setn in SETS:
    assert (JAVA_ROOT/f"assets/{NS}/equipment/{setn}_set.json").is_file()
assert (JAVA_ROOT/"assets/soultide").exists()
assert (JAVA_ROOT/"assets/legendaryrais").exists()

if JAVA_OUT.exists(): JAVA_OUT.unlink()
with zipfile.ZipFile(JAVA_OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(JAVA_ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(JAVA_ROOT).as_posix())
with zipfile.ZipFile(JAVA_OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)
JAVA_SHA.write_text(sha1_file(JAVA_OUT)+"\n",encoding="utf-8")

# ---------------- Bedrock pack ----------------
if not BED_BASE.is_file(): raise FileNotFoundError(BED_BASE)
BED_ROOT.mkdir(parents=True)
with zipfile.ZipFile(BED_BASE) as z: z.extractall(BED_ROOT)

bed_meta={
 "emberfall_claymore":("geometry.raisnet_emberfall_v355",[32,56,0],[.68,.68,.68]),
 "noctis_longsword":("geometry.raisnet_noctis_v355",[32,56,0],[.68,.68,.68]),
 "stormpiercer_recurve_bow":("geometry.raisnet_stormpiercer_v355",[32,32,0],[.82,.82,.82]),
 "gaia_war_spear":("geometry.raisnet_gaia_v355",[32,58,0],[.68,.68,.68]),
 "astral_twin_daggers":("geometry.raisnet_astral_v355",[32,56,0],[.72,.72,.72])
}

for name,(gid,pivot,scale) in bed_meta.items():
    src=Image.open(ASSETS/f"{name}.png").convert("RGBA").resize((64,64),Image.Resampling.LANCZOS)
    dst=BED_ROOT/f"textures/items/{name}.png"; dst.parent.mkdir(parents=True,exist_ok=True); src.save(dst,optimize=True)
    wr(BED_ROOT,f"models/entity/{name}.geo.json",{
      "format_version":"1.21.0","minecraft:geometry":[{
        "description":{"identifier":gid,"texture_width":64,"texture_height":64,
          "visible_bounds_width":4.5,"visible_bounds_height":5.5,"visible_bounds_offset":[0,1,0]},
        "bones":[{"name":"bb_main","pivot":[0,8,0],
          "binding":"q.item_slot_to_bone_name(context.item_slot)",
          "texture_meshes":[{"texture":"default","position":[0,0,0],"local_pivot":pivot,
            "rotation":[0,0,0],"scale":scale,"use_pixel_depth":True}]}]
      }]})
    wr(BED_ROOT,f"attachables/{name}.player.json",{
      "format_version":"1.20.30","minecraft:attachable":{"description":{
        "identifier":f"raisnet:{name}",
        "item":{f"raisnet:{name}":"query.is_owner_identifier_any('minecraft:player')"},
        "materials":{"default":"entity_alphatest","enchanted":"entity_alphatest_glint"},
        "textures":{"default":f"textures/items/{name}","enchanted":"textures/misc/enchanted_item_glint"},
        "geometry":{"default":gid},"render_controllers":["controller.render.item_default"]}}})

for setn in SETS:
    for layer in (1,2):
        img=Image.open(ASSETS/f"{setn}_{layer}.png").convert("RGBA")
        dst=BED_ROOT/f"textures/models/armor/{setn}_{layer}.png"; dst.parent.mkdir(parents=True,exist_ok=True); img.save(dst,optimize=True)
    for piece in PIECES:
        img=Image.open(ASSETS/f"icon_{setn}_{piece}.png").convert("RGBA")
        dst=BED_ROOT/f"textures/items/armor_{setn}_{piece}.png"; dst.parent.mkdir(parents=True,exist_ok=True); img.save(dst,optimize=True)

it=BED_ROOT/"textures/item_texture.json"
idata=json.loads(it.read_text(encoding="utf-8")); td=idata.setdefault("texture_data",{})
for name in WEAPONS: td[f"raisnet:{name}"]={"textures":f"textures/items/{name}"}
for setn in SETS:
    for piece in PIECES: td[f"raisnet:{setn}_{piece}"]={"textures":f"textures/items/armor_{setn}_{piece}"}
it.write_text(json.dumps(idata,separators=(",",":")),encoding="utf-8")

mf=BED_ROOT/"manifest.json"
manifest=json.loads(mf.read_text(encoding="utf-8"))
manifest["header"]["name"]="RaisNet LegendaryRais v3.5.5 ART REBUILD"
manifest["header"]["description"]="HD texture-mesh weapons + forged native armor; Soul Tide and Leviathan preserved"
manifest["header"]["uuid"]="9b0438d3-6e5b-4c5f-ae70-bd7e483e9d05"
manifest["header"]["version"]=[3,5,5]
manifest["modules"][0]["uuid"]="3a8fc5f9-85d4-4439-8b6d-5cfb0e705bb1"
manifest["modules"][0]["version"]=[3,5,5]
mf.write_text(json.dumps(manifest,separators=(",",":")),encoding="utf-8")

for p in BED_ROOT.rglob("*.json"): json.loads(p.read_text(encoding="utf-8"))
for name in WEAPONS:
    geo=json.loads((BED_ROOT/f"models/entity/{name}.geo.json").read_text())
    tm=geo["minecraft:geometry"][0]["bones"][0]["texture_meshes"][0]
    assert tm["texture"]=="default" and tm["use_pixel_depth"] is True
    assert (BED_ROOT/f"attachables/{name}.player.json").is_file()
for setn in SETS:
    for piece in PIECES: assert (BED_ROOT/f"attachables/armor_{setn}_{piece}.json").is_file()
assert (BED_ROOT/"models/entity/soul_tide_katana.geo.json").is_file()
assert (BED_ROOT/"models/entity/abyss_leviathan_trident.geo.json").is_file()
assert (BED_ROOT/"attachables/soul_tide_katana.player.json").is_file()
assert (BED_ROOT/"attachables/abyss_leviathan_trident.player.json").is_file()

if BED_OUT.exists(): BED_OUT.unlink()
with zipfile.ZipFile(BED_OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(BED_ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(BED_ROOT).as_posix())
with zipfile.ZipFile(BED_OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)
BED_SHA.write_text(sha1_file(BED_OUT)+"\n",encoding="utf-8")

# Modern Geyser v2 mapping is unchanged in keys/models; validate and republish with versioned name.
mapping=json.loads(MAP_BASE.read_text(encoding="utf-8"))
assert mapping.get("format_version")==2
seen=set()
for base,defs in mapping.get("items",{}).items():
    for d in defs:
        if d.get("type")=="definition":
            key=(base,d.get("model"),json.dumps(d.get("predicate",None),sort_keys=True))
            if key in seen: raise RuntimeError("duplicate mapping "+repr(key))
            seen.add(key)
MAP_OUT.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

print("JAVA",JAVA_OUT.stat().st_size,JAVA_SHA.read_text().strip())
print("BEDROCK",BED_OUT.stat().st_size,BED_SHA.read_text().strip())
print("MAPPINGS",MAP_OUT.stat().st_size,"definitions",len(seen))

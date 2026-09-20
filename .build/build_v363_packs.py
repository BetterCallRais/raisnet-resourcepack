from pathlib import Path
import json, shutil, zipfile, hashlib, uuid
from PIL import Image

JBASE=Path("LegendaryRais-Java-26.1.2-v3.6.2-CROSSPLAY-ASCENSION.zip")
BBASE=Path("LegendaryRais-Bedrock-v3.6.2-CROSSPLAY-ASCENSION.mcpack")
MBASE=Path("LegendaryRais-Geyser-v3.6.2-mappings.json")
JOUT=Path("LegendaryRais-Java-26.1.2-v3.6.3-RESOURCE-INTEGRITY.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.6.3-RESOURCE-INTEGRITY.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.6.3-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.6.3-RESOURCE-INTEGRITY.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.6.3-RESOURCE-INTEGRITY.sha1")
ROOT=Path(".build/generated-v363"); JR=ROOT/"java"; BR=ROOT/"bedrock"

shutil.rmtree(ROOT,ignore_errors=True); JR.mkdir(parents=True); BR.mkdir(parents=True)
with zipfile.ZipFile(JBASE) as z:z.extractall(JR)
with zipfile.ZipFile(BBASE) as z:z.extractall(BR)

NS="legendaryv34"
WEAPON_MODELS={
 "emberfall_claymore":"emberfall_claymore",
 "noctis_longsword":"noctis_longsword",
 "stormpiercer_recurve_bow":"stormpiercer_recurve_bow",
 "gaia_war_spear":"gaia_war_spear",
 "astral_twin_daggers":"astral_frost_greataxe",
 "astral_frost_greataxe":"astral_frost_greataxe",
}
SETS=("phoenix","voidwalker","titan","celestial","water_sovereign")
PIECES=("helmet","chest","legs","boots")

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

# 1) Legacy namespace aliases. Remove duplicated heavy assets but keep old item-model keys valid.
for legacy in ("legendaryv32","legendaryv33"):
    base=JR/"assets"/legacy
    shutil.rmtree(base,ignore_errors=True)
    for old_name,current in WEAPON_MODELS.items():
        write_json(base/"items"/f"{old_name}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/{current}"}})
    for s in SETS:
        eq=json.loads((JR/"assets"/NS/"equipment"/f"{s}_set.json").read_text())
        write_json(base/"equipment"/f"{s}_set.json",eq)
        for p in PIECES:
            write_json(base/"items"/"armor"/f"{s}_{p}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/armor/{s}_{p}"}})

# Compatibility aliases inside namespaces used by older plugin builds.
for old_name,current in WEAPON_MODELS.items():
    # legendaryv34 old Astral key and any old IDs become current model immediately.
    write_json(JR/"assets"/NS/"items"/f"{old_name}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/{current}"}})
    # legendaryrais old expansion item_model keys route to current v34 assets.
    if old_name!="astral_frost_greataxe":
        write_json(JR/"assets"/"legendaryrais"/"items"/f"{old_name}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/{current}"}})

for s in SETS:
    for p in PIECES:
        write_json(JR/"assets"/"legendaryrais"/"items"/"armor"/f"{s}_{p}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/armor/{s}_{p}"}})

# Remove superseded v34 texture revisions. Current v3.6.2/v3.6.3 models use v362 textures.
for olddir in ("v355","v360","v361"):
    shutil.rmtree(JR/"assets"/NS/"textures"/"item"/olddir,ignore_errors=True)

# Old Astral dagger model referenced the removed v361 textures. Its item definition is now
# a compatibility alias to the v3.6.3 greataxe, so the stale model file must not remain.
(JR/"assets"/NS/"models"/"item"/"astral_twin_daggers.json").unlink(missing_ok=True)

# 2) Fix any custom model element outside Minecraft model coordinate limits.
# Keep x/z centered around 8 and y grip near 4 so the v3.6.2 hand fix stays intact.
def repair_model_bounds(path):
    obj=json.loads(path.read_text())
    els=obj.get("elements")
    if not isinstance(els,list) or not els:return False
    changed=False
    for axis_i,anchor in ((0,8.0),(1,4.0),(2,8.0)):
        vals=[]
        for e in els:
            for k in ("from","to"):
                a=e.get(k)
                if isinstance(a,list) and len(a)==3:vals.append(float(a[axis_i]))
            rot=e.get("rotation")
            if isinstance(rot,dict):
                a=rot.get("origin")
                if isinstance(a,list) and len(a)==3:vals.append(float(a[axis_i]))
        if not vals:continue
        lo,hi=min(vals),max(vals)
        if lo>=-16 and hi<=32:continue
        factors=[1.0]
        if hi>31.5 and hi!=anchor:factors.append((31.5-anchor)/(hi-anchor))
        if lo<-15.5 and lo!=anchor:factors.append((-15.5-anchor)/(lo-anchor))
        factor=min(f for f in factors if f>0)
        for e in els:
            for k in ("from","to"):
                a=e.get(k)
                if isinstance(a,list) and len(a)==3:
                    a[axis_i]=round(anchor+(float(a[axis_i])-anchor)*factor,4)
            rot=e.get("rotation")
            if isinstance(rot,dict):
                a=rot.get("origin")
                if isinstance(a,list) and len(a)==3:
                    a[axis_i]=round(anchor+(float(a[axis_i])-anchor)*factor,4)
        changed=True
    if changed:path.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")
    return changed

repaired=[]
for p in JR.rglob("*.json"):
    sp=p.as_posix()
    if "/models/" not in sp:continue
    # Water relic namespaces are locked. They already pass bounds validation and are never touched.
    if "/assets/soultide/" in sp:continue
    if sp.endswith("/assets/legendaryrais/models/item/abyss_leviathan_trident.json"):continue
    if repair_model_bounds(p):repaired.append(str(p.relative_to(JR)))

# 3) Pack metadata.
mc=JR/"pack.mcmeta"; meta=json.loads(mc.read_text())
meta["pack"]["description"]="LegendaryRais v3.6.3 RESOURCE INTEGRITY | fixed model bounds | legacy aliases | clean refs"
meta["pack"]["min_format"]=[84,0];meta["pack"]["max_format"]=[84,0]
mc.write_text(json.dumps(meta,separators=(",",":")),encoding="utf-8")

mf=BR/"manifest.json"; bm=json.loads(mf.read_text())
bm["header"]["name"]="RaisNet LegendaryRais v3.6.3 Resource Integrity"
bm["header"]["description"]="Validated crossplay pack; v3.6.2 visuals with fresh cache identity"
bm["header"]["uuid"]="5cd7e6a2-6ca1-4f33-b159-0567040f7f38"
bm["header"]["version"]=[3,6,3]
bm["modules"][0]["uuid"]="a4e98ad0-49ad-49ed-834d-06ef167ca2b8"
bm["modules"][0]["version"]=[3,6,3]
mf.write_text(json.dumps(bm,separators=(",",":")),encoding="utf-8")

# Mapping content stays functionally identical; file name/version changes for clean deployment.
mapping=json.loads(MBASE.read_text());MOUT.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# ---------- exhaustive Java integrity audit ----------
bad_json=[];bad_bounds=[];missing_models=[];missing_textures=[];bad_png=[]
for p in JR.rglob("*.json"):
    try: obj=json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        bad_json.append((str(p.relative_to(JR)),str(e)));continue

    if "/models/" in p.as_posix():
        for i,e in enumerate(obj.get("elements",[])):
            for key in ("from","to"):
                arr=e.get(key)
                if isinstance(arr,list) and len(arr)==3:
                    for axis,v in zip("xyz",arr):
                        if float(v)<-16 or float(v)>32:bad_bounds.append((str(p.relative_to(JR)),i,key,axis,v))
            rot=e.get("rotation")
            if isinstance(rot,dict):
                arr=rot.get("origin")
                if isinstance(arr,list) and len(arr)==3:
                    for axis,v in zip("xyz",arr):
                        if float(v)<-16 or float(v)>32:bad_bounds.append((str(p.relative_to(JR)),i,"rotation.origin",axis,v))
        for key,ref in obj.get("textures",{}).items():
            if not isinstance(ref,str) or ref.startswith("#"):continue
            ns,path=(ref.split(":",1) if ":" in ref else ("minecraft",ref))
            if ns=="minecraft":continue
            q=JR/"assets"/ns/"textures"/f"{path}.png"
            if not q.is_file():missing_textures.append((str(p.relative_to(JR)),ref))

    if "/items/" in p.as_posix():
        refs=[]
        def walk(x):
            if isinstance(x,dict):
                if x.get("type")=="minecraft:model" and isinstance(x.get("model"),str):refs.append(x["model"])
                for v in x.values():walk(v)
            elif isinstance(x,list):
                for v in x:walk(v)
        walk(obj)
        for ref in refs:
            ns,path=(ref.split(":",1) if ":" in ref else ("minecraft",ref))
            if ns=="minecraft":continue
            q=JR/"assets"/ns/"models"/f"{path}.json"
            if not q.is_file():missing_models.append((str(p.relative_to(JR)),ref))

for p in JR.rglob("*.png"):
    try:
        with Image.open(p) as im:
            im.verify()
    except Exception as e:bad_png.append((str(p.relative_to(JR)),str(e)))

assert not bad_json,bad_json[:10]
assert not bad_bounds,bad_bounds[:20]
assert not missing_models,missing_models[:20]
assert not missing_textures,missing_textures[:20]
assert not bad_png,bad_png[:10]

# Current weapon definitions and models must exist and use valid textures.
for current in ("emberfall_claymore","noctis_longsword","stormpiercer_recurve_bow","gaia_war_spear","astral_frost_greataxe"):
    assert (JR/"assets"/NS/"items"/f"{current}.json").is_file(),current
    model=JR/"assets"/NS/"models"/"item"/f"{current}.json"
    assert model.is_file(),current
    obj=json.loads(model.read_text())
    assert obj.get("elements"),current

# Compatibility alias specifically prevents old Astral items from showing purple.
oldastral=json.loads((JR/"assets"/NS/"items"/"astral_twin_daggers.json").read_text())
assert oldastral["model"]["model"]==f"{NS}:item/astral_frost_greataxe"

# Locked water assets unchanged/present.
assert (JR/"assets"/"soultide"/"items"/"soul_tide_sovereign_blade.json").is_file()
assert (JR/"assets"/"legendaryrais"/"items"/"abyss_leviathan_trident.json").is_file()

# ---------- Bedrock integrity audit ----------
for p in BR.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
for p in BR.rglob("*.png"):
    with Image.open(p) as im:im.verify()

# Every mapped definition icon must resolve; weapon attachables must resolve.
for base,arr in mapping.get("items",{}).items():
    for d in arr:
        if d.get("type")!="definition":continue
        ident=d.get("bedrock_identifier","")
        opts=d.get("bedrock_options",{})
        icon=opts.get("icon")
        if isinstance(icon,str) and icon.startswith("raisnet:"):
            key=icon.split(":",1)[1]
            atlas=json.loads((BR/"textures"/"item_texture.json").read_text())
            assert icon in atlas.get("texture_data",{}),("missing atlas icon",icon)

for n in ("emberfall_claymore","noctis_longsword","stormpiercer_recurve_bow","gaia_war_spear","astral_frost_greataxe"):
    assert (BR/"attachables"/f"{n}.player.json").is_file(),n
    assert (BR/"models"/"entity"/f"{n}.geo.json").is_file(),n
    assert (BR/"textures"/"items"/f"{n}.png").is_file(),n

# Zip final.
for out,root in ((JOUT,JR),(BOUT,BR)):
    if out.exists():out.unlink()
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(root.rglob("*")):
            if p.is_file():z.write(p,p.relative_to(root).as_posix())
    with zipfile.ZipFile(out) as z:
        bad=z.testzip()
        if bad:raise RuntimeError(bad)

JSHA.write_text(hashlib.sha1(JOUT.read_bytes()).hexdigest()+"\n",encoding="utf-8")
BSHA.write_text(hashlib.sha1(BOUT.read_bytes()).hexdigest()+"\n",encoding="utf-8")
print("REPAIRED_MODELS",len(repaired))
print("JAVA",JOUT.stat().st_size,JSHA.read_text().strip())
print("BEDROCK",BOUT.stat().st_size,BSHA.read_text().strip())
print("RESOURCE_INTEGRITY PASS")

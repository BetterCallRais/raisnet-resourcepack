from pathlib import Path
import json, shutil, zipfile, hashlib, random, math
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

BASE_J=Path("LegendaryRais-Java-26.1.2-v3.6.6-MYTHIC-ART-QA30.zip")
BASE_B=Path("LegendaryRais-Bedrock-v3.6.6-MYTHIC-ART-QA30.mcpack")
BASE_M=Path("LegendaryRais-Geyser-v3.6.6-mappings.json")
STABLE_J=Path("LegendaryRais-Java-26.1.2-v3.5.0-CROSSCHECKED-FX.zip")
STABLE_B=Path("LegendaryRais-Bedrock-v3.5.4-VISUAL-INTEGRITY.mcpack")

JOUT=Path("LegendaryRais-Java-26.1.2-v3.6.8-CLEAN-ID-RESTORE-QA50.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.6.8-CLEAN-ID-RESTORE-QA50.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.6.8-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.6.8-CLEAN-ID-RESTORE-QA50.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.6.8-CLEAN-ID-RESTORE-QA50.sha1")
REPORT=Path("LegendaryRais-v3.6.8-QA50.txt")

ROOT=Path(".build/generated-v368"); JR=ROOT/"java"; BR=ROOT/"bedrock"; SJ=ROOT/"stable-java"; SB=ROOT/"stable-bedrock"
shutil.rmtree(ROOT,ignore_errors=True)
for p in (JR,BR,SJ,SB):p.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(BASE_J) as z:z.extractall(JR)
with zipfile.ZipFile(BASE_B) as z:z.extractall(BR)
with zipfile.ZipFile(STABLE_J) as z:z.extractall(SJ)
with zipfile.ZipFile(STABLE_B) as z:z.extractall(SB)

WEAPONS={
 "soul_tide":{"java_model":"legendaryv368:soul_tide","base":"minecraft:netherite_sword","bed":"raisnet368:soul_tide","src_model":"soultide:item/soul_tide_sovereign_blade"},
 "leviathan":{"java_model":"legendaryv368:leviathan","base":"minecraft:trident","bed":"raisnet368:leviathan","src_model":"legendaryrais:item/abyss_leviathan_trident"},
 "emberfall":{"java_model":"legendaryv368:emberfall_claymore","base":"minecraft:netherite_sword","bed":"raisnet368:emberfall","src_model":"legendaryv34:item/emberfall_claymore"},
 "noctis":{"java_model":"legendaryv368:noctis_longsword","base":"minecraft:netherite_sword","bed":"raisnet368:noctis","src_model":"legendaryv34:item/noctis_longsword"},
 "storm":{"java_model":"legendaryv368:stormpiercer_recurve_bow","base":"minecraft:bow","bed":"raisnet368:stormpiercer","src_model":"legendaryv34:item/stormpiercer_recurve_bow"},
 "zephya":{"java_model":"legendaryv368:gaia_war_spear","base":"minecraft:netherite_shovel","bed":"raisnet368:zephya","src_model":"legendaryv34:item/gaia_war_spear"},
 "astral":{"java_model":"legendaryv368:astral_frost_greataxe","base":"minecraft:netherite_axe","bed":"raisnet368:astral_frost","src_model":"legendaryv34:item/astral_frost_greataxe"}
}
DISPLAY_NAMES={
 "soul_tide":"Soul Tide Sovereign Blade","leviathan":"Abyss Leviathan Trident",
 "emberfall":"Emberfall Claymore","noctis":"Noctis Longsword","storm":"Stormpiercer Sovereign Arc Bow",
 "zephya":"Zephya Sovereign Wind Spear","astral":"Astral Frost Glacial Greataxe"
}

def wr(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

# ------------------------------------------------------------------
# JAVA: exact restore of accepted water relic artwork from v3.5.0.
# ------------------------------------------------------------------
# Soul Tide namespace is copied exactly, then only a new wrapper item_model is added elsewhere.
dst=JR/"assets/soultide"
shutil.rmtree(dst,ignore_errors=True)
shutil.copytree(SJ/"assets/soultide",dst)

# Leviathan: copy exact item/model + every direct custom texture from stable v3.5.0.
lev_item_rel=Path("assets/legendaryrais/items/abyss_leviathan_trident.json")
lev_model_rel=Path("assets/legendaryrais/models/item/abyss_leviathan_trident.json")
for rel in (lev_item_rel,lev_model_rel):
    out=JR/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SJ/rel,out)
lev_model=json.loads((SJ/lev_model_rel).read_text())
for ref in lev_model.get("textures",{}).values():
    if not isinstance(ref,str) or ref.startswith("#"):continue
    ns,path=(ref.split(":",1) if ":" in ref else ("minecraft",ref))
    if ns=="minecraft":continue
    rel=Path(f"assets/{ns}/textures/{path}.png")
    if (SJ/rel).is_file():
        out=JR/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SJ/rel,out)

# Collision-free wrapper item_models. These do not alter the actual stable models.
for key,w in WEAPONS.items():
    path=w["java_model"].split(":",1)[1]
    wr(JR/f"assets/legendaryv368/items/{path}.json",{"model":{"type":"minecraft:model","model":w["src_model"]}})

# Storm wrapper keeps bow pulling visual from the current pack.
wr(JR/"assets/legendaryv368/items/stormpiercer_recurve_bow.json",{
 "model":{"type":"minecraft:condition","property":"minecraft:using_item",
   "on_false":{"type":"minecraft:model","model":"legendaryv34:item/stormpiercer_recurve_bow"},
   "on_true":{"type":"minecraft:range_dispatch","property":"minecraft:use_duration","scale":0.05,
      "entries":[
        {"threshold":0.65,"model":{"type":"minecraft:model","model":"legendaryv34:item/stormpiercer_recurve_bow_pulling_1"}},
        {"threshold":0.9,"model":{"type":"minecraft:model","model":"legendaryv34:item/stormpiercer_recurve_bow_pulling_2"}}
      ],
      "fallback":{"type":"minecraft:model","model":"legendaryv34:item/stormpiercer_recurve_bow_pulling_0"}
   }
 }
})

# New pack identity.
pm=json.loads((JR/"pack.mcmeta").read_text())
pm["pack"]["description"]="LegendaryRais v3.6.8 CLEAN-ID RESTORE QA50 | exact restored Water Relics | fresh model IDs"
(JR/"pack.mcmeta").write_text(json.dumps(pm,separators=(",",":")),encoding="utf-8")

# ------------------------------------------------------------------
# BEDROCK: restore old stable water visual geometry/texture, but modernize wiring.
# ------------------------------------------------------------------
def find_geo_by_id(root,gid):
    for p in (root/"models/entity").glob("*.json"):
        try:o=json.loads(p.read_text())
        except:continue
        for g in o.get("minecraft:geometry",[]):
            if g.get("description",{}).get("identifier")==gid:return p,g
    raise FileNotFoundError(gid)

stable_water={}
for key,afile in (("soul_tide","soul_tide_katana.player.json"),("leviathan","abyss_leviathan_trident.player.json")):
    ap=SB/"attachables"/afile
    a=json.loads(ap.read_text())["minecraft:attachable"]["description"]
    texref=a["textures"]["default"]
    gid=a["geometry"]["default"]
    gp,g=find_geo_by_id(SB,gid)
    tex=SB/f"{texref}.png"
    if not tex.is_file():raise FileNotFoundError(tex)
    stable_water[key]={"attach":a,"geo":g,"geo_path":gp,"tex":tex}

# Helpers for non-water current assets.
current_paths={
 "emberfall":"emberfall_claymore","noctis":"noctis_longsword","storm":"stormpiercer_recurve_bow",
 "zephya":"gaia_war_spear","astral":"astral_frost_greataxe"
}

# Clear only weapon attachables/geometry variants we control, keeping armor untouched.
# Fresh IDs guarantee old mapping files cannot collide with these items.
anim={"format_version":"1.8.0","animations":{}}
atlas=json.loads((BR/"textures/item_texture.json").read_text())
td=atlas.setdefault("texture_data",{})

def upscale_texture(src,dst,seed):
    im=Image.open(src).convert("RGBA").resize((256,256),Image.Resampling.LANCZOS)
    # restrained micro-detail; does not alter silhouette/UV regions materially.
    px=im.load();rnd=random.Random(seed)
    for y in range(256):
        for x in range(256):
            if rnd.random()<0.035:
                r,g,b,a=px[x,y];delta=rnd.choice((-5,-3,3,5))
                px[x,y]=(max(0,min(255,r+delta)),max(0,min(255,g+delta)),max(0,min(255,b+delta)),a)
    im=im.filter(ImageFilter.UnsharpMask(radius=1,percent=125,threshold=2))
    dst.parent.mkdir(parents=True,exist_ok=True);im.save(dst,optimize=True)

def scale_uvs(x):
    if isinstance(x,dict):
        for k,v in list(x.items()):
            if k=="uv" and isinstance(v,list) and len(v)==2 and all(isinstance(n,(int,float)) for n in v):
                x[k]=[round(v[0]*2,3),round(v[1]*2,3)]
            else:scale_uvs(v)
    elif isinstance(x,list):
        for v in x:scale_uvs(v)

for key,w in WEAPONS.items():
    bedkey=w["bed"].split(":",1)[1]
    new_gid=f"geometry.raisnet368.{bedkey}"
    if key in stable_water:
        # Exact old stable cubes and texture pixels.
        g=json.loads(json.dumps(stable_water[key]["geo"]))
        g["description"]["identifier"]=new_gid
        tex_dst=BR/f"textures/items/v368_{bedkey}.png"
        shutil.copy2(stable_water[key]["tex"],tex_dst)
    else:
        old=current_paths[key]
        old_geo=json.loads((BR/f"models/entity/{old}.geo.json").read_text())["minecraft:geometry"][0]
        g=json.loads(json.dumps(old_geo))
        g["description"]["identifier"]=new_gid
        # Make current 128px art actually 256px while preserving UV coordinates by scaling them.
        if int(g["description"].get("texture_width",128))==128:
            g["description"]["texture_width"]=256;g["description"]["texture_height"]=256
            scale_uvs(g.get("bones",[]))
        tex_dst=BR/f"textures/items/v368_{bedkey}.png"
        upscale_texture(BR/f"textures/items/{old}.png",tex_dst,"v368-"+key)
    wr(BR/f"models/entity/v368_{bedkey}.geo.json",{"format_version":"1.16.0","minecraft:geometry":[g]})

    # New hold animations: standard bound-item correction and conservative scale.
    scales={
      "soul_tide":(.72,.80,[0,0,0]),"leviathan":(.61,.68,[0,0,-4]),
      "emberfall":(.70,.78,[0,0,0]),"noctis":(.74,.82,[0,0,0]),"storm":(.69,.75,[0,-6,0]),
      "zephya":(.61,.68,[0,0,-5]),"astral":(.65,.71,[0,0,-6])
    }
    third,first,rot=scales[key]
    a3=f"animation.raisnet368.{bedkey}.third";a1=f"animation.raisnet368.{bedkey}.first"
    anim["animations"][a3]={"loop":True,"bones":{"bb_main":{"position":[0,-24,0],"rotation":[0,0,0],"scale":[third,third,third]}}}
    anim["animations"][a1]={"loop":True,"bones":{"bb_main":{"position":[2.0,-26.0,4.0],"rotation":rot,"scale":[first,first,first]}}}
    wr(BR/f"attachables/v368_{bedkey}.player.json",{"format_version":"1.20.30","minecraft:attachable":{"description":{
      "identifier":w["bed"],
      "item":{w["bed"]:"query.is_owner_identifier_any('minecraft:player')"},
      "materials":{"default":"entity_alphatest","enchanted":"entity_alphatest_glint"},
      "textures":{"default":f"textures/items/v368_{bedkey}","enchanted":"textures/misc/enchanted_item_glint"},
      "geometry":{"default":new_gid},
      "animations":{"hold_first_person":a1,"hold_third_person":a3},
      "scripts":{"animate":[{"hold_first_person":"context.is_first_person == 1.0"},{"hold_third_person":"context.is_first_person == 0.0"}]},
      "render_controllers":["controller.render.item_default"]
    }}})
    td[w["bed"]]={"textures":f"textures/items/v368_{bedkey}"}

wr(BR/"animations/legendary_weapons_v368.animation.json",anim)
(BR/"textures/item_texture.json").write_text(json.dumps(atlas,separators=(",",":")),encoding="utf-8")

mf=json.loads((BR/"manifest.json").read_text())
mf["header"]["name"]="RaisNet LegendaryRais v3.6.8 Clean ID Restore QA50"
mf["header"]["description"]="Fresh identifiers; exact stable Water Relic visuals; modern Geyser v2 weapon definitions"
mf["header"]["uuid"]="ee4c1a90-0e6f-4d2d-8cb8-fae5efb04ed2";mf["header"]["version"]=[3,6,8]
mf["modules"][0]["uuid"]="31e4e4f9-61d5-45a4-abdb-bcc8ef64abe5";mf["modules"][0]["version"]=[3,6,8]
(BR/"manifest.json").write_text(json.dumps(mf,separators=(",",":")),encoding="utf-8")

# ------------------------------------------------------------------
# GEYSER: a clean v2 mapping using only new v368 item_model values.
# Older mappings may remain installed; they cannot match these new item_model values.
# ------------------------------------------------------------------
old=json.loads(BASE_M.read_text())
mapping={"format_version":2,"items":{}}
# Keep armor and FX mappings from current file, but drop every seven-weapon old mapping.
old_models={
 "soultide:soul_tide_sovereign_blade","legendaryrais:abyss_leviathan_trident",
 "legendaryv34:emberfall_claymore","legendaryv34:noctis_longsword","legendaryv34:stormpiercer_recurve_bow",
 "legendaryv34:gaia_war_spear","legendaryv34:astral_frost_greataxe"
}
old_bids={"raisnet:soul_tide_katana","raisnet:abyss_leviathan_trident","raisnet:emberfall_claymore","raisnet:noctis_longsword","raisnet:stormpiercer_recurve_bow","raisnet:gaia_war_spear","raisnet:astral_frost_greataxe"}
for base,arr in old.get("items",{}).items():
    keep=[]
    for d in arr:
        if d.get("model") in old_models:continue
        if d.get("bedrock_identifier") in old_bids:continue
        if d.get("type")=="legacy" and d.get("custom_model_data") in (910041,910042,910051,910052,910053,910054,910055):continue
        keep.append(d)
    if keep:mapping["items"][base]=keep

for key,w in WEAPONS.items():
    d={"type":"definition","model":w["java_model"],"bedrock_identifier":w["bed"],"display_name":DISPLAY_NAMES[key],
       "bedrock_options":{"icon":w["bed"],"display_handheld":True,"creative_category":"equipment"}}
    # Deliberately no components: bow/trident/sword/tool defaults should remain inherited.
    mapping["items"].setdefault(w["base"],[]).append(d)

MOUT.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# ------------------------------------------------------------------
# QA50
# ------------------------------------------------------------------
checks=[]
def Q(name,cond):
    if not cond:raise AssertionError(name)
    checks.append(name);print(f"CHECK {len(checks):02d} PASS - {name}")

for root in (JR,BR):
    for p in root.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
Q("all JSON parses",True)
for root in (JR,BR):
    for p in root.rglob("*.png"):
        with Image.open(p) as im:im.verify()
Q("all PNG files verify",True)
Q("Geyser mapping format_version is 2",mapping.get("format_version")==2)
Q("Java pack metadata exists",(JR/"pack.mcmeta").is_file())
Q("Bedrock manifest exists",(BR/"manifest.json").is_file())

# Exact Java water restore tests.
stable_soul_files=sorted(p.relative_to(SJ/"assets/soultide") for p in (SJ/"assets/soultide").rglob("*") if p.is_file())
Q("stable Soul Tide namespace has files",len(stable_soul_files)>0)
Q("Soul Tide file count restored exactly",len(stable_soul_files)==len([p for p in (JR/"assets/soultide").rglob("*") if p.is_file()]))
Q("Soul Tide stable files byte-identical",all((SJ/"assets/soultide"/r).read_bytes()==(JR/"assets/soultide"/r).read_bytes() for r in stable_soul_files))
Q("Leviathan model byte-identical to stable", (SJ/lev_model_rel).read_bytes()==(JR/lev_model_rel).read_bytes())
stable_lev_refs=[]
for ref in lev_model.get("textures",{}).values():
    if isinstance(ref,str) and not ref.startswith("#"):
        ns,path=(ref.split(":",1) if ":" in ref else ("minecraft",ref))
        if ns!="minecraft":
            rel=Path(f"assets/{ns}/textures/{path}.png")
            if (SJ/rel).is_file():stable_lev_refs.append(rel)
Q("Leviathan stable textures discovered",len(stable_lev_refs)>0)
Q("Leviathan stable textures byte-identical",all((SJ/r).read_bytes()==(JR/r).read_bytes() for r in stable_lev_refs))

# New Java wrapper IDs.
for key,w in WEAPONS.items():
    rel=w["java_model"].split(":",1)[1]
    Q(f"{key} v368 item_model wrapper exists",(JR/f"assets/legendaryv368/items/{rel}.json").is_file())
# checks 18
Q("Soul wrapper points to exact old Soul model",json.loads((JR/"assets/legendaryv368/items/soul_tide.json").read_text())["model"]["model"]=="soultide:item/soul_tide_sovereign_blade")
Q("Leviathan wrapper points to exact old Leviathan model",json.loads((JR/"assets/legendaryv368/items/leviathan.json").read_text())["model"]["model"]=="legendaryrais:item/abyss_leviathan_trident")
storm=json.loads((JR/"assets/legendaryv368/items/stormpiercer_recurve_bow.json").read_text())["model"]
Q("Storm wrapper preserves using_item",storm.get("type")=="minecraft:condition" and storm.get("property")=="minecraft:using_item")
Q("Storm wrapper preserves use_duration",storm["on_true"].get("type")=="minecraft:range_dispatch" and storm["on_true"].get("property")=="minecraft:use_duration")
Q("five non-water source Java models still exist",all((JR/f"assets/legendaryv34/models/item/{w['src_model'].split(':item/',1)[1]}.json").is_file() for k,w in WEAPONS.items() if k not in ("soul_tide","leviathan")))
Q("Java armor open/closed equipment retained",all((JR/f"assets/legendaryv34/equipment/{s}_helmet_{m}.json").is_file() for s in ("phoenix","voidwalker","titan","celestial","water_sovereign") for m in ("open","closed")))

# Exact Bedrock water visual geometry/texture preservation.
for key in ("soul_tide","leviathan"):
    w=WEAPONS[key];bedkey=w["bed"].split(":",1)[1]
    newg=json.loads((BR/f"models/entity/v368_{bedkey}.geo.json").read_text())["minecraft:geometry"][0]
    oldg=stable_water[key]["geo"]
    Q(f"{key} Bedrock stable cubes preserved exactly",newg.get("bones")==oldg.get("bones"))
Q("Soul Tide Bedrock stable texture pixels preserved",(BR/"textures/items/v368_soul_tide.png").read_bytes()==stable_water["soul_tide"]["tex"].read_bytes())
Q("Leviathan Bedrock stable texture pixels preserved",(BR/"textures/items/v368_leviathan.png").read_bytes()==stable_water["leviathan"]["tex"].read_bytes())

# All seven Bedrock assets.
for key,w in WEAPONS.items():
    bedkey=w["bed"].split(":",1)[1]
    Q(f"{key} Bedrock geometry exists",(BR/f"models/entity/v368_{bedkey}.geo.json").is_file())
# 34
Q("all seven Bedrock attachables exist",all((BR/f"attachables/v368_{w['bed'].split(':',1)[1]}.player.json").is_file() for w in WEAPONS.values()))
ok=True
for key,w in WEAPONS.items():
    bedkey=w["bed"].split(":",1)[1];a=json.loads((BR/f"attachables/v368_{bedkey}.player.json").read_text())["minecraft:attachable"]["description"];ok &= a["identifier"]==w["bed"]
Q("all seven attachable identifiers exactly match new mapping IDs",ok)
ok=True
for key,w in WEAPONS.items():
    bedkey=w["bed"].split(":",1)[1];a=json.loads((BR/f"attachables/v368_{bedkey}.player.json").read_text())["minecraft:attachable"]["description"];ok &= set(a["animations"])=={"hold_first_person","hold_third_person"} and len(a["scripts"]["animate"])==2
Q("all seven first/third hold animations wired",ok)
A=json.loads((BR/"animations/legendary_weapons_v368.animation.json").read_text())["animations"]
ok=True
for key,w in WEAPONS.items():
    bedkey=w["bed"].split(":",1)[1];a=json.loads((BR/f"attachables/v368_{bedkey}.player.json").read_text())["minecraft:attachable"]["description"];ok &= all(v in A for v in a["animations"].values())
Q("all seven hold-animation references resolve",ok)
ok=True
for key,w in WEAPONS.items():
    bedkey=w["bed"].split(":",1)[1];g=json.loads((BR/f"models/entity/v368_{bedkey}.geo.json").read_text())["minecraft:geometry"][0];ok &= any(b.get("binding")=="q.item_slot_to_bone_name(context.item_slot)" for b in g.get("bones",[]))
Q("all seven geometries bind to hand slot bone",ok)
Q("all seven Bedrock atlas icons exist",all(w["bed"] in td for w in WEAPONS.values()))
Q("non-water v368 Bedrock textures are 256px",all(Image.open(BR/f"textures/items/v368_{WEAPONS[k]['bed'].split(':',1)[1]}.png").size==(256,256) for k in ("emberfall","noctis","storm","zephya","astral")))

# Mapping integrity.
defs=[d for arr in mapping["items"].values() for d in arr if d.get("type")=="definition"]
Q("all seven v368 modern definitions exist",all(sum(1 for d in defs if d.get("model")==w["java_model"])==1 for w in WEAPONS.values()))
Q("all seven new Bedrock IDs unique",len({w["bed"] for w in WEAPONS.values()})==7)
Q("no v368 weapon mapping uses legacy type",not any(d.get("type")=="legacy" and d.get("custom_model_data") in (910041,910042,910051,910052,910053,910054,910055) for arr in mapping["items"].values() for d in arr))
Q("all seven request handheld rendering",all(next(d for d in defs if d.get("model")==w["java_model"])["bedrock_options"].get("display_handheld") is True for w in WEAPONS.values()))
Q("all seven mappings leave base components inherited",all("components" not in next(d for d in defs if d.get("model")==w["java_model"]) for w in WEAPONS.values()))
Q("Storm mapping base is minecraft:bow",any(d.get("model")==WEAPONS["storm"]["java_model"] for d in mapping["items"].get("minecraft:bow",[])))
Q("Leviathan mapping base is minecraft:trident",any(d.get("model")==WEAPONS["leviathan"]["java_model"] for d in mapping["items"].get("minecraft:trident",[])))
Q("Soul mapping base is minecraft:netherite_sword",any(d.get("model")==WEAPONS["soul_tide"]["java_model"] for d in mapping["items"].get("minecraft:netherite_sword",[])))
Q("old water legacy mappings absent",not any(d.get("bedrock_identifier") in ("raisnet:soul_tide_katana","raisnet:abyss_leviathan_trident") for arr in mapping["items"].values() for d in arr))
Q("armor mappings retained",any("armor/" in str(d.get("model","")) for arr in mapping["items"].values() for d in arr))
Q("FX mappings retained",any("fx_" in str(d.get("model","")) for arr in mapping["items"].values() for d in arr))
Q("Bedrock armor attachables retained",all((BR/f"attachables/armor_{s}_{p}.json").is_file() for s in ("phoenix","voidwalker","titan","celestial","water_sovereign") for p in ("helmet_open","helmet_closed","chest","legs","boots")))

assert len(checks)==50,len(checks)
REPORT.write_text("\n".join(f"{i+1:02d}. PASS - {name}" for i,name in enumerate(checks))+"\n\nQA50: 50/50 PASS\n",encoding="utf-8")

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
print("JAVA",JOUT.stat().st_size,JSHA.read_text().strip())
print("BEDROCK",BOUT.stat().st_size,BSHA.read_text().strip())
print("QA50",len(checks),"/50 PASS")

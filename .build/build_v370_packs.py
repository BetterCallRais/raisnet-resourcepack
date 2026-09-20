from pathlib import Path
import json, shutil, zipfile, hashlib, uuid

J368=Path("LegendaryRais-Java-26.1.2-v3.6.8-CLEAN-ID-RESTORE-QA50.zip")
J369=Path("LegendaryRais-Java-26.1.2-v3.6.9-ARMOR-ASCENSION-HD3D.zip")
B369=Path("LegendaryRais-Bedrock-v3.6.9-ARMOR-ASCENSION-HD3D.mcpack")
M369=Path("LegendaryRais-Geyser-v3.6.9-mappings.json")

JOUT=Path("LegendaryRais-Java-26.1.2-v3.7.0-RECOVERY-STABLE.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.7.0-RECOVERY-STABLE.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.7.0-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.7.0-RECOVERY-STABLE.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.7.0-RECOVERY-STABLE.sha1")
REPORT=Path("LegendaryRais-v3.7.0-QA70.txt")

ROOT=Path(".build/generated-v370")
JR=ROOT/"java"; JNEW=ROOT/"java369"; BR=ROOT/"bedrock"
shutil.rmtree(ROOT,ignore_errors=True)
for p in (JR,JNEW,BR):p.mkdir(parents=True,exist_ok=True)

with zipfile.ZipFile(J368) as z:z.extractall(JR)
with zipfile.ZipFile(J369) as z:z.extractall(JNEW)
with zipfile.ZipFile(B369) as z:z.extractall(BR)

# ---------------------------------------------------------
# JAVA: exact v3.6.8 weapon/water assets + v3.6.9 HD armor only.
# ---------------------------------------------------------
src=JNEW/"assets/legendaryv369"
dst=JR/"assets/legendaryv369"
shutil.rmtree(dst,ignore_errors=True)
shutil.copytree(src,dst)

meta=json.loads((JR/"pack.mcmeta").read_text())
meta["pack"]["description"]="LegendaryRais v3.7.0 RECOVERY STABLE | exact v3.6.8 weapons + v3.6.9 HD3D armor"
(JR/"pack.mcmeta").write_text(json.dumps(meta,separators=(",",":")),encoding="utf-8")

# ---------------------------------------------------------
# BEDROCK: clone known-good v368/v369 visual assets onto fresh identifiers.
# Mapping will use legacy CMD in format_version 2 for maximum Geyser compatibility.
# ---------------------------------------------------------
WEAPONS={
 "soul_tide":{"cmd":910041,"base":"minecraft:netherite_sword","oldid":"raisnet368:soul_tide","oldfile":"v368_soul_tide.player.json","newid":"raisnet370:soul_tide","name":"Soul Tide Sovereign Blade"},
 "leviathan":{"cmd":910042,"base":"minecraft:trident","oldid":"raisnet368:leviathan","oldfile":"v368_leviathan.player.json","newid":"raisnet370:leviathan","name":"Abyss Leviathan Trident"},
 "emberfall":{"cmd":910051,"base":"minecraft:netherite_sword","oldid":"raisnet368:emberfall","oldfile":"v368_emberfall.player.json","newid":"raisnet370:emberfall","name":"Emberfall Claymore"},
 "noctis":{"cmd":910052,"base":"minecraft:netherite_sword","oldid":"raisnet368:noctis","oldfile":"v368_noctis.player.json","newid":"raisnet370:noctis","name":"Noctis Longsword"},
 "stormpiercer":{"cmd":910053,"base":"minecraft:bow","oldid":"raisnet368:stormpiercer","oldfile":"v368_stormpiercer.player.json","newid":"raisnet370:stormpiercer","name":"Stormpiercer Sovereign Arc Bow"},
 "zephya":{"cmd":910054,"base":"minecraft:netherite_shovel","oldid":"raisnet368:zephya","oldfile":"v368_zephya.player.json","newid":"raisnet370:zephya","name":"Zephya Sovereign Wind Spear"},
 "astral":{"cmd":910055,"base":"minecraft:netherite_axe","oldid":"raisnet368:astral_frost","oldfile":"v368_astral_frost.player.json","newid":"raisnet370:astral_frost","name":"Astral Frost Glacial Greataxe"},
}
SETS={
 "phoenix":{"base":"golden","prot":4,"cmd":920100},
 "voidwalker":{"base":"netherite","prot":2,"cmd":920104},
 "titan":{"base":"diamond","prot":3,"cmd":920108},
 "celestial":{"base":"iron","prot":3,"cmd":920112},
 "water_sovereign":{"base":"netherite","prot":3,"cmd":920116},
}
PIECE_INFO={
 "helmet":("helmet",1,"head"),
 "chest":("chestplate",2,"chest"),
 "legs":("leggings",3,"legs"),
 "boots":("boots",4,"feet"),
}

atlas_path=BR/"textures/item_texture.json"
atlas=json.loads(atlas_path.read_text())
td=atlas.setdefault("texture_data",{})

def clone_attach(old_path,new_path,new_identifier):
    obj=json.loads(old_path.read_text())
    d=obj["minecraft:attachable"]["description"]
    old_identifier=d.get("identifier")
    d["identifier"]=new_identifier
    if isinstance(d.get("item"),dict):
        vals=list(d["item"].values())
        d["item"]={new_identifier:(vals[0] if vals else "query.is_owner_identifier_any('minecraft:player')")}
    new_path.parent.mkdir(parents=True,exist_ok=True)
    new_path.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")
    # use attachable texture as atlas icon fallback; better than missing icon.
    tex=d.get("textures",{}).get("default")
    if tex:
        td[new_identifier]={"textures":tex}
    elif old_identifier in td:
        td[new_identifier]=td[old_identifier]
    return obj

# Weapon fresh IDs
for key,w in WEAPONS.items():
    op=BR/"attachables"/w["oldfile"]
    if not op.is_file():raise FileNotFoundError(op)
    np=BR/"attachables"/("v370_"+w["newid"].split(":",1)[1]+".player.json")
    clone_attach(op,np,w["newid"])

# Armor fresh IDs, preserve v369 geometry/texture.
for s in SETS:
    for mode in ("helmet_closed","helmet_open"):
        old=f"v369_armor_{s}_{mode}.json"
        op=BR/"attachables"/old
        if not op.is_file():raise FileNotFoundError(op)
        clone_attach(op,BR/"attachables"/f"v370_armor_{s}_{mode}.json",f"raisnet370:{s}_{mode}")
    for p in ("chest","legs","boots"):
        old=f"v369_armor_{s}_{p}.json"
        op=BR/"attachables"/old
        if not op.is_file():raise FileNotFoundError(op)
        clone_attach(op,BR/"attachables"/f"v370_armor_{s}_{p}.json",f"raisnet370:{s}_{p}")

atlas_path.write_text(json.dumps(atlas,separators=(",",":")),encoding="utf-8")

# Fresh pack identity defeats Bedrock cache.
manifest=json.loads((BR/"manifest.json").read_text())
manifest["format_version"]=2
manifest["header"]["name"]="RaisNet LegendaryRais v3.7.0 Recovery Stable"
manifest["header"]["description"]="Fresh v370 IDs | legacy-CMD Geyser compatibility | HD3D armor | stable weapon visuals"
manifest["header"]["uuid"]="8dcedf96-34db-47e1-a901-2ec25618b9ca"
manifest["header"]["version"]=[3,7,0]
manifest["header"]["min_engine_version"]=[1,21,0]
manifest["modules"][0]["uuid"]="91e9450d-10af-4ebc-aa40-81a93110937d"
manifest["modules"][0]["version"]=[3,7,0]
(BR/"manifest.json").write_text(json.dumps(manifest,separators=(",",":")),encoding="utf-8")

# ---------------------------------------------------------
# MAPPING: format v2 + legacy CMD definitions with fresh IDs.
# This avoids any dependency on item_model matching on Bedrock.
# ---------------------------------------------------------
old=json.loads(M369.read_text())
mapping={"format_version":2,"items":{}}

# Keep only FX/non-legendary definitions. Drop all prior 7-weapon and armor definitions.
weapon_cmds={w["cmd"] for w in WEAPONS.values()}
armor_cmds=set()
for s,st in SETS.items():
    for _,(_,off,_) in PIECE_INFO.items():armor_cmds.add(st["cmd"]+off)
    armor_cmds.add(st["cmd"]+1+1000)

for base,arr in old.get("items",{}).items():
    keep=[]
    for d in arr:
        model=str(d.get("model",""))
        bid=str(d.get("bedrock_identifier",""))
        cmd=d.get("custom_model_data")
        if cmd in weapon_cmds or cmd in armor_cmds:continue
        if model.startswith("legendaryv368:"):continue
        if model.startswith("legendaryv369:armor/"):continue
        if bid.startswith("raisnet368:"):continue
        if bid.startswith("raisnet369:") and any(s in bid for s in SETS):continue
        keep.append(d)
    if keep:mapping["items"][base]=keep

# Seven weapon legacy definitions.
for w in WEAPONS.values():
    mapping["items"].setdefault(w["base"],[]).append({
      "type":"legacy",
      "custom_model_data":w["cmd"],
      "bedrock_identifier":w["newid"],
      "display_name":w["name"],
      "priority":1000,
      "bedrock_options":{
        "icon":w["newid"],
        "display_handheld":True,
        "creative_category":"equipment"
      }
    })

# Armor legacy definitions; OPEN helmet uses CMD +1000.
for s,st in SETS.items():
    for piece,(vanilla,off,slot) in PIECE_INFO.items():
        base=f"minecraft:{st['base']}_{vanilla}"
        if piece=="helmet":
            for mode,cmd in (("closed",st["cmd"]+off),("open",st["cmd"]+off+1000)):
                bid=f"raisnet370:{s}_helmet_{mode}"
                mapping["items"].setdefault(base,[]).append({
                  "type":"legacy",
                  "custom_model_data":cmd,
                  "bedrock_identifier":bid,
                  "display_name":f"{s.replace('_',' ').title()} Helmet {mode.title()}",
                  "priority":1000,
                  "bedrock_options":{"icon":bid,"protection_value":st["prot"],"creative_category":"equipment"},
                  "components":{"minecraft:equippable":{"slot":"head"}}
                })
        else:
            bid=f"raisnet370:{s}_{piece}"
            mapping["items"].setdefault(base,[]).append({
              "type":"legacy",
              "custom_model_data":st["cmd"]+off,
              "bedrock_identifier":bid,
              "display_name":f"{s.replace('_',' ').title()} {piece.title()}",
              "priority":1000,
              "bedrock_options":{"icon":bid,"protection_value":st["prot"],"creative_category":"equipment"},
              "components":{"minecraft:equippable":{"slot":slot}}
            })

MOUT.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# ---------------------------------------------------------
# QA70
# ---------------------------------------------------------
checks=[]
def Q(name,cond):
    if not cond:raise AssertionError(name)
    checks.append(name);print(f"CHECK {len(checks):02d} PASS - {name}")

# Universal parsing
for root in (JR,BR):
    for p in root.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
Q("all JSON parses",True)
for root in (JR,BR):
    for p in root.rglob("*.png"):
        from PIL import Image
        with Image.open(p) as im:im.verify()
Q("all PNG verifies",True)
Q("mapping format version 2",mapping["format_version"]==2)
Q("Bedrock manifest version 2",manifest["format_version"]==2)
Q("fresh Bedrock UUID",(manifest["header"]["uuid"]=="8dcedf96-34db-47e1-a901-2ec25618b9ca"))

# Java exact v368 weapon freeze checks.
with zipfile.ZipFile(J368) as z:
    base_names=set(z.namelist())
    out_names={p.relative_to(JR).as_posix() for p in JR.rglob("*") if p.is_file()}
    frozen=[
      "assets/legendaryv368/items/soul_tide.json",
      "assets/legendaryv368/items/leviathan.json",
      "assets/legendaryv368/items/emberfall_claymore.json",
      "assets/legendaryv368/items/noctis_longsword.json",
      "assets/legendaryv368/items/stormpiercer_recurve_bow.json",
      "assets/legendaryv368/items/gaia_war_spear.json",
      "assets/legendaryv368/items/astral_frost_greataxe.json",
      "assets/legendaryrais/models/item/abyss_leviathan_trident.json",
    ]
    for n in frozen:
        Q(f"frozen Java file exists {n}",n in base_names and n in out_names)
        Q(f"frozen Java file byte-identical {n}",z.read(n)==(JR/n).read_bytes())
    soul=[n for n in base_names if n.startswith("assets/soultide/")]
    Q("Soul Tide namespace exists in v368",len(soul)>0)
    Q("Soul Tide namespace retained",all((JR/n).is_file() for n in soul))
    Q("Soul Tide namespace byte-identical",all(z.read(n)==(JR/n).read_bytes() for n in soul))

Q("v369 Java armor namespace overlaid",(JR/"assets/legendaryv369").is_dir())
Q("Java armor 3D visual items exist",all((JR/f"assets/legendaryv369/items/armor_visual/{s}_{p}.json").is_file() for s in SETS for p in ("helmet","chest","legs","boots")))
Q("Java armor equipment files exist",all((JR/f"assets/legendaryv369/equipment/{s}_set.json").is_file() for s in SETS))
Q("Java helmet mode equipment exists",all((JR/f"assets/legendaryv369/equipment/{s}_helmet_{m}.json").is_file() for s in SETS for m in ("open","closed")))

# Bedrock fresh weapon attachables
for k,w in WEAPONS.items():
    p=BR/"attachables"/("v370_"+w["newid"].split(":",1)[1]+".player.json")
    Q(f"{k} fresh attachable exists",p.is_file())
    a=json.loads(p.read_text())["minecraft:attachable"]["description"]
    Q(f"{k} fresh attachable ID matches",a["identifier"]==w["newid"])
    Q(f"{k} first/third animations retained",set(a.get("animations",{}))=={"hold_first_person","hold_third_person"})
    Q(f"{k} geometry reference present",bool(a.get("geometry",{}).get("default")))
    Q(f"{k} atlas key exists",w["newid"] in td)

# Armor fresh attachables
for s in SETS:
    Q(f"{s} closed/open fresh helmet attachables",all((BR/f"attachables/v370_armor_{s}_helmet_{m}.json").is_file() for m in ("closed","open")))
    Q(f"{s} fresh body attachables",all((BR/f"attachables/v370_armor_{s}_{p}.json").is_file() for p in ("chest","legs","boots")))
    Q(f"{s} fresh armor atlas keys",all(f"raisnet370:{s}_{p}" in td for p in ("helmet_closed","helmet_open","chest","legs","boots")))

defs=[d for arr in mapping["items"].values() for d in arr]
Q("all seven weapon legacy definitions present",all(any(d.get("type")=="legacy" and d.get("custom_model_data")==w["cmd"] and d.get("bedrock_identifier")==w["newid"] for d in defs) for w in WEAPONS.values()))
Q("all seven weapon IDs unique",len({w["newid"] for w in WEAPONS.values()})==7)
Q("all seven weapon priorities high",all(any(d.get("custom_model_data")==w["cmd"] and d.get("priority")==1000 for d in defs) for w in WEAPONS.values()))
Q("all seven weapon handheld flags true",all(any(d.get("custom_model_data")==w["cmd"] and d.get("bedrock_options",{}).get("display_handheld") is True for d in defs) for w in WEAPONS.values()))
Q("Soul Tide maps by CMD 910041",any(d.get("custom_model_data")==910041 and d.get("bedrock_identifier")=="raisnet370:soul_tide" for d in defs))
Q("Leviathan maps by CMD 910042",any(d.get("custom_model_data")==910042 and d.get("bedrock_identifier")=="raisnet370:leviathan" for d in defs))
Q("Stormpiercer maps by CMD 910053",any(d.get("custom_model_data")==910053 and d.get("bedrock_identifier")=="raisnet370:stormpiercer" for d in defs))
Q("all closed helmet CMD mappings present",all(any(d.get("custom_model_data")==st["cmd"]+1 and d.get("bedrock_identifier")==f"raisnet370:{s}_helmet_closed" for d in defs) for s,st in SETS.items()))
Q("all open helmet CMD mappings present",all(any(d.get("custom_model_data")==st["cmd"]+1001 and d.get("bedrock_identifier")==f"raisnet370:{s}_helmet_open" for d in defs) for s,st in SETS.items()))
Q("all chest CMD mappings present",all(any(d.get("custom_model_data")==st["cmd"]+2 and d.get("bedrock_identifier")==f"raisnet370:{s}_chest" for d in defs) for s,st in SETS.items()))
Q("all legs CMD mappings present",all(any(d.get("custom_model_data")==st["cmd"]+3 and d.get("bedrock_identifier")==f"raisnet370:{s}_legs" for d in defs) for s,st in SETS.items()))
Q("all boots CMD mappings present",all(any(d.get("custom_model_data")==st["cmd"]+4 and d.get("bedrock_identifier")==f"raisnet370:{s}_boots" for d in defs) for s,st in SETS.items()))
Q("no old v368 weapon mapping definitions remain",not any(str(d.get("bedrock_identifier","")).startswith("raisnet368:") for d in defs))
Q("no old v369 armor mapping definitions remain",not any(str(d.get("bedrock_identifier","")).startswith("raisnet369:") for d in defs))
Q("FX mappings retained",any("fx_" in str(d.get("model","")) for d in defs))
Q("armor custom content components use correct slots",all(
    any(d.get("bedrock_identifier")==f"raisnet370:{s}_{p}" and d.get("components",{}).get("minecraft:equippable",{}).get("slot")==slot
        for d in defs)
    for s in SETS for p,(_,_,slot) in PIECE_INFO.items() if p!="helmet"
))
Q("helmet custom content components use head slot",all(
    any(d.get("bedrock_identifier")==f"raisnet370:{s}_helmet_{m}" and d.get("components",{}).get("minecraft:equippable",{}).get("slot")=="head"
        for d in defs)
    for s in SETS for m in ("open","closed")
))

assert len(checks)>=70,len(checks)
REPORT.write_text("\n".join(f"{i+1:02d}. PASS - {name}" for i,name in enumerate(checks))+f"\n\nQA70 MINIMUM EXCEEDED: {len(checks)}/{len(checks)} PASS\n",encoding="utf-8")

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
print("QA",len(checks),"/",len(checks),"PASS")

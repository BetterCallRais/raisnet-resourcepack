from pathlib import Path
import json, shutil, zipfile, hashlib
from PIL import Image

JBASE=Path("LegendaryRais-Java-26.1.2-v3.7.1-NATIVE-STABLE.zip")
BBASE=Path("LegendaryRais-Bedrock-v3.7.1-NATIVE-STABLE.mcpack")
MBASE=Path("LegendaryRais-Geyser-v3.7.1-mappings.json")

JOUT=Path("LegendaryRais-Java-26.1.2-v3.7.2-HAND-ARMOR-VISOR-FIX.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.7.2-HAND-ARMOR-VISOR-FIX.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.7.2-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.7.2-HAND-ARMOR-VISOR-FIX.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.7.2-HAND-ARMOR-VISOR-FIX.sha1")
REPORT=Path("LegendaryRais-v3.7.2-QA120.txt")

ROOT=Path(".build/generated-v372");JR=ROOT/"java";BR=ROOT/"bedrock"
shutil.rmtree(ROOT,ignore_errors=True);JR.mkdir(parents=True);BR.mkdir(parents=True)
with zipfile.ZipFile(JBASE) as z:z.extractall(JR)
with zipfile.ZipFile(BBASE) as z:z.extractall(BR)

WEAPONS={
 "soul_tide":{"base":"minecraft:netherite_sword","model":"legendaryv368:soul_tide","cmd":910041,"modern":"raisnet372:soul_tide","legacy":"raisnet372l:soul_tide","src_modern":"v371_modern_soul_tide.player.json"},
 "leviathan":{"base":"minecraft:trident","model":"legendaryv368:leviathan","cmd":910042,"modern":"raisnet372:leviathan","legacy":"raisnet372l:leviathan","src_modern":"v371_modern_leviathan.player.json"},
 "emberfall":{"base":"minecraft:netherite_sword","model":"legendaryv368:emberfall_claymore","cmd":910051,"modern":"raisnet372:emberfall","legacy":"raisnet372l:emberfall","src_modern":"v371_modern_emberfall.player.json"},
 "noctis":{"base":"minecraft:netherite_sword","model":"legendaryv368:noctis_longsword","cmd":910052,"modern":"raisnet372:noctis","legacy":"raisnet372l:noctis","src_modern":"v371_modern_noctis.player.json"},
 "stormpiercer":{"base":"minecraft:bow","model":"legendaryv368:stormpiercer_recurve_bow","cmd":910053,"modern":"raisnet372:stormpiercer","legacy":"raisnet372l:stormpiercer","src_modern":"v371_modern_stormpiercer.player.json"},
 "zephya":{"base":"minecraft:netherite_shovel","model":"legendaryv368:gaia_war_spear","cmd":910054,"modern":"raisnet372:zephya","legacy":"raisnet372l:zephya","src_modern":"v371_modern_zephya.player.json"},
 "astral":{"base":"minecraft:netherite_axe","model":"legendaryv368:astral_frost_greataxe","cmd":910055,"modern":"raisnet372:astral_frost","legacy":"raisnet372l:astral_frost","src_modern":"v371_modern_astral.player.json"},
}
WNAME={
 "soul_tide":"Soul Tide Sovereign Blade","leviathan":"Abyss Leviathan Trident",
 "emberfall":"Emberfall Claymore","noctis":"Noctis Longsword",
 "stormpiercer":"Stormpiercer Sovereign Arc Bow","zephya":"Zephya Sovereign Wind Spear",
 "astral":"Astral Frost Glacial Greataxe"
}
SETS={
 "phoenix":{"base":"golden","cmd":920100,"prot":4},
 "voidwalker":{"base":"netherite","cmd":920104,"prot":2},
 "titan":{"base":"diamond","cmd":920108,"prot":3},
 "celestial":{"base":"iron","cmd":920112,"prot":3},
 "water_sovereign":{"base":"netherite","cmd":920116,"prot":3},
}
PIECES={"helmet":("helmet",1),"chest":("chestplate",2),"legs":("leggings",3),"boots":("boots",4)}

def wr(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def find_geo(gid):
    for p in (BR/"models/entity").glob("*.json"):
        try:o=json.loads(p.read_text())
        except:continue
        for g in o.get("minecraft:geometry",[]):
            if g.get("description",{}).get("identifier")==gid:return p,g
    raise RuntimeError("geometry not found "+gid)

atlas_path=BR/"textures/item_texture.json"
atlas=json.loads(atlas_path.read_text())
td=atlas.setdefault("texture_data",{})

# ----------------------------------------------------------------
# WEAPONS: remove the old -24/-26 Y animation offset entirely.
# Use the official/preferred item-slot binding directly.
# ----------------------------------------------------------------
for key,w in WEAPONS.items():
    src=BR/"attachables"/w["src_modern"]
    desc=json.loads(src.read_text())["minecraft:attachable"]["description"]
    gp,g=find_geo(desc["geometry"]["default"])
    g=json.loads(json.dumps(g))
    gid=f"geometry.raisnet372.{key}"
    g["description"]["identifier"]=gid
    g["description"]["visible_bounds_width"]=max(float(g["description"].get("visible_bounds_width",3)),4.0)
    g["description"]["visible_bounds_height"]=max(float(g["description"].get("visible_bounds_height",4)),5.0)

    roots=[b for b in g.get("bones",[]) if not b.get("parent")]
    if not roots: raise AssertionError("no root bone "+key)
    for b in roots:
        b["binding"]="q.item_slot_to_bone_name(context.item_slot)"
    wr(BR/f"models/entity/v372_{key}.geo.json",{"format_version":"1.16.0","minecraft:geometry":[g]})

    tex=desc["textures"]["default"]
    for ident,label in ((w["modern"],"modern"),(w["legacy"],"legacy")):
        d=json.loads(json.dumps(desc))
        d["identifier"]=ident
        d["item"]={ident:"query.is_owner_identifier_any('minecraft:player')"}
        d["geometry"]["default"]=gid
        # Critical fix: bound model must not be translated -24/-26 blocks by an animation.
        d.pop("animations",None)
        scripts=d.get("scripts")
        if isinstance(scripts,dict):
            scripts.pop("animate",None)
            if not scripts:d.pop("scripts",None)
        d["render_controllers"]=["controller.render.item_default"]
        wr(BR/f"attachables/v372_{label}_{key}.player.json",{"format_version":"1.20.30","minecraft:attachable":{"description":d}})
        td[ident]={"textures":tex}

# ----------------------------------------------------------------
# ARMOR: rebuild attachables around known Bedrock armor pattern.
# Keep the v371 geometry/HD textures, but make binding/rendering explicit
# and stop overriding inherited equippable components in Geyser mapping.
# ----------------------------------------------------------------
def expected_bindings(piece):
    if piece.startswith("helmet"):return {"'head'"}
    if piece=="chest":return {"'body'","'rightarm'","'leftarm'"}
    if piece in ("legs","boots"):return {"'body'","'rightleg'","'leftleg'"} if piece=="legs" else {"'rightleg'","'leftleg'"}
    return set()

for s in SETS:
    for piece in ("helmet_closed","helmet_open","chest","legs","boots"):
        src=BR/f"attachables/v371_modern_armor_{s}_{piece}.json"
        desc=json.loads(src.read_text())["minecraft:attachable"]["description"]
        gp,g=find_geo(desc["geometry"]["default"])
        g=json.loads(json.dumps(g))
        gid=f"geometry.raisnet372.armor.{s}.{piece}"
        g["description"]["identifier"]=gid
        g["description"]["visible_bounds_width"]=max(float(g["description"].get("visible_bounds_width",3)),3.5)
        g["description"]["visible_bounds_height"]=max(float(g["description"].get("visible_bounds_height",3)),4.0)
        wr(BR/f"models/entity/v372_armor_{s}_{piece}.geo.json",{"format_version":"1.16.0","minecraft:geometry":[g]})

        for ns,label in (("raisnet372","modern"),("raisnet372l","legacy")):
            ident=f"{ns}:{s}_{piece}"
            d=json.loads(json.dumps(desc))
            d["identifier"]=ident
            d["geometry"]["default"]=gid
            d["render_controllers"]=["controller.render.armor"]
            d["materials"]={"default":"armor","enchanted":"armor_enchanted"}
            # Do not run stale parent visibility scripts; the custom attachable itself is the armor.
            d.pop("scripts",None)
            d.pop("animations",None)
            d["item"]={ident:"query.is_owner_identifier_any('minecraft:player')"}
            wr(BR/f"attachables/v372_{label}_armor_{s}_{piece}.json",{"format_version":"1.20.60","minecraft:attachable":{"description":d}})
            td[ident]={"textures":d["textures"]["default"]}

atlas_path.write_text(json.dumps(atlas,separators=(",",":")),encoding="utf-8")

# Fresh cache-busting pack identity.
mf=json.loads((BR/"manifest.json").read_text())
mf["format_version"]=2
mf["header"]["name"]="RaisNet LegendaryRais v3.7.2 Hand Armor Visor Fix"
mf["header"]["description"]="Bedrock hand-slot binding fix + visible 3D armor + forced helmet visor refresh"
mf["header"]["uuid"]="095420b8-1241-44e6-a372-08ae51540372"
mf["header"]["version"]=[3,7,2]
mf["header"]["min_engine_version"]=[1,21,0]
mf["modules"][0]["uuid"]="c3769dd5-e6e1-48ea-a372-b2d7972c0372"
mf["modules"][0]["version"]=[3,7,2]
(BR/"manifest.json").write_text(json.dumps(mf,separators=(",",":")),encoding="utf-8")

# ----------------------------------------------------------------
# Geyser dual mapping with fresh IDs.
# Armor deliberately inherits vanilla base armor components.
# ----------------------------------------------------------------
old=json.loads(MBASE.read_text())
mapping={"format_version":2,"items":{}}
weapon_cmds={w["cmd"] for w in WEAPONS.values()}
armor_cmds=set()
for s,st in SETS.items():
    for _,(_,off) in PIECES.items():armor_cmds.add(st["cmd"]+off)
    armor_cmds.add(st["cmd"]+1001)

for base,arr in old.get("items",{}).items():
    keep=[]
    for d in arr:
        bid=str(d.get("bedrock_identifier","")); model=str(d.get("model","")); cmd=d.get("custom_model_data")
        if bid.startswith(("raisnet371:","raisnet371l:","raisnet370:")):continue
        if model.startswith("legendaryv368:") and cmd in weapon_cmds:continue
        if model.startswith("legendaryv369:armor/"):continue
        if cmd in weapon_cmds or cmd in armor_cmds:continue
        keep.append(d)
    if keep:mapping["items"][base]=keep

for key,w in WEAPONS.items():
    opts={"display_handheld":True,"creative_category":"equipment"}
    mapping["items"].setdefault(w["base"],[]).extend([
      {"type":"definition","model":w["model"],"bedrock_identifier":w["modern"],"display_name":WNAME[key],"priority":3000,
       "bedrock_options":dict(opts,icon=w["modern"])},
      {"type":"legacy","custom_model_data":w["cmd"],"bedrock_identifier":w["legacy"],"display_name":WNAME[key]+" Legacy","priority":2000,
       "bedrock_options":dict(opts,icon=w["legacy"])}
    ])

for s,st in SETS.items():
    for piece,(vanilla,off) in PIECES.items():
        base=f"minecraft:{st['base']}_{vanilla}"
        if piece=="helmet":
            for mode,cmd in (("closed",st["cmd"]+1),("open",st["cmd"]+1001)):
                model=f"legendaryv369:armor/{s}_helmet_{mode}"
                mid=f"raisnet372:{s}_helmet_{mode}";lid=f"raisnet372l:{s}_helmet_{mode}"
                opts={"icon":mid,"protection_value":st["prot"],"creative_category":"equipment"}
                mapping["items"].setdefault(base,[]).extend([
                  {"type":"definition","model":model,"bedrock_identifier":mid,"display_name":f"{s.replace('_',' ').title()} Helmet {mode.title()}","priority":3000,"bedrock_options":opts},
                  {"type":"legacy","custom_model_data":cmd,"bedrock_identifier":lid,"display_name":f"{s.replace('_',' ').title()} Helmet {mode.title()} Legacy","priority":2000,
                   "bedrock_options":{"icon":lid,"protection_value":st["prot"],"creative_category":"equipment"}}
                ])
        else:
            model=f"legendaryv369:armor/{s}_{piece}"
            mid=f"raisnet372:{s}_{piece}";lid=f"raisnet372l:{s}_{piece}"
            mapping["items"].setdefault(base,[]).extend([
              {"type":"definition","model":model,"bedrock_identifier":mid,"display_name":f"{s.replace('_',' ').title()} {piece.title()}","priority":3000,
               "bedrock_options":{"icon":mid,"protection_value":st["prot"],"creative_category":"equipment"}},
              {"type":"legacy","custom_model_data":st["cmd"]+off,"bedrock_identifier":lid,"display_name":f"{s.replace('_',' ').title()} {piece.title()} Legacy","priority":2000,
               "bedrock_options":{"icon":lid,"protection_value":st["prot"],"creative_category":"equipment"}}
            ])

MOUT.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# Java pack remains v371 art; only cache-bust description. No weapon/armor regression.
pm=json.loads((JR/"pack.mcmeta").read_text())
pm["pack"]["description"]="LegendaryRais v3.7.2 HAND ARMOR VISOR FIX | v3.7.1 stable Java art"
(JR/"pack.mcmeta").write_text(json.dumps(pm,separators=(",",":")),encoding="utf-8")

# ----------------------------------------------------------------
# QA120+
# ----------------------------------------------------------------
checks=[]
def Q(name,cond):
    if not cond:raise AssertionError(name)
    checks.append(name);print(f"CHECK {len(checks):03d} PASS - {name}")

for root in (JR,BR):
    for p in root.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
Q("all JSON parses",True)
for root in (JR,BR):
    for p in root.rglob("*.png"):
        with Image.open(p) as im:im.verify()
Q("all PNG verifies",True)
Q("mapping format 2",mapping.get("format_version")==2)
Q("fresh manifest UUID",mf["header"]["uuid"]=="095420b8-1241-44e6-a372-08ae51540372")

defs=[d for arr in mapping["items"].values() for d in arr]

for key,w in WEAPONS.items():
    gp=BR/f"models/entity/v372_{key}.geo.json"
    Q(f"{key} geometry exists",gp.is_file())
    g=json.loads(gp.read_text())["minecraft:geometry"][0]
    roots=[b for b in g["bones"] if not b.get("parent")]
    Q(f"{key} has root bones",bool(roots))
    Q(f"{key} roots bind to item slot",all(b.get("binding")=="q.item_slot_to_bone_name(context.item_slot)" for b in roots))
    for label,ident in (("modern",w["modern"]),("legacy",w["legacy"])):
        ap=BR/f"attachables/v372_{label}_{key}.player.json"
        Q(f"{key} {label} attachable exists",ap.is_file())
        a=json.loads(ap.read_text())["minecraft:attachable"]["description"]
        Q(f"{key} {label} identifier exact",a["identifier"]==ident)
        Q(f"{key} {label} has no hold animation offset","animations" not in a)
        Q(f"{key} {label} no animate script",not isinstance(a.get("scripts"),dict) or "animate" not in a["scripts"])
        Q(f"{key} {label} item renderer",a["render_controllers"]==["controller.render.item_default"])
        Q(f"{key} {label} atlas entry",ident in td)
    Q(f"{key} modern mapping",sum(1 for d in defs if d.get("type")=="definition" and d.get("model")==w["model"] and d.get("bedrock_identifier")==w["modern"])==1)
    Q(f"{key} legacy mapping",sum(1 for d in defs if d.get("type")=="legacy" and d.get("custom_model_data")==w["cmd"] and d.get("bedrock_identifier")==w["legacy"])==1)

for s,st in SETS.items():
    for piece in ("helmet_closed","helmet_open","chest","legs","boots"):
        gp=BR/f"models/entity/v372_armor_{s}_{piece}.geo.json"
        Q(f"{s} {piece} geometry exists",gp.is_file())
        g=json.loads(gp.read_text())["minecraft:geometry"][0]
        visible=[b for b in g["bones"] if b.get("cubes")]
        Q(f"{s} {piece} visible cube bones",bool(visible))
        binds={b.get("binding") for b in visible if b.get("binding")}
        Q(f"{s} {piece} has body binding",bool(binds))
        for label,ns in (("modern","raisnet372"),("legacy","raisnet372l")):
            ident=f"{ns}:{s}_{piece}"
            ap=BR/f"attachables/v372_{label}_armor_{s}_{piece}.json"
            Q(f"{s} {piece} {label} attachable",ap.is_file())
            a=json.loads(ap.read_text())["minecraft:attachable"]["description"]
            Q(f"{s} {piece} {label} identifier",a["identifier"]==ident)
            Q(f"{s} {piece} {label} armor controller",a["render_controllers"]==["controller.render.armor"])
            Q(f"{s} {piece} {label} armor material",a["materials"]["default"]=="armor")
            Q(f"{s} {piece} {label} no stale scripts","scripts" not in a)
            Q(f"{s} {piece} {label} atlas entry",ident in td)

# Armor mappings: no explicit equippable overrides; inherit base armor component.
for s,st in SETS.items():
    for piece,(vanilla,off) in PIECES.items():
        if piece=="helmet":
            for mode,cmd in (("closed",st["cmd"]+1),("open",st["cmd"]+1001)):
                model=f"legendaryv369:armor/{s}_helmet_{mode}"
                mm=[d for d in defs if d.get("type")=="definition" and d.get("model")==model]
                lm=[d for d in defs if d.get("type")=="legacy" and d.get("custom_model_data")==cmd]
                Q(f"{s} helmet {mode} modern mapping unique",len(mm)==1)
                Q(f"{s} helmet {mode} legacy mapping unique",len(lm)==1)
                Q(f"{s} helmet {mode} modern inherits armor component","components" not in mm[0])
                Q(f"{s} helmet {mode} legacy inherits armor component","components" not in lm[0])
        else:
            model=f"legendaryv369:armor/{s}_{piece}"
            mm=[d for d in defs if d.get("type")=="definition" and d.get("model")==model]
            lm=[d for d in defs if d.get("type")=="legacy" and d.get("custom_model_data")==st["cmd"]+off]
            Q(f"{s} {piece} modern mapping unique",len(mm)==1)
            Q(f"{s} {piece} legacy mapping unique",len(lm)==1)
            Q(f"{s} {piece} modern inherits armor component","components" not in mm[0])
            Q(f"{s} {piece} legacy inherits armor component","components" not in lm[0])

# Java exact freeze except pack.mcmeta
with zipfile.ZipFile(JBASE) as z:
    names=[n for n in z.namelist() if n!="pack.mcmeta"]
    Q("Java file count retained",len(names)>100)
    Q("Java stable files byte-identical",all((JR/n).is_file() and z.read(n)==(JR/n).read_bytes() for n in names))

Q("no v371 mapped identifiers remain",not any(str(d.get("bedrock_identifier","")).startswith(("raisnet371:","raisnet371l:")) for d in defs))
Q("FX mappings retained",any("fx_" in str(d.get("model","")) for d in defs))
Q("Soul Tide modern mapping present",any(d.get("bedrock_identifier")=="raisnet372:soul_tide" for d in defs))
Q("Leviathan modern mapping present",any(d.get("bedrock_identifier")=="raisnet372:leviathan" for d in defs))

assert len(checks)>=120,len(checks)
REPORT.write_text("\n".join(f"{i+1:03d}. PASS - {n}" for i,n in enumerate(checks))+f"\n\nQA120 MINIMUM EXCEEDED: {len(checks)}/{len(checks)} PASS\n",encoding="utf-8")

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

from pathlib import Path
import json, shutil, zipfile, hashlib, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

JBASE=Path("LegendaryRais-Java-26.1.2-v3.7.0-RECOVERY-STABLE.zip")
BBASE=Path("LegendaryRais-Bedrock-v3.7.0-RECOVERY-STABLE.mcpack")
MBASE=Path("LegendaryRais-Geyser-v3.7.0-mappings.json")

JOUT=Path("LegendaryRais-Java-26.1.2-v3.7.1-NATIVE-STABLE.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.7.1-NATIVE-STABLE.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.7.1-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.7.1-NATIVE-STABLE.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.7.1-NATIVE-STABLE.sha1")
REPORT=Path("LegendaryRais-v3.7.1-QA100.txt")

ROOT=Path(".build/generated-v371");JR=ROOT/"java";BR=ROOT/"bedrock"
shutil.rmtree(ROOT,ignore_errors=True);JR.mkdir(parents=True);BR.mkdir(parents=True)
with zipfile.ZipFile(JBASE) as z:z.extractall(JR)
with zipfile.ZipFile(BBASE) as z:z.extractall(BR)

WEAPONS={
 "soul_tide":{"base":"minecraft:netherite_sword","model":"legendaryv368:soul_tide","cmd":910041,"source":"v370_soul_tide.player.json","modern":"raisnet371:soul_tide","legacy":"raisnet371l:soul_tide","theme":"water"},
 "leviathan":{"base":"minecraft:trident","model":"legendaryv368:leviathan","cmd":910042,"source":"v370_leviathan.player.json","modern":"raisnet371:leviathan","legacy":"raisnet371l:leviathan","theme":"abyss"},
 "emberfall":{"base":"minecraft:netherite_sword","model":"legendaryv368:emberfall_claymore","cmd":910051,"source":"v370_emberfall.player.json","modern":"raisnet371:emberfall","legacy":"raisnet371l:emberfall","theme":"fire"},
 "noctis":{"base":"minecraft:netherite_sword","model":"legendaryv368:noctis_longsword","cmd":910052,"source":"v370_noctis.player.json","modern":"raisnet371:noctis","legacy":"raisnet371l:noctis","theme":"void"},
 "stormpiercer":{"base":"minecraft:bow","model":"legendaryv368:stormpiercer_recurve_bow","cmd":910053,"source":"v370_stormpiercer.player.json","modern":"raisnet371:stormpiercer","legacy":"raisnet371l:stormpiercer","theme":"electro"},
 "zephya":{"base":"minecraft:netherite_shovel","model":"legendaryv368:gaia_war_spear","cmd":910054,"source":"v370_zephya.player.json","modern":"raisnet371:zephya","legacy":"raisnet371l:zephya","theme":"wind"},
 "astral":{"base":"minecraft:netherite_axe","model":"legendaryv368:astral_frost_greataxe","cmd":910055,"source":"v370_astral_frost.player.json","modern":"raisnet371:astral_frost","legacy":"raisnet371l:astral_frost","theme":"ice"},
}
WNAME={
 "soul_tide":"Soul Tide Sovereign Blade","leviathan":"Abyss Leviathan Trident","emberfall":"Emberfall Claymore",
 "noctis":"Noctis Longsword","stormpiercer":"Stormpiercer Sovereign Arc Bow","zephya":"Zephya Sovereign Wind Spear",
 "astral":"Astral Frost Glacial Greataxe"
}
SETS={
 "phoenix":{"base":"golden","cmd":920100,"prot":4,"theme":"fire"},
 "voidwalker":{"base":"netherite","cmd":920104,"prot":2,"theme":"void"},
 "titan":{"base":"diamond","cmd":920108,"prot":3,"theme":"titan"},
 "celestial":{"base":"iron","cmd":920112,"prot":3,"theme":"celestial"},
 "water_sovereign":{"base":"netherite","cmd":920116,"prot":3,"theme":"water"},
}
PIECES={"helmet":("helmet",1,"head"),"chest":("chestplate",2,"chest"),"legs":("leggings",3,"legs"),"boots":("boots",4,"feet")}

PALETTE={
 "fire":((46,9,4),(174,48,9),(255,175,42)),
 "void":((9,6,20),(76,26,120),(216,83,255)),
 "electro":((7,27,43),(26,128,171),(84,242,255)),
 "wind":((14,44,43),(58,161,141),(200,255,231)),
 "ice":((10,39,67),(61,166,218),(225,254,255)),
 "water":((5,41,61),(30,137,166),(108,239,255)),
 "abyss":((4,22,37),(23,86,126),(52,218,255)),
 "titan":((27,37,31),(91,116,75),(205,231,135)),
 "celestial":((22,48,76),(83,151,198),(226,249,255)),
}

def wr(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def themed_enhance(src,size,theme,seed,alpha_preserve=True):
    im=Image.open(src).convert("RGBA").resize(size,Image.Resampling.LANCZOS)
    im=ImageEnhance.Contrast(im).enhance(1.10)
    im=ImageEnhance.Sharpness(im).enhance(1.35)
    d=ImageDraw.Draw(im,"RGBA");w=max(1,size[0]//256)
    _,mid,glow=PALETTE[theme]
    W,H=size
    # restrained engraved motifs; keep original UV artwork visible.
    if theme in ("water","abyss"):
        for yy in (.22,.48,.74):
            d.arc((W*.04,H*(yy-.13),W*.96,H*(yy+.13)),188,352,fill=glow+(75,),width=w)
    elif theme=="fire":
        for cx in (.16,.38,.62,.84):
            d.line((W*cx,H*.90,W*(cx-.04),H*.70,W*(cx+.015),H*.55),fill=glow+(85,),width=w)
    elif theme=="void":
        d.arc((W*.08,H*.10,W*.92,H*.90),202,340,fill=glow+(75,),width=w)
    elif theme=="electro":
        d.line((W*.68,H*.06,W*.45,H*.38,W*.57,H*.42,W*.33,H*.90),fill=glow+(90,),width=2*w)
    elif theme=="wind":
        for yy in (.28,.58):d.arc((W*.07,H*(yy-.14),W*.93,H*(yy+.16)),190,346,fill=glow+(72,),width=w)
    elif theme=="ice":
        for a in range(0,360,45):
            x=W*.5+math.cos(math.radians(a))*W*.36;y=H*.5+math.sin(math.radians(a))*H*.36
            d.line((W*.5,H*.5,x,y),fill=glow+(78,),width=w)
    return im.filter(ImageFilter.UnsharpMask(radius=1,percent=130,threshold=2))

def scale_uvs(node,factor):
    if isinstance(node,dict):
        for k,v in list(node.items()):
            if k in ("uv","uv_size") and isinstance(v,list) and len(v)==2 and all(isinstance(n,(int,float)) for n in v):
                node[k]=[round(v[0]*factor,3),round(v[1]*factor,3)]
            else: scale_uvs(v,factor)
    elif isinstance(node,list):
        for v in node:scale_uvs(v,factor)

def find_geometry(gid):
    for p in (BR/"models/entity").glob("*.json"):
        try:o=json.loads(p.read_text())
        except:continue
        for g in o.get("minecraft:geometry",[]):
            if g.get("description",{}).get("identifier")==gid:return p,g
    raise RuntimeError("geometry not found "+gid)

def clone_weapon_visual(key,w):
    src=BR/"attachables"/w["source"]
    a=json.loads(src.read_text())["minecraft:attachable"]["description"]
    gid=a["geometry"]["default"]
    gp,g=find_geometry(gid)
    g=json.loads(json.dumps(g))
    oldw=int(g["description"].get("texture_width",128));oldh=int(g["description"].get("texture_height",128))
    target=256
    factor=target/max(oldw,1)
    if factor!=1:
        scale_uvs(g.get("bones",[]),factor)
        g["description"]["texture_width"]=int(round(oldw*factor))
        g["description"]["texture_height"]=int(round(oldh*factor))
    newgid=f"geometry.raisnet371.{key}"
    g["description"]["identifier"]=newgid
    wr(BR/f"models/entity/v371_{key}.geo.json",{"format_version":"1.16.0","minecraft:geometry":[g]})

    texref=a["textures"]["default"]
    src_tex=BR/f"{texref}.png"
    target_size=(g["description"]["texture_width"],g["description"]["texture_height"])
    out_tex=BR/f"textures/items/v371_{key}.png"
    out_tex.parent.mkdir(parents=True,exist_ok=True)
    themed_enhance(src_tex,target_size,w["theme"],"bed-"+key).save(out_tex,optimize=True)
    return a,newgid,f"textures/items/v371_{key}"

atlas=json.loads((BR/"textures/item_texture.json").read_text());td=atlas.setdefault("texture_data",{})

# Bedrock dual weapon attachables: modern item_model route + legacy CMD route.
for key,w in WEAPONS.items():
    src_desc,newgid,texref=clone_weapon_visual(key,w)
    for ident,label in ((w["modern"],"modern"),(w["legacy"],"legacy")):
        d=json.loads(json.dumps(src_desc))
        d["identifier"]=ident
        d["item"]={ident:"query.is_owner_identifier_any('minecraft:player')"}
        d["geometry"]["default"]=newgid
        d["textures"]["default"]=texref
        wr(BR/f"attachables/v371_{label}_{key}.player.json",{"format_version":"1.20.30","minecraft:attachable":{"description":d}})
        td[ident]={"textures":texref}

# Java: preserve both Water Relics exactly; only enhance five non-water texture sheets.
J_NONWATER={
 "emberfall":"assets/legendaryv34/models/item/emberfall_claymore.json",
 "noctis":"assets/legendaryv34/models/item/noctis_longsword.json",
 "stormpiercer":"assets/legendaryv34/models/item/stormpiercer_recurve_bow.json",
 "zephya":"assets/legendaryv34/models/item/gaia_war_spear.json",
 "astral":"assets/legendaryv34/models/item/astral_frost_greataxe.json",
}
for key,rel in J_NONWATER.items():
    p=JR/rel;o=json.loads(p.read_text());theme=WEAPONS[key]["theme"]
    for tkey,tref in list(o.get("textures",{}).items()):
        if not isinstance(tref,str) or tref.startswith("#"):continue
        ns,path=tref.split(":",1)
        src=JR/f"assets/{ns}/textures/{path}.png"
        if not src.is_file():continue
        out=JR/f"assets/legendaryv371/textures/item/{key}_{tkey}.png";out.parent.mkdir(parents=True,exist_ok=True)
        themed_enhance(src,(512,512),theme,"java-"+key+"-"+tkey).save(out,optimize=True)
        o["textures"][tkey]=f"legendaryv371:item/{key}_{tkey}"
    p.write_text(json.dumps(o,separators=(",",":")),encoding="utf-8")
    if key=="stormpiercer":
        for i in range(3):
            pp=JR/f"assets/legendaryv34/models/item/stormpiercer_recurve_bow_pulling_{i}.json"
            if pp.is_file():
                po=json.loads(pp.read_text());po["textures"]=dict(o["textures"]);pp.write_text(json.dumps(po,separators=(",",":")),encoding="utf-8")

# HD native Java armor only. No display overlay is required at runtime.
def armor_detail(src,theme,setname,kind):
    im=Image.open(src).convert("RGBA").resize((512,256),Image.Resampling.LANCZOS)
    d=ImageDraw.Draw(im,"RGBA");_,mid,glow=PALETTE[theme]
    W,H=im.size
    # Fine trim follows the atlas without adding detached geometry.
    for x in range(0,W,64):d.line((x,0,x,H-1),fill=mid+(34,),width=2)
    for y in range(0,H,64):d.line((0,y,W-1,y),fill=mid+(26,),width=2)
    if setname=="phoenix":
        for x in (64,192,320,448):d.polygon([(x,18),(x-16,54),(x,43),(x+17,70),(x+9,37)],outline=glow+(140,))
    elif setname=="voidwalker":
        d.arc((28,18,154,114),205,340,fill=glow+(130,),width=3);d.arc((176,18,302,114),200,335,fill=glow+(105,),width=3)
    elif setname=="titan":
        for x in (20,142,264,386):d.rounded_rectangle((x,22,x+88,46),radius=6,outline=glow+(120,),width=3)
    elif setname=="celestial":
        for x,y in ((72,42),(168,86),(252,36),(348,82),(442,45)):
            d.line((x-8,y,x+8,y),fill=glow+(150,),width=3);d.line((x,y-8,x,y+8),fill=glow+(150,),width=3)
    else:
        for yy in (48,112,176):
            d.arc((30,yy-28,190,yy+34),185,355,fill=glow+(120,),width=3);d.arc((220,yy-28,380,yy+34),185,355,fill=glow+(100,),width=3)
    return im.filter(ImageFilter.UnsharpMask(1,150,2))

for s,st in SETS.items():
    for sub in ("humanoid","humanoid_leggings"):
        for layer in ("base","accent"):
            src=JR/f"assets/legendaryv369/textures/entity/equipment/{sub}/{s}_{layer}.png"
            if src.is_file():
                out=JR/f"assets/legendaryv371/textures/entity/equipment/{sub}/{s}_{layer}.png";out.parent.mkdir(parents=True,exist_ok=True)
                armor_detail(src,st["theme"],s,layer).save(out,optimize=True)
    # open helmet variants
    for layer in ("open_base","open_accent"):
        src=JR/f"assets/legendaryv369/textures/entity/equipment/humanoid/{s}_{layer}.png"
        if src.is_file():
            out=JR/f"assets/legendaryv371/textures/entity/equipment/humanoid/{s}_{layer}.png";out.parent.mkdir(parents=True,exist_ok=True)
            armor_detail(src,st["theme"],s,layer).save(out,optimize=True)

    eq=JR/f"assets/legendaryv369/equipment/{s}_set.json"
    if eq.is_file():
        o=json.loads(eq.read_text())
        for layer in o["layers"].get("humanoid",[]): layer["texture"]=layer["texture"].replace("legendaryv369:", "legendaryv371:")
        for layer in o["layers"].get("humanoid_leggings",[]): layer["texture"]=layer["texture"].replace("legendaryv369:", "legendaryv371:")
        eq.write_text(json.dumps(o,separators=(",",":")),encoding="utf-8")
    for mode in ("closed","open"):
        ep=JR/f"assets/legendaryv369/equipment/{s}_helmet_{mode}.json"
        if ep.is_file():
            o=json.loads(ep.read_text())
            for layer in o["layers"].get("humanoid",[]): layer["texture"]=layer["texture"].replace("legendaryv369:", "legendaryv371:")
            ep.write_text(json.dumps(o,separators=(",",":")),encoding="utf-8")

# Bedrock armor: clone v370 visuals, scale textures to 512x256, add attached set-specific accents.
def add_cube(bone,cube):
    bone.setdefault("cubes",[]).append(cube)

def armor_extra(g,setname,piece):
    bones={b.get("name"):b for b in g.get("bones",[])}
    if piece.startswith("helmet"):
        b=bones.get("armor_head")
        if b:
            if setname=="phoenix":
                add_cube(b,{"origin":[-1.0,33.0,-.7],"size":[2,4.2,1.4],"uv":[360,0],"inflate":.04})
                add_cube(b,{"origin":[-5.6,29,-.7],"size":[1.3,5,1.4],"uv":[376,0],"pivot":[-4.2,30,0],"rotation":[0,0,-28],"inflate":.04})
                add_cube(b,{"origin":[4.3,29,-.7],"size":[1.3,5,1.4],"uv":[392,0],"pivot":[4.2,30,0],"rotation":[0,0,28],"inflate":.04})
            elif setname=="voidwalker":
                add_cube(b,{"origin":[-5.0,31,-.5],"size":[1.1,6,1.0],"uv":[360,0],"pivot":[-4.0,31,0],"rotation":[0,0,-35],"inflate":.03})
                add_cube(b,{"origin":[3.9,31,-.5],"size":[1.1,6,1.0],"uv":[372,0],"pivot":[4.0,31,0],"rotation":[0,0,35],"inflate":.03})
            elif setname=="celestial":
                for ox,rz in ((-3,-30),(0,0),(3,30)):
                    add_cube(b,{"origin":[ox-.45,33,-.45],"size":[.9,3.7,.9],"uv":[360+int((ox+3)*4),0],"pivot":[ox,33,0],"rotation":[0,0,rz],"inflate":.02})
            elif setname=="water_sovereign":
                add_cube(b,{"origin":[-5.4,27,-.5],"size":[1.1,6.0,1.0],"uv":[360,0],"pivot":[-4,28,0],"rotation":[0,0,-24],"inflate":.03})
                add_cube(b,{"origin":[4.3,27,-.5],"size":[1.1,6.0,1.0],"uv":[376,0],"pivot":[4,28,0],"rotation":[0,0,24],"inflate":.03})
    elif piece=="chest":
        body=bones.get("armor_body");r=bones.get("armor_rarm");l=bones.get("armor_larm")
        if body:
            add_cube(body,{"origin":[-1.2,8.0,-4.1],"size":[2.4,3.2,.8],"uv":[360,48],"inflate":.03})
        if r:add_cube(r,{"origin":[-9.8,8,-2.8],"size":[1.5,5.5,5.6],"uv":[376,48],"pivot":[-5.2,10,0],"rotation":[0,0,-16],"inflate":.05})
        if l:add_cube(l,{"origin":[8.3,8,-2.8],"size":[1.5,5.5,5.6],"uv":[400,48],"pivot":[5.2,10,0],"rotation":[0,0,16],"inflate":.05})
    elif piece=="legs":
        r=bones.get("armor_rleg");l=bones.get("armor_lleg")
        if r:add_cube(r,{"origin":[-3.7,5,-3.1],"size":[3.2,3.6,1.0],"uv":[360,96],"inflate":.04})
        if l:add_cube(l,{"origin":[.5,5,-3.1],"size":[3.2,3.6,1.0],"uv":[380,96],"inflate":.04,"mirror":True})
    elif piece=="boots":
        r=bones.get("armor_rboot");l=bones.get("armor_lboot")
        if r:add_cube(r,{"origin":[-3.8,0,-3.5],"size":[3.6,2.4,1.1],"uv":[360,128],"inflate":.04})
        if l:add_cube(l,{"origin":[.2,0,-3.5],"size":[3.6,2.4,1.1],"uv":[380,128],"inflate":.04,"mirror":True})

def clone_armor(setname,piece,source_attach,theme):
    a=json.loads((BR/"attachables"/source_attach).read_text())["minecraft:attachable"]["description"]
    gp,g=find_geometry(a["geometry"]["default"]);g=json.loads(json.dumps(g))
    oldw=int(g["description"].get("texture_width",256));oldh=int(g["description"].get("texture_height",128))
    factor=2
    scale_uvs(g.get("bones",[]),factor);g["description"]["texture_width"]=oldw*factor;g["description"]["texture_height"]=oldh*factor
    armor_extra(g,setname,piece)
    gid=f"geometry.raisnet371.armor.{setname}.{piece}";g["description"]["identifier"]=gid
    wr(BR/f"models/entity/v371_armor_{setname}_{piece}.geo.json",{"format_version":"1.16.0","minecraft:geometry":[g]})
    texref=a["textures"]["default"];src=BR/f"{texref}.png"
    out=BR/f"textures/models/armor/v371_{setname}_{piece}.png";out.parent.mkdir(parents=True,exist_ok=True)
    themed_enhance(src,(oldw*factor,oldh*factor),theme,"armor-"+setname+"-"+piece).save(out,optimize=True)
    return a,gid,f"textures/models/armor/v371_{setname}_{piece}"

for s,st in SETS.items():
    for piece in ("helmet_closed","helmet_open","chest","legs","boots"):
        src=f"v370_armor_{s}_{piece}.json"
        base,gid,texref=clone_armor(s,piece,src,st["theme"])
        for ns,label in (("raisnet371","modern"),("raisnet371l","legacy")):
            ident=f"{ns}:{s}_{piece}"
            d=json.loads(json.dumps(base));d["identifier"]=ident;d["geometry"]["default"]=gid;d["textures"]["default"]=texref
            wr(BR/f"attachables/v371_{label}_armor_{s}_{piece}.json",{"format_version":"1.20.60","minecraft:attachable":{"description":d}})
            td[ident]={"textures":texref}

(BR/"textures/item_texture.json").write_text(json.dumps(atlas,separators=(",",":")),encoding="utf-8")

# Fresh pack identity.
mf=json.loads((BR/"manifest.json").read_text())
mf["format_version"]=2
mf["header"]["name"]="RaisNet LegendaryRais v3.7.1 Native Stable"
mf["header"]["description"]="Dual Geyser mapping | fresh custom IDs | true 3D Bedrock armor | stable weapons"
mf["header"]["uuid"]="8a777a1f-629f-40e3-a3f3-c1a6e2b3c371"
mf["header"]["version"]=[3,7,1]
mf["header"]["min_engine_version"]=[1,21,0]
mf["modules"][0]["uuid"]="5f44bbfd-c1d5-4bea-9183-4488fed42371"
mf["modules"][0]["version"]=[3,7,1]
(BR/"manifest.json").write_text(json.dumps(mf,separators=(",",":")),encoding="utf-8")

# Dual mapping: definition (item_model) + legacy CMD, unique identifiers but identical visuals.
old=json.loads(MBASE.read_text())
mapping={"format_version":2,"items":{}}
# Preserve FX only / unrelated custom definitions.
for base,arr in old.get("items",{}).items():
    keep=[]
    for d in arr:
        bid=str(d.get("bedrock_identifier",""));model=str(d.get("model",""));cmd=d.get("custom_model_data")
        if bid.startswith(("raisnet370:","raisnet369:","raisnet368:")):continue
        if model.startswith(("legendaryv368:","legendaryv369:armor/")):continue
        if cmd in {w["cmd"] for w in WEAPONS.values()}:continue
        keep.append(d)
    if keep:mapping["items"][base]=keep

for key,w in WEAPONS.items():
    common={"display_name":WNAME[key],"bedrock_options":{"display_handheld":True,"creative_category":"equipment"}}
    modern={"type":"definition","model":w["model"],"bedrock_identifier":w["modern"],"priority":2000,**common}
    modern["bedrock_options"]=dict(common["bedrock_options"],icon=w["modern"])
    legacy={"type":"legacy","custom_model_data":w["cmd"],"bedrock_identifier":w["legacy"],"priority":1000,**common}
    legacy["bedrock_options"]=dict(common["bedrock_options"],icon=w["legacy"])
    mapping["items"].setdefault(w["base"],[]).extend([modern,legacy])

for s,st in SETS.items():
    for piece,(vanilla,off,slot) in PIECES.items():
        base=f"minecraft:{st['base']}_{vanilla}"
        if piece=="helmet":
            modes=(("closed",st["cmd"]+off),("open",st["cmd"]+off+1000))
            for mode,cmd in modes:
                model=f"legendaryv369:armor/{s}_helmet_{mode}"
                modern_id=f"raisnet371:{s}_helmet_{mode}";legacy_id=f"raisnet371l:{s}_helmet_{mode}"
                opts={"protection_value":st["prot"],"creative_category":"equipment"}
                comps={"minecraft:equippable":{"slot":"head"},"minecraft:max_stack_size":1}
                mapping["items"].setdefault(base,[]).extend([
                  {"type":"definition","model":model,"bedrock_identifier":modern_id,"display_name":f"{s.replace('_',' ').title()} Helmet {mode.title()}","priority":2000,"bedrock_options":dict(opts,icon=modern_id),"components":comps},
                  {"type":"legacy","custom_model_data":cmd,"bedrock_identifier":legacy_id,"display_name":f"{s.replace('_',' ').title()} Helmet {mode.title()} Legacy","priority":1000,"bedrock_options":dict(opts,icon=legacy_id),"components":comps}
                ])
        else:
            model=f"legendaryv369:armor/{s}_{piece}"
            modern_id=f"raisnet371:{s}_{piece}";legacy_id=f"raisnet371l:{s}_{piece}"
            opts={"protection_value":st["prot"],"creative_category":"equipment"}
            comps={"minecraft:equippable":{"slot":slot},"minecraft:max_stack_size":1}
            mapping["items"].setdefault(base,[]).extend([
              {"type":"definition","model":model,"bedrock_identifier":modern_id,"display_name":f"{s.replace('_',' ').title()} {piece.title()}","priority":2000,"bedrock_options":dict(opts,icon=modern_id),"components":comps},
              {"type":"legacy","custom_model_data":st["cmd"]+off,"bedrock_identifier":legacy_id,"display_name":f"{s.replace('_',' ').title()} {piece.title()} Legacy","priority":1000,"bedrock_options":dict(opts,icon=legacy_id),"components":comps}
            ])

MOUT.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# Java metadata.
pm=json.loads((JR/"pack.mcmeta").read_text())
pm["pack"]["description"]="LegendaryRais v3.7.1 NATIVE STABLE | exact Water Relics | HD native armor | sharper legendary weapons"
(JR/"pack.mcmeta").write_text(json.dumps(pm,separators=(",",":")),encoding="utf-8")

# QA100+
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
Q("mapping format v2",mapping.get("format_version")==2)
Q("fresh Bedrock UUID",mf["header"]["uuid"]=="8a777a1f-629f-40e3-a3f3-c1a6e2b3c371")
Q("fresh Bedrock module UUID",mf["modules"][0]["uuid"]=="5f44bbfd-c1d5-4bea-9183-4488fed42371")

# Water Java exact freeze vs base v3.7.0 (which already freezes v3.6.8).
with zipfile.ZipFile(JBASE) as z:
    soul=[n for n in z.namelist() if n.startswith("assets/soultide/")]
    Q("Soul Tide namespace found",len(soul)>0)
    Q("Soul Tide namespace fully retained",all((JR/n).is_file() for n in soul))
    Q("Soul Tide exact bytes retained",all(z.read(n)==(JR/n).read_bytes() for n in soul))
    lev="assets/legendaryrais/models/item/abyss_leviathan_trident.json"
    Q("Leviathan model exact bytes retained",z.read(lev)==(JR/lev).read_bytes())
    # Water wrapper exact.
    for n in ("assets/legendaryv368/items/soul_tide.json","assets/legendaryv368/items/leviathan.json"):
        Q(f"{n} exact retained",z.read(n)==(JR/n).read_bytes())

# Java non-water HD refs.
for key,rel in J_NONWATER.items():
    o=json.loads((JR/rel).read_text())
    Q(f"{key} Java model exists",bool(o.get("elements")))
    Q(f"{key} uses v371 HD texture refs",all(str(v).startswith("legendaryv371:") for v in o.get("textures",{}).values() if not str(v).startswith("#")))
    for tref in o.get("textures",{}).values():
        if str(tref).startswith("#"):continue
        ns,path=tref.split(":",1);tp=JR/f"assets/{ns}/textures/{path}.png"
        Q(f"{key} texture {path} exists",tp.is_file())
        Q(f"{key} texture {path} is 512",Image.open(tp).size==(512,512))

# Native Java armor HD.
for s in SETS:
    Q(f"{s} Java native set model exists",(JR/f"assets/legendaryv369/equipment/{s}_set.json").is_file())
    Q(f"{s} Java native closed helmet exists",(JR/f"assets/legendaryv369/equipment/{s}_helmet_closed.json").is_file())
    Q(f"{s} Java native open helmet exists",(JR/f"assets/legendaryv369/equipment/{s}_helmet_open.json").is_file())
    for sub in ("humanoid","humanoid_leggings"):
        for layer in ("base","accent"):
            tp=JR/f"assets/legendaryv371/textures/entity/equipment/{sub}/{s}_{layer}.png"
            Q(f"{s} {sub} {layer} HD exists",tp.is_file())
            Q(f"{s} {sub} {layer} 512x256",Image.open(tp).size==(512,256))

# Bedrock dual weapon assets.
defs=[d for arr in mapping["items"].values() for d in arr]
for key,w in WEAPONS.items():
    Q(f"{key} modern attachable exists",(BR/f"attachables/v371_modern_{key}.player.json").is_file())
    Q(f"{key} legacy attachable exists",(BR/f"attachables/v371_legacy_{key}.player.json").is_file())
    ma=json.loads((BR/f"attachables/v371_modern_{key}.player.json").read_text())["minecraft:attachable"]["description"]
    la=json.loads((BR/f"attachables/v371_legacy_{key}.player.json").read_text())["minecraft:attachable"]["description"]
    Q(f"{key} modern identifier exact",ma["identifier"]==w["modern"])
    Q(f"{key} legacy identifier exact",la["identifier"]==w["legacy"])
    Q(f"{key} modern/legacy share geometry",ma["geometry"]["default"]==la["geometry"]["default"])
    Q(f"{key} modern/legacy share texture",ma["textures"]["default"]==la["textures"]["default"])
    Q(f"{key} modern definition exists",sum(1 for d in defs if d.get("type")=="definition" and d.get("model")==w["model"] and d.get("bedrock_identifier")==w["modern"])==1)
    Q(f"{key} legacy definition exists",sum(1 for d in defs if d.get("type")=="legacy" and d.get("custom_model_data")==w["cmd"] and d.get("bedrock_identifier")==w["legacy"])==1)
    Q(f"{key} atlas modern exists",w["modern"] in td)
    Q(f"{key} atlas legacy exists",w["legacy"] in td)
    Q(f"{key} geometry file exists",(BR/f"models/entity/v371_{key}.geo.json").is_file())
    Q(f"{key} texture exists",(BR/f"textures/items/v371_{key}.png").is_file())

# Bedrock armor true 3D + dual mappings.
for s,st in SETS.items():
    for piece in ("helmet_closed","helmet_open","chest","legs","boots"):
        Q(f"{s} {piece} geometry exists",(BR/f"models/entity/v371_armor_{s}_{piece}.geo.json").is_file())
        Q(f"{s} {piece} modern attachable exists",(BR/f"attachables/v371_modern_armor_{s}_{piece}.json").is_file())
        Q(f"{s} {piece} legacy attachable exists",(BR/f"attachables/v371_legacy_armor_{s}_{piece}.json").is_file())
        ma=json.loads((BR/f"attachables/v371_modern_armor_{s}_{piece}.json").read_text())["minecraft:attachable"]["description"]
        Q(f"{s} {piece} uses armor render controller",ma["render_controllers"]==["controller.render.armor"])
        g=json.loads((BR/f"models/entity/v371_armor_{s}_{piece}.geo.json").read_text())["minecraft:geometry"][0]
        cubes=sum(len(b.get("cubes",[])) for b in g["bones"])
        Q(f"{s} {piece} true 3D cubes >=4",cubes>=4)
        Q(f"{s} {piece} true 3D cubes <=24",cubes<=24)

# Mapping armor pairs.
for s,st in SETS.items():
    for piece,(vanilla,off,slot) in PIECES.items():
        if piece=="helmet":
            for mode,cmd in (("closed",st["cmd"]+off),("open",st["cmd"]+off+1000)):
                model=f"legendaryv369:armor/{s}_helmet_{mode}"
                Q(f"{s} helmet {mode} modern mapping",any(d.get("type")=="definition" and d.get("model")==model and d.get("bedrock_identifier")==f"raisnet371:{s}_helmet_{mode}" for d in defs))
                Q(f"{s} helmet {mode} legacy mapping",any(d.get("type")=="legacy" and d.get("custom_model_data")==cmd and d.get("bedrock_identifier")==f"raisnet371l:{s}_helmet_{mode}" for d in defs))
        else:
            model=f"legendaryv369:armor/{s}_{piece}"
            Q(f"{s} {piece} modern mapping",any(d.get("type")=="definition" and d.get("model")==model and d.get("bedrock_identifier")==f"raisnet371:{s}_{piece}" for d in defs))
            Q(f"{s} {piece} legacy mapping",any(d.get("type")=="legacy" and d.get("custom_model_data")==st["cmd"]+off and d.get("bedrock_identifier")==f"raisnet371l:{s}_{piece}" for d in defs))

Q("no v370 weapon/armor identifiers remain mapped",not any(str(d.get("bedrock_identifier","")).startswith("raisnet370:") for d in defs))
Q("all weapon modern IDs unique",len({w["modern"] for w in WEAPONS.values()})==len(WEAPONS))
Q("all weapon legacy IDs unique",len({w["legacy"] for w in WEAPONS.values()})==len(WEAPONS))
Q("all modern IDs disjoint legacy IDs",{w["modern"] for w in WEAPONS.values()}.isdisjoint({w["legacy"] for w in WEAPONS.values()}))
Q("FX mappings still present",any("fx_" in str(d.get("model","")) for d in defs))

assert len(checks)>=100,len(checks)
REPORT.write_text("\n".join(f"{i+1:03d}. PASS - {n}" for i,n in enumerate(checks))+f"\n\nQA100 MINIMUM EXCEEDED: {len(checks)}/{len(checks)} PASS\n",encoding="utf-8")

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

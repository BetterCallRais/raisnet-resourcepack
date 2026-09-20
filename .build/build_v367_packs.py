from pathlib import Path
import json, math, random, shutil, zipfile, hashlib
from PIL import Image, ImageDraw, ImageFilter

JBASE=Path("LegendaryRais-Java-26.1.2-v3.6.6-MYTHIC-ART-QA30.zip")
BBASE=Path("LegendaryRais-Bedrock-v3.6.6-MYTHIC-ART-QA30.mcpack")
MBASE=Path("LegendaryRais-Geyser-v3.6.6-mappings.json")
JOUT=Path("LegendaryRais-Java-26.1.2-v3.6.7-CROSSPLAY-WATERFIX-QA50.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.6.7-CROSSPLAY-WATERFIX-QA50.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.6.7-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.6.7-CROSSPLAY-WATERFIX-QA50.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.6.7-CROSSPLAY-WATERFIX-QA50.sha1")
REPORT=Path("LegendaryRais-v3.6.7-QA50.txt")
ROOT=Path(".build/generated-v367");JR=ROOT/"java";BR=ROOT/"bedrock"

shutil.rmtree(ROOT,ignore_errors=True);JR.mkdir(parents=True);BR.mkdir(parents=True)
with zipfile.ZipFile(JBASE) as z:z.extractall(JR)
with zipfile.ZipFile(BBASE) as z:z.extractall(BR)

# Java item_model path -> metadata
WEAPONS={
 "soul_tide":{"model":"soultide:soul_tide_sovereign_blade","ns":"soultide","path":"soul_tide_sovereign_blade","base":"minecraft:netherite_sword","bid":"raisnet:soul_tide_v367","kind":"water","colors":((7,37,55),(31,132,163),(127,244,255))},
 "leviathan":{"model":"legendaryrais:abyss_leviathan_trident","ns":"legendaryrais","path":"abyss_leviathan_trident","base":"minecraft:trident","bid":"raisnet:leviathan_v367","kind":"abyss","colors":((5,26,40),(24,91,128),(57,225,255))},
 "emberfall":{"model":"legendaryv34:emberfall_claymore","ns":"legendaryv34","path":"emberfall_claymore","base":"minecraft:netherite_sword","bid":"raisnet:emberfall_v367","kind":"fire","colors":((44,10,5),(172,47,12),(255,151,35))},
 "noctis":{"model":"legendaryv34:noctis_longsword","ns":"legendaryv34","path":"noctis_longsword","base":"minecraft:netherite_sword","bid":"raisnet:noctis_v367","kind":"void","colors":((10,7,22),(72,25,116),(215,84,255))},
 "stormpiercer":{"model":"legendaryv34:stormpiercer_recurve_bow","ns":"legendaryv34","path":"stormpiercer_recurve_bow","base":"minecraft:bow","bid":"raisnet:stormpiercer_v367","kind":"electro","colors":((7,28,44),(30,127,168),(83,240,255))},
 "zephya":{"model":"legendaryv34:gaia_war_spear","ns":"legendaryv34","path":"gaia_war_spear","base":"minecraft:netherite_shovel","bid":"raisnet:zephya_v367","kind":"wind","colors":((17,42,43),(59,157,140),(199,255,230))},
 "astral":{"model":"legendaryv34:astral_frost_greataxe","ns":"legendaryv34","path":"astral_frost_greataxe","base":"minecraft:netherite_axe","bid":"raisnet:astral_frost_v367","kind":"ice","colors":((12,39,67),(65,166,216),(222,253,255))}
}
SETS=("phoenix","voidwalker","titan","celestial","water_sovereign")

def wr(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def faces(k):return {f:{"texture":"#"+k} for f in ("north","south","east","west","up","down")}
def E(fr,to,key="metal",rot=None):
    e={"from":[round(v,3) for v in fr],"to":[round(v,3) for v in to],"faces":faces(key)}
    if rot:
        origin,axis,ang=rot
        e["rotation"]={"origin":[round(v,3) for v in origin],"axis":axis,"angle":ang,"rescale":True}
    return e

def material(size,base,mid,glow,kind,seed):
    rnd=random.Random(seed);im=Image.new("RGBA",(size,size),base+(255,));px=im.load()
    for y in range(size):
        for x in range(size):
            nx=x/(size-1);ny=y/(size-1)
            spec=max(0,1-abs(nx-.37)/.22)*.16
            bands=.05*math.sin(x*.22+y*.08)+.025*math.sin(y*.43)
            t=max(.04,min(.64,.12+.24*nx+.16*(1-ny)+spec+bands+rnd.uniform(-.012,.012)))
            c=tuple(max(0,min(255,int(base[i]*(1-t)+mid[i]*t))) for i in range(3))
            px[x,y]=c+(255,)
    d=ImageDraw.Draw(im,"RGBA");w=max(1,size//128)
    d.rectangle((2*w,2*w,size-2*w-1,size-2*w-1),outline=mid+(80,),width=w)
    if kind=="water":
        for yy in (.24,.48,.72):
            d.arc((size*.06,size*(yy-.13),size*.94,size*(yy+.15)),185,350,fill=glow+(130,),width=2*w)
        d.polygon([(size*.5,size*.08),(size*.62,size*.30),(size*.50,size*.47),(size*.38,size*.30)],outline=glow+(145,))
    elif kind=="abyss":
        d.arc((size*.08,size*.11,size*.92,size*.91),195,345,fill=glow+(140,),width=2*w)
        for x,y in ((.19,.27),(.34,.72),(.67,.31),(.83,.72)):d.ellipse((size*x-2*w,size*y-2*w,size*x+2*w,size*y+2*w),fill=glow+(190,))
        d.line((size*.5,size*.09,size*.5,size*.89),fill=mid+(90,),width=w)
    elif kind=="fire":
        for cx in (.18,.39,.61,.82):d.line((size*cx,size*.91,size*(cx-.05),size*.66,size*(cx+.02),size*.48,size*(cx-.02),size*.27),fill=glow+(150,),width=2*w)
    elif kind=="void":
        d.arc((size*.08,size*.10,size*.92,size*.90),204,340,fill=glow+(145,),width=2*w)
        for x,y in ((.16,.26),(.34,.74),(.68,.30),(.84,.72)):d.ellipse((size*x-2*w,size*y-2*w,size*x+2*w,size*y+2*w),fill=glow+(195,))
    elif kind=="electro":
        for off in (0,.14,-.12):d.line((size*(.67+off),size*.04,size*(.44+off),size*.36,size*(.56+off),size*.40,size*(.31+off),size*.94),fill=glow+(165,),width=2*w)
    elif kind=="wind":
        for yy in (.22,.46,.70):d.arc((size*.05,size*(yy-.14),size*.95,size*(yy+.16)),192,346,fill=glow+(120,),width=2*w)
    elif kind=="ice":
        for a in range(0,360,45):
            x=size*.5+math.cos(math.radians(a))*size*.37;y=size*.5+math.sin(math.radians(a))*size*.37
            d.line((size*.5,size*.5,x,y),fill=glow+(145,),width=2*w)
    return im.filter(ImageFilter.UnsharpMask(radius=max(1,size//128),percent=190,threshold=2))

# ---------- Java water weapon rebuild ----------
SOUL_TRANS={
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,3.25,0],"scale":[.60,.60,.60]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,3.25,0],"scale":[.60,.60,.60]},
 "firstperson_righthand":{"rotation":[0,-90,24],"translation":[1.0,3.10,.22],"scale":[.68,.68,.68]},
 "firstperson_lefthand":{"rotation":[0,90,-24],"translation":[1.0,3.10,.22],"scale":[.68,.68,.68]},
 "gui":{"rotation":[25,-35,0],"scale":[.54,.54,.54]},"ground":{"translation":[0,2,0],"scale":[.38,.38,.38]},"fixed":{"rotation":[0,180,0],"scale":[.58,.58,.58]}
}
LEVI_TRANS={
 "thirdperson_righthand":{"rotation":[0,-90,58],"translation":[0,2.25,0],"scale":[.49,.49,.49]},
 "thirdperson_lefthand":{"rotation":[0,90,-58],"translation":[0,2.25,0],"scale":[.49,.49,.49]},
 "firstperson_righthand":{"rotation":[0,-90,28],"translation":[.95,2.10,.24],"scale":[.55,.55,.55]},
 "firstperson_lefthand":{"rotation":[0,90,-28],"translation":[.95,2.10,.24],"scale":[.55,.55,.55]},
 "gui":{"rotation":[25,-35,0],"scale":[.50,.50,.50]},"ground":{"translation":[0,2,0],"scale":[.34,.34,.34]},"fixed":{"rotation":[0,180,0],"scale":[.52,.52,.52]}
}

def soul_geom():
    e=[E((7.25,-1.5,7.25),(8.75,6.8,8.75),"grip"),E((6.8,-1.7,7.08),(9.2,-.2,8.92),"accent")]
    for y in (1.0,3.2,5.4):e.append(E((6.95,y,7.10),(9.05,y+.28,8.90),"accent"))
    e += [
      E((3.5,6.6,7.45),(7.4,7.7,8.55),"accent",([7.2,7.1,8],"z",-22.5)),
      E((8.6,6.6,7.45),(12.5,7.7,8.55),"accent",([8.8,7.1,8],"z",22.5)),
      E((5.1,7.0,7.58),(6.9,9.2,8.42),"metal",([6.8,7.7,8],"z",-22.5)),
      E((9.1,7.0,7.58),(10.9,9.2,8.42),"metal",([9.2,7.7,8],"z",22.5))
    ]
    for y,w in [(7.8,4.1),(12.1,3.9),(16.4,3.55),(20.7,3.15),(25.0,2.65)]:
        e += [E((8-w/2,y,7.32),(8+w/2,y+4.15,8.68),"metal"),E((7.80,y+.1,7.05),(8.20,y+4.0,8.95),"accent")]
    e += [E((7.1,29.0,7.50),(8.9,31.4,8.50),"metal"),E((7.55,30.7,7.35),(8.45,32.0,8.65),"accent")]
    return e

def levi_geom():
    e=[E((7.45,-4.5,7.35),(8.55,20.8,8.65),"grip")]
    for y in (-2,2.5,7,11.5,16):e.append(E((7.05,y,7.18),(8.95,y+.30,8.82),"accent"))
    e += [
      E((6.75,19.8,7.05),(9.25,23.0,8.95),"accent"),
      E((7.20,22.2,7.35),(8.80,31.8,8.65),"metal"),
      E((3.8,22.0,7.45),(6.9,29.8,8.55),"metal",([6.7,24.6,8],"z",-22.5)),
      E((9.1,22.0,7.45),(12.2,29.8,8.55),"metal",([9.3,24.6,8],"z",22.5)),
      E((2.8,24.0,7.55),(5.0,30.8,8.45),"accent",([4.7,26.1,8],"z",-22.5)),
      E((11.0,24.0,7.55),(13.2,30.8,8.45),"accent",([11.3,26.1,8],"z",22.5)),
      E((6.25,20.4,7.50),(7.2,24.7,8.50),"accent",([7.0,22.0,8],"z",-22.5)),
      E((8.8,20.4,7.50),(9.75,24.7,8.50),"accent",([9.0,22.0,8],"z",22.5))
    ]
    return e

for key,geom,trans in (("soul_tide",soul_geom(),SOUL_TRANS),("leviathan",levi_geom(),LEVI_TRANS)):
    v=WEAPONS[key];base,mid,glow=v["colors"]
    for texkey,(a,b,k) in {"metal":(base,mid,v["kind"]),"grip":((17,19,23),(60,83,91),"water"),"accent":(mid,glow,v["kind"])}.items():
        im=material(256,a,b,glow,k,"v367-"+key+"-"+texkey)
        p=JR/f"assets/{v['ns']}/textures/item/v367/{v['path']}_{texkey}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
    obj={"textures":{"metal":f"{v['ns']}:item/v367/{v['path']}_metal","grip":f"{v['ns']}:item/v367/{v['path']}_grip","accent":f"{v['ns']}:item/v367/{v['path']}_accent"},"elements":geom,"display":trans,"gui_light":"front"}
    wr(JR/f"assets/{v['ns']}/models/item/{v['path']}.json",obj)
    wr(JR/f"assets/{v['ns']}/items/{v['path']}.json",{"model":{"type":"minecraft:model","model":f"{v['ns']}:item/{v['path']}"}})

# Old Soul item_model alias points to current sovereign blade.
wr(JR/"assets/soultide/items/soul_tide_katana.json",{"model":{"type":"minecraft:model","model":"soultide:item/soul_tide_sovereign_blade"}})

# ---------- Improve five non-water models/textures without changing IDs ----------
for key in ("emberfall","noctis","stormpiercer","zephya","astral"):
    v=WEAPONS[key];p=JR/f"assets/{v['ns']}/models/item/{v['path']}.json";obj=json.loads(p.read_text())
    # Fresh material pass.
    base,mid,glow=v["colors"]
    for texkey,(a,b,k) in {"metal":(base,mid,v["kind"]),"grip":((20,15,13),(92,62,40),"water"),"accent":(mid,glow,v["kind"])}.items():
        im=material(256,a,b,glow,k,"v367-"+key+"-"+texkey)
        tp=JR/f"assets/{v['ns']}/textures/item/v367/{v['path']}_{texkey}.png";tp.parent.mkdir(parents=True,exist_ok=True);im.save(tp,optimize=True)
        obj["textures"][texkey]=f"{v['ns']}:item/v367/{v['path']}_{texkey}"
    # Small identity detail upgrade while remaining under 30 elements.
    extra=[]
    if key=="emberfall": extra=[E((6.2,8.0,6.95),(6.75,11.0,9.05),"accent"),E((9.25,8.0,6.95),(9.8,11.0,9.05),"accent")]
    elif key=="noctis": extra=[E((6.65,8.0,7.15),(7.15,10.8,8.85),"accent"),E((8.85,8.0,7.15),(9.35,10.8,8.85),"accent")]
    elif key=="stormpiercer": extra=[E((6.8,6.6,6.95),(7.3,9.5,9.05),"accent"),E((8.7,6.6,6.95),(9.2,9.5,9.05),"accent")]
    elif key=="zephya": extra=[E((6.45,22.5,7.0),(7.0,25.8,9.0),"accent"),E((9.0,22.5,7.0),(9.55,25.8,9.0),"accent")]
    else: extra=[E((5.0,21.5,7.0),(5.55,24.8,9.0),"accent"),E((10.45,21.5,7.0),(11.0,24.8,9.0),"accent")]
    if len(obj.get("elements",[]))+len(extra)<=30: obj["elements"].extend(extra)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

# Storm pull models must inherit refreshed base art/geometry.
storm=JR/"assets/legendaryv34/models/item/stormpiercer_recurve_bow.json"
base=json.loads(storm.read_text())
for idx,delta in enumerate((0.0,1.0,1.9)):
    d=json.loads(json.dumps(base))
    if delta:
        for e in d["elements"]:
            if e["from"][0] < 6.0:e["from"][0]+=delta;e["to"][0]+=delta
            elif e["to"][0] > 10.0:e["from"][0]-=delta;e["to"][0]-=delta
    wr(JR/f"assets/legendaryv34/models/item/stormpiercer_recurve_bow_pulling_{idx}.json",d)

# ---------- Bedrock seven-weapon rebuild with fresh v367 identifiers ----------
def C(origin,size,uv=(0,0),pivot=None,rotation=None):
    c={"origin":[round(v,3) for v in origin],"size":[round(v,3) for v in size],"uv":list(uv)}
    if pivot is not None:c["pivot"]=[round(v,3) for v in pivot]
    if rotation is not None:c["rotation"]=[round(v,3) for v in rotation]
    return c

def soul_bed():
    c=[C((-.7,-8,-.58),(1.4,8,1.16),(0,96)),C((-4.0,0,-.52),(8,1.1,1.04),(64,96))]
    for y,w in [(1,4.1),(5.4,3.9),(9.8,3.55),(14.2,3.15),(18.6,2.65)]:c.append(C((-w/2,y,-.5),(w,4.2,1),(0,0)))
    c += [C((-1.0,22.7,-.40),(2,2.7,.8),(64,0)),C((-2.5,.4,-.42),(2.2,2.3,.84),(82,96),(-.8,1.0,0),(0,0,-22.5)),C((.3,.4,-.42),(2.2,2.3,.84),(90,96),(.8,1.0,0),(0,0,22.5))]
    return c

def levi_bed():
    c=[C((-.48,-12,-.48),(.96,31,.96),(0,96))]
    for y in (-9,-4,1,6,11,16):c.append(C((-.78,y,-.56),(1.56,.30,1.12),(64,96)))
    c += [
      C((-.90,18.7,-.62),(1.8,4.2,1.24),(80,96)),
      C((-.55,22.0,-.45),(1.1,8.7,.9),(0,0)),
      C((-2.9,21.5,-.40),(1.4,8.0,.8),(32,0),(-1.0,23.8,0),(0,0,-22.5)),
      C((1.5,21.5,-.40),(1.4,8.0,.8),(48,0),(1.0,23.8,0),(0,0,22.5)),
      C((-4.0,23.7,-.34),(1.5,6.0,.68),(64,0),(-2.0,25.0,0),(0,0,-22.5)),
      C((2.5,23.7,-.34),(1.5,6.0,.68),(76,0),(2.0,25.0,0),(0,0,22.5))
    ]
    return c

# Existing five geometry from v366, with modest extra accent.
BED_GEOM={"soul_tide":soul_bed(),"leviathan":levi_bed()}
for key in ("emberfall","noctis","stormpiercer","zephya","astral"):
    v=WEAPONS[key]
    old=BR/f"models/entity/{v['path']}.geo.json";g=json.loads(old.read_text())["minecraft:geometry"][0]["bones"][0]["cubes"]
    cubes=json.loads(json.dumps(g))
    if key=="emberfall":cubes += [C((-2.8,.8,-.72),(.6,3,1.44),(110,96)),C((2.2,.8,-.72),(.6,3,1.44),(116,96))]
    elif key=="noctis":cubes += [C((-1.8,.6,-.65),(.5,2.8,1.3),(110,96)),C((1.3,.6,-.65),(.5,2.8,1.3),(116,96))]
    elif key=="stormpiercer":cubes += [C((-.25,-1.1,-.85),(.5,2.2,1.7),(110,96))]
    elif key=="zephya":cubes += [C((-1.7,18.2,-.52),(.5,3.1,1.04),(110,96)),C((1.2,18.2,-.52),(.5,3.1,1.04),(116,96))]
    else:cubes += [C((-2.2,16.8,-.74),(.5,3.0,1.48),(110,96)),C((1.7,16.8,-.74),(.5,3.0,1.48),(116,96))]
    BED_GEOM[key]=cubes[:30]

SCALE={
 "soul_tide":(.72,.80,[0,0,0]),
 "leviathan":(.61,.68,[0,0,-4]),
 "emberfall":(.70,.78,[0,0,0]),
 "noctis":(.74,.82,[0,0,0]),
 "stormpiercer":(.69,.75,[0,-6,0]),
 "zephya":(.61,.68,[0,0,-5]),
 "astral":(.65,.71,[0,0,-6])
}
animations={"format_version":"1.8.0","animations":{}}
atlas_path=BR/"textures/item_texture.json";atlas=json.loads(atlas_path.read_text());td=atlas.setdefault("texture_data",{})

for key,v in WEAPONS.items():
    bid_key=v["bid"].split(":",1)[1]
    base,mid,glow=v["colors"]
    im=material(128,base,mid,glow,v["kind"],"bed-v367-"+key)
    texpath=BR/f"textures/items/{bid_key}.png";texpath.parent.mkdir(parents=True,exist_ok=True);im.save(texpath,optimize=True)
    td[v["bid"]]={"textures":f"textures/items/{bid_key}"}

    gid=f"geometry.raisnet.{bid_key}"
    wr(BR/f"models/entity/{bid_key}.geo.json",{"format_version":"1.16.0","minecraft:geometry":[{
      "description":{"identifier":gid,"texture_width":128,"texture_height":128,"visible_bounds_width":7,"visible_bounds_height":8,"visible_bounds_offset":[0,8,0]},
      "bones":[{"name":"bb_main","pivot":[0,8,0],"binding":"q.item_slot_to_bone_name(context.item_slot)","cubes":BED_GEOM[key]}]
    }]})

    third,first,rot=SCALE[key]
    third_name=f"animation.raisnet.{bid_key}.third"
    first_name=f"animation.raisnet.{bid_key}.first"
    animations["animations"][third_name]={"loop":True,"bones":{"bb_main":{"position":[0,-24,0],"rotation":[0,0,0],"scale":[third,third,third]}}}
    animations["animations"][first_name]={"loop":True,"bones":{"bb_main":{"position":[2.0,-26.0,4.0],"rotation":rot,"scale":[first,first,first]}}}
    wr(BR/f"attachables/{bid_key}.player.json",{"format_version":"1.20.30","minecraft:attachable":{"description":{
      "identifier":v["bid"],
      "item":{v["bid"]:"query.is_owner_identifier_any('minecraft:player')"},
      "materials":{"default":"entity_alphatest","enchanted":"entity_alphatest_glint"},
      "textures":{"default":f"textures/items/{bid_key}","enchanted":"textures/misc/enchanted_item_glint"},
      "geometry":{"default":gid},
      "animations":{"hold_first_person":first_name,"hold_third_person":third_name},
      "scripts":{"animate":[{"hold_first_person":"context.is_first_person == 1.0"},{"hold_third_person":"context.is_first_person == 0.0"}]},
      "render_controllers":["controller.render.item_default"]
    }}})

atlas_path.write_text(json.dumps(atlas,separators=(",",":")),encoding="utf-8")
wr(BR/"animations/legendary_weapons_v367.animation.json",animations)

# ---------- Modern Geyser definitions for all 7 ----------
mapping=json.loads(MBASE.read_text())
# Remove old/current definitions for our seven models + old water legacy entries.
for base,arr in list(mapping["items"].items()):
    cleaned=[]
    for d in arr:
        if d.get("model") in {v["model"] for v in WEAPONS.values()}:continue
        if d.get("bedrock_identifier") in {"raisnet:soul_tide_katana","raisnet:abyss_leviathan_trident"}:continue
        if d.get("type")=="legacy" and d.get("custom_model_data") in (910041,910042):continue
        cleaned.append(d)
    mapping["items"][base]=cleaned

for key,v in WEAPONS.items():
    d={
      "type":"definition","model":v["model"],"bedrock_identifier":v["bid"],
      "display_name":{
        "soul_tide":"Soul Tide Sovereign Blade","leviathan":"Abyss Leviathan Trident",
        "emberfall":"Emberfall Claymore","noctis":"Noctis Longsword","stormpiercer":"Stormpiercer Sovereign Arc Bow",
        "zephya":"Zephya Sovereign Wind Spear","astral":"Astral Frost Glacial Greataxe"
      }[key],
      "bedrock_options":{"icon":v["bid"],"display_handheld":True,"creative_category":"equipment"}
    }
    # Preserve inherited base-item use behavior by not replacing components.
    mapping["items"].setdefault(v["base"],[]).append(d)

MOUT.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# ---------- fresh metadata ----------
jm=JR/"pack.mcmeta";meta=json.loads(jm.read_text());meta["pack"]["description"]="LegendaryRais v3.6.7 CROSSPLAY WATERFIX QA50 | rebuilt all 7 legendary weapons";jm.write_text(json.dumps(meta,separators=(",",":")),encoding="utf-8")
mf=BR/"manifest.json";bm=json.loads(mf.read_text());bm["header"]["name"]="RaisNet LegendaryRais v3.6.7 Crossplay Waterfix QA50";bm["header"]["description"]="Fresh identifiers + rebuilt Soul Tide/Leviathan + upgraded seven-weapon rigs";bm["header"]["uuid"]="bd2fdd74-b655-4b71-9a62-ec43ff9bc7f0";bm["header"]["version"]=[3,6,7];bm["modules"][0]["uuid"]="96a5fc31-8fbf-4f0c-a708-ad81e5dcfe60";bm["modules"][0]["version"]=[3,6,7];mf.write_text(json.dumps(bm,separators=(",",":")),encoding="utf-8")

# ---------- QA50 ----------
checks=[]
def Q(name,cond):
    if not cond:raise AssertionError(name)
    checks.append(name);print(f"CHECK {len(checks):02d} PASS - {name}")

# universal
for root in (JR,BR):
    for p in root.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
Q("all Java and Bedrock JSON parses",True)
for root in (JR,BR):
    for p in root.rglob("*.png"):
        with Image.open(p) as im:im.verify()
Q("all Java and Bedrock PNG verifies",True)
Q("Java pack metadata exists",(JR/"pack.mcmeta").is_file())
Q("Bedrock manifest exists",(BR/"manifest.json").is_file())
Q("Geyser mapping root valid",isinstance(mapping.get("items"),dict))

# Java water
Q("Soul Tide item definition exists",(JR/"assets/soultide/items/soul_tide_sovereign_blade.json").is_file())
Q("Soul Tide Java model exists",(JR/"assets/soultide/models/item/soul_tide_sovereign_blade.json").is_file())
Q("Leviathan item definition exists",(JR/"assets/legendaryrais/items/abyss_leviathan_trident.json").is_file())
Q("Leviathan Java model exists",(JR/"assets/legendaryrais/models/item/abyss_leviathan_trident.json").is_file())
Q("old Soul item_model aliases current model",json.loads((JR/"assets/soultide/items/soul_tide_katana.json").read_text())["model"]["model"]=="soultide:item/soul_tide_sovereign_blade")

# all Java models
for key,v in WEAPONS.items():
    mp=JR/f"assets/{v['ns']}/models/item/{v['path']}.json";o=json.loads(mp.read_text())
    Q(f"{key} Java geometry has 10..30 elements",10<=len(o.get("elements",[]))<=30)
# now checks count 17
# bounds and pivots grouped
ok=True
for key,v in WEAPONS.items():
    o=json.loads((JR/f"assets/{v['ns']}/models/item/{v['path']}.json").read_text())
    for e in o["elements"]:ok &= all(-16<=float(x)<=32 for x in e["from"]+e["to"])
Q("all seven Java geometries stay within -16..32",ok)
ok=True
for key,v in WEAPONS.items():
    o=json.loads((JR/f"assets/{v['ns']}/models/item/{v['path']}.json").read_text());zs=[z for e in o["elements"] for z in (e["from"][2],e["to"][2])];ok &= 7<=sum(zs)/len(zs)<=9
Q("all seven Java models centered around Z=8",ok)
ok=True
for key,v in WEAPONS.items():
    o=json.loads((JR/f"assets/{v['ns']}/models/item/{v['path']}.json").read_text());g=[e for e in o["elements"] if any(f.get("texture")=="#grip" for f in e["faces"].values())];ok &= bool(g) and any(e["from"][0]<=8<=e["to"][0] and e["from"][1]<=4<=e["to"][1] for e in g)
Q("all seven Java grip anchors cross x8/y4",ok)
ok=True
for key,v in WEAPONS.items():
    o=json.loads((JR/f"assets/{v['ns']}/models/item/{v['path']}.json").read_text());t=o["display"]["thirdperson_righthand"]["translation"];ok &= abs(t[0])<=.1 and abs(t[2])<=.3
Q("all seven Java third-person side offsets constrained",ok)
ok=True
for key,v in WEAPONS.items():
    o=json.loads((JR/f"assets/{v['ns']}/models/item/{v['path']}.json").read_text());ok &= o["display"]["thirdperson_righthand"]["scale"][0]<=.65
Q("all seven Java third-person scales safe",ok)
ok=True
for key,v in WEAPONS.items():
    o=json.loads((JR/f"assets/{v['ns']}/models/item/{v['path']}.json").read_text())
    for ref in o["textures"].values():
        ns,path=ref.split(":",1);ok &= (JR/f"assets/{ns}/textures/{path}.png").is_file()
Q("all seven Java model texture references resolve",ok)
ok=True
for key,v in WEAPONS.items():
    o=json.loads((JR/f"assets/{v['ns']}/models/item/{v['path']}.json").read_text())
    for ref in o["textures"].values():
        ns,path=ref.split(":",1);ok &= Image.open(JR/f"assets/{ns}/textures/{path}.png").size==(256,256)
Q("all seven Java weapon textures are 256px",ok)
Q("Stormpiercer three pull models present",all((JR/f"assets/legendaryv34/models/item/stormpiercer_recurve_bow_pulling_{i}.json").is_file() for i in range(3)))
stormdef=json.loads((JR/"assets/legendaryv34/items/stormpiercer_recurve_bow.json").read_text())["model"]
Q("Stormpiercer still uses using_item model condition",stormdef.get("type")=="minecraft:condition" and stormdef.get("property")=="minecraft:using_item")
Q("Stormpiercer still uses use_duration pull dispatch",stormdef["on_true"].get("type")=="minecraft:range_dispatch" and stormdef["on_true"].get("property")=="minecraft:use_duration")
Q("Java armor visor open/closed files retained",all((JR/f"assets/legendaryv34/equipment/{s}_helmet_{m}.json").is_file() for s in SETS for m in ("open","closed")))
Q("Java armor full-set equipment files retained",all((JR/f"assets/legendaryv34/equipment/{s}_set.json").is_file() for s in SETS))

# Bedrock individual geometry
for key,v in WEAPONS.items():
    bid=v["bid"].split(":",1)[1]
    Q(f"{key} Bedrock geometry exists",(BR/f"models/entity/{bid}.geo.json").is_file())
# count now 36
ok=True
for key,v in WEAPONS.items():
    bid=v["bid"].split(":",1)[1];g=json.loads((BR/f"models/entity/{bid}.geo.json").read_text())["minecraft:geometry"][0];n=sum(len(b.get("cubes",[])) for b in g["bones"]);ok &= 8<=n<=30
Q("all seven Bedrock cube budgets stay 8..30",ok)
ok=True
for key,v in WEAPONS.items():
    bid=v["bid"].split(":",1)[1];g=json.loads((BR/f"models/entity/{bid}.geo.json").read_text())["minecraft:geometry"][0]["bones"];ok &= any(b.get("binding")=="q.item_slot_to_bone_name(context.item_slot)" for b in g)
Q("all seven Bedrock weapon geometries bind to hand slot bone",ok)
Q("all seven Bedrock attachables exist",all((BR/f"attachables/{v['bid'].split(':',1)[1]}.player.json").is_file() for v in WEAPONS.values()))
ok=True
for key,v in WEAPONS.items():
    bid=v["bid"].split(":",1)[1];a=json.loads((BR/f"attachables/{bid}.player.json").read_text())["minecraft:attachable"]["description"];ok &= a["identifier"]==v["bid"]
Q("all seven Bedrock attachable identifiers match mappings",ok)
ok=True
for key,v in WEAPONS.items():
    bid=v["bid"].split(":",1)[1];a=json.loads((BR/f"attachables/{bid}.player.json").read_text())["minecraft:attachable"]["description"];ok &= set(a.get("animations",{}))=={"hold_first_person","hold_third_person"} and len(a.get("scripts",{}).get("animate",[]))==2
Q("all seven Bedrock attachables wire first/third hold animations",ok)
anim=json.loads((BR/"animations/legendary_weapons_v367.animation.json").read_text())["animations"]
ok=True
for key,v in WEAPONS.items():
    bid=v["bid"].split(":",1)[1];a=json.loads((BR/f"attachables/{bid}.player.json").read_text())["minecraft:attachable"]["description"];ok &= all(ref in anim for ref in a["animations"].values())
Q("all seven Bedrock hold animation references resolve",ok)
ok=True
for key,v in WEAPONS.items():
    bid=v["bid"].split(":",1)[1];a=json.loads((BR/f"attachables/{bid}.player.json").read_text())["minecraft:attachable"]["description"];third=anim[a["animations"]["hold_third_person"]]["bones"]["bb_main"];ok &= third["position"][1]==-24
Q("all seven Bedrock third-person bound-bone offsets use -24Y",ok)
Q("all seven Bedrock weapon textures are 128px",all(Image.open(BR/f"textures/items/{v['bid'].split(':',1)[1]}.png").size==(128,128) for v in WEAPONS.values()))
Q("all seven Bedrock atlas icon keys exist",all(v["bid"] in td for v in WEAPONS.values()))

# Mapping
defs=[d for arr in mapping["items"].values() for d in arr if d.get("type")=="definition"]
Q("all seven modern definition mappings exist",all(sum(1 for d in defs if d.get("model")==v["model"])==1 for v in WEAPONS.values()))
Q("Soul Tide no longer uses legacy CMD mapping",not any(d.get("type")=="legacy" and d.get("custom_model_data")==910041 for arr in mapping["items"].values() for d in arr))
Q("Leviathan no longer uses legacy CMD mapping",not any(d.get("type")=="legacy" and d.get("custom_model_data")==910042 for arr in mapping["items"].values() for d in arr))
Q("all seven Bedrock identifiers are unique",len({v["bid"] for v in WEAPONS.values()})==7)
Q("all seven mapped items request handheld rendering",all(next(d for d in defs if d.get("model")==v["model"])["bedrock_options"].get("display_handheld") is True for v in WEAPONS.values()))
# Five additional safeguards after QA50; these do not change the requested 50-count report.
assert "components" not in next(d for d in defs if d.get("model")==WEAPONS["stormpiercer"]["model"])
assert "components" not in next(d for d in defs if d.get("model")==WEAPONS["soul_tide"]["model"])
assert "components" not in next(d for d in defs if d.get("model")==WEAPONS["leviathan"]["model"])
assert all((BR/f"attachables/armor_{s}_helmet_{m}.json").is_file() for s in SETS for m in ("open","closed"))
assert all((BR/f"attachables/armor_{s}_{p}.json").is_file() for s in SETS for p in ("chest","legs","boots"))
print("EXTRA 5 SAFEGUARDS PASS")

assert len(checks)==50,len(checks)
REPORT.write_text("\n".join(f"{i+1:02d}. PASS - {name}" for i,name in enumerate(checks))+"\n\nQA50: 50/50 PASS\nEXTRA SAFEGUARDS: 5/5 PASS\n",encoding="utf-8")

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

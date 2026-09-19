from pathlib import Path
import json, math, shutil, zipfile, hashlib, uuid, random
from PIL import Image, ImageDraw

BASE=Path("LegendaryRais-Bedrock-v2.8.0-REALISM-FX.mcpack")
OUT=Path("LegendaryRais-Bedrock-v3.5.2-REFORGED-HOTFIX.mcpack")
SHA=Path("LegendaryRais-Bedrock-v3.5.2-REFORGED-HOTFIX.sha1")
MAP=Path("LegendaryRais-Geyser-v3.5.2-mappings.json")
ROOT=Path(".build/generated-v352-bedrock")

if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def wr(rel,obj):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def tex(name,base,edge,glow):
    p=ROOT/f"textures/items/{name}.png"; p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new("RGBA",(256,256),base+(255,))
    d=ImageDraw.Draw(im)
    for y in range(256):
        t=y/255
        c=tuple(int(base[i]*(1-t*.42)+edge[i]*(t*.42)) for i in range(3))+(255,)
        d.line((0,y,255,y),fill=c)
    random.seed(name)
    for _ in range(900):
        x=random.randrange(256); y=random.randrange(256)
        if random.random()<.68:d.point((x,y),fill=glow+(random.randrange(20,78),))
    for i in range(6):
        d.line((0,30+i*38,255,30+i*38),fill=glow+(38,),width=2)
    im.save(p,optimize=True)

def cube(origin,size,uv=(0,0),pivot=None,rot=None):
    c={"origin":[round(v,3) for v in origin],"size":[round(v,3) for v in size],"uv":list(uv)}
    if pivot is not None:c["pivot"]=[round(v,3) for v in pivot]
    if rot is not None:c["rotation"]=[round(v,3) for v in rot]
    return c

def sword(width=3.2,length=28,handle=9,curve=0):
    a=[]
    a += [cube((-1,-13,-1),(2,1.5,2)),cube((-.82,-11.5,-.72),(1.64,handle,.44))]
    for i in range(7):
        y=-10.8+i*(handle/7)
        a.append(cube((-1.02,y,-.78),(2.04,.22,.56),(32,0)))
    a += [cube((-4,-2.2,-.48),(8,.70,.96),(0,32)),cube((-1.2,-1.55,-.68),(2.4,1.1,1.36),(64,32))]
    y0=-.45
    for i in range(30):
        t=i/29
        y=y0+t*length
        w=width*(1-t)**.64+.18
        cx=curve*math.sin(math.pi*t)*1.8
        a.append(cube((cx-w/2,y,-.40),(w,length/30+.16,.80),(0,64)))
        if i%3==0:a.append(cube((cx-w/2-.10,y+.05,-.20),(.14,length/30,.40),(96,64)))
    tip=y0+length
    for i in range(5):
        w=(width*.58)*(1-i/5)
        a.append(cube((-w/2,tip+i*.52,-.32),(w,.56,.64),(0,96)))
    return a

def bow():
    a=[cube((-.75,-4,-.65),(1.5,8,1.3)),cube((-1.45,-.8,-.9),(2.9,2.8,1.8),(64,0))]
    for s in (-1,1):
        for i in range(9):
            t=i/8; y=s*(5.5+i*2.45); x=s*(.75+2.7*t**1.25)
            ang=s*(-18-5*i)
            a.append(cube((x-.42,y-1.6,-.38),(.84,3.2,.76),(0,64),(x,y,0),(0,0,ang)))
        y=s*26.0; x=s*3.6
        a.append(cube((x-.34,y-1.7,-.34),(.68,3.4,.68),(64,64),(x,y,0),(0,0,s*38)))
    # thin string segments
    a += [cube((-.10,-27,-.10),(.20,23,.20),(128,0),(-.1,-15,0),(0,0,-8)),
          cube((-.10,4,-.10),(.20,23,.20),(128,0),(.1,15,0),(0,0,8))]
    return a

def spear():
    a=[]
    for i in range(32):
        y=-16+i*1.2
        a.append(cube((-.46,y,-.46),(.92,1.14,.92),(0,0)))
        if i%5==0:a.append(cube((-.70,y+.36,-.58),(1.4,.18,1.16),(64,0)))
    y=22.0
    for i in range(16):
        t=i/15; half=2.7*(math.sin(math.pi*t)**.72)+.12
        a.append(cube((-half,y+i*.76,-.36),(half*2,.80,.72),(0,64)))
    a.append(cube((-.14,34.0,-.20),(.28,2.0,.40),(128,64)))
    return a

def daggers():
    a=[]
    for s in (-1,1):
        cx=s*2.9
        a += [cube((cx-.65,-10,-.58),(1.30,7.5,1.16),(0,0)),
              cube((cx-1.75,-2.7,-.38),(3.5,.65,.76),(64,0))]
        for i in range(15):
            t=i/14; y=-2+i*1.15; h=1.26*(1-t)+.16
            bend=s*.45*math.sin(math.pi*t)
            a.append(cube((cx+bend-h,y,-.38),(h*2,1.08,.76),(0,64)))
        a.append(cube((cx-.12,14.8,-.20),(.24,1.8,.40),(128,64)))
    return a

def geo(identifier,cubes):
    return {"format_version":"1.16.0","minecraft:geometry":[{
      "description":{"identifier":identifier,"texture_width":256,"texture_height":256,
      "visible_bounds_width":7,"visible_bounds_height":8,"visible_bounds_offset":[0,8,0]},
      "bones":[{"name":"bb_main","pivot":[0,8,0],"binding":"q.item_slot_to_bone_name(context.item_slot)","cubes":cubes}]
    }]}

def attach(identifier,texture,geometry):
    return {"format_version":"1.20.30","minecraft:attachable":{"description":{
      "identifier":identifier,
      "item":{identifier:"query.is_owner_identifier_any('minecraft:player')"},
      "materials":{"default":"entity_alphatest","enchanted":"entity_alphatest_glint"},
      "textures":{"default":texture,"enchanted":"textures/misc/enchanted_item_glint"},
      "geometry":{"default":geometry},
      "render_controllers":["controller.render.item_default"]
    }}}

items={
 "emberfall_claymore":("geometry.raisnet_emberfall_reforged",sword(4.1,29,9,.05),(44,17,11),(112,33,12),(255,104,28)),
 "noctis_longsword":("geometry.raisnet_noctis_reforged",sword(2.7,30,8,-.04),(15,12,25),(58,20,88),(178,70,255)),
 "stormpiercer_recurve_bow":("geometry.raisnet_stormpiercer_reforged",bow(),(14,31,42),(32,84,106),(90,230,255)),
 "gaia_war_spear":("geometry.raisnet_gaia_reforged",spear(),(27,46,20),(70,94,34),(165,228,82)),
 "astral_twin_daggers":("geometry.raisnet_astral_reforged",daggers(),(28,16,52),(74,36,110),(220,105,255)),
}

for name,(gid,cubes,b,e,g) in items.items():
    tex(name,b,e,g)
    wr(f"models/entity/{name}.geo.json",geo(gid,cubes))
    identifier=f"raisnet:{name}"
    wr(f"attachables/{name}.player.json",attach(identifier,f"textures/items/{name}",gid))

it=ROOT/"textures/item_texture.json"
idata=json.loads(it.read_text(encoding="utf-8"))
td=idata.setdefault("texture_data",{})
for name in items: td[f"raisnet:{name}"]={"textures":f"textures/items/{name}"}
it.write_text(json.dumps(idata,separators=(",",":")),encoding="utf-8")

mapping=json.loads(Path("LegendaryRais-Geyser-v2.8.0-mappings.json").read_text(encoding="utf-8"))
mi=mapping.setdefault("items",{})
def add(base,cmd,name,title):
    arr=mi.setdefault(base,[])
    arr=[x for x in arr if x.get("custom_model_data")!=cmd]
    arr.append({"type":"legacy","custom_model_data":cmd,"bedrock_identifier":f"raisnet:{name}","display_name":title,
      "bedrock_options":{"icon":f"raisnet:{name}","display_handheld":True,"creative_category":"equipment"}})
    mi[base]=arr
add("minecraft:netherite_sword",910051,"emberfall_claymore","Emberfall Claymore")
add("minecraft:netherite_sword",910052,"noctis_longsword","Noctis Longsword")
add("minecraft:bow",910053,"stormpiercer_recurve_bow","Stormpiercer Tempest Bow")
add("minecraft:netherite_shovel",910054,"gaia_war_spear","Gaia War Spear")
add("minecraft:shears",910055,"astral_twin_daggers","Astral Twin Daggers")
MAP.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# New manifest identity. Existing Soul Tide + Leviathan assets are preserved untouched from v2.8.
mf=ROOT/"manifest.json"
manifest=json.loads(mf.read_text(encoding="utf-8"))
manifest["header"]["name"]="RaisNet LegendaryRais v3.5.2 Reforged Hotfix"
manifest["header"]["description"]="Refined crossplay legendary arsenal; Soul Tide + Leviathan preserved; stable armor rendering"
manifest["header"]["uuid"]="b9cc2d8b-8544-41bc-8799-7d4ad4c05d82"
manifest["header"]["version"]=[3,5,2]
manifest["modules"][0]["uuid"]="d0f439b1-1527-4f50-bbca-d15a4f61c03f"
manifest["modules"][0]["version"]=[3,5,2]
mf.write_text(json.dumps(manifest,separators=(",",":")),encoding="utf-8")

# Validate JSON and make pack.
for p in ROOT.rglob("*.json"): json.loads(p.read_text(encoding="utf-8"))
for n in items:
    assert (ROOT/f"models/entity/{n}.geo.json").is_file()
    assert (ROOT/f"attachables/{n}.player.json").is_file()
# Water locks: old files must still be present.
assert (ROOT/"models/entity/soul_tide_katana.geo.json").is_file()
assert (ROOT/"models/entity/abyss_leviathan_trident.geo.json").is_file()

if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n",encoding="utf-8")
print("VALID",OUT.stat().st_size,sha,"GEYSER",MAP)

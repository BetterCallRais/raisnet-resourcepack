from pathlib import Path
import json, math, shutil, zipfile, hashlib, random
from PIL import Image, ImageDraw

BASE=Path("LegendaryRais-Bedrock-v3.5.2-REFORGED-HOTFIX.mcpack")
BASEMAP=Path("LegendaryRais-Geyser-v3.5.2-mappings.json")
OUT=Path("LegendaryRais-Bedrock-v3.5.3-FULL-REFORGE.mcpack")
SHA=Path("LegendaryRais-Bedrock-v3.5.3-FULL-REFORGE.sha1")
MAP=Path("LegendaryRais-Geyser-v3.5.3-mappings.json")
ROOT=Path(".build/generated-v353-bedrock")

if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def wr(rel,obj):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def cube(origin,size,uv=(0,0),pivot=None,rot=None):
    c={"origin":[round(float(v),3) for v in origin],"size":[round(float(v),3) for v in size],"uv":list(uv)}
    if pivot is not None:c["pivot"]=[round(float(v),3) for v in pivot]
    if rot is not None:c["rotation"]=[round(float(v),3) for v in rot]
    return c

def forged_tex(name,base,edge,accent):
    p=ROOT/f"textures/items/{name}.png"; p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new("RGBA",(256,256),base+(255,)); px=im.load()
    random.seed("bed-v353-"+name)
    for y in range(256):
        for x in range(256):
            shine=.11*(1-y/255)+.07*(x/255)
            noise=(random.random()-.5)*.025
            col=[]
            for i in range(3):
                v=base[i]*(1-shine*.28)+edge[i]*(shine*.28+noise)
                col.append(max(0,min(255,int(v))))
            px[x,y]=tuple(col)+(255,)
    d=ImageDraw.Draw(im,"RGBA")
    for y in (48,104,168,224):d.line((0,y,255,y),fill=accent+(28,),width=2)
    d.line((35,0,95,255),fill=accent+(32,),width=3)
    im.save(p,optimize=True)

def sword(width=3.0,length=31,heavy=False,dark=False):
    a=[]
    a += [cube((-1.0,-13.2,-.75),(2.0,1.7,1.5),(0,0)),
          cube((-.72,-11.5,-.52),(1.44,8.0,1.04),(32,0))]
    for i in range(7):
        y=-11.0+i*1.05
        a.append(cube((-.92,y,-.60),(1.84,.20,1.20),(64,0)))
    gy=-3.45
    a += [cube((-4.2,gy,-.34),(3.7,.65,.68),(0,48),(-.5,gy+.3,0),(0,0,-22.5)),
          cube((.5,gy,-.34),(3.7,.65,.68),(0,48),(.5,gy+.3,0),(0,0,22.5)),
          cube((-1.1,gy+.1,-.65),(2.2,1.1,1.3),(64,48))]
    y0=-2.3
    seg=36
    for i in range(seg):
        t=i/(seg-1); y=y0+t*length
        half=((width*(1-.68*t)+.14)/2)
        cx=(.30*math.sin(t*math.pi)) if dark else 0
        thick=.32 if not heavy else .42
        a.append(cube((cx-half,y,-thick),(half*2,length/seg+.10,thick*2),(0,96)))
        if i%3==0:a.append(cube((cx-.10,y+.03,-thick-.05),(.20,length/seg,.10),(128,96)))
    a += [cube((-.44,28.7,-.22),(.88,1.35,.44),(0,144)),
          cube((-.18,29.9,-.14),(.36,1.35,.28),(64,144))]
    return a

def bow():
    a=[cube((-.65,-3.2,-.55),(1.3,7.4,1.1),(0,0)),cube((-1.25,-.2,-.75),(2.5,2.6,1.5),(64,0))]
    upper=[(0,5,0),(.6,8.1,18),(1.5,11.2,24),(2.5,14.4,30),(3.4,17.8,36),(4.0,21.2,43)]
    lower=[(0,-4,0),(-.6,-7.1,-18),(-1.5,-10.2,-24),(-2.5,-13.4,-30),(-3.4,-16.8,-36),(-4.0,-20.2,-43)]
    for cx,cy,ang in upper+lower:
        a.append(cube((cx-.36,cy-1.85,-.30),(.72,3.7,.60),(0,64),(cx,cy,0),(0,0,ang)))
    a += [cube((3.65,22.1,-.28),(.60,4.0,.56),(64,64),(3.9,24,0),(0,0,-25)),
          cube((-4.25,-24.1,-.28),(.60,4.0,.56),(64,64),(-3.9,-22,0),(0,0,25))]
    # slim string
    a += [cube((-.08,-22.0,-.06),(.16,20.5,.12),(128,0),(-.1,-12,0),(0,0,-10)),
          cube((-.08,1.5,-.06),(.16,22.5,.12),(128,0),(.1,12,0),(0,0,10))]
    return a

def spear():
    a=[]
    for i in range(35):
        y=-17+i*1.10
        a.append(cube((-.38,y,-.38),(.76,1.05,.76),(0,0)))
        if i%5==0:a.append(cube((-.60,y+.30,-.48),(1.20,.18,.96),(64,0)))
    y=21.0
    for i in range(18):
        t=i/17; half=2.5*(math.sin(math.pi*t)**.72)+.10
        a.append(cube((-half,y+i*.65,-.30),(half*2,.70,.60),(0,64)))
    a += [cube((-.11,32.2,-.18),(.22,1.8,.36),(128,64)),
          cube((-2.15,21.0,-.22),(1.65,1.2,.44),(96,64),(-.5,21.5,0),(0,0,-24)),
          cube((.5,21.0,-.22),(1.65,1.2,.44),(96,64),(.5,21.5,0),(0,0,24))]
    return a

def daggers():
    a=[]
    for s in (-1,1):
        cx=s*2.75
        a += [cube((cx-.52,-9.4,-.42),(1.04,6.8,.84),(0,0)),
              cube((cx-1.45,-2.8,-.28),(2.9,.60,.56),(64,0))]
        for i in range(16):
            t=i/15; y=-2.15+i*1.02
            half=1.12*(1-t)+.12
            bend=s*.42*math.sin(t*math.pi)
            a.append(cube((cx+bend-half,y,-.27),(half*2,.98,.54),(0,64)))
        a.append(cube((cx-.10,13.2,-.17),(.20,1.8,.34),(128,64)))
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
 "emberfall_claymore":("geometry.raisnet_emberfall_v353",sword(4.0,31,True,False),(42,15,9),(126,48,18),(255,118,38)),
 "noctis_longsword":("geometry.raisnet_noctis_v353",sword(2.55,31,False,True),(12,11,22),(70,28,102),(190,82,255)),
 "stormpiercer_recurve_bow":("geometry.raisnet_stormpiercer_v353",bow(),(12,28,39),(42,100,126),(100,238,255)),
 "gaia_war_spear":("geometry.raisnet_gaia_v353",spear(),(24,41,17),(82,108,42),(174,236,92)),
 "astral_twin_daggers":("geometry.raisnet_astral_v353",daggers(),(26,13,47),(88,44,128),(230,120,255)),
}
for name,(gid,cubes,b,e,g) in items.items():
    forged_tex(name,b,e,g)
    wr(f"models/entity/{name}.geo.json",geo(gid,cubes))
    wr(f"attachables/{name}.player.json",attach(f"raisnet:{name}",f"textures/items/{name}",gid))

it=ROOT/"textures/item_texture.json"
idata=json.loads(it.read_text(encoding="utf-8"))
td=idata.setdefault("texture_data",{})
for name in items:td[f"raisnet:{name}"]={"textures":f"textures/items/{name}"}
it.write_text(json.dumps(idata,separators=(",",":")),encoding="utf-8")

mapping=json.loads(BASEMAP.read_text(encoding="utf-8"))
mi=mapping.setdefault("items",{})
def add(base,cmd,name,title):
    arr=[x for x in mi.get(base,[]) if x.get("custom_model_data")!=cmd]
    arr.append({"type":"legacy","custom_model_data":cmd,"bedrock_identifier":f"raisnet:{name}","display_name":title,
      "bedrock_options":{"icon":f"raisnet:{name}","display_handheld":True,"creative_category":"equipment"}})
    mi[base]=arr
add("minecraft:netherite_sword",910051,"emberfall_claymore","Emberfall Claymore")
add("minecraft:netherite_sword",910052,"noctis_longsword","Noctis Longsword")
add("minecraft:bow",910053,"stormpiercer_recurve_bow","Stormpiercer Tempest Bow")
add("minecraft:netherite_shovel",910054,"gaia_war_spear","Gaia War Spear")
add("minecraft:shears",910055,"astral_twin_daggers","Astral Twin Daggers")
MAP.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# Fresh manifest; water weapon files from base remain untouched.
mf=ROOT/"manifest.json"
manifest=json.loads(mf.read_text(encoding="utf-8"))
manifest["header"]["name"]="RaisNet LegendaryRais v3.5.3 FULL REFORGE"
manifest["header"]["description"]="Full visual reforge for non-water relics; native armor rig; Soul Tide + Leviathan preserved"
manifest["header"]["uuid"]="676f97c8-f676-4d44-bd4e-bd31e2d2f81e"
manifest["header"]["version"]=[3,5,3]
manifest["modules"][0]["uuid"]="30f4d982-2f60-4ac7-b86f-877f0533bfe2"
manifest["modules"][0]["version"]=[3,5,3]
mf.write_text(json.dumps(manifest,separators=(",",":")),encoding="utf-8")

for p in ROOT.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
for n in items:
    assert (ROOT/f"models/entity/{n}.geo.json").is_file()
    assert (ROOT/f"attachables/{n}.player.json").is_file()
# hard lock the two accepted water weapons
assert (ROOT/"models/entity/soul_tide_katana.geo.json").is_file()
assert (ROOT/"models/entity/abyss_leviathan_trident.geo.json").is_file()
assert (ROOT/"attachables/soul_tide_katana.player.json").is_file()
assert (ROOT/"attachables/abyss_leviathan_trident.player.json").is_file()

if OUT.exists():OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad:raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n",encoding="utf-8")
print("VALID",OUT.stat().st_size,sha,"WEAPONS",len(items))

from pathlib import Path
import subprocess, zipfile, json, shutil, hashlib, math, struct, zlib

BASE=Path("LegendaryRais-Bedrock-v2.6.0-AQUATIC-AWAKENING.mcpack")
OUT=Path("LegendaryRais-Bedrock-v2.8.0-REALISM-FX.mcpack")
SHA=Path("LegendaryRais-Bedrock-v2.8.0-REALISM-FX.sha1")
MAP=Path("LegendaryRais-Geyser-v2.8.0-mappings.json")
ROOT=Path(".build/generated-v280-bedrock")

subprocess.run(["python3",".build/build_v260_bedrock.py"],check=True)
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def wr(rel,obj):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def png(path,w,h,fn):
    raw=b"".join(b"\x00"+b"".join(bytes(fn(x,y)) for x in range(w)) for y in range(h))
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    data=b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+ch(b"IDAT",zlib.compress(raw,9))+ch(b"IEND",b"")
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)

# --- realistic Bedrock geometry ---
soul=[]
# pommel + slim tsuka
soul += [{"origin":[-1.0,-12,-1.0],"size":[2.0,1.3,2.0],"uv":[0,0]}]
for i in range(14):
    y=-10.7+i*1.05
    soul.append({"origin":[-1.0,round(y,2),-0.95],"size":[2.0,.98,1.9],"uv":[0,0]})
    if i%2==0:
        soul.append({"origin":[-1.18,round(y+.22,2),-.80],"size":[2.36,.22,1.60],"uv":[48,0]})
# tsuba and habaki
soul += [
 {"origin":[-3.15,5.0,-1.55],"size":[6.3,.65,3.1],"uv":[0,48]},
 {"origin":[-.95,5.55,-.82],"size":[1.9,.72,1.64],"uv":[48,48]}
]
# subtly curved blade
for i in range(58):
    t=i/57.0
    y=6.05+t*25.35
    cx=.86*(t**1.72)
    half=1.50*(1-t)+.14*t
    soul.append({"origin":[round(cx-half,3),round(y,3),-.46],"size":[round(half*2,3),.49,.92],"uv":[0,96]})
    soul.append({"origin":[round(cx-half-.12,3),round(y,3),-.34],"size":[.12,.49,.68],"uv":[96,96]})
    if i%3==0:
        hx=cx-half*.48+.09*math.sin(i*.58)
        soul.append({"origin":[round(hx-.06,3),round(y+.07,3),.46],"size":[.17,.22,.12],"uv":[144,96]})
# pointed kissaki
soul += [
 {"origin":[.48,31.35,-.40],"size":[.58,.38,.80],"uv":[0,128]},
 {"origin":[.78,31.70,-.28],"size":[.28,.24,.56],"uv":[96,128]},
 {"origin":[.96,31.91,-.17],"size":[.10,.09,.34],"uv":[144,128]}
]
# subtle water motes
for i in range(14):
    t=i/13.0; y=8.5+t*20.5; cx=.78*(t**1.7); a=i*1.47
    r=.40+.08*math.sin(i); x=cx+math.cos(a)*r; z=math.sin(a)*r
    soul.append({"origin":[round(x-.05,3),round(y-.05,3),round(z-.05,3)],"size":[.10,.10,.10],"uv":[192,0]})

abyss=[]
# butt and slim long shaft
abyss += [{"origin":[-.82,-12,-.82],"size":[1.64,1.4,1.64],"uv":[0,0]}]
for i in range(25):
    y=-10.6+i*1.02
    abyss.append({"origin":[-.76,round(y,2),-.76],"size":[1.52,.98,1.52],"uv":[0,0]})
    if i%4==0:
        abyss.append({"origin":[-.94,round(y+.18,2),-.30],"size":[1.88,.20,.60],"uv":[64,0]})
# collar
abyss += [
 {"origin":[-1.45,14.75,-1.38],"size":[2.90,1.40,2.76],"uv":[0,48]},
 {"origin":[-.92,15.10,-.92],"size":[1.84,1.40,1.84],"uv":[64,48]}
]
# 3 tines, central longest
for side in (-1,0,1):
    count=32 if side==0 else 27
    for i in range(count):
        t=i/(count-1)
        y=16.25+t*(15.55 if side==0 else 13.75)
        cx=0 if side==0 else side*(2.85+1.05*math.sin(t*math.pi))
        half=(.58*(1-t)+.09*t) if side==0 else (.50*(1-t)+.08*t)
        abyss.append({"origin":[round(cx-half,3),round(y,3),-.46],"size":[round(half*2,3),.52,.92],"uv":[0,96]})
        abyss.append({"origin":[round(cx-half-.09,3),round(y,3),-.33],"size":[.09,.52,.66],"uv":[96,96]})
        if i%4==0:
            abyss.append({"origin":[round(cx-.06,3),round(y+.08,3),.46],"size":[.12,.24,.12],"uv":[144,96]})
# bridges
for side in (-1,1):
    abyss.append({"origin":[0 if side>0 else -2.75,16.05,-.40],"size":[2.75,.50,.80],"uv":[0,128]})
# orbit motes
for i in range(18):
    ang=2*math.pi*i/18
    x=math.cos(ang)*3.7; z=math.sin(ang)*1.35; y=17.2+.24*math.sin(ang*2)
    abyss.append({"origin":[round(x-.05,3),round(y-.05,3),round(z-.05,3)],"size":[.10,.10,.10],"uv":[192,0]})

def geo(identifier,cubes):
    return {"format_version":"1.16.0","minecraft:geometry":[{
      "description":{"identifier":identifier,"texture_width":512,"texture_height":512,
                     "visible_bounds_width":6,"visible_bounds_height":7,"visible_bounds_offset":[0,9,0]},
      "bones":[{"name":"bb_main","pivot":[0,8,0],"binding":"q.item_slot_to_bone_name(context.item_slot)","cubes":cubes}]
    }]}

wr("models/entity/soul_tide_katana.geo.json",geo("geometry.raisnet_soul_tide_katana_realism",soul))
wr("models/entity/abyss_leviathan_trident.geo.json",geo("geometry.raisnet_abyss_leviathan_realism",abyss))

# Update attachables to new geometry identifiers.
def attach(identifier,texture,geometry):
    return {"format_version":"1.20.30","minecraft:attachable":{"description":{
      "identifier":identifier,
      "item":{identifier:"query.is_owner_identifier_any('minecraft:player')"},
      "materials":{"default":"entity_alphatest","enchanted":"entity_alphatest_glint"},
      "textures":{"default":texture,"enchanted":"textures/misc/enchanted_item_glint"},
      "geometry":{"default":geometry},
      "render_controllers":["controller.render.item_default"]
    }}}

wr("attachables/soul_tide_katana.player.json",
   attach("raisnet:soul_tide_katana","textures/items/soul_tide_katana","geometry.raisnet_soul_tide_katana_realism"))
wr("attachables/abyss_leviathan_trident.player.json",
   attach("raisnet:abyss_leviathan_trident","textures/items/abyss_leviathan_trident","geometry.raisnet_abyss_leviathan_realism"))

# Bedrock custom FX icons/models for ItemDisplay fallback translation when available.
def fxtex(kind):
    def fn(x,y):
        cx=x-32; cy=y-32
        if kind in ("ring","aring"):
            r=(cx*cx+cy*cy)**.5
            band=abs(r-21)<2.2
        else:
            band=abs(cy - (-0.045*cx*cx+12))<2.2 and -27<cx<27
        if not band:return (0,0,0,0)
        if kind.startswith("a"): return (70,35,180,220)
        return (40,220,255,225)
    return fn
for name,kind in [("fx_water_ring","ring"),("fx_abyss_ring","aring"),("fx_water_slash","slash"),("fx_abyss_slash","aslash")]:
    png(Path(f"textures/items/{name}.png"),64,64,fxtex(kind))

itemtex=json.loads((ROOT/"textures/item_texture.json").read_text(encoding="utf-8"))
td=itemtex.setdefault("texture_data",{})
for name in ["fx_water_ring","fx_abyss_ring","fx_water_slash","fx_abyss_slash"]:
    td[f"raisnet:{name}"]={"textures":f"textures/items/{name}"}
(ROOT/"textures/item_texture.json").write_text(json.dumps(itemtex,separators=(",",":")),encoding="utf-8")

# Version/UUID refresh.
manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
manifest["header"]["name"]="RaisNet LegendaryRais v2.8 REALISM FX"
manifest["header"]["description"]="Realistic katana/trident geometry + crossplay skill FX"
manifest["header"]["uuid"]="37010ab0-3a20-47a8-89ee-e51a13b6c2da"
manifest["header"]["version"]=[2,8,0]
manifest["modules"][0]["uuid"]="b93b8b47-7522-4f79-89fa-6906512dbe34"
manifest["modules"][0]["version"]=[2,8,0]
(ROOT/"manifest.json").write_text(json.dumps(manifest,separators=(",",":")),encoding="utf-8")

mapping=json.loads(Path("LegendaryRais-Geyser-v2.6.0-mappings.json").read_text(encoding="utf-8"))
mapping["items"]["minecraft:prismarine_shard"]=[
 {"type":"legacy","custom_model_data":910051,"bedrock_identifier":"raisnet:fx_water_slash","display_name":"FX Water Slash",
  "bedrock_options":{"icon":"raisnet:fx_water_slash","display_handheld":False}},
 {"type":"legacy","custom_model_data":910052,"bedrock_identifier":"raisnet:fx_water_ring","display_name":"FX Water Ring",
  "bedrock_options":{"icon":"raisnet:fx_water_ring","display_handheld":False}},
 {"type":"legacy","custom_model_data":910053,"bedrock_identifier":"raisnet:fx_abyss_ring","display_name":"FX Abyss Ring",
  "bedrock_options":{"icon":"raisnet:fx_abyss_ring","display_handheld":False}},
 {"type":"legacy","custom_model_data":910054,"bedrock_identifier":"raisnet:fx_abyss_slash","display_name":"FX Abyss Slash",
  "bedrock_options":{"icon":"raisnet:fx_abyss_slash","display_handheld":False}}
]
MAP.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)

sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n",encoding="utf-8")
print("VALID",OUT.stat().st_size,sha,"SOUL_CUBES",len(soul),"ABYSS_CUBES",len(abyss))

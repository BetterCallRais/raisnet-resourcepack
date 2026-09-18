from pathlib import Path
import json,zipfile,hashlib,struct,zlib,shutil,math

OUT=Path("LegendaryRais-Java-26plus-v2.2.0-FIX.zip")
ROOT=Path(".build/generated-v220")
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)

def wr(p,s):
    p=ROOT/p; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding="utf-8")

def png(path,w,h,fn):
    raw=b"".join(b"\x00"+b"".join(bytes(fn(x,y)) for x in range(w)) for y in range(h))
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    data=b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+ch(b"IDAT",zlib.compress(raw,9))+ch(b"IEND",b"")
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)

def clamp(v): return max(0,min(255,int(v)))
def mix(a,b,t): return tuple(clamp(a[i]*(1-t)+b[i]*t) for i in range(3))
def n2(x,y,s=0): return (((x*73856093)^(y*19349663)^(s*83492791)) & 255)/255.0
def metal_tex(base,hi,seed=0):
    def fn(x,y):
        t=(y/63)*0.45+n2(x,y,seed)*0.22
        rgb=mix(base,hi,min(1,t))
        scratch=20 if ((x*3+y*5+seed)%29==0) else 0
        return (clamp(rgb[0]+scratch),clamp(rgb[1]+scratch),clamp(rgb[2]+scratch),255)
    return fn
def rune_tex(base,hi,seed=0):
    def fn(x,y):
        wave=(math.sin((x+y)*.33)+1)/2
        glow=max(wave, 1.0 if ((x*7+y*11+seed)%37<2) else 0)
        rgb=mix(base,hi,.35+.55*glow)
        return (*rgb,255)
    return fn
def sand_tex(x,y):
    v=n2(x,y,9)
    base=(66,49,39); hi=(124,92,63)
    rgb=mix(base,hi,.2+.65*v)
    if ((x+y*2)%17)==0: rgb=mix(rgb,(60,42,32),.6)
    return (*rgb,255)
def wrap_tex(x,y):
    band=((x+y)//5)%2
    v=n2(x,y,13)
    b=(8,11,16) if band==0 else (18,22,30)
    h=(30,36,48)
    return (*mix(b,h,.25*v),255)
def bone_tex(x,y):
    v=n2(x,y,21); rgb=mix((105,122,132),(220,232,228),.25+.55*v)
    if ((x*2-y)%31)==0: rgb=mix(rgb,(45,60,68),.65)
    return (*rgb,255)
def void_tex(x,y):
    v=n2(x,y,29); wave=(math.sin(x*.28)+math.cos(y*.21)+2)/4
    rgb=mix((13,4,22),(102,25,148),.18+.62*wave*.7+.12*v)
    return (*rgb,255)

# high quality 64x64 textures
texdir=Path("assets/legendaryrais/textures/item")
png(texdir/"dark_metal.png",64,64,metal_tex((7,12,20),(48,66,82),1))
png(texdir/"blue_steel.png",64,64,metal_tex((13,34,58),(54,116,164),2))
png(texdir/"cyan_rune.png",64,64,rune_tex((12,104,155),(150,255,255),3))
png(texdir/"soul_sand.png",64,64,sand_tex)
png(texdir/"black_wrap.png",64,64,wrap_tex)
png(texdir/"bone.png",64,64,bone_tex)
png(texdir/"void.png",64,64,void_tex)

# animated water: four 64x64 frames stacked vertically
def water_anim(x,y):
    f=y//64; yy=y%64
    wave=(math.sin((x*.22)+(yy*.17)+f*1.4)+math.cos((x*.08)-(yy*.25)+f*.8)+2)/4
    foam=1.0 if ((x+yy+f*7)%31<2) else 0
    rgb=mix((8,60,126),(54,216,252),.28+.62*wave)
    if foam: rgb=mix(rgb,(180,255,255),.72)
    alpha=190+int(45*wave)
    return (*rgb,alpha)
png(texdir/"water.png",64,256,water_anim)
wr(texdir/"water.png.mcmeta",json.dumps({"animation":{"frametime":2,"interpolate":True,"frames":[0,1,2,3]}}))

png(Path("pack.png"),64,64,lambda x,y:(6,clamp(55+2*y),clamp(100+2*x),255))

textures={
 "dark":"legendaryrais:item/dark_metal",
 "steel":"legendaryrais:item/blue_steel",
 "cyan":"legendaryrais:item/cyan_rune",
 "sand":"legendaryrais:item/soul_sand",
 "wrap":"legendaryrais:item/black_wrap",
 "bone":"legendaryrais:item/bone",
 "void":"legendaryrais:item/void",
 "water":"legendaryrais:item/water"
}

def face(tex):
    return {k:{"uv":[0,0,16,16],"texture":"#"+tex} for k in ["north","south","east","west","up","down"]}
def cube(fr,to,tex,rot=None):
    d={"from":[round(v,3) for v in fr],"to":[round(v,3) for v in to],"faces":face(tex)}
    if rot: d["rotation"]={"origin":[round(v,3) for v in rot[0]],"axis":rot[1],"angle":rot[2],"rescale":False}
    return d
def mdl(elements):
    return {"textures":textures,"elements":elements,"display":display}

display={
 "thirdperson_righthand":{"rotation":[0,90,-38],"translation":[0,2,1],"scale":[.78,.78,.78]},
 "thirdperson_lefthand":{"rotation":[0,-90,38],"translation":[0,2,1],"scale":[.78,.78,.78]},
 "firstperson_righthand":{"rotation":[0,90,-18],"translation":[1,3,1],"scale":[.82,.82,.82]},
 "firstperson_lefthand":{"rotation":[0,-90,18],"translation":[1,3,1],"scale":[.82,.82,.82]},
 "gui":{"rotation":[24,-38,18],"translation":[0,0,0],"scale":[.74,.74,.74]},
 "ground":{"translation":[0,3,0],"scale":[.48,.48,.48]},
 "fixed":{"rotation":[0,0,0],"translation":[0,0,0],"scale":[.72,.72,.72]}
}

# ---------------- Soul Tide Katana V5 visual rebuild ----------------
s=[]
# pommel + handle core
s += [cube([6.7,-12,6.7],[9.3,-9.8,9.3],"dark"),
      cube([7.15,-11.6,7.15],[8.85,-10.0,8.85],"cyan")]
for y in [ -9.8,-8.0,-6.2,-4.4,-2.6,-0.8,1.0,2.8,4.6 ]:
    s += [cube([6.8,y,6.8],[9.2,min(6.0,y+1.65),9.2],"wrap"),
          cube([7.25,y,7.25],[8.75,min(6.0,y+1.65),8.75],"dark")]
    if y<4:
        s += [cube([6.5,y+.25,6.55],[9.5,y+.58,9.45],"cyan",([8,y+.42,8],"z",22.5 if int(y*10)%2==0 else -22.5))]
# 3D tsuba + soul sand spikes
s += [cube([2.4,5.6,5.6],[13.6,7.0,10.4],"dark"),
      cube([3.2,5.3,6.25],[12.8,7.3,9.75],"sand"),
      cube([5.0,5.55,5.35],[11.0,7.05,10.65],"steel"),
      cube([6.2,5.15,6.3],[9.8,7.5,9.7],"cyan")]
for side in (-1,1):
    x=8+side*5.2
    s += [cube([x-.55,4.7,7.0],[x+.55,7.1,9.0],"sand",([x,6.0,8],"z",22.5*side)),
          cube([x-.35,5.0,6.6],[x+.35,6.2,7.2],"cyan")]
# curved layered blade
for yi in range(7,31):
    t=(yi-7)/24.0
    center=8.0 + 1.55*(t**1.55)
    width=2.45*(1-t)+.72*t
    y2=min(32,yi+1.08)
    s += [cube([center-width,yi,7.08],[center+width,y2,8.92],"water"),
          cube([center-width-.34,yi,7.26],[center-width,y2,8.74],"cyan"),
          cube([center+width,yi,7.26],[center+width+.34,y2,8.74],"steel"),
          cube([center-.38,yi,6.72],[center+.38,y2,7.08],"dark")]
    if yi%3==0:
        s += [cube([center-.23,yi+.16,6.30],[center+.23,min(32,yi+.82),6.72],"cyan"),
              cube([center-width*.56,yi+.22,8.92],[center-width*.18,min(32,yi+.76),9.18],"water")]
# tip
s += [cube([8.95,30.6,7.25],[10.25,32,8.75],"cyan"),
      cube([9.35,31.0,7.45],[10.05,32,8.55],"water")]
wr(Path("assets/legendaryrais/models/item/soul_tide_katana.json"),json.dumps(mdl(s),separators=(",",":")))

# ---------------- Abyss Leviathan Dark Emperor V4 visual rebuild ----------------
a=[]
# shaft
for yi in range(-12,16):
    if yi%2==0:
        a += [cube([6.75,yi,6.75],[9.25,yi+2,9.25],"dark"),
              cube([7.18,yi,7.18],[8.82,yi+2,8.82],"steel")]
    if yi%4==0:
        a += [cube([6.38,yi+.18,6.38],[9.62,yi+.58,9.62],"cyan")]
# chain / tassel-like lower accents
for yi in (-10,-7,-4):
    a += [cube([5.95,yi,7.35],[6.55,yi+1.2,8.65],"bone",([6.25,yi+.6,8],"z",-22.5)),
          cube([9.45,yi,7.35],[10.05,yi+1.2,8.65],"bone",([9.75,yi+.6,8],"z",22.5))]
# leviathan head crown + eye
a += [cube([2.6,14.8,5.2],[13.4,17.3,10.8],"dark"),
      cube([3.3,16.2,5.7],[12.7,19.7,10.3],"bone"),
      cube([4.4,17.2,5.25],[11.6,20.4,10.75],"void"),
      cube([6.15,17.65,4.75],[9.85,20.0,11.25],"cyan"),
      cube([7.0,18.1,4.35],[9.0,19.55,11.65],"void")]
# horns around crown
for side in (-1,1):
    for j,(yy,reach) in enumerate(((15.2,4.8),(17.2,5.8),(19.0,6.5))):
        x=8+side*(4.0+j*.45)
        a += [cube([x-.55,yy,6.35],[x+.55,min(22,yy+2.6),9.65],"bone",([x,yy+1.2,8],"z",22.5*side)),
              cube([x-.26,yy+.25,6.0],[x+.26,yy+1.55,6.4],"cyan")]
# center prong
for yi in range(19,32):
    t=(yi-19)/13.0; w=1.6*(1-t)+.48*t
    a += [cube([8-w,yi,7.05],[8+w,min(32,yi+1.05),8.95],"steel"),
          cube([7.72,yi,6.62],[8.28,min(32,yi+1.05),7.05],"cyan")]
    if yi%2==0:a += [cube([7.35,yi+.15,8.95],[8.65,min(32,yi+.55),9.22],"void")]
# jaw / side prongs
for side in (-1,1):
    for yi in range(19,31):
        t=(yi-19)/12.0
        center=8+side*(4.0+1.55*t)
        w=1.12*(1-t)+.45*t
        a += [cube([center-w,yi,7.05],[center+w,yi+1.05,8.95],"bone"),
              cube([center-.36,yi,6.64],[center+.36,yi+1.05,7.05],"cyan")]
        if yi%2==1:
            tooth=center-side*.5
            a += [cube([tooth-.34,yi+.15,5.85],[tooth+.34,yi+.9,6.64],"bone",([tooth,yi+.5,6.3],"z",22.5*side))]
# fins and barbs
for yi in (10,13,16,19,22,25):
    a += [cube([4.45,yi,5.35],[6.35,yi+1.0,7.05],"bone",([6.2,yi+.5,7],"z",22.5)),
          cube([9.65,yi,8.95],[11.55,yi+1.0,10.65],"bone",([9.8,yi+.5,9],"z",-22.5)),
          cube([5.55,yi+.2,6.25],[6.15,yi+.75,6.85],"cyan"),
          cube([9.85,yi+.2,9.15],[10.45,yi+.75,9.75],"cyan")]
wr(Path("assets/legendaryrais/models/item/abyss_leviathan_trident.json"),json.dumps(mdl(a),separators=(",",":")))

# modern item definitions (26.x style) + explicit item_model identifiers used by plugin
def modern(base,cmd,target):
    return {"model":{"type":"minecraft:range_dispatch","property":"minecraft:custom_model_data","index":0,
        "entries":[{"threshold":float(cmd),"model":{"type":"minecraft:model","model":target}},
                   {"threshold":float(cmd+1),"model":{"type":"minecraft:model","model":"minecraft:item/"+base}}],
        "fallback":{"type":"minecraft:model","model":"minecraft:item/"+base}}}
wr(Path("assets/minecraft/items/netherite_sword.json"),json.dumps(modern("netherite_sword",910041,"legendaryrais:item/soul_tide_katana")))
wr(Path("assets/minecraft/items/trident.json"),json.dumps(modern("trident",910042,"legendaryrais:item/abyss_leviathan_trident")))
wr(Path("assets/soultide/items/soul_tide_katana.json"),json.dumps({"model":{"type":"minecraft:model","model":"legendaryrais:item/soul_tide_katana"}}))
wr(Path("assets/legendaryrais/items/abyss_leviathan_trident.json"),json.dumps({"model":{"type":"minecraft:model","model":"legendaryrais:item/abyss_leviathan_trident"}}))
# 1.21.1 CMD fallback
wr(Path("assets/minecraft/models/item/netherite_sword.json"),json.dumps({"parent":"minecraft:item/handheld","textures":{"layer0":"minecraft:item/netherite_sword"},"overrides":[{"predicate":{"custom_model_data":910041},"model":"legendaryrais:item/soul_tide_katana"}]}))
wr(Path("assets/minecraft/models/item/trident.json"),json.dumps({"parent":"minecraft:item/generated","textures":{"layer0":"minecraft:item/trident"},"overrides":[{"predicate":{"custom_model_data":910042},"model":"legendaryrais:item/abyss_leviathan_trident"}]}))

# strict validation
allowed={-45.0,-22.5,0.0,22.5,45.0}
for mp in [ROOT/"assets/legendaryrais/models/item/soul_tide_katana.json",ROOT/"assets/legendaryrais/models/item/abyss_leviathan_trident.json"]:
    data=json.loads(mp.read_text())
    for i,e in enumerate(data.get("elements",[])):
        for k in ("from","to"):
            if any(v < -16 or v > 32 for v in e[k]): raise RuntimeError(f"{mp.name} element {i} {k} out of bounds {e[k]}")
        if "rotation" in e and float(e["rotation"].get("angle",0)) not in allowed:
            raise RuntimeError(f"{mp.name} element {i} invalid rotation {e['rotation']}")
for jp in ROOT.rglob("*.json"): json.loads(jp.read_text())

wr(Path("pack.mcmeta"),json.dumps({"pack":{"pack_format":34,"supported_formats":{"min_inclusive":34,"max_inclusive":88},"min_format":[34,0],"max_format":[88,0],"description":"LegendaryRais v2.2.0 FIX • HD Soul Tide + Abyss Leviathan • Java 1.21.1–26.2"}}))

if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
Path("LegendaryRais-Java-26plus-v2.2.0-FIX.sha1").write_text(sha+"\n")
print("VALID",OUT.stat().st_size,sha,"SOUL_ELEMENTS",len(s),"ABYSS_ELEMENTS",len(a))

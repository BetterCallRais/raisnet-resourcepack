from pathlib import Path
import subprocess, zipfile, json, shutil, hashlib, math, struct, zlib

BASE=Path("LegendaryRais-Java-26plus-v2.5.0-LIVE-AURA.zip")
OUT=Path("LegendaryRais-Java-26plus-v2.6.0-AQUATIC-AWAKENING.zip")
SHA=Path("LegendaryRais-Java-26plus-v2.6.0-AQUATIC-AWAKENING.sha1")
ROOT=Path(".build/generated-v260-java")

subprocess.run(["python3",".build/build_v250_java.py"],check=True)
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def clamp(v): return max(0,min(255,int(v)))
def mix(a,b,t): return tuple(clamp(a[i]*(1-t)+b[i]*t) for i in range(3))
def n2(x,y,s=0): return (((x*73856093)^(y*19349663)^(s*83492791)) & 1023)/1023.0

def png(path,w,h,fn):
    raw=b"".join(b"\x00"+b"".join(bytes(fn(x,y)) for x in range(w)) for y in range(h))
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    data=b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+ch(b"IDAT",zlib.compress(raw,9))+ch(b"IEND",b"")
    path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)

tex=ROOT/"assets/legendaryrais/textures/item"

# 512px hand-painted-style procedural materials.
def dark_metal(x,y):
    n=n2(x,y,1); brushed=(math.sin(y*.21+x*.025)+1)/2; seam=1 if (x%97<2 or y%113<2) else 0
    rgb=mix((4,8,15),(31,48,68),.18+.50*brushed+.18*n)
    if seam: rgb=mix(rgb,(1,4,8),.72)
    if ((x+y*3)%211)<2: rgb=mix(rgb,(40,160,190),.18)
    return (*rgb,255)

def blue_steel(x,y):
    n=n2(x,y,2); grain=(math.sin(x*.18+y*.012)+math.sin(x*.041-y*.09)+2)/4
    edge=(math.sin((x-y)*.035)+1)/2
    rgb=mix((8,22,46),(54,138,205),.22+.56*grain+.12*n)
    if edge>.92: rgb=mix(rgb,(130,220,250),.16)
    return (*rgb,255)

def cyan_rune(x,y):
    n=n2(x,y,3); glow=(math.sin(x*.08)+math.cos(y*.075)+2)/4
    veins=((x*7+y*11)%127)<3 or ((x-y*2)%173)<2
    rgb=mix((4,55,95),(55,225,255),.32+.54*glow+.08*n)
    if veins: rgb=(160,255,255)
    return (*rgb,255)

def soul_sand(x,y):
    n=n2(x,y,4); pits=((x*13+y*17)%97)<7
    rgb=mix((31,25,24),(112,89,65),.24+.58*n)
    if pits: rgb=mix(rgb,(7,10,13),.72)
    return (*rgb,255)

def black_wrap(x,y):
    band=((x+y)//18)%2; fiber=(math.sin((x-y)*.22)+1)/2; n=n2(x,y,5)
    base=(9,11,17) if band else (16,19,27)
    rgb=mix(base,(42,51,66),.10+.18*fiber+.08*n)
    if ((x+y)%64)<2: rgb=mix(rgb,(25,160,180),.22)
    return (*rgb,255)

def bone(x,y):
    n=n2(x,y,6); vein=(math.sin(x*.045+y*.071)+1)/2
    rgb=mix((88,82,71),(214,207,180),.38+.45*vein+.10*n)
    if ((x*5+y*3)%191)<2: rgb=mix(rgb,(45,38,42),.35)
    return (*rgb,255)

def void_tex(x,y):
    n=n2(x,y,7); neb=(math.sin(x*.031+y*.049)+math.cos(x*.061-y*.023)+2)/4
    rgb=mix((8,3,18),(96,24,145),.20+.56*neb+.10*n)
    if ((x*9+y*7)%223)<3: rgb=(30,205,245)
    return (*rgb,255)

png(tex/"dark_metal.png",512,512,dark_metal)
png(tex/"blue_steel.png",512,512,blue_steel)
png(tex/"cyan_rune.png",512,512,cyan_rune)
png(tex/"soul_sand.png",512,512,soul_sand)
png(tex/"black_wrap.png",512,512,black_wrap)
png(tex/"bone.png",512,512,bone)
png(tex/"void.png",512,512,void_tex)

def water_anim(x,y):
    f=y//512; yy=y%512
    wave=(math.sin(x*.026+yy*.038+f*1.37)+math.cos(x*.013-yy*.047+f*.82)+2)/4
    caustic=(math.sin((x+yy)*.072+f*.9)+1)/2
    foam=1 if ((x+yy+f*41)%173)<3 else 0
    rgb=mix((3,43,112),(38,208,246),.22+.58*wave+.10*caustic)
    if foam: rgb=mix(rgb,(190,255,255),.80)
    alpha=185+int(60*wave)
    return (*rgb,clamp(alpha))

png(tex/"water.png",512,2048,water_anim)
(tex/"water.png.mcmeta").write_text(json.dumps({"animation":{"frametime":2,"interpolate":True,"frames":[0,1,2,3]}}),encoding="utf-8")

def add_cube(arr,fr,to,texture):
    faces={k:{"uv":[0,0,16,16],"texture":"#"+texture} for k in ["north","south","east","west","up","down"]}
    arr.append({"from":[round(v,3) for v in fr],"to":[round(v,3) for v in to],"faces":faces})

# Refine both silhouettes with extra water-energy fins, runes and sharp details.
sp=ROOT/"assets/legendaryrais/models/item/soul_tide_katana.json"
s=json.loads(sp.read_text(encoding="utf-8"))
els=s.setdefault("elements",[])
for i in range(24):
    t=i/23.0; y=8.3+t*22.4; cx=8+2.0*(t**1.55)
    side=-1 if i%2==0 else 1
    add_cube(els,[cx+side*.44,y,6.92],[cx+side*.58,min(32,y+.48),7.18],"cyan")
for i in range(12):
    a=2*math.pi*i/12
    add_cube(els,[8+math.cos(a)*2.7-.09,5.75+math.sin(a*2)*.22,8+math.sin(a)*1.18-.09],
                 [8+math.cos(a)*2.7+.09,6.05+math.sin(a*2)*.22,8+math.sin(a)*1.18+.09],"water")
# Slightly cleaner first-person proportions.
s.setdefault("display",{})["firstperson_righthand"]={"rotation":[0,90,-16],"translation":[1.2,3.1,.8],"scale":[.88,.88,.88]}
s["display"]["thirdperson_righthand"]={"rotation":[0,90,-36],"translation":[0,2,1],"scale":[.82,.82,.82]}
sp.write_text(json.dumps(s,separators=(",",":")),encoding="utf-8")

ap=ROOT/"assets/legendaryrais/models/item/abyss_leviathan_trident.json"
a=json.loads(ap.read_text(encoding="utf-8"))
els=a.setdefault("elements",[])
# Leviathan gill fins + crown runes + sharpened side silhouette.
for side in (-1,1):
    for i in range(8):
        y=17.0+i*1.55
        x=8+side*(4.2+i*.34)
        add_cube(els,[x-.20,y,7.10],[x+.20,min(32,y+1.05),8.90],"void" if i%2 else "cyan")
for i in range(18):
    ang=2*math.pi*i/18
    x=8+math.cos(ang)*4.4; z=8+math.sin(ang)*2.0; y=19.2+.35*math.sin(ang*3)
    add_cube(els,[x-.11,y-.11,z-.11],[x+.11,y+.11,z+.11],"water" if i%3 else "cyan")
for i in range(10):
    y=21+i*.95
    add_cube(els,[7.76,y,6.55],[8.24,min(32,y+.58),6.88],"cyan")
a.setdefault("display",{})["firstperson_righthand"]={"rotation":[0,90,-12],"translation":[1.1,2.7,.6],"scale":[.86,.86,.86]}
a["display"]["thirdperson_righthand"]={"rotation":[0,90,-30],"translation":[0,2,1],"scale":[.80,.80,.80]}
ap.write_text(json.dumps(a,separators=(",",":")),encoding="utf-8")

mc=ROOT/"pack.mcmeta"
meta=json.loads(mc.read_text(encoding="utf-8"))
meta["pack"]["description"]="LegendaryRais v2.6 AQUATIC AWAKENING • 512px Java Legendary Weapons"
mc.write_text(json.dumps(meta,separators=(",",":")),encoding="utf-8")

for mp in [sp,ap]:
    data=json.loads(mp.read_text(encoding="utf-8"))
    for n,e in enumerate(data.get("elements",[])):
        for key in ("from","to"):
            if any(v < -16 or v > 32 for v in e[key]):
                raise RuntimeError(f"{mp.name} element {n} out of bounds: {e[key]}")

if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n",encoding="utf-8")
print("VALID",OUT.stat().st_size,sha,"SOUL",len(s["elements"]),"ABYSS",len(a["elements"]))

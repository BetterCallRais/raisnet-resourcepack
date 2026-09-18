from pathlib import Path
import subprocess, zipfile, json, shutil, hashlib, math, struct, zlib

BASE=Path("LegendaryRais-Java-26plus-v2.6.0-AQUATIC-AWAKENING.zip")
OUT=Path("LegendaryRais-Java-26plus-v2.7.0-MYTHIC-OCEAN.zip")
SHA=Path("LegendaryRais-Java-26plus-v2.7.0-MYTHIC-OCEAN.sha1")
ROOT=Path(".build/generated-v270-java")

subprocess.run(["python3",".build/build_v260_java.py"],check=True)
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def clamp(v): return max(0,min(255,int(v)))
def mix(a,b,t): return tuple(clamp(a[i]*(1-t)+b[i]*t) for i in range(3))
def n2(x,y,s=0): return (((x*73856093)^(y*19349663)^(s*83492791)) & 4095)/4095.0
def ridges(x,y,a,b): return (math.sin(x*a+y*b)+math.sin(x*(a*.43)-y*(b*.71))+2)/4

def png(path,w,h,fn):
    raw=b"".join(b"\x00"+b"".join(bytes(fn(x,y)) for x in range(w)) for y in range(h))
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    data=b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+ch(b"IDAT",zlib.compress(raw,9))+ch(b"IEND",b"")
    path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)

tex=ROOT/"assets/legendaryrais/textures/item"

# 1024px layered materials. Designed to read as polished fantasy metal instead of flat procedural color.
def dark_metal(x,y):
    n=n2(x,y,1); brush=ridges(x,y,.10,.012); micro=ridges(x,y,.31,.004)
    rgb=mix((2,6,12),(34,52,75),.13+.46*brush+.17*micro+.10*n)
    if ((x*3+y*5)%503)<2: rgb=mix(rgb,(30,125,160),.28)
    if x%257<2 or y%271<2: rgb=mix(rgb,(0,2,5),.75)
    return (*rgb,255)

def blue_steel(x,y):
    n=n2(x,y,2); grain=ridges(x,y,.17,.008); sheen=(math.sin((x-y)*.024)+1)/2
    rgb=mix((5,19,45),(58,147,220),.18+.52*grain+.17*sheen+.07*n)
    if sheen>.965: rgb=mix(rgb,(175,235,255),.36)
    if ((x+y*2)%607)<2: rgb=mix(rgb,(8,68,125),.32)
    return (*rgb,255)

def cyan_rune(x,y):
    n=n2(x,y,3); glow=ridges(x,y,.052,.071)
    vein=((x*11+y*17)%337)<3 or ((x-y*3)%419)<3
    halo=((x*7-y*5)%251)<5
    rgb=mix((2,45,84),(58,228,255),.27+.58*glow+.06*n)
    if halo: rgb=mix(rgb,(110,250,255),.30)
    if vein: rgb=(205,255,255)
    return (*rgb,255)

def soul_sand(x,y):
    n=n2(x,y,4); dunes=ridges(x,y,.023,.039)
    pits=((x*19+y*23)%283)<13
    rgb=mix((25,21,22),(128,98,68),.20+.52*dunes+.18*n)
    if pits: rgb=mix(rgb,(5,8,12),.77)
    if ((x-y)%199)<2: rgb=mix(rgb,(80,125,125),.12)
    return (*rgb,255)

def black_wrap(x,y):
    diag=((x+y)//25)%2; fibers=ridges(x,y,.34,-.29); n=n2(x,y,5)
    base=(7,9,14) if diag else (17,20,29)
    rgb=mix(base,(48,59,74),.08+.18*fibers+.08*n)
    if ((x+y)%127)<3: rgb=mix(rgb,(18,165,188),.28)
    return (*rgb,255)

def bone(x,y):
    n=n2(x,y,6); marble=ridges(x,y,.031,.047); crack=((x*5+y*11)%467)<3
    rgb=mix((75,70,66),(226,218,189),.33+.48*marble+.09*n)
    if crack: rgb=mix(rgb,(48,37,41),.48)
    return (*rgb,255)

def void_tex(x,y):
    n=n2(x,y,7); neb=ridges(x,y,.018,.029); pulse=(math.sin((x+y)*.019)+1)/2
    rgb=mix((5,2,15),(108,25,169),.16+.52*neb+.12*pulse+.06*n)
    if ((x*13+y*7)%557)<3: rgb=(32,220,255)
    return (*rgb,255)

for name,fn in [
    ("dark_metal.png",dark_metal),("blue_steel.png",blue_steel),("cyan_rune.png",cyan_rune),
    ("soul_sand.png",soul_sand),("black_wrap.png",black_wrap),("bone.png",bone),("void.png",void_tex)
]:
    png(tex/name,1024,1024,fn)

def water_anim(x,y):
    f=y//1024; yy=y%1024
    phase=f*(math.pi/4)
    wave=(math.sin(x*.017+yy*.026+phase)+math.cos(x*.008-yy*.031+phase*.73)+2)/4
    caust=(math.sin((x+yy)*.041+phase*1.7)+math.cos((x-yy)*.027-phase)+2)/4
    foam=1 if ((x+yy+f*67)%389)<4 else 0
    deep=(math.sin(yy*.006+phase)+1)/2
    rgb=mix((1,31,96),(45,218,255),.17+.48*wave+.17*caust+.07*deep)
    if foam: rgb=mix(rgb,(220,255,255),.86)
    alpha=178+int(70*wave)
    return (*rgb,clamp(alpha))

png(tex/"water.png",1024,8192,water_anim)
(tex/"water.png.mcmeta").write_text(json.dumps({"animation":{"frametime":2,"interpolate":True,"frames":[0,1,2,3,4,5,6,7]}}),encoding="utf-8")

def add_cube(arr,fr,to,texture,rot=None):
    faces={k:{"uv":[0,0,16,16],"texture":"#"+texture} for k in ["north","south","east","west","up","down"]}
    d={"from":[round(v,3) for v in fr],"to":[round(v,3) for v in to],"faces":faces}
    if rot:
        d["rotation"]={"origin":[round(v,3) for v in rot[0]],"axis":rot[1],"angle":rot[2],"rescale":False}
    arr.append(d)

# Soul Tide: premium katana silhouette with thinner edge, pointed kissaki, hamon shards and water halo.
sp=ROOT/"assets/legendaryrais/models/item/soul_tide_katana.json"
s=json.loads(sp.read_text(encoding="utf-8"))
se=s.setdefault("elements",[])

# blade-side hamon shards
for i in range(34):
    t=i/33.0; y=7.7+t*23.5; cx=8+2.05*(t**1.58)
    wave=.24*math.sin(i*.72)
    x=cx-0.72+wave
    add_cube(se,[x-.07,y,8.40],[x+.12,min(32,y+.34),8.62],"cyan")

# fine dorsal runes
for i in range(16):
    t=i/15.0; y=9.0+t*21.8; cx=8+2.05*(t**1.58)
    add_cube(se,[cx-.10,y,6.73],[cx+.10,min(32,y+.30),6.92],"cyan")

# water halo around guard / lower blade
for i in range(20):
    a=2*math.pi*i/20
    x=8+math.cos(a)*3.25
    z=8+math.sin(a)*1.42
    y=6.05+.32*math.sin(a*2)
    add_cube(se,[x-.085,y-.085,z-.085],[x+.085,y+.085,z+.085],"water")

# directional water droplets following blade curvature
for i in range(18):
    t=i/17.0; y=10+t*20.6; cx=8+2.05*(t**1.58); a=i*1.23
    r=.68+.16*math.sin(i*.61)
    x=cx+math.cos(a)*r; z=8+math.sin(a)*r
    add_cube(se,[x-.075,y-.075,z-.075],[x+.075,y+.075,z+.075],"water" if i%3 else "cyan")

# sharp kissaki micro detail
add_cube(se,[9.92,31.40,7.54],[10.38,31.84,8.46],"water")
add_cube(se,[10.16,31.78,7.70],[10.34,32.00,8.30],"cyan")
add_cube(se,[9.84,31.34,7.28],[10.36,31.74,7.48],"steel")

# more natural hand presentation
s.setdefault("display",{})["firstperson_righthand"]={"rotation":[0,90,-14],"translation":[1.35,3.0,.75],"scale":[.91,.91,.91]}
s["display"]["firstperson_lefthand"]={"rotation":[0,-90,14],"translation":[1.35,3.0,.75],"scale":[.91,.91,.91]}
s["display"]["thirdperson_righthand"]={"rotation":[0,90,-34],"translation":[0,2.1,.9],"scale":[.84,.84,.84]}
s["display"]["thirdperson_lefthand"]={"rotation":[0,-90,34],"translation":[0,2.1,.9],"scale":[.84,.84,.84]}
sp.write_text(json.dumps(s,separators=(",",":")),encoding="utf-8")

# Abyss Leviathan: sharpen crown, jaw, gills, rune spine and orbiting abyss-water droplets.
ap=ROOT/"assets/legendaryrais/models/item/abyss_leviathan_trident.json"
a=json.loads(ap.read_text(encoding="utf-8"))
ae=a.setdefault("elements",[])

# crown/gill fins
for side in (-1,1):
    for i in range(11):
        y=16.3+i*1.30
        x=8+side*(4.0+i*.31)
        add_cube(ae,[x-.17,y,7.04],[x+.17,min(32,y+.88),8.96],"void" if i%3 else "cyan",
                 ([x,y+.42,8],"z",22.5*side if i%2==0 else -22.5*side))

# vertical abyss runes on the center crown
for i in range(14):
    y=18.6+i*.84
    add_cube(ae,[7.79,y,6.45],[8.21,min(32,y+.42),6.74],"cyan")

# floating orbit detail around head
for i in range(26):
    ang=2*math.pi*i/26
    r=4.6+.35*math.sin(i*.8)
    x=8+math.cos(ang)*r
    z=8+math.sin(ang)*(2.0+.22*math.cos(i))
    y=19.4+.55*math.sin(ang*3)
    add_cube(ae,[x-.09,y-.09,z-.09],[x+.09,y+.09,z+.09],"water" if i%4 else "void")

# teeth/jaw accents
for side in (-1,1):
    for i in range(7):
        x=8+side*(1.4+i*.56)
        y=17.4+(i%2)*.55
        add_cube(ae,[x-.11,y,5.10],[x+.11,y+.68,5.43],"bone",
                 ([x,y+.34,5.25],"z",22.5*side))

# spike-tip cyan micro accents
for side in (-1,0,1):
    x=8+side*4.25
    add_cube(ae,[x-.13,30.9,7.56],[x+.13,31.68,8.44],"cyan")
    add_cube(ae,[x-.075,31.62,7.72],[x+.075,32.00,8.28],"water")

a.setdefault("display",{})["firstperson_righthand"]={"rotation":[0,90,-10],"translation":[1.2,2.65,.55],"scale":[.89,.89,.89]}
a["display"]["firstperson_lefthand"]={"rotation":[0,-90,10],"translation":[1.2,2.65,.55],"scale":[.89,.89,.89]}
a["display"]["thirdperson_righthand"]={"rotation":[0,90,-28],"translation":[0,2.0,.9],"scale":[.82,.82,.82]}
a["display"]["thirdperson_lefthand"]={"rotation":[0,-90,28],"translation":[0,2.0,.9],"scale":[.82,.82,.82]}
ap.write_text(json.dumps(a,separators=(",",":")),encoding="utf-8")

mc=ROOT/"pack.mcmeta"
meta=json.loads(mc.read_text(encoding="utf-8"))
meta["pack"]["description"]="LegendaryRais v2.7 MYTHIC OCEAN • 1024px Java Legendary Weapons"
mc.write_text(json.dumps(meta,separators=(",",":")),encoding="utf-8")

for mp in [sp,ap]:
    data=json.loads(mp.read_text(encoding="utf-8"))
    for n,e in enumerate(data.get("elements",[])):
        for key in ("from","to"):
            if any(v < -16 or v > 32 for v in e[key]):
                raise RuntimeError(f"{mp.name} element {n} out of bounds: {e[key]}")
        if "rotation" in e and e["rotation"]["angle"] not in (-45,-22.5,0,22.5,45):
            raise RuntimeError(f"{mp.name} element {n} invalid rotation")

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

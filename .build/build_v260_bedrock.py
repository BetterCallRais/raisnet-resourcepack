from pathlib import Path
import subprocess, zipfile, json, shutil, hashlib, math, struct, zlib

BASE=Path("LegendaryRais-Bedrock-v2.5.0-LIVE-AURA.mcpack")
OUT=Path("LegendaryRais-Bedrock-v2.6.0-AQUATIC-AWAKENING.mcpack")
SHA=Path("LegendaryRais-Bedrock-v2.6.0-AQUATIC-AWAKENING.sha1")
MAP=Path("LegendaryRais-Geyser-v2.6.0-mappings.json")
ROOT=Path(".build/generated-v260-bedrock")

subprocess.run(["python3",".build/build_v250_bedrock.py"],check=True)
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

def soul_tex(x,y):
    n=n2(x,y,11); wave=(math.sin(x*.028+y*.017)+math.cos(y*.031-x*.009)+2)/4
    metal=(math.sin((x-y)*.055)+1)/2
    rgb=mix((5,28,72),(38,198,244),.20+.55*wave+.10*metal+.07*n)
    if ((x+y*3)%181)<3: rgb=mix(rgb,(175,255,255),.80)
    return (*rgb,255)

def abyss_tex(x,y):
    n=n2(x,y,17); wave=(math.sin(x*.021-y*.037)+math.cos(x*.011+y*.026)+2)/4
    rgb=mix((6,4,18),(91,28,145),.22+.52*wave+.08*n)
    if ((x*7+y*5)%199)<3: rgb=(34,215,255)
    return (*rgb,255)

png(ROOT/"textures/items/soul_tide_katana.png",512,512,soul_tex)
png(ROOT/"textures/items/abyss_leviathan_trident.png",512,512,abyss_tex)

# Refine geometry with more blade detail and Leviathan crown fins.
def loadgeo(path):
    d=json.loads(path.read_text(encoding="utf-8"))
    g=d["minecraft:geometry"][0]
    g["description"]["texture_width"]=512
    g["description"]["texture_height"]=512
    return d,g,g["bones"][0]["cubes"]

sp=ROOT/"models/entity/soul_tide_katana.geo.json"
s,sg,sc=loadgeo(sp)
for i in range(18):
    t=i/17.0; y=9+t*23; x=1.9*(t**1.55)
    sc.append({"origin":[round(x-.12,2),round(y,2),-.95],"size":[.24,.55,.28],"uv":[160,32]})
for i in range(12):
    a=2*math.pi*i/12
    sc.append({"origin":[round(math.cos(a)*3.0-.12,2),round(6+math.sin(a*2)*.25,2),round(math.sin(a)*1.45-.12,2)],"size":[.24,.24,.24],"uv":[192,32]})
sp.write_text(json.dumps(s,separators=(",",":")),encoding="utf-8")

ap=ROOT/"models/entity/abyss_leviathan_trident.geo.json"
a,ag,ac=loadgeo(ap)
for side in (-1,1):
    for i in range(7):
        y=18+i*1.65; x=side*(5.0+i*.42)
        ac.append({"origin":[round(x-.22,2),round(y,2),-1.15],"size":[.44,1.15,2.3],"uv":[160,64],
                   "pivot":[round(x,2),round(y+.55,2),0],"rotation":[0,0,22.5*side]})
for i in range(18):
    ang=2*math.pi*i/18
    ac.append({"origin":[round(math.cos(ang)*6.2-.13,2),round(20+.45*math.sin(ang*3),2),round(math.sin(ang)*3.0-.13,2)],
               "size":[.26,.26,.26],"uv":[224,64]})
ap.write_text(json.dumps(a,separators=(",",":")),encoding="utf-8")

manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
manifest["header"]["name"]="RaisNet LegendaryRais v2.6 AQUATIC AWAKENING"
manifest["header"]["description"]="512px Soul Tide + Abyss Leviathan with live aquatic aura"
manifest["header"]["uuid"]="2bd1651b-45d1-4e9d-a431-687d80d4db6a"
manifest["header"]["version"]=[2,6,0]
manifest["modules"][0]["uuid"]="f0c14a2e-7334-47cd-b6ee-44311774289d"
manifest["modules"][0]["version"]=[2,6,0]
(ROOT/"manifest.json").write_text(json.dumps(manifest,separators=(",",":")),encoding="utf-8")

# Mapping values remain CMD-compatible; publish a versioned mapping file.
mapping=json.loads(Path("LegendaryRais-Geyser-v2.5.0-mappings.json").read_text(encoding="utf-8"))
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
print("VALID",OUT.stat().st_size,sha,"SOUL_CUBES",len(sc),"ABYSS_CUBES",len(ac))

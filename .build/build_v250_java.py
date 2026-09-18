from pathlib import Path
import subprocess, zipfile, json, shutil, hashlib, math

BASE=Path("LegendaryRais-Java-26plus-v2.4.0-FINAL.zip")
OUT=Path("LegendaryRais-Java-26plus-v2.5.0-LIVE-AURA.zip")
SHA=Path("LegendaryRais-Java-26plus-v2.5.0-LIVE-AURA.sha1")
ROOT=Path(".build/generated-v250-java")

subprocess.run(["python3",".build/build_v240.py"],check=True)
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def faces(tex):
    return {k:{"uv":[0,0,16,16],"texture":"#"+tex} for k in ["north","south","east","west","up","down"]}

def droplet(x,y,z,s,tex="water"):
    return {"from":[round(x-s,3),round(y-s,3),round(z-s,3)],
            "to":[round(x+s,3),round(y+s,3),round(z+s,3)],
            "faces":faces(tex)}

# Fake animated water droplets permanently embedded in the resource-pack model.
# Actual moving live particles are emitted by the plugin.
soulp=ROOT/"assets/legendaryrais/models/item/soul_tide_katana.json"
soul=json.loads(soulp.read_text(encoding="utf-8"))
els=soul.setdefault("elements",[])
for i in range(34):
    t=i/33.0
    y=7.0+t*24.0
    cx=8.0+2.0*(t**1.55)
    a=i*1.73
    r=.62+.18*math.sin(i*.9)
    x=cx+math.cos(a)*r
    z=8.0+math.sin(a)*r
    size=.10+(i%3)*.025
    els.append(droplet(x,y,z,size,"water" if i%4 else "cyan"))
# Small animated soul-water ribbon shards around the guard.
for i in range(12):
    a=2*math.pi*i/12
    x=8+math.cos(a)*3.1
    z=8+math.sin(a)*1.25
    els.append(droplet(x,6.0+(.25*math.sin(a*2)),z,.13,"cyan" if i%2==0 else "water"))
soulp.write_text(json.dumps(soul,separators=(",",":")),encoding="utf-8")

abp=ROOT/"assets/legendaryrais/models/item/abyss_leviathan_trident.json"
abyss=json.loads(abp.read_text(encoding="utf-8"))
els=abyss.setdefault("elements",[])
for i in range(30):
    t=i/29.0
    y=16.5+t*14.5
    a=i*1.41
    r=.85+.35*math.sin(i*.72)
    x=8+math.cos(a)*r
    z=8+math.sin(a)*r
    els.append(droplet(x,y,z,.11+(i%4)*.018,"cyan" if i%3 else "water"))
for i in range(14):
    a=2*math.pi*i/14
    x=8+math.cos(a)*4.35
    z=8+math.sin(a)*1.7
    els.append(droplet(x,19.0+.45*math.sin(a*2),z,.14,"water" if i%2 else "void"))
abp.write_text(json.dumps(abyss,separators=(",",":")),encoding="utf-8")

mc=ROOT/"pack.mcmeta"
meta=json.loads(mc.read_text(encoding="utf-8"))
meta["pack"]["description"]="LegendaryRais v2.5 LIVE AURA • 256px Java models + animated water aura"
mc.write_text(json.dumps(meta,separators=(",",":")),encoding="utf-8")

# Validate all model element bounds and JSON.
for mp in [soulp,abp]:
    data=json.loads(mp.read_text(encoding="utf-8"))
    for n,e in enumerate(data.get("elements",[])):
        for k in ("from","to"):
            if any(v < -16 or v > 32 for v in e[k]):
                raise RuntimeError(f"{mp.name} element {n} {k} out of bounds: {e[k]}")

if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)

sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n",encoding="utf-8")
print("VALID",OUT.stat().st_size,sha,"SOUL",len(soul["elements"]),"ABYSS",len(abyss["elements"]))

from pathlib import Path
import subprocess, zipfile, json, shutil, hashlib, math

BASE=Path("LegendaryRais-Java-26plus-v2.7.0-MYTHIC-OCEAN.zip")
OUT=Path("LegendaryRais-Java-26plus-v2.8.0-REALISM-FX.zip")
SHA=Path("LegendaryRais-Java-26plus-v2.8.0-REALISM-FX.sha1")
ROOT=Path(".build/generated-v280-java")

subprocess.run(["python3",".build/build_v270_java.py"],check=True)
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def wr(rel,obj):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

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
    if rot:
        d["rotation"]={"origin":[round(v,3) for v in rot[0]],"axis":rot[1],"angle":rot[2],"rescale":False}
    return d

display_katana={
 "thirdperson_righthand":{"rotation":[0,90,-34],"translation":[0,2.0,.7],"scale":[.84,.84,.84]},
 "thirdperson_lefthand":{"rotation":[0,-90,34],"translation":[0,2.0,.7],"scale":[.84,.84,.84]},
 "firstperson_righthand":{"rotation":[0,90,-14],"translation":[1.25,3.0,.6],"scale":[.90,.90,.90]},
 "firstperson_lefthand":{"rotation":[0,-90,14],"translation":[1.25,3.0,.6],"scale":[.90,.90,.90]},
 "gui":{"rotation":[20,-38,14],"translation":[0,0,0],"scale":[.72,.72,.72]},
 "ground":{"translation":[0,3,0],"scale":[.46,.46,.46]},
 "fixed":{"rotation":[0,0,0],"translation":[0,0,0],"scale":[.72,.72,.72]}
}

display_trident={
 "thirdperson_righthand":{"rotation":[0,90,-28],"translation":[0,2.0,.8],"scale":[.82,.82,.82]},
 "thirdperson_lefthand":{"rotation":[0,-90,28],"translation":[0,2.0,.8],"scale":[.82,.82,.82]},
 "firstperson_righthand":{"rotation":[0,90,-10],"translation":[1.1,2.6,.5],"scale":[.88,.88,.88]},
 "firstperson_lefthand":{"rotation":[0,-90,10],"translation":[1.1,2.6,.5],"scale":[.88,.88,.88]},
 "gui":{"rotation":[20,-38,12],"translation":[0,0,0],"scale":[.70,.70,.70]},
 "ground":{"translation":[0,3,0],"scale":[.44,.44,.44]},
 "fixed":{"rotation":[0,0,0],"translation":[0,0,0],"scale":[.70,.70,.70]}
}

# REALISM REBUILD:
# Soul Tide follows a restrained real katana silhouette: slim tsuka, small tsuba,
# subtle curvature and long tapered kissaki instead of a chunky fantasy slab.
s=[]
# kashira / pommel
s += [cube([7.10,-12.0,7.15],[8.90,-10.7,8.85],"dark"),
      cube([7.35,-11.85,7.38],[8.65,-10.95,8.62],"cyan")]
# tsuka core + alternating wrap diamonds
for i in range(14):
    y=-10.7+i*1.06
    y2=min(4.95,y+.98)
    s += [cube([7.00,y,7.04],[9.00,y2,8.96],"wrap"),
          cube([7.38,y+.08,7.38],[8.62,y2-.06,8.62],"dark")]
    if i%2==0:
        s.append(cube([6.84,y+.24,7.10],[9.16,min(4.95,y+.48),8.90],"cyan",
                      ([8,y+.36,8],"z",22.5 if (i//2)%2==0 else -22.5)))
# fuchi + habaki
s += [cube([6.82,4.82,6.88],[9.18,5.45,9.12],"dark"),
      cube([6.92,5.38,7.10],[9.08,6.12,8.90],"steel"),
      cube([7.20,5.50,7.28],[8.80,6.18,8.72],"cyan")]
# small elliptical tsuba approximated with thin radial segments
for i in range(18):
    a=2*math.pi*i/18
    x=8+math.cos(a)*3.15
    z=8+math.sin(a)*1.62
    s.append(cube([x-.22,5.02,z-.22],[x+.22,5.78,z+.22],"dark"))
    if i%3==0:
        s.append(cube([x-.12,5.14,z-.12],[x+.12,5.66,z+.12],"cyan"))
# blade: modest historical curvature, narrow thickness, smooth taper
segments=58
for i in range(segments):
    t=i/(segments-1)
    y=6.02+t*25.45
    y2=min(31.55,y+.49)
    # restrained curvature: only ~0.85 model units across full blade
    cx=8.0+0.86*(t**1.72)
    half=1.50*(1-t)+0.16*t
    # main ji/shinogi body
    s.append(cube([cx-half,y,7.52],[cx+half,y2,8.48],"steel"))
    # bright cutting edge
    s.append(cube([cx-half-.13,y,7.60],[cx-half,y2,8.40],"cyan"))
    # dark mune/spine
    s.append(cube([cx+half,y,7.68],[cx+half+.13,y2,8.32],"dark"))
    # subtle hamon, not chunky
    if i%2==0:
        h=cx-half*.48+.10*math.sin(i*.58)
        s.append(cube([h-.07,y+.07,8.48],[h+.11,min(31.55,y+.30),8.62],"water"))
# kissaki: tapered, pointed
s += [cube([8.48,31.35,7.58],[9.05,31.72,8.42],"steel"),
      cube([8.78,31.68,7.68],[9.08,31.93,8.32],"cyan"),
      cube([8.96,31.90,7.78],[9.08,32.00,8.22],"cyan")]
# minimal permanent water accents, keeps real-world silhouette readable
for i in range(14):
    t=i/13.0; y=8.5+t*20.8; cx=8+.78*(t**1.7); a=i*1.47
    r=.40+.08*math.sin(i)
    x=cx+math.cos(a)*r; z=8+math.sin(a)*r
    s.append(cube([x-.055,y-.055,z-.055],[x+.055,y+.055,z+.055],"water" if i%3 else "cyan"))

wr("assets/legendaryrais/models/item/soul_tide_katana.json",
   {"textures":textures,"elements":s,"display":display_katana})

# Abyss Leviathan rebuilt as a restrained three-tined trident:
# long slim shaft, central tine longest, side tines shorter and gently swept.
a=[]
# butt cap
a += [cube([7.20,-12,7.20],[8.80,-10.6,8.80],"dark"),
      cube([7.45,-11.85,7.45],[8.55,-10.95,8.55],"cyan")]
# long shaft
for i in range(25):
    y=-10.6+i*1.02
    y2=min(14.9,y+.98)
    a += [cube([7.24,y,7.24],[8.76,y2,8.76],"dark"),
          cube([7.52,y+.04,7.52],[8.48,y2-.04,8.48],"steel")]
    if i%4==0:
        a.append(cube([7.06,y+.18,7.70],[8.94,y+.38,8.30],"cyan"))
# compact collar
a += [cube([6.55,14.75,6.62],[9.45,16.15,9.38],"dark"),
      cube([6.92,15.10,6.95],[9.08,16.45,9.05],"steel"),
      cube([7.35,15.28,7.15],[8.65,16.60,8.85],"cyan")]
# three realistic tines with subtle sweep
for side in (-1,0,1):
    count=32 if side==0 else 27
    for i in range(count):
        t=i/(count-1)
        y=16.25+t*(15.55 if side==0 else 13.75)
        y2=min(32,y+.52)
        if side==0:
            cx=8.0
        else:
            # side tines flare slightly outward then return toward the tip
            cx=8+side*(2.85+1.05*math.sin(t*math.pi))
        half=(.58*(1-t)+.10*t) if side==0 else (.50*(1-t)+.09*t)
        a.append(cube([cx-half,y,7.50],[cx+half,y2,8.50],"steel"))
        a.append(cube([cx-half-.10,y,7.64],[cx-half,y2,8.36],"cyan"))
        if i%4==0:
            a.append(cube([cx-.08,y+.08,8.50],[cx+.08,min(32,y+.34),8.62],"void" if side else "cyan"))
# side bridges, thin instead of giant head block
for side in (-1,1):
    a += [cube([8 if side>0 else 5.25,16.02,7.58],[10.75 if side>0 else 8,16.55,8.42],"dark",
               ([9.35 if side>0 else 6.65,16.28,8],"z",-22.5*side)),
          cube([8 if side>0 else 5.55,16.22,7.72],[10.45 if side>0 else 8,16.42,8.28],"cyan")]
# understated abyss-water orbit around crown
for i in range(18):
    ang=2*math.pi*i/18
    x=8+math.cos(ang)*3.7; z=8+math.sin(ang)*1.35; y=17.2+.24*math.sin(ang*2)
    a.append(cube([x-.06,y-.06,z-.06],[x+.06,y+.06,z+.06],"water" if i%3 else "void"))

wr("assets/legendaryrais/models/item/abyss_leviathan_trident.json",
   {"textures":textures,"elements":a,"display":display_trident})

# --- Entity-model skill FX fallback ---
# These are not particles. Java renders them as short-lived ItemDisplay entities,
# so even a client that suppresses particles still sees the skill effect.
def fx_display():
    return {
      "thirdperson_righthand":{"rotation":[0,0,0],"translation":[0,0,0],"scale":[1,1,1]},
      "firstperson_righthand":{"rotation":[0,0,0],"translation":[0,0,0],"scale":[1,1,1]},
      "gui":{"rotation":[20,-30,0],"translation":[0,0,0],"scale":[.8,.8,.8]},
      "fixed":{"rotation":[0,0,0],"translation":[0,0,0],"scale":[1,1,1]}
    }

def ring_model(abyss=False):
    e=[]; tex="void" if abyss else "water"
    for i in range(28):
        ang=2*math.pi*i/28
        x=8+math.cos(ang)*5.15
        z=8+math.sin(ang)*5.15
        e.append(cube([x-.13,7.88,z-.13],[x+.13,8.12,z+.13],tex))
        if i%4==0:
            e.append(cube([x-.08,7.78,z-.08],[x+.08,8.22,z+.08],"cyan"))
    return {"textures":textures,"elements":e,"display":fx_display()}

def slash_model(abyss=False):
    e=[]; tex="void" if abyss else "water"
    for i in range(30):
        t=i/29.0
        ang=(-1.0+2.0*t)
        x=8+math.sin(ang)*5.7
        y=8+math.cos(ang)*3.2
        e.append(cube([x-.12,y-.12,7.86],[x+.12,y+.12,8.14],tex))
        if i%5==0:
            e.append(cube([x-.07,y-.07,7.70],[x+.07,y+.07,8.30],"cyan"))
    return {"textures":textures,"elements":e,"display":fx_display()}

wr("assets/legendaryrais/models/item/fx_water_ring.json",ring_model(False))
wr("assets/legendaryrais/models/item/fx_abyss_ring.json",ring_model(True))
wr("assets/legendaryrais/models/item/fx_water_slash.json",slash_model(False))
wr("assets/legendaryrais/models/item/fx_abyss_slash.json",slash_model(True))

# Modern item-model identifiers used directly by plugin.
for name in ["fx_water_ring","fx_abyss_ring","fx_water_slash","fx_abyss_slash"]:
    wr(f"assets/legendaryrais/items/{name}.json",
       {"model":{"type":"minecraft:model","model":f"legendaryrais:item/{name}"}})

# Prismarine shard CMD fallback for 1.21.1 + modern range dispatch.
wr("assets/minecraft/models/item/prismarine_shard.json",{
 "parent":"minecraft:item/generated",
 "textures":{"layer0":"minecraft:item/prismarine_shard"},
 "overrides":[
   {"predicate":{"custom_model_data":910051},"model":"legendaryrais:item/fx_water_slash"},
   {"predicate":{"custom_model_data":910052},"model":"legendaryrais:item/fx_water_ring"},
   {"predicate":{"custom_model_data":910053},"model":"legendaryrais:item/fx_abyss_ring"},
   {"predicate":{"custom_model_data":910054},"model":"legendaryrais:item/fx_abyss_slash"}
 ]})
wr("assets/minecraft/items/prismarine_shard.json",{
 "model":{
   "type":"minecraft:range_dispatch",
   "property":"minecraft:custom_model_data","index":0,
   "entries":[
     {"threshold":910051.0,"model":{"type":"minecraft:model","model":"legendaryrais:item/fx_water_slash"}},
     {"threshold":910052.0,"model":{"type":"minecraft:model","model":"legendaryrais:item/fx_water_ring"}},
     {"threshold":910053.0,"model":{"type":"minecraft:model","model":"legendaryrais:item/fx_abyss_ring"}},
     {"threshold":910054.0,"model":{"type":"minecraft:model","model":"legendaryrais:item/fx_abyss_slash"}},
     {"threshold":910055.0,"model":{"type":"minecraft:model","model":"minecraft:item/prismarine_shard"}}
   ],
   "fallback":{"type":"minecraft:model","model":"minecraft:item/prismarine_shard"}
 }})

mc=ROOT/"pack.mcmeta"
meta=json.loads(mc.read_text(encoding="utf-8"))
meta["pack"]["description"]="LegendaryRais v2.8 REALISM FX • Realistic Katana/Trident + entity-based Java skill FX"
mc.write_text(json.dumps(meta,separators=(",",":")),encoding="utf-8")

allowed={-45.0,-22.5,0.0,22.5,45.0}
check=[
 ROOT/"assets/legendaryrais/models/item/soul_tide_katana.json",
 ROOT/"assets/legendaryrais/models/item/abyss_leviathan_trident.json",
 ROOT/"assets/legendaryrais/models/item/fx_water_ring.json",
 ROOT/"assets/legendaryrais/models/item/fx_abyss_ring.json",
 ROOT/"assets/legendaryrais/models/item/fx_water_slash.json",
 ROOT/"assets/legendaryrais/models/item/fx_abyss_slash.json",
]
for mp in check:
    data=json.loads(mp.read_text(encoding="utf-8"))
    for n,e in enumerate(data.get("elements",[])):
        for key in ("from","to"):
            if any(v < -16 or v > 32 for v in e[key]):
                raise RuntimeError(f"{mp.name} element {n} out of bounds: {e[key]}")
        if "rotation" in e and float(e["rotation"].get("angle",0)) not in allowed:
            raise RuntimeError(f"{mp.name} element {n} invalid rotation")
for jp in ROOT.rglob("*.json"): json.loads(jp.read_text(encoding="utf-8"))

if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)

sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n",encoding="utf-8")
print("VALID",OUT.stat().st_size,sha,"SOUL",len(s),"ABYSS",len(a))

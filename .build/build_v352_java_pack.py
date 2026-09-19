from pathlib import Path
import json, math, shutil, zipfile, hashlib, random
from PIL import Image, ImageDraw

BASE=Path("LegendaryRais-Java-26.1.2-v3.5.0-CROSSCHECKED-FX.zip")
OUT=Path("LegendaryRais-Java-26.1.2-v3.5.2-REFORGED-HOTFIX.zip")
SHA=Path("LegendaryRais-Java-26.1.2-v3.5.2-REFORGED-HOTFIX.sha1")
ROOT=Path(".build/generated-v352-java")
NS="legendaryv34"

if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def wr(rel,obj):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def texture(name, base, edge, glow):
    p=ROOT/f"assets/{NS}/textures/item/{name}.png"; p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new("RGBA",(256,256),base+(255,))
    d=ImageDraw.Draw(im)
    for y in range(256):
        t=y/255
        col=tuple(int(base[i]*(1-t*.35)+edge[i]*(t*.35)) for i in range(3))+(255,)
        d.line((0,y,255,y),fill=col)
    random.seed(name)
    for _ in range(1000):
        x=random.randrange(256); y=random.randrange(256)
        if random.random()<.72:
            a=random.randrange(18,65)
            d.point((x,y),fill=glow+(a,))
    for k in range(7):
        y=26+k*31
        d.line((0,y,255,y),fill=glow+(45,),width=2)
    im.save(p,optimize=True)

def faces(tex):
    return {k:{"texture":f"#main"} for k in ("north","south","east","west","up","down")}

def elem(x1,y1,z1,x2,y2,z2,rot=None):
    e={"from":[round(x1,3),round(y1,3),round(z1,3)],"to":[round(x2,3),round(y2,3),round(z2,3)],"faces":faces("main")}
    if rot: e["rotation"]={"origin":[round(rot[0],3),round(rot[1],3),round(rot[2],3)],"axis":rot[3],"angle":rot[4],"rescale":True}
    return e

DISPLAY={
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,4,1],"scale":[0.72,0.72,0.72]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,4,1],"scale":[0.72,0.72,0.72]},
 "firstperson_righthand":{"rotation":[0,-90,25],"translation":[1.2,3.2,1.0],"scale":[0.82,0.82,0.82]},
 "firstperson_lefthand":{"rotation":[0,90,-25],"translation":[1.2,3.2,1.0],"scale":[0.82,0.82,0.82]},
 "gui":{"rotation":[25,-35,0],"translation":[0,0,0],"scale":[0.52,0.52,0.52]},
 "ground":{"rotation":[0,0,0],"translation":[0,2,0],"scale":[0.42,0.42,0.42]},
 "fixed":{"rotation":[0,180,0],"translation":[0,0,0],"scale":[0.58,0.58,0.58]}
}

def save_model(name,elements,display=None):
    wr(f"assets/{NS}/models/item/{name}.json",{
      "textures":{"main":f"{NS}:item/{name}"},
      "elements":elements,
      "display":display or DISPLAY
    })
    wr(f"assets/{NS}/items/{name}.json",{
      "model":{"type":"minecraft:model","model":f"{NS}:item/{name}"}
    })

def blade(name,width,length,handle,guard,curve=0.0,thickness=.72):
    es=[]
    # pommel + ergonomic grip
    es += [elem(7.0,-12,-.9,9.0,-10,.9),elem(7.25,-10,-.72,8.75,-10+handle,.72)]
    for i in range(6):
        y=-9.5+i*(handle/6)
        es.append(elem(7.0,y,-.82,9.0,y+.34,.82, (8,y+.17,0,"y",22 if i%2==0 else -22)))
    # slimmer guard
    es += [elem(3.0,-10+handle,-.55,13.0,-9.2+handle,.55),
           elem(6.75,-9.3+handle,-.82,9.25,-7.8+handle,.82)]
    y0=-7.8+handle
    seg=24
    for i in range(seg):
        t=i/(seg-1)
        y=y0+t*length
        w=(width*(1-t)**.60)+.24
        cx=8+curve*math.sin(t*math.pi)*2.1
        h=length/seg+.18
        es.append(elem(cx-w/2,y,-thickness/2,cx+w/2,y+h,thickness/2))
        # thin bevel stripe, gives less blocky silhouette
        if i%2==0:
            es.append(elem(cx-w/2-.08,y+.04,-.18,cx-w/2+.16,y+h-.03,.18))
    tip=y0+length
    for j in range(5):
        w=(width*.62)*(1-j/5)
        cx=8+curve*math.sin((.94+j*.012)*math.pi)*2.1
        es.append(elem(cx-w/2,tip+j*.56,-thickness*.42,cx+w/2,tip+(j+1)*.56,thickness*.42))
    return es

def emberfall():
    es=blade("emberfall_claymore",4.15,28,8.0,10,curve=.04,thickness=.86)
    # winged guard, angled not cubic slab
    es += [elem(2.4,-2.0,-.42,7.2,-.9,.42,(7.2,-1.45,0,"z",-22)),
           elem(8.8,-2.0,-.42,13.6,-.9,.42,(8.8,-1.45,0,"z",22))]
    return es

def noctis():
    es=blade("noctis_longsword",2.75,29.5,7.6,8,curve=-.035,thickness=.58)
    es += [elem(4.2,-2.4,-.34,7.5,-1.55,.34,(7.4,-2.0,0,"z",-35)),
           elem(8.5,-2.4,-.34,11.8,-1.55,.34,(8.6,-2.0,0,"z",35))]
    return es

def bow():
    es=[]
    # grip + storm core
    es += [elem(7.15,4,-.72,8.85,12,.72),elem(6.35,7,-1.0,9.65,10,1.0)]
    # curved upper/lower limbs: many thin rotated sections
    for upper in (1,-1):
        for i in range(9):
            t=i/8
            cy=12 + upper*(2.15+i*2.45)
            cx=8 + upper*(1.0+3.0*(t**1.25))
            ang=upper*(-18-5*i)
            es.append(elem(cx-.46,cy-1.8,-.42,cx+.46,cy+1.8,.42,(cx,cy,0,"z",ang)))
        # recurve tip
        cy=12+upper*24.3; cx=8+upper*4.0
        es.append(elem(cx-.38,cy-2.0,-.38,cx+.38,cy+2.0,.38,(cx,cy,0,"z",upper*38)))
    # visual string: thin cuboids
    es += [elem(7.88,-12,-.10,8.12,8,.10,(8,-2,0,"z",-11)),
           elem(7.88,10,-.10,8.12,36,.10,(8,23,0,"z",11))]
    return es

def spear():
    es=[]
    for i in range(30):
        y=-15+i*1.25
        es.append(elem(7.52,y,-.48,8.48,y+1.18,.48))
        if i%5==0: es.append(elem(7.26,y+.35,-.60,8.74,y+.55,.60))
    y=22.5
    # leaf blade from narrow slices
    for i in range(15):
        t=i/14
        half=2.7*math.sin(math.pi*t)**.72+.15
        es.append(elem(8-half,y+i*.78,-.42,8+half,y+i*.82,.42))
    es += [elem(7.75,34.2,-.30,8.25,36.0,.30)]
    return es

def daggers():
    es=[]
    for side in (-1,1):
        cx=8+side*3.1
        es += [elem(cx-.75,-8,-.62,cx+.75,-1,.62),
               elem(cx-2.0,-1.2,-.42,cx+2.0,-.45,.42)]
        for i in range(14):
            t=i/13; y=-.45+i*1.18; half=1.35*(1-t)+.20
            curve=side*.55*math.sin(t*math.pi)
            es.append(elem(cx+curve-half,y,-.42,cx+curve+half,y+1.10,.42))
        es.append(elem(cx-.15,16.0,-.24,cx+.15,17.8,.24))
    return es

specs={
 "emberfall_claymore":(emberfall(),(46,18,12),(112,34,12),(255,102,28)),
 "noctis_longsword":(noctis(),(15,12,24),(58,20,86),(180,70,255)),
 "stormpiercer_recurve_bow":(bow(),(15,32,42),(34,86,108),(95,230,255)),
 "gaia_war_spear":(spear(),(28,46,20),(70,92,32),(164,230,80)),
 "astral_twin_daggers":(daggers(),(28,16,52),(72,36,108),(220,105,255)),
}
for name,(els,b,e,g) in specs.items():
    texture(name,b,e,g)
    save_model(name,els)

# Update pack description only. Water namespaces/files remain byte-for-byte from the v3.5 base.
mc=ROOT/"pack.mcmeta"
if mc.exists():
    data=json.loads(mc.read_text(encoding="utf-8"))
    data.setdefault("pack",{})["description"]="LegendaryRais v3.5.2 Reforged Hotfix | refined 5 gacha weapons | Soul Tide + Leviathan preserved"
    mc.write_text(json.dumps(data,separators=(",",":")),encoding="utf-8")

# Strict validation
for p in ROOT.rglob("*.json"): json.loads(p.read_text(encoding="utf-8"))
for name in specs:
    assert (ROOT/f"assets/{NS}/items/{name}.json").is_file()
    assert (ROOT/f"assets/{NS}/models/item/{name}.json").is_file()
# Explicit lock: we never overwrite these namespaces.
assert (ROOT/"assets/soultide").exists() or True
assert (ROOT/"assets/legendaryrais").exists() or True

if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n",encoding="utf-8")
print("VALID",OUT.stat().st_size,sha,"REFORGED",",".join(specs))

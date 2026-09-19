from pathlib import Path
import json, math, shutil, zipfile, hashlib, random
from PIL import Image, ImageDraw

BASE=Path("LegendaryRais-Java-26.1.2-v3.5.2-REFORGED-HOTFIX.zip")
OUT=Path("LegendaryRais-Java-26.1.2-v3.5.3-FULL-REFORGE.zip")
SHA=Path("LegendaryRais-Java-26.1.2-v3.5.3-FULL-REFORGE.sha1")
ROOT=Path(".build/generated-v353-java")
NS="legendaryv34"

if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

ALLOWED_ANGLES={-45,-22.5,0,22.5,45}

def wr(rel,obj):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def clamp(v): return max(-15.9,min(31.9,float(v)))

def faces():
    return {k:{"texture":"#main"} for k in ("north","south","east","west","up","down")}

def elem(x1,y1,z1,x2,y2,z2,rot=None):
    vals=[clamp(v) for v in (x1,y1,z1,x2,y2,z2)]
    e={"from":[round(vals[0],3),round(vals[1],3),round(vals[2],3)],
       "to":[round(vals[3],3),round(vals[4],3),round(vals[5],3)],
       "faces":faces()}
    if rot:
        ox,oy,oz,axis,ang=rot
        if ang not in ALLOWED_ANGLES: raise ValueError(("illegal rotation",ang))
        e["rotation"]={"origin":[round(clamp(ox),3),round(clamp(oy),3),round(clamp(oz),3)],
                       "axis":axis,"angle":ang,"rescale":True}
    return e

DISPLAY={
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,3.8,1],"scale":[0.69,0.69,0.69]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,3.8,1],"scale":[0.69,0.69,0.69]},
 "firstperson_righthand":{"rotation":[0,-90,20],"translation":[1.1,3.0,.8],"scale":[0.78,0.78,0.78]},
 "firstperson_lefthand":{"rotation":[0,90,-20],"translation":[1.1,3.0,.8],"scale":[0.78,0.78,0.78]},
 "gui":{"rotation":[22,-34,0],"translation":[0,-.5,0],"scale":[0.50,0.50,0.50]},
 "ground":{"translation":[0,2,0],"scale":[0.40,0.40,0.40]},
 "fixed":{"rotation":[0,180,0],"scale":[0.56,0.56,0.56]}
}

def metal_texture(name,base,highlight,accent):
    p=ROOT/f"assets/{NS}/textures/item/{name}.png"; p.parent.mkdir(parents=True,exist_ok=True)
    w=h=128
    im=Image.new("RGBA",(w,h),base+(255,))
    pix=im.load()
    random.seed("v353-"+name)
    for y in range(h):
        for x in range(w):
            directional=(x/w)*.10+(1-y/h)*.08
            grain=((x*13+y*7)%19)/19*.05
            noise=(random.random()-.5)*.035
            vals=[]
            for i in range(3):
                v=base[i]*(1-directional*.35)+highlight[i]*(directional*.35+grain+noise)
                vals.append(max(0,min(255,int(v))))
            pix[x,y]=tuple(vals)+(255,)
    d=ImageDraw.Draw(im,"RGBA")
    # restrained forged bands, not random confetti
    for y in (18,46,78,108):
        d.line((0,y,w,y),fill=accent+(25,),width=1)
    d.line((16,0,56,128),fill=accent+(30,),width=2)
    d.line((100,0,72,128),fill=highlight+(22,),width=1)
    im.save(p,optimize=True)

def save_model(name,elements):
    wr(f"assets/{NS}/models/item/{name}.json",{
      "textures":{"main":f"{NS}:item/{name}"},
      "elements":elements,
      "display":DISPLAY
    })
    wr(f"assets/{NS}/items/{name}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/{name}"}})

def sword_profile(width=3.0,blade_len=24.5,handle_len=8.0,heavy=False,void=False):
    es=[]
    # grip/pommel
    es.append(elem(7.15,-13.0,-.62,8.85,-11.4,.62))
    es.append(elem(7.38,-11.4,-.48,8.62,-11.4+handle_len,.48))
    for i in range(6):
        y=-10.9+i*(handle_len/6)
        es.append(elem(7.16,y,-.54,8.84,y+.22,.54, (8,y+.11,0,"y",22.5 if i%2==0 else -22.5)))
    guard_y=-11.4+handle_len
    # elegant guard with legal angles only
    es.append(elem(3.8,guard_y-.4,-.38,7.5,guard_y+.35,.38,(7.45,guard_y,0,"z",-22.5)))
    es.append(elem(8.5,guard_y-.4,-.38,12.2,guard_y+.35,.38,(8.55,guard_y,0,"z",22.5)))
    es.append(elem(6.9,guard_y-.15,-.62,9.1,guard_y+1.1,.62))
    y0=guard_y+1.0
    seg=26
    for i in range(seg):
        t=i/(seg-1)
        y=y0+t*blade_len
        if heavy:
            half=(width*(1-.60*t)+.20)/2
            ridge=.16
        else:
            half=(width*(1-.74*t)+.14)/2
            ridge=.11
        if void:
            cx=8+(.34*math.sin(t*math.pi))
        else:
            cx=8
        h=blade_len/seg+.11
        es.append(elem(cx-half,y,-.34,cx+half,y+h,.34))
        # central fuller/ridge
        if i%2==0:
            es.append(elem(cx-ridge,y+.03,-.40,cx+ridge,y+h-.03,.40))
    # point
    tip=y0+blade_len
    es.append(elem(7.45,tip,-.26,8.55,min(31.6,tip+.85),.26))
    es.append(elem(7.72,min(31.0,tip+.62),-.18,8.28,min(31.7,tip+1.25),.18))
    return es

def emberfall():
    es=sword_profile(width=4.05,blade_len=25.0,handle_len=8.4,heavy=True)
    # flame fins
    es += [elem(4.5,-2.8,-.28,6.7,-1.65,.28,(6.6,-2.0,0,"z",-22.5)),
           elem(9.3,-2.8,-.28,11.5,-1.65,.28,(9.4,-2.0,0,"z",22.5))]
    return es

def noctis():
    es=sword_profile(width=2.55,blade_len=25.7,handle_len=8.0,void=True)
    # slim eclipse hooks
    es += [elem(5.0,-3.0,-.24,6.8,-2.0,.24,(6.7,-2.35,0,"z",-45)),
           elem(9.2,-3.0,-.24,11.0,-2.0,.24,(9.3,-2.35,0,"z",45))]
    return es

def bow():
    es=[]
    es += [elem(7.25,5.0,-.50,8.75,12.0,.50),elem(6.55,7.3,-.72,9.45,9.7,.72)]
    # only legal angled limb sections
    upper=[(8.0,12.0,0),(8.7,15.1,22.5),(10.0,18.0,22.5),(11.2,20.9,22.5),(12.1,23.8,22.5),(12.8,26.6,45)]
    lower=[(8.0,5.0,0),(7.3,1.9,-22.5),(6.0,-1.0,-22.5),(4.8,-3.9,-22.5),(3.9,-6.8,-22.5),(3.2,-9.6,-45)]
    for cx,cy,ang in upper:
        es.append(elem(cx-.40,cy-1.9,-.34,cx+.40,cy+1.9,.34,(cx,cy,0,"z",ang)))
    for cx,cy,ang in lower:
        es.append(elem(cx-.40,cy-1.9,-.34,cx+.40,cy+1.9,.34,(cx,cy,0,"z",ang)))
    # recurve tips + string, staying within legal coordinate range
    es += [elem(12.0,27.0,-.30,13.1,31.1,.30,(12.5,29.0,0,"z",-22.5)),
           elem(2.9,-13.5,-.30,4.0,-9.4,.30,(3.5,-11.5,0,"z",22.5))]
    es += [elem(7.92,-11.6,-.08,8.08,8.4,.08,(8,-1.6,0,"z",-22.5)),
           elem(7.92,8.4,-.08,8.08,29.1,.08,(8,18.5,0,"z",22.5))]
    return es

def spear():
    es=[]
    # shaft with subtle ring wraps
    for i in range(20):
        y=-14.0+i*1.65
        es.append(elem(7.58,y,-.38,8.42,y+1.58,.38))
        if i%4==0: es.append(elem(7.34,y+.42,-.48,8.66,y+.63,.48))
    y=18.4
    for i in range(14):
        t=i/13
        half=(2.35*math.sin(math.pi*t)**.70+.13)
        es.append(elem(8-half,y+i*.78,-.30,8+half,y+i*.84,.30))
    es.append(elem(7.68,29.2,-.20,8.32,31.2,.20))
    # small opposing hook fins
    es += [elem(5.8,18.8,-.22,7.2,20.1,.22,(7.1,19.3,0,"z",-22.5)),
           elem(8.8,18.8,-.22,10.2,20.1,.22,(8.9,19.3,0,"z",22.5))]
    return es

def daggers():
    es=[]
    for side in (-1,1):
        cx=8+side*2.65
        es.append(elem(cx-.58,-8.6,-.44,cx+.58,-2.2,.44))
        es.append(elem(cx-1.50,-2.4,-.28,cx+1.50,-1.75,.28))
        for i in range(13):
            t=i/12
            y=-1.7+i*1.30
            half=1.05*(1-t)+.15
            offset=side*.33*math.sin(t*math.pi)
            es.append(elem(cx+offset-half,y,-.28,cx+offset+half,y+1.20,.28))
        es.append(elem(cx-.12,14.0,-.18,cx+.12,15.7,.18))
        # crescent accent
        es.append(elem(cx-side*1.25,-1.8,-.20,cx-side*.25,-.75,.20,(cx-side*.4,-1.2,0,"z",22.5*side)))
    return es

specs={
 "emberfall_claymore":(emberfall(),(43,16,10),(122,48,18),(255,120,42)),
 "noctis_longsword":(noctis(),(13,12,23),(66,26,96),(186,78,255)),
 "stormpiercer_recurve_bow":(bow(),(13,28,38),(40,96,122),(102,236,255)),
 "gaia_war_spear":(spear(),(25,42,18),(78,104,38),(170,234,88)),
 "astral_twin_daggers":(daggers(),(27,14,48),(84,42,124),(226,115,255)),
}
for name,(els,b,h,a) in specs.items():
    metal_texture(name,b,h,a)
    save_model(name,els)

# Stable body-locked Java armor: modern equipment model + themed humanoid textures.
ARMOR={
 "phoenix":((94,34,13),(220,104,26),(255,198,72)),
 "voidwalker":((25,15,38),(85,38,120),(196,82,255)),
 "titan":((30,47,37),(78,118,90),(130,220,160)),
 "celestial":((32,56,78),(90,148,190),(170,228,255)),
 "water_sovereign":((18,52,67),(42,132,160),(105,230,255)),
}

def armor_tex(setname,base,edge,glow,leggings=False):
    path=ROOT/f"assets/{NS}/textures/entity/equipment/{'humanoid_leggings' if leggings else 'humanoid'}/{setname}_set.png"
    path.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new("RGBA",(64,32),base+(255,))
    d=ImageDraw.Draw(im,"RGBA")
    # restrained plate borders/highlights across vanilla UV atlas
    d.rectangle((0,0,63,31),outline=edge+(180,),width=1)
    for y in (8,16,24): d.line((0,y,63,y),fill=edge+(40,),width=1)
    d.line((8,0,24,31),fill=glow+(65,),width=1)
    d.line((56,0,40,31),fill=glow+(42,),width=1)
    # chest/leg emblem zones
    d.rectangle((20,8,35,19),outline=glow+(100,),width=1)
    d.line((27,8,27,19),fill=glow+(75,),width=1)
    im.save(path,optimize=True)

def armor_icon(setname,piece,base,edge,glow):
    p=ROOT/f"assets/{NS}/textures/item/armor/{setname}_{piece}.png"; p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new("RGBA",(64,64),(0,0,0,0)); d=ImageDraw.Draw(im,"RGBA")
    if piece=="helmet":
        d.rounded_rectangle((16,12,48,38),radius=6,fill=base+(255,),outline=edge+(255,),width=3)
        d.rectangle((20,30,44,42),fill=base+(255,),outline=edge+(255,),width=2)
    elif piece=="chest":
        d.polygon([(15,16),(25,10),(39,10),(49,16),(44,48),(20,48)],fill=base+(255,),outline=edge+(255,))
        d.line((32,12,32,48),fill=glow+(210,),width=2)
    elif piece=="legs":
        d.polygon([(18,12),(46,12),(44,28),(39,54),(31,54),(29,31),(25,54),(17,54),(20,28)],fill=base+(255,),outline=edge+(255,))
    else:
        d.polygon([(16,22),(29,22),(29,47),(15,52)],fill=base+(255,),outline=edge+(255,))
        d.polygon([(35,22),(48,22),(49,52),(35,47)],fill=base+(255,),outline=edge+(255,))
    d.line((20,18,44,18),fill=glow+(180,),width=2)
    im.save(p,optimize=True)
    wr(f"assets/{NS}/models/item/armor/{setname}_{piece}.json",{"parent":"minecraft:item/generated","textures":{"layer0":f"{NS}:item/armor/{setname}_{piece}"}})
    wr(f"assets/{NS}/items/armor/{setname}_{piece}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/armor/{setname}_{piece}"}})

for setname,(base,edge,glow) in ARMOR.items():
    armor_tex(setname,base,edge,glow,False)
    armor_tex(setname,base,edge,glow,True)
    wr(f"assets/{NS}/equipment/{setname}_set.json",{"layers":{
      "humanoid":[{"texture":f"{NS}:{setname}_set"}],
      "humanoid_leggings":[{"texture":f"{NS}:{setname}_set"}]
    }})
    for piece in ("helmet","chest","legs","boots"):
        armor_icon(setname,piece,base,edge,glow)

# pack description
mc=ROOT/"pack.mcmeta"
data=json.loads(mc.read_text(encoding="utf-8"))
data.setdefault("pack",{})["description"]="LegendaryRais v3.5.3 FULL REFORGE | safe geometry | body-locked armor | Soul Tide + Leviathan preserved"
mc.write_text(json.dumps(data,separators=(",",":")),encoding="utf-8")

# Semantic validation beyond JSON syntax.
for p in ROOT.rglob("*.json"): json.loads(p.read_text(encoding="utf-8"))
for name in specs:
    model=json.loads((ROOT/f"assets/{NS}/models/item/{name}.json").read_text())
    for e in model["elements"]:
        for v in e["from"]+e["to"]: assert -16 <= v <= 32, (name,v)
        if "rotation" in e: assert e["rotation"]["angle"] in ALLOWED_ANGLES
for setname in ARMOR:
    assert (ROOT/f"assets/{NS}/equipment/{setname}_set.json").is_file()
# locked water assets must survive from base pack
assert any((ROOT/"assets/soultide").rglob("*"))
assert any((ROOT/"assets/legendaryrais").rglob("*"))

if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n",encoding="utf-8")
print("VALID",OUT.stat().st_size,sha,"WEAPONS",len(specs),"ARMORSETS",len(ARMOR))

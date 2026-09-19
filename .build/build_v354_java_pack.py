from pathlib import Path
import json, math, shutil, zipfile, hashlib, random
from PIL import Image, ImageDraw

BASE=Path("LegendaryRais-Java-26.1.2-v3.5.3-FULL-REFORGE.zip")
OUT=Path("LegendaryRais-Java-26.1.2-v3.5.4-VISUAL-INTEGRITY.zip")
SHA=Path("LegendaryRais-Java-26.1.2-v3.5.4-VISUAL-INTEGRITY.sha1")
ROOT=Path(".build/generated-v354-java")
NS="legendaryv34"

if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def wr(rel,obj):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def face_tex(key):
    return {k:{"texture":f"#{key}"} for k in ("north","south","east","west","up","down")}

def elem(fr,to,key="metal",rot=None):
    e={"from":[round(float(x),3) for x in fr],"to":[round(float(x),3) for x in to],"faces":face_tex(key)}
    if rot:
        ox,oy,oz,axis,angle=rot
        assert angle in (-45,-22.5,0,22.5,45)
        e["rotation"]={"origin":[ox,oy,oz],"axis":axis,"angle":angle,"rescale":True}
    return e

DISPLAY={
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,3.5,1],"scale":[0.67,0.67,0.67]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,3.5,1],"scale":[0.67,0.67,0.67]},
 "firstperson_righthand":{"rotation":[0,-90,18],"translation":[1.0,3.0,.7],"scale":[0.76,0.76,0.76]},
 "firstperson_lefthand":{"rotation":[0,90,-18],"translation":[1.0,3.0,.7],"scale":[0.76,0.76,0.76]},
 "gui":{"rotation":[22,-34,0],"translation":[0,-.5,0],"scale":[0.49,0.49,0.49]},
 "ground":{"translation":[0,2,0],"scale":[0.39,0.39,0.39]},
 "fixed":{"rotation":[0,180,0],"scale":[0.55,0.55,0.55]}
}

THEMES={
 "emberfall_claymore":{"metal":((76,35,20),(162,74,28)),"grip":((30,19,15),(74,48,33)),"accent":((255,98,24),(255,198,80))},
 "noctis_longsword":{"metal":((24,21,34),(72,55,96)),"grip":((20,15,22),(52,38,58)),"accent":((137,62,212),(227,130,255))},
 "stormpiercer_recurve_bow":{"metal":((22,48,62),(58,111,135)),"grip":((31,25,20),(82,62,45)),"accent":((69,190,230),(185,250,255))},
 "gaia_war_spear":{"metal":((42,58,32),(93,119,57)),"grip":((52,35,22),(104,73,42)),"accent":((126,198,77),(210,244,120))},
 "astral_twin_daggers":{"metal":((35,25,54),(95,62,128)),"grip":((26,20,28),(61,45,66)),"accent":((175,75,236),(245,150,255))}
}

def make_material_texture(path, base, hi, accent=False):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new("RGBA",(64,64),base+(255,))
    px=im.load(); random.seed(path)
    for y in range(64):
        for x in range(64):
            band=((x+y)%11)/11
            n=(random.random()-.5)*8
            vals=[]
            for i in range(3):
                v=base[i]*(.84+.10*band)+hi[i]*(.08+.08*(1-y/63))+n
                vals.append(max(0,min(255,int(v))))
            px[x,y]=tuple(vals)+(255,)
    d=ImageDraw.Draw(im,"RGBA")
    if accent:
        for y in range(6,64,12):
            d.line((4,y,59,y),fill=hi+(90,),width=1)
        d.line((31,3,31,60),fill=hi+(80,),width=1)
    else:
        for y in (8,24,40,56):
            d.line((2,y,61,y),fill=hi+(24,),width=1)
    im.save(p,optimize=True)

def save_weapon(name,elements):
    theme=THEMES[name]
    for key,(base,hi) in theme.items():
        make_material_texture(f"assets/{NS}/textures/item/v354/{name}_{key}.png",base,hi,key=="accent")
    tex={key:f"{NS}:item/v354/{name}_{key}" for key in ("metal","grip","accent")}
    wr(f"assets/{NS}/models/item/{name}.json",{"textures":tex,"elements":elements,"display":DISPLAY})
    wr(f"assets/{NS}/items/{name}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/{name}"}})

def common_grip(y0=-13,y1=-3.5):
    out=[elem((7.18,y0,-.55),(8.82,y0+1.5,.55),"accent"),
         elem((7.38,y0+1.5,-.48),(8.62,y1,.48),"grip")]
    for y in (y0+2.4,y0+4.7,y0+7.0):
        out.append(elem((7.15,y,-.56),(8.85,y+.22,.56),"accent"))
    return out

def emberfall():
    e=common_grip(-13,-3.3)
    e += [
      elem((4.0,-3.5,-.34),(7.4,-2.75,.34),"accent",(7.3,-3.1,0,"z",-22.5)),
      elem((8.6,-3.5,-.34),(12.0,-2.75,.34),"accent",(8.7,-3.1,0,"z",22.5)),
      elem((6.9,-3.1,-.62),(9.1,-1.9,.62),"metal"),
      elem((6.2,-1.9,-.42),(9.8,23.7,.42),"metal"),
      elem((6.45,-1.6,-.49),(6.85,23.1,.49),"accent"),
      elem((9.15,-1.6,-.49),(9.55,23.1,.49),"accent"),
      elem((6.65,23.7,-.36),(9.35,27.2,.36),"metal"),
      elem((7.15,27.2,-.26),(8.85,29.4,.26),"metal"),
      elem((7.65,29.4,-.16),(8.35,30.8,.16),"accent")
    ]
    return e

def noctis():
    e=common_grip(-13,-3.4)
    e += [
      elem((4.9,-3.55,-.26),(7.25,-2.9,.26),"accent",(7.15,-3.2,0,"z",-45)),
      elem((8.75,-3.55,-.26),(11.1,-2.9,.26),"accent",(8.85,-3.2,0,"z",45)),
      elem((7.05,-3.0,-.52),(8.95,-1.75,.52),"metal"),
      elem((6.95,-1.75,-.31),(9.05,25.7,.31),"metal"),
      elem((7.08,-1.5,-.39),(7.34,25.1,.39),"accent"),
      elem((8.66,-1.5,-.39),(8.92,25.1,.39),"accent"),
      elem((7.25,25.7,-.25),(8.75,28.2,.25),"metal"),
      elem((7.65,28.2,-.16),(8.35,30.5,.16),"accent")
    ]
    return e

def bow():
    e=[
      elem((7.2,5.0,-.55),(8.8,11.6,.55),"grip"),
      elem((6.4,7.0,-.80),(9.6,9.7,.80),"accent")
    ]
    segs=[(8.0,12.0,0),(8.8,15.0,22.5),(10.0,18.0,22.5),(11.1,21.0,22.5),(12.0,24.0,22.5),(12.7,27.0,45),
          (8.0,4.6,0),(7.2,1.5,-22.5),(6.0,-1.5,-22.5),(4.9,-4.5,-22.5),(4.0,-7.5,-22.5),(3.3,-10.5,-45)]
    for cx,cy,ang in segs:
        e.append(elem((cx-.36,cy-1.75,-.32),(cx+.36,cy+1.75,.32),"metal",(cx,cy,0,"z",ang)))
    e += [
      elem((7.92,-11.8,-.07),(8.08,8.0,.07),"accent",(8,-2,0,"z",-22.5)),
      elem((7.92,9.2,-.07),(8.08,30.3,.07),"accent",(8,20,0,"z",22.5))
    ]
    return e

def gaia():
    e=[
      elem((7.56,-15.0,-.38),(8.44,20.1,.38),"grip"),
      elem((7.30,-12.0,-.47),(8.70,-11.72,.47),"accent"),
      elem((7.30,-3.0,-.47),(8.70,-2.72,.47),"accent"),
      elem((7.30,6.0,-.47),(8.70,6.28,.47),"accent"),
      elem((7.30,15.0,-.47),(8.70,15.28,.47),"accent"),
      elem((7.3,19.6,-.55),(8.7,21.0,.55),"metal"),
      elem((7.15,20.8,-.34),(8.85,28.0,.34),"metal"),
      elem((6.15,21.3,-.28),(7.45,25.7,.28),"metal",(7.3,23.4,0,"z",-22.5)),
      elem((8.55,21.3,-.28),(9.85,25.7,.28),"metal",(8.7,23.4,0,"z",22.5)),
      elem((7.55,27.8,-.22),(8.45,30.8,.22),"accent")
    ]
    return e

def astral():
    e=[]
    for side in (-1,1):
        cx=8+side*2.55
        e += [
          elem((cx-.52,-9.4,-.42),(cx+.52,-2.8,.42),"grip"),
          elem((cx-1.35,-3.0,-.25),(cx+1.35,-2.35,.25),"accent"),
          elem((cx-.78,-2.35,-.28),(cx+.78,12.0,.28),"metal"),
          elem((cx-side*.95,4.0,-.20),(cx-side*.22,9.5,.20),"accent",(cx-side*.4,6.7,0,"z",22.5*side)),
          elem((cx-.48,12.0,-.20),(cx+.48,14.4,.20),"metal"),
          elem((cx-.18,14.4,-.12),(cx+.18,16.1,.12),"accent")
        ]
    return e

for n,fn in {
 "emberfall_claymore":emberfall,
 "noctis_longsword":noctis,
 "stormpiercer_recurve_bow":bow,
 "gaia_war_spear":gaia,
 "astral_twin_daggers":astral
}.items():
    save_weapon(n,fn())

ARMOR={
 "phoenix":((58,20,10),(126,49,16),(255,126,34)),
 "voidwalker":((20,14,31),(55,32,82),(181,80,240)),
 "titan":((27,42,31),(62,82,49),(142,188,96)),
 "celestial":((27,46,64),(67,105,137),(150,214,246)),
 "water_sovereign":((15,46,61),(35,94,117),(82,202,230))
}
PIECES=("helmet","chest","legs","boots")

def armor_pattern(setname,base,mid,glow,leggings=False):
    p=ROOT/f"assets/{NS}/textures/entity/equipment/{'humanoid_leggings' if leggings else 'humanoid'}/{setname}_set.png"
    p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new("RGBA",(64,32),base+(255,)); px=im.load(); random.seed("armor-"+setname+str(leggings))
    for y in range(32):
        for x in range(64):
            checker=((x//4+y//4)%2)*5
            noise=random.randint(-3,3)
            c=tuple(max(0,min(255,base[i]+checker+noise)) for i in range(3))
            px[x,y]=c+(255,)
    d=ImageDraw.Draw(im,"RGBA")
    # small plate/rune pattern; intentionally tile-scale so UV seams do not create giant shapes
    for y in range(3,32,8):
        d.line((1,y,62,y),fill=mid+(58,),width=1)
    for x in range(5,64,12):
        d.line((x,1,x,30),fill=mid+(34,),width=1)
    if setname=="phoenix":
        for x in (8,24,40,56):
            d.line((x,4,x-2,10),fill=glow+(135,),width=1); d.line((x-2,10,x+2,14),fill=glow+(90,),width=1)
    elif setname=="voidwalker":
        for x,y in ((7,6),(19,19),(33,8),(48,23),(58,12)):
            d.point((x,y),fill=glow+(210,)); d.point((x+1,y),fill=glow+(120,))
    elif setname=="titan":
        for x in range(4,64,16):
            d.rectangle((x,6,x+8,12),outline=glow+(70,),width=1)
    elif setname=="celestial":
        for x in range(6,64,14):
            d.line((x,5,x+3,8),fill=glow+(120,),width=1); d.line((x+3,8,x,11),fill=glow+(80,),width=1)
    else:
        for x in range(0,64,16):
            d.arc((x,8,x+14,20),0,180,fill=glow+(115,),width=1)
    im.save(p,optimize=True)

def armor_icon(setname,piece,base,mid,glow):
    p=ROOT/f"assets/{NS}/textures/item/armor/{setname}_{piece}.png"; p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new("RGBA",(32,32),(0,0,0,0)); d=ImageDraw.Draw(im,"RGBA")
    edge=mid+(255,); hi=glow+(225,); fill=base+(255,)
    if piece=="helmet":
        d.rounded_rectangle((7,5,24,18),radius=3,fill=fill,outline=edge,width=2); d.rectangle((9,16,22,22),fill=fill,outline=edge,width=1)
    elif piece=="chest":
        d.polygon([(6,8),(11,5),(21,5),(26,8),(23,25),(9,25)],fill=fill,outline=edge); d.line((16,7,16,24),fill=hi,width=1)
    elif piece=="legs":
        d.polygon([(8,5),(24,5),(23,14),(20,27),(16,27),(15,15),(12,27),(8,27),(9,14)],fill=fill,outline=edge)
    else:
        d.polygon([(7,10),(14,10),(14,24),(6,27)],fill=fill,outline=edge); d.polygon([(18,10),(25,10),(26,27),(18,24)],fill=fill,outline=edge)
    d.line((10,8,22,8),fill=hi,width=1)
    im.save(p,optimize=True)
    wr(f"assets/{NS}/models/item/armor/{setname}_{piece}.json",{"parent":"minecraft:item/generated","textures":{"layer0":f"{NS}:item/armor/{setname}_{piece}"}})
    wr(f"assets/{NS}/items/armor/{setname}_{piece}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/armor/{setname}_{piece}"}})

for setname,(base,mid,glow) in ARMOR.items():
    armor_pattern(setname,base,mid,glow,False)
    armor_pattern(setname,base,mid,glow,True)
    wr(f"assets/{NS}/equipment/{setname}_set.json",{"layers":{
      "humanoid":[{"texture":f"{NS}:{setname}_set"}],
      "humanoid_leggings":[{"texture":f"{NS}:{setname}_set"}]
    }})
    for piece in PIECES: armor_icon(setname,piece,base,mid,glow)

# semantic audit
for p in ROOT.rglob("*.json"): json.loads(p.read_text(encoding="utf-8"))
for name in THEMES:
    d=json.loads((ROOT/f"assets/{NS}/models/item/{name}.json").read_text())
    assert len(d["elements"]) <= 40
    for e in d["elements"]:
        for v in e["from"]+e["to"]: assert -16 <= v <= 32, (name,v)
        if "rotation" in e: assert e["rotation"]["angle"] in (-45,-22.5,0,22.5,45)
for setname in ARMOR:
    assert (ROOT/f"assets/{NS}/equipment/{setname}_set.json").is_file()
    assert (ROOT/f"assets/{NS}/textures/entity/equipment/humanoid/{setname}_set.png").is_file()
    assert (ROOT/f"assets/{NS}/textures/entity/equipment/humanoid_leggings/{setname}_set.png").is_file()

# preserve accepted water weapons
assert any((ROOT/"assets/soultide").rglob("*"))
assert any((ROOT/"assets/legendaryrais").rglob("*"))

mc=ROOT/"pack.mcmeta"; data=json.loads(mc.read_text())
data["pack"]["description"]="LegendaryRais v3.5.4 VISUAL INTEGRITY | cleaner weapons | native armor textures | Soul Tide + Leviathan preserved"
mc.write_text(json.dumps(data,separators=(",",":")))

if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n")
print("VALID",OUT.stat().st_size,sha)

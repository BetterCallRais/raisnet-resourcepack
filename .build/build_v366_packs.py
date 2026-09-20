from pathlib import Path
import json, math, random, shutil, zipfile, hashlib
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

JBASE=Path("LegendaryRais-Java-26.1.2-v3.6.5-WEAPON-RIG-ARMOR-SKILL.zip")
BBASE=Path("LegendaryRais-Bedrock-v3.6.5-WEAPON-RIG-ARMOR-SKILL.mcpack")
MBASE=Path("LegendaryRais-Geyser-v3.6.5-mappings.json")
JOUT=Path("LegendaryRais-Java-26.1.2-v3.6.6-MYTHIC-ART-QA30.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.6.6-MYTHIC-ART-QA30.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.6.6-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.6.6-MYTHIC-ART-QA30.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.6.6-MYTHIC-ART-QA30.sha1")
REPORT=Path("LegendaryRais-v3.6.6-QA30.txt")
ROOT=Path(".build/generated-v366"); JR=ROOT/"java"; BR=ROOT/"bedrock"; NS="legendaryv34"

shutil.rmtree(ROOT,ignore_errors=True);JR.mkdir(parents=True);BR.mkdir(parents=True)
with zipfile.ZipFile(JBASE) as z:z.extractall(JR)
with zipfile.ZipFile(BBASE) as z:z.extractall(BR)

W={
"emberfall_claymore":{"base":(44,10,5),"mid":(172,47,12),"glow":(255,151,35),"kind":"fire"},
"noctis_longsword":{"base":(10,7,22),"mid":(72,25,116),"glow":(215,84,255),"kind":"void"},
"stormpiercer_recurve_bow":{"base":(7,28,44),"mid":(30,127,168),"glow":(83,240,255),"kind":"electro"},
"gaia_war_spear":{"base":(17,42,43),"mid":(59,157,140),"glow":(199,255,230),"kind":"wind"},
"astral_frost_greataxe":{"base":(12,39,67),"mid":(65,166,216),"glow":(222,253,255),"kind":"ice"},
}
SETS={
"phoenix":((45,11,5),(160,43,11),(255,153,35)),
"voidwalker":((11,7,24),(67,28,105),(207,80,255)),
"titan":((20,35,23),(77,105,52),(185,224,113)),
"celestial":((16,37,58),(72,125,165),(205,241,255)),
"water_sovereign":((5,38,59),(31,116,144),(91,231,252)),
}

def wr(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def tex(size,base,mid,glow,kind,seed,alpha=True):
    rnd=random.Random(seed);im=Image.new("RGBA",(size,size),(0,0,0,0 if alpha else 255));px=im.load()
    for y in range(size):
        for x in range(size):
            nx=x/(size-1);ny=y/(size-1)
            radial=max(0,1-math.dist((nx,ny),(.45,.42))/.8)
            brushed=.055*math.sin((x*.29+y*.07))+ .025*math.sin(y*.51)
            t=max(.03,min(.62,.13+.22*nx+.18*(1-ny)+.13*radial+brushed+rnd.uniform(-.012,.012)))
            c=tuple(max(0,min(255,int(base[i]*(1-t)+mid[i]*t))) for i in range(3))
            px[x,y]=c+(255,)
    d=ImageDraw.Draw(im,"RGBA");w=max(1,size//128)
    # edge/frame gives a crafted material rather than procedural noise.
    d.rectangle((2*w,2*w,size-2*w-1,size-2*w-1),outline=mid+(85,),width=w)
    if kind=="fire":
        for cx in (.18,.38,.62,.82):
            d.polygon([(size*cx,size*.90),(size*(cx-.055),size*.66),(size*(cx+.02),size*.51),(size*(cx-.015),size*.31)],outline=glow+(155,))
    elif kind=="void":
        d.arc((size*.08,size*.10,size*.92,size*.90),204,340,fill=glow+(145,),width=2*w)
        d.arc((size*.18,size*.20,size*.82,size*.82),25,158,fill=mid+(120,),width=w)
        for x,y in ((.16,.26),(.34,.74),(.68,.30),(.84,.72)):d.ellipse((size*x-2*w,size*y-2*w,size*x+2*w,size*y+2*w),fill=glow+(200,))
    elif kind=="electro":
        for off in (0,.15,-.13):
            d.line((size*(.67+off),size*.04,size*(.44+off),size*.36,size*(.56+off),size*.40,size*(.31+off),size*.94),fill=glow+(170,),width=2*w)
    elif kind=="wind":
        for yy in (.22,.46,.70):
            d.arc((size*.05,size*(yy-.14),size*.95,size*(yy+.16)),192,346,fill=glow+(120,),width=2*w)
        d.line((size*.12,size*.86,size*.88,size*.14),fill=mid+(70,),width=w)
    elif kind=="ice":
        for a in range(0,360,45):
            x=size*.5+math.cos(math.radians(a))*size*.37;y=size*.5+math.sin(math.radians(a))*size*.37
            d.line((size*.5,size*.5,x,y),fill=glow+(145,),width=2*w)
        for x in (.24,.5,.76):
            d.polygon([(size*x,size*.07),(size*(x+.065),size*.30),(size*x,size*.46),(size*(x-.05),size*.28)],outline=glow+(165,))
    return im.filter(ImageFilter.UnsharpMask(radius=max(1,size//128),percent=185,threshold=2))

def faces(key):
    return {f:{"texture":"#"+key} for f in ("north","south","east","west","up","down")}

def E(fr,to,key="metal",rot=None):
    e={"from":[round(v,3) for v in fr],"to":[round(v,3) for v in to],"faces":faces(key)}
    if rot:
        origin,axis,ang=rot
        e["rotation"]={"origin":[round(v,3) for v in origin],"axis":axis,"angle":ang,"rescale":True}
    return e

# Curated Java weapon geometry, centered x/z=8 and hand grip near y=4.
def java_geometry(n):
    if n=="emberfall_claymore":
        e=[E((7.25,-1,7.3),(8.75,7.2,8.7),"grip"),E((6.7,-1.3,7.15),(9.3,.2,8.85),"accent")]
        for y in (1.2,3.4,5.6):e.append(E((7.0,y,7.15),(9.0,y+.30,8.85),"accent"))
        e += [
          E((3.1,7.0,7.45),(7.35,8.1,8.55),"accent",([7.15,7.55,8],"z",-22.5)),
          E((8.65,7.0,7.45),(12.9,8.1,8.55),"accent",([8.85,7.55,8],"z",22.5)),
          E((5.2,7.65,7.58),(7.0,9.4,8.42),"metal",([6.8,8.0,8],"z",-22.5)),
          E((9.0,7.65,7.58),(10.8,9.4,8.42),"metal",([9.2,8.0,8],"z",22.5)),
        ]
        for y,w in [(8.2,4.5),(12.7,4.2),(17.2,3.8),(21.7,3.4),(26.2,2.8)]:
            e += [E((8-w/2,y,7.35),(8+w/2,y+4.3,8.65),"metal"),
                  E((7.80,y+.15,7.18),(8.20,y+4.15,8.82),"accent")]
        e += [E((7.2,30.5,7.55),(8.8,32,8.45),"metal")]
        return e
    if n=="noctis_longsword":
        e=[E((7.35,-.5,7.4),(8.65,7.2,8.6),"grip"),E((6.85,-.8,7.15),(9.15,.1,8.85),"accent")]
        e += [E((4.0,6.9,7.55),(7.5,7.8,8.45),"accent",([7.3,7.3,8],"z",-45)),
              E((8.5,6.9,7.55),(12.0,7.8,8.45),"accent",([8.7,7.3,8],"z",45))]
        for y,w in [(8,2.9),(12.6,2.65),(17.2,2.3),(21.8,1.95),(26.4,1.55)]:
            e += [E((8-w/2,y,7.48),(8+w/2,y+4.4,8.52),"metal"),
                  E((7.88,y+.15,7.28),(8.12,y+4.25,8.72),"accent")]
        e += [E((7.55,30.4,7.65),(8.45,32,8.35),"accent")]
        return e
    if n=="stormpiercer_recurve_bow":
        e=[E((7.25,3.0,7.25),(8.75,10.0,8.75),"grip"),E((6.25,6.1,7.1),(9.75,8.9,8.9),"accent")]
        # top and lower recurve limbs
        for cx,cy,ang in [(8,10.3,0),(8.8,13.1,22.5),(10.2,16.2,22.5),(11.6,19.3,22.5),(12.9,22.4,22.5),(13.8,25.2,45),
                          (8,2.7,0),(7.2,-.1,-22.5),(5.8,-3.2,-22.5),(4.4,-6.3,-22.5),(3.1,-9.4,-22.5),(2.2,-12.2,-45)]:
            e.append(E((cx-.48,cy-1.65,7.52),(cx+.48,cy+1.65,8.48),"metal",([cx,cy,8],"z",ang)))
        # visible string in side profile
        e += [E((7.93,-12.0,7.92),(8.07,7.0,8.08),"accent",([8,-2,8],"z",-22.5)),
              E((7.93,8.0,7.92),(8.07,27.0,8.08),"accent",([8,18,8],"z",22.5)),
              E((7.55,7.55,7.42),(8.45,8.45,8.58),"accent")]
        return e
    if n=="gaia_war_spear":
        e=[E((7.52,-5,7.5),(8.48,23.5,8.5),"grip")]
        for y in (-2,3,8,13,18):e.append(E((7.20,y,7.36),(8.80,y+.30,8.64),"accent"))
        e += [
          E((6.95,22.8,7.38),(9.05,27.6,8.62),"metal"),
          E((5.1,23.7,7.55),(7.3,29.3,8.45),"accent",([7.0,26.0,8],"z",-22.5)),
          E((8.7,23.7,7.55),(10.9,29.3,8.45),"accent",([9.0,26.0,8],"z",22.5)),
          E((6.35,27.0,7.48),(9.65,31.0,8.52),"metal"),
          E((7.30,30.4,7.62),(8.70,32.0,8.38),"accent")
        ]
        return e
    # frost great axe
    e=[E((7.28,-3,7.30),(8.72,20.5,8.70),"grip")]
    for y in (-1,3,7,11,15):e.append(E((6.98,y,7.18),(9.02,y+.32,8.82),"accent"))
    e += [
      E((6.6,19.0,7.05),(9.4,22.6,8.95),"accent"),
      E((3.8,21.0,7.28),(12.2,23.6,8.72),"metal"),
      E((.8,22.0,7.38),(6.0,26.0,8.62),"metal",([5.5,23.5,8],"z",-22.5)),
      E((-1.5,24.5,7.46),(4.7,29.5,8.54),"metal",([4.2,26.2,8],"z",-45)),
      E((10.0,21.8,7.42),(14.2,25.4,8.58),"metal",([10.2,23.3,8],"z",22.5)),
      E((6.75,22.0,6.95),(9.25,27.0,9.05),"accent"),
      E((7.35,26.6,7.42),(8.65,31.2,8.58),"accent")
    ]
    return e

TRANS={
"emberfall_claymore":{"thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,3.35,0],"scale":[.59]*3},"thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,3.35,0],"scale":[.59]*3},"firstperson_righthand":{"rotation":[0,-90,24],"translation":[1.05,3.15,.25],"scale":[.67]*3},"firstperson_lefthand":{"rotation":[0,90,-24],"translation":[1.05,3.15,.25],"scale":[.67]*3}},
"noctis_longsword":{"thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,3.45,0],"scale":[.62]*3},"thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,3.45,0],"scale":[.62]*3},"firstperson_righthand":{"rotation":[0,-90,23],"translation":[1.0,3.25,.22],"scale":[.69]*3},"firstperson_lefthand":{"rotation":[0,90,-23],"translation":[1.0,3.25,.22],"scale":[.69]*3}},
"stormpiercer_recurve_bow":{"thirdperson_righthand":{"rotation":[-6,-90,4],"translation":[0,2.0,0],"scale":[.60]*3},"thirdperson_lefthand":{"rotation":[-6,90,-4],"translation":[0,2.0,0],"scale":[.60]*3},"firstperson_righthand":{"rotation":[-5,-91,3],"translation":[.95,1.75,.35],"scale":[.71]*3},"firstperson_lefthand":{"rotation":[-5,91,-3],"translation":[.95,1.75,.35],"scale":[.71]*3}},
"gaia_war_spear":{"thirdperson_righthand":{"rotation":[0,-90,58],"translation":[0,2.35,0],"scale":[.46]*3},"thirdperson_lefthand":{"rotation":[0,90,-58],"translation":[0,2.35,0],"scale":[.46]*3},"firstperson_righthand":{"rotation":[0,-90,28],"translation":[.95,2.15,.25],"scale":[.52]*3},"firstperson_lefthand":{"rotation":[0,90,-28],"translation":[.95,2.15,.25],"scale":[.52]*3}},
"astral_frost_greataxe":{"thirdperson_righthand":{"rotation":[0,-90,53],"translation":[0,2.85,0],"scale":[.53]*3},"thirdperson_lefthand":{"rotation":[0,90,-53],"translation":[0,2.85,0],"scale":[.53]*3},"firstperson_righthand":{"rotation":[0,-90,21],"translation":[.95,2.75,.28],"scale":[.59]*3},"firstperson_lefthand":{"rotation":[0,90,-21],"translation":[.95,2.75,.28],"scale":[.59]*3}},
}
COMMON={"gui":{"rotation":[25,-35,0],"scale":[.53]*3},"ground":{"translation":[0,2,0],"scale":[.38]*3},"fixed":{"rotation":[0,180,0],"scale":[.57]*3}}

# Generate Java textures/models.
for n,v in W.items():
    for key,(a,b,k) in {"metal":(v["base"],v["mid"],v["kind"]),"grip":((20,15,13),(92,62,40),"neutral"),"accent":(v["mid"],v["glow"],v["kind"])}.items():
        im=tex(256,a,b,v["glow"],k,"v366-"+n+"-"+key)
        p=JR/f"assets/{NS}/textures/item/v366/{n}_{key}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
    obj={"textures":{"metal":f"{NS}:item/v366/{n}_metal","grip":f"{NS}:item/v366/{n}_grip","accent":f"{NS}:item/v366/{n}_accent"},"elements":java_geometry(n),"display":dict(COMMON),"gui_light":"front"}
    obj["display"].update(TRANS[n])
    wr(JR/f"assets/{NS}/models/item/{n}.json",obj)

# Stormpiercer draw states for Java: same model with increasing limb flex.
base=json.loads((JR/f"assets/{NS}/models/item/stormpiercer_recurve_bow.json").read_text())
for idx,delta in enumerate((0.0,1.2,2.2)):
    d=json.loads(json.dumps(base))
    if delta:
        for e in d["elements"]:
            # Shift only outer limb elements toward center for a visible draw state.
            if e["from"][0] < 6.0:
                e["from"][0]+=delta;e["to"][0]+=delta
            elif e["to"][0] > 10.0:
                e["from"][0]-=delta;e["to"][0]-=delta
    wr(JR/f"assets/{NS}/models/item/stormpiercer_recurve_bow_pulling_{idx}.json",d)
wr(JR/f"assets/{NS}/items/stormpiercer_recurve_bow.json",{
 "model":{"type":"minecraft:condition","property":"minecraft:using_item",
   "on_false":{"type":"minecraft:model","model":f"{NS}:item/stormpiercer_recurve_bow"},
   "on_true":{"type":"minecraft:range_dispatch","property":"minecraft:use_duration","scale":0.05,
     "entries":[
       {"threshold":0.65,"model":{"type":"minecraft:model","model":f"{NS}:item/stormpiercer_recurve_bow_pulling_1"}},
       {"threshold":0.9,"model":{"type":"minecraft:model","model":f"{NS}:item/stormpiercer_recurve_bow_pulling_2"}}
     ],
     "fallback":{"type":"minecraft:model","model":f"{NS}:item/stormpiercer_recurve_bow_pulling_0"}
   }
 }
})

# ------------------------------------------------------------------
# Java armor: two-layer native equipment art for depth without unstable display entities.
# ------------------------------------------------------------------
def armor_base(setn,size=(64,32)):
    base,mid,glow=SETS[setn];w,h=size;im=Image.new("RGBA",size,base+(255,));d=ImageDraw.Draw(im,"RGBA")
    # tiled metal panels / seam work
    for x in range(0,w,8):d.line((x,0,x,h),fill=mid+(45,),width=1)
    for y in range(0,h,8):d.line((0,y,w,y),fill=mid+(28,),width=1)
    d.rectangle((1,1,w-2,h-2),outline=mid+(80,))
    return im

def armor_accent(setn,size=(64,32),open_face=False):
    base,mid,glow=SETS[setn];im=Image.new("RGBA",size,(0,0,0,0));d=ImageDraw.Draw(im,"RGBA")
    # helmet quadrants + chest/leg motifs designed to remain visible on vanilla UV.
    if setn=="phoenix":
        col=glow+(220,)
        for x in (8,24,40,56):d.line((x,2,x-2,7,x+1,11),fill=col,width=1)
        d.arc((18,17,32,30),195,345,fill=col,width=1);d.arc((36,17,50,30),195,345,fill=col,width=1)
    elif setn=="voidwalker":
        col=glow+(210,);d.arc((2,1,17,14),205,338,fill=col,width=1);d.arc((21,16,37,31),20,160,fill=col,width=1)
        for x,y in ((10,5),(27,23),(44,7),(57,24)):d.point((x,y),fill=col)
    elif setn=="titan":
        col=glow+(200,)
        for x in (3,20,37,54):d.rectangle((x,3,min(x+7,63),5),fill=col)
        d.rectangle((19,18,31,20),fill=col);d.rectangle((37,18,49,20),fill=col)
    elif setn=="celestial":
        col=glow+(230,)
        for x,y in ((8,4),(22,10),(28,23),(43,5),(55,21)):
            d.line((x-1,y,x+1,y),fill=col);d.line((x,y-1,x,y+1),fill=col)
        d.arc((18,17,31,30),200,340,fill=col,width=1)
    else:
        col=glow+(220,)
        for x in (4,20,36,52):d.arc((x,3,min(x+10,63),12),0,180,fill=col,width=1)
        d.arc((19,18,32,29),185,355,fill=col,width=1);d.arc((37,18,50,29),185,355,fill=col,width=1)
    if open_face:
        # transparent face opening, preserve brow trim
        for y in range(10,16):
            for x in range(8,16):im.putpixel((x,y),(0,0,0,0))
    return im

for s in SETS:
    for sub in ("humanoid","humanoid_leggings"):
        base=armor_base(s);accent=armor_accent(s)
        pb=JR/f"assets/{NS}/textures/entity/equipment/{sub}/{s}_v366_base.png";pa=JR/f"assets/{NS}/textures/entity/equipment/{sub}/{s}_v366_accent.png"
        pb.parent.mkdir(parents=True,exist_ok=True);base.save(pb,optimize=True);accent.save(pa,optimize=True)
    # equipment full set uses two layers.
    wr(JR/f"assets/{NS}/equipment/{s}_set.json",{"layers":{
      "humanoid":[{"texture":f"{NS}:{s}_v366_base"},{"texture":f"{NS}:{s}_v366_accent"}],
      "humanoid_leggings":[{"texture":f"{NS}:{s}_v366_base"},{"texture":f"{NS}:{s}_v366_accent"}]
    }})
    # closed/open helmet mode also two layers.
    wr(JR/f"assets/{NS}/equipment/{s}_helmet_closed.json",{"layers":{"humanoid":[{"texture":f"{NS}:{s}_v366_base"},{"texture":f"{NS}:{s}_v366_accent"}]}})
    openacc=armor_accent(s,open_face=True);op=JR/f"assets/{NS}/textures/entity/equipment/humanoid/{s}_v366_open_accent.png";openacc.save(op,optimize=True)
    # open mode uses transparent base front region too.
    openbase=armor_base(s)
    for y in range(10,16):
        for x in range(8,16):openbase.putpixel((x,y),(0,0,0,0))
    obp=JR/f"assets/{NS}/textures/entity/equipment/humanoid/{s}_v366_open_base.png";openbase.save(obp,optimize=True)
    wr(JR/f"assets/{NS}/equipment/{s}_helmet_open.json",{"layers":{"humanoid":[{"texture":f"{NS}:{s}_v366_open_base"},{"texture":f"{NS}:{s}_v366_open_accent"}]}})

# ------------------------------------------------------------------
# Bedrock weapons: rebuild low-cube silhouette to match Java.
# ------------------------------------------------------------------
def C(origin,size,uv=(0,0),pivot=None,rotation=None):
    c={"origin":[round(x,3) for x in origin],"size":[round(x,3) for x in size],"uv":list(uv)}
    if pivot is not None:c["pivot"]=list(pivot)
    if rotation is not None:c["rotation"]=list(rotation)
    return c

def bed_geom(n):
    if n=="emberfall_claymore":
        c=[C((-.7,-8,-.6),(1.4,8,1.2),(0,96)),C((-4.2,0,-.52),(8.4,1.1,1.04),(64,96))]
        for y,w in [(1,4.5),(5.6,4.2),(10.2,3.8),(14.8,3.4),(19.4,2.8)]:c.append(C((-w/2,y,-.5),(w,4.4,1),(0,0)))
        c += [C((-1,23.8,-.35),(2,2.2,.7),(64,0)),C((-2.3,.4,-.45),(2.2,2.2,.9),(80,96),(-.8,1,0),(0,0,-22.5)),C((.1,.4,-.45),(2.2,2.2,.9),(88,96),(.8,1,0),(0,0,22.5))]
        return c
    if n=="noctis_longsword":
        c=[C((-.62,-7.5,-.48),(1.24,7.5,.96),(0,96)),C((-3.5,0,-.34),(7,.8,.68),(64,96))]
        for y,w in [(1,2.9),(5.7,2.65),(10.4,2.3),(15.1,1.95),(19.8,1.55)]:c.append(C((-w/2,y,-.38),(w,4.45,.76),(0,0)))
        c += [C((-.45,24.0,-.24),(.9,2.2,.48),(64,0)),C((-2.0,.2,-.4),(1.9,2.2,.8),(80,96),(-.5,.8,0),(0,0,-22.5)),C((.1,.2,-.4),(1.9,2.2,.8),(88,96),(.5,.8,0),(0,0,22.5))]
        return c
    if n=="stormpiercer_recurve_bow":
        c=[C((-.7,-3.4,-.58),(1.4,6.8,1.16),(0,96)),C((-1.6,-.7,-.7),(3.2,2.4,1.4),(64,96))]
        for cx,cy,ang in [(0,4.0,0),(.8,6.9,18),(2,9.8,28),(3.2,12.7,38),(4.1,15.5,45),(0,-4,0),(-.8,-6.9,-18),(-2,-9.8,-28),(-3.2,-12.7,-38),(-4.1,-15.5,-45)]:
            c.append(C((cx-.38,cy-1.5,-.38),(.76,3,.76),(0,0),(cx,cy,0),(0,0,ang)))
        return c
    if n=="gaia_war_spear":
        c=[C((-.43,-12,-.43),(.86,32,.86),(0,96))]
        for y in (-9,-4,1,6,11,16):c.append(C((-.75,y,-.52),(1.5,.28,1.04),(64,96)))
        c += [C((-.95,19,-.48),(1.9,5.3,.96),(0,0)),C((-2.5,20,-.32),(2.0,5.8,.64),(64,0),(-.4,22,0),(0,0,-24)),C((.5,20,-.32),(2.0,5.8,.64),(64,0),(.4,22,0),(0,0,24)),C((-1.5,24.2,-.32),(3,4.5,.64),(92,0)),C((-.48,28.2,-.22),(.96,3.3,.44),(108,0))]
        return c
    c=[C((-.68,-10,-.56),(1.36,27,1.12),(0,96))]
    for y in (-7,-2,3,8,13):c.append(C((-.95,y,-.65),(1.9,.30,1.3),(64,96)))
    c += [C((-1.2,16,-.8),(2.4,4,1.6),(80,96)),C((-5.8,18,-.55),(6.2,3.7,1.1),(0,0),(-.5,19.4,0),(0,0,-22)),C((-8.3,20.7,-.48),(5.2,4.6,.96),(20,0),(-3.6,21.7,0),(0,0,-45)),C((.5,18.2,-.50),(4.3,3.2,1),(42,0),(.5,19.3,0),(0,0,22)),C((-1.0,19.3,-.86),(2,5.2,1.72),(64,0)),C((-.45,24.2,-.34),(.9,4.7,.68),(84,0))]
    return c

for n,v in W.items():
    im=tex(128,v["base"],v["mid"],v["glow"],v["kind"],"bed366-"+n);im.save(BR/f"textures/items/{n}.png",optimize=True)
    gid=f"geometry.raisnet_{n}_v366";cubes=bed_geom(n)
    wr(BR/f"models/entity/{n}.geo.json",{"format_version":"1.16.0","minecraft:geometry":[{"description":{"identifier":gid,"texture_width":128,"texture_height":128,"visible_bounds_width":7,"visible_bounds_height":8,"visible_bounds_offset":[0,8,0]},"bones":[{"name":"bb_main","pivot":[0,8,0],"binding":"q.item_slot_to_bone_name(context.item_slot)","cubes":cubes}]}]})
    ap=BR/f"attachables/{n}.player.json";a=json.loads(ap.read_text());d=a["minecraft:attachable"]["description"];d["geometry"]["default"]=gid;ap.write_text(json.dumps(a,separators=(",",":")),encoding="utf-8")

# Bedrock armor texture art upgrade + restrained geometry accent additions.
def bed_armor_art(setn,layer):
    base,mid,glow=SETS[setn];im=Image.new("RGBA",(64,32),base+(255,));d=ImageDraw.Draw(im,"RGBA")
    for x in range(0,64,8):d.line((x,0,x,31),fill=mid+(48,))
    for y in range(0,32,8):d.line((0,y,63,y),fill=mid+(32,))
    if setn=="phoenix":
        for x in (8,24,40,56):d.line((x,2,x-2,8,x+1,12),fill=glow+(220,),width=1)
    elif setn=="voidwalker":
        d.arc((2,1,17,14),205,338,fill=glow+(215,),width=1);d.arc((20,16,38,31),20,160,fill=glow+(190,),width=1)
    elif setn=="titan":
        for x in (3,20,37,54):d.rectangle((x,3,min(x+7,63),5),fill=glow+(205,))
    elif setn=="celestial":
        for x,y in ((8,4),(22,10),(28,23),(43,5),(55,21)):d.line((x-1,y,x+1,y),fill=glow+(230,));d.line((x,y-1,x,y+1),fill=glow+(230,))
    else:
        for x in (4,20,36,52):d.arc((x,3,min(x+10,63),12),0,180,fill=glow+(220,),width=1)
    return im

for s in SETS:
    for layer in (1,2):bed_armor_art(s,layer).save(BR/f"textures/models/armor/{s}_{layer}.png",optimize=True)

# Fresh mapping copy, ensure weapon identifiers unique/current.
mapping=json.loads(MBASE.read_text())
weapon_pairs={f"{NS}:emberfall_claymore":"raisnet:emberfall_claymore",f"{NS}:noctis_longsword":"raisnet:noctis_longsword",f"{NS}:stormpiercer_recurve_bow":"raisnet:stormpiercer_recurve_bow",f"{NS}:gaia_war_spear":"raisnet:gaia_war_spear",f"{NS}:astral_frost_greataxe":"raisnet:astral_frost_greataxe"}
for model,ident in weapon_pairs.items():
    defs=[d for arr in mapping["items"].values() for d in arr if d.get("type")=="definition" and d.get("model")==model]
    if len(defs)!=1:raise RuntimeError((model,len(defs)))
    defs[0]["bedrock_identifier"]=ident;defs[0].setdefault("bedrock_options",{})["display_handheld"]=True
    if model.endswith("stormpiercer_recurve_bow"):defs[0].pop("components",None)
MOUT.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# Pack metadata/UUID.
jm=JR/"pack.mcmeta";meta=json.loads(jm.read_text());meta["pack"]["description"]="LegendaryRais v3.6.6 MYTHIC ART QA30 | curated 3D weapons | layered armor | bow draw states";jm.write_text(json.dumps(meta,separators=(",",":")),encoding="utf-8")
mf=BR/"manifest.json";bm=json.loads(mf.read_text());bm["header"]["name"]="RaisNet LegendaryRais v3.6.6 Mythic Art QA30";bm["header"]["description"]="Curated low-cube 3D arsenal + upgraded armor art + validated attachables";bm["header"]["uuid"]="66ab6ef5-12af-46a8-8f2e-84e8cb373e4b";bm["header"]["version"]=[3,6,6];bm["modules"][0]["uuid"]="81cc3799-c51b-45e0-9cba-9d4ee9bf8f99";bm["modules"][0]["version"]=[3,6,6];mf.write_text(json.dumps(bm,separators=(",",":")),encoding="utf-8")

# ---------------------- QA30 ----------------------
checks=[]
def Q(name,cond):
    if not cond: raise AssertionError(name)
    checks.append(name);print(f"CHECK {len(checks):02d} PASS - {name}")

# 1 JSON validity
for root in (JR,BR):
    for p in root.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
Q("all JSON files parse",True)
# 2 PNG integrity
for root in (JR,BR):
    for p in root.rglob("*.png"):
        with Image.open(p) as im:im.verify()
Q("all PNG files verify",True)
# 3 pack mcmeta
Q("Java pack metadata exists",(JR/"pack.mcmeta").is_file())
# 4 manifest
Q("Bedrock manifest exists",(BR/"manifest.json").is_file())
# 5 mapping parse
Q("Geyser mapping parses",isinstance(mapping.get("items"),dict))
# 6 current Java item defs
Q("all Java weapon item definitions exist",all((JR/f"assets/{NS}/items/{n}.json").is_file() for n in W))
# 7 current Java models
Q("all Java weapon models exist",all((JR/f"assets/{NS}/models/item/{n}.json").is_file() for n in W))
# 8 textures 256
ok=True
for n in W:
    o=json.loads((JR/f"assets/{NS}/models/item/{n}.json").read_text())
    for key in ("metal","grip","accent"):
        ns,path=o["textures"][key].split(":",1);ok &= Image.open(JR/f"assets/{ns}/textures/{path}.png").size==(256,256)
Q("Java weapon textures are 256px",ok)
# 9 element budget
Q("Java element budgets 10..28",all(10<=len(json.loads((JR/f"assets/{NS}/models/item/{n}.json").read_text())["elements"])<=28 for n in W))
# 10 element bounds
ok=True
for n in W:
    for e in json.loads((JR/f"assets/{NS}/models/item/{n}.json").read_text())["elements"]:
        ok &= all(-16<=float(v)<=32 for v in e["from"]+e["to"])
Q("Java model coordinates remain inside -16..32",ok)
# 11 Z centers
ok=True
for n in W:
    o=json.loads((JR/f"assets/{NS}/models/item/{n}.json").read_text());zs=[v for e in o["elements"] for v in (e["from"][2],e["to"][2])];ok &= 7<=sum(zs)/len(zs)<=9
Q("Java models centered on Z=8 hand pivot",ok)
# 12 grip anchors
ok=True
for n in W:
    o=json.loads((JR/f"assets/{NS}/models/item/{n}.json").read_text());g=[e for e in o["elements"] if any(v.get("texture")=="#grip" for v in e["faces"].values())];ok &= bool(g) and any(e["from"][0]<=8<=e["to"][0] and e["from"][1]<=4<=e["to"][1] for e in g)
Q("all Java grips cross x=8/y=4 hand anchor",ok)
# 13 third person x
Q("Java third-person X offsets centered",all(abs(json.loads((JR/f"assets/{NS}/models/item/{n}.json").read_text())["display"]["thirdperson_righthand"]["translation"][0])<=.05 for n in W))
# 14 third person z
Q("Java third-person Z offsets centered",all(abs(json.loads((JR/f"assets/{NS}/models/item/{n}.json").read_text())["display"]["thirdperson_righthand"]["translation"][2])<=.1 for n in W))
# 15 scale limits
Q("Java third-person scales <=0.63",all(json.loads((JR/f"assets/{NS}/models/item/{n}.json").read_text())["display"]["thirdperson_righthand"]["scale"][0]<=.63 for n in W))
# 16 bow pull definitions
Q("Stormpiercer three pull models exist",all((JR/f"assets/{NS}/models/item/stormpiercer_recurve_bow_pulling_{i}.json").is_file() for i in range(3)))
# 17 bow item condition
bo=json.loads((JR/f"assets/{NS}/items/stormpiercer_recurve_bow.json").read_text())["model"]
Q("Stormpiercer uses using_item condition",bo.get("type")=="minecraft:condition" and bo.get("property")=="minecraft:using_item")
# 18 bow duration dispatch
Q("Stormpiercer draw uses use_duration",bo["on_true"].get("type")=="minecraft:range_dispatch" and bo["on_true"].get("property")=="minecraft:use_duration")
# 19 Java armor layered
Q("all Java full armor equipment has >=2 layers",all(len(json.loads((JR/f"assets/{NS}/equipment/{s}_set.json").read_text())["layers"]["humanoid"])>=2 for s in SETS))
# 20 visor files
Q("all Java open/closed helmet equipment files exist",all((JR/f"assets/{NS}/equipment/{s}_helmet_{m}.json").is_file() for s in SETS for m in ("open","closed")))
# 21 Bedrock weapon geometries
Q("all Bedrock weapon geometry files exist",all((BR/f"models/entity/{n}.geo.json").is_file() for n in W))
# 22 Bedrock cube budget
ok=True
for n in W:
    g=json.loads((BR/f"models/entity/{n}.geo.json").read_text())["minecraft:geometry"][0];ok &= 8<=sum(len(b.get("cubes",[])) for b in g["bones"])<=30
Q("Bedrock weapon cube budgets 8..30",ok)
# 23 Bedrock textures
Q("all Bedrock weapon textures 128px",all(Image.open(BR/f"textures/items/{n}.png").size==(128,128) for n in W))
# 24 attachables
Q("all Bedrock weapon attachables exist",all((BR/f"attachables/{n}.player.json").is_file() for n in W))
# 25 bound bones
ok=True
for n in W:
    g=json.loads((BR/f"models/entity/{n}.geo.json").read_text())["minecraft:geometry"][0]["bones"];ok &= any(b.get("binding")=="q.item_slot_to_bone_name(context.item_slot)" for b in g)
Q("Bedrock weapon geometry binds to item slot bone",ok)
# 26 hold animations still wired
ok=True
for n in W:
    a=json.loads((BR/f"attachables/{n}.player.json").read_text())["minecraft:attachable"]["description"];ok &= set(a.get("animations",{}))=={"hold_first_person","hold_third_person"} and len(a.get("scripts",{}).get("animate",[]))==2
Q("Bedrock first/third-person hold animations wired",ok)
# 27 unique Geyser definitions
defs=[d for arr in mapping["items"].values() for d in arr if d.get("type")=="definition"]
Q("each weapon has exactly one Geyser definition",all(sum(1 for d in defs if d.get("model")==m)==1 for m in weapon_pairs))
# 28 unique bedrock identifiers
ids=[d["bedrock_identifier"] for d in defs if d.get("model") in weapon_pairs]
Q("weapon Bedrock identifiers unique",len(ids)==len(set(ids))==5)
# 29 armor attachables complete
Q("all Bedrock armor attachables complete",all((BR/f"attachables/armor_{s}_{p}.json").is_file() for s in SETS for p in ("helmet_open","helmet_closed","chest","legs","boots")))
# 30 water relic lock
Q("Soul Tide and Leviathan locked assets still present",(JR/"assets/soultide/items/soul_tide_sovereign_blade.json").is_file() and (JR/"assets/legendaryrais/items/abyss_leviathan_trident.json").is_file() and (BR/"models/entity/soul_tide_katana.geo.json").is_file() and (BR/"models/entity/abyss_leviathan_trident.geo.json").is_file())

assert len(checks)==30,len(checks)
REPORT.write_text("\n".join(f"{i+1:02d}. PASS - {n}" for i,n in enumerate(checks))+"\n\nQA30: 30/30 PASS\n",encoding="utf-8")

for out,root in ((JOUT,JR),(BOUT,BR)):
    if out.exists():out.unlink()
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(root.rglob("*")):
            if p.is_file():z.write(p,p.relative_to(root).as_posix())
    with zipfile.ZipFile(out) as z:
        bad=z.testzip()
        if bad:raise RuntimeError(bad)

JSHA.write_text(hashlib.sha1(JOUT.read_bytes()).hexdigest()+"\n",encoding="utf-8")
BSHA.write_text(hashlib.sha1(BOUT.read_bytes()).hexdigest()+"\n",encoding="utf-8")
print("JAVA",JOUT.stat().st_size,JSHA.read_text().strip())
print("BEDROCK",BOUT.stat().st_size,BSHA.read_text().strip())
print("QA30",len(checks),"/30 PASS")

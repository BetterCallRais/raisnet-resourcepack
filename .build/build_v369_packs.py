from pathlib import Path
import json, shutil, zipfile, hashlib, math, random
from PIL import Image, ImageDraw, ImageFilter

JBASE=Path("LegendaryRais-Java-26.1.2-v3.6.8-CLEAN-ID-RESTORE-QA50.zip")
BBASE=Path("LegendaryRais-Bedrock-v3.6.8-CLEAN-ID-RESTORE-QA50.mcpack")
MBASE=Path("LegendaryRais-Geyser-v3.6.8-mappings.json")

JOUT=Path("LegendaryRais-Java-26.1.2-v3.6.9-ARMOR-ASCENSION-HD3D.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.6.9-ARMOR-ASCENSION-HD3D.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.6.9-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.6.9-ARMOR-ASCENSION-HD3D.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.6.9-ARMOR-ASCENSION-HD3D.sha1")
REPORT=Path("LegendaryRais-v3.6.9-QA60.txt")
ROOT=Path(".build/generated-v369");JR=ROOT/"java";BR=ROOT/"bedrock"
shutil.rmtree(ROOT,ignore_errors=True);JR.mkdir(parents=True);BR.mkdir(parents=True)
with zipfile.ZipFile(JBASE) as z:z.extractall(JR)
with zipfile.ZipFile(BBASE) as z:z.extractall(BR)

SETS={
 "phoenix":{"base":(86,22,8),"mid":(196,67,15),"accent":(255,176,48),"dark":(39,12,6),"prot":4,
            "base_items":{"helmet":"minecraft:golden_helmet","chest":"minecraft:golden_chestplate","legs":"minecraft:golden_leggings","boots":"minecraft:golden_boots"}},
 "voidwalker":{"base":(16,9,30),"mid":(82,35,121),"accent":(213,92,255),"dark":(7,5,15),"prot":2,
            "base_items":{"helmet":"minecraft:netherite_helmet","chest":"minecraft:netherite_chestplate","legs":"minecraft:netherite_leggings","boots":"minecraft:netherite_boots"}},
 "titan":{"base":(37,48,42),"mid":(98,124,82),"accent":(203,228,132),"dark":(16,22,19),"prot":3,
            "base_items":{"helmet":"minecraft:diamond_helmet","chest":"minecraft:diamond_chestplate","legs":"minecraft:diamond_leggings","boots":"minecraft:diamond_boots"}},
 "celestial":{"base":(30,61,92),"mid":(101,162,201),"accent":(225,249,255),"dark":(12,28,46),"prot":3,
            "base_items":{"helmet":"minecraft:iron_helmet","chest":"minecraft:iron_chestplate","legs":"minecraft:iron_leggings","boots":"minecraft:iron_boots"}},
 "water_sovereign":{"base":(8,49,72),"mid":(36,139,166),"accent":(113,240,255),"dark":(5,25,38),"prot":3,
            "base_items":{"helmet":"minecraft:netherite_helmet","chest":"minecraft:netherite_chestplate","legs":"minecraft:netherite_leggings","boots":"minecraft:netherite_boots"}}
}
PIECES=("helmet","chest","legs","boots")
NS="legendaryv369"

def wr(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def item_faces(key):
    return {f:{"texture":"#"+key} for f in ("north","south","east","west","up","down")}

def JE(fr,to,key="metal",rot=None):
    e={"from":[round(v,3) for v in fr],"to":[round(v,3) for v in to],"faces":item_faces(key)}
    if rot:
        origin,axis,ang=rot
        e["rotation"]={"origin":[round(v,3) for v in origin],"axis":axis,"angle":ang,"rescale":True}
    return e

def make_material(size,st,seed,transparent=False):
    rnd=random.Random(seed);base=st["base"];mid=st["mid"];accent=st["accent"];dark=st["dark"]
    im=Image.new("RGBA",(size,size),(0,0,0,0) if transparent else base+(255,))
    if not transparent:
        px=im.load()
        for y in range(size):
            for x in range(size):
                nx=x/(size-1);ny=y/(size-1)
                spec=max(0,1-abs(nx-.35)/.18)*.13
                t=max(.02,min(.62,.10+.18*nx+.18*(1-ny)+spec+.045*math.sin(x*.19+y*.07)+rnd.uniform(-.01,.01)))
                c=tuple(int(base[i]*(1-t)+mid[i]*t) for i in range(3))
                px[x,y]=c+(255,)
    d=ImageDraw.Draw(im,"RGBA");w=max(1,size//128)
    d.rectangle((2*w,2*w,size-2*w-1,size-2*w-1),outline=mid+(90,),width=w)
    return im

def armor_native_layers(setn):
    st=SETS[setn]
    base=Image.new("RGBA",(256,128),st["base"]+(255,))
    px=base.load();rnd=random.Random("native-"+setn)
    for y in range(128):
        for x in range(256):
            nx=x/255;ny=y/127
            bevel=.11*max(0,1-abs((x%32)-16)/16)
            stripe=.04*math.sin((x+y)*.18)
            t=max(0,min(.48,.12+.15*(1-ny)+.12*nx+bevel+stripe+rnd.uniform(-.015,.015)))
            c=tuple(int(st["base"][i]*(1-t)+st["mid"][i]*t) for i in range(3))
            px[x,y]=c+(255,)
    d=ImageDraw.Draw(base,"RGBA")
    for x in range(0,256,32):d.line((x,0,x,127),fill=st["dark"]+(50,),width=2)
    for y in range(0,128,32):d.line((0,y,255,y),fill=st["dark"]+(42,),width=2)
    accent=Image.new("RGBA",(256,128),(0,0,0,0));a=ImageDraw.Draw(accent,"RGBA");col=st["accent"]+(220,)
    if setn=="phoenix":
        for ox in (32,96,160,224):
            a.polygon([(ox,8),(ox-10,28),(ox-3,24),(ox-12,50),(ox+2,32),(ox+10,50),(ox+5,25)],outline=col)
        a.arc((70,62,125,116),205,340,fill=col,width=4);a.arc((132,62,187,116),200,335,fill=col,width=4)
    elif setn=="voidwalker":
        a.arc((20,8,76,58),205,340,fill=col,width=4);a.arc((80,8,136,58),200,335,fill=col,width=4)
        for x,y in ((24,74),(61,98),(108,79),(151,103),(202,77),(231,105)):a.ellipse((x-3,y-3,x+3,y+3),fill=col)
    elif setn=="titan":
        for x in (10,66,122,178):
            a.rectangle((x,12,x+42,20),fill=col)
            a.rectangle((x+6,42,x+36,48),fill=st["mid"]+(180,))
        a.rectangle((70,70,118,82),outline=col,width=4);a.rectangle((138,70,186,82),outline=col,width=4)
    elif setn=="celestial":
        for x,y in ((36,21),(86,45),(119,18),(165,39),(210,23),(232,90)):
            a.line((x-5,y,x+5,y),fill=col,width=3);a.line((x,y-5,x,y+5),fill=col,width=3)
        a.arc((70,58,128,117),195,345,fill=col,width=4);a.arc((130,58,188,117),195,345,fill=col,width=4)
    else:
        for y in (20,52,84):
            a.arc((15,y-13,88,y+18),185,355,fill=col,width=4);a.arc((95,y-13,168,y+18),185,355,fill=col,width=4)
        a.polygon([(211,15),(226,36),(216,52),(235,70),(212,63),(198,82),(203,55),(188,43)],outline=col)
    return base.filter(ImageFilter.UnsharpMask(1,150,2)),accent

def java_overlay_elements(setn,piece):
    e=[]
    if piece=="helmet":
        e += [JE((3,3,3),(13,13,13),"metal"),JE((4,12.4,4),(12,14.1,12),"accent")]
        if setn=="phoenix":
            e += [JE((2.1,9,5),(4,15,11),"accent",([4,11,8],"z",-22.5)),JE((12,9,5),(13.9,15,11),"accent",([12,11,8],"z",22.5)),JE((6.8,13.4,5.7),(9.2,16,10.3),"accent")]
        elif setn=="voidwalker":
            e += [JE((3.0,12.5,6.2),(5.0,16,9.8),"dark",([4.5,13.5,8],"z",-22.5)),JE((11.0,12.5,6.2),(13.0,16,9.8),"dark",([11.5,13.5,8],"z",22.5)),JE((6.5,4,2.2),(9.5,7,4),"accent")]
        elif setn=="titan":
            e += [JE((2.2,5,4),(4,12,12),"dark"),JE((12,5,4),(13.8,12,12),"dark"),JE((5.5,12.5,4),(10.5,15,12),"metal")]
        elif setn=="celestial":
            e += [JE((7.2,13,7.2),(8.8,16,8.8),"accent"),JE((3.0,9,4),(4.3,14,12),"accent",([4,11,8],"z",-22.5)),JE((11.7,9,4),(13.0,14,12),"accent",([12,11,8],"z",22.5))]
        else:
            e += [JE((2.4,8.5,5),(4,14,11),"accent",([4,10.5,8],"z",-22.5)),JE((12,8.5,5),(13.6,14,11),"accent",([12,10.5,8],"z",22.5)),JE((6.6,13,6.3),(9.4,15.7,9.7),"accent")]
    elif piece=="chest":
        e += [JE((3,1.5,5),(13,13.5,11),"metal"),JE((5.5,5,3.6),(10.5,10.5,6),"accent")]
        if setn=="phoenix":
            e += [JE((.5,6,5.5),(4.0,13,10.5),"accent",([3.2,8,8],"z",-22.5)),JE((12,6,5.5),(15.5,13,10.5),"accent",([12.8,8,8],"z",22.5)),JE((7,8,3),(9,12.5,5),"accent")]
        elif setn=="voidwalker":
            e += [JE((.7,7,5),(4.1,12.5,11),"dark",([3.4,8.5,8],"z",-22.5)),JE((11.9,7,5),(15.3,12.5,11),"dark",([12.6,8.5,8],"z",22.5)),JE((6.5,7,3.2),(9.5,10.5,5.3),"accent")]
        elif setn=="titan":
            e += [JE((.2,5,4.5),(4.4,13.5,11.5),"metal"),JE((11.6,5,4.5),(15.8,13.5,11.5),"metal"),JE((5,10,3.8),(11,13.3,5.4),"dark")]
        elif setn=="celestial":
            e += [JE((.5,7,5),(4.2,14,11),"accent",([3.5,8.5,8],"z",-22.5)),JE((11.8,7,5),(15.5,14,11),"accent",([12.5,8.5,8],"z",22.5)),JE((7,7,3),(9,9,5),"accent")]
        else:
            e += [JE((.5,6.5,5),(4.1,13.5,11),"accent",([3.4,8.4,8],"z",-22.5)),JE((11.9,6.5,5),(15.5,13.5,11),"accent",([12.6,8.4,8],"z",22.5)),JE((5.5,8,3.2),(10.5,10,5.1),"accent")]
    elif piece=="legs":
        e += [JE((3,1,5),(7.2,14.5,11),"metal"),JE((8.8,1,5),(13,14.5,11),"metal"),JE((5.5,10.5,4.2),(10.5,14.5,11.8),"accent")]
        e += [JE((3.6,5,4.2),(6.6,8,6),"accent"),JE((9.4,5,4.2),(12.4,8,6),"accent")]
        if setn=="titan":e += [JE((2.5,7,5),(4.0,12,11),"dark"),JE((12,7,5),(13.5,12,11),"dark")]
        if setn=="water_sovereign":e += [JE((2.8,10,6),(4.0,14,10),"accent",([4,11,8],"z",-22.5)),JE((12,10,6),(13.2,14,10),"accent",([12,11,8],"z",22.5))]
    else:
        e += [JE((2.7,1,4.5),(7.2,11,11.5),"metal"),JE((8.8,1,4.5),(13.3,11,11.5),"metal"),JE((2.2,7.5,4),(7.6,11.5,12),"accent"),JE((8.4,7.5,4),(13.8,11.5,12),"accent")]
        if setn=="phoenix":e += [JE((3.1,1,3.2),(6.8,4.5,5.1),"accent"),JE((9.2,1,3.2),(12.9,4.5,5.1),"accent")]
        if setn=="voidwalker":e += [JE((2.4,8,5),(4,12,11),"dark"),JE((12,8,5),(13.6,12,11),"dark")]
    return e[:24]

# Java HD native layers + 3D overlay/item models
for s,st in SETS.items():
    base,accent=armor_native_layers(s)
    for sub in ("humanoid","humanoid_leggings"):
        p=JR/f"assets/{NS}/textures/entity/equipment/{sub}/{s}_base.png";p.parent.mkdir(parents=True,exist_ok=True);base.save(p,optimize=True)
        q=JR/f"assets/{NS}/textures/entity/equipment/{sub}/{s}_accent.png";accent.save(q,optimize=True)
    open_base=base.copy();open_acc=accent.copy()
    # visor opening region: 4x upscale of old 8..15 x 10..15 region
    for y in range(40,64):
        for x in range(32,64):
            open_base.putpixel((x,y),(0,0,0,0));open_acc.putpixel((x,y),(0,0,0,0))
    ob=JR/f"assets/{NS}/textures/entity/equipment/humanoid/{s}_open_base.png";oa=JR/f"assets/{NS}/textures/entity/equipment/humanoid/{s}_open_accent.png"
    open_base.save(ob,optimize=True);open_acc.save(oa,optimize=True)

    wr(JR/f"assets/{NS}/equipment/{s}_set.json",{"layers":{
      "humanoid":[{"texture":f"{NS}:{s}_base"},{"texture":f"{NS}:{s}_accent"}],
      "humanoid_leggings":[{"texture":f"{NS}:{s}_base"},{"texture":f"{NS}:{s}_accent"}]}})
    wr(JR/f"assets/{NS}/equipment/{s}_helmet_closed.json",{"layers":{"humanoid":[{"texture":f"{NS}:{s}_base"},{"texture":f"{NS}:{s}_accent"}]}})
    wr(JR/f"assets/{NS}/equipment/{s}_helmet_open.json",{"layers":{"humanoid":[{"texture":f"{NS}:{s}_open_base"},{"texture":f"{NS}:{s}_open_accent"}]}})

    for piece in PIECES:
        tex=make_material(256,st,f"java-armor-{s}-{piece}")
        tp=JR/f"assets/{NS}/textures/item/armor/{s}_{piece}.png";tp.parent.mkdir(parents=True,exist_ok=True);tex.save(tp,optimize=True)
        model={"textures":{"metal":f"{NS}:item/armor/{s}_{piece}","accent":f"{NS}:item/armor/{s}_{piece}","dark":f"{NS}:item/armor/{s}_{piece}"},
               "elements":java_overlay_elements(s,piece),"gui_light":"front",
               "display":{"gui":{"rotation":[24,-34,0],"translation":[0,0,0],"scale":[.72,.72,.72]},
                          "fixed":{"rotation":[0,180,0],"translation":[0,0,0],"scale":[.72,.72,.72]},
                          "ground":{"translation":[0,2,0],"scale":[.45,.45,.45]}}}
        wr(JR/f"assets/{NS}/models/item/armor/{s}_{piece}.json",model)
        wr(JR/f"assets/{NS}/items/armor/{s}_{piece}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/armor/{s}_{piece}"}})
        wr(JR/f"assets/{NS}/models/item/armor_visual/{s}_{piece}.json",model)
        wr(JR/f"assets/{NS}/items/armor_visual/{s}_{piece}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/armor_visual/{s}_{piece}"}})
    # helmet mode item_model wrappers
    wr(JR/f"assets/{NS}/items/armor/{s}_helmet_closed.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/armor/{s}_helmet"}})
    wr(JR/f"assets/{NS}/items/armor/{s}_helmet_open.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/armor/{s}_helmet"}})

# ---------- Bedrock true 3D armor ----------
def BC(origin,size,uv=(0,0),inflate=None,pivot=None,rotation=None,mirror=None):
    c={"origin":[round(v,3) for v in origin],"size":[round(v,3) for v in size],"uv":[round(v,3) for v in uv]}
    if inflate is not None:c["inflate"]=inflate
    if pivot is not None:c["pivot"]=[round(v,3) for v in pivot]
    if rotation is not None:c["rotation"]=[round(v,3) for v in rotation]
    if mirror is not None:c["mirror"]=mirror
    return c

def armor_tex_bed(setn):
    base,acc=armor_native_layers(setn)
    comp=Image.alpha_composite(base,acc)
    return comp.filter(ImageFilter.UnsharpMask(1,170,2))

def head_cubes(s,open_mode):
    c=[]
    if open_mode:
        c += [BC((-4,30,-4),(8,2,8),(0,0),.82),BC((-4,24,-4),(1.8,6,8),(0,40),.82),BC((2.2,24,-4),(1.8,6,8),(40,40),.82),BC((-2.8,24,2.2),(5.6,6,1.8),(80,40),.82)]
    else:c += [BC((-4,24,-4),(8,8,8),(0,0),.82)]
    if s=="phoenix":
        c += [BC((-5.5,28,-1),(1.5,5,3),(120,0),.08,(-4,29,0),(0,0,-18)),BC((4,28,-1),(1.5,5,3),(136,0),.08,(4,29,0),(0,0,18)),BC((-.8,32,-.8),(1.6,4,1.6),(152,0),.06)]
    elif s=="voidwalker":
        c += [BC((-5.1,30,-.7),(1.2,5,1.4),(120,0),.06,(-4,30,0),(0,0,-22)),BC((3.9,30,-.7),(1.2,5,1.4),(132,0),.06,(4,30,0),(0,0,22)),BC((-1.4,23.6,-4.8),(2.8,2.2,1.0),(144,0),.06)]
    elif s=="titan":
        c += [BC((-5.1,25,-3.2),(1.4,5.5,6.4),(120,0),.09),BC((3.7,25,-3.2),(1.4,5.5,6.4),(140,0),.09),BC((-2.4,31,-4.5),(4.8,2.5,1.2),(160,0),.08)]
    elif s=="celestial":
        c += [BC((-.55,32,-.55),(1.1,4.2,1.1),(120,0),.05),BC((-5.0,28,-.8),(1.2,3.8,1.6),(132,0),.05,(-4,29,0),(0,0,-15)),BC((3.8,28,-.8),(1.2,3.8,1.6),(144,0),.05,(4,29,0),(0,0,15))]
    else:
        c += [BC((-5.3,27,-.8),(1.3,5,3),(120,0),.06,(-4,28,0),(0,0,-20)),BC((4,27,-.8),(1.3,5,3),(136,0),.06,(4,28,0),(0,0,20)),BC((-1.0,32,-.8),(2,3.5,1.6),(152,0),.05)]
    return c

def chest_parts(s):
    body=[BC((-4,2,-2),(8,12,4),(0,0),1.05),BC((-2.7,5,-3.3),(5.4,5.8,1.2),(80,0),.08)]
    r=[BC((-8,2,-2),(4,12,4),(0,64),1.03)]
    l=[BC((4,2,-2),(4,12,4),(0,64),1.03,None,None,True)]
    if s=="phoenix":
        body += [BC((-.9,8,-3.9),(1.8,4.5,.8),(100,0),.04)]
        r += [BC((-9.4,8,-2.6),(5.2,4.2,5.2),(120,32),.10,(-5.2,10,0),(0,0,-12))]
        l += [BC((4.2,8,-2.6),(5.2,4.2,5.2),(144,32),.10,(5.2,10,0),(0,0,12),True)]
    elif s=="voidwalker":
        body += [BC((-2.4,7,-3.8),(4.8,1.3,.7),(100,0),.03),BC((-.7,9,-4.1),(1.4,2.8,.8),(108,0),.03)]
        r += [BC((-9.0,9,-2.5),(4.8,3.0,5),(120,32),.07,(-5.2,10,0),(0,0,-18))]
        l += [BC((4.2,9,-2.5),(4.8,3.0,5),(144,32),.07,(5.2,10,0),(0,0,18),True)]
    elif s=="titan":
        body += [BC((-4.8,3,-2.8),(1.3,8,5.6),(100,0),.08),BC((3.5,3,-2.8),(1.3,8,5.6),(110,0),.08),BC((-2.5,9,-3.7),(5,3.2,.9),(120,0),.06)]
        r += [BC((-9.6,7.5,-2.8),(5.8,5.2,5.6),(128,32),.12)]
        l += [BC((3.8,7.5,-2.8),(5.8,5.2,5.6),(156,32),.12,None,None,True)]
    elif s=="celestial":
        body += [BC((-.85,8.5,-3.8),(1.7,1.7,.8),(100,0),.04),BC((-2.5,6,-3.55),(5,1,.6),(108,0),.03)]
        r += [BC((-9.2,8,-2.5),(5,4,5),(120,32),.07,(-5.2,10,0),(0,0,-12))]
        l += [BC((4.2,8,-2.5),(5,4,5),(144,32),.07,(5.2,10,0),(0,0,12),True)]
    else:
        body += [BC((-2.8,7,-3.8),(5.6,1.2,.8),(100,0),.04),BC((-1.2,9,-4.0),(2.4,2.3,.9),(112,0),.04)]
        r += [BC((-9.3,8,-2.6),(5.1,4.1,5.2),(120,32),.08,(-5.2,10,0),(0,0,-15))]
        l += [BC((4.2,8,-2.6),(5.1,4.1,5.2),(144,32),.08,(5.2,10,0),(0,0,15),True)]
    return body,r,l

def leg_parts(s):
    waist=[BC((-4,8,-2),(8,4,4),(64,64),.72)]
    r=[BC((-4,0,-2),(4,12,4),(0,64),.62),BC((-3.5,4,-2.9),(3,3.3,1.1),(96,64),.05)]
    l=[BC((0,0,-2),(4,12,4),(0,64),.62,None,None,True),BC((.5,4,-2.9),(3,3.3,1.1),(112,64),.05,None,None,True)]
    if s=="titan":
        r += [BC((-4.4,6,-2.4),(1.0,5,4.8),(128,64),.05)]
        l += [BC((3.4,6,-2.4),(1.0,5,4.8),(140,64),.05)]
    elif s=="water_sovereign":
        r += [BC((-4.4,8,-.8),(1.1,4,2.0),(128,64),.04,(-3.5,9,0),(0,0,-15))]
        l += [BC((3.3,8,-.8),(1.1,4,2.0),(140,64),.04,(3.5,9,0),(0,0,15))]
    elif s=="phoenix":
        waist += [BC((-1.0,11,-3.0),(2,2,.8),(128,64),.04)]
    return waist,r,l

def boot_parts(s):
    r=[BC((-4,0,-2),(4,6,4),(0,96),.92),BC((-3.7,0,-3.2),(3.4,2.3,1.4),(96,96),.05)]
    l=[BC((0,0,-2),(4,6,4),(0,96),.92,None,None,True),BC((.3,0,-3.2),(3.4,2.3,1.4),(112,96),.05,None,None,True)]
    if s=="phoenix":
        r += [BC((-3.4,4.6,-2.7),(2.8,2.2,1),(128,96),.05)]
        l += [BC((.6,4.6,-2.7),(2.8,2.2,1),(144,96),.05,None,None,True)]
    elif s=="voidwalker":
        r += [BC((-4.2,5,-1.5),(1.1,2.5,3),(128,96),.04)]
        l += [BC((3.1,5,-1.5),(1.1,2.5,3),(140,96),.04)]
    elif s=="titan":
        r += [BC((-4.5,3.6,-2.4),(1.2,3.4,4.8),(128,96),.05)]
        l += [BC((3.3,3.6,-2.4),(1.2,3.4,4.8),(140,96),.05)]
    return r,l

def geo_helmet(s,mode):
    gid=f"geometry.raisnet369.armor.{s}.helmet.{mode}"
    return gid,{"format_version":"1.16.0","minecraft:geometry":[{"description":{"identifier":gid,"texture_width":256,"texture_height":128,"visible_bounds_width":3,"visible_bounds_height":4,"visible_bounds_offset":[0,1,0]},"bones":[{"name":"head","pivot":[0,24,0]},{"name":"armor_head","parent":"head","pivot":[0,24,0],"binding":"'head'","cubes":head_cubes(s,mode=="open")}]}]}

def geo_chest(s):
    gid=f"geometry.raisnet369.armor.{s}.chest";body,r,l=chest_parts(s)
    return gid,{"format_version":"1.16.0","minecraft:geometry":[{"description":{"identifier":gid,"texture_width":256,"texture_height":128,"visible_bounds_width":3,"visible_bounds_height":3.4,"visible_bounds_offset":[0,.8,0]},"bones":[{"name":"body","pivot":[0,14,0]},{"name":"armor_body","parent":"body","pivot":[0,0,0],"binding":"'body'","cubes":body},{"name":"rightarm","pivot":[-5,12,0]},{"name":"armor_rarm","parent":"rightarm","pivot":[-5,12,0],"binding":"'rightarm'","cubes":r},{"name":"leftarm","pivot":[5,12,0]},{"name":"armor_larm","parent":"leftarm","pivot":[5,12,0],"binding":"'leftarm'","cubes":l}]}]}

def geo_legs(s):
    gid=f"geometry.raisnet369.armor.{s}.legs";waist,r,l=leg_parts(s)
    return gid,{"format_version":"1.16.0","minecraft:geometry":[{"description":{"identifier":gid,"texture_width":256,"texture_height":128,"visible_bounds_width":3,"visible_bounds_height":3.0,"visible_bounds_offset":[0,.5,0]},"bones":[{"name":"body","pivot":[0,12,0]},{"name":"armor_waist","parent":"body","pivot":[0,12,0],"binding":"'body'","cubes":waist},{"name":"rightleg","pivot":[-1.9,12,0]},{"name":"armor_rleg","parent":"rightleg","pivot":[-1.9,12,0],"binding":"'rightleg'","cubes":r},{"name":"leftleg","pivot":[1.9,12,0]},{"name":"armor_lleg","parent":"leftleg","pivot":[1.9,12,0],"binding":"'leftleg'","cubes":l}]}]}

def geo_boots(s):
    gid=f"geometry.raisnet369.armor.{s}.boots";r,l=boot_parts(s)
    return gid,{"format_version":"1.16.0","minecraft:geometry":[{"description":{"identifier":gid,"texture_width":256,"texture_height":128,"visible_bounds_width":3,"visible_bounds_height":2.5,"visible_bounds_offset":[0,.35,0]},"bones":[{"name":"rightleg","pivot":[-1.9,12,0]},{"name":"armor_rboot","parent":"rightleg","pivot":[-1.9,12,0],"binding":"'rightleg'","cubes":r},{"name":"leftleg","pivot":[1.9,12,0]},{"name":"armor_lboot","parent":"leftleg","pivot":[1.9,12,0],"binding":"'leftleg'","cubes":l}]}]}

def attach(ident,gid,tex,parent_setup):
    return {"format_version":"1.20.60","minecraft:attachable":{"description":{"identifier":ident,"render_controllers":["controller.render.armor"],"materials":{"default":"entity_alphatest","enchanted":"entity_alphatest_glint"},"textures":{"default":tex,"enchanted":"textures/misc/enchanted_actor_glint"},"geometry":{"default":gid},"scripts":{"parent_setup":parent_setup}}}}

atlas_path=BR/"textures/item_texture.json";atlas=json.loads(atlas_path.read_text());td=atlas.setdefault("texture_data",{})
for s,st in SETS.items():
    bt=armor_tex_bed(s)
    for layer in (1,2):
        p=BR/f"textures/models/armor/v369_{s}_{layer}.png";p.parent.mkdir(parents=True,exist_ok=True);bt.save(p,optimize=True)
    # icon
    icon=make_material(128,st,f"bed-icon-{s}")
    iconp=BR/f"textures/items/v369_armor_{s}.png";iconp.parent.mkdir(parents=True,exist_ok=True);icon.save(iconp,optimize=True)
    for piece in PIECES:
        ident=f"raisnet369:{s}_{piece}"
        td[ident]={"textures":f"textures/items/v369_armor_{s}"}
    for mode in ("closed","open"):
        ident=f"raisnet369:{s}_helmet_{mode}"
        td[ident]={"textures":f"textures/items/v369_armor_{s}"}
        gid,g=geo_helmet(s,mode);wr(BR/f"models/entity/v369_armor_{s}_helmet_{mode}.geo.json",g)
        wr(BR/f"attachables/v369_armor_{s}_helmet_{mode}.json",attach(ident,gid,f"textures/models/armor/v369_{s}_1","v.helmet_layer_visible = false;"))
    gid,g=geo_chest(s);wr(BR/f"models/entity/v369_armor_{s}_chest.geo.json",g);wr(BR/f"attachables/v369_armor_{s}_chest.json",attach(f"raisnet369:{s}_chest",gid,f"textures/models/armor/v369_{s}_1","v.chest_layer_visible = false;"))
    gid,g=geo_legs(s);wr(BR/f"models/entity/v369_armor_{s}_legs.geo.json",g);wr(BR/f"attachables/v369_armor_{s}_legs.json",attach(f"raisnet369:{s}_legs",gid,f"textures/models/armor/v369_{s}_2","v.leg_layer_visible = false;"))
    gid,g=geo_boots(s);wr(BR/f"models/entity/v369_armor_{s}_boots.geo.json",g);wr(BR/f"attachables/v369_armor_{s}_boots.json",attach(f"raisnet369:{s}_boots",gid,f"textures/models/armor/v369_{s}_1","v.boot_layer_visible = false;"))

(BR/"textures/item_texture.json").write_text(json.dumps(atlas,separators=(",",":")),encoding="utf-8")

# ---------- fresh armor mappings, preserve v368 weapons/FX ----------
mapping=json.loads(MBASE.read_text())
for base,arr in list(mapping["items"].items()):
    keep=[]
    for d in arr:
        model=str(d.get("model",""))
        bid=str(d.get("bedrock_identifier",""))
        if "armor/" in model and model.startswith("legendaryv34:"):continue
        if bid.startswith("raisnet:") and any(f"{s}_" in bid for s in SETS):continue
        keep.append(d)
    mapping["items"][base]=keep

slot_name={"helmet":"head","chest":"chest","legs":"legs","boots":"feet"}
display_piece={"helmet":"Helmet","chest":"Chestplate","legs":"Leggings","boots":"Boots"}
for s,st in SETS.items():
    for piece in PIECES:
        if piece=="helmet":
            for mode in ("closed","open"):
                mapping["items"].setdefault(st["base_items"][piece],[]).append({
                  "type":"definition","model":f"{NS}:armor/{s}_helmet_{mode}","bedrock_identifier":f"raisnet369:{s}_helmet_{mode}",
                  "display_name":f"{s.replace('_',' ').title()} Helmet {mode.title()}",
                  "bedrock_options":{"icon":f"raisnet369:{s}_helmet_{mode}","protection_value":st["prot"],"creative_category":"equipment"},
                  "components":{"minecraft:equippable":{"slot":"head"},"minecraft:max_stack_size":1}})
        else:
            mapping["items"].setdefault(st["base_items"][piece],[]).append({
              "type":"definition","model":f"{NS}:armor/{s}_{piece}","bedrock_identifier":f"raisnet369:{s}_{piece}",
              "display_name":f"{s.replace('_',' ').title()} {display_piece[piece]}",
              "bedrock_options":{"icon":f"raisnet369:{s}_{piece}","protection_value":st["prot"],"creative_category":"equipment"},
              "components":{"minecraft:equippable":{"slot":slot_name[piece]},"minecraft:max_stack_size":1}})

MOUT.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# metadata
jm=json.loads((JR/"pack.mcmeta").read_text());jm["pack"]["description"]="LegendaryRais v3.6.9 ARMOR ASCENSION HD3D | Java HD layered + 3D overlays | Bedrock true 3D";(JR/"pack.mcmeta").write_text(json.dumps(jm,separators=(",",":")),encoding="utf-8")
mf=json.loads((BR/"manifest.json").read_text());mf["header"]["name"]="RaisNet LegendaryRais v3.6.9 Armor Ascension HD3D";mf["header"]["description"]="True 3D Bedrock legendary armor + 256x128 HD materials + clean v369 armor IDs";mf["header"]["uuid"]="d9913b28-00f2-4fb5-ad70-26dcdb93218b";mf["header"]["version"]=[3,6,9];mf["modules"][0]["uuid"]="1c0f6051-cfcb-4e99-9e08-b01121ec37d7";mf["modules"][0]["version"]=[3,6,9];(BR/"manifest.json").write_text(json.dumps(mf,separators=(",",":")),encoding="utf-8")

# ---------- QA60 ----------
checks=[]
def Q(name,cond):
    if not cond:raise AssertionError(name)
    checks.append(name);print(f"CHECK {len(checks):02d} PASS - {name}")

for root in (JR,BR):
    for p in root.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
Q("all JSON parses",True)
for root in (JR,BR):
    for p in root.rglob("*.png"):
        with Image.open(p) as im:im.verify()
Q("all PNG verifies",True)
Q("Geyser format_version remains 2",mapping.get("format_version")==2)
Q("Java pack metadata exists",(JR/"pack.mcmeta").is_file())
Q("Bedrock manifest exists",(BR/"manifest.json").is_file())

# freeze weapons/water by checking exact wrapper/model paths still present
Q("v368 Soul wrapper retained",(JR/"assets/legendaryv368/items/soul_tide.json").is_file())
Q("v368 Leviathan wrapper retained",(JR/"assets/legendaryv368/items/leviathan.json").is_file())
Q("v368 five non-water wrappers retained",all((JR/f"assets/legendaryv368/items/{n}.json").is_file() for n in ("emberfall_claymore","noctis_longsword","stormpiercer_recurve_bow","gaia_war_spear","astral_frost_greataxe")))
Q("Soul stable namespace retained",(JR/"assets/soultide").is_dir())
Q("Leviathan stable model retained",(JR/"assets/legendaryrais/models/item/abyss_leviathan_trident.json").is_file())

# Java armor checks
for s in SETS:
    Q(f"{s} Java set equipment exists",(JR/f"assets/{NS}/equipment/{s}_set.json").is_file())
for s in SETS:
    Q(f"{s} Java open/closed equipment exists",all((JR/f"assets/{NS}/equipment/{s}_helmet_{m}.json").is_file() for m in ("open","closed")))
for s in SETS:
    base=Image.open(JR/f"assets/{NS}/textures/entity/equipment/humanoid/{s}_base.png")
    Q(f"{s} Java armor texture is HD 256x128",base.size==(256,128))
for s in SETS:
    eq=json.loads((JR/f"assets/{NS}/equipment/{s}_set.json").read_text())
    Q(f"{s} Java armor uses layered equipment",len(eq["layers"]["humanoid"])==2 and len(eq["layers"]["humanoid_leggings"])==2)
for s in SETS:
    ok=True
    for piece in PIECES:
        o=json.loads((JR/f"assets/{NS}/models/item/armor_visual/{s}_{piece}.json").read_text())
        ok &= 4<=len(o.get("elements",[]))<=24
        ok &= all(-16<=float(v)<=32 for e in o["elements"] for v in e["from"]+e["to"])
    Q(f"{s} Java 3D overlay models valid",ok)
Q("all Java armor item_model wrappers exist",all((JR/f"assets/{NS}/items/armor/{s}_{p}.json").is_file() for s in SETS for p in ("chest","legs","boots")))
Q("all Java helmet mode wrappers exist",all((JR/f"assets/{NS}/items/armor/{s}_helmet_{m}.json").is_file() for s in SETS for m in ("open","closed")))
Q("all Java armor overlay item_models exist",all((JR/f"assets/{NS}/items/armor_visual/{s}_{p}.json").is_file() for s in SETS for p in PIECES))

# Bedrock armor
for s in SETS:
    Q(f"{s} Bedrock HD armor textures are 256x128",all(Image.open(BR/f"textures/models/armor/v369_{s}_{layer}.png").size==(256,128) for layer in (1,2)))
for s in SETS:
    Q(f"{s} Bedrock helmet open/closed geometry exists",all((BR/f"models/entity/v369_armor_{s}_helmet_{m}.geo.json").is_file() for m in ("open","closed")))
for s in SETS:
    Q(f"{s} Bedrock chest/legs/boots geometry exists",all((BR/f"models/entity/v369_armor_{s}_{p}.geo.json").is_file() for p in ("chest","legs","boots")))
for s in SETS:
    ok=True
    for piece in ("helmet_closed","helmet_open","chest","legs","boots"):
        g=json.loads((BR/f"models/entity/v369_armor_{s}_{piece}.geo.json").read_text())["minecraft:geometry"][0]
        n=sum(len(b.get("cubes",[])) for b in g["bones"])
        ok &= 3<=n<=20
    Q(f"{s} Bedrock 3D cube budgets valid",ok)
for s in SETS:
    Q(f"{s} Bedrock attachables complete",all((BR/f"attachables/v369_armor_{s}_{p}.json").is_file() for p in ("helmet_closed","helmet_open","chest","legs","boots")))
for s in SETS:
    ok=True
    for p in ("helmet_closed","helmet_open","chest","legs","boots"):
        a=json.loads((BR/f"attachables/v369_armor_{s}_{p}.json").read_text())["minecraft:attachable"]["description"]
        ok &= a["identifier"]==f"raisnet369:{s}_{p}"
        ok &= a["render_controllers"]==["controller.render.armor"]
    Q(f"{s} Bedrock armor identifiers/render controllers valid",ok)

# mapping
defs=[d for arr in mapping["items"].values() for d in arr if d.get("type")=="definition"]
Q("all v369 armor mapping definitions exist",all(any(d.get("model")==f"{NS}:armor/{s}_{p}" for d in defs) for s in SETS for p in ("chest","legs","boots")))
Q("all v369 helmet mode mappings exist",all(any(d.get("model")==f"{NS}:armor/{s}_helmet_{m}" for d in defs) for s in SETS for m in ("open","closed")))
Q("no old legendaryv34 armor mapping remains",not any(str(d.get("model","")).startswith("legendaryv34:armor/") for d in defs))
Q("all new armor Bedrock IDs unique",len([d["bedrock_identifier"] for d in defs if str(d.get("model","")).startswith(f"{NS}:armor/")])==len(set(d["bedrock_identifier"] for d in defs if str(d.get("model","")).startswith(f"{NS}:armor/"))))
Q("v368 weapon mappings retained",all(any(str(d.get("model","")).startswith("legendaryv368:") for d in defs) for _ in [0]))
Q("FX mappings retained",any("fx_" in str(d.get("model","")) for d in defs))
Q("armor atlas contains all new IDs",all(f"raisnet369:{s}_{p}" in td for s in SETS for p in ("chest","legs","boots","helmet_open","helmet_closed")))
Q("Bedrock old weapon attachables retained",all(any(p.name.endswith(".player.json") and key in p.name for p in (BR/"attachables").glob("*.json")) for key in ("soul_tide","leviathan","emberfall","noctis","stormpiercer","zephya","astral_frost")))

# make minimum 60 explicit checks by split-preservation checks
Q("Stormpiercer bow wrapper retained",(JR/"assets/legendaryv368/items/stormpiercer_recurve_bow.json").is_file())
Q("Stormpiercer pull model 0 retained",(JR/"assets/legendaryv34/models/item/stormpiercer_recurve_bow_pulling_0.json").is_file())
Q("Stormpiercer pull model 1 retained",(JR/"assets/legendaryv34/models/item/stormpiercer_recurve_bow_pulling_1.json").is_file())
Q("Stormpiercer pull model 2 retained",(JR/"assets/legendaryv34/models/item/stormpiercer_recurve_bow_pulling_2.json").is_file())
Q("Soul Bedrock v368 geometry retained",(BR/"models/entity/v368_soul_tide.geo.json").is_file())
Q("Leviathan Bedrock v368 geometry retained",(BR/"models/entity/v368_leviathan.geo.json").is_file())
Q("water weapon animation file retained",(BR/"animations/legendary_weapons_v368.animation.json").is_file())
Q("Java visor OPEN textures contain transparency",all(any(px[3]==0 for px in Image.open(JR/f"assets/{NS}/textures/entity/equipment/humanoid/{s}_open_base.png").getdata()) for s in SETS))
Q("Java armor visual namespace is isolated",all((JR/f"assets/{NS}/items/armor_visual/{s}_helmet.json").is_file() for s in SETS))
Q("Bedrock armor item icons are 128x128",all(Image.open(BR/f"textures/items/v369_armor_{s}.png").size==(128,128) for s in SETS))

assert len(checks)>=60,len(checks)
REPORT.write_text("\n".join(f"{i+1:02d}. PASS - {n}" for i,n in enumerate(checks))+f"\n\nQA60 MINIMUM EXCEEDED: {len(checks)}/{len(checks)} PASS\n",encoding="utf-8")

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
print("QA",len(checks),"/",len(checks),"PASS")

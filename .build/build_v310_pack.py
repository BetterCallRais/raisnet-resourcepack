from pathlib import Path
import zipfile,json,shutil,hashlib,math
from PIL import Image,ImageDraw,ImageFilter

BASE=Path("LegendaryRais-Java-26.1.2-v2.9.6-ABSOLUTE-WATER.zip")
ROOT=Path(".build/v310-pack")
OUT=Path("LegendaryRais-Java-26.1.2-v3.1.0-REALISTIC-ARSENAL.zip")
SHA=Path("LegendaryRais-Java-26.1.2-v3.1.0-REALISTIC-ARSENAL.sha1")
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z:
    assert z.testzip() is None
    z.extractall(ROOT)

def save(rel,obj):
    p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def tex(name,c1,c2,accent,kind="metal"):
    W=1024;H=1024
    im=Image.new("RGBA",(W,H)); px=im.load()
    for y in range(H):
        t=y/(H-1)
        for x in range(W):
            grain=(math.sin(y*.11)+math.sin(x*.017+y*.037)+math.cos(x*.029))*.018
            r=int(max(0,min(255,(c1[0]*(1-t)+c2[0]*t)*(0.90+0.10*math.sin(math.pi*x/W))+grain*255)))
            g=int(max(0,min(255,(c1[1]*(1-t)+c2[1]*t)*(0.90+0.10*math.sin(math.pi*x/W))+grain*255)))
            b=int(max(0,min(255,(c1[2]*(1-t)+c2[2]*t)*(0.90+0.10*math.sin(math.pi*x/W))+grain*255)))
            mark=False
            if kind=="ember": mark=((x+2*y)%257)<5
            elif kind=="void": mark=((3*x-y)%331)<4
            elif kind=="storm": mark=abs(((x-y)%353)-176)<2
            elif kind=="gaia": mark=((x//96+y//96)%9==0 and x%96<4)
            elif kind=="astral": mark=((2*x+3*y)%401)<3
            if mark:r,g,b=accent
            px[x,y]=(r,g,b,255)
    p=ROOT/f"assets/legendaryrais/textures/item/{name}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)

def equiptex(name,c1,c2,accent,leggings=False):
    W,H=1024,512
    im=Image.new("RGBA",(W,H));d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/(H-1);c=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))+(255,)
        d.line((0,y,W,y),fill=c)
    # dark segmented plate seams + colored rivets; deliberately no white
    dark=tuple(max(0,int(v*.38)) for v in c1)+(255,)
    for x in range(0,W,128): d.rectangle((x,0,x+5,H),fill=dark)
    for y in range(0,H,128): d.rectangle((0,y,W,y+5),fill=dark)
    for x in range(64,W,128):
        for y in range(64,H,128): d.ellipse((x-5,y-5,x+5,y+5),fill=accent+(255,))
    p=ROOT/f"assets/legendaryrais/textures/entity/equipment/{'humanoid_leggings' if leggings else 'humanoid'}/{name}.png"
    p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)

def cube(a,b,t,rot=None):
    f={k:{"texture":"#"+t} for k in ("north","south","east","west","up","down")}
    o={"from":[round(v,3) for v in a],"to":[round(v,3) for v in b],"faces":f}
    if rot:o["rotation"]={"origin":rot[0],"axis":rot[1],"angle":rot[2],"rescale":True}
    return o

def itemmodel(name,textures,e,gui=.62):
    save(f"assets/legendaryrais/models/item/{name}.json",{
      "credit":"LegendaryRais v3.1 realistic","ambientocclusion":False,
      "textures":dict(textures,particle=next(iter(textures.values()))),"elements":e,
      "display":{
       "gui":{"rotation":[25,-35,0],"translation":[0,-1,0],"scale":[gui]*3},
       "firstperson_righthand":{"rotation":[0,-90,25],"translation":[1,3,1],"scale":[.82]*3},
       "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,1,-3],"scale":[.68]*3},
       "ground":{"scale":[.52]*3},"fixed":{"rotation":[0,180,0],"scale":[.8]*3}}})
    save(f"assets/legendaryrais/items/{name}.json",{"hand_animation_on_swap":True,"oversized_in_gui":True,"model":{"type":"minecraft:model","model":f"legendaryrais:item/{name}"}})

def blade(cx,y0,y1,w0,w1,th,main,edge,n=15):
    e=[];step=(y1-y0)/n
    for i in range(n):
        q=i/n;w=w0*(1-q)+w1*q;y=y0+i*step
        e += [cube([cx-w/2,y,8-th/2],[cx+w/2,y+step+.02,8+th/2],main),
              cube([cx-w/2-.12,y+.03,7.7],[cx-w/2+.08,y+step,8.3],edge),
              cube([cx+w/2-.08,y+.03,7.7],[cx+w/2+.12,y+step,8.3],edge)]
    e.append(cube([cx-.18,y1,7.7],[cx+.18,y1+2.5,8.3],edge,([cx,y1+.3,8],"z",45)))
    return e

# ---- realistic weapons ----
def build_weapons():
    # Emberfall Claymore
    tex("ember_steel",(65,38,30),(28,18,18),(190,65,22),"ember");tex("ember_trim",(125,75,52),(58,31,28),(235,112,38),"ember");tex("ember_grip",(54,28,19),(25,16,15),(120,55,24),"ember")
    e=blade(8,4,31,4.2,.7,1.15,"steel","trim",16)
    e += [cube([1.5,2.3,7.1],[7.2,3.6,8.9],"trim",([7,3,8],"z",-22.5)),cube([8.8,2.3,7.1],[14.5,3.6,8.9],"trim",([9,3,8],"z",22.5)),cube([7.2,-7.5,7.2],[8.8,2.5,8.8],"grip"),cube([6.8,-10.2,6.8],[9.2,-7.3,9.2],"trim",([8,-8.5,8],"z",45))]
    itemmodel("emberfall_claymore",{"steel":"legendaryrais:item/ember_steel","trim":"legendaryrais:item/ember_trim","grip":"legendaryrais:item/ember_grip"},e,.55)

    # Noctis Longsword
    tex("noctis_steel",(30,28,38),(8,8,14),(88,45,125),"void");tex("noctis_trim",(84,77,104),(28,24,42),(135,70,175),"void");tex("noctis_grip",(31,22,37),(14,13,20),(80,40,105),"void")
    e=blade(8,4,30,2.8,.45,.90,"steel","trim",16)
    e += [cube([2.3,2.4,7.25],[7.2,3.4,8.75],"trim",([7,3,8],"z",22.5)),cube([8.8,2.4,7.25],[13.7,3.4,8.75],"trim",([9,3,8],"z",-22.5)),cube([7.25,-6.8,7.3],[8.75,2.6,8.7],"grip"),cube([6.9,-9.4,6.9],[9.1,-6.6,9.1],"trim",([8,-8,8],"z",45))]
    itemmodel("noctis_longsword",{"steel":"legendaryrais:item/noctis_steel","trim":"legendaryrais:item/noctis_trim","grip":"legendaryrais:item/noctis_grip"},e)

    # Stormpiercer Recurve Bow
    tex("storm_body",(51,68,78),(22,31,40),(70,155,188),"storm");tex("storm_trim",(106,119,122),(45,64,72),(80,185,215),"storm");tex("storm_grip",(59,42,28),(28,22,20),(95,70,45),"metal")
    e=[cube([7.2,5,7],[8.8,12,9],"grip"),cube([6.7,7,6.5],[9.3,10.3,9.5],"trim")]
    seg=[(8,12,0),(8.5,15,8),(9.4,18,15),(10.7,21,22.5),(11.9,24,30),(12.5,27,45)]
    for x,y,a in seg:
        aa=min(45,a);e.append(cube([x-.5,y,7.2],[x+.5,y+3.4,8.8],"body",([x,y+1.5,8],"z",aa)))
        yl=5-(y-12);e.append(cube([x-.5,yl-3.4,7.2],[x+.5,yl,8.8],"body",([x,yl-1.5,8],"z",-aa)))
    for y in range(-9,29,4):e.append(cube([13.05,y,7.88],[13.18,y+4.1,8.12],"grip"))
    itemmodel("stormpiercer_recurve_bow",{"body":"legendaryrais:item/storm_body","trim":"legendaryrais:item/storm_trim","grip":"legendaryrais:item/storm_grip"},e,.66)

    # Gaia War Spear — no white channels anywhere
    tex("gaia_steel",(75,82,55),(34,43,31),(51,87,45),"gaia");tex("gaia_edge",(112,108,65),(58,65,44),(66,105,48),"gaia");tex("gaia_wood",(72,44,24),(42,28,18),(57,82,43),"gaia")
    e=[cube([7.35,-17,7.35],[8.65,20,8.65],"wood")]
    for y in range(-14,19,3):e.append(cube([7.12,y,7.12],[8.88,y+.22,8.88],"edge"))
    widths=[1.2,2,2.8,3.5,3.8,3.3,2.5,1.5,.55]
    for i,w in enumerate(widths):
        y=20+i*1.5;e.append(cube([8-w/2,y,7.25],[8+w/2,y+1.53,8.75],"steel"))
        e += [cube([8-w/2-.10,y+.04,7.55],[8-w/2+.10,y+1.5,8.45],"edge"),cube([8+w/2-.10,y+.04,7.55],[8+w/2+.10,y+1.5,8.45],"edge")]
    itemmodel("gaia_war_spear",{"steel":"legendaryrais:item/gaia_steel","edge":"legendaryrais:item/gaia_edge","wood":"legendaryrais:item/gaia_wood"},e,.56)

    # Astral Twin Daggers
    tex("astral_steel",(53,44,80),(19,16,36),(110,67,150),"astral");tex("astral_trim",(104,88,132),(43,33,67),(174,102,198),"astral");tex("astral_grip",(38,26,45),(18,15,25),(95,55,115),"astral")
    e=[]
    for cx,a in ((5.7,-8),(10.3,8)):
        e+=blade(cx,2.5,17.5,1.8,.25,.68,"steel","trim",9)
        e += [cube([cx-1.5,.8,7.25],[cx+1.5,2.2,8.75],"trim",([cx,1.5,8],"z",a)),cube([cx-.6,-5.7,7.4],[cx+.6,1.2,8.6],"grip"),cube([cx-.9,-7.5,7.1],[cx+.9,-5.6,8.9],"trim",([cx,-6.5,8],"z",45))]
    itemmodel("astral_twin_daggers",{"steel":"legendaryrais:item/astral_steel","trim":"legendaryrais:item/astral_trim","grip":"legendaryrais:item/astral_grip"},e,.58)

# ---- wearable armor ----
PAL={
"phoenix":((93,38,17),(190,76,25),(232,157,61),"ember"),
"voidwalker":((22,19,31),(57,39,78),(119,68,145),"void"),
"titan":((48,60,51),(88,101,84),(143,127,72),"gaia"),
"celestial":((68,82,94),(139,158,170),(91,157,188),"storm"),
"water_sovereign":((15,49,68),(23,105,137),(67,177,199),"storm")}

def armor_item(setn,piece):
    e=[]
    if piece=="helmet": e=[cube([3,3,3.5],[13,13,12.5],"metal"),cube([4,3,2.6],[12,5,4],"trim"),cube([2.3,6,4.2],[4.2,12,11.8],"trim",([3.5,8,8],"z",-22.5)),cube([11.8,6,4.2],[13.7,12,11.8],"trim",([12.5,8,8],"z",22.5))]
    elif piece=="chest": e=[cube([3,0,5.2],[13,14,10.8],"metal"),cube([.8,6,5.4],[4,13,10.6],"trim",([3,8,8],"z",-22.5)),cube([12,6,5.4],[15.2,13,10.6],"trim",([13,8,8],"z",22.5)),cube([4.4,6,3.9],[11.6,11.5,5.8],"trim")]
    elif piece=="legs": e=[cube([3,-2,5.3],[7.2,13,10.7],"metal"),cube([8.8,-2,5.3],[13,13,10.7],"metal"),cube([4,10,4.5],[12,14,11.5],"trim")]
    else:e=[cube([3,-1.5,5.1],[7.2,11.5,10.9],"metal"),cube([8.8,-1.5,5.1],[13,11.5,10.9],"metal"),cube([2.5,7,4.6],[7.7,11.6,11.4],"trim"),cube([8.3,7,4.6],[13.5,11.6,11.4],"trim")]
    # distinct silhouette accents
    if setn=="phoenix" and piece in ("helmet","chest"):e.append(cube([7.4,11,6.5],[8.6,17,9.5],"trim",([8,12,8],"z",22.5)))
    if setn=="titan" and piece=="chest":e += [cube([1,10,4.7],[5,15,11.3],"metal"),cube([11,10,4.7],[15,15,11.3],"metal")]
    if setn=="water_sovereign" and piece=="helmet":e += [cube([2.8,10,5.5],[5,16,10.5],"trim",([4,11,8],"z",-22.5)),cube([11,10,5.5],[13.2,16,10.5],"trim",([12,11,8],"z",22.5))]
    save(f"assets/legendaryrais/models/item/armor/{setn}_{piece}.json",{"ambientocclusion":False,"textures":{"metal":f"legendaryrais:item/armor_{setn}_metal","trim":f"legendaryrais:item/armor_{setn}_trim","particle":f"legendaryrais:item/armor_{setn}_metal"},"elements":e,"display":{"gui":{"rotation":[20,-32,0],"scale":[.86]*3}}})
    save(f"assets/legendaryrais/items/armor/{setn}_{piece}.json",{"oversized_in_gui":True,"model":{"type":"minecraft:model","model":f"legendaryrais:item/armor/{setn}_{piece}"}})

def build_armor():
    for n,(a,b,c,k) in PAL.items():
        tex(f"armor_{n}_metal",a,b,c,k);tex(f"armor_{n}_trim",tuple(min(255,x+30) for x in b),tuple(max(0,x//2) for x in a),c,k)
        equiptex(n,a,b,c,False);equiptex(n,a,b,c,True)
        # correct modern equipment path: assets/<namespace>/equipment/
        save(f"assets/legendaryrais/equipment/{n}_set.json",{"layers":{"humanoid":[{"texture":f"legendaryrais:{n}"}],"humanoid_leggings":[{"texture":f"legendaryrais:{n}"}]}})
        for p in ("helmet","chest","legs","boots"):armor_item(n,p)

# ---- distinct non-water FX ----
def fx(name,setn,kind):
    e=[];t="main"
    if kind=="slash":
        for i,a in enumerate((-45,-22.5,0,22.5,45)):e.append(cube([2.5,5+i*1.2,7.55],[13.5,5.5+i*1.2,8.45],t,([8,8,8],"z",a)))
    elif kind=="cage":
        for i in range(8):
            a=i*math.pi/4;x=8+math.cos(a)*5;z=8+math.sin(a)*5;e.append(cube([x-.25,2,z-.25],[x+.25,14,z+.25],t))
    elif kind=="vortex":
        for rr,yy,n in ((6,5,16),(4.5,8,12),(3,11,8)):
            for i in range(n):
                a=2*math.pi*i/n;x=8+math.cos(a)*rr;z=8+math.sin(a)*rr;e.append(cube([x-.7,yy-.2,z-.18],[x+.7,yy+.2,z+.18],t))
    elif kind=="bolt":
        for i in range(8):e.append(cube([7.7+i*.3,3+i*1.35,7.65],[8.3+i*.3,5+i*1.35,8.35],t,([8,8,8],"z",22.5 if i%2 else -22.5)))
    elif kind=="spikes":
        for i in range(10):
            a=2*math.pi*i/10;x=8+math.cos(a)*5;z=8+math.sin(a)*5;e.append(cube([x-.35,2,z-.35],[x+.35,11,z+.35],t,([x,2,z],"z",22.5 if i%2 else -22.5)))
    elif kind=="stars":
        for i in range(6):
            a=2*math.pi*i/6;x=8+math.cos(a)*5;z=8+math.sin(a)*5;e += [cube([x-.2,6,z-1.4],[x+.2,10,z+1.4],t,([x,8,z],"z",45)),cube([x-1.4,7.8,z-.2],[x+1.4,8.2,z+.2],t,([x,8,z],"z",45))]
    else:
        for i in range(16):
            a=2*math.pi*i/16;x=8+math.cos(a)*5;z=8+math.sin(a)*5;e.append(cube([x-.6,7.7,z-.15],[x+.6,8.3,z+.15],t))
    save(f"assets/legendaryrais/models/item/{name}.json",{"ambientocclusion":False,"textures":{"main":f"legendaryrais:item/armor_{setn}_trim","particle":f"legendaryrais:item/armor_{setn}_trim"},"elements":e})
    save(f"assets/legendaryrais/items/{name}.json",{"model":{"type":"minecraft:model","model":f"legendaryrais:item/{name}"}})

build_weapons();build_armor()
for n,s,k in [
("fx_ember_rift","phoenix","slash"),("fx_ember_meteor","phoenix","bolt"),("fx_inferno_crown","phoenix","vortex"),
("fx_shade_step","voidwalker","bolt"),("fx_soul_harvest","voidwalker","slash"),("fx_eclipse_cage","voidwalker","cage"),
("fx_gale_bolt","celestial","bolt"),("fx_cyclone_volley","celestial","vortex"),("fx_thunderhead","celestial","stars"),
("fx_rootline","titan","spikes"),("fx_stoneguard","titan","cage"),("fx_worldspike","titan","spikes"),
("fx_rift_blink","celestial","vortex"),("fx_star_shards","celestial","stars"),("fx_dimension_rend","celestial","slash"),
("fx_phoenix_rebirth","phoenix","stars"),("fx_void_phase","voidwalker","vortex"),("fx_titan_bastion","titan","cage"),("fx_celestial_sanctuary","celestial","stars"),
("fx_water_sovereign_guard","water_sovereign","vortex")]:fx(n,s,k)

save("pack.mcmeta",{"pack":{"description":"LegendaryRais v3.1 REALISTIC ARSENAL • untouched premium Water Relics • realistic weapons + wearable armor","min_format":[84,0],"max_format":[84,0]}})

# Verify premium water assets are byte-identical to the v2.9.6 base.
water=["assets/soultide/models/item/soul_tide_sovereign_blade.json","assets/legendaryrais/models/item/abyss_leviathan_trident.json","assets/legendaryrais/models/item/fx_leviathan_projectile.json"]
with zipfile.ZipFile(BASE) as b:
    for rel in water: assert hashlib.sha256((ROOT/rel).read_bytes()).digest()==hashlib.sha256(b.read(rel)).digest(),rel
for p in ROOT.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
for n in PAL:assert (ROOT/f"assets/legendaryrais/equipment/{n}_set.json").is_file()
if OUT.exists():OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:assert z.testzip() is None
h=hashlib.sha1(OUT.read_bytes()).hexdigest();SHA.write_text(h+"\n")
print("PACK_OK",OUT.stat().st_size,h)

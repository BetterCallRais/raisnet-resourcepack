from pathlib import Path
import json, math, random, shutil, zipfile, hashlib
from PIL import Image, ImageDraw, ImageFilter

JBASE=Path("LegendaryRais-Java-26.1.2-v3.6.4-BEDROCK-RIG-VISOR.zip")
BBASE=Path("LegendaryRais-Bedrock-v3.6.4-BEDROCK-RIG-VISOR.mcpack")
MBASE=Path("LegendaryRais-Geyser-v3.6.4-mappings.json")
JOUT=Path("LegendaryRais-Java-26.1.2-v3.6.5-WEAPON-RIG-ARMOR-SKILL.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.6.5-WEAPON-RIG-ARMOR-SKILL.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.6.5-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.6.5-WEAPON-RIG-ARMOR-SKILL.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.6.5-WEAPON-RIG-ARMOR-SKILL.sha1")
ROOT=Path(".build/generated-v365");JR=ROOT/"java";BR=ROOT/"bedrock";NS="legendaryv34"

shutil.rmtree(ROOT,ignore_errors=True);JR.mkdir(parents=True);BR.mkdir(parents=True)
with zipfile.ZipFile(JBASE) as z:z.extractall(JR)
with zipfile.ZipFile(BBASE) as z:z.extractall(BR)

W={
"emberfall_claymore":((50,13,6),(169,52,14),(255,144,37),"fire"),
"noctis_longsword":((11,8,24),(69,29,110),(207,85,255),"void"),
"stormpiercer_recurve_bow":((10,31,47),(40,124,161),(87,239,255),"electro"),
"gaia_war_spear":((20,44,46),(65,154,140),(202,255,230),"wind"),
"astral_frost_greataxe":((16,45,72),(72,166,210),(220,253,255),"ice")
}
SETS=("phoenix","voidwalker","titan","celestial","water_sovereign")

def wr(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def elemental_texture(size,base,mid,glow,kind,seed):
    rnd=random.Random(seed);im=Image.new("RGBA",(size,size),base+(255,));px=im.load()
    for y in range(size):
        for x in range(size):
            nx=x/(size-1);ny=y/(size-1)
            bevel=max(0.0,1-abs(nx-.42)/.24)*.20
            bands=.07*math.sin((nx*6+ny*2)*math.pi)+.035*math.sin((ny*11-nx*2)*math.pi)
            grain=rnd.uniform(-.018,.018)
            t=max(0,min(.55,.12+.24*nx+.12*(1-ny)+bevel+bands+grain))
            c=tuple(max(0,min(255,int(base[i]*(1-t)+mid[i]*t))) for i in range(3))
            px[x,y]=c+(255,)
    d=ImageDraw.Draw(im,"RGBA");w=max(1,size//128)
    # crisp mythic engravings; cheap at runtime because still one texture.
    d.rectangle((size*.035,size*.035,size*.965,size*.965),outline=mid+(58,),width=w)
    if kind=="fire":
        for cx in (.22,.50,.78):
            d.line((size*cx,size*.91,size*(cx-.06),size*.64,size*(cx+.02),size*.42,size*(cx-.025),size*.20),fill=glow+(135,),width=2*w)
    elif kind=="void":
        d.arc((size*.10,size*.12,size*.90,size*.88),205,343,fill=glow+(125,),width=2*w)
        d.arc((size*.23,size*.25,size*.77,size*.79),25,160,fill=mid+(105,),width=w)
        for x,y in ((.18,.28),(.38,.68),(.70,.32),(.83,.76)):d.ellipse((size*x-2*w,size*y-2*w,size*x+2*w,size*y+2*w),fill=glow+(180,))
    elif kind=="electro":
        for off in (0,.16):
            d.line((size*(.68-off),size*.06,size*(.45-off),size*.36,size*(.57-off),size*.40,size*(.33-off),size*.90),fill=glow+(150,),width=2*w)
    elif kind=="wind":
        for yy in (.25,.48,.72):d.arc((size*.07,size*(yy-.15),size*.93,size*(yy+.16)),192,344,fill=glow+(105,),width=2*w)
        d.line((size*.18,size*.82,size*.82,size*.18),fill=mid+(65,),width=w)
    elif kind=="ice":
        for a in range(0,360,45):
            x=size*.5+math.cos(math.radians(a))*size*.35;y=size*.5+math.sin(math.radians(a))*size*.35
            d.line((size*.5,size*.5,x,y),fill=glow+(125,),width=2*w)
        for x in (.28,.50,.72):d.polygon([(size*x,size*.08),(size*(x+.06),size*.30),(size*x,size*.46),(size*(x-.05),size*.29)],outline=glow+(145,))
    return im.filter(ImageFilter.UnsharpMask(radius=max(1,size//128),percent=170,threshold=2))

# ------------------------------------------------------------------
# Java: center geometry on the actual item-model Z pivot and retune hand transforms.
# ------------------------------------------------------------------
TRANS={
"emberfall_claymore":{
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,3.35,.10],"scale":[.60,.60,.60]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,3.35,.10],"scale":[.60,.60,.60]},
 "firstperson_righthand":{"rotation":[0,-90,25],"translation":[1.10,3.25,.35],"scale":[.68,.68,.68]},
 "firstperson_lefthand":{"rotation":[0,90,-25],"translation":[1.10,3.25,.35],"scale":[.68,.68,.68]}},
"noctis_longsword":{
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,3.55,.10],"scale":[.63,.63,.63]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,3.55,.10],"scale":[.63,.63,.63]},
 "firstperson_righthand":{"rotation":[0,-90,24],"translation":[1.05,3.40,.30],"scale":[.70,.70,.70]},
 "firstperson_lefthand":{"rotation":[0,90,-24],"translation":[1.05,3.40,.30],"scale":[.70,.70,.70]}},
"stormpiercer_recurve_bow":{
 "thirdperson_righthand":{"rotation":[-7,-90,5],"translation":[0,2.10,.10],"scale":[.61,.61,.61]},
 "thirdperson_lefthand":{"rotation":[-7,90,-5],"translation":[0,2.10,.10],"scale":[.61,.61,.61]},
 "firstperson_righthand":{"rotation":[-5,-92,3],"translation":[1.0,1.8,.45],"scale":[.72,.72,.72]},
 "firstperson_lefthand":{"rotation":[-5,92,-3],"translation":[1.0,1.8,.45],"scale":[.72,.72,.72]}},
"gaia_war_spear":{
 "thirdperson_righthand":{"rotation":[0,-90,58],"translation":[0,2.45,.05],"scale":[.47,.47,.47]},
 "thirdperson_lefthand":{"rotation":[0,90,-58],"translation":[0,2.45,.05],"scale":[.47,.47,.47]},
 "firstperson_righthand":{"rotation":[0,-90,28],"translation":[1.0,2.25,.35],"scale":[.53,.53,.53]},
 "firstperson_lefthand":{"rotation":[0,90,-28],"translation":[1.0,2.25,.35],"scale":[.53,.53,.53]}},
"astral_frost_greataxe":{
 "thirdperson_righthand":{"rotation":[0,-90,53],"translation":[0,3.0,.08],"scale":[.54,.54,.54]},
 "thirdperson_lefthand":{"rotation":[0,90,-53],"translation":[0,3.0,.08],"scale":[.54,.54,.54]},
 "firstperson_righthand":{"rotation":[0,-90,22],"translation":[1.0,2.85,.35],"scale":[.60,.60,.60]},
 "firstperson_lefthand":{"rotation":[0,90,-22],"translation":[1.0,2.85,.35],"scale":[.60,.60,.60]}}
}
COMMON={"gui":{"rotation":[25,-35,0],"translation":[0,0,0],"scale":[.54,.54,.54]},
        "ground":{"translation":[0,2,0],"scale":[.38,.38,.38]},
        "fixed":{"rotation":[0,180,0],"scale":[.58,.58,.58]}}

def add_element(obj,fr,to,tex,rot=None):
    faces={f:{"texture":"#"+tex} for f in ("north","south","east","west","up","down")}
    e={"from":[round(x,3) for x in fr],"to":[round(x,3) for x in to],"faces":faces}
    if rot:e["rotation"]={"origin":rot[0],"axis":rot[1],"angle":rot[2],"rescale":True}
    obj.setdefault("elements",[]).append(e)

for name,(base,mid,glow,kind) in W.items():
    modelp=JR/f"assets/{NS}/models/item/{name}.json";obj=json.loads(modelp.read_text())
    # Recenter all geometry from the old z~=0 plane to the standard item model pivot z=8.
    zs=[]
    for e in obj.get("elements",[]):
        for key in ("from","to"):
            if key in e:zs.append(float(e[key][2]))
        if isinstance(e.get("rotation"),dict) and "origin" in e["rotation"]:zs.append(float(e["rotation"]["origin"][2]))
    center=(min(zs)+max(zs))/2 if zs else 8.0
    dz=8.0-center
    for e in obj.get("elements",[]):
        for key in ("from","to"):
            if key in e:e[key][2]=round(float(e[key][2])+dz,4)
        if isinstance(e.get("rotation"),dict) and "origin" in e["rotation"]:
            e["rotation"]["origin"][2]=round(float(e["rotation"]["origin"][2])+dz,4)

    # Extra small silhouette accents; no huge blocky shapes.
    if name=="emberfall_claymore":
        add_element(obj,(6.7,6.7,7.35),(9.3,8.2,8.65),"accent")
        add_element(obj,(5.1,7.0,7.55),(6.8,9.0,8.45),"metal",([6.7,8,8],"z",-22.5))
        add_element(obj,(9.2,7.0,7.55),(10.9,9.0,8.45),"metal",([9.3,8,8],"z",22.5))
    elif name=="noctis_longsword":
        add_element(obj,(5.9,6.8,7.5),(7.3,9.1,8.5),"accent",([7.2,7.8,8],"z",-22.5))
        add_element(obj,(8.7,6.8,7.5),(10.1,9.1,8.5),"accent",([8.8,7.8,8],"z",22.5))
    elif name=="stormpiercer_recurve_bow":
        add_element(obj,(7.35,6.6,7.1),(8.65,9.4,8.9),"accent")
    elif name=="gaia_war_spear":
        add_element(obj,(5.9,24.0,7.55),(7.0,28.8,8.45),"accent",([7,25.5,8],"z",-22.5))
        add_element(obj,(9.0,24.0,7.55),(10.1,28.8,8.45),"accent",([9,25.5,8],"z",22.5))
    else:
        add_element(obj,(5.1,21.8,7.4),(7.2,25.5,8.6),"accent",([7,23.5,8],"z",-22.5))
        add_element(obj,(8.8,21.8,7.4),(10.9,25.5,8.6),"accent",([9,23.5,8],"z",22.5))

    # New coherent material textures.
    for key,(a,b,k) in {
        "metal":(base,mid,kind),
        "grip":((22,17,15),(83,59,40),"neutral"),
        "accent":(mid,glow,kind)
    }.items():
        im=elemental_texture(256,a,b,glow,k,name+"-"+key+"-365")
        tp=JR/f"assets/{NS}/textures/item/v365/{name}_{key}.png";tp.parent.mkdir(parents=True,exist_ok=True);im.save(tp,optimize=True)
        obj.setdefault("textures",{})[key]=f"{NS}:item/v365/{name}_{key}"
    disp=dict(COMMON);disp.update(TRANS[name]);obj["display"]=disp;obj["gui_light"]="front"
    modelp.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

# ------------------------------------------------------------------
# Armor texture polish: preserve v3.6.4 art, add sharper set identity.
# ------------------------------------------------------------------
def polish_armor(im,setn):
    im=im.convert("RGBA");d=ImageDraw.Draw(im,"RGBA");w,h=im.size
    def line(points,fill,width=1):d.line(points,fill=fill,width=width)
    if setn=="phoenix":
        col=(255,178,48,175);line([(4,4),(8,1),(12,4),(8,7),(4,4)],col);line([(20,22),(24,17),(28,22)],col)
    elif setn=="voidwalker":
        col=(206,92,255,165);d.arc((3,2,15,12),200,340,fill=col,width=1);d.rectangle((24,18,25,19),fill=col)
    elif setn=="titan":
        col=(192,223,117,165);d.rectangle((3,3,14,4),fill=col);d.rectangle((20,18,31,19),fill=col);d.rectangle((38,18,49,19),fill=col)
    elif setn=="celestial":
        col=(210,245,255,180)
        for x,y in ((8,5),(24,19),(42,6),(54,22)):d.point((x,y),fill=col);d.point((x+1,y),fill=col);d.point((x,y+1),fill=col)
    else:
        col=(91,231,251,170);d.arc((2,3,15,12),0,180,fill=col,width=1);d.arc((19,18,32,27),180,355,fill=col,width=1);d.arc((39,18,52,27),180,355,fill=col,width=1)
    return im

for s in SETS:
    for sub in ("humanoid","humanoid_leggings"):
        p=JR/f"assets/{NS}/textures/entity/equipment/{sub}/{s}_set.png"
        if p.is_file():polish_armor(Image.open(p),s).save(p,optimize=True)
    # open visor texture is separate.
    p=JR/f"assets/{NS}/textures/entity/equipment/humanoid/{s}_helmet_open.png"
    if p.is_file():polish_armor(Image.open(p),s).save(p,optimize=True)
    for layer in (1,2):
        p=BR/f"textures/models/armor/{s}_{layer}.png"
        if p.is_file():polish_armor(Image.open(p),s).save(p,optimize=True)

# ------------------------------------------------------------------
# Bedrock weapons: correct bound-bone placement with first/third-person animations.
# Bound item models require positioning animations; third-person includes the known -24 Y correction.
# ------------------------------------------------------------------
BED_SCALE={
 "emberfall_claymore":(.72,.80),
 "noctis_longsword":(.76,.84),
 "stormpiercer_recurve_bow":(.70,.76),
 "gaia_war_spear":(.63,.69),
 "astral_frost_greataxe":(.66,.72)
}
ANIMS={"format_version":"1.8.0","animations":{}}
for name,(base,mid,glow,kind) in W.items():
    # New texture palette but same validated low-cube geometry.
    im=elemental_texture(128,base,mid,glow,kind,"bed-"+name+"-365")
    tp=BR/f"textures/items/{name}.png";tp.parent.mkdir(parents=True,exist_ok=True);im.save(tp,optimize=True)

    third,first=BED_SCALE[name]
    third_name=f"animation.raisnet.{name}.hold_third_person"
    first_name=f"animation.raisnet.{name}.hold_first_person"
    ANIMS["animations"][third_name]={
      "loop":True,
      "bones":{"bb_main":{"position":[0,-24,0],"rotation":[0,0,0],"scale":[third,third,third]}}
    }
    # First-person remains close to hand, not floating across the screen.
    first_rot=[0,0,0]
    if name=="stormpiercer_recurve_bow":first_rot=[0,-6,0]
    elif name=="gaia_war_spear":first_rot=[0,0,-5]
    elif name=="astral_frost_greataxe":first_rot=[0,0,-6]
    ANIMS["animations"][first_name]={
      "loop":True,
      "bones":{"bb_main":{"position":[2.2,-26.0,4.0],"rotation":first_rot,"scale":[first,first,first]}}
    }

    ap=BR/f"attachables/{name}.player.json";a=json.loads(ap.read_text())
    d=a["minecraft:attachable"]["description"]
    d["animations"]={"hold_first_person":first_name,"hold_third_person":third_name}
    d["scripts"]={"animate":[
      {"hold_first_person":"context.is_first_person == 1.0"},
      {"hold_third_person":"context.is_first_person == 0.0"}
    ]}
    d["render_controllers"]=["controller.render.item_default"]
    ap.write_text(json.dumps(a,separators=(",",":")),encoding="utf-8")

wr(BR/"animations/legendary_weapons_v365.animation.json",ANIMS)

# Add restrained extra armor geometry accents (still low-cost).
for s in SETS:
    # chest
    gp=BR/f"models/entity/armor_{s}_chest_v364.geo.json"
    if gp.is_file():
        g=json.loads(gp.read_text());bones=g["minecraft:geometry"][0]["bones"]
        body=next((b for b in bones if b["name"]=="chestplate"),None)
        if body is not None:
            if s=="phoenix":body.setdefault("cubes",[]).append({"origin":[-1.2,9.0,-3.65],"size":[2.4,2.4,.55],"uv":[54,22],"inflate":.03})
            elif s=="voidwalker":body.setdefault("cubes",[]).append({"origin":[-2.5,7.2,-3.65],"size":[5,1.0,.55],"uv":[52,22],"inflate":.03})
            elif s=="titan":body.setdefault("cubes",[]).append({"origin":[-2.0,8.5,-3.65],"size":[4,2.0,.55],"uv":[52,22],"inflate":.04})
            elif s=="celestial":body.setdefault("cubes",[]).append({"origin":[-.8,9.5,-3.65],"size":[1.6,1.6,.55],"uv":[55,22],"inflate":.03})
            else:body.setdefault("cubes",[]).append({"origin":[-2.6,7.5,-3.65],"size":[5.2,1.0,.55],"uv":[52,22],"inflate":.03})
        gp.write_text(json.dumps(g,separators=(",",":")),encoding="utf-8")

# ------------------------------------------------------------------
# Geyser mapping consistency
# ------------------------------------------------------------------
mapping=json.loads(MBASE.read_text())
weapon_models={
 f"{NS}:emberfall_claymore":"raisnet:emberfall_claymore",
 f"{NS}:noctis_longsword":"raisnet:noctis_longsword",
 f"{NS}:stormpiercer_recurve_bow":"raisnet:stormpiercer_recurve_bow",
 f"{NS}:gaia_war_spear":"raisnet:gaia_war_spear",
 f"{NS}:astral_frost_greataxe":"raisnet:astral_frost_greataxe"
}
for model,ident in weapon_models.items():
    defs=[d for arr in mapping["items"].values() for d in arr if d.get("type")=="definition" and d.get("model")==model]
    if len(defs)!=1:raise RuntimeError((model,"mapping count",len(defs)))
    d=defs[0];d["bedrock_identifier"]=ident;d.setdefault("bedrock_options",{})["display_handheld"]=True
    if model.endswith("stormpiercer_recurve_bow"):d.pop("components",None)
MOUT.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# Fresh identities.
jm=JR/"pack.mcmeta";meta=json.loads(jm.read_text())
meta["pack"]["description"]="LegendaryRais v3.6.5 WEAPON RIG + ARMOR SKILL | centered Java grip | animated Bedrock weapons"
jm.write_text(json.dumps(meta,separators=(",",":")),encoding="utf-8")
mf=BR/"manifest.json";bm=json.loads(mf.read_text())
bm["header"]["name"]="RaisNet LegendaryRais v3.6.5 Weapon Rig Armor Skill"
bm["header"]["description"]="Centered weapon rigs + first/third person Bedrock animations + enhanced armor design"
bm["header"]["uuid"]="a1ca4c8e-c56a-4f6f-a745-b402a906871f";bm["header"]["version"]=[3,6,5]
bm["modules"][0]["uuid"]="e6c87c32-09f4-43fc-bdab-003968701f24";bm["modules"][0]["version"]=[3,6,5]
mf.write_text(json.dumps(bm,separators=(",",":")),encoding="utf-8")

# ------------------------------------------------------------------
# Exhaustive validation
# ------------------------------------------------------------------
for root in (JR,BR):
    for p in root.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
    for p in root.rglob("*.png"):
        with Image.open(p) as im:im.verify()

# Java weapon grip/model center checks.
for name in W:
    p=JR/f"assets/{NS}/models/item/{name}.json";obj=json.loads(p.read_text())
    assert 8<=len(obj.get("elements",[]))<=32,(name,len(obj.get("elements",[])))
    zs=[]
    grips=[]
    for e in obj["elements"]:
        zs += [float(e["from"][2]),float(e["to"][2])]
        if any(v.get("texture")=="#grip" for v in e["faces"].values()):grips.append(e)
        for v in e["from"]+e["to"]:
            assert -16<=float(v)<=32,(name,"bounds",v)
    assert 7.0<=sum(zs)/len(zs)<=9.0,(name,"z center",sum(zs)/len(zs))
    assert grips,(name,"no grip")
    assert any(e["from"][0]<=8<=e["to"][0] and e["from"][1]<=4<=e["to"][1] for e in grips),(name,"grip anchor")
    tp=obj["display"]["thirdperson_righthand"]
    assert abs(tp["translation"][0])<=.05,(name,tp)
    assert abs(tp["translation"][2])<=.15,(name,tp)
    for key in ("metal","grip","accent"):
        ref=obj["textures"][key];nsp,path=ref.split(":",1)
        im=Image.open(JR/f"assets/{nsp}/textures/{path}.png");assert im.size==(256,256)

# Bedrock weapon attachables now MUST have positioning animations.
anim=json.loads((BR/"animations/legendary_weapons_v365.animation.json").read_text())["animations"]
for name in W:
    ap=BR/f"attachables/{name}.player.json";a=json.loads(ap.read_text())["minecraft:attachable"]["description"]
    assert a["identifier"]==f"raisnet:{name}"
    assert set(a["animations"])=={"hold_first_person","hold_third_person"}
    assert len(a["scripts"]["animate"])==2
    for ref in a["animations"].values():assert ref in anim,(name,ref)
    third=anim[a["animations"]["hold_third_person"]]["bones"]["bb_main"]
    assert third["position"][1]==-24,(name,third)
    assert a["render_controllers"]==["controller.render.item_default"]
    assert (BR/f"models/entity/{name}.geo.json").is_file()
    im=Image.open(BR/f"textures/items/{name}.png");assert im.size==(128,128)

# All mapped weapon definitions resolve to pack assets and unique identifiers.
idents=set()
for model,ident in weapon_models.items():
    defs=[d for arr in mapping["items"].values() for d in arr if d.get("type")=="definition" and d.get("model")==model]
    assert len(defs)==1
    d=defs[0];assert d["bedrock_identifier"]==ident
    assert ident not in idents;idents.add(ident)
    key=ident.split(":",1)[1]
    assert (BR/f"attachables/{key}.player.json").is_file()
    atlas=json.loads((BR/"textures/item_texture.json").read_text())["texture_data"]
    assert d["bedrock_options"]["icon"] in atlas,(model,d["bedrock_options"]["icon"])

# Armor v364 visor and rig files remain complete after polish.
for s in SETS:
    for mode in ("open","closed"):
        assert (JR/f"assets/{NS}/items/armor/{s}_helmet_{mode}.json").is_file()
        assert (JR/f"assets/{NS}/equipment/{s}_helmet_{mode}.json").is_file()
        assert (BR/f"attachables/armor_{s}_helmet_{mode}.json").is_file()
    for piece in ("chest","legs","boots"):assert (BR/f"attachables/armor_{s}_{piece}.json").is_file()

# Water relics frozen.
assert (JR/"assets/soultide/items/soul_tide_sovereign_blade.json").is_file()
assert (JR/"assets/legendaryrais/items/abyss_leviathan_trident.json").is_file()
assert (BR/"models/entity/soul_tide_katana.geo.json").is_file()
assert (BR/"models/entity/abyss_leviathan_trident.geo.json").is_file()

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
print("V365_WEAPON_RIG_ARMOR_SKILL PASS")

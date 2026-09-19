from pathlib import Path
import json, math, shutil, zipfile, hashlib, random
from PIL import Image, ImageDraw, ImageFilter

JBASE=Path("LegendaryRais-Java-26.1.2-v3.5.5-ART-REBUILD.zip")
BBASE=Path("LegendaryRais-Bedrock-v3.5.5-ART-REBUILD.mcpack")
MBASE=Path("LegendaryRais-Geyser-v3.5.5-mappings.json")
JOUT=Path("LegendaryRais-Java-26.1.2-v3.6.0-ELEMENTAL-ELITE.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.6.0-ELEMENTAL-ELITE.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.6.0-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.6.0-ELEMENTAL-ELITE.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.6.0-ELEMENTAL-ELITE.sha1")
ROOT=Path(".build/generated-v360")
JR=ROOT/"java"; BR=ROOT/"bedrock"; NS="legendaryv34"
shutil.rmtree(ROOT,ignore_errors=True); JR.mkdir(parents=True); BR.mkdir(parents=True)
with zipfile.ZipFile(JBASE) as z:z.extractall(JR)
with zipfile.ZipFile(BBASE) as z:z.extractall(BR)

WEAPONS={
 "emberfall_claymore":{"element":"fire","base":(58,18,8),"mid":(145,48,14),"glow":(255,112,25)},
 "noctis_longsword":{"element":"void","base":(14,10,24),"mid":(65,31,95),"glow":(177,72,242)},
 "stormpiercer_recurve_bow":{"element":"electro","base":(17,38,52),"mid":(52,118,148),"glow":(91,230,255)},
 "gaia_war_spear":{"element":"wind","base":(30,48,52),"mid":(90,148,142),"glow":(185,255,221)},
 "astral_twin_daggers":{"element":"ice","base":(24,50,72),"mid":(79,154,191),"glow":(190,244,255)},
}
ARM={
 "phoenix":((64,18,8),(149,48,14),(255,126,28)),
 "voidwalker":((16,11,28),(62,31,91),(186,78,248)),
 "titan":((25,40,29),(77,98,51),(164,205,102)),
 "celestial":((23,42,61),(76,117,151),(170,226,255)),
 "water_sovereign":((9,43,61),(34,106,132),(86,217,244))
}
PIECES=("helmet","chest","legs","boots")
FX={
 "fx_ember_rift":(255,80,20),"fx_ember_meteor":(255,124,24),"fx_inferno_crown":(255,190,50),
 "fx_shade_step":(120,46,180),"fx_soul_harvest":(154,58,224),"fx_eclipse_cage":(84,22,132),
 "fx_thunderhead":(95,225,255),
 "fx_gale_bolt":(184,255,225),"fx_cyclone_volley":(145,235,215),
 "fx_frost_shard":(190,245,255),"fx_glacier_fang":(130,220,255),"fx_absolute_zero":(225,252,255),
 "fx_phoenix_rebirth":(255,128,32),"fx_void_phase":(170,72,240),"fx_titan_bastion":(168,210,108),
 "fx_celestial_sanctuary":(176,228,255),"fx_water_sovereign_guard":(85,220,245)
}

def wr(root,rel,obj):
 p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")
def faces(key):
 return {k:{"texture":"#"+key} for k in ("north","south","east","west","up","down")}
def elem(fr,to,key="metal",rot=None):
 e={"from":[round(x,3) for x in fr],"to":[round(x,3) for x in to],"faces":faces(key)}
 if rot:
  ox,oy,oz,axis,ang=rot
  assert ang in (-45,-22.5,0,22.5,45)
  e["rotation"]={"origin":[ox,oy,oz],"axis":axis,"angle":ang,"rescale":True}
 return e
DISPLAY={
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,4,1],"scale":[.72,.72,.72]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,4,1],"scale":[.72,.72,.72]},
 "firstperson_righthand":{"rotation":[0,-90,22],"translation":[1,3.2,1],"scale":[.84,.84,.84]},
 "firstperson_lefthand":{"rotation":[0,90,-22],"translation":[1,3.2,1],"scale":[.84,.84,.84]},
 "gui":{"rotation":[25,-35,0],"translation":[0,0,0],"scale":[.58,.58,.58]},
 "ground":{"translation":[0,2,0],"scale":[.42,.42,.42]},
 "fixed":{"rotation":[0,180,0],"scale":[.62,.62,.62]}
}

def make_mat(path,base,mid,glow):
 p=path;p.parent.mkdir(parents=True,exist_ok=True)
 im=Image.new("RGBA",(64,64),base+(255,));px=im.load();rnd=random.Random(str(path))
 for y in range(64):
  for x in range(64):
   t=(x/63)*.18+(1-y/63)*.20;n=rnd.randint(-5,5)
   c=tuple(max(0,min(255,int(base[i]*(1-t)+mid[i]*t+n))) for i in range(3));px[x,y]=c+(255,)
 d=ImageDraw.Draw(im,"RGBA")
 d.line((4,8,60,8),fill=glow+(75,),width=1);d.line((8,32,56,32),fill=mid+(45,),width=1)
 d.line((12,58,52,6),fill=glow+(30,),width=1)
 im.save(p,optimize=True)

def weapon_model(name):
 if name=="emberfall_claymore":
  e=[elem((7.2,-14,-.7),(8.8,-12.2,.7),"accent"),elem((7.4,-12.2,-.52),(8.6,-4,.52),"grip")]
  for y in (-10.8,-8.8,-6.8):e.append(elem((7.15,y,-.58),(8.85,y+.25,.58),"accent"))
  e += [elem((3.2,-4.2,-.45),(7.4,-3.3,.45),"accent",(7.3,-3.7,0,"z",-22.5)),elem((8.6,-4.2,-.45),(12.8,-3.3,.45),"accent",(8.7,-3.7,0,"z",22.5))]
  for y,w in [(-3.2,4.2),(2.0,3.8),(7.2,3.4),(12.4,3.0),(17.6,2.5),(22.8,1.8)]:
   e.append(elem((8-w/2,y,-.48),(8+w/2,y+5.1,.48),"metal"))
   e.append(elem((7.82,y+.15,-.58),(8.18,y+4.95,.58),"accent"))
  e += [elem((7.35,27.9,-.34),(8.65,30.4,.34),"metal"),elem((7.72,30.2,-.2),(8.28,31.6,.2),"accent")]
  return e
 if name=="noctis_longsword":
  e=[elem((7.25,-14,-.6),(8.75,-12.4,.6),"accent"),elem((7.45,-12.4,-.43),(8.55,-4.3,.43),"grip"),
     elem((4.5,-4.4,-.3),(7.4,-3.7,.3),"accent",(7.3,-4,0,"z",-45)),elem((8.6,-4.4,-.3),(11.5,-3.7,.3),"accent",(8.7,-4,0,"z",45))]
  for y,w in [(-3.5,2.7),(2.0,2.45),(7.5,2.2),(13.0,1.9),(18.5,1.5),(24.0,1.0)]:
   e.append(elem((8-w/2,y,-.34),(8+w/2,y+5.4,.34),"metal"))
   e.append(elem((7.9,y+.2,-.42),(8.1,y+5.2,.42),"accent"))
  e.append(elem((7.7,29.2,-.2),(8.3,31.5,.2),"accent"));return e
 if name=="stormpiercer_recurve_bow":
  e=[elem((7.25,4.4,-.6),(8.75,11.8,.6),"grip"),elem((6.4,7.1,-.8),(9.6,9.6,.8),"accent")]
  for cx,cy,ang in [(8,12,0),(8.7,15,22.5),(10,18,22.5),(11.3,21,22.5),(12.3,24,22.5),(13,27,45),
                    (8,4.2,0),(7.3,1.1,-22.5),(6,-1.9,-22.5),(4.7,-4.9,-22.5),(3.7,-7.9,-22.5),(3,-10.9,-45)]:
   e.append(elem((cx-.42,cy-1.8,-.42),(cx+.42,cy+1.8,.42),"metal",(cx,cy,0,"z",ang)))
  e += [elem((7.92,-12,-.08),(8.08,8.2,.08),"accent",(8,-2,0,"z",-22.5)),elem((7.92,9.2,-.08),(8.08,30.5,.08),"accent",(8,20,0,"z",22.5))]
  return e
 if name=="gaia_war_spear":
  e=[elem((7.58,-15,-.42),(8.42,19.5,.42),"grip")]
  for y in (-12,-5,2,9,16):e.append(elem((7.3,y,-.5),(8.7,y+.25,.5),"accent"))
  e += [elem((7.1,19,-.42),(8.9,25.0,.42),"metal"),
        elem((5.8,20,-.3),(7.5,25.2,.3),"accent",(7.4,22.4,0,"z",-22.5)),
        elem((8.5,20,-.3),(10.2,25.2,.3),"accent",(8.6,22.4,0,"z",22.5)),
        elem((6.7,24.6,-.34),(9.3,28.8,.34),"metal"),
        elem((7.5,28.7,-.2),(8.5,31.2,.2),"accent")]
  return e
 # ice twin daggers
 e=[]
 for side in (-1,1):
  cx=8+side*2.8
  e += [elem((cx-.55,-10,-.45),(cx+.55,-3.2,.45),"grip"),elem((cx-1.5,-3.4,-.28),(cx+1.5,-2.7,.28),"accent")]
  for y,w in [(-2.5,1.8),(1.4,1.55),(5.3,1.3),(9.2,.95),(13.1,.6)]:
   e.append(elem((cx-w/2,y,-.34),(cx+w/2,y+3.8,.34),"metal"))
  e.append(elem((cx-.16,16.7,-.2),(cx+.16,18.4,.2),"accent"))
  # crystal side fin
  e.append(elem((cx-side*1.1,4.0,-.24),(cx-side*.2,9.4,.24),"accent",(cx-side*.35,6.5,0,"z",22.5*side)))
 return e

# Java true-3D weapons
for name,s in WEAPONS.items():
 for key,(a,b) in {"metal":(s["base"],s["mid"]),"grip":((28,22,18),(70,55,42)),"accent":(s["mid"],s["glow"])}.items():
  make_mat(JR/f"assets/{NS}/textures/item/v360/{name}_{key}.png",a,b,s["glow"])
 wr(JR,f"assets/{NS}/models/item/{name}.json",{"textures":{
  "metal":f"{NS}:item/v360/{name}_metal","grip":f"{NS}:item/v360/{name}_grip","accent":f"{NS}:item/v360/{name}_accent"
 },"elements":weapon_model(name),"display":DISPLAY})
 wr(JR,f"assets/{NS}/items/{name}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/{name}"}})

# Ornate armor texture + icons, native equipment rig retained.
def armor_tex(setn,layer):
 base,mid,glow=ARM[setn];im=Image.new("RGBA",(64,32),base+(255,));px=im.load();rnd=random.Random(setn+str(layer))
 for y in range(32):
  for x in range(64):
   wave=5*math.sin(x*.28)+3*math.sin(y*.55);n=rnd.randint(-3,3)
   px[x,y]=tuple(max(0,min(255,int(base[i]+wave+n+(mid[i]-base[i])*(1-y/31)*.12))) for i in range(3))+(255,)
 d=ImageDraw.Draw(im,"RGBA")
 d.rectangle((1,1,62,30),outline=mid+(80,),width=1)
 # central elite crest repeated within UV-safe zones
 for cx in (8,24,40,56):
  d.line((cx,6,cx-3,11),fill=glow+(110,),width=1);d.line((cx,6,cx+3,11),fill=glow+(110,),width=1)
  d.line((cx-3,11,cx,16),fill=glow+(70,),width=1);d.line((cx+3,11,cx,16),fill=glow+(70,),width=1)
 if setn=="phoenix":
  for cx in (16,48):d.arc((cx-7,17,cx+7,29),190,350,fill=glow+(150,),width=1)
 elif setn=="voidwalker":
  for x,y in ((11,9),(29,21),(45,8),(57,23)):d.ellipse((x-1,y-1,x+1,y+1),fill=glow+(190,))
 elif setn=="titan":
  for x in (12,32,52):d.rectangle((x-4,19,x+4,26),outline=glow+(85,),width=1)
 elif setn=="celestial":
  for x,y in ((10,22),(27,8),(43,24),(58,12)):d.point((x,y),fill=(240,255,255,255))
 else:
  for x in (8,24,40,56):d.arc((x-6,19,x+6,28),0,180,fill=glow+(120,),width=1)
 return im

def armor_icon(setn,piece):
 base,mid,glow=ARM[setn];im=Image.new("RGBA",(64,64),(0,0,0,0));d=ImageDraw.Draw(im,"RGBA")
 fill=base+(255,);edge=mid+(255,);hi=glow+(230,)
 if piece=="helmet":
  d.polygon([(17,17),(25,10),(39,10),(47,17),(44,39),(38,48),(26,48),(20,39)],fill=fill,outline=edge)
  d.polygon([(23,27),(41,27),(38,34),(32,38),(26,34)],fill=(8,8,12,230),outline=hi)
 elif piece=="chest":
  d.polygon([(14,20),(24,12),(40,12),(50,20),(45,51),(19,51)],fill=fill,outline=edge);d.line((32,16,32,48),fill=hi,width=2)
  d.polygon([(32,20),(38,30),(32,42),(26,30)],outline=hi,fill=mid+(120,))
 elif piece=="legs":
  d.polygon([(18,12),(46,12),(44,30),(39,55),(31,55),(29,31),(25,55),(17,55),(20,30)],fill=fill,outline=edge);d.line((32,15,32,31),fill=hi,width=2)
 else:
  d.polygon([(14,22),(28,22),(28,48),(12,55)],fill=fill,outline=edge);d.polygon([(36,22),(50,22),(52,55),(36,48)],fill=fill,outline=edge)
 d.line((21,19,43,19),fill=hi,width=1)
 return im

for setn in ARM:
 for layer,sub in ((1,"humanoid"),(2,"humanoid_leggings")):
  im=armor_tex(setn,layer);p=JR/f"assets/{NS}/textures/entity/equipment/{sub}/{setn}_set.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
  bp=BR/f"textures/models/armor/{setn}_{layer}.png";bp.parent.mkdir(parents=True,exist_ok=True);im.save(bp,optimize=True)
 for piece in PIECES:
  im=armor_icon(setn,piece)
  p=JR/f"assets/{NS}/textures/item/armor/{setn}_{piece}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
  bp=BR/f"textures/items/armor_{setn}_{piece}.png";bp.parent.mkdir(parents=True,exist_ok=True);im.save(bp,optimize=True)

# Java elemental FX sprites/models
for name,col in FX.items():
 im=Image.new("RGBA",(64,64),(0,0,0,0));d=ImageDraw.Draw(im,"RGBA");cx=cy=32
 for r,a in [(25,35),(19,60),(13,105)]:
  d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=col+(a,),width=2)
 if "gale" in name or "cyclone" in name:
  d.arc((8,12,56,52),20,310,fill=col+(235,),width=5)
 elif "frost" in name or "glacier" in name or "zero" in name:
  for ang in range(0,360,60):
   x=cx+int(math.cos(math.radians(ang))*25);y=cy+int(math.sin(math.radians(ang))*25);d.line((cx,cy,x,y),fill=col+(240,),width=3)
 elif "thunder" in name:
  d.line((34,6,23,30,34,30,25,57,46,25,35,25),fill=col+(245,),width=4)
 elif "ember" in name or "inferno" in name or "phoenix" in name:
  d.polygon([(32,5),(20,28),(27,27),(18,51),(33,42),(38,57),(47,33),(40,34)],fill=col+(230,))
 else:
  d.polygon([(32,7),(44,25),(55,32),(44,39),(32,57),(20,39),(9,32),(20,25)],outline=col+(235,))
 glow=im.getchannel("A").filter(ImageFilter.GaussianBlur(6));g=Image.new("RGBA",(64,64),col+(0,));g.putalpha(glow.point(lambda x:min(100,x//2)));im=Image.alpha_composite(g,im)
 p=JR/f"assets/{NS}/textures/item/fx/{name}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
 wr(JR,f"assets/{NS}/models/item/{name}.json",{"parent":"minecraft:item/generated","textures":{"layer0":f"{NS}:item/fx/{name}"}})
 wr(JR,f"assets/{NS}/items/{name}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/{name}"}})
 # Bedrock icon
 bp=BR/f"textures/items/{name}.png";bp.parent.mkdir(parents=True,exist_ok=True);im.save(bp,optimize=True)

# Bedrock real 3D geometry.
def bcube(o,s,uv=(0,0),pivot=None,rot=None):
 c={"origin":[round(x,3) for x in o],"size":[round(x,3) for x in s],"uv":list(uv)}
 if pivot is not None:c["pivot"]=list(pivot)
 if rot is not None:c["rotation"]=list(rot)
 return c
def bgeom(name):
 if name=="emberfall_claymore":
  a=[bcube((-1,-14,-.7),(2,10,1.4),(0,128)),bcube((-4,-4,-.45),(8,.9,.9),(64,128))]
  for y,w in [(-3,4.2),(2,3.8),(7,3.4),(12,3.0),(17,2.5),(22,1.8)]:a.append(bcube((-w/2,y,-.5),(w,5,.95),(0,0)))
  a.append(bcube((-.5,27,-.3),(1,4,.6),(64,0)));return a
 if name=="noctis_longsword":
  a=[bcube((-.8,-14,-.55),(1.6,10,.9),(0,128)),bcube((-3.6,-4,-.3),(7.2,.7,.6),(64,128))]
  for y,w in [(-3,2.7),(2,2.4),(7,2.1),(12,1.8),(17,1.4),(22,.9)]:a.append(bcube((-w/2,y,-.35),(w,5,.7),(0,0)))
  a.append(bcube((-.3,27,-.2),(.6,4,.4),(64,0)));return a
 if name=="stormpiercer_recurve_bow":
  a=[bcube((-.7,-3,-.55),(1.4,7.5,1.1),(0,128))]
  for cx,cy,ang in [(0,5,0),(.7,8,18),(1.7,11,24),(2.8,14,30),(3.8,17,36),(4.5,20,43),(0,-4,0),(-.7,-7,-18),(-1.7,-10,-24),(-2.8,-13,-30),(-3.8,-16,-36),(-4.5,-19,-43)]:
   a.append(bcube((cx-.35,cy-1.6,-.35),(.7,3.2,.7),(0,0),(cx,cy,0),(0,0,ang)))
  return a
 if name=="gaia_war_spear":
  return [bcube((-.42,-16,-.42),(.84,35,.84),(0,128)),bcube((-.9,19,-.45),(1.8,6,.9),(0,0)),bcube((-2.2,20,-.3),(1.7,5,.6),(64,0),(-.5,22,0),(0,0,-25)),bcube((.5,20,-.3),(1.7,5,.6),(64,0),(.5,22,0),(0,0,25)),bcube((-.55,25,-.28),(1.1,6,.56),(96,0))]
 a=[]
 for side in (-1,1):
  cx=side*2.8;a += [bcube((cx-.55,-10,-.45),(1.1,7,.9),(0,128)),bcube((cx-1.5,-3.2,-.28),(3,.7,.56),(64,128))]
  for y,w in [(-2.5,1.8),(1.3,1.5),(5.1,1.25),(8.9,.9),(12.7,.55)]:a.append(bcube((cx-w/2,y,-.34),(w,3.7,.68),(0,0)))
 return a

for name,s in WEAPONS.items():
 im=Image.new("RGBA",(128,128),s["base"]+(255,));d=ImageDraw.Draw(im,"RGBA")
 for y in range(128):
  t=y/127;d.line((0,y,127,y),fill=tuple(int(s["base"][i]*(1-t*.35)+s["mid"][i]*(t*.35)) for i in range(3))+(255,))
 for y in (16,48,80,112):d.line((0,y,127,y),fill=s["glow"]+(45,),width=1)
 p=BR/f"textures/items/{name}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
 gid=f"geometry.raisnet_{name}_v360"
 wr(BR,f"models/entity/{name}.geo.json",{"format_version":"1.16.0","minecraft:geometry":[{
  "description":{"identifier":gid,"texture_width":128,"texture_height":128,"visible_bounds_width":7,"visible_bounds_height":8,"visible_bounds_offset":[0,8,0]},
  "bones":[{"name":"bb_main","pivot":[0,8,0],"binding":"q.item_slot_to_bone_name(context.item_slot)","cubes":bgeom(name)}]
 }]})
 wr(BR,f"attachables/{name}.player.json",{"format_version":"1.20.30","minecraft:attachable":{"description":{
  "identifier":f"raisnet:{name}","item":{f"raisnet:{name}":"query.is_owner_identifier_any('minecraft:player')"},
  "materials":{"default":"entity_alphatest","enchanted":"entity_alphatest_glint"},
  "textures":{"default":f"textures/items/{name}","enchanted":"textures/misc/enchanted_item_glint"},
  "geometry":{"default":gid},"render_controllers":["controller.render.item_default"]}}})

# Bedrock atlas FX + weapon/armor entries.
it=BR/"textures/item_texture.json";idata=json.loads(it.read_text(encoding="utf-8"));td=idata.setdefault("texture_data",{})
for name in WEAPONS:td[f"raisnet:{name}"]={"textures":f"textures/items/{name}"}
for name in FX:td[f"raisnet:{name}"]={"textures":f"textures/items/{name}"}
for setn in ARM:
 for piece in PIECES:td[f"raisnet:{setn}_{piece}"]={"textures":f"textures/items/armor_{setn}_{piece}"}
it.write_text(json.dumps(idata,separators=(",",":")),encoding="utf-8")

# Pack identities/descriptions.
jmc=JR/"pack.mcmeta";j=json.loads(jmc.read_text());j["pack"]["description"]="LegendaryRais v3.6.0 ELEMENTAL ELITE | true 3D Fire/Void/Electro/Wind/Ice | elite armor";jmc.write_text(json.dumps(j,separators=(",",":")))
mf=BR/"manifest.json";b=json.loads(mf.read_text());b["header"]["name"]="RaisNet LegendaryRais v3.6.0 Elemental Elite";b["header"]["description"]="True 3D elemental weapons + elite armor + crossplay FX";b["header"]["uuid"]="45454aec-e24f-4bc9-96b1-03a3bdeeb35f";b["header"]["version"]=[3,6,0];b["modules"][0]["uuid"]="1e488ad0-ab5f-45f8-a9ab-541421159f12";b["modules"][0]["version"]=[3,6,0];mf.write_text(json.dumps(b,separators=(",",":")))

# Modern Geyser mappings + FX paper models.
m=json.loads(MBASE.read_text(encoding="utf-8"))
items=m.setdefault("items",{})
# existing weapon+armor definition model keys stay compatible; add FX item-models
paper=items.setdefault("minecraft:paper",[])
existing={(x.get("type"),x.get("model")) for x in paper}
for name in FX:
 if ("definition",f"{NS}:{name}") not in existing:
  paper.append({"type":"definition","model":f"{NS}:{name}","bedrock_identifier":f"raisnet:{name}","display_name":"FX",
                "bedrock_options":{"icon":f"raisnet:{name}","display_handheld":False}})
MOUT.write_text(json.dumps(m,indent=2),encoding="utf-8")

# Validation
for root in (JR,BR):
 for p in root.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
for n in WEAPONS:
 jm=json.loads((JR/f"assets/{NS}/models/item/{n}.json").read_text())
 assert len(jm["elements"])>=8,(n,len(jm["elements"]))
 bg=json.loads((BR/f"models/entity/{n}.geo.json").read_text())
 assert len(bg["minecraft:geometry"][0]["bones"][0]["cubes"])>=4
for setn in ARM:
 assert (JR/f"assets/{NS}/equipment/{setn}_set.json").is_file()
 for piece in PIECES:assert (BR/f"attachables/armor_{setn}_{piece}.json").is_file()
# water relics frozen
assert (JR/"assets/soultide").exists() and (JR/"assets/legendaryrais").exists()
assert (BR/"models/entity/soul_tide_katana.geo.json").is_file()
assert (BR/"models/entity/abyss_leviathan_trident.geo.json").is_file()
# mapping fx definitions
mm=json.loads(MOUT.read_text());fxdefs=[x for x in mm["items"].get("minecraft:paper",[]) if x.get("type")=="definition" and x.get("model","").startswith(NS+":fx_")]
assert len(fxdefs)>=len(FX),(len(fxdefs),len(FX))

for out,root in ((JOUT,JR),(BOUT,BR)):
 if out.exists():out.unlink()
 with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(root.rglob("*")):
   if p.is_file():z.write(p,p.relative_to(root).as_posix())
 with zipfile.ZipFile(out) as z:
  bad=z.testzip()
  if bad:raise RuntimeError(bad)
JSHA.write_text(hashlib.sha1(JOUT.read_bytes()).hexdigest()+"\n")
BSHA.write_text(hashlib.sha1(BOUT.read_bytes()).hexdigest()+"\n")
print("JAVA",JOUT.stat().st_size,JSHA.read_text().strip())
print("BEDROCK",BOUT.stat().st_size,BSHA.read_text().strip())
print("FX_DEFS",len(fxdefs))

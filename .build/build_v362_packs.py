from pathlib import Path
import json,math,random,shutil,zipfile,hashlib
from PIL import Image,ImageDraw,ImageFilter

JBASE=Path("LegendaryRais-Java-26.1.2-v3.6.1-PERFORMANCE-ELITE.zip")
BBASE=Path("LegendaryRais-Bedrock-v3.6.1-PERFORMANCE-ELITE.mcpack")
MBASE=Path("LegendaryRais-Geyser-v3.6.1-mappings.json")
JOUT=Path("LegendaryRais-Java-26.1.2-v3.6.2-CROSSPLAY-ASCENSION.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.6.2-CROSSPLAY-ASCENSION.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.6.2-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.6.2-CROSSPLAY-ASCENSION.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.6.2-CROSSPLAY-ASCENSION.sha1")
ROOT=Path(".build/generated-v362");JR=ROOT/"java";BR=ROOT/"bedrock";NS="legendaryv34"
shutil.rmtree(ROOT,ignore_errors=True);JR.mkdir(parents=True);BR.mkdir(parents=True)
with zipfile.ZipFile(JBASE) as z:z.extractall(JR)
with zipfile.ZipFile(BBASE) as z:z.extractall(BR)

W={
"emberfall_claymore":((52,14,6),(158,53,14),(255,133,31),"fire"),
"noctis_longsword":((12,8,23),(68,30,101),(194,82,255),"void"),
"stormpiercer_recurve_bow":((12,32,47),(48,119,154),(92,233,255),"electro"),
"gaia_war_spear":((22,43,46),(72,148,137),(190,255,226),"wind"),
"astral_frost_greataxe":((18,45,70),(80,162,202),(207,250,255),"ice")
}
ARM={
"phoenix":((57,16,7),(154,50,13),(255,135,31)),
"voidwalker":((14,9,27),(64,31,95),(194,84,255)),
"titan":((23,38,27),(80,102,53),(177,215,107)),
"celestial":((21,41,62),(78,122,157),(183,235,255)),
"water_sovereign":((7,41,61),(35,111,138),(92,226,249))
}
PIECES=("helmet","chest","legs","boots")

def wr(root,rel,obj):
 p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def metal(size,base,mid,glow,kind,seed):
 im=Image.new("RGBA",(size,size),base+(255,));px=im.load();rnd=random.Random(seed)
 for y in range(size):
  for x in range(size):
   t=.18*(x/(size-1))+.14*(1-y/(size-1))
   spec=max(0,1-abs((x*.82-y-size*.08)/(size*.20)))*.18
   grain=4*math.sin(x*.22+y*.07)+2*math.sin(y*.41)+rnd.randint(-3,3)
   c=[max(0,min(255,int(base[i]*(1-t-spec*.08)+mid[i]*(t+spec)+grain))) for i in range(3)]
   px[x,y]=tuple(c)+(255,)
 d=ImageDraw.Draw(im,"RGBA");w=max(1,size//128)
 if kind=="fire":
  for x in (.22,.50,.78):d.line((size*x,size*.88,size*(x-.05),size*.57,size*(x+.03),size*.35),fill=glow+(120,),width=2*w)
 elif kind=="void":
  d.arc((size*.12,size*.18,size*.88,size*.84),205,340,fill=glow+(95,),width=2*w)
  for x,y in ((.2,.28),(.43,.72),(.72,.36),(.82,.76)):d.ellipse((size*x-2*w,size*y-2*w,size*x+2*w,size*y+2*w),fill=glow+(160,))
 elif kind=="electro":
  d.line((size*.68,size*.06,size*.46,size*.38,size*.59,size*.39,size*.35,size*.92),fill=glow+(135,),width=2*w)
 elif kind=="wind":
  for off in (.25,.5,.74):d.arc((size*.08,size*(off-.14),size*.92,size*(off+.18)),190,345,fill=glow+(90,),width=2*w)
 elif kind=="ice":
  for a in range(0,360,45):
   x=size*.5+math.cos(math.radians(a))*size*.34;y=size*.5+math.sin(math.radians(a))*size*.34
   d.line((size*.5,size*.5,x,y),fill=glow+(105,),width=2*w)
  d.polygon([(size*.48,size*.08),(size*.58,size*.35),(size*.51,size*.52),(size*.39,size*.74)],outline=glow+(150,))
 else:
  d.rectangle((size*.1,size*.1,size*.9,size*.9),outline=glow+(45,),width=w)
 return im.filter(ImageFilter.UnsharpMask(radius=max(1,size//128),percent=145,threshold=2))

# ---------- Java true 3D models: grip anchor deliberately centered around x=8, y=4 ----------
def faces(k):return {f:{"texture":"#"+k} for f in ("north","south","east","west","up","down")}
def el(fr,to,k="metal",rot=None):
 e={"from":[round(v,3) for v in fr],"to":[round(v,3) for v in to],"faces":faces(k)}
 if rot:
  ox,oy,oz,axis,ang=rot
  assert ang in (-45,-22.5,0,22.5,45)
  e["rotation"]={"origin":[ox,oy,oz],"axis":axis,"angle":ang,"rescale":True}
 return e

def weapon_elements(name):
 if name=="emberfall_claymore":
  e=[el((7.25,0,-.65),(8.75,7,.65),"grip")]
  for y in (1.0,3.1,5.2):e.append(el((7.0,y,-.72),(9.0,y+.28,.72),"accent"))
  e += [el((3.1,7.0,-.48),(7.35,8.1,.48),"accent",(7.2,7.6,0,"z",-22.5)),
        el((8.65,7.0,-.48),(12.9,8.1,.48),"accent",(8.8,7.6,0,"z",22.5))]
  for y,w in [(8.2,4.4),(13.0,4.0),(17.8,3.6),(22.6,3.1),(27.4,2.5)]:
   e.append(el((8-w/2,y,-.55),(8+w/2,y+4.7,.55),"metal"))
   e.append(el((7.82,y+.2,-.67),(8.18,y+4.45,.67),"accent"))
  e += [el((7.2,32.0,-.35),(8.8,35.3,.35),"metal"),el((7.7,35.0,-.2),(8.3,37.0,.2),"accent")]
  return e
 if name=="noctis_longsword":
  e=[el((7.35,0,-.52),(8.65,7,.52),"grip"),
     el((4.1,7,-.36),(7.45,7.8,.36),"accent",(7.3,7.4,0,"z",-45)),
     el((8.55,7,-.36),(11.9,7.8,.36),"accent",(8.7,7.4,0,"z",45))]
  for y,w in [(8,2.8),(13.2,2.5),(18.4,2.15),(23.6,1.75),(28.8,1.25)]:
   e.append(el((8-w/2,y,-.40),(8+w/2,y+5.0,.40),"metal"))
   e.append(el((7.90,y+.2,-.49),(8.10,y+4.7,.49),"accent"))
  e.append(el((7.75,33.6,-.22),(8.25,36.7,.22),"accent"));return e
 if name=="stormpiercer_recurve_bow":
  e=[el((7.25,3.2,-.68),(8.75,10.4,.68),"grip"),el((6.35,6.2,-.82),(9.65,8.6,.82),"accent")]
  for cx,cy,ang in [(8,12,0),(8.7,15,22.5),(10.0,18,22.5),(11.5,21,22.5),(12.7,24,22.5),(13.5,27,45),
                    (8,4,0),(7.3,1,-22.5),(6,-2,-22.5),(4.6,-5,-22.5),(3.4,-8,-22.5),(2.7,-11,-45)]:
   e.append(el((cx-.46,cy-1.7,-.46),(cx+.46,cy+1.7,.46),"metal",(cx,cy,0,"z",ang)))
  e += [el((7.92,-12,-.08),(8.08,8.2,.08),"accent",(8,-2,0,"z",-22.5)),
        el((7.92,8.8,-.08),(8.08,30.2,.08),"accent",(8,19,0,"z",22.5)),
        el((7.6,7.7,-.35),(8.4,8.5,.35),"accent")]
  return e
 if name=="gaia_war_spear":
  e=[el((7.52,-2,-.44),(8.48,25,.44),"grip")]
  for y in (0,5,10,15,20):e.append(el((7.23,y,-.52),(8.77,y+.28,.52),"accent"))
  e += [el((7.0,24.5,-.48),(9.0,30.2,.48),"metal"),
        el((5.4,25.2,-.32),(7.4,31.1,.32),"accent",(7.1,27.8,0,"z",-22.5)),
        el((8.6,25.2,-.32),(10.6,31.1,.32),"accent",(8.9,27.8,0,"z",22.5)),
        el((6.45,29.8,-.38),(9.55,34.6,.38),"metal"),el((7.35,34.3,-.23),(8.65,39.4,.23),"accent")]
  return e
 # glacial great axe: long shaft, asymmetric crescent head
 e=[el((7.30,0,-.58),(8.70,22,.58),"grip")]
 for y in (2,6,10,14,18):e.append(el((7.0,y,-.66),(9.0,y+.30,.66),"accent"))
 e += [el((6.8,20.5,-.75),(9.2,24.0,.75),"accent"),
       el((4.4,22.5,-.60),(11.6,25.0,.60),"metal"),
       el((1.2,23.2,-.52),(6.2,27.0,.52),"metal",(5.8,24.4,0,"z",-22.5)),
       el((-1.5,25.6,-.46),(4.9,30.5,.46),"metal",(4.3,27.0,0,"z",-45)),
       el((9.8,23.4,-.48),(13.6,26.6,.48),"metal",(10.2,24.5,0,"z",22.5)),
       el((6.9,24.0,-.88),(9.1,28.1,.88),"accent"),
       el((7.4,27.7,-.46),(8.6,33.2,.46),"accent")]
 return e

# Screenshot-driven transforms: center grip into hand; third-person translation kept close to vanilla.
TRANS={
"emberfall_claymore":{
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,3.0,.55],"scale":[.61,.61,.61]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,3.0,.55],"scale":[.61,.61,.61]},
 "firstperson_righthand":{"rotation":[0,-90,24],"translation":[1.0,3.1,.9],"scale":[.70,.70,.70]},
 "firstperson_lefthand":{"rotation":[0,90,-24],"translation":[1.0,3.1,.9],"scale":[.70,.70,.70]}},
"noctis_longsword":{
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,3.1,.5],"scale":[.64,.64,.64]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,3.1,.5],"scale":[.64,.64,.64]},
 "firstperson_righthand":{"rotation":[0,-90,24],"translation":[1.0,3.2,.85],"scale":[.72,.72,.72]},
 "firstperson_lefthand":{"rotation":[0,90,-24],"translation":[1.0,3.2,.85],"scale":[.72,.72,.72]}},
"stormpiercer_recurve_bow":{
 "thirdperson_righthand":{"rotation":[-8,-90,8],"translation":[0,1.8,1.0],"scale":[.62,.62,.62]},
 "thirdperson_lefthand":{"rotation":[-8,90,-8],"translation":[0,1.8,1.0],"scale":[.62,.62,.62]},
 "firstperson_righthand":{"rotation":[-6,-92,5],"translation":[1.0,1.6,1.5],"scale":[.74,.74,.74]},
 "firstperson_lefthand":{"rotation":[-6,92,-5],"translation":[1.0,1.6,1.5],"scale":[.74,.74,.74]}},
"gaia_war_spear":{
 "thirdperson_righthand":{"rotation":[0,-90,58],"translation":[0,2.0,.55],"scale":[.48,.48,.48]},
 "thirdperson_lefthand":{"rotation":[0,90,-58],"translation":[0,2.0,.55],"scale":[.48,.48,.48]},
 "firstperson_righthand":{"rotation":[0,-90,28],"translation":[1.0,2.2,1.0],"scale":[.54,.54,.54]},
 "firstperson_lefthand":{"rotation":[0,90,-28],"translation":[1.0,2.2,1.0],"scale":[.54,.54,.54]}},
"astral_frost_greataxe":{
 "thirdperson_righthand":{"rotation":[0,-90,52],"translation":[0,2.7,.6],"scale":[.55,.55,.55]},
 "thirdperson_lefthand":{"rotation":[0,90,-52],"translation":[0,2.7,.6],"scale":[.55,.55,.55]},
 "firstperson_righthand":{"rotation":[0,-90,20],"translation":[1.0,2.8,.9],"scale":[.62,.62,.62]},
 "firstperson_lefthand":{"rotation":[0,90,-20],"translation":[1.0,2.8,.9],"scale":[.62,.62,.62]}}
}
COMMON={"gui":{"rotation":[25,-35,0],"scale":[.55,.55,.55]},"ground":{"translation":[0,2,0],"scale":[.40,.40,.40]},"fixed":{"rotation":[0,180,0],"scale":[.58,.58,.58]}}

for name,(base,mid,glow,kind) in W.items():
 for k,(a,b,kk) in {"metal":(base,mid,kind),"grip":((22,17,14),(76,53,37),"neutral"),"accent":(mid,glow,kind)}.items():
  im=metal(256,a,b,glow,kk,name+k)
  p=JR/f"assets/{NS}/textures/item/v362/{name}_{k}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
 disp=dict(COMMON);disp.update(TRANS[name])
 wr(JR,f"assets/{NS}/models/item/{name}.json",{"textures":{"metal":f"{NS}:item/v362/{name}_metal","grip":f"{NS}:item/v362/{name}_grip","accent":f"{NS}:item/v362/{name}_accent"},"elements":weapon_elements(name),"display":disp})
 wr(JR,f"assets/{NS}/items/{name}.json",{"model":{"type":"minecraft:model","model":f"{NS}:item/{name}"}})

# ---------- ornate armor textures ----------
def armor_tex(setn,layer):
 base,mid,glow=ARM[setn];S=256;im=metal(S,base,mid,glow,"neutral",setn+str(layer));d=ImageDraw.Draw(im,"RGBA")
 # embossed panels / crest; designed at 256 then downsample to vanilla UV.
 for x in (32,96,160,224):
  d.polygon([(x,28),(x-18,54),(x,82),(x+18,54)],outline=glow+(135,),width=4)
  d.line((x,82,x,126),fill=mid+(90,),width=3)
 if setn=="phoenix":
  for cx in (64,192):
   d.arc((cx-36,126,cx+36,220),190,350,fill=glow+(185,),width=6)
   d.line((cx,142,cx-24,196),fill=glow+(120,),width=4);d.line((cx,142,cx+24,196),fill=glow+(120,),width=4)
 elif setn=="voidwalker":
  d.arc((68,102,188,224),22,158,fill=glow+(160,),width=6)
  for x,y in ((44,145),(92,195),(155,137),(214,196)):d.ellipse((x-5,y-5,x+5,y+5),fill=glow+(185,))
 elif setn=="titan":
  for x in (52,128,204):
   d.rectangle((x-22,132,x+22,196),outline=glow+(130,),width=6)
   d.line((x-16,164,x+16,164),fill=mid+(105,),width=4)
 elif setn=="celestial":
  for x,y in ((46,146),(94,208),(145,122),(205,188)):
   d.line((x-10,y,x+10,y),fill=glow+(165,),width=4);d.line((x,y-10,x,y+10),fill=glow+(165,),width=4)
 elif setn=="water_sovereign":
  for x in (38,92,146,210):
   d.arc((x-24,130,x+24,190),5,175,fill=glow+(175,),width=5)
   d.arc((x-18,168,x+18,220),190,350,fill=mid+(110,),width=4)
 return im.resize((64,32),Image.Resampling.LANCZOS)

def armor_icon(setn,piece):
 base,mid,glow=ARM[setn];S=128;im=Image.new("RGBA",(S,S),(0,0,0,0));d=ImageDraw.Draw(im,"RGBA");f=base+(255,);e=mid+(255,);h=glow+(245,)
 if piece=="helmet":
  d.polygon([(30,34),(48,16),(80,16),(98,34),(91,83),(76,104),(52,104),(37,83)],fill=f,outline=e)
  # crest/horns
  d.polygon([(46,24),(39,5),(57,20)],fill=e,outline=h);d.polygon([(82,24),(89,5),(71,20)],fill=e,outline=h)
  d.polygon([(44,56),(84,56),(77,71),(64,80),(51,71)],fill=(7,8,12,235),outline=h)
 elif piece=="chest":
  d.polygon([(24,39),(45,18),(83,18),(104,39),(93,106),(35,106)],fill=f,outline=e)
  d.polygon([(64,30),(82,60),(64,92),(46,60)],fill=mid+(130,),outline=h);d.line((64,22,64,103),fill=h,width=4)
  d.polygon([(24,39),(8,49),(30,63)],fill=e,outline=h);d.polygon([(104,39),(120,49),(98,63)],fill=e,outline=h)
 elif piece=="legs":
  d.polygon([(34,20),(94,20),(90,59),(80,114),(63,114),(59,63),(49,114),(32,114),(38,59)],fill=f,outline=e)
  d.line((64,26,64,66),fill=h,width=4);d.line((42,49,58,58),fill=e,width=4);d.line((86,49,70,58),fill=e,width=4)
 else:
  d.polygon([(26,44),(56,44),(56,97),(20,114)],fill=f,outline=e);d.polygon([(72,44),(102,44),(108,114),(72,97)],fill=f,outline=e)
  d.line((27,65,55,59),fill=h,width=4);d.line((101,65,73,59),fill=h,width=4)
 return im.resize((64,64),Image.Resampling.LANCZOS)

for setn in ARM:
 for layer,sub in ((1,"humanoid"),(2,"humanoid_leggings")):
  im=armor_tex(setn,layer)
  p=JR/f"assets/{NS}/textures/entity/equipment/{sub}/{setn}_set.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
  p=BR/f"textures/models/armor/{setn}_{layer}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
 for piece in PIECES:
  im=armor_icon(setn,piece)
  p=JR/f"assets/{NS}/textures/item/armor/{setn}_{piece}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
  p=BR/f"textures/items/armor_{setn}_{piece}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)

# ---------- Bedrock weapon geometry ----------
def bcube(origin,size,uv=(0,0),pivot=None,rot=None,inflate=None):
 c={"origin":[round(v,3) for v in origin],"size":[round(v,3) for v in size],"uv":list(uv)}
 if pivot is not None:c["pivot"]=list(pivot)
 if rot is not None:c["rotation"]=list(rot)
 if inflate is not None:c["inflate"]=inflate
 return c

def bweapon(name):
 if name=="emberfall_claymore":
  a=[bcube((-.75,-8,-.6),(1.5,8,1.2),(0,96)),bcube((-4,0,-.5),(8,1.1,1),(64,96))]
  for y,w in [(1,4.4),(6,4),(11,3.6),(16,3.1),(21,2.5)]:a.append(bcube((-w/2,y,-.5),(w,4.8,1),(0,0)))
  a.append(bcube((-.5,25.7,-.3),(1,4,.6),(64,0)));return a
 if name=="noctis_longsword":
  a=[bcube((-.65,-7,-.5),(1.3,7,.9),(0,96)),bcube((-3.4,0,-.35),(6.8,.8,.7),(64,96))]
  for y,w in [(1,2.8),(6,2.5),(11,2.1),(16,1.7),(21,1.2)]:a.append(bcube((-w/2,y,-.4),(w,4.8,.8),(0,0)))
  a.append(bcube((-.25,25.7,-.2),(.5,4,.4),(64,0)));return a
 if name=="stormpiercer_recurve_bow":
  a=[bcube((-.72,-3.5,-.58),(1.44,7,1.16),(0,96))]
  for cx,cy,ang in [(0,4,0),(.8,7,18),(2,10,26),(3.4,13,34),(4.6,16,42),(0,-4,0),(-.8,-7,-18),(-2,-10,-26),(-3.4,-13,-34),(-4.6,-16,-42)]:
   a.append(bcube((cx-.38,cy-1.6,-.38),(.76,3.2,.76),(0,0),(cx,cy,0),(0,0,ang)))
  return a
 if name=="gaia_war_spear":
  return [bcube((-.45,-10,-.45),(.9,31,.9),(0,96)),
          bcube((-.95,20.5,-.48),(1.9,6,.96),(0,0)),
          bcube((-2.3,21,-.34),(1.9,6,.68),(64,0),(-.4,23.5,0),(0,0,-24)),
          bcube((.4,21,-.34),(1.9,6,.68),(64,0),(.4,23.5,0),(0,0,24)),
          bcube((-1.5,26,-.32),(3,5,.64),(92,0)),bcube((-.5,30.5,-.22),(1,4,.44),(108,0))]
 # frost greataxe, 14 cubes max
 a=[bcube((-.7,-9,-.58),(1.4,26,1.16),(0,96))]
 for y in (-6,-1,4,9,14):a.append(bcube((-1.0,y,-.67),(2,.32,1.34),(64,96)))
 a += [bcube((-1.2,16,-.8),(2.4,4,.1+1.5),(80,96)),
       bcube((-5.5,18,-.56),(6.0,3.5,1.12),(0,0),(-.5,19.5,0),(0,0,-20)),
       bcube((-8.0,20.5,-.5),(5.0,4.5,1),(20,0),(-3.5,21.5,0),(0,0,-42)),
       bcube((.4,18.2,-.52),(4.2,3.1,1.04),(42,0),(.5,19.4,0),(0,0,22)),
       bcube((-1.0,19.2,-.85),(2,5,1.7),(64,0)),bcube((-.45,24,-.35),(.9,5,.7),(84,0))]
 return a

for name,(base,mid,glow,kind) in W.items():
 im=metal(128,base,mid,glow,kind,"bed362-"+name);p=BR/f"textures/items/{name}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
 gid=f"geometry.raisnet_{name}_v362"
 cubes=bweapon(name)
 wr(BR,f"models/entity/{name}.geo.json",{"format_version":"1.16.0","minecraft:geometry":[{
  "description":{"identifier":gid,"texture_width":128,"texture_height":128,"visible_bounds_width":7,"visible_bounds_height":8,"visible_bounds_offset":[0,8,0]},
  "bones":[{"name":"bb_main","pivot":[0,8,0],"binding":"q.item_slot_to_bone_name(context.item_slot)","cubes":cubes}]
 }]})
 wr(BR,f"attachables/{name}.player.json",{"format_version":"1.20.30","minecraft:attachable":{"description":{
  "identifier":f"raisnet:{name}","item":{f"raisnet:{name}":"query.is_owner_identifier_any('minecraft:player')"},
  "materials":{"default":"entity_alphatest","enchanted":"entity_alphatest_glint"},
  "textures":{"default":f"textures/items/{name}","enchanted":"textures/misc/enchanted_item_glint"},
  "geometry":{"default":gid},"render_controllers":["controller.render.item_default"]}}})

# ---------- Bedrock actual 3D armor geometry, low cube-count ----------
# Built from the official custom armor approach: bones bind to player bones.
def armor_geo(setn,piece):
 gid=f"geometry.raisnet.armor.{setn}.{piece}.v362";bones=[]
 if piece=="helmet":
  cubes=[bcube((-4,24,-4),(8,8,8),(0,0),inflate=1.0),
         bcube((-1,32,-1),(2,3,2),(32,0)),bcube((-5.2,28,-2),(1.5,3,4),(36,0)),bcube((3.7,28,-2),(1.5,3,4),(44,0))]
  bones=[{"name":"helmet_plate","pivot":[0,24,0],"binding":"'head'","cubes":cubes}]
 elif piece=="chest":
  body=[bcube((-4,2,-2),(8,12,4),(0,0),inflate=1.02),bcube((-3.1,7,-3.25),(6.2,4,1.3),(32,8))]
  ra=[bcube((-8,2,-2),(4,12,4),(0,16),inflate=1.0),bcube((-9.2,10,-2.6),(5.2,3,5.2),(40,16))]
  la=[bcube((4,2,-2),(4,12,4),(0,16),inflate=1.0),bcube((4,10,-2.6),(5.2,3,5.2),(40,16))]
  bones=[{"name":"body_plate","pivot":[0,12,0],"binding":"'body'","cubes":body},
         {"name":"right_pauldron","pivot":[-5,12,0],"binding":"'rightarm'","cubes":ra},
         {"name":"left_pauldron","pivot":[5,12,0],"binding":"'leftarm'","cubes":la}]
 elif piece=="legs":
  body=[bcube((-4,8,-2),(8,4,4),(16,16),inflate=.62)]
  rl=[bcube((-4,0,-2),(4,12,4),(0,16),inflate=.55),bcube((-3.5,4,-2.8),(3,3,1.1),(48,16))]
  ll=[bcube((0,0,-2),(4,12,4),(0,16),inflate=.55),bcube((.5,4,-2.8),(3,3,1.1),(48,16))]
  bones=[{"name":"waist_plate","pivot":[0,12,0],"binding":"'body'","cubes":body},
         {"name":"right_leg_plate","pivot":[-1.9,12,0],"binding":"'rightleg'","cubes":rl},
         {"name":"left_leg_plate","pivot":[1.9,12,0],"binding":"'leftleg'","cubes":ll}]
 else:
  rl=[bcube((-4,0,-2),(4,6,4),(0,16),inflate=1.0),bcube((-3.8,0,-3),(3.6,2.2,1.2),(48,24))]
  ll=[bcube((0,0,-2),(4,6,4),(0,16),inflate=1.0),bcube((.2,0,-3),(3.6,2.2,1.2),(48,24))]
  bones=[{"name":"right_boot","pivot":[-1.9,12,0],"binding":"'rightleg'","cubes":rl},
         {"name":"left_boot","pivot":[1.9,12,0],"binding":"'leftleg'","cubes":ll}]
 # accent silhouette differs by set without adding large cube counts
 glow=ARM[setn][2]
 return gid,{"format_version":"1.16.0","minecraft:geometry":[{"description":{"identifier":gid,"texture_width":64,"texture_height":32,"visible_bounds_width":3,"visible_bounds_height":4,"visible_bounds_offset":[0,1,0]},"bones":bones}]}

for setn in ARM:
 for piece in PIECES:
  gid,g=armor_geo(setn,piece);wr(BR,f"models/entity/armor_{setn}_{piece}_v362.geo.json",g)
  tex=f"textures/models/armor/{setn}_{2 if piece=='legs' else 1}"
  parent_var={"helmet":"v.helmet_layer_visible = false;","chest":"v.chest_layer_visible = false;","legs":"v.leg_layer_visible = false;","boots":"v.boot_layer_visible = false;"}[piece]
  wr(BR,f"attachables/armor_{setn}_{piece}.json",{"format_version":"1.20.60","minecraft:attachable":{"description":{
    "identifier":f"raisnet:{setn}_{piece}",
    "materials":{"default":"armor","enchanted":"armor_enchanted"},
    "textures":{"default":tex,"enchanted":"textures/misc/enchanted_actor_glint"},
    "geometry":{"default":gid},
    "scripts":{"parent_setup":parent_var},
    "render_controllers":["controller.render.armor"]
  }}})

# Atlas: new great axe + existing names.
it=BR/"textures/item_texture.json";idata=json.loads(it.read_text());td=idata.setdefault("texture_data",{})
for name in W:td[f"raisnet:{name}"]={"textures":f"textures/items/{name}"}
for setn in ARM:
 for piece in PIECES:td[f"raisnet:{setn}_{piece}"]={"textures":f"textures/items/armor_{setn}_{piece}"}
it.write_text(json.dumps(idata,separators=(",",":")))

# ---------- Geyser mapping ----------
m=json.loads(MBASE.read_text());items=m["items"]
# remove old astral mapping from shears
items["minecraft:shears"]=[d for d in items.get("minecraft:shears",[]) if d.get("model")!="legendaryv34:astral_twin_daggers"]
items.setdefault("minecraft:netherite_axe",[])
items["minecraft:netherite_axe"]=[d for d in items["minecraft:netherite_axe"] if d.get("bedrock_identifier")!="raisnet:astral_frost_greataxe"]
items["minecraft:netherite_axe"].append({
 "type":"definition","model":"legendaryv34:astral_frost_greataxe","bedrock_identifier":"raisnet:astral_frost_greataxe",
 "display_name":"Astral Frost Glacial Greataxe",
 "bedrock_options":{"icon":"raisnet:astral_frost_greataxe","display_handheld":True,"creative_category":"equipment"}
})
# Update display names and enforce bow inheritance: no component overrides.
for d in items.get("minecraft:bow",[]):
 if d.get("model")=="legendaryv34:stormpiercer_recurve_bow":
  d["display_name"]="Stormpiercer Sovereign Arc Bow";d.pop("components",None)
  d.setdefault("bedrock_options",{})["display_handheld"]=True
for d in items.get("minecraft:netherite_shovel",[]):
 if d.get("model")=="legendaryv34:gaia_war_spear":d["display_name"]="Zephya Sovereign Wind Spear"
MOUT.write_text(json.dumps(m,indent=2))

# Pack metadata/UUID cache bust.
mc=JR/"pack.mcmeta";j=json.loads(mc.read_text());j["pack"]["description"]="LegendaryRais v3.6.2 CROSSPLAY ASCENSION | corrected grips | greataxe | ornate armor";mc.write_text(json.dumps(j,separators=(",",":")))
mf=BR/"manifest.json";b=json.loads(mf.read_text());b["header"]["name"]="RaisNet LegendaryRais v3.6.2 Crossplay Ascension";b["header"]["description"]="Low-cube true 3D weapons + custom 3D armor geometry + crossplay-safe FX";b["header"]["uuid"]="51293d6c-483a-4471-9aa3-5bb79f4e3a62";b["header"]["version"]=[3,6,2];b["modules"][0]["uuid"]="08f09047-bb8f-4b17-8f0c-1c9a6a6e7207";b["modules"][0]["version"]=[3,6,2];mf.write_text(json.dumps(b,separators=(",",":")))

# ---------- Deep validation ----------
for root in (JR,BR):
 for p in root.rglob("*.json"):json.loads(p.read_text())

for name in W:
 jm=json.loads((JR/f"assets/{NS}/models/item/{name}.json").read_text())
 els=jm["elements"];assert 8<=len(els)<=32,(name,len(els))
 # Grip acceptance: at least one grip element centered on x=8 and y includes the hand anchor around 4.
 grips=[e for e in els if any(face.get("texture")=="#grip" for face in e["faces"].values())]
 assert grips,name+" no grip"
 assert any(e["from"][0] <= 8 <= e["to"][0] and e["from"][1] <= 4 <= e["to"][1] for e in grips),(name,"grip anchor")
 tp=jm["display"]["thirdperson_righthand"];assert abs(tp["translation"][0])<=.1,(name,tp)
 assert tp["scale"][0]<=.65,(name,tp)
 for key in ("metal","grip","accent"):
  ns,path=jm["textures"][key].split(":",1);im=Image.open(JR/f"assets/{ns}/textures/{path}.png");assert im.size==(256,256)

assert (JR/f"assets/{NS}/models/item/astral_frost_greataxe.json").is_file()
assert (JR/f"assets/{NS}/items/astral_frost_greataxe.json").is_file()

for name in W:
 bg=json.loads((BR/f"models/entity/{name}.geo.json").read_text());cubes=bg["minecraft:geometry"][0]["bones"][0]["cubes"]
 assert 4<=len(cubes)<=30,(name,len(cubes))
 im=Image.open(BR/f"textures/items/{name}.png");assert im.size==(128,128)

# Armor geometry cube budgets per spec.
limits={"helmet":8,"chest":12,"legs":8,"boots":6}
for setn in ARM:
 for piece in PIECES:
  gp=BR/f"models/entity/armor_{setn}_{piece}_v362.geo.json";g=json.loads(gp.read_text())
  n=sum(len(b.get("cubes",[])) for b in g["minecraft:geometry"][0]["bones"])
  assert n<=limits[piece],(setn,piece,n)
  a=json.loads((BR/f"attachables/armor_{setn}_{piece}.json").read_text())
  assert a["minecraft:attachable"]["description"]["geometry"]["default"]==g["minecraft:geometry"][0]["description"]["identifier"]

mm=json.loads(MOUT.read_text())
bow=[d for d in mm["items"]["minecraft:bow"] if d.get("model")=="legendaryv34:stormpiercer_recurve_bow"]
assert len(bow)==1 and "components" not in bow[0]
assert bow[0]["bedrock_options"]["display_handheld"] is True
axe=[d for d in mm["items"]["minecraft:netherite_axe"] if d.get("model")=="legendaryv34:astral_frost_greataxe"]
assert len(axe)==1
assert not any(d.get("model")=="legendaryv34:astral_twin_daggers" for d in mm["items"].get("minecraft:shears",[]))

# Water relic assets frozen/preserved.
assert (JR/"assets/soultide").exists() and (JR/"assets/legendaryrais").exists()
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
JSHA.write_text(hashlib.sha1(JOUT.read_bytes()).hexdigest()+"\n")
BSHA.write_text(hashlib.sha1(BOUT.read_bytes()).hexdigest()+"\n")
print("JAVA",JOUT.stat().st_size,JSHA.read_text().strip())
print("BEDROCK",BOUT.stat().st_size,BSHA.read_text().strip())
print("ASCENSION PASS: grip anchors, bow base behavior mapping, great axe, armor 3D budgets")

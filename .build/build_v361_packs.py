from pathlib import Path
import json,math,random,shutil,zipfile,hashlib
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance

JBASE=Path("LegendaryRais-Java-26.1.2-v3.6.0-ELEMENTAL-ELITE.zip")
BBASE=Path("LegendaryRais-Bedrock-v3.6.0-ELEMENTAL-ELITE.mcpack")
MBASE=Path("LegendaryRais-Geyser-v3.6.0-mappings.json")
JOUT=Path("LegendaryRais-Java-26.1.2-v3.6.1-PERFORMANCE-ELITE.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.6.1-PERFORMANCE-ELITE.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.6.1-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.6.1-PERFORMANCE-ELITE.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.6.1-PERFORMANCE-ELITE.sha1")
ROOT=Path(".build/generated-v361");JR=ROOT/"java";BR=ROOT/"bedrock";NS="legendaryv34"
shutil.rmtree(ROOT,ignore_errors=True);JR.mkdir(parents=True);BR.mkdir(parents=True)
with zipfile.ZipFile(JBASE) as z:z.extractall(JR)
with zipfile.ZipFile(BBASE) as z:z.extractall(BR)

W={
"emberfall_claymore":((54,16,7),(151,52,15),(255,126,30),"fire"),
"noctis_longsword":((13,9,24),(67,31,99),(188,79,250),"void"),
"stormpiercer_recurve_bow":((15,36,49),(52,121,151),(94,230,255),"electro"),
"gaia_war_spear":((23,45,47),(75,145,134),(185,255,222),"wind"),
"astral_twin_daggers":((20,48,72),(78,157,196),(195,246,255),"ice")
}
ARM={
"phoenix":((58,16,7),(151,48,13),(255,130,30)),
"voidwalker":((15,10,27),(62,31,92),(190,82,250)),
"titan":((24,39,27),(78,99,51),(170,210,104)),
"celestial":((22,42,62),(76,119,153),(177,231,255)),
"water_sovereign":((8,42,61),(34,108,134),(89,221,246))
}
PIECES=("helmet","chest","legs","boots")

TRANS={
"emberfall_claymore":{
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,2.0,1.0],"scale":[.58,.58,.58]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,2.0,1.0],"scale":[.58,.58,.58]},
 "firstperson_righthand":{"rotation":[0,-90,18],"translation":[1.2,2.55,1.15],"scale":[.66,.66,.66]},
 "firstperson_lefthand":{"rotation":[0,90,-18],"translation":[1.2,2.55,1.15],"scale":[.66,.66,.66]}},
"noctis_longsword":{
 "thirdperson_righthand":{"rotation":[0,-90,55],"translation":[0,2.2,1.0],"scale":[.62,.62,.62]},
 "thirdperson_lefthand":{"rotation":[0,90,-55],"translation":[0,2.2,1.0],"scale":[.62,.62,.62]},
 "firstperson_righthand":{"rotation":[0,-90,20],"translation":[1.1,2.7,1.1],"scale":[.70,.70,.70]},
 "firstperson_lefthand":{"rotation":[0,90,-20],"translation":[1.1,2.7,1.1],"scale":[.70,.70,.70]}},
"stormpiercer_recurve_bow":{
 "thirdperson_righthand":{"rotation":[-12,-92,8],"translation":[-1.0,1.3,2.2],"scale":[.67,.67,.67]},
 "thirdperson_lefthand":{"rotation":[-12,92,-8],"translation":[1.0,1.3,2.2],"scale":[.67,.67,.67]},
 "firstperson_righthand":{"rotation":[-8,-96,4],"translation":[1.0,1.1,1.8],"scale":[.78,.78,.78]},
 "firstperson_lefthand":{"rotation":[-8,96,-4],"translation":[1.0,1.1,1.8],"scale":[.78,.78,.78]}},
"gaia_war_spear":{
 "thirdperson_righthand":{"rotation":[0,-90,62],"translation":[0,1.0,1.2],"scale":[.52,.52,.52]},
 "thirdperson_lefthand":{"rotation":[0,90,-62],"translation":[0,1.0,1.2],"scale":[.52,.52,.52]},
 "firstperson_righthand":{"rotation":[0,-90,30],"translation":[1.0,1.7,1.4],"scale":[.58,.58,.58]},
 "firstperson_lefthand":{"rotation":[0,90,-30],"translation":[1.0,1.7,1.4],"scale":[.58,.58,.58]}},
"astral_twin_daggers":{
 "thirdperson_righthand":{"rotation":[0,-90,48],"translation":[0,3.0,1.0],"scale":[.72,.72,.72]},
 "thirdperson_lefthand":{"rotation":[0,90,-48],"translation":[0,3.0,1.0],"scale":[.72,.72,.72]},
 "firstperson_righthand":{"rotation":[0,-90,12],"translation":[1.2,3.2,1.0],"scale":[.78,.78,.78]},
 "firstperson_lefthand":{"rotation":[0,90,-12],"translation":[1.2,3.2,1.0],"scale":[.78,.78,.78]}}
}
COMMON={
"gui":{"rotation":[24,-34,0],"translation":[0,0,0],"scale":[.56,.56,.56]},
"ground":{"translation":[0,2,0],"scale":[.40,.40,.40]},
"fixed":{"rotation":[0,180,0],"scale":[.60,.60,.60]}
}

def metal(size,base,mid,glow,kind,seed):
 im=Image.new("RGBA",(size,size),base+(255,));px=im.load();rnd=random.Random(seed)
 for y in range(size):
  for x in range(size):
   diag=(x+y)/(2*(size-1));grain=math.sin((x*0.31+y*.07))*4+math.sin(y*.19)*3
   n=rnd.randint(-4,4);shine=max(0,1-abs((x-y-size*.05)/(size*.22)))*.16
   c=[]
   for i in range(3):
    v=base[i]*(1-.22*diag-shine*.05)+mid[i]*(.22*diag+shine)+grain+n
    c.append(max(0,min(255,int(v))))
   px[x,y]=tuple(c)+(255,)
 d=ImageDraw.Draw(im,"RGBA")
 w=max(1,size//128)
 for y in range(size//8,size,size//4):d.line((size*.05,y,size*.95,y-2*w),fill=mid+(34,),width=w)
 if kind=="fire":
  for x in (size*.25,size*.5,size*.75):d.line((x,size*.82,x-size*.06,size*.55,x+size*.03,size*.38),fill=glow+(90,),width=2*w)
 elif kind=="void":
  for x,y in ((.2,.25),(.45,.7),(.7,.35),(.82,.78)):d.ellipse((size*x-2*w,size*y-2*w,size*x+2*w,size*y+2*w),fill=glow+(115,))
 elif kind=="electro":
  d.line((size*.62,size*.08,size*.45,size*.42,size*.58,size*.42,size*.38,size*.9),fill=glow+(110,),width=2*w)
 elif kind=="wind":
  for off in (.28,.52,.72):d.arc((size*.1,size*(off-.16),size*.9,size*(off+.18)),195,340,fill=glow+(75,),width=w)
 else:
  for a in range(0,360,60):
   x=size*.5+math.cos(math.radians(a))*size*.32;y=size*.5+math.sin(math.radians(a))*size*.32
   d.line((size*.5,size*.5,x,y),fill=glow+(70,),width=w)
 return im.filter(ImageFilter.UnsharpMask(radius=max(1,size//128),percent=125,threshold=3))

def armor_tex(setn,layer):
 base,mid,glow=ARM[setn];S=128;im=metal(S,base,mid,glow,setn,setn+str(layer))
 d=ImageDraw.Draw(im,"RGBA")
 # ornamental panels designed first at 128 then downsampled to vanilla 64x32 UV.
 d.rectangle((4,4,123,123),outline=mid+(95,),width=2)
 for cx in (20,52,84,116):
  d.polygon([(cx,18),(cx-9,34),(cx,52),(cx+9,34)],outline=glow+(120,))
 if setn=="phoenix":
  for cx in (32,96):d.arc((cx-18,64,cx+18,108),190,350,fill=glow+(170,),width=3)
 elif setn=="voidwalker":
  d.arc((35,50,93,110),20,160,fill=glow+(130,),width=3)
 elif setn=="titan":
  for x in (24,64,104):d.rectangle((x-10,70,x+10,98),outline=glow+(100,),width=3)
 elif setn=="celestial":
  for x,y in ((22,75),(48,101),(75,68),(105,98)):d.ellipse((x-2,y-2,x+2,y+2),fill=(245,255,255,230))
 else:
  for x in (20,52,84,116):d.arc((x-12,70,x+12,100),0,180,fill=glow+(145,),width=2)
 return im.resize((64,32),Image.Resampling.LANCZOS)

def icon(setn,piece):
 base,mid,glow=ARM[setn];S=128;im=Image.new("RGBA",(S,S),(0,0,0,0));d=ImageDraw.Draw(im,"RGBA")
 f=base+(255,);e=mid+(255,);h=glow+(240,)
 if piece=="helmet":
  d.polygon([(32,34),(49,18),(79,18),(96,34),(89,82),(76,101),(52,101),(39,82)],fill=f,outline=e)
  d.polygon([(45,55),(83,55),(77,69),(64,78),(51,69)],fill=(6,8,12,230),outline=h)
  d.line((64,24,64,52),fill=h,width=4)
 elif piece=="chest":
  d.polygon([(26,38),(47,20),(81,20),(102,38),(91,104),(37,104)],fill=f,outline=e)
  d.polygon([(64,34),(78,58),(64,86),(50,58)],fill=mid+(120,),outline=h);d.line((64,24,64,100),fill=h,width=3)
 elif piece=="legs":
  d.polygon([(36,22),(92,22),(88,58),(78,112),(62,112),(58,62),(50,112),(34,112),(40,58)],fill=f,outline=e);d.line((64,28,64,63),fill=h,width=3)
 else:
  d.polygon([(28,44),(55,44),(55,96),(23,111)],fill=f,outline=e);d.polygon([(73,44),(100,44),(105,111),(73,96)],fill=f,outline=e)
  d.line((29,63,54,58),fill=h,width=3);d.line((99,63,74,58),fill=h,width=3)
 return im.resize((64,64),Image.Resampling.LANCZOS)

# Java: preserve true geometry, upgrade materials and hand transforms.
for name,(base,mid,glow,kind) in W.items():
 modelp=JR/f"assets/{NS}/models/item/{name}.json";m=json.loads(modelp.read_text())
 for key,(a,b,k) in {"metal":(base,mid,kind),"grip":((24,18,15),(80,55,37),"grip"),"accent":(mid,glow,kind)}.items():
  tex=metal(256,a,b,glow,k,name+key)
  p=JR/f"assets/{NS}/textures/item/v361/{name}_{key}.png";p.parent.mkdir(parents=True,exist_ok=True);tex.save(p,optimize=True)
  m.setdefault("textures",{})[key]=f"{NS}:item/v361/{name}_{key}"
 disp=dict(COMMON);disp.update(TRANS[name]);m["display"]=disp
 modelp.write_text(json.dumps(m,separators=(",",":")))

# Armor relief-style textures: visually dimensional, native rig = stable/cheap.
for setn in ARM:
 for layer,sub in ((1,"humanoid"),(2,"humanoid_leggings")):
  im=armor_tex(setn,layer)
  jp=JR/f"assets/{NS}/textures/entity/equipment/{sub}/{setn}_set.png";jp.parent.mkdir(parents=True,exist_ok=True);im.save(jp,optimize=True)
  bp=BR/f"textures/models/armor/{setn}_{layer}.png";bp.parent.mkdir(parents=True,exist_ok=True);im.save(bp,optimize=True)
 for piece in PIECES:
  im=icon(setn,piece)
  jp=JR/f"assets/{NS}/textures/item/armor/{setn}_{piece}.png";jp.parent.mkdir(parents=True,exist_ok=True);im.save(jp,optimize=True)
  bp=BR/f"textures/items/armor_{setn}_{piece}.png";bp.parent.mkdir(parents=True,exist_ok=True);im.save(bp,optimize=True)

# Bedrock: 128px efficient-HD atlas. Keep cube geometry; quality comes from shading not huge textures.
for name,(base,mid,glow,kind) in W.items():
 im=metal(128,base,mid,glow,kind,"bedrock-"+name)
 p=BR/f"textures/items/{name}.png";p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)
 gp=BR/f"models/entity/{name}.geo.json";g=json.loads(gp.read_text())
 desc=g["minecraft:geometry"][0]["description"];desc["texture_width"]=128;desc["texture_height"]=128;desc["visible_bounds_width"]=6.5
 # keep model low-complexity for weak phones.
 cubes=g["minecraft:geometry"][0]["bones"][0].get("cubes",[])
 if len(cubes)>30:raise RuntimeError(f"{name}: too many cubes for low-end target: {len(cubes)}")
 gp.write_text(json.dumps(g,separators=(",",":")))

# Update pack metadata.
mc=JR/"pack.mcmeta";j=json.loads(mc.read_text());j["pack"]["description"]="LegendaryRais v3.6.1 PERFORMANCE ELITE | true 3D HD-efficient | low-end safe FX";mc.write_text(json.dumps(j,separators=(",",":")))
mf=BR/"manifest.json";b=json.loads(mf.read_text());b["header"]["name"]="RaisNet LegendaryRais v3.6.1 Performance Elite";b["header"]["description"]="Efficient-HD 3D weapons + ornate native armor + low-end-safe client FX";b["header"]["uuid"]="15041947-305e-423c-87a3-820641b9aa61";b["header"]["version"]=[3,6,1];b["modules"][0]["uuid"]="97245a9e-7ce1-41c2-b319-e203908b19b2";b["modules"][0]["version"]=[3,6,1];mf.write_text(json.dumps(b,separators=(",",":")))

# Mapping identifiers/models unchanged; versioned copy.
m=json.loads(MBASE.read_text());MOUT.write_text(json.dumps(m,indent=2))

# Validation and performance budget.
for root in (JR,BR):
 for p in root.rglob("*.json"):json.loads(p.read_text())
for name in W:
 jm=json.loads((JR/f"assets/{NS}/models/item/{name}.json").read_text())
 assert len(jm.get("elements",[]))>=8 and len(jm.get("elements",[]))<=32,(name,len(jm.get("elements",[])))
 assert jm["display"]["firstperson_righthand"]["scale"][0] <= .80
 for key in ("metal","grip","accent"):
  tex=jm["textures"][key];ns,path=tex.split(":",1);im=Image.open(JR/f"assets/{ns}/textures/{path}.png");assert im.size==(256,256)
 bg=json.loads((BR/f"models/entity/{name}.geo.json").read_text());cubes=bg["minecraft:geometry"][0]["bones"][0].get("cubes",[])
 assert 4<=len(cubes)<=30
 im=Image.open(BR/f"textures/items/{name}.png");assert im.size==(128,128)
for setn in ARM:
 for piece in PIECES:assert (BR/f"attachables/armor_{setn}_{piece}.json").is_file()
# accepted water relics untouched
assert (JR/"assets/soultide").exists() and (JR/"assets/legendaryrais").exists()
assert (BR/"models/entity/soul_tide_katana.geo.json").is_file() and (BR/"models/entity/abyss_leviathan_trident.geo.json").is_file()

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
print("PERF","Java weapon textures=256px; Bedrock=128px; Bedrock cube cap<=30")

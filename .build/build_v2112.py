from pathlib import Path
import json,zipfile,hashlib,struct,zlib,shutil,math

OUT=Path("LegendaryRais-Java-26plus-v2.1.2-FIX.zip")
ROOT=Path(".build/generated-v2112")
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)

def wr(p,s):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding="utf-8")
def png(path,w,h,fn):
 raw=b"".join(b"\x00"+b"".join(bytes(fn(x,y)) for x in range(w)) for y in range(h))
 def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
 data=b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+ch(b"IDAT",zlib.compress(raw,9))+ch(b"IEND",b"")
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)

# textures
pal={
"dark":((10,16,26,255),(28,42,58,255)),
"metal":((28,42,58,255),(62,82,104,255)),
"cyan":((30,150,220,255),(160,250,255,255)),
"water":((20,90,180,220),(90,220,255,210)),
"sand":((75,58,45,255),(115,88,62,255)),
"wrap":((12,14,18,255),(38,42,50,255)),
"bone":((125,145,155,255),(205,222,224,255)),
"void":((24,8,40,255),(82,30,118,255)),
}
for n,(a,b) in pal.items():
 png(Path("assets/legendaryrais/textures/item")/(n+".png"),16,16,
     lambda x,y,a=a,b=b: a if ((x//2+y//2)%2==0) else b)
png(Path("pack.png"),64,64,lambda x,y:(20,70+int(120*y/63),120+int(120*x/63),255))

def face(tex): return {k:{"uv":[0,0,16,16],"texture":"#"+tex} for k in ["north","south","east","west","up","down"]}
def cube(fr,to,tex,rot=None):
 d={"from":fr,"to":to,"faces":face(tex)}
 if rot:d["rotation"]={"origin":rot[0],"axis":rot[1],"angle":rot[2],"rescale":False}
 return d
def model(elements,display):
 return {"textures":{k:"legendaryrais:item/"+k for k in pal},"elements":elements,"display":display}

display={
"thirdperson_righthand":{"rotation":[0,90,-35],"translation":[0,2,1],"scale":[0.75,0.75,0.75]},
"thirdperson_lefthand":{"rotation":[0,-90,35],"translation":[0,2,1],"scale":[0.75,0.75,0.75]},
"firstperson_righthand":{"rotation":[0,90,-20],"translation":[1,3,1],"scale":[0.8,0.8,0.8]},
"firstperson_lefthand":{"rotation":[0,-90,20],"translation":[1,3,1],"scale":[0.8,0.8,0.8]},
"gui":{"rotation":[20,-35,20],"translation":[0,0,0],"scale":[0.72,0.72,0.72]},
"ground":{"translation":[0,3,0],"scale":[0.5,0.5,0.5]}
}

# Soul Tide Katana: layered blade, bevels, soul-sand guard, wrapped handle
s=[]
for y in range(-12,7,2):
 s+= [cube([6.8,y,6.8],[9.2,y+2,9.2],"wrap"),cube([7.25,y,7.25],[8.75,y+2,8.75],"dark")]
for y in [-10,-6,-2,2]:
 s+= [cube([6.45,y,6.45],[9.55,y+0.55,9.55],"cyan")]
s += [cube([3.0,6.2,5.8],[13.0,7.6,10.2],"dark"),
      cube([4.0,6.0,6.5],[12.0,7.9,9.5],"sand"),
      cube([5.0,6.4,6.9],[11.0,7.5,9.1],"cyan")]
for y in range(7,31,2):
 width=max(1.0,2.55-(y-7)*0.045)
 s += [cube([8-width,y,7.0],[8+width,y+2,9.0],"water"),
       cube([8-width-0.35,y,7.25],[8-width,y+2,8.75],"cyan"),
       cube([8+width,y,7.25],[8+width+0.35,y+2,8.75],"metal"),
       cube([7.55,y,6.65],[8.45,y+2,7.0],"dark")]
 if y%4==3: s += [cube([7.65,y+0.5,6.2],[8.35,y+1.3,6.65],"cyan")]
s += [cube([7.2,31,7.1],[8.8,32,8.9],"cyan"),
      cube([7.55,32,7.4],[8.45,33.2,8.6],"water")]
wr(Path("assets/legendaryrais/models/item/soul_tide_katana.json"),json.dumps(model(s,display),separators=(",",":")))

# Abyss Leviathan Trident: dark shaft, eye crown, 3 jaw-like prongs
a=[]
for y in range(-12,17,2):
 a += [cube([6.75,y,6.75],[9.25,y+2,9.25],"dark"),
       cube([7.2,y,7.2],[8.8,y+2,8.8],"metal")]
 if y%4==0:a += [cube([6.45,y,6.45],[9.55,y+0.55,9.55],"cyan")]
# crown and eye
a += [cube([3.0,16,5.3],[13.0,19,10.7],"dark"),
      cube([4.0,17,5.8],[12.0,20.5,10.2],"bone"),
      cube([6.0,17.4,4.8],[10.0,20.2,11.2],"void"),
      cube([7.0,18.0,4.3],[9.0,19.6,11.7],"cyan")]
# central prong
for y in range(19,34,2):
 w=max(0.65,1.7-(y-19)*0.065)
 a += [cube([8-w,y,7.0],[8+w,y+2,9.0],"metal"),
       cube([7.75,y,6.6],[8.25,y+2,7.0],"cyan")]
# side prongs / jaws
for side in (-1,1):
 cx=8+side*4.0
 for y in range(19,31,2):
  drift=side*(y-19)*0.10
  a += [cube([cx-1+drift,y,7.05],[cx+1+drift,y+2,8.95],"bone"),
        cube([cx-0.45+drift,y,6.65],[cx+0.45+drift,y+2,7.05],"cyan")]
 for y in (21,25,29):
  x=cx+side*(y-19)*0.10
  a += [cube([x-0.55,y,5.7],[x+0.55,y+1.0,6.65],"bone",([x,y,6.3],"z",22*side))]
# extra fins
for y in (13,16,20,23):
 a += [cube([4.5,y,5.3],[6.4,y+1.1,7.0],"bone",([6.2,y+0.5,7],"z",22)),
       cube([9.6,y,9.0],[11.5,y+1.1,10.7],"bone",([9.8,y+0.5,9],"z",-22))]
wr(Path("assets/legendaryrais/models/item/abyss_leviathan_trident.json"),json.dumps(model(a,display),separators=(",",":")))

# modern item model definitions
def modern(base,cmd,target):
 return {"model":{"type":"minecraft:range_dispatch","property":"minecraft:custom_model_data","index":0,
 "entries":[{"threshold":float(cmd),"model":{"type":"minecraft:model","model":target}},
            {"threshold":float(cmd+1),"model":{"type":"minecraft:model","model":"minecraft:item/"+base}}],
 "fallback":{"type":"minecraft:model","model":"minecraft:item/"+base}}}
wr(Path("assets/minecraft/items/netherite_sword.json"),json.dumps(modern("netherite_sword",910041,"legendaryrais:item/soul_tide_katana")))
wr(Path("assets/minecraft/items/trident.json"),json.dumps(modern("trident",910042,"legendaryrais:item/abyss_leviathan_trident")))
# explicit item_model names used by plugin
wr(Path("assets/soultide/items/soul_tide_katana.json"),json.dumps({"model":{"type":"minecraft:model","model":"legendaryrais:item/soul_tide_katana"}}))
wr(Path("assets/legendaryrais/items/abyss_leviathan_trident.json"),json.dumps({"model":{"type":"minecraft:model","model":"legendaryrais:item/abyss_leviathan_trident"}}))
# legacy 1.21.1 CMD fallbacks
wr(Path("assets/minecraft/models/item/netherite_sword.json"),json.dumps({"parent":"minecraft:item/handheld","textures":{"layer0":"minecraft:item/netherite_sword"},"overrides":[{"predicate":{"custom_model_data":910041},"model":"legendaryrais:item/soul_tide_katana"}]}))
wr(Path("assets/minecraft/models/item/trident.json"),json.dumps({"parent":"minecraft:item/generated","textures":{"layer0":"minecraft:item/trident"},"overrides":[{"predicate":{"custom_model_data":910042},"model":"legendaryrais:item/abyss_leviathan_trident"}]}))

wr(Path("pack.mcmeta"),json.dumps({"pack":{"pack_format":34,"supported_formats":{"min_inclusive":34,"max_inclusive":88},"min_format":[34,0],"max_format":[88,0],"description":"LegendaryRais v2.1.2 FIX - Java 1.21.1 to 26.2"}}))
if OUT.exists():OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(ROOT.rglob("*")):
  if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
 bad=z.testzip()
 if bad:raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
Path("LegendaryRais-Java-26plus-v2.1.2-FIX.sha1").write_text(sha+"\n")
print("VALID",OUT.stat().st_size,sha,len(s),len(a))

from pathlib import Path
import json, zipfile, hashlib, struct, zlib, shutil, math

ROOT=Path(".build/generated-v250-bedrock")
OUT=Path("LegendaryRais-Bedrock-v2.5.0-LIVE-AURA.mcpack")
MAP=Path("LegendaryRais-Geyser-v2.5.0-mappings.json")
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)

def wr(p,obj):
    p=ROOT/p; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def png(path,w,h,fn):
    raw=b"".join(b"\x00"+b"".join(bytes(fn(x,y)) for x in range(w)) for y in range(h))
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    data=b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+ch(b"IDAT",zlib.compress(raw,9))+ch(b"IEND",b"")
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)

def clamp(v): return max(0,min(255,int(v)))
def noise(x,y,s): return (((x*92837111)^(y*689287499)^(s*283923481))&255)/255.0

def soul_tex(x,y):
    n=noise(x,y,7); wave=(math.sin(x*.09+y*.04)+math.cos(y*.07)+2)/4
    r=clamp(5+18*n); g=clamp(45+135*wave+40*n); b=clamp(90+145*wave+20*n)
    if (x+y)%53<2: r,g,b=110,245,255
    return (r,g,b,255)

def abyss_tex(x,y):
    n=noise(x,y,13); wave=(math.sin(x*.07-y*.11)+1)/2
    r=clamp(12+75*wave+30*n); g=clamp(10+55*n); b=clamp(28+115*wave+70*n)
    if (x*3+y*5)%67<2: r,g,b=30,225,255
    return (r,g,b,255)

def icon_soul(x,y):
    dx=x-32; blade=abs(dx-(y-12)*.17)<3 and 8<y<56
    handle=abs(dx)<5 and 4<y<18
    glow=abs(dx-(y-12)*.17)<6 and 8<y<56
    if blade:return (80,235,255,255)
    if handle:return (12,16,24,255)
    if glow:return (10,80,160,180)
    return (0,0,0,0)

def icon_abyss(x,y):
    shaft=abs(x-32)<3 and 5<y<47
    crown=20<x<44 and 39<y<49
    prong=(abs(x-32)<3 or abs(x-22)<3 or abs(x-42)<3) and 45<y<60
    if prong:return (75,225,255,255)
    if crown:return (70,30,105,255)
    if shaft:return (22,28,42,255)
    return (0,0,0,0)

png(Path("textures/items/soul_tide_katana.png"),256,256,soul_tex)
png(Path("textures/items/abyss_leviathan_trident.png"),256,256,abyss_tex)
png(Path("textures/items/soul_tide_katana_icon.png"),64,64,icon_soul)
png(Path("textures/items/abyss_leviathan_trident_icon.png"),64,64,icon_abyss)

wr(Path("manifest.json"),{
 "format_version":2,
 "header":{"name":"RaisNet LegendaryRais v2.5 LIVE AURA","description":"Soul Tide Katana + Abyss Leviathan for Geyser Bedrock","uuid":"22c9a77e-897d-41cb-9acd-063c9d33a4e8","version":[2,5,0],"min_engine_version":[1,21,0]},
 "modules":[{"type":"resources","uuid":"a25e11f5-b4db-4260-9c8a-bec32a889f72","version":[2,5,0],"description":"LegendaryRais Bedrock resources"}]
})

wr(Path("textures/item_texture.json"),{
 "resource_pack_name":"RaisNet LegendaryRais v2.5 LIVE AURA",
 "texture_name":"atlas.items",
 "texture_data":{
   "raisnet:soul_tide_katana":{"textures":"textures/items/soul_tide_katana_icon"},
   "raisnet:abyss_leviathan_trident":{"textures":"textures/items/abyss_leviathan_trident_icon"}
 }
})

def attach(identifier,texture,geometry):
    return {
     "format_version":"1.20.30",
     "minecraft:attachable":{"description":{
       "identifier":identifier,
       "item":{identifier:"query.is_owner_identifier_any('minecraft:player')"},
       "materials":{"default":"entity_alphatest","enchanted":"entity_alphatest_glint"},
       "textures":{"default":texture,"enchanted":"textures/misc/enchanted_item_glint"},
       "geometry":{"default":geometry},
       "animations":{"hold_first_person":"animation.steve_head.hold_first_person","hold_third_person":"animation.steve_head.hold_third_person"},
       "scripts":{"animate":[{"hold_first_person":"context.is_first_person == 1.0"},{"hold_third_person":"context.is_first_person == 0.0"}]},
       "render_controllers":["controller.render.item_default"]
     }}
    }

wr(Path("attachables/soul_tide_katana.player.json"),attach("raisnet:soul_tide_katana","textures/items/soul_tide_katana","geometry.raisnet_soul_tide_katana"))
wr(Path("attachables/abyss_leviathan_trident.player.json"),attach("raisnet:abyss_leviathan_trident","textures/items/abyss_leviathan_trident","geometry.raisnet_abyss_leviathan"))

# Bedrock geometry is intentionally built around the holder's item-slot binding.
soul_cubes=[]
# handle
for i in range(8):
    soul_cubes.append({"origin":[-1.4,-10+i*2, -1.4],"size":[2.8,2.0,2.8],"uv":[0,0]})
# guard
soul_cubes += [
 {"origin":[-6,6,-2],"size":[12,1.5,4],"uv":[0,0]},
 {"origin":[-3.7,5.4,-2.6],"size":[7.4,2.4,5.2],"uv":[16,0]}
]
# slender curved blue blade
for i in range(28):
    t=i/27.0; y=7+i*.9; x=1.9*(t**1.55); w=2.4*(1-t)+.35*t
    soul_cubes.append({"origin":[x-w,y,-.65],"size":[w*2,.95,1.3],"uv":[0,32]})
# sharp kissaki
soul_cubes += [
 {"origin":[1.55,31.8,-.48],"size":[1.2,2.0,.96],"uv":[32,32]},
 {"origin":[2.15,33.4,-.32],"size":[.45,1.2,.64],"uv":[48,32]}
]
# built-in fake aura droplets
for i in range(20):
    t=i/19.0; y=9+t*25; a=i*1.6; x=1.9*(t**1.55)+math.cos(a)*2.4; z=math.sin(a)*2.0
    soul_cubes.append({"origin":[round(x-.18,2),round(y-.18,2),round(z-.18,2)],"size":[.36,.36,.36],"uv":[64,0]})

abyss_cubes=[]
# shaft
for i in range(15):
    abyss_cubes.append({"origin":[-1.25,-12+i*2,-1.25],"size":[2.5,2,2.5],"uv":[0,0]})
# crown/head
abyss_cubes += [
 {"origin":[-6,16,-3],"size":[12,3,6],"uv":[0,32]},
 {"origin":[-4.5,18,-3.5],"size":[9,3.2,7],"uv":[32,32]}
]
# three prongs
for cx in (-4.5,0,4.5):
    for j in range(9):
        t=j/8.0; y=20+j*1.35; w=1.8*(1-t)+.45*t
        abyss_cubes.append({"origin":[cx-w/2,y,-.75],"size":[w,1.4,1.5],"uv":[64,32]})
# teeth/horns
for side in (-1,1):
    for j in range(4):
        abyss_cubes.append({"origin":[side*(5.2+j*.5)-.4,18+j*2,-2.8],"size":[.8,2.0,1.2],"uv":[96,32],"pivot":[side*(5.2+j*.5),19+j*2,-2.2],"rotation":[0,0,side*22.5]})
# fake abyss droplets
for i in range(18):
    a=i*1.35; y=18+(i%9)*1.4; x=math.cos(a)*6; z=math.sin(a)*2.8
    abyss_cubes.append({"origin":[round(x-.2,2),round(y-.2,2),round(z-.2,2)],"size":[.4,.4,.4],"uv":[128,0]})

def geo(identifier,cubes):
    return {"format_version":"1.16.0","minecraft:geometry":[{
      "description":{"identifier":identifier,"texture_width":256,"texture_height":256,
                     "visible_bounds_width":5,"visible_bounds_height":6,"visible_bounds_offset":[0,10,0]},
      "bones":[{"name":"bb_main","pivot":[0,8,0],"binding":"q.item_slot_to_bone_name(context.item_slot)","cubes":cubes}]
    }]}

wr(Path("models/entity/soul_tide_katana.geo.json"),geo("geometry.raisnet_soul_tide_katana",soul_cubes))
wr(Path("models/entity/abyss_leviathan_trident.geo.json"),geo("geometry.raisnet_abyss_leviathan",abyss_cubes))

mapping={
 "format_version":2,
 "items":{
   "minecraft:netherite_sword":[{
     "type":"legacy","custom_model_data":910041,
     "bedrock_identifier":"raisnet:soul_tide_katana",
     "display_name":"Soul Tide Katana",
     "bedrock_options":{"icon":"raisnet:soul_tide_katana","display_handheld":True,"creative_category":"equipment"}
   }],
   "minecraft:trident":[{
     "type":"legacy","custom_model_data":910042,
     "bedrock_identifier":"raisnet:abyss_leviathan_trident",
     "display_name":"Abyss Leviathan Trident",
     "bedrock_options":{"icon":"raisnet:abyss_leviathan_trident","display_handheld":True,"creative_category":"equipment"}
   }]
 }
}
MAP.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

if OUT.exists():OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad:raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
Path("LegendaryRais-Bedrock-v2.5.0-LIVE-AURA.sha1").write_text(sha+"\n")
print("VALID",OUT.stat().st_size,sha,"SOUL_CUBES",len(soul_cubes),"ABYSS_CUBES",len(abyss_cubes))

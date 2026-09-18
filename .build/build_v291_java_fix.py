from pathlib import Path
import subprocess, zipfile, json, shutil, hashlib, math

BASE=Path("LegendaryRais-Java-26plus-v2.8.0-REALISM-FX.zip")
OUT=Path("LegendaryRais-Java-26plus-v2.9.1-PAPER-26.2-FIX.zip")
SHA=Path("LegendaryRais-Java-26plus-v2.9.1-PAPER-26.2-FIX.sha1")
ROOT=Path(".build/generated-v291-java")

subprocess.run(["python3",".build/build_v280_java.py"],check=True)
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def wr(rel,obj):
    p=ROOT/rel
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

textures={
 "dark":"legendaryrais:item/dark_metal",
 "steel":"legendaryrais:item/blue_steel",
 "cyan":"legendaryrais:item/cyan_rune",
 "wrap":"legendaryrais:item/black_wrap",
 "water":"legendaryrais:item/water",
 "void":"legendaryrais:item/void"
}

def face(tex):
    return {k:{"texture":"#"+tex} for k in ["north","south","east","west","up","down"]}

def cube(fr,to,tex,rot=None):
    d={"from":[round(v,3) for v in fr],"to":[round(v,3) for v in to],"faces":face(tex)}
    if rot:
        d["rotation"]={"origin":[round(v,3) for v in rot[0]],"axis":rot[1],"angle":rot[2],"rescale":True}
    return d

# ------------------------------------------------------------------
# SOVEREIGN BLADE V5 — straight fantasy longsword, NOT katana.
# ------------------------------------------------------------------
s=[]
s += [
 cube([6.8,-8.5,6.8],[9.2,-6.4,9.2],"dark"),
 cube([7.15,-6.5,7.15],[8.85,4.8,8.85],"wrap"),
 cube([6.7,4.4,6.7],[9.3,6.2,9.3],"dark"),
 cube([7.35,-9.5,7.35],[8.65,-8.0,8.65],"cyan",([8,-8.7,8],"z",45))
]
for y in [-5.5,-3.4,-1.3,.8,2.9]:
    s.append(cube([6.95,y,6.95],[9.05,y+.32,9.05],"cyan"))
# broad ornate crossguard
s += [
 cube([2.5,5.0,7.0],[13.5,6.3,9.0],"dark"),
 cube([.6,5.2,7.1],[6.7,6.5,8.9],"steel",([6.2,5.8,8],"z",-22.5)),
 cube([9.3,5.2,7.1],[15.4,6.5,8.9],"steel",([9.8,5.8,8],"z",22.5)),
 cube([.4,6.4,7.25],[4.4,7.15,8.75],"cyan",([4.0,6.7,8],"z",-45)),
 cube([11.6,6.4,7.25],[15.6,7.15,8.75],"cyan",([12.0,6.7,8],"z",45)),
 cube([6.5,5.1,6.5],[9.5,7.5,9.5],"cyan",([8,6.2,8],"z",45))
]
# straight double-edged tapered blade
y0=6.7
for i in range(44):
    t=i/43.0
    ya=y0+t*24.7
    yb=min(31.55,ya+.62)
    half=3.0*(1-t)**.58+.22
    s.append(cube([8-half,ya,7.32],[8+half,yb,8.68],"steel"))
    edge=min(.30,half*.25)
    s.append(cube([8-half-.05,ya,7.16],[8-half+edge,yb,8.84],"cyan"))
    s.append(cube([8+half-edge,ya,7.16],[8+half+.05,yb,8.84],"cyan"))
    if i%5==0 and i<38:
        s.append(cube([7.73,ya+.08,6.98],[8.27,min(yb,ya+.43),9.02],"water"))
# pointed tip
s += [
 cube([6.9,31.1,7.35],[9.1,31.65,8.65],"steel"),
 cube([7.35,31.55,7.45],[8.65,31.9,8.55],"cyan"),
 cube([7.78,31.86,7.6],[8.22,32.0,8.4],"cyan")
]

display_sword={
 "thirdperson_righthand":{"rotation":[2,-90,51],"translation":[.2,2.4,.8],"scale":[.66,.66,.66]},
 "thirdperson_lefthand":{"rotation":[2,90,-51],"translation":[.2,2.4,.8],"scale":[.66,.66,.66]},
 "firstperson_righthand":{"rotation":[0,-92,38],"translation":[1.1,2.9,1.5],"scale":[.78,.78,.78]},
 "firstperson_lefthand":{"rotation":[0,92,-38],"translation":[1.1,2.9,1.5],"scale":[.78,.78,.78]},
 "gui":{"rotation":[18,145,-42],"translation":[0,-.3,0],"scale":[.66,.66,.66]},
 "ground":{"translation":[0,2.6,0],"scale":[.46,.46,.46]},
 "fixed":{"rotation":[0,180,-38],"scale":[.60,.60,.60]}
}
sword_model={"credit":"LegendaryRais v2.9.1 Sovereign Blade","textures":textures,"elements":s,"display":display_sword}
for rel in [
 "assets/soultide/models/item/soul_tide_sovereign_blade.json",
 "assets/soultide/models/item/soul_tide_katana.json"
]:
    wr(rel,sword_model)
for name in ["soul_tide_sovereign_blade","soul_tide_katana"]:
    wr(f"assets/soultide/items/{name}.json",{
      "hand_animation_on_swap":True,
      "oversized_in_gui":True,
      "model":{"type":"minecraft:model","model":"soultide:item/soul_tide_sovereign_blade"}
    })

# ------------------------------------------------------------------
# LEVIATHAN TRIDENT V5 — long, slim, three-prong legendary trident.
# ------------------------------------------------------------------
t=[]
t += [
 cube([7.15,-15.0,7.15],[8.85,-12.4,8.85],"cyan",([8,-13.7,8],"z",45)),
 cube([7.35,-13.0,7.35],[8.65,19.5,8.65],"wrap")
]
for y in [-11,-6,-1,4,9,14,18]:
    t.append(cube([7.05,y,7.05],[8.95,y+.38,8.95],"cyan"))
t += [
 cube([5.8,18.7,6.9],[10.2,21.0,9.1],"dark"),
 cube([6.7,20.0,6.5],[9.3,22.6,9.5],"cyan",([8,21.2,8],"z",45))
]
# center spear
for i in range(22):
    f=i/21.0
    ya=21.0+f*10.7
    yb=min(32,ya+.58)
    half=1.2*(1-f)+.15
    t.append(cube([8-half,ya,7.3],[8+half,yb,8.7],"steel"))
    t.append(cube([8-half-.05,ya,7.12],[8-half+.20,yb,8.88],"cyan"))
    t.append(cube([8+half-.20,ya,7.12],[8+half+.05,yb,8.88],"cyan"))
# side swept tines
for side in (-1,1):
    xbase=3.15 if side<0 else 12.85
    ang=22.5 if side<0 else -22.5
    t.append(cube([xbase-.65,20.0,7.2],[xbase+.65,27.0,8.8],"steel",([xbase,21.0,8],"z",ang)))
    x2=2.0 if side<0 else 14.0
    t.append(cube([x2-.50,25.2,7.25],[x2+.50,30.8,8.75],"steel"))
    t.append(cube([x2-.22,29.9,7.35],[x2+.22,32.0,8.65],"cyan"))
    # shoulder wings
    if side<0:
        t.append(cube([1.0,19.5,7.1],[7.2,20.8,8.9],"dark",([6.7,20.1,8],"z",-22.5)))
    else:
        t.append(cube([8.8,19.5,7.1],[15.0,20.8,8.9],"dark",([9.3,20.1,8],"z",22.5)))

display_tri={
 "thirdperson_righthand":{"rotation":[0,-90,48],"translation":[.2,2.6,.5],"scale":[.62,.62,.62]},
 "thirdperson_lefthand":{"rotation":[0,90,-48],"translation":[.2,2.6,.5],"scale":[.62,.62,.62]},
 "firstperson_righthand":{"rotation":[0,-92,37],"translation":[1.3,3.1,.9],"scale":[.70,.70,.70]},
 "firstperson_lefthand":{"rotation":[0,92,-37],"translation":[1.3,3.1,.9],"scale":[.70,.70,.70]},
 "gui":{"rotation":[18,-34,-40],"scale":[.65,.65,.65]},
 "ground":{"translation":[0,2,0],"scale":[.44,.44,.44]},
 "fixed":{"rotation":[0,0,-45],"scale":[.58,.58,.58]}
}
tri_model={"credit":"LegendaryRais v2.9.1 Leviathan Trident","textures":textures,"elements":t,"display":display_tri}
wr("assets/legendaryrais/models/item/abyss_leviathan_trident.json",tri_model)
wr("assets/legendaryrais/items/abyss_leviathan_trident.json",{
 "hand_animation_on_swap":True,
 "oversized_in_gui":True,
 "model":{"type":"minecraft:model","model":"legendaryrais:item/abyss_leviathan_trident"}
})

# ------------------------------------------------------------------
# Java skill FX: custom ItemDisplay models, no vanilla particle dependency.
# Reuse the proven v2.8 3D FX geometry but expose v2.9 model IDs.
# ------------------------------------------------------------------
mapping={
 "fx_soul_slash":"fx_water_slash",
 "fx_tidal_crescent":"fx_water_slash",
 "fx_undertow_ring":"fx_water_ring",
 "fx_domain_sigil":"fx_abyss_ring",
 "fx_leviathan_fang":"fx_abyss_slash",
 "fx_maelstrom":"fx_abyss_ring",
 "fx_leviathan_impact":"fx_abyss_ring",
 "fx_lightning_spear":"fx_abyss_slash"
}
for dst,src in mapping.items():
    srcp=ROOT/f"assets/legendaryrais/models/item/{src}.json"
    data=json.loads(srcp.read_text(encoding="utf-8"))
    wr(f"assets/legendaryrais/models/item/{dst}.json",data)
    wr(f"assets/legendaryrais/items/{dst}.json",{
      "oversized_in_gui":True,
      "model":{"type":"minecraft:model","model":f"legendaryrais:item/{dst}"}
    })

# Modern vanilla selectors + CMD fallback.
wr("assets/minecraft/items/netherite_sword.json",{
 "hand_animation_on_swap":True,
 "model":{
  "type":"minecraft:range_dispatch","property":"minecraft:custom_model_data","index":0,
  "entries":[
   {"threshold":910041.0,"model":{"type":"minecraft:model","model":"soultide:item/soul_tide_sovereign_blade"}},
   {"threshold":910042.0,"model":{"type":"minecraft:model","model":"minecraft:item/netherite_sword"}}
  ],
  "fallback":{"type":"minecraft:model","model":"minecraft:item/netherite_sword"}
 }})

# Keep vanilla trident special rendering as fallback.
vanilla_tri={
 "type":"minecraft:select","property":"minecraft:display_context",
 "cases":[{"when":["gui","ground","fixed","on_shelf"],"model":{"type":"minecraft:model","model":"minecraft:item/trident"}}],
 "fallback":{"type":"minecraft:condition","property":"minecraft:using_item",
   "on_false":{"type":"minecraft:special","base":"minecraft:item/trident_in_hand","model":{"type":"minecraft:trident"}},
   "on_true":{"type":"minecraft:special","base":"minecraft:item/trident_throwing","model":{"type":"minecraft:trident"}}}
}
wr("assets/minecraft/items/trident.json",{
 "hand_animation_on_swap":True,
 "model":{"type":"minecraft:range_dispatch","property":"minecraft:custom_model_data","index":0,
  "entries":[
   {"threshold":910042.0,"model":{"type":"minecraft:model","model":"legendaryrais:item/abyss_leviathan_trident"}},
   {"threshold":910043.0,"model":vanilla_tri}
  ],
  "fallback":vanilla_tri
 }})

fxnames=list(mapping.keys())
wr("assets/minecraft/items/paper.json",{
 "model":{"type":"minecraft:range_dispatch","property":"minecraft:custom_model_data","index":0,
  "entries":[
   *[{"threshold":910101.0+i,"model":{"type":"minecraft:model","model":f"legendaryrais:item/{n}"}} for i,n in enumerate(fxnames)],
   {"threshold":910109.0,"model":{"type":"minecraft:model","model":"minecraft:item/paper"}}
  ],
  "fallback":{"type":"minecraft:model","model":"minecraft:item/paper"}
 }})

# Paper/Minecraft 26.2 resource format is 88.
wr("pack.mcmeta",{"pack":{
 "description":"LegendaryRais v2.9.1 FIX • Paper/Java 26.2 • Sovereign Blade + Leviathan V5 • ItemDisplay skill FX",
 "min_format":[88,0],"max_format":[88,0]
}})

# Validate all JSON and archive integrity.
for jp in ROOT.rglob("*.json"):
    json.loads(jp.read_text(encoding="utf-8"))
if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file(): z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad: raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n",encoding="utf-8")
print("VALID",OUT.stat().st_size,sha,"SWORD_ELEMENTS",len(s),"TRIDENT_ELEMENTS",len(t),"FX",len(fxnames))

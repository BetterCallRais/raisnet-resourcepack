from pathlib import Path
import json, math, shutil, zipfile, hashlib, random
from PIL import Image, ImageDraw

BASE=Path("LegendaryRais-Bedrock-v3.5.3-FULL-REFORGE.mcpack")
BASEMAP=Path("LegendaryRais-Geyser-v3.5.3-mappings.json")
OUT=Path("LegendaryRais-Bedrock-v3.5.4-VISUAL-INTEGRITY.mcpack")
SHA=Path("LegendaryRais-Bedrock-v3.5.4-VISUAL-INTEGRITY.sha1")
MAP=Path("LegendaryRais-Geyser-v3.5.4-mappings.json")
ROOT=Path(".build/generated-v354-bedrock")

if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z: z.extractall(ROOT)

def wr(rel,obj):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

def cube(origin,size,uv=(0,0),pivot=None,rot=None):
    c={"origin":[round(float(v),3) for v in origin],"size":[round(float(v),3) for v in size],"uv":list(uv)}
    if pivot is not None:c["pivot"]=[round(float(v),3) for v in pivot]
    if rot is not None:c["rotation"]=[round(float(v),3) for v in rot]
    return c

THEMES={
 "emberfall_claymore":((72,31,17),(155,64,24),(255,116,35)),
 "noctis_longsword":((23,19,32),(75,49,101),(185,78,248)),
 "stormpiercer_recurve_bow":((20,45,59),(58,110,136),(95,226,249)),
 "gaia_war_spear":((39,54,29),(91,115,54),(159,218,92)),
 "astral_twin_daggers":((33,23,50),(90,58,119),(216,105,252))
}

def make_atlas(name,base,mid,accent):
    p=ROOT/f"textures/items/{name}.png"; p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new("RGBA",(256,256),base+(255,)); px=im.load(); random.seed("b354-"+name)
    for y in range(256):
        for x in range(256):
            n=random.randint(-5,5)
            if y<128: src=mid
            elif x<128: src=tuple(max(0,v-15) for v in base)
            else: src=accent
            mix=.16 if y<128 else .08
            c=tuple(max(0,min(255,int(base[i]*(1-mix)+src[i]*mix+n))) for i in range(3))
            px[x,y]=c+(255,)
    d=ImageDraw.Draw(im,"RGBA")
    for y in (32,64,96): d.line((0,y,255,y),fill=mid+(30,),width=1)
    for y in (144,176,208,240): d.line((128,y,255,y),fill=accent+(70,),width=1)
    im.save(p,optimize=True)

def sword(heavy=False,dark=False):
    a=[
      cube((-1,-13,-.7),(2,1.5,1.4),(128,132)),
      cube((-.72,-11.5,-.5),(1.44,8.0,1.0),(0,140))
    ]
    for y in (-10,-7.8,-5.6): a.append(cube((-.95,y,-.58),(1.9,.2,1.16),(136,140)))
    a += [
      cube((-4.0,-3.5,-.3),(3.6,.65,.6),(136,136),(-.45,-3.2,0),(0,0,-22.5)),
      cube((.4,-3.5,-.3),(3.6,.65,.6),(136,136),(.45,-3.2,0),(0,0,22.5)),
      cube((-1.1,-3.1,-.58),(2.2,1.2,1.16),(0,96))
    ]
    width=4.0 if heavy else 2.2
    a += [cube((-width/2,-1.9,-.34),(width,27.0,.68),(0,0)),
          cube((-width/2+.18,-1.5,-.40),(.26,26.0,.80),(192,144)),
          cube((width/2-.44,-1.5,-.40),(.26,26.0,.80),(192,144))]
    if dark: a.append(cube((-.13,-1.1,-.44),(.26,25.2,.88),(208,144)))
    a += [cube((-width*.38,25.0,-.27),(width*.76,3.0,.54),(16,0)),
          cube((-.35,28.0,-.18),(.7,2.1,.36),(32,0))]
    return a

def bow():
    a=[cube((-.7,-3.0,-.5),(1.4,7.0,1.0),(0,140)),cube((-1.35,-.1,-.72),(2.7,2.5,1.44),(192,144))]
    for cx,cy,ang in [(0,5,0),(.7,8.1,18),(1.7,11.2,24),(2.8,14.4,30),(3.8,17.7,36),(4.5,21.0,43),
                      (0,-4,0),(-.7,-7.1,-18),(-1.7,-10.2,-24),(-2.8,-13.4,-30),(-3.8,-16.7,-36),(-4.5,-20.0,-43)]:
        a.append(cube((cx-.36,cy-1.7,-.30),(.72,3.4,.60),(0,0),(cx,cy,0),(0,0,ang)))
    a += [cube((-.08,-21.8,-.06),(.16,20.2,.12),(208,144),(-.1,-12,0),(0,0,-10)),
          cube((-.08,1.4,-.06),(.16,21.8,.12),(208,144),(.1,12,0),(0,0,10))]
    return a

def spear():
    return [
      cube((-.38,-16,-.38),(.76,35.2,.76),(0,140)),
      cube((-.62,-12,-.48),(1.24,.18,.96),(136,140)),
      cube((-.62,-3,-.48),(1.24,.18,.96),(136,140)),
      cube((-.62,6,-.48),(1.24,.18,.96),(136,140)),
      cube((-.62,15,-.48),(1.24,.18,.96),(136,140)),
      cube((-.82,19.0,-.34),(1.64,8.3,.68),(0,0)),
      cube((-2.2,20.1,-.26),(1.7,4.7,.52),(16,0),(-.5,22.3,0),(0,0,-22.5)),
      cube((.5,20.1,-.26),(1.7,4.7,.52),(16,0),(.5,22.3,0),(0,0,22.5)),
      cube((-.25,27.1,-.18),(.5,3.4,.36),(192,144))
    ]

def daggers():
    a=[]
    for s in (-1,1):
        cx=s*2.75
        a += [
          cube((cx-.52,-9.0,-.42),(1.04,6.4,.84),(0,140)),
          cube((cx-1.35,-2.8,-.25),(2.7,.60,.50),(192,144)),
          cube((cx-.78,-2.2,-.28),(1.56,14.0,.56),(0,0)),
          cube((cx-s*.95,3.8,-.20),(.72,5.4,.40),(192,144),(cx-s*.4,6.4,0),(0,0,22.5*s)),
          cube((cx-.20,11.8,-.17),(.40,3.6,.34),(192,144))
        ]
    return a

def geo(identifier,cubes):
    return {"format_version":"1.16.0","minecraft:geometry":[{
      "description":{"identifier":identifier,"texture_width":256,"texture_height":256,
                     "visible_bounds_width":7,"visible_bounds_height":8,"visible_bounds_offset":[0,8,0]},
      "bones":[{"name":"bb_main","pivot":[0,8,0],"binding":"q.item_slot_to_bone_name(context.item_slot)","cubes":cubes}]
    }]}

def weapon_attach(identifier,texture,geometry):
    return {"format_version":"1.20.30","minecraft:attachable":{"description":{
      "identifier":identifier,
      "item":{identifier:"query.is_owner_identifier_any('minecraft:player')"},
      "materials":{"default":"entity_alphatest","enchanted":"entity_alphatest_glint"},
      "textures":{"default":texture,"enchanted":"textures/misc/enchanted_item_glint"},
      "geometry":{"default":geometry},
      "render_controllers":["controller.render.item_default"]
    }}}

weapons={
 "emberfall_claymore":("geometry.raisnet_emberfall_v354",sword(True,False)),
 "noctis_longsword":("geometry.raisnet_noctis_v354",sword(False,True)),
 "stormpiercer_recurve_bow":("geometry.raisnet_stormpiercer_v354",bow()),
 "gaia_war_spear":("geometry.raisnet_gaia_v354",spear()),
 "astral_twin_daggers":("geometry.raisnet_astral_v354",daggers())
}
for name,(gid,cubes) in weapons.items():
    make_atlas(name,*THEMES[name])
    wr(f"models/entity/{name}.geo.json",geo(gid,cubes))
    wr(f"attachables/{name}.player.json",weapon_attach(f"raisnet:{name}",f"textures/items/{name}",gid))

ARMOR={
 "phoenix":((58,20,10),(126,49,16),(255,126,34)),
 "voidwalker":((20,14,31),(55,32,82),(181,80,240)),
 "titan":((27,42,31),(62,82,49),(142,188,96)),
 "celestial":((27,46,64),(67,105,137),(150,214,246)),
 "water_sovereign":((15,46,61),(35,94,117),(82,202,230))
}
PIECES=("helmet","chest","legs","boots")

def armor_tex(setname,base,mid,glow,layer):
    p=ROOT/f"textures/models/armor/{setname}_{layer}.png"; p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new("RGBA",(64,32),base+(255,)); px=im.load(); random.seed("barmor-"+setname+str(layer))
    for y in range(32):
        for x in range(64):
            checker=((x//4+y//4)%2)*4; n=random.randint(-3,3)
            px[x,y]=tuple(max(0,min(255,base[i]+checker+n)) for i in range(3))+(255,)
    d=ImageDraw.Draw(im,"RGBA")
    for y in range(4,32,8):d.line((1,y,62,y),fill=mid+(52,),width=1)
    if setname=="phoenix":
        for x in (8,24,40,56): d.line((x,5,x-2,11),fill=glow+(120,),width=1)
    elif setname=="voidwalker":
        for x,y in ((8,6),(20,18),(35,9),(50,23),(59,13)):d.point((x,y),fill=glow+(210,))
    elif setname=="titan":
        for x in range(5,64,16):d.rectangle((x,7,x+7,12),outline=glow+(65,),width=1)
    elif setname=="celestial":
        for x in range(7,64,14):d.line((x,5,x+3,8),fill=glow+(115,),width=1)
    else:
        for x in range(0,64,16):d.arc((x,8,x+14,20),0,180,fill=glow+(110,),width=1)
    im.save(p,optimize=True)

def armor_icon(setname,piece,base,mid,glow):
    p=ROOT/f"textures/items/armor_{setname}_{piece}.png"; p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new("RGBA",(32,32),(0,0,0,0)); d=ImageDraw.Draw(im,"RGBA")
    fill=base+(255,); edge=mid+(255,); hi=glow+(225,)
    if piece=="helmet":
        d.rounded_rectangle((7,5,24,18),radius=3,fill=fill,outline=edge,width=2);d.rectangle((9,16,22,22),fill=fill,outline=edge,width=1)
    elif piece=="chest":
        d.polygon([(6,8),(11,5),(21,5),(26,8),(23,25),(9,25)],fill=fill,outline=edge);d.line((16,7,16,24),fill=hi,width=1)
    elif piece=="legs":
        d.polygon([(8,5),(24,5),(23,14),(20,27),(16,27),(15,15),(12,27),(8,27),(9,14)],fill=fill,outline=edge)
    else:
        d.polygon([(7,10),(14,10),(14,24),(6,27)],fill=fill,outline=edge);d.polygon([(18,10),(25,10),(26,27),(18,24)],fill=fill,outline=edge)
    d.line((10,8,22,8),fill=hi,width=1)
    im.save(p,optimize=True)

def armor_attach(identifier,setname,piece):
    geometry={
      "helmet":"geometry.humanoid.armor.helmet",
      "chest":"geometry.humanoid.armor.chestplate",
      "legs":"geometry.humanoid.armor.leggings",
      "boots":"geometry.humanoid.armor.boots"
    }[piece]
    setup={
      "helmet":"v.helmet_layer_visible = false;",
      "chest":"v.chest_layer_visible = false;",
      "legs":"v.leg_layer_visible = false;",
      "boots":"v.boot_layer_visible = false;"
    }[piece]
    layer=2 if piece=="legs" else 1
    return {"format_version":"1.8.0","minecraft:attachable":{"description":{
      "identifier":identifier,
      "materials":{"default":"armor","enchanted":"armor_enchanted"},
      "textures":{"default":f"textures/models/armor/{setname}_{layer}","enchanted":"textures/misc/enchanted_actor_glint"},
      "geometry":{"default":geometry},
      "scripts":{"parent_setup":setup},
      "render_controllers":["controller.render.armor.v2"]
    }}}

# icons + stable vanilla armor attachables
for setname,(base,mid,glow) in ARMOR.items():
    armor_tex(setname,base,mid,glow,1); armor_tex(setname,base,mid,glow,2)
    for piece in PIECES:
        armor_icon(setname,piece,base,mid,glow)
        wr(f"attachables/armor_{setname}_{piece}.json",armor_attach(f"raisnet:{setname}_{piece}",setname,piece))

# update item atlas
it=ROOT/"textures/item_texture.json"
idata=json.loads(it.read_text())
td=idata.setdefault("texture_data",{})
for name in weapons: td[f"raisnet:{name}"]={"textures":f"textures/items/{name}"}
for setname in ARMOR:
    for piece in PIECES: td[f"raisnet:{setname}_{piece}"]={"textures":f"textures/items/armor_{setname}_{piece}"}
it.write_text(json.dumps(idata,separators=(",",":")))

# Modern Geyser v2 mappings: item_model definitions for v26.x.
mapping=json.loads(BASEMAP.read_text())
mi=mapping.setdefault("items",{})

# Remove obsolete non-water v3.5.x legacy entries, preserve Soul Tide + Leviathan legacy mappings.
for base,arr in list(mi.items()):
    mi[base]=[x for x in arr if not (x.get("type")=="legacy" and x.get("custom_model_data") in (910051,910052,910053,910054,910055))]

def add_definition(base,model,identifier,title,handheld=True):
    arr=mi.setdefault(base,[])
    arr=[x for x in arr if not (x.get("type")=="definition" and x.get("model")==model)]
    arr.append({"type":"definition","model":model,"bedrock_identifier":identifier,"display_name":title,
                "bedrock_options":{"icon":identifier,"display_handheld":handheld,"creative_category":"equipment"}})
    mi[base]=arr

add_definition("minecraft:netherite_sword","legendaryv34:emberfall_claymore","raisnet:emberfall_claymore","Emberfall Claymore")
add_definition("minecraft:netherite_sword","legendaryv34:noctis_longsword","raisnet:noctis_longsword","Noctis Longsword")
add_definition("minecraft:bow","legendaryv34:stormpiercer_recurve_bow","raisnet:stormpiercer_recurve_bow","Stormpiercer Tempest Bow")
add_definition("minecraft:netherite_shovel","legendaryv34:gaia_war_spear","raisnet:gaia_war_spear","Gaia War Spear")
add_definition("minecraft:shears","legendaryv34:astral_twin_daggers","raisnet:astral_twin_daggers","Astral Twin Daggers")

MATERIALS={
 "phoenix":"golden",
 "voidwalker":"netherite",
 "titan":"diamond",
 "celestial":"iron",
 "water_sovereign":"netherite"
}
CMD_BASE={"phoenix":920100,"voidwalker":920104,"titan":920108,"celestial":920112,"water_sovereign":920116}
PROT={"phoenix":4,"voidwalker":2,"titan":3,"celestial":3,"water_sovereign":3}
SLOT={"helmet":"head","chest":"chest","legs":"legs","boots":"feet"}
SUFFIX={"helmet":"helmet","chest":"chestplate","legs":"leggings","boots":"boots"}

for setname in ARMOR:
    for piece in PIECES:
        base=f"minecraft:{MATERIALS[setname]}_{SUFFIX[piece]}"
        model=f"legendaryv34:armor/{setname}_{piece}"
        ident=f"raisnet:{setname}_{piece}"
        arr=mi.setdefault(base,[])
        arr=[x for x in arr if not (x.get("type")=="definition" and x.get("model")==model)]
        arr.append({
          "type":"definition","model":model,"bedrock_identifier":ident,
          "display_name":f"{setname.replace('_',' ').title()} {piece.title()}",
          "bedrock_options":{"icon":ident,"protection_value":PROT[setname],"creative_category":"equipment"},
          "components":{"minecraft:equippable":{"slot":SLOT[piece]},"minecraft:max_stack_size":1}
        })
        mi[base]=arr

MAP.write_text(json.dumps(mapping,indent=2))

# fresh pack identity
mf=ROOT/"manifest.json"; manifest=json.loads(mf.read_text())
manifest["header"]["name"]="RaisNet LegendaryRais v3.5.4 Visual Integrity"
manifest["header"]["description"]="Modern Geyser mappings + native armor attachables + cleaner weapon geometry; Soul Tide + Leviathan preserved"
manifest["header"]["uuid"]="149d797f-4bc0-4bf8-b2d7-78f1550e1160"
manifest["header"]["version"]=[3,5,4]
manifest["modules"][0]["uuid"]="4dcc8029-ffb8-4aab-901a-7f11f44d1937"
manifest["modules"][0]["version"]=[3,5,4]
mf.write_text(json.dumps(manifest,separators=(",",":")))

# strict validation
for p in ROOT.rglob("*.json"): json.loads(p.read_text())
for setname in ARMOR:
    for piece in PIECES:
        assert (ROOT/f"attachables/armor_{setname}_{piece}.json").is_file()
        assert (ROOT/f"textures/items/armor_{setname}_{piece}.png").is_file()
    assert (ROOT/f"textures/models/armor/{setname}_1.png").is_file()
    assert (ROOT/f"textures/models/armor/{setname}_2.png").is_file()
assert (ROOT/"models/entity/soul_tide_katana.geo.json").is_file()
assert (ROOT/"models/entity/abyss_leviathan_trident.geo.json").is_file()
assert (ROOT/"attachables/soul_tide_katana.player.json").is_file()
assert (ROOT/"attachables/abyss_leviathan_trident.player.json").is_file()

if OUT.exists():OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad:raise RuntimeError(bad)
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+"\n")
print("VALID",OUT.stat().st_size,sha,"ARMOR_ATTACHABLES",len(ARMOR)*len(PIECES))

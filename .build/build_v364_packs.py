from pathlib import Path
import json, shutil, zipfile, hashlib
from PIL import Image, ImageDraw

JBASE=Path("LegendaryRais-Java-26.1.2-v3.6.3-RESOURCE-INTEGRITY.zip")
BBASE=Path("LegendaryRais-Bedrock-v3.6.3-RESOURCE-INTEGRITY.mcpack")
MBASE=Path("LegendaryRais-Geyser-v3.6.3-mappings.json")
JOUT=Path("LegendaryRais-Java-26.1.2-v3.6.4-BEDROCK-RIG-VISOR.zip")
BOUT=Path("LegendaryRais-Bedrock-v3.6.4-BEDROCK-RIG-VISOR.mcpack")
MOUT=Path("LegendaryRais-Geyser-v3.6.4-mappings.json")
JSHA=Path("LegendaryRais-Java-26.1.2-v3.6.4-BEDROCK-RIG-VISOR.sha1")
BSHA=Path("LegendaryRais-Bedrock-v3.6.4-BEDROCK-RIG-VISOR.sha1")
ROOT=Path(".build/generated-v364");JR=ROOT/"java";BR=ROOT/"bedrock";NS="legendaryv34"

shutil.rmtree(ROOT,ignore_errors=True);JR.mkdir(parents=True);BR.mkdir(parents=True)
with zipfile.ZipFile(JBASE) as z:z.extractall(JR)
with zipfile.ZipFile(BBASE) as z:z.extractall(BR)

SETS=("phoenix","voidwalker","titan","celestial","water_sovereign")
PIECES=("helmet","chest","legs","boots")
PROTECTION={"phoenix":4,"voidwalker":2,"titan":3,"celestial":3,"water_sovereign":3}
BASE_ITEM={
 "phoenix":{"helmet":"minecraft:golden_helmet","chest":"minecraft:golden_chestplate","legs":"minecraft:golden_leggings","boots":"minecraft:golden_boots"},
 "voidwalker":{"helmet":"minecraft:netherite_helmet","chest":"minecraft:netherite_chestplate","legs":"minecraft:netherite_leggings","boots":"minecraft:netherite_boots"},
 "titan":{"helmet":"minecraft:diamond_helmet","chest":"minecraft:diamond_chestplate","legs":"minecraft:diamond_leggings","boots":"minecraft:diamond_boots"},
 "celestial":{"helmet":"minecraft:iron_helmet","chest":"minecraft:iron_chestplate","legs":"minecraft:iron_leggings","boots":"minecraft:iron_boots"},
 "water_sovereign":{"helmet":"minecraft:netherite_helmet","chest":"minecraft:netherite_chestplate","legs":"minecraft:netherite_leggings","boots":"minecraft:netherite_boots"}
}

def wr(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,separators=(",",":")),encoding="utf-8")

# ------------------------------------------------------------------
# Java helmet visor modes
# ------------------------------------------------------------------
for s in SETS:
    icon_model=f"{NS}:item/armor/{s}_helmet"
    wr(JR/f"assets/{NS}/items/armor/{s}_helmet_closed.json",{"model":{"type":"minecraft:model","model":icon_model}})
    wr(JR/f"assets/{NS}/items/armor/{s}_helmet_open.json",{"model":{"type":"minecraft:model","model":icon_model}})

    # closed equipment = current stable full-set texture
    wr(JR/f"assets/{NS}/equipment/{s}_helmet_closed.json",{
        "layers":{"humanoid":[{"texture":f"{NS}:{s}_set"}]}
    })

    # open visor texture: same art, only front helmet face polygon becomes transparent.
    src=JR/f"assets/{NS}/textures/entity/equipment/humanoid/{s}_set.png"
    im=Image.open(src).convert("RGBA")
    # Vanilla armor helmet front face region is 8..15 x 8..15.
    for y in range(8,16):
        for x in range(8,16):
            r,g,b,a=im.getpixel((x,y))
            im.putpixel((x,y),(r,g,b,0))
    # preserve forehead trim on first two rows for an open-visored look
    for y in range(8,10):
        for x in range(8,16):
            r,g,b,a=Image.open(src).convert("RGBA").getpixel((x,y))
            im.putpixel((x,y),(r,g,b,a))
    dst=JR/f"assets/{NS}/textures/entity/equipment/humanoid/{s}_helmet_open.png"
    im.save(dst,optimize=True)
    wr(JR/f"assets/{NS}/equipment/{s}_helmet_open.json",{
        "layers":{"humanoid":[{"texture":f"{NS}:{s}_helmet_open"}]}
    })

    # legacy helmet item_model remains closed-compatible
    wr(JR/f"assets/{NS}/items/armor/{s}_helmet.json",{"model":{"type":"minecraft:model","model":icon_model}})

# ------------------------------------------------------------------
# Bedrock armor geometry rebuilt to official bound-bone pattern
# ------------------------------------------------------------------
def cube(origin,size,uv=(0,0),inflate=None,mirror=None):
    c={"origin":list(origin),"size":list(size),"uv":list(uv)}
    if inflate is not None:c["inflate"]=inflate
    if mirror is not None:c["mirror"]=mirror
    return c

def helmet_geo(s,open_mode=False):
    gid=f"geometry.raisnet.armor.{s}.helmet.{'open' if open_mode else 'closed'}.v364"
    if open_mode:
        shell=[
          cube((-4,30,-4),(8,2,8),(0,0),.72),
          cube((-4,24,-4),(2,6,8),(0,10),.72),
          cube((2,24,-4),(2,6,8),(20,10),.72),
          cube((-2.8,24,2.1),(5.6,6,1.9),(40,10),.72),
          cube((-1,32,-1),(2,3,2),(54,0),.15)
        ]
    else:
        shell=[
          cube((-4,24,-4),(8,8,8),(0,0),.72),
          cube((-1,32,-1),(2,3,2),(40,0),.15)
        ]
    # set-specific silhouette accents remain low-cube.
    if s=="phoenix": shell += [cube((-5.2,29,-1),(1.4,3,3),(48,0),.08),cube((3.8,29,-1),(1.4,3,3),(54,0),.08)]
    elif s=="voidwalker": shell += [cube((-4.8,30,-.6),(1.1,4,1.2),(48,0),.05),cube((3.7,30,-.6),(1.1,4,1.2),(52,0),.05)]
    elif s=="titan": shell += [cube((-4.7,27,-3.1),(1.4,3,6.2),(48,0),.08),cube((3.3,27,-3.1),(1.4,3,6.2),(54,0),.08)]
    elif s=="celestial": shell += [cube((-.5,34,-.5),(1,2,1),(48,0),.04)]
    else: shell += [cube((-5,28,-1),(1.3,3,3),(48,0),.05),cube((3.7,28,-1),(1.3,3,3),(54,0),.05)]
    return gid,{"format_version":"1.16.0","minecraft:geometry":[{
      "description":{"identifier":gid,"texture_width":64,"texture_height":32,"visible_bounds_width":3,"visible_bounds_height":4,"visible_bounds_offset":[0,1,0]},
      "bones":[
        {"name":"head","pivot":[0,24,0]},
        {"name":"helmet_plate","parent":"head","pivot":[0,24,0],"binding":"'head'","cubes":shell}
      ]
    }]}

def chest_geo(s):
    gid=f"geometry.raisnet.armor.{s}.chest.v364"
    body=[cube((-4,2,-2),(8,12,4),(0,0),1.01),cube((-2.4,5,-3.1),(4.8,5,1.1),(32,8),.08)]
    rarm=[cube((-8,2,-2),(4,12,4),(0,16),1.0),cube((-9.1,9,-2.5),(5.0,3.2,5),(40,16),.08)]
    larm=[cube((4,2,-2),(4,12,4),(0,16),1.0,True),cube((4.1,9,-2.5),(5.0,3.2,5),(40,16),.08,True)]
    if s=="phoenix": body.append(cube((-.7,9,-3.7),(1.4,3.2,.8),(56,16),.04))
    elif s=="voidwalker": body.append(cube((-2,7,-3.7),(4,1,.8),(52,16),.04))
    elif s=="titan": body += [cube((-4.6,4,-2.6),(1.2,7,5.2),(52,16),.05),cube((3.4,4,-2.6),(1.2,7,5.2),(57,16),.05)]
    elif s=="celestial": body.append(cube((-.7,10,-3.6),(1.4,1.4,.7),(56,16),.04))
    else: body.append(cube((-2.8,4,-3.5),(5.6,1,.7),(52,16),.04))
    return gid,{"format_version":"1.16.0","minecraft:geometry":[{
      "description":{"identifier":gid,"texture_width":64,"texture_height":32,"visible_bounds_width":3,"visible_bounds_height":3,"visible_bounds_offset":[0,.8,0]},
      "bones":[
        {"name":"body","pivot":[0,14,0]},
        {"name":"chestplate","parent":"body","pivot":[0,0,0],"binding":"'body'","cubes":body},
        {"name":"arm_right","pivot":[-5,12,0]},
        {"name":"arm_plate_right","parent":"arm_right","pivot":[-5,12,0],"binding":"'rightarm'","cubes":rarm},
        {"name":"arm_left","pivot":[5,12,0]},
        {"name":"arm_plate_left","parent":"arm_left","pivot":[5,12,0],"binding":"'leftarm'","cubes":larm}
      ]
    }]}

def legs_geo(s):
    gid=f"geometry.raisnet.armor.{s}.legs.v364"
    waist=[cube((-4,8,-2),(8,4,4),(16,16),.62)]
    r=[cube((-4,0,-2),(4,12,4),(0,16),.55),cube((-3.5,4,-2.75),(3,3,1),(48,16),.04)]
    l=[cube((0,0,-2),(4,12,4),(0,16),.55,True),cube((.5,4,-2.75),(3,3,1),(48,16),.04,True)]
    return gid,{"format_version":"1.16.0","minecraft:geometry":[{
      "description":{"identifier":gid,"texture_width":64,"texture_height":32,"visible_bounds_width":3,"visible_bounds_height":3,"visible_bounds_offset":[0,.5,0]},
      "bones":[
        {"name":"body","pivot":[0,12,0]},
        {"name":"waist_plate","parent":"body","pivot":[0,12,0],"binding":"'body'","cubes":waist},
        {"name":"rightleg","pivot":[-1.9,12,0]},
        {"name":"right_leg_plate","parent":"rightleg","pivot":[-1.9,12,0],"binding":"'rightleg'","cubes":r},
        {"name":"leftleg","pivot":[1.9,12,0]},
        {"name":"left_leg_plate","parent":"leftleg","pivot":[1.9,12,0],"binding":"'leftleg'","cubes":l}
      ]
    }]}

def boots_geo(s):
    gid=f"geometry.raisnet.armor.{s}.boots.v364"
    r=[cube((-4,0,-2),(4,6,4),(0,16),.85),cube((-3.7,0,-3),(3.4,2,1.2),(48,24),.04)]
    l=[cube((0,0,-2),(4,6,4),(0,16),.85,True),cube((.3,0,-3),(3.4,2,1.2),(48,24),.04,True)]
    return gid,{"format_version":"1.16.0","minecraft:geometry":[{
      "description":{"identifier":gid,"texture_width":64,"texture_height":32,"visible_bounds_width":3,"visible_bounds_height":2.5,"visible_bounds_offset":[0,.35,0]},
      "bones":[
        {"name":"rightleg","pivot":[-1.9,12,0]},
        {"name":"right_boot","parent":"rightleg","pivot":[-1.9,12,0],"binding":"'rightleg'","cubes":r},
        {"name":"leftleg","pivot":[1.9,12,0]},
        {"name":"left_boot","parent":"leftleg","pivot":[1.9,12,0],"binding":"'leftleg'","cubes":l}
      ]
    }]}

def attachable(identifier,gid,texture,parent_setup):
    return {
      "format_version":"1.20.60",
      "minecraft:attachable":{"description":{
        "identifier":identifier,
        "render_controllers":["controller.render.armor"],
        "materials":{"default":"entity_alphatest","enchanted":"entity_alphatest_glint"},
        "textures":{"default":texture,"enchanted":"textures/misc/enchanted_actor_glint"},
        "geometry":{"default":gid},
        "scripts":{"parent_setup":parent_setup}
      }}
    }

for s in SETS:
    # helmet closed/open plus legacy closed identifier
    for mode in ("closed","open"):
        gid,g=helmet_geo(s,mode=="open")
        wr(BR/f"models/entity/armor_{s}_helmet_{mode}_v364.geo.json",g)
        ident=f"raisnet:{s}_helmet_{mode}"
        wr(BR/f"attachables/armor_{s}_helmet_{mode}.json",attachable(ident,gid,f"textures/models/armor/{s}_1","v.helmet_layer_visible = false;"))
    gid,g=helmet_geo(s,False)
    wr(BR/f"models/entity/armor_{s}_helmet_v364.geo.json",g)
    wr(BR/f"attachables/armor_{s}_helmet.json",attachable(f"raisnet:{s}_helmet",gid,f"textures/models/armor/{s}_1","v.helmet_layer_visible = false;"))

    # chest/legs/boots rebuild
    gid,g=chest_geo(s);wr(BR/f"models/entity/armor_{s}_chest_v364.geo.json",g)
    wr(BR/f"attachables/armor_{s}_chest.json",attachable(f"raisnet:{s}_chest",gid,f"textures/models/armor/{s}_1","v.chest_layer_visible = false;"))
    gid,g=legs_geo(s);wr(BR/f"models/entity/armor_{s}_legs_v364.geo.json",g)
    wr(BR/f"attachables/armor_{s}_legs.json",attachable(f"raisnet:{s}_legs",gid,f"textures/models/armor/{s}_2","v.leg_layer_visible = false;"))
    gid,g=boots_geo(s);wr(BR/f"models/entity/armor_{s}_boots_v364.geo.json",g)
    wr(BR/f"attachables/armor_{s}_boots.json",attachable(f"raisnet:{s}_boots",gid,f"textures/models/armor/{s}_1","v.boot_layer_visible = false;"))

# Atlas aliases for visor identifiers, reusing helmet inventory icon.
atlas_path=BR/"textures/item_texture.json";atlas=json.loads(atlas_path.read_text())
td=atlas.setdefault("texture_data",{})
for s in SETS:
    base=td.get(f"raisnet:{s}_helmet",{"textures":f"textures/items/armor_{s}_helmet"})
    td[f"raisnet:{s}_helmet_closed"]=base
    td[f"raisnet:{s}_helmet_open"]=base
atlas_path.write_text(json.dumps(atlas,separators=(",",":")),encoding="utf-8")

# ------------------------------------------------------------------
# Geyser mappings: add explicit OPEN/CLOSED definitions.
# ------------------------------------------------------------------
mapping=json.loads(MBASE.read_text())
for s in SETS:
    base=BASE_ITEM[s]["helmet"]
    arr=mapping["items"].setdefault(base,[])
    arr[:]=[d for d in arr if d.get("model") not in (
        f"{NS}:armor/{s}_helmet_closed",f"{NS}:armor/{s}_helmet_open"
    )]
    common_components={"minecraft:equippable":{"slot":"head"},"minecraft:max_stack_size":1}
    arr.append({
      "type":"definition","model":f"{NS}:armor/{s}_helmet_closed",
      "bedrock_identifier":f"raisnet:{s}_helmet_closed",
      "display_name":f"{s.replace('_',' ').title()} Helmet Closed",
      "bedrock_options":{"icon":f"raisnet:{s}_helmet_closed","protection_value":PROTECTION[s],"creative_category":"equipment"},
      "components":common_components
    })
    arr.append({
      "type":"definition","model":f"{NS}:armor/{s}_helmet_open",
      "bedrock_identifier":f"raisnet:{s}_helmet_open",
      "display_name":f"{s.replace('_',' ').title()} Helmet Open",
      "bedrock_options":{"icon":f"raisnet:{s}_helmet_open","protection_value":PROTECTION[s],"creative_category":"equipment"},
      "components":common_components
    })

# Enforce current weapon Bedrock handheld definitions + Storm vanilla behavior.
for base,arr in mapping["items"].items():
    for d in arr:
        model=d.get("model","")
        if model in (
          f"{NS}:emberfall_claymore",f"{NS}:noctis_longsword",f"{NS}:stormpiercer_recurve_bow",
          f"{NS}:gaia_war_spear",f"{NS}:astral_frost_greataxe"
        ):
            d.setdefault("bedrock_options",{})["display_handheld"]=True
        if model==f"{NS}:stormpiercer_recurve_bow":
            d.pop("components",None)

MOUT.write_text(json.dumps(mapping,indent=2),encoding="utf-8")

# ------------------------------------------------------------------
# Fresh pack identity
# ------------------------------------------------------------------
jm=JR/"pack.mcmeta";meta=json.loads(jm.read_text())
meta["pack"]["description"]="LegendaryRais v3.6.4 BEDROCK RIG & VISOR | open/closed helmets | stable armor bindings"
jm.write_text(json.dumps(meta,separators=(",",":")),encoding="utf-8")

mf=BR/"manifest.json";bm=json.loads(mf.read_text())
bm["header"]["name"]="RaisNet LegendaryRais v3.6.4 Bedrock Rig & Visor"
bm["header"]["description"]="Rebuilt bound-bone armor rigs + open/closed visor modes + validated custom items"
bm["header"]["uuid"]="0c85bc3d-d5b3-43ea-8fb4-c9db4b5613a8"
bm["header"]["version"]=[3,6,4]
bm["modules"][0]["uuid"]="e46253ed-f2b0-46ae-99db-834867b739e3"
bm["modules"][0]["version"]=[3,6,4]
mf.write_text(json.dumps(bm,separators=(",",":")),encoding="utf-8")

# ------------------------------------------------------------------
# Deep validation: Java + Bedrock + Geyser
# ------------------------------------------------------------------
for root in (JR,BR):
    for p in root.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
    for p in root.rglob("*.png"):
        with Image.open(p) as im:im.verify()

# Java visor definitions / equipment references.
for s in SETS:
    for mode in ("closed","open"):
        ip=JR/f"assets/{NS}/items/armor/{s}_helmet_{mode}.json"
        ep=JR/f"assets/{NS}/equipment/{s}_helmet_{mode}.json"
        assert ip.is_file() and ep.is_file(),(s,mode)
        item=json.loads(ip.read_text());assert item["model"]["model"]==f"{NS}:item/armor/{s}_helmet"
        eq=json.loads(ep.read_text())
        for layer in eq["layers"].get("humanoid",[]):
            ref=layer["texture"];nsp,path=ref.split(":",1)
            assert (JR/f"assets/{nsp}/textures/entity/equipment/humanoid/{path}.png").is_file(),ref

# Bedrock armor attachable identifiers/geometry/textures.
for s in SETS:
    for name,ident in [
        (f"armor_{s}_helmet",f"raisnet:{s}_helmet"),
        (f"armor_{s}_helmet_closed",f"raisnet:{s}_helmet_closed"),
        (f"armor_{s}_helmet_open",f"raisnet:{s}_helmet_open"),
        (f"armor_{s}_chest",f"raisnet:{s}_chest"),
        (f"armor_{s}_legs",f"raisnet:{s}_legs"),
        (f"armor_{s}_boots",f"raisnet:{s}_boots")
    ]:
        ap=BR/f"attachables/{name}.json";assert ap.is_file(),ap
        a=json.loads(ap.read_text())["minecraft:attachable"]["description"]
        assert a["identifier"]==ident,(name,a["identifier"],ident)
        assert a["render_controllers"]==["controller.render.armor"]
        gid=a["geometry"]["default"]
        geos=list(BR.glob(f"models/entity/{name}*_v364.geo.json"))
        assert geos,(name,gid)
        assert any(json.loads(g.read_text())["minecraft:geometry"][0]["description"]["identifier"]==gid for g in geos),(name,gid)
        tex=a["textures"]["default"]
        assert (BR/f"{tex}.png").is_file(),(name,tex)

# New mappings must exactly resolve to attachables + atlas.
for s in SETS:
    arr=mapping["items"][BASE_ITEM[s]["helmet"]]
    for mode in ("closed","open"):
        model=f"{NS}:armor/{s}_helmet_{mode}"
        found=[d for d in arr if d.get("type")=="definition" and d.get("model")==model]
        assert len(found)==1,(s,mode,len(found))
        d=found[0]
        ident=d["bedrock_identifier"]
        assert ident==f"raisnet:{s}_helmet_{mode}"
        assert d.get("components",{}).get("minecraft:equippable",{}).get("slot")=="head"
        assert ident in td,(ident,"atlas")
        ap=BR/f"attachables/armor_{s}_helmet_{mode}.json"
        a=json.loads(ap.read_text())["minecraft:attachable"]["description"]
        assert a["identifier"]==ident

# Weapon mappings and attachables.
weapon_pairs={
 f"{NS}:emberfall_claymore":"raisnet:emberfall_claymore",
 f"{NS}:noctis_longsword":"raisnet:noctis_longsword",
 f"{NS}:stormpiercer_recurve_bow":"raisnet:stormpiercer_recurve_bow",
 f"{NS}:gaia_war_spear":"raisnet:gaia_war_spear",
 f"{NS}:astral_frost_greataxe":"raisnet:astral_frost_greataxe"
}
for model,ident in weapon_pairs.items():
    defs=[d for arr in mapping["items"].values() for d in arr if d.get("type")=="definition" and d.get("model")==model]
    assert len(defs)==1,(model,len(defs))
    d=defs[0];assert d["bedrock_identifier"]==ident
    assert d["bedrock_options"]["display_handheld"] is True
    if model.endswith("stormpiercer_recurve_bow"):assert "components" not in d
    key=ident.split(":",1)[1]
    ap=BR/f"attachables/{key}.player.json";assert ap.is_file(),ap
    a=json.loads(ap.read_text())["minecraft:attachable"]["description"]
    assert a["identifier"]==ident,(ident,a["identifier"])

# cube budgets keep weak phones viable.
for s in SETS:
    for piece,limit in (("helmet_closed",8),("helmet_open",10),("helmet",8),("chest",12),("legs",8),("boots",6)):
        gp=next(iter(BR.glob(f"models/entity/armor_{s}_{piece}*_v364.geo.json")))
        g=json.loads(gp.read_text())["minecraft:geometry"][0]
        n=sum(len(b.get("cubes",[])) for b in g["bones"])
        assert n<=limit,(s,piece,n,limit)

# Locked water assets stay present.
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
print("V364 BEDROCK_RIG_VISOR PASS")

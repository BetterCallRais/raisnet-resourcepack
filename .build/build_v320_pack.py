from pathlib import Path
import zipfile,shutil,json,hashlib
from PIL import Image,ImageDraw

BASE=Path("LegendaryRais-Java-26.1.2-v3.1.0-REALISTIC-ARSENAL.zip")
ROOT=Path(".build/v320-pack")
OUT=Path("LegendaryRais-Java-26.1.2-v3.2.0-HEALTH-ARMOR.zip")
SHA=Path("LegendaryRais-Java-26.1.2-v3.2.0-HEALTH-ARMOR.sha1")
if ROOT.exists():shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z:
    assert z.testzip() is None
    z.extractall(ROOT)

src=ROOT/"assets/legendaryrais"
dst=ROOT/"assets/legendaryv32"
if dst.exists():shutil.rmtree(dst)
shutil.copytree(src,dst)
for p in dst.rglob("*.json"):
    t=p.read_text(encoding="utf-8").replace("legendaryrais:","legendaryv32:")
    p.write_text(t,encoding="utf-8")

sets={
"phoenix":((92,35,18),(214,82,26),(238,161,58)),
"voidwalker":((24,20,34),(69,43,91),(140,73,166)),
"titan":((41,55,46),(93,108,88),(159,137,72)),
"celestial":((54,77,98),(131,163,186),(82,180,217)),
"water_sovereign":((10,42,69),(20,119,159),(68,207,224))}
for name,(dark,mid,accent) in sets.items():
    for sub in ("humanoid","humanoid_leggings"):
        p=dst/f"textures/entity/equipment/{sub}/{name}.png"
        W,H=1024,512
        im=Image.new("RGBA",(W,H));d=ImageDraw.Draw(im)
        for y in range(H):
            q=y/(H-1);c=tuple(int(dark[i]*(1-q)+mid[i]*q) for i in range(3))+(255,)
            d.line((0,y,W,y),fill=c)
        seam=tuple(max(0,int(x*.42)) for x in dark)+(255,)
        for x in range(0,W,128):d.rectangle((x,0,x+6,H),fill=seam)
        for y in range(0,H,96):d.rectangle((0,y,W,y+5),fill=seam)
        for x in range(-120,W+120,180):d.polygon([(x,40),(x+65,12),(x+125,40),(x+65,68)],outline=accent+(255,),width=5)
        for x in range(64,W,128):
            for y in range(48,H,96):d.ellipse((x-7,y-7,x+7,y+7),fill=accent+(255,),outline=seam,width=2)
        scratch=tuple(min(220,int(x*1.25)) for x in mid)+(150,)
        for i in range(42):
            x=(i*83+31)%W;y=(i*57+17)%H
            d.line((x,y,min(W-1,x+45),min(H-1,y+9)),fill=scratch,width=2)
        p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True,compress_level=6)

mc=ROOT/"pack.mcmeta";o=json.loads(mc.read_text())
o["pack"]["description"]="LegendaryRais v3.2 HEALTH ARMOR • locked Water Relics • cache-safe realistic arsenal"
mc.write_text(json.dumps(o,separators=(",",":")),encoding="utf-8")

for p in ROOT.rglob("*.json"):json.loads(p.read_text(encoding="utf-8"))
for p in dst.rglob("models/**/*.json"):
    o=json.loads(p.read_text())
    for v in o.get("textures",{}).values():
        if not isinstance(v,str) or v.startswith("#"):continue
        ns,path=v.split(":",1) if ":" in v else ("minecraft",v)
        if ns=="legendaryv32":assert (ROOT/f"assets/{ns}/textures/{path}.png").exists(),(p,v)

water=["assets/soultide/models/item/soul_tide_sovereign_blade.json","assets/legendaryrais/models/item/abyss_leviathan_trident.json","assets/legendaryrais/models/item/fx_leviathan_projectile.json"]
with zipfile.ZipFile(BASE) as z:
    for rel in water:assert hashlib.sha256((ROOT/rel).read_bytes()).digest()==hashlib.sha256(z.read(rel)).digest(),rel

if OUT.exists():OUT.unlink()
with zipfile.ZipFile(OUT,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z:assert z.testzip() is None
h=hashlib.sha1(OUT.read_bytes()).hexdigest();SHA.write_text(h+"\n")
print("PACK_OK",OUT.stat().st_size,h)

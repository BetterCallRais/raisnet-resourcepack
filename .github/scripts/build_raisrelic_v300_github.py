from pathlib import Path
import json, shutil, zipfile, hashlib
from PIL import Image, ImageDraw

OUT=Path('.')
BASE=Path('/tmp/rp23inspect')
JAVA=Path('/tmp/rr300_java_pack')
if JAVA.exists(): shutil.rmtree(JAVA)
JAVA.mkdir(parents=True)
shutil.copytree(BASE, JAVA, dirs_exist_ok=True)

# Remove v2.x legendary assets, but preserve social assets (Discord/WhatsApp).
for rel in ['assets/raisnet/models/legend','assets/raisnet/models/legendary','assets/raisnet/textures/item/legend','assets/raisnet/textures/item/legendary']:
    p=JAVA/rel
    if p.exists(): shutil.rmtree(p)
for old in ['raijin_no_kiba','kurotsuki_requiem','enka_ryujin','hoshikiri','shirogane_setsuna','tenma_guren','aetherion_arc']:
    f=JAVA/'assets/raisnet/items'/f'{old}.json'
    if f.exists(): f.unlink()

weapons = {
 'ame_no_zanketsu': {'name':'Ame no Zanketsu','colors':[(205,230,240),(20,28,40),(50,160,220),(150,235,255),(40,45,55)]},
 'kurohana_calamity': {'name':'Kurohana Calamity','colors':[(80,75,82),(24,18,24),(170,25,45),(255,70,80),(45,35,40)]},
 'seiryuu_lance': {'name':'Seiryuu Lance','colors':[(175,220,225),(14,45,60),(25,135,165),(80,235,235),(35,70,80)]},
 'tsukikage_reaper': {'name':'Tsukikage Reaper','colors':[(165,155,185),(24,18,35),(100,45,155),(205,120,255),(45,30,60)]},
 'guren_fang': {'name':'Guren Fang','colors':[(190,180,165),(50,20,18),(200,55,25),(255,150,35),(70,30,25)]},
 'tenma_crusher': {'name':'Tenma Crusher','colors':[(100,92,95),(30,22,22),(145,20,25),(255,75,35),(60,38,35)]},
 'astra_veloce': {'name':'Astra Veloce','colors':[(230,225,190),(32,45,65),(220,170,40),(105,215,255),(75,80,90)]},
}
texkeys=['metal','dark','accent','glow','grip']

def make_swatch(path, rgb):
    img=Image.new('RGBA',(16,16),(*rgb,255)); d=ImageDraw.Draw(img)
    hi=tuple(min(255,c+35) for c in rgb); lo=tuple(max(0,c-30) for c in rgb)
    for i in range(0,16,4): d.line((0,i,15,i), fill=(*lo,255))
    d.line((0,0,15,15), fill=(*hi,255), width=1)
    d.line((0,1,14,15), fill=(*tuple(min(255,c+15) for c in rgb),255), width=1)
    path.parent.mkdir(parents=True, exist_ok=True); img.save(path)

def faces(tex): return {f:{'texture':'#'+tex} for f in ['north','south','east','west','up','down']}
def cube(frm,to,tex='metal',rot=None):
    e={'from':[round(x,3) for x in frm],'to':[round(x,3) for x in to],'faces':faces(tex)}
    if rot:
        axis,angle,origin=rot
        e['rotation']={'origin':list(origin),'axis':axis,'angle':angle,'rescale':True}
    return e

def disp(scale=1.0, gui=1.0, first_rot=(0,-90,25), third_rot=(0,-90,55), trans=(0,4,1)):
    return {
      'thirdperson_righthand':{'rotation':list(third_rot),'translation':list(trans),'scale':[scale]*3},
      'thirdperson_lefthand':{'rotation':[third_rot[0],-third_rot[1],-third_rot[2]],'translation':list(trans),'scale':[scale]*3},
      'firstperson_righthand':{'rotation':list(first_rot),'translation':[1.2,4.2,1.3],'scale':[scale*1.05]*3},
      'firstperson_lefthand':{'rotation':[first_rot[0],-first_rot[1],-first_rot[2]],'translation':[1.2,4.2,1.3],'scale':[scale*1.05]*3},
      'gui':{'rotation':[25,-40,25],'translation':[0,0,0],'scale':[gui]*3},
      'ground':{'rotation':[0,0,0],'translation':[0,2,0],'scale':[0.65]*3},
      'fixed':{'rotation':[0,180,0],'translation':[0,0,0],'scale':[0.9]*3},
    }

def build_elements(wid):
    E=[]
    if wid=='ame_no_zanketsu':
        E += [cube((7.25,0,7.25),(8.75,4.1,8.75),'grip'),cube((6.8,0,6.8),(9.2,.7,9.2),'accent'),cube((4.9,4.0,7.0),(11.1,5.0,9.0),'dark'),cube((6.0,4.15,7.1),(10.0,4.85,8.9),'accent'),cube((7.25,4.8,7.45),(8.7,15.0,8.55),'metal'),cube((8.45,5.0,7.35),(9.0,14.6,8.65),'glow'),cube((7.45,14.5,7.45),(8.55,16.0,8.55),'metal',('z',-22.5,(8,14.5,8))),cube((5.5,2.1,7.2),(6.2,3.7,8.8),'accent',('z',22.5,(6,3,8)))]
    elif wid=='kurohana_calamity':
        E += [cube((7.0,0,7.0),(9.0,4.0,9.0),'grip'),cube((6.3,0,6.3),(9.7,.8,9.7),'accent'),cube((3.8,3.8,6.7),(12.2,5.2,9.3),'dark'),cube((5.2,4.8,6.6),(10.8,13.9,9.4),'metal'),cube((7.35,5.2,6.45),(8.65,14.4,9.55),'accent'),cube((5.0,12.8,6.8),(7.1,15.1,9.2),'metal',('z',22.5,(7,13,8))),cube((8.9,12.8,6.8),(11.0,15.1,9.2),'metal',('z',-22.5,(9,13,8))),cube((4.4,6.3,7.0),(5.3,10.2,9.0),'dark'),cube((10.7,6.3,7.0),(11.6,10.2,9.0),'dark'),cube((7.3,13.8,7.1),(8.7,16.0,8.9),'glow')]
    elif wid=='seiryuu_lance':
        E += [cube((7.45,-2,7.45),(8.55,11.8,8.55),'grip'),cube((7.05,1.0,7.05),(8.95,5.0,8.95),'dark'),cube((6.3,10.2,6.8),(9.7,11.5,9.2),'accent'),cube((7.1,11.0,7.0),(8.9,15.5,9.0),'metal'),cube((6.0,11.3,7.2),(7.35,14.2,8.8),'metal',('z',22.5,(7.2,12,8))),cube((8.65,11.3,7.2),(10.0,14.2,8.8),'metal',('z',-22.5,(8.8,12,8))),cube((7.45,14.4,7.2),(8.55,17.0,8.8),'glow'),cube((5.7,9.6,7.25),(6.7,11.1,8.75),'accent',('z',45,(6.5,10.5,8))),cube((9.3,9.6,7.25),(10.3,11.1,8.75),'accent',('z',-45,(9.5,10.5,8)))]
    elif wid=='tsukikage_reaper':
        E += [cube((7.35,-1,7.35),(8.65,13.5,8.65),'grip'),cube((6.9,3.0,6.9),(9.1,5.0,9.1),'dark'),cube((7.0,12.5,6.8),(9.0,14.2,9.2),'accent'),cube((8.2,13.0,7.1),(12.5,14.2,8.9),'metal',('z',-22.5,(8.4,13.4,8))),cube((10.8,13.0,7.15),(15.2,14.1,8.85),'metal',('z',-45,(11.0,13.5,8))),cube((12.7,11.8,7.2),(16.2,13.0,8.8),'glow',('z',-45,(13.0,12.5,8))),cube((5.3,12.7,7.2),(7.2,13.8,8.8),'metal',('z',22.5,(7.0,13.3,8))),cube((7.55,13.5,7.2),(8.45,15.7,8.8),'glow')]
    elif wid=='guren_fang':
        E += [cube((7.2,0,7.2),(8.8,4.0,8.8),'grip'),cube((5.6,3.8,7.0),(10.4,4.8,9.0),'dark'),cube((5.1,4.4,7.35),(6.5,14.4,8.65),'metal',('z',22.5,(6.0,5.0,8))),cube((9.5,4.4,7.35),(10.9,14.4,8.65),'metal',('z',-22.5,(10.0,5.0,8))),cube((5.85,5.0,7.2),(6.4,13.7,8.8),'glow',('z',22.5,(6.0,5.0,8))),cube((9.6,5.0,7.2),(10.15,13.7,8.8),'accent',('z',-22.5,(10.0,5.0,8))),cube((4.8,13.2,7.3),(6.2,15.0,8.7),'accent',('z',22.5,(5.8,13.5,8))),cube((9.8,13.2,7.3),(11.2,15.0,8.7),'glow',('z',-22.5,(10.2,13.5,8)))]
    elif wid=='tenma_crusher':
        E += [cube((7.0,-1,7.0),(9.0,10.3,9.0),'grip'),cube((6.5,1.2,6.5),(9.5,3.0,9.5),'dark'),cube((3.0,9.2,5.3),(13.0,14.2,10.7),'metal'),cube((4.0,10.0,4.6),(12.0,13.4,5.5),'dark'),cube((6.5,10.0,4.2),(9.5,13.5,11.8),'accent'),cube((7.1,10.5,3.8),(8.9,13.0,12.2),'glow'),cube((1.5,10.1,6.5),(4.0,12.8,9.5),'metal',('z',22.5,(3.5,11.5,8))),cube((12.0,10.1,6.5),(14.5,12.8,9.5),'metal',('z',-22.5,(12.5,11.5,8))),cube((4.2,13.3,6.8),(6.0,15.7,9.2),'dark',('z',-22.5,(5,13.5,8))),cube((10.0,13.3,6.8),(11.8,15.7,9.2),'dark',('z',22.5,(11,13.5,8)))]
    elif wid=='astra_veloce':
        E += [cube((7.25,5.2,7.25),(8.75,10.8,8.75),'grip'),cube((6.2,7.0,6.8),(9.8,9.0,9.2),'accent'),cube((4.9,0.5,7.25),(6.2,6.6,8.75),'metal',('z',-22.5,(6,6,8))),cube((3.3,-1.0,7.3),(4.7,4.5,8.7),'metal',('z',-45,(4.5,4,8))),cube((9.8,9.4,7.25),(11.1,15.5,8.75),'metal',('z',-22.5,(10,10,8))),cube((11.3,12.0,7.3),(12.7,17.0,8.7),'metal',('z',-45,(11.5,12,8))),cube((5.8,4.7,7.5),(6.3,11.3,8.5),'glow',('z',22.5,(6,8,8))),cube((9.7,4.7,7.5),(10.2,11.3,8.5),'glow',('z',-22.5,(10,8,8))),cube((7.2,7.1,6.8),(8.8,8.9,9.2),'glow')]
    return E

packmeta={'pack':{'description':'RaisNet • RaisRelic v3.0 Legendary Reforge • TRUE 3D • Java 26.2 + Social','min_format':[88,0],'max_format':[88,0]}}
(JAVA/'pack.mcmeta').write_text(json.dumps(packmeta,indent=2))
for wid,info in weapons.items():
    for key,rgb in zip(texkeys,info['colors']): make_swatch(JAVA/f'assets/raisnet/textures/item/legendary/{wid}_{key}.png',rgb)
    textures={k:f'raisnet:item/legendary/{wid}_{k}' for k in texkeys}
    model={'textures':textures,'elements':build_elements(wid),'display':disp(1.15 if wid not in ['seiryuu_lance','tsukikage_reaper','tenma_crusher'] else 0.95,1.05)}
    mp=JAVA/f'assets/raisnet/models/legendary/{wid}.json'; mp.parent.mkdir(parents=True,exist_ok=True); mp.write_text(json.dumps(model,indent=2))
    ip=JAVA/f'assets/raisnet/items/{wid}.json'; ip.parent.mkdir(parents=True,exist_ok=True); ip.write_text(json.dumps({'model':{'type':'minecraft:model','model':f'raisnet:legendary/{wid}'}},indent=2))

icon=Image.new('RGBA',(128,128),(10,15,25,255)); d=ImageDraw.Draw(icon)
for r in range(55,5,-5): d.ellipse((64-r,64-r,64+r,64+r),outline=(min(255,50+r*2),140,230,180),width=2)
d.polygon([(64,10),(80,55),(118,64),(80,73),(64,118),(48,73),(10,64),(48,55)],fill=(70,180,240,240),outline=(230,245,255,255))
d.polygon([(64,24),(72,58),(103,64),(72,70),(64,104),(56,70),(25,64),(56,58)],fill=(22,30,45,255))
icon.save(JAVA/'pack.png')
for f in JAVA.rglob('*.json'): json.loads(f.read_text())
json.loads((JAVA/'pack.mcmeta').read_text())
java_zip=OUT/'RaisNet-RaisRelic-LegendaryWeapons-Java-26.2-v3.0.zip'
with zipfile.ZipFile(java_zip,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(JAVA.rglob('*')):
        if f.is_file(): z.write(f,f.relative_to(JAVA).as_posix())
sha=hashlib.sha1(java_zip.read_bytes()).hexdigest()
(OUT/'RaisNet-RaisRelic-LegendaryWeapons-Java-26.2-v3.0.sha1').write_text(sha+'\n')
print(java_zip.name,java_zip.stat().st_size,sha)

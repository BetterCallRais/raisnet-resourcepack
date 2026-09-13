from pathlib import Path
import json, math, zipfile, hashlib, shutil
from PIL import Image, ImageDraw

ROOT=Path('build/legendarsenal_v101')
OUT=Path('RaisLegendArsenal-Java-26.2-v1.0.1.zip')
SHA=Path('RaisLegendArsenal-Java-26.2-v1.0.1.sha1')
shutil.rmtree(ROOT, ignore_errors=True)
ROOT.mkdir(parents=True)

weapons=[
('royal_longsword',(235,190,60),(80,150,255)),('dark_katana',(70,8,20),(230,20,80)),
('celestial_spear',(30,150,230),(220,245,255)),('infernal_mace',(90,25,10),(255,80,15)),
('dragon_greatsword',(80,10,12),(245,35,40)),('moon_scythe',(35,18,75),(120,80,255)),
('arcane_bow',(70,35,100),(190,80,255)),('twin_daggers',(10,75,85),(40,230,255)),
('guardian_axe',(30,80,95),(80,220,245)),('hexa_noctis',(50,10,90),(180,70,255)),
]
fx=[('hexa_blade',(50,10,90),(210,120,255)),('fx_slash',(80,15,20),(255,50,80)),
('fx_lance',(20,90,120),(80,230,255)),('fx_rune',(60,20,100),(190,90,255)),
('fx_shockwave',(120,45,10),(255,130,20))]
alltex=weapons+fx

(ROOT/'pack.mcmeta').write_text(json.dumps({'pack':{
    'description':'RaisNet Legend Arsenal 3D • Java 26.2',
    'min_format':[88,0],'max_format':[88,0]
}},indent=2), encoding='utf-8')

im=Image.new('RGB',(128,128),(8,10,22)); d=ImageDraw.Draw(im)
for y in range(128):
    t=y/127
    d.line((0,y,127,y),fill=(int(12+30*t),int(18+40*t),int(38+80*t)))
for r in (48,38,28):
    d.ellipse((64-r,64-r,64+r,64+r),outline=(120,70+int(r),255),width=3)
d.polygon([(64,9),(74,50),(119,64),(74,78),(64,119),(54,78),(9,64),(54,50)],outline=(230,210,255),fill=(38,25,80))
d.text((43,56),'RLA',fill=(255,255,255))
im.save(ROOT/'pack.png')

tdir=ROOT/'assets/raisnet/textures/item'; tdir.mkdir(parents=True)
for name,c1,c2 in alltex:
    im=Image.new('RGBA',(64,64),(0,0,0,0)); dr=ImageDraw.Draw(im)
    for y in range(64):
        t=y/63
        c=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))+(255,)
        dr.rectangle((0,y,63,y),fill=c)
    for x in range(0,64,8): dr.line((x,0,63-x,63),fill=(255,255,255,48),width=1)
    dr.rectangle((2,2,61,61),outline=(255,255,255,160),width=2)
    dr.line((8,32,56,32),fill=(255,255,255,180),width=2)
    dr.line((32,8,32,56),fill=(255,255,255,130),width=1)
    im.save(tdir/f'{name}.png')

faces=['north','south','east','west','up','down']
def cube(fr,to,tex='#0',rot=None):
    e={'from':fr,'to':to,'faces':{k:{'texture':tex} for k in faces}}
    if rot:e['rotation']=rot
    return e

def displays(scale=1.0):
    return {
      'thirdperson_righthand':{'rotation':[0,-90,55],'translation':[0,4,.5],'scale':[.75*scale]*3},
      'thirdperson_lefthand':{'rotation':[0,90,-55],'translation':[0,4,.5],'scale':[.75*scale]*3},
      'firstperson_righthand':{'rotation':[0,-90,25],'translation':[1,4,1],'scale':[.85*scale]*3},
      'firstperson_lefthand':{'rotation':[0,90,-25],'translation':[1,4,1],'scale':[.85*scale]*3},
      'gui':{'rotation':[25,-35,0],'translation':[0,0,0],'scale':[.9*scale]*3},
      'ground':{'translation':[0,3,0],'scale':[.55*scale]*3},
      'fixed':{'rotation':[0,180,0],'scale':[.85*scale]*3}}

def rot(origin,axis,angle):return {'origin':origin,'axis':axis,'angle':angle,'rescale':True}

def elements(name):
    e=[]
    if name=='royal_longsword':
        e=[cube([7,0,7],[9,5,9]),cube([5.8,0,6.8],[10.2,1.4,9.2]),cube([2,4.4,7],[14,5.6,9]),cube([6.7,5,7.2],[9.3,15.3,8.8]),cube([7.2,15,7.4],[8.8,16,8.6]),cube([6.2,7,7],[6.8,14.5,9]),cube([9.2,7,7],[9.8,14.5,9])]
    elif name=='dark_katana':
        e=[cube([7.2,0,7.3],[8.8,5.5,8.7]),cube([5.7,5,7],[10.3,5.8,9]),cube([7.2,5.5,7.5],[8.5,10.2,8.5]),cube([7.7,10,7.5],[9,14.2,8.5]),cube([8.3,14,7.5],[9.5,16,8.5])]
    elif name=='celestial_spear':
        e=[cube([7.45,0,7.45],[8.55,12,8.55]),cube([6.5,11.2,6.8],[9.5,12.2,9.2]),cube([7,12,7],[9,14.4,9]),cube([7.5,14.2,7.4],[8.5,16,8.6]),cube([5.8,12.3,7.3],[7.2,13.2,8.7]),cube([8.8,12.3,7.3],[10.2,13.2,8.7])]
    elif name=='infernal_mace':
        e=[cube([7.3,0,7.3],[8.7,10.5,8.7]),cube([4.5,9.5,4.5],[11.5,14.5,11.5]),cube([3.5,11,6.5],[4.5,13,9.5]),cube([11.5,11,6.5],[12.5,13,9.5]),cube([6.5,14.5,6.5],[9.5,16,9.5]),cube([6.5,8.5,6.5],[9.5,10.2,9.5])]
    elif name=='dragon_greatsword':
        e=[cube([6.7,0,6.7],[9.3,4.5,9.3]),cube([2,4,6.2],[14,5.5,9.8]),cube([5.2,5,6.2],[10.8,14.5,9.8]),cube([6,14,6.5],[10,16,9.5]),cube([4.4,7,6.5],[5.2,12.5,9.5]),cube([10.8,7,6.5],[11.6,12.5,9.5])]
    elif name=='moon_scythe':
        e=[cube([7.35,0,7.35],[8.65,15,8.65]),cube([7.5,13.6,6.8],[13.5,15.3,9.2]),cube([11.8,12.2,6.8],[15.2,13.9,9.2],rot([12,13.5,8],'z',-22.5)),cube([13.6,10.8,7],[16,12.6,9],rot([14,12,8],'z',-22.5))]
    elif name=='arcane_bow':
        e=[cube([7.4,3,7.4],[8.6,13,8.6]),cube([4.5,11.5,7.2],[8,13,8.8],rot([7,12,8],'z',-22.5)),cube([3,8.5,7.2],[5.5,12,8.8],rot([5,10,8],'z',-22.5)),cube([8,11.5,7.2],[11.5,13,8.8],rot([9,12,8],'z',22.5)),cube([10.5,8.5,7.2],[13,12,8.8],rot([11,10,8],'z',22.5)),cube([4,7.8,7.8],[12,8.2,8.2])]
    elif name=='twin_daggers':
        for off in (-2.2,2.2):
            x=8+off;e += [cube([x-.7,1,7.3],[x+.7,6,8.7]),cube([x-2,5.6,7],[x+2,6.4,9]),cube([x-.8,6,7.4],[x+.8,13.5,8.6]),cube([x-.45,13.2,7.5],[x+.45,15,8.5])]
    elif name=='guardian_axe':
        e=[cube([7.2,0,7.2],[8.8,13,8.8]),cube([3.5,9.5,6.5],[7.5,14.5,9.5]),cube([8.5,9.5,6.5],[12.5,14.5,9.5]),cube([2.5,10.5,7],[4.2,13.5,9]),cube([11.8,10.5,7],[13.5,13.5,9]),cube([6.5,12.5,6.5],[9.5,15,9.5])]
    elif name in ('hexa_noctis','hexa_blade'):
        e=[cube([7.1,0,7.1],[8.9,4.8,8.9]),cube([3.8,4.2,6.8],[12.2,5.4,9.2]),cube([6.4,5,7],[9.6,14.5,9]),cube([7,14.2,7.2],[9,16,8.8]),cube([5.5,6,7.2],[6.4,12,8.8]),cube([9.6,6,7.2],[10.5,12,8.8])]
    return e

mdir=ROOT/'assets/raisnet/models/item'; mdir.mkdir(parents=True)
for n,_,_ in weapons+[('hexa_blade',(0,0,0),(0,0,0))]:
    model={'parent':'minecraft:block/block','textures':{'0':f'raisnet:item/{n}','particle':f'raisnet:item/{n}'},'elements':elements(n),'display':displays()}
    (mdir/f'{n}.json').write_text(json.dumps(model,indent=2),encoding='utf-8')

fxels={
 'fx_slash':[cube([1,7.4,7.6],[15,8.6,8.4],rot=rot([8,8,8],'z',22.5)),cube([4,6.8,7.7],[14,7.5,8.3],rot=rot([8,8,8],'z',-22.5))],
 'fx_lance':[cube([1,7.3,7.3],[15,8.7,8.7]),cube([13.5,6.2,6.2],[16,9.8,9.8])],
 'fx_rune':[cube([2,7.5,2],[14,8.5,3]),cube([13,7.5,2],[14,8.5,14]),cube([2,7.5,13],[14,8.5,14]),cube([2,7.5,2],[3,8.5,14]),cube([7.5,7.2,4],[8.5,8.8,12]),cube([4,7.2,7.5],[12,8.8,8.5])],
 'fx_shockwave':[cube([1,7.4,1],[15,8.6,2]),cube([14,7.4,1],[15,8.6,15]),cube([1,7.4,14],[15,8.6,15]),cube([1,7.4,1],[2,8.6,15])]
}
for n,els in fxels.items():
    model={'parent':'minecraft:block/block','textures':{'0':f'raisnet:item/{n}','particle':f'raisnet:item/{n}'},'elements':els,'display':displays(1.4)}
    (mdir/f'{n}.json').write_text(json.dumps(model,indent=2),encoding='utf-8')

legacy=ROOT/'assets/minecraft/models/item'; legacy.mkdir(parents=True)
over=[{'predicate':{'custom_model_data':1001+i},'model':f'raisnet:item/{n}'} for i,(n,_,_) in enumerate(weapons)]
over += [{'predicate':{'custom_model_data':cmd},'model':f'raisnet:item/{n}'} for cmd,n in [(1101,'hexa_blade'),(1201,'fx_slash'),(1202,'fx_lance'),(1203,'fx_rune'),(1204,'fx_shockwave')]]
(legacy/'netherite_sword.json').write_text(json.dumps({'parent':'minecraft:item/handheld','textures':{'layer0':'minecraft:item/netherite_sword'},'overrides':over},indent=2),encoding='utf-8')

items=ROOT/'assets/minecraft/items'; items.mkdir(parents=True)
entries=[]
for i,(n,_,_) in enumerate(weapons,1001): entries.append({'threshold':float(i),'model':{'type':'minecraft:model','model':f'raisnet:item/{n}'}})
for cmd,n in [(1101,'hexa_blade'),(1201,'fx_slash'),(1202,'fx_lance'),(1203,'fx_rune'),(1204,'fx_shockwave')]: entries.append({'threshold':float(cmd),'model':{'type':'minecraft:model','model':f'raisnet:item/{n}'}})
itemdef={'model':{'type':'minecraft:range_dispatch','property':'minecraft:custom_model_data','index':0,'entries':entries,'fallback':{'type':'minecraft:model','model':'minecraft:item/netherite_sword'}}}
(items/'netherite_sword.json').write_text(json.dumps(itemdef,indent=2),encoding='utf-8')

for f in ROOT.rglob('*.json'): json.loads(f.read_text(encoding='utf-8'))
if OUT.exists():OUT.unlink()
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(ROOT.rglob('*')):
        if f.is_file(): z.write(f,f.relative_to(ROOT).as_posix())
sha=hashlib.sha1(OUT.read_bytes()).hexdigest()
SHA.write_text(sha+'\n',encoding='utf-8')
print(OUT,OUT.stat().st_size,sha)

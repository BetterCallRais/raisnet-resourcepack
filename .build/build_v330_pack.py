from pathlib import Path
import zipfile, json, shutil, hashlib, math, uuid
from PIL import Image, ImageDraw, ImageFilter

BASE_JAVA=Path('LegendaryRais-Java-26.1.2-v3.2.0-HEALTH-ARMOR.zip')
BASE_BED=Path('.build/unused-bedrock')
OUTDIR=Path('.build/v330-out'); OUTDIR.mkdir(parents=True,exist_ok=True)
JROOT=OUTDIR/'java_pack'; BROOT=OUTDIR/'bedrock_pack'
if JROOT.exists(): shutil.rmtree(JROOT)
JROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE_JAVA) as z:
    assert z.testzip() is None
    z.extractall(JROOT)

def savej(root,rel,obj):
    p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,separators=(',',':')),encoding='utf-8')

def gradient_texture(path, size, c1,c2,accent, pattern='steel'):
    FW,FH=size
    w=min(FW,256);h=max(32,round(FH*w/FW))
    im=Image.new('RGBA',(w,h)); px=im.load()
    sx=FW/w;sy=FH/h
    for yy in range(h):
        y=yy*sy;v=yy/max(1,h-1)
        for xx in range(w):
            x=xx*sx;u=xx/max(1,w-1)
            grain=(math.sin(x*.073+y*.021)+math.cos(y*.095-x*.013)+math.sin((x+y)*.031))*.022
            shine=.84+.14*math.sin(math.pi*u)
            rgb=[]
            for i in range(3): rgb.append(int(max(0,min(255,(c1[i]*(1-v)+c2[i]*v)*shine+grain*255))))
            mark=False
            if pattern=='ember': mark=((int(x)+2*int(y))%193)<6
            elif pattern=='void': mark=((3*int(x)-int(y))%251)<5
            elif pattern=='storm': mark=abs(((int(x)-int(y))%283)-141)<4
            elif pattern=='gaia': mark=((int(x)//48+int(y)//48)%7==0 and int(x)%48<5)
            elif pattern=='astral': mark=((2*int(x)+3*int(y))%311)<5
            if mark: rgb=list(accent)
            px[xx,yy]=(*rgb,255)
    if (w,h)!=(FW,FH): im=im.resize((FW,FH),Image.Resampling.LANCZOS)
    im=im.filter(ImageFilter.UnsharpMask(radius=1.0,percent=100,threshold=3))
    path.parent.mkdir(parents=True,exist_ok=True); im.save(path,optimize=True,compress_level=6)

def cube(fr,to,tex,rot=None,shade=True):
    d={'from':[round(x,3) for x in fr],'to':[round(x,3) for x in to],'shade':shade,
       'faces':{k:{'texture':'#'+tex} for k in ('north','south','east','west','up','down')}}
    if rot:d['rotation']={'origin':[round(x,3) for x in rot[0]],'axis':rot[1],'angle':rot[2],'rescale':True}
    return d

def java_item(name,textures,elements,gui=.62,first=.84,third=.70):
    savej(JROOT,f'assets/legendaryv33/models/item/{name}.json',{
        'credit':'LegendaryRais v3.3 Final Rebuild','ambientocclusion':False,
        'textures':dict(textures,particle=next(iter(textures.values()))),'elements':elements,
        'display':{
            'gui':{'rotation':[24,-35,0],'translation':[0,-1,0],'scale':[gui]*3},
            'firstperson_righthand':{'rotation':[0,-90,25],'translation':[1.1,3,1.3],'scale':[first]*3},
            'firstperson_lefthand':{'rotation':[0,90,-25],'translation':[1.1,3,1.3],'scale':[first]*3},
            'thirdperson_righthand':{'rotation':[0,-90,55],'translation':[0,1,-3],'scale':[third]*3},
            'thirdperson_lefthand':{'rotation':[0,90,-55],'translation':[0,1,-3],'scale':[third]*3},
            'ground':{'scale':[.50]*3},'fixed':{'rotation':[0,180,0],'scale':[.78]*3}}})
    savej(JROOT,f'assets/legendaryv33/items/{name}.json',{'hand_animation_on_swap':True,'oversized_in_gui':True,'model':{'type':'minecraft:model','model':f'legendaryv33:item/{name}'}})

def tapered_blade(cx,y0,y1,w0,w1,thick,main,edge,segments=14):
    e=[]; step=(y1-y0)/segments
    for i in range(segments):
        a=i/segments;b=(i+1)/segments;wa=w0*(1-a)+w1*a;wb=w0*(1-b)+w1*b;w=max(wa,wb);y=y0+i*step
        e.append(cube([cx-w/2,y,8-thick/2],[cx+w/2,y+step+.015,8+thick/2],main))
        e.append(cube([cx-w/2-.10,y+.03,7.76],[cx-w/2+.10,y+step,8.24],edge))
        e.append(cube([cx+w/2-.10,y+.03,7.76],[cx+w/2+.10,y+step,8.24],edge))
    e.append(cube([cx-.16,y1,7.75],[cx+.16,min(31.7,y1+1.35),8.25],edge,([cx,y1+.1,8],'z',45)))
    return e

p=JROOT/'assets/legendaryv33'
if p.exists(): shutil.rmtree(p)

weapon_pal={
 'ember':((69,39,30),(27,17,17),(211,76,25),'ember'),
 'noctis':((36,33,43),(9,8,15),(128,61,166),'void'),
 'storm':((54,73,84),(21,31,39),(78,181,215),'storm'),
 'gaia':((78,83,56),(35,44,31),(65,104,50),'gaia'),
 'astral':((57,47,84),(20,16,37),(165,91,200),'astral')}
for k,(a,b,c,pat) in weapon_pal.items():
    gradient_texture(JROOT/f'assets/legendaryv33/textures/item/{k}_metal.png',(1024,1024),a,b,c,pat)
    gradient_texture(JROOT/f'assets/legendaryv33/textures/item/{k}_trim.png',(1024,1024),tuple(min(255,x+35) for x in a),tuple(max(0,x//2) for x in b),c,pat)
    gradient_texture(JROOT/f'assets/legendaryv33/textures/item/{k}_grip.png',(1024,1024),(55,34,23),(22,17,15),c,'steel')

e=tapered_blade(8,3.8,29.8,4.2,.65,1.05,'metal','trim',15)
e += [cube([7.72,5.2,7.45],[8.28,28.3,8.55],'trim'),
      cube([1.7,2.1,7.15],[7.1,3.35,8.85],'trim',([7.0,2.8,8],'z',-22.5)),cube([8.9,2.1,7.15],[14.3,3.35,8.85],'trim',([9.0,2.8,8],'z',22.5)),
      cube([7.18,-7.1,7.15],[8.82,2.45,8.85],'grip')]
for y in (-6.3,-4.8,-3.3,-1.8,-.3,1.2):e.append(cube([7.0,y,7.0],[9.0,y+.24,9.0],'trim'))
e += [cube([6.8,-9.6,6.8],[9.2,-7.0,9.2],'trim',([8,-8.3,8],'z',45))]
java_item('emberfall_claymore',{'metal':'legendaryv33:item/ember_metal','trim':'legendaryv33:item/ember_trim','grip':'legendaryv33:item/ember_grip'},e,.55,.75,.60)

e=tapered_blade(8,3.8,28.6,2.8,.42,.82,'metal','trim',15)
e += [cube([2.4,2.3,7.25],[7.25,3.35,8.75],'trim',([7.1,2.9,8],'z',22.5)),cube([8.75,2.3,7.25],[13.6,3.35,8.75],'trim',([8.9,2.9,8],'z',-22.5)),cube([7.3,-6.4,7.3],[8.7,2.5,8.7],'grip'),cube([6.9,-8.9,6.9],[9.1,-6.3,9.1],'trim',([8,-7.7,8],'z',45))]
for y in (-5.5,-4,-2.5,-1,.5):e.append(cube([7.05,y,7.08],[8.95,y+.18,8.92],'trim'))
java_item('noctis_longsword',{'metal':'legendaryv33:item/noctis_metal','trim':'legendaryv33:item/noctis_trim','grip':'legendaryv33:item/noctis_grip'},e,.62,.86,.68)

e=[cube([7.2,5.1,7.0],[8.8,12.0,9.0],'grip'),cube([6.65,7.1,6.55],[9.35,10.2,9.45],'trim')]
upper=[(8.0,12,0),(8.5,14.8,8),(9.25,17.5,15),(10.3,20.1,22.5),(11.25,22.8,30),(11.7,25.5,38)]
for x,y,a in upper:
    e.append(cube([x-.45,y,7.2],[x+.45,min(28.7,y+3.2),8.8],'metal',([x,y+1.5,8],'z',a)))
    yl=5-(y-12); e.append(cube([x-.45,max(-10.5,yl-3.2),7.2],[x+.45,yl,8.8],'metal',([x,yl-1.5,8],'z',-a)))
for y in range(-8,28,3):e.append(cube([12.45,y,7.9],[12.58,min(28.2,y+3.1),8.1],'trim'))
java_item('stormpiercer_recurve_bow',{'metal':'legendaryv33:item/storm_metal','trim':'legendaryv33:item/storm_trim','grip':'legendaryv33:item/storm_grip'},e,.66,.92,.76)

e=[cube([7.35,-15.5,7.35],[8.65,18.3,8.65],'grip')]
for y in range(-14,18,3):e.append(cube([7.12,y,7.12],[8.88,y+.20,8.88],'trim'))
widths=[1.1,1.8,2.6,3.25,3.55,3.1,2.35,1.45,.55]
for i,w in enumerate(widths):
    y=18.2+i*1.42;yt=min(31.15,y+1.44);e.append(cube([8-w/2,y,7.25],[8+w/2,yt,8.75],'metal'))
    e += [cube([8-w/2-.10,y+.03,7.55],[8-w/2+.10,yt-.03,8.45],'trim'),cube([8+w/2-.10,y+.03,7.55],[8+w/2+.10,yt-.03,8.45],'trim')]
e += [cube([7.65,-15.9,7.65],[8.35,-15.45,8.35],'trim')]
java_item('gaia_war_spear',{'metal':'legendaryv33:item/gaia_metal','trim':'legendaryv33:item/gaia_trim','grip':'legendaryv33:item/gaia_grip'},e,.56,.79,.64)

e=[]
for cx,ang in ((5.65,-8),(10.35,8)):
    e += tapered_blade(cx,2.4,18.5,1.8,.24,.64,'metal','trim',9)
    e += [cube([cx-1.45,.75,7.28],[cx+1.45,2.15,8.72],'trim',([cx,1.45,8],'z',ang)),cube([cx-.58,-5.4,7.4],[cx+.58,1.15,8.6],'grip'),cube([cx-.85,-7.1,7.1],[cx+.85,-5.35,8.9],'trim',([cx,-6.2,8],'z',45))]
java_item('astral_twin_daggers',{'metal':'legendaryv33:item/astral_metal','trim':'legendaryv33:item/astral_trim','grip':'legendaryv33:item/astral_grip'},e,.58,.80,.64)

sets={
'phoenix':((94,37,18),(193,74,24),(244,170,67)),
'voidwalker':((24,20,34),(66,42,91),(143,75,171)),
'titan':((45,57,48),(94,110,88),(163,140,72)),
'celestial':((56,77,96),(133,165,188),(91,190,222)),
'water_sovereign':((10,43,69),(20,121,160),(75,215,229))}

def armor_worn_tex(setn,c1,c2,accent,leggings=False):
    W,H=1024,512
    im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/(H-1); c=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))+(255,);d.line((0,y,W,y),fill=c)
    dark=tuple(max(0,int(x*.34)) for x in c1)+(255,); bright=tuple(min(235,int(x*1.18)) for x in c2)+(210,)
    for y in range(35,H,92):d.arc((80,y-30,W-80,y+65),190,350,fill=dark,width=7)
    for x in (128,320,512,704,896):d.line((x-18,0,x+18,H),fill=dark,width=3)
    for x in range(64,W,128):
        for y in range(48,H,96):d.ellipse((x-7,y-7,x+7,y+7),fill=accent+(255,),outline=dark,width=2)
    for i in range(38):
        x=(i*97+37)%W;y=(i*61+23)%H;d.line((x,y,min(W-1,x+52),min(H-1,y+7)),fill=bright,width=2)
    p=JROOT/f'assets/legendaryv33/textures/entity/equipment/{"humanoid_leggings" if leggings else "humanoid"}/{setn}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True,compress_level=6)

def armor_item(setn,piece,c1,c2,accent):
    gradient_texture(JROOT/f'assets/legendaryv33/textures/item/armor_{setn}_metal.png',(1024,1024),c1,c2,accent,'steel')
    gradient_texture(JROOT/f'assets/legendaryv33/textures/item/armor_{setn}_trim.png',(1024,1024),tuple(min(255,x+32) for x in c2),tuple(max(0,x//2) for x in c1),accent,'steel')
    e=[]
    if piece=='helmet':
        e=[cube([3.2,3.4,3.4],[12.8,12.6,12.6],'metal'),cube([3.8,3.2,2.6],[12.2,5.0,4.2],'trim'),cube([2.3,7,4.5],[4.2,13.5,11.5],'trim',([3.5,8,8],'z',-22.5)),cube([11.8,7,4.5],[13.7,13.5,11.5],'trim',([12.5,8,8],'z',22.5))]
    elif piece=='chest':
        e=[cube([3.3,.5,5.3],[12.7,13.5,10.7],'metal'),cube([1.0,6,5.4],[4.0,12.8,10.6],'trim',([3,8,8],'z',-22.5)),cube([12.0,6,5.4],[15.0,12.8,10.6],'trim',([13,8,8],'z',22.5)),cube([5.0,7,4.2],[11.0,11.7,5.9],'trim')]
    elif piece=='legs':
        e=[cube([3.2,.2,5.4],[7.2,13.5,10.6],'metal'),cube([8.8,.2,5.4],[12.8,13.5,10.6],'metal'),cube([4.2,10.5,4.7],[11.8,14.3,11.3],'trim')]
    else:
        e=[cube([3.2,.2,5.3],[7.2,11.3,10.7],'metal'),cube([8.8,.2,5.3],[12.8,11.3,10.7],'metal'),cube([2.7,7.0,4.7],[7.7,11.5,11.3],'trim'),cube([8.3,7.0,4.7],[13.3,11.5,11.3],'trim')]
    savej(JROOT,f'assets/legendaryv33/models/item/armor/{setn}_{piece}.json',{'credit':'LegendaryRais v3.3 armor','ambientocclusion':False,'textures':{'metal':f'legendaryv33:item/armor_{setn}_metal','trim':f'legendaryv33:item/armor_{setn}_trim','particle':f'legendaryv33:item/armor_{setn}_metal'},'elements':e,'display':{'gui':{'rotation':[20,-32,0],'scale':[.88]*3}}})
    savej(JROOT,f'assets/legendaryv33/items/armor/{setn}_{piece}.json',{'oversized_in_gui':True,'model':{'type':'minecraft:model','model':f'legendaryv33:item/armor/{setn}_{piece}'}})

for n,(a,b,c) in sets.items():
    armor_worn_tex(n,a,b,c,False);armor_worn_tex(n,a,b,c,True)
    savej(JROOT,f'assets/legendaryv33/equipment/{n}_set.json',{'layers':{'humanoid':[{'texture':f'legendaryv33:{n}'}],'humanoid_leggings':[{'texture':f'legendaryv33:{n}'}]}})
    for piece in ('helmet','chest','legs','boots'):armor_item(n,piece,a,b,c)

def fx_model(name,setn,kind):
    e=[]
    if kind=='slash':
        for i,a in enumerate((-45,-22.5,0,22.5,45)):e.append(cube([2.4,5.0+i*1.1,7.55],[13.6,5.45+i*1.1,8.45],'main',([8,8,8],'z',a)))
    elif kind=='meteor':
        e=[cube([6,3,6],[10,13,10],'main',([8,8,8],'z',45)),cube([5,7,7],[11,9,9],'main',([8,8,8],'z',45))]
    elif kind=='cage':
        for i in range(8):
            a=2*math.pi*i/8;x=8+math.cos(a)*5;z=8+math.sin(a)*5;e.append(cube([x-.22,2,z-.22],[x+.22,14,z+.22],'main'))
    elif kind=='vortex':
        for rr,yy,n in ((5.8,5,14),(4.2,8,11),(2.7,11,8)):
            for i in range(n):
                a=2*math.pi*i/n;x=8+math.cos(a)*rr;z=8+math.sin(a)*rr;e.append(cube([x-.55,yy-.18,z-.14],[x+.55,yy+.18,z+.14],'main'))
    elif kind=='bolt':
        for i in range(8):e.append(cube([7.7+i*.27,2.5+i*1.38,7.65],[8.3+i*.27,4.4+i*1.38,8.35],'main',([8,8,8],'z',22.5 if i%2 else -22.5)))
    elif kind=='spikes':
        for i in range(10):
            a=2*math.pi*i/10;x=8+math.cos(a)*5;z=8+math.sin(a)*5;e.append(cube([x-.32,2,z-.32],[x+.32,10,z+.32],'main',([x,2,z],'z',22.5 if i%2 else -22.5)))
    elif kind=='stars':
        for i in range(6):
            a=2*math.pi*i/6;x=8+math.cos(a)*5;z=8+math.sin(a)*5;e += [cube([x-.18,6,z-1.3],[x+.18,10,z+1.3],'main',([x,8,z],'z',45)),cube([x-1.3,7.82,z-.18],[x+1.3,8.18,z+.18],'main',([x,8,z],'z',45))]
    savej(JROOT,f'assets/legendaryv33/models/item/{name}.json',{'ambientocclusion':False,'textures':{'main':f'legendaryv33:item/armor_{setn}_trim','particle':f'legendaryv33:item/armor_{setn}_trim'},'elements':e})
    savej(JROOT,f'assets/legendaryv33/items/{name}.json',{'model':{'type':'minecraft:model','model':f'legendaryv33:item/{name}'}})

fx_specs=[
('fx_ember_rift','phoenix','slash'),('fx_ember_meteor','phoenix','meteor'),('fx_inferno_crown','phoenix','vortex'),
('fx_shade_step','voidwalker','vortex'),('fx_soul_harvest','voidwalker','slash'),('fx_eclipse_cage','voidwalker','cage'),
('fx_gale_bolt','celestial','bolt'),('fx_cyclone_volley','celestial','vortex'),('fx_thunderhead','celestial','stars'),
('fx_rootline','titan','spikes'),('fx_stoneguard','titan','cage'),('fx_worldspike','titan','spikes'),
('fx_rift_blink','celestial','vortex'),('fx_star_shards','celestial','stars'),('fx_dimension_rend','celestial','slash'),
('fx_phoenix_rebirth','phoenix','vortex'),('fx_void_phase','voidwalker','cage'),('fx_titan_bastion','titan','spikes'),('fx_celestial_sanctuary','celestial','stars'),('fx_water_sovereign_guard','water_sovereign','vortex')]
for x in fx_specs:fx_model(*x)

savej(JROOT,'pack.mcmeta',{'pack':{'description':'LegendaryRais v3.3 FINAL REBUILD • fixed models + real health + premium Water Relics locked','min_format':[84,0],'max_format':[84,0]}})

for p in JROOT.rglob('*.json'):json.loads(p.read_text(encoding='utf-8'))
for p in JROOT.glob('assets/legendaryv33/models/item/**/*.json'):
    d=json.loads(p.read_text())
    for el in d.get('elements',[]):
        vals=el.get('from',[])+el.get('to',[])
        assert all(-16 <= float(v) <= 32 for v in vals),(p,el)
    for v in d.get('textures',{}).values():
        if isinstance(v,str) and not v.startswith('#') and ':' in v:
            ns,path=v.split(':',1);tp=JROOT/f'assets/{ns}/textures/{path}.png';assert tp.exists(),(p,v,tp)
for nm in ('emberfall_claymore','noctis_longsword','stormpiercer_recurve_bow','gaia_war_spear','astral_twin_daggers'):
    assert (JROOT/f'assets/legendaryv33/items/{nm}.json').exists()
water_java=['assets/soultide/models/item/soul_tide_sovereign_blade.json','assets/legendaryrais/models/item/abyss_leviathan_trident.json','assets/legendaryrais/models/item/fx_leviathan_projectile.json']
with zipfile.ZipFile(BASE_JAVA) as z:
    for rel in water_java: assert hashlib.sha256((JROOT/rel).read_bytes()).digest()==hashlib.sha256(z.read(rel)).digest(),rel

JAVA_OUT=Path('LegendaryRais-Java-26.1.2-v3.3.0-FINAL-REBUILD.zip')
if JAVA_OUT.exists():JAVA_OUT.unlink()
with zipfile.ZipFile(JAVA_OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(JROOT.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(JROOT).as_posix())
with zipfile.ZipFile(JAVA_OUT) as z:assert z.testzip() is None
JAVA_SHA1=hashlib.sha1(JAVA_OUT.read_bytes()).hexdigest();Path('LegendaryRais-Java-26.1.2-v3.3.0-FINAL-REBUILD.sha1').write_text(JAVA_SHA1+'\n')
print('JAVA_PACK_OK',JAVA_OUT.stat().st_size,JAVA_SHA1)

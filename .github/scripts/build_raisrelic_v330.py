import json, math, random, shutil, zipfile, hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

BASE_ZIP=Path('RaisNet-RaisRelic-LegendaryWeapons-Java-26.2-v3.2.zip')
OUT_DIR=Path('build/raisrelic-v330-pack')
OUT_ZIP=Path('RaisNet-RaisRelic-LegendaryWeapons-Java-26.1-v3.3.0.zip')
if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
OUT_DIR.mkdir(parents=True)
with zipfile.ZipFile(BASE_ZIP) as z: z.extractall(OUT_DIR)
root=OUT_DIR

(root/'assets/raisnet/models/legendary').mkdir(parents=True, exist_ok=True)
(root/'assets/raisnet/textures/item/legendary').mkdir(parents=True, exist_ok=True)
(root/'assets/raisnet/models/effects').mkdir(parents=True, exist_ok=True)
(root/'assets/raisnet/textures/item/effects').mkdir(parents=True, exist_ok=True)
(root/'assets/raisnet/items').mkdir(parents=True, exist_ok=True)

meta={'pack':{'description':'RaisNet • RaisRelic v3.3 Ascendant Forge • Original Legendary Swords • Cinematic Skills • Evolution','min_format':[88,0],'max_format':[88,0]}}
(root/'pack.mcmeta').write_text(json.dumps(meta,indent=2))

# pack icon
im=Image.new('RGBA',(256,256),(8,8,18,255)); dr=ImageDraw.Draw(im)
for r,a in [(110,80),(86,110),(62,150),(38,210)]:
    dr.ellipse((128-r,128-r,128+r,128+r),outline=(175,80,255,a),width=5)
dr.polygon([(128,26),(154,102),(142,102),(168,220),(128,194),(88,220),(114,102),(102,102)],fill=(230,235,255,245),outline=(120,55,235,255))
dr.line((128,35,128,205),fill=(255,125,235,255),width=6)
dr.text((74,228),'RAISNET',fill=(220,220,255,255))
im.save(root/'pack.png')

FACES=['north','south','east','west','up','down']
def elem(a,b,t,rotation=None):
    e={'from':[round(x,3) for x in a],'to':[round(x,3) for x in b],'faces':{f:{'texture':'#'+t} for f in FACES}}
    if rotation: e['rotation']=rotation
    return e
def rot(o,axis,angle): return {'origin':[round(x,3) for x in o],'axis':axis,'angle':angle,'rescale':True}

def clamp(v): return max(0,min(255,int(v)))
def mix(a,b,t): return tuple(clamp(a[i]*(1-t)+b[i]*t) for i in range(3))

def texture(path, base, accent, glow=False, seed=0, grip=False):
    random.seed(seed)
    w=h=128
    im=Image.new('RGBA',(w,h),(*base,255)); px=im.load()
    # brushed metal / magical gradient
    for y in range(h):
        for x in range(w):
            v=int(10*math.sin((x+y)*0.17)+7*math.cos(y*0.11)+random.randint(-3,3))
            if grip: v += 10 if ((x//8+y//8)%2==0) else -12
            px[x,y]=(clamp(base[0]+v),clamp(base[1]+v),clamp(base[2]+v),255)
    d=ImageDraw.Draw(im,'RGBA')
    # diagonal forged streaks
    for x in range(-128,256,18):
        d.line((x,0,x-90,128),fill=(*accent,70 if not glow else 120),width=3)
    # runic diamonds / borders
    for r in (10,24,40,56):
        d.rectangle((r,r,127-r,127-r),outline=(*accent,40 if not glow else 90),width=2)
    for i in range(7):
        cx=16+i*16; cy=64+int(math.sin(i*1.7)*18)
        d.polygon([(cx,cy-6),(cx+5,cy),(cx,cy+6),(cx-5,cy)],fill=(*accent,120 if glow else 70))
    if glow:
        halo=Image.new('RGBA',(w,h),(0,0,0,0)); hd=ImageDraw.Draw(halo,'RGBA')
        hd.line((10,118,118,10),fill=(*accent,220),width=6)
        hd.line((22,118,118,22),fill=(255,255,255,180),width=2)
        halo=halo.filter(ImageFilter.GaussianBlur(2.2))
        im=Image.alpha_composite(im,halo)
    im.save(path)

themes={
 'ame_no_zanketsu': dict(style='solar', metal=(224,208,154), dark=(54,38,18), accent=(255,166,44), glow=(255,238,132), grip=(82,56,25)),
 'kurohana_calamity': dict(style='void', metal=(116,108,145), dark=(12,8,24), accent=(110,45,170), glow=(218,86,255), grip=(38,22,52)),
 'seiryuu_lance': dict(style='storm', metal=(160,212,224), dark=(16,40,50), accent=(46,175,220), glow=(117,245,255), grip=(30,72,84)),
 'tsukikage_reaper': dict(style='phantom', metal=(218,224,230), dark=(40,43,56), accent=(130,150,184), glow=(224,245,255), grip=(65,72,88)),
 'guren_fang': dict(style='crimson', metal=(210,126,103), dark=(56,12,14), accent=(220,48,42), glow=(255,170,70), grip=(82,28,20)),
 'tenma_crusher': dict(style='earth', metal=(130,144,122), dark=(18,30,22), accent=(46,126,72), glow=(112,242,144), grip=(48,64,42)),
 'astra_veloce': dict(style='astral', metal=(226,232,246), dark=(20,26,58), accent=(87,113,220), glow=(166,215,255), grip=(48,54,98)),
 'hexa_noctis': dict(style='hexa', metal=(188,178,224), dark=(18,12,38), accent=(104,52,205), glow=(230,91,255), grip=(44,28,79)),
}

# evolution palettes blended from all base themes
base_order=['ame_no_zanketsu','kurohana_calamity','seiryuu_lance','tsukikage_reaper','guren_fang','tenma_crusher','astra_veloce','hexa_noctis']
evo_ids=['ascendant_ii','ascendant_iii','ascendant_iv','ascendant_v','ascendant_vi','ascendant_vii','eternity_empyrean']
for idx,eid in enumerate(evo_ids, start=2):
    chosen=base_order[:idx]
    def avg(key):
        vals=[themes[x][key] for x in chosen]
        return tuple(sum(v[i] for v in vals)//len(vals) for i in range(3))
    themes[eid]=dict(style='ascendant' if idx<8 else 'eternity',metal=avg('metal'),dark=avg('dark'),accent=avg('accent'),glow=avg('glow'),grip=avg('grip'),stage=idx)

def display(scale=1.12, long=False):
    sc=1.02 if long else scale
    return {
      'thirdperson_righthand':{'rotation':[0,-90,52],'translation':[0,2.8,0.8],'scale':[0.98,0.98,0.98]},
      'thirdperson_lefthand':{'rotation':[0,90,-52],'translation':[0,2.8,0.8],'scale':[0.98,0.98,0.98]},
      'firstperson_righthand':{'rotation':[0,-90,30],'translation':[0.9,2.0,0.8],'scale':[sc,sc,sc]},
      'firstperson_lefthand':{'rotation':[0,90,-30],'translation':[-0.9,2.0,0.8],'scale':[sc,sc,sc]},
      'gui':{'rotation':[28,225,0],'translation':[0,0,0],'scale':[0.82,0.82,0.82]},
      'ground':{'rotation':[0,0,0],'translation':[0,2.0,0],'scale':[0.67,0.67,0.67]},
      'fixed':{'rotation':[0,180,0],'translation':[0,0,0],'scale':[0.98,0.98,0.98]}
    }

def sword_model(wid, th):
    st=th['style']; stage=th.get('stage',1)
    E=[]
    # grip & pommel
    E += [elem([7.25,.25,7.2],[8.75,3.95,8.8],'grip'), elem([6.95,.0,6.95],[9.05,.72,9.05],'accent')]
    E += [elem([7.35,.35,6.7],[8.65,3.8,7.15],'dark'), elem([7.35,.35,8.85],[8.65,3.8,9.3],'dark')]
    # guard core
    E += [elem([5.0,3.85,6.95],[11.0,4.9,9.05],'dark'), elem([5.5,4.05,7.15],[10.5,4.7,8.85],'accent')]
    # guard wings
    wing=3.4 if st in ('earth','void') else 2.7
    E += [elem([3.4,3.9,7.05],[6.0,4.75,8.95],'accent',rot([5.7,4.3,8],'z',-22.5)), elem([10.0,3.9,7.05],[12.6,4.75,8.95],'accent',rot([10.3,4.3,8],'z',22.5))]
    # blade base/spine
    bw=1.35 if st=='earth' else 1.0 if st in ('phantom','astral') else 1.15
    E += [elem([8-bw,4.72,7.2],[8+bw,14.7,8.8],'metal')]
    E += [elem([7.72,5.0,6.92],[8.28,14.45,9.08],'glow')]
    # blade bevels
    E += [elem([6.45,5.0,7.35],[7.0,14.3,8.65],'dark'), elem([9.0,5.0,7.35],[9.55,14.3,8.65],'dark')]
    # tip crown
    E += [elem([6.7,13.9,7.2],[8.1,15.85,8.8],'metal',rot([7.6,14.7,8],'z',22.5)), elem([7.9,13.9,7.2],[9.3,15.85,8.8],'metal',rot([8.4,14.7,8],'z',-22.5))]
    # rune ribs along blade
    ribs=4+min(stage,4)
    for j in range(ribs):
        y=5.6+j*(8.3/max(1,ribs-1))
        E += [elem([6.15,y,7.15],[6.8,y+.34,8.85],'accent',rot([6.6,y+.2,8],'z',22.5 if j%2==0 else -22.5)),
              elem([9.2,y,7.15],[9.85,y+.34,8.85],'glow',rot([9.4,y+.2,8],'z',-22.5 if j%2==0 else 22.5))]
    # style-specific silhouette
    if st=='solar':
        for a,x in [(-45,4.7),(-22.5,5.7),(22.5,10.3),(45,11.3)]:
            E.append(elem([x,4.3,7.25],[x+.75,7.2,8.75],'glow',rot([x+.4,4.8,8],'z',a)))
        E.append(elem([7.1,9.0,6.65],[8.9,10.1,9.35],'accent',rot([8,9.5,8],'z',45)))
    elif st=='void':
        E += [elem([6.0,6.2,6.85],[6.75,13.9,9.15],'dark',rot([6.6,8,8],'z',-22.5)), elem([9.25,6.2,6.85],[10.0,13.9,9.15],'dark',rot([9.4,8,8],'z',22.5))]
        for y in (6.5,9,11.5): E.append(elem([7.1,y,6.55],[8.9,y+.42,9.45],'glow'))
    elif st=='storm':
        for j,y in enumerate((5.5,7.1,8.7,10.3,11.9,13.5)):
            side=1 if j%2==0 else -1; x=8+side*2.0
            E.append(elem([x-.28,y,7.0],[x+.28,y+1.35,9.0],'glow',rot([x,y+.6,8],'z',45*side)))
    elif st=='phantom':
        for x in (5.6,10.0):
            E.append(elem([x,5.0,7.2],[x+.45,12.7,8.8],'accent'))
            E.append(elem([x-.5,11.6,7.0],[x+.95,13.0,9.0],'glow',rot([x+.2,12.2,8],'z',45 if x<8 else -45)))
    elif st=='crimson':
        for j,a in enumerate((-45,-22.5,22.5,45)):
            x=4.8+j*2.1
            E.append(elem([x,6.0+j*.8,7.15],[x+.9,9.4+j*.6,8.85],'accent',rot([x+.4,7,8],'z',a)))
    elif st=='earth':
        E += [elem([5.7,5.0,6.7],[7.1,13.7,9.3],'dark'),elem([8.9,5.0,6.7],[10.3,13.7,9.3],'dark')]
        for y in (6.1,8.2,10.3,12.4): E.append(elem([5.45,y,7.0],[10.55,y+.5,9.0],'accent'))
    elif st=='astral':
        for j,a in enumerate((0,45,90,135)):
            # star crown around mid blade
            x=8+math.cos(math.radians(a))*2.4; y=9+math.sin(math.radians(a))*1.8
            E.append(elem([x-.35,y-.35,7.0],[x+.35,y+.35,9.0],'glow',rot([x,y,8],'z',45 if j%2==0 else -45)))
    elif st=='hexa':
        for j,a in enumerate(range(0,360,60)):
            x=8+math.cos(math.radians(a))*2.35; y=7.0+j*.65
            E.append(elem([x-.28,y,6.65],[x+.28,y+1.55,9.35],'glow',rot([x,y+.7,8],'z',45 if j%2==0 else -45)))
    else: # ascendant / eternity
        rings=stage
        for j in range(min(8,rings)):
            a=360*j/max(1,min(8,rings)); x=8+math.cos(math.radians(a))*2.65; y=7.0+math.sin(math.radians(a))*2.2
            E.append(elem([x-.32,y-.55,6.65],[x+.32,y+1.25,9.35],'glow',rot([x,y,8],'z',45 if j%2==0 else -45)))
        for y in [5.4,7.1,8.8,10.5,12.2,13.9][:min(6,stage)]:
            E.append(elem([5.65,y,6.8],[6.25,y+.45,9.2],'accent',rot([6,y+.2,8],'z',-22.5)))
            E.append(elem([9.75,y,6.8],[10.35,y+.45,9.2],'accent',rot([10,y+.2,8],'z',22.5)))
        if st=='eternity':
            for a in (-45,-22.5,22.5,45):
                E.append(elem([4.0,8.0,7.0],[5.1,14.7,9.0],'glow',rot([5,8.2,8],'z',a)))
                E.append(elem([10.9,8.0,7.0],[12.0,14.7,9.0],'glow',rot([11,8.2,8],'z',-a)))
            E.append(elem([6.2,14.2,6.5],[9.8,15.4,9.5],'accent',rot([8,14.7,8],'z',45)))
    return {'ambientocclusion':False,'textures':{k:f'raisnet:item/legendary/{wid}_{k}' for k in ('metal','dark','accent','glow','grip')},'elements':E,'display':display(1.10, stage>=7)}

for idx,(wid,th) in enumerate(themes.items()):
    tdir=root/'assets/raisnet/textures/item/legendary'
    for k in ('metal','dark','accent','glow','grip'):
        base=th[k]; acc=th['glow'] if k!='glow' else (255,255,255)
        texture(tdir/f'{wid}_{k}.png',base,acc,glow=(k=='glow'),seed=hash(wid+k)&0xffff,grip=(k=='grip'))
    model=sword_model(wid,th)
    (root/f'assets/raisnet/models/legendary/{wid}.json').write_text(json.dumps(model,indent=2))
    (root/f'assets/raisnet/items/{wid}.json').write_text(json.dumps({'model':{'type':'minecraft:model','model':f'raisnet:legendary/{wid}'},'hand_animation_on_swap':False,'oversized_in_gui':True},indent=2))

# Keep orbit model separate but more compact for Hexa projectiles
hexa=json.loads((root/'assets/raisnet/models/legendary/hexa_noctis.json').read_text())
hexa['display']['fixed']={'rotation':[0,180,0],'translation':[0,0,0],'scale':[0.72,0.72,0.72]}
(root/'assets/raisnet/models/legendary/hexa_noctis_orbit.json').write_text(json.dumps(hexa,indent=2))
(root/'assets/raisnet/items/hexa_noctis_orbit.json').write_text(json.dumps({'model':{'type':'minecraft:model','model':'raisnet:legendary/hexa_noctis_orbit'},'hand_animation_on_swap':False,'oversized_in_gui':True},indent=2))

# Re-theme legacy skill FX textures to match new seven swords while retaining model keys used by plugin.
legacy_fx={
 'fx_cyan_slash':(255,210,70),'fx_cyan_horizon':(255,238,160),
 'fx_crimson_arc':(120,45,190),'fx_crimson_burst':(225,80,255),
 'fx_dragon_spiral':(65,210,255),'fx_dragon_head':(145,245,255),
 'fx_moon_crescent':(205,220,235),'fx_moon_execution':(245,250,255),
 'fx_guren_slash_a':(230,55,35),'fx_guren_slash_b':(255,135,45),'fx_guren_cross':(255,190,70),
 'fx_oni_ring':(65,160,90),'fx_oni_impact':(90,220,120),'fx_oni_pillar':(125,250,150),
 'fx_star_projectile':(120,165,255),'fx_star_burst':(205,230,255),
 'fx_hexa_slash':(200,90,255),'fx_hexa_burst':(155,55,235)
}

def make_fx_texture(name,col,kind='slash'):
    im=Image.new('RGBA',(128,128),(0,0,0,0)); d=ImageDraw.Draw(im,'RGBA')
    if kind in ('ring','crown'):
        for r in (54,43,31,19): d.ellipse((64-r,64-r,64+r,64+r),outline=(*col,210),width=5)
        for a in range(0,360,45):
            x=64+math.cos(math.radians(a))*48; y=64+math.sin(math.radians(a))*48
            d.polygon([(x,y-8),(x+6,y),(x,y+8),(x-6,y)],fill=(*col,190))
    elif kind=='throne':
        d.polygon([(18,100),(30,28),(46,70),(64,16),(82,70),(98,28),(110,100)],fill=(*col,170),outline=(255,255,255,220))
        d.rectangle((24,94,104,110),fill=(*col,220)); d.line((64,18,64,108),fill=(255,255,255,230),width=4)
    elif kind=='star':
        pts=[]
        for i in range(16):
            a=-math.pi/2+i*math.pi/8; r=55 if i%2==0 else 23; pts.append((64+math.cos(a)*r,64+math.sin(a)*r))
        d.polygon(pts,fill=(*col,200),outline=(255,255,255,210))
    else:
        d.polygon([(6,96),(22,78),(47,64),(72,48),(116,20),(97,42),(73,62),(44,78)],fill=(*col,210))
        d.line((12,92,108,26),fill=(255,255,255,235),width=4)
        d.arc((22,18,112,108),200,330,fill=(*col,150),width=6)
    halo=im.filter(ImageFilter.GaussianBlur(4)); im=Image.alpha_composite(halo,im)
    im.save(root/f'assets/raisnet/textures/item/effects/{name}.png')

for n,c in legacy_fx.items():
    kind='ring' if any(x in n for x in ('burst','impact','ring')) else ('star' if 'star' in n else 'slash')
    make_fx_texture(n,c,kind)

cast_fx={
 'fx_cast_solar':((255,210,70),'ring'),'fx_cast_void':((180,70,255),'ring'),'fx_cast_storm':((85,225,255),'ring'),
 'fx_cast_phantom':((220,235,250),'ring'),'fx_cast_crimson':((255,75,45),'ring'),'fx_cast_earth':((90,210,120),'ring'),
 'fx_cast_astral':((145,185,255),'star'),'fx_cast_ascendant':((225,120,255),'ring'),'fx_cast_release':((255,255,255),'star'),
 'fx_ascendant_forge':((220,90,255),'ring'),'fx_ascendant_blade_a':((255,210,90),'slash'),'fx_ascendant_blade_b':((160,85,255),'slash'),
 'fx_ascendant_crown':((230,150,255),'crown'),'fx_eternity_throne':((245,225,255),'throne')
}
for n,(c,k) in cast_fx.items(): make_fx_texture(n,c,k)

# generic effect models + modern item definitions
for n,(c,k) in cast_fx.items():
    if k in ('ring','crown'):
        es=[elem([0.5,7.65,0.5],[15.5,8.35,15.5],'fx')]
    elif k=='throne':
        es=[elem([1.0,0.5,7.4],[15.0,15.5,8.6],'fx')]
    else:
        es=[elem([0.8,7.45,7.5],[15.2,8.55,8.5],'fx',rot([8,8,8],'z',-22.5))]
    mm={'ambientocclusion':False,'textures':{'fx':f'raisnet:item/effects/{n}'},'elements':es,'display':{'fixed':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[2.2,2.2,2.2]},'gui':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[.9,.9,.9]}}}
    (root/f'assets/raisnet/models/effects/{n}.json').write_text(json.dumps(mm,indent=2))
    (root/f'assets/raisnet/items/{n}.json').write_text(json.dumps({'model':{'type':'minecraft:model','model':f'raisnet:effects/{n}'},'hand_animation_on_swap':False,'oversized_in_gui':True},indent=2))

# Validate every JSON and every texture reference used by our generated models.
for f in root.rglob('*.json'):
    json.loads(f.read_text())

if OUT_ZIP.exists(): OUT_ZIP.unlink()
with zipfile.ZipFile(OUT_ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in sorted(root.rglob('*')):
        if f.is_file(): z.write(f,f.relative_to(root).as_posix())
sha1=hashlib.sha1(OUT_ZIP.read_bytes()).hexdigest()
Path('RaisNet-RaisRelic-LegendaryWeapons-Java-26.1-v3.3.0.sha1').write_text(sha1+'\n')
print('built',OUT_ZIP,OUT_ZIP.stat().st_size,'sha1',sha1)
print('json',sum(1 for _ in root.rglob('*.json')),'png',sum(1 for _ in root.rglob('*.png')))

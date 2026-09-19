from pathlib import Path
import zipfile, json, shutil, hashlib, math, struct, zlib, random
BASE=Path('LegendaryRais-Java-26.1.2-v2.9.6-ABSOLUTE-WATER.zip')
ROOT=Path('.build/pack300')
OUT=Path('LegendaryRais-Java-26.1.2-v3.0.0-LEGENDARY-ARSENAL.zip')
if ROOT.exists(): shutil.rmtree(ROOT)
ROOT.mkdir(parents=True)
with zipfile.ZipFile(BASE) as z:z.extractall(ROOT)

def save(rel,obj):
 p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,separators=(',',':')),encoding='utf-8')

def png(path,w,h,fn):
 path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
 raw=bytearray()
 for y in range(h):
  raw.append(0)
  for x in range(w): raw.extend(fn(x,y))
 def chunk(t,d):
  return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b'')
 path.write_bytes(data)

def texture(name,c1,c2,accent):
 def f(x,y):
  u=x/1023;v=y/1023
  wave=(math.sin(u*18+v*9)+math.cos(v*22-u*7))*0.08
  r=int(max(0,min(255,c1[0]*(1-v)+c2[0]*v+wave*255)))
  g=int(max(0,min(255,c1[1]*(1-v)+c2[1]*v+wave*255)))
  b=int(max(0,min(255,c1[2]*(1-v)+c2[2]*v+wave*255)))
  if abs(((x+y*2)%173)-86)<3 or abs(((x*2-y)%211)-105)<2: r,g,b=accent
  return r,g,b,255
 png(f'assets/legendaryrais/textures/item/{name}.png',1024,1024,f)

def armor_tex(name,c1,c2,accent,leggings=False):
 W,H=1024,512
 def f(x,y):
  u=x/(W-1);v=y/(H-1);wave=(math.sin(u*35)+math.cos(v*26))*0.06
  r=int(max(0,min(255,c1[0]*(1-v)+c2[0]*v+wave*255)))
  g=int(max(0,min(255,c1[1]*(1-v)+c2[1]*v+wave*255)))
  b=int(max(0,min(255,c1[2]*(1-v)+c2[2]*v+wave*255)))
  if ((x+2*y)%127)<4 or ((3*x-y)%191)<3: r,g,b=accent
  return r,g,b,255
 folder='humanoid_leggings' if leggings else 'humanoid'
 png(f'assets/legendaryrais/textures/entity/equipment/{folder}/{name}.png',W,H,f)

def cube(fr,to,tex,rot=None):
 faces={k:{'texture':'#'+tex} for k in ['north','south','east','west','up','down']}
 d={'from':[round(x,3) for x in fr],'to':[round(x,3) for x in to],'faces':faces}
 if rot:d['rotation']={'origin':rot[0],'axis':rot[1],'angle':rot[2],'rescale':True}
 return d

def weapon_model(name,style,colors):
 tex=name+'_tex'; texture(tex,*colors); els=[]
 if style=='greatsword':
  els += [cube([7,-12,7],[9,7,9],'main'),cube([5.7,5,6.6],[10.3,8,9.4],'dark'),cube([7.2,7,6.8],[8.8,31,9.2],'main')]
  for y in range(9,30,3): els += [cube([6.4,y,7.1],[9.6,y+.45,8.9],'accent'),cube([7.4,y+.4,6.2],[8.6,y+2.5,9.8],'main',([8,y+1.4,8],'z',-22.5 if y%2 else 22.5))]
 elif style=='reaper':
  els += [cube([7.2,-13,7.2],[8.8,19,8.8],'dark')]
  for i,a in enumerate([-45,-22.5,0,22.5,45]): els.append(cube([8,15+i*1.2,7],[15,17+i*1.2,9],'main',([8,16+i*1.2,8],'z',a)))
  els += [cube([6.3,14,6.3],[9.7,17,9.7],'accent',([8,15.5,8],'z',45))]
 elif style=='bow':
  els += [cube([7.2,-9,7.2],[8.8,25,8.8],'dark')]
  for y,a in [(-5,-22.5),(0,-45),(5,-22.5),(15,22.5),(20,45),(25,22.5)]: els.append(cube([4.5,y,7],[11.5,y+1.2,9],'main',([8,y+.6,8],'z',a)))
  els += [cube([7.65,-8,7.65],[8.35,27,8.35],'accent')]
 elif style=='spear':
  els += [cube([7.2,-15,7.2],[8.8,20,8.8],'dark'),cube([6.1,18,6.2],[9.9,24,9.8],'accent',([8,21,8],'z',45)),cube([7,22,6.6],[9,33,9.4],'main')]
  for y in range(-12,20,4):els.append(cube([6.7,y,6.7],[9.3,y+.35,9.3],'accent'))
 elif style=='katars':
  els += [cube([5,-8,7],[7,5,9],'dark'),cube([9,-8,7],[11,5,9],'dark')]
  for x,a in [(5,-22.5),(11,22.5)]:els += [cube([x-1,3,6.7],[x+1,25,9.3],'main',([x,12,8],'z',a)),cube([x-1.4,4,6.4],[x+1.4,8,9.6],'accent',([x,6,8],'z',45))]
 model={'credit':'LegendaryRais v3.0 HD','textures':{'main':f'legendaryrais:item/{tex}','dark':f'legendaryrais:item/{tex}','accent':f'legendaryrais:item/{tex}','particle':f'legendaryrais:item/{tex}'},'elements':els,'display':{'thirdperson_righthand':{'rotation':[0,-90,55],'translation':[0,1,-3],'scale':[.75,.75,.75]},'firstperson_righthand':{'rotation':[0,-90,25],'translation':[1,3,1],'scale':[.9,.9,.9]},'gui':{'rotation':[25,-35,0],'translation':[0,0,0],'scale':[.72,.72,.72]}}}
 save(f'assets/legendaryrais/models/item/{name}.json',model)
 save(f'assets/legendaryrais/items/{name}.json',{'hand_animation_on_swap':True,'oversized_in_gui':True,'model':{'type':'minecraft:model','model':f'legendaryrais:item/{name}'}})
 return len(els)

pal={'emberfall_greatsword':((82,15,5),(230,55,5),(255,180,30)),'noctis_reaper':((8,5,18),(70,20,105),(210,60,255)),'stormpiercer_bow':((20,28,42),(70,135,175),(210,245,255)),'gaia_thorn_spear':((18,55,28),(75,125,42),(205,225,85)),'astral_rift_katars':((28,8,60),(110,45,180),(255,170,255))}
styles={'emberfall_greatsword':'greatsword','noctis_reaper':'reaper','stormpiercer_bow':'bow','gaia_thorn_spear':'spear','astral_rift_katars':'katars'}
counts={n:weapon_model(n,styles[n],pal[n]) for n in pal}
armor_pal={'phoenix':((80,20,5),(220,70,5),(255,210,80)),'voidwalker':((10,5,22),(70,25,110),(190,70,255)),'titan':((20,55,35),(75,130,75),(210,190,80)),'celestial':((28,60,100),(105,180,220),(235,250,255)),'water_sovereign':((5,30,65),(12,125,175),(80,240,255))}
for setn,cols in armor_pal.items():
 texture('armor_'+setn,*cols);armor_tex(setn,*cols,False);armor_tex(setn,*cols,True)
 save(f'assets/legendaryrais/models/equipment/{setn}_set.json',{'layers':{'humanoid':[{'texture':f'legendaryrais:{setn}'}],'humanoid_leggings':[{'texture':f'legendaryrais:{setn}'}]}})
 for piece in ['helmet','chest','legs','boots']:
  if piece=='helmet': els=[cube([3,3,3],[13,13,13],'main'),cube([2,10,4],[5,17,12],'accent',([4,12,8],'z',-22.5)),cube([11,10,4],[14,17,12],'accent',([12,12,8],'z',22.5)),cube([6,12,2],[10,17,5],'accent')]
  elif piece=='chest': els=[cube([3,0,5],[13,13,11],'main'),cube([1,5,6],[4,12,10],'accent',([3,8,8],'z',-22.5)),cube([12,5,6],[15,12,10],'accent',([13,8,8],'z',22.5)),cube([6,7,3],[10,11,6],'accent',([8,9,5],'z',45))]
  elif piece=='legs': els=[cube([3,1,5],[7,15,11],'main'),cube([9,1,5],[13,15,11],'main'),cube([5,11,4],[11,15,12],'accent')]
  else: els=[cube([3,1,5],[7,12,11],'main'),cube([9,1,5],[13,12,11],'main'),cube([2.5,8,4.5],[7.5,12,11.5],'accent'),cube([8.5,8,4.5],[13.5,12,11.5],'accent')]
  model={'credit':'LegendaryRais v3.0 HD Armor','textures':{'main':f'legendaryrais:item/armor_{setn}','accent':f'legendaryrais:item/armor_{setn}','particle':f'legendaryrais:item/armor_{setn}'},'elements':els,'display':{'gui':{'rotation':[20,-30,0],'scale':[.9,.9,.9]},'thirdperson_righthand':{'rotation':[0,0,0],'scale':[.6,.6,.6]}}}
  save(f'assets/legendaryrais/models/item/armor/{setn}_{piece}.json',model)
  save(f'assets/legendaryrais/items/armor/{setn}_{piece}.json',{'model':{'type':'minecraft:model','model':f'legendaryrais:item/armor/{setn}_{piece}'}})
fx_names=['fx_ember_rift','fx_ember_meteor','fx_inferno_crown','fx_shade_step','fx_soul_harvest','fx_eclipse_cage','fx_gale_bolt','fx_cyclone_volley','fx_thunderhead','fx_rootline','fx_stoneguard','fx_worldspike','fx_rift_blink','fx_star_shards','fx_dimension_rend','fx_phoenix_rebirth','fx_void_phase','fx_titan_bastion','fx_celestial_sanctuary','fx_water_sovereign_guard']
for n in fx_names:
 setkey='water_sovereign' if 'water_sovereign' in n else ('phoenix' if 'phoenix' in n else 'voidwalker' if 'void' in n or 'shade' in n or 'eclipse' in n or 'soul_harvest' in n else 'titan' if 'titan' in n or 'stone' in n or 'root' in n or 'world' in n else 'celestial' if 'celestial' in n or 'star' in n or 'rift' in n or 'dimension' in n else 'phoenix' if 'ember' in n or 'inferno' in n else 'celestial')
 tex='armor_'+setkey; els=[]
 for k in range(12):
  a=k*30;rad=4.5+(k%3)*1.2;x=8+math.cos(math.radians(a))*rad;z=8+math.sin(math.radians(a))*rad
  els.append(cube([x-.35,7+(k%2)*.4,z-.35],[x+.35,9+(k%2)*.4,z+.35],'main',([8,8,8],'y',22.5 if k%2 else -22.5)))
 save(f'assets/legendaryrais/models/item/{n}.json',{'textures':{'main':f'legendaryrais:item/{tex}','particle':f'legendaryrais:item/{tex}'},'elements':els})
 save(f'assets/legendaryrais/items/{n}.json',{'model':{'type':'minecraft:model','model':f'legendaryrais:item/{n}'}})
save('pack.mcmeta',{'pack':{'description':'LegendaryRais v3.0 LEGENDARY ARSENAL • Premium Water Relics + 5 gacha weapons + 5 armor sets • HD 3D','min_format':[84,0],'max_format':[84,0]}})
for p in ROOT.rglob('*.json'):json.loads(p.read_text())
if OUT.exists():OUT.unlink()
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUT) as z: assert z.testzip() is None
sha=hashlib.sha1(OUT.read_bytes()).hexdigest();Path(str(OUT)+'.sha1').write_text(sha+'\n')
print('PACK_OK',OUT.stat().st_size,sha,counts)
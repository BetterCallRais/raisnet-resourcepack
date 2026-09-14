#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, json, math, os, random, re, shutil, tarfile, urllib.request, zipfile
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path.cwd()
BASE_URL = 'https://raw.githubusercontent.com/BetterCallRais/raisnet-resourcepack/main/RaisNet-RaisRelic-SovereignArsenal-Java-26.1-v3.4.1-FIX.zip'
BASE_ZIP = ROOT / '.build' / 'raisrelic-v350-pack' / 'base-v341.zip'
DELTA_B64 = ROOT / '.build' / 'raisrelic-v350-pack' / 'nonpng_delta.b64'
WORK = ROOT / '.build' / 'raisrelic-v350-pack' / 'work'
OUT = ROOT / 'RaisNet-RaisRelic-UltimatePolish-Java-26.1-v3.5.0.zip'
SHA = ROOT / 'RaisNet-RaisRelic-UltimatePolish-Java-26.1-v3.5.0.sha1'

PALETTES = {
    'ame_no_zanketsu': ((238,215,116),(255,246,200),(118,83,28),(255,234,115)),
    'aurelius': ((238,215,116),(255,246,200),(118,83,28),(255,234,115)),
    'kurohana_calamity': ((64,35,84),(155,72,218),(19,14,29),(205,96,255)),
    'vanta': ((64,35,84),(155,72,218),(19,14,29),(205,96,255)),
    'seiryuu_lance': ((62,163,204),(117,230,255),(20,54,78),(192,249,255)),
    'tempest': ((62,163,204),(117,230,255),(20,54,78),(192,249,255)),
    'tsukikage_reaper': ((71,155,157),(130,245,224),(17,46,50),(176,255,239)),
    'eidolon': ((71,155,157),(130,245,224),(17,46,50),(176,255,239)),
    'guren_fang': ((180,51,34),(255,119,58),(65,18,16),(255,195,86)),
    'pyre': ((180,51,34),(255,119,58),(65,18,16),(255,195,86)),
    'tenma_crusher': ((124,104,67),(193,162,93),(52,43,32),(220,197,122)),
    'terra': ((124,104,67),(193,162,93),(52,43,32),(220,197,122)),
    'astra_veloce': ((126,154,222),(208,229,255),(49,42,91),(221,205,255)),
    'celestial': ((126,154,222),(208,229,255),(49,42,91),(221,205,255)),
    'hexa_noctis': ((92,41,128),(217,68,236),(22,14,34),(245,111,255)),
    'hexa': ((92,41,128),(217,68,236),(22,14,34),(245,111,255)),
    'ascendant_ii': ((197,159,72),(130,67,172),(36,24,36),(255,212,108)),
    'ascendant_iii': ((68,168,193),(163,95,210),(26,34,59),(188,240,255)),
    'ascendant_iv': ((74,132,150),(185,93,216),(24,26,45),(179,255,246)),
    'ascendant_v': ((211,70,46),(183,87,207),(53,20,29),(255,178,86)),
    'ascendant_vi': ((161,116,68),(116,124,221),(43,35,35),(235,205,120)),
    'ascendant_vii': ((139,163,229),(195,127,237),(41,38,79),(232,223,255)),
    'eternity_empyrean': ((210,184,102),(189,105,235),(31,25,53),(255,238,173)),
    'eternity': ((210,184,102),(189,105,235),(31,25,53),(255,238,173)),
}

def mix(a,b,t): return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
def clamp(x): return max(0,min(255,int(x)))

def palette_for(name):
    low=name.lower()
    for k,v in PALETTES.items():
        if k in low: return v
    if any(k in low for k in ('solar','crown','holy','gold')): return ((235,185,68),(255,239,149),(72,48,20),(255,245,178))
    if any(k in low for k in ('void','abyss','vanta','night')): return ((75,35,106),(176,66,226),(15,9,26),(231,104,255))
    if any(k in low for k in ('storm','lightning','skyline','electric')): return ((55,155,208),(126,230,255),(14,45,71),(214,250,255))
    if any(k in low for k in ('soul','phantom','reaper','spectral','funeral')): return ((55,139,145),(131,231,219),(14,39,46),(186,255,240))
    if any(k in low for k in ('fire','crimson','meteor','pyre','ember')): return ((194,51,34),(255,118,42),(69,14,17),(255,207,93))
    if any(k in low for k in ('terra','earth','world','rock','pillar')): return ((126,102,59),(195,158,87),(48,37,28),(225,198,125))
    if any(k in low for k in ('astral','celestial','star','constellation','judgment')): return ((111,146,220),(204,218,255),(43,34,84),(232,215,255))
    return ((115,89,153),(199,141,223),(26,21,37),(232,187,255))

def material_texture(path, size=512):
    name=path.stem.lower(); p0,p1,p2,glow=palette_for(name)
    seed=int(hashlib.sha256(str(path).encode()).hexdigest()[:16],16); rng=random.Random(seed)
    role='metal'
    for r in ('accent','dark','grip','glow','metal'):
        if name.endswith('_'+r): role=r
    if role=='metal': base=mix(p0,(210,210,220),.22)
    elif role=='accent': base=p1
    elif role=='dark': base=mix(p2,(0,0,0),.18)
    elif role=='grip': base=mix(p2,(75,54,43),.38)
    else: base=mix(glow,(255,255,255),.08)
    im=Image.new('RGBA',(size,size),(*base,255)); px=im.load()
    for y in range(size):
        wave=9*math.sin(y*.085)+5*math.sin(y*.021)
        for x in range(size):
            n=rng.randint(-16,16) + int(wave) + int(6*math.sin((x+y)*.045))
            if role=='glow': n//=3
            px[x,y]=(clamp(base[0]+n),clamp(base[1]+n),clamp(base[2]+n),255)
    d=ImageDraw.Draw(im,'RGBA')
    step=64
    for x in range(0,size,step): d.line((x,0,x,size), fill=(*mix(base,(255,255,255),.28),28), width=1)
    for y in range(0,size,step): d.line((0,y,size,y), fill=(*mix(base,(0,0,0),.4),34), width=1)
    for i in range(9):
        cx=(seed>>(i%8)*4)%size; cy=(seed>>(i%7)*5)%size
        rad=18+(seed>>(i+3))%42
        d.arc((cx-rad,cy-rad,cx+rad,cy+rad),rng.randrange(0,360),rng.randrange(180,540),fill=(*glow,70 if role!='dark' else 34),width=2)
    if role=='grip':
        for y in range(-size,size,28): d.line((-20,y,size+20,y+size//2),fill=(230,220,205,42),width=5)
    if role=='glow':
        layer=Image.new('RGBA',im.size,(0,0,0,0)); ld=ImageDraw.Draw(layer,'RGBA')
        for i in range(12):
            y=(i*43 + seed%31)%size
            ld.line((0,y,size,y+(seed%97)-48),fill=(*glow,120),width=2)
        blur=layer.filter(ImageFilter.GaussianBlur(6)); im=Image.alpha_composite(im,blur); im=Image.alpha_composite(im,layer)
    return im

def effect_texture(path, size=256):
    name=path.stem.lower(); p0,p1,p2,glow=palette_for(name)
    seed=int(hashlib.sha256(name.encode()).hexdigest()[:16],16); rng=random.Random(seed)
    im=Image.new('RGBA',(size,size),(0,0,0,0)); soft=Image.new('RGBA',im.size,(0,0,0,0)); sd=ImageDraw.Draw(soft,'RGBA'); d=ImageDraw.Draw(im,'RGBA')
    cx=cy=size//2
    for r in range(size//2,5,-5):
        a=int(2 + 38*(1-r/(size/2))**2)
        sd.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(*p0,a))
    if any(k in name for k in ('ring','halo','domain','crown','orbit','court','throne','constellation')):
        for j in range(2,6):
            r=25+j*18
            d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(*glow,90+20*(j%2)),width=2+j%2)
        pts=[]
        spikes=6 if 'hexa' in name else 8
        for i in range(spikes*2):
            a=i*math.pi/spikes-math.pi/2; rr=92 if i%2==0 else 64
            pts.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr))
        d.line(pts+[pts[0]],fill=(*p1,105),width=2)
    elif any(k in name for k in ('slash','cleave','guillotine','reaper','sweep','cross')):
        for j in range(5):
            off=(j-2)*5
            d.arc((18+off,36,238+off,220),205,338,fill=(*glow,170-j*18),width=7-j)
        if 'cross' in name: d.line((50,205,205,50),fill=(*p1,150),width=5)
    elif any(k in name for k in ('beam','pillar','lance','thrust','pierce','impale')):
        d.polygon([(cx-12,20),(cx+12,20),(cx+3,230),(cx-3,230)],fill=(*glow,185))
        d.line((cx,10,cx,246),fill=(255,255,255,195),width=3)
    elif any(k in name for k in ('meteor','boulder','rock','shard','rupture')):
        d.ellipse((73,72,183,182),fill=(*p0,175),outline=(*glow,190),width=4)
        for i in range(8):
            a=rng.random()*math.tau; rr=rng.randint(70,112); x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr
            d.polygon([(x,y),(cx+math.cos(a+.12)*50,cy+math.sin(a+.12)*50),(cx+math.cos(a-.12)*50,cy+math.sin(a-.12)*50)],fill=(*p1,105))
    else:
        for i in range(18):
            a=rng.random()*math.tau; r=rng.randint(20,112); x=cx+math.cos(a)*r; y=cy+math.sin(a)*r; s=rng.randint(2,8)
            d.ellipse((x-s,y-s,x+s,y+s),fill=(*glow,rng.randint(80,200)))
        d.ellipse((70,70,186,186),outline=(*p1,150),width=4)
    soft=soft.filter(ImageFilter.GaussianBlur(12)); im=Image.alpha_composite(soft,im)
    hd=ImageDraw.Draw(im,'RGBA')
    for i in range(10):
        a=(i/10)*math.tau + (seed%100)/100; r=40+(i%4)*14
        x=cx+math.cos(a)*r; y=cy+math.sin(a)*r
        hd.ellipse((x-2,y-2,x+2,y+2),fill=(255,255,255,180))
    return im

def collect_texture_refs(root):
    refs=set(); pat=re.compile(r'raisnet:item/([A-Za-z0-9_./-]+)')
    for f in (root/'assets'/'raisnet').rglob('*.json'):
        try: text=f.read_text('utf-8')
        except Exception: continue
        for m in pat.finditer(text): refs.add(m.group(1))
    return refs

def main():
    BASE_ZIP.parent.mkdir(parents=True,exist_ok=True)
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    urllib.request.urlretrieve(BASE_URL, BASE_ZIP)
    with zipfile.ZipFile(BASE_ZIP) as z: z.extractall(WORK)
    tgz=DELTA_B64.with_suffix('.tar.gz')
    tgz.write_bytes(base64.b64decode(''.join(DELTA_B64.read_text().split())))
    with tarfile.open(tgz,'r:gz') as t: t.extractall(WORK)
    refs=collect_texture_refs(WORK); targets=[]
    for ref in refs:
        if ref.startswith('legendary/') or ref.startswith('effects/'):
            targets.append(WORK/'assets'/'raisnet'/'textures'/'item'/(ref+'.png'))
    for folder in [WORK/'assets'/'raisnet'/'textures'/'item'/'legendary', WORK/'assets'/'raisnet'/'textures'/'item'/'effects']:
        if folder.exists(): targets.extend(folder.glob('*.png'))
    uniq={str(p):p for p in targets}
    for p in uniq.values():
        p.parent.mkdir(parents=True,exist_ok=True)
        im=material_texture(p,512) if '/legendary/' in str(p).replace('\\','/') else effect_texture(p,256)
        im.save(p,'PNG',optimize=True,compress_level=9)
    icon=effect_texture(Path('fx_eternity_eightfold.png'),512)
    icon.save(WORK/'pack.png','PNG',optimize=True,compress_level=9)
    mc=json.loads((WORK/'pack.mcmeta').read_text()); pf=mc.get('pack',{}).get('pack_format')
    if pf not in (84,84.0): raise SystemExit(f'Unexpected pack_format {pf}')
    missing=[]
    for ref in collect_texture_refs(WORK):
        p=WORK/'assets'/'raisnet'/'textures'/'item'/(ref+'.png')
        if not p.exists(): missing.append(ref)
    if missing: raise SystemExit('Missing textures: '+', '.join(missing[:20]))
    if OUT.exists(): OUT.unlink()
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(WORK.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(WORK).as_posix())
    sha1=hashlib.sha1(OUT.read_bytes()).hexdigest(); SHA.write_text(sha1+'\n')
    print('Built',OUT.name,'bytes',OUT.stat().st_size,'sha1',sha1,'textures',len(uniq))

if __name__=='__main__': main()

from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance
from pathlib import Path
import math, random, json, shutil
OUT=None
S=4; W=H=256; WS=HS=W*S

def up(points): return [(int(x*S),int(y*S)) for x,y in points]

def gradient_fill(mask, top, bottom, lateral=True):
    im=Image.new('RGBA',(WS,HS),(0,0,0,0)); px=im.load(); mp=mask.load()
    for y in range(HS):
        ty=y/(HS-1)
        for x in range(WS):
            if mp[x,y]:
                tx=x/(WS-1)
                t=.75*ty + (.25*tx if lateral else 0)
                c=tuple(int(top[i]*(1-t)+bottom[i]*t) for i in range(3))
                px[x,y]=c+(255,)
    return im

def metal_sprite(name, shape_draw, palette):
    base, hi, edge, glow=palette
    mask=Image.new('L',(WS,HS),0); md=ImageDraw.Draw(mask)
    shape_draw(md)
    body=gradient_fill(mask,hi,base)
    rnd=random.Random('v355-'+name)
    noise=Image.new('L',(WS,HS),0); np=noise.load()
    for y in range(0,HS,2):
        val=rnd.randint(2,18)
        for x in range(WS): np[x,y]=val
    tint=Image.new('RGBA',(WS,HS),edge+(0,)); tint.putalpha(ImageChops.multiply(mask,noise))
    body=Image.alpha_composite(body,tint)
    outline=mask.filter(ImageFilter.MaxFilter(11))
    inner=mask.filter(ImageFilter.MinFilter(7))
    ring=ImageChops.subtract(outline,inner)
    glowm=outline.filter(ImageFilter.GaussianBlur(12))
    canvas=Image.new('RGBA',(WS,HS),(0,0,0,0))
    g=Image.new('RGBA',(WS,HS),glow+(0,)); g.putalpha(glowm.point(lambda p:min(90,p//2)))
    canvas=Image.alpha_composite(canvas,g)
    o=Image.new('RGBA',(WS,HS),edge+(0,)); o.putalpha(ring.point(lambda p:min(230,p)))
    canvas=Image.alpha_composite(canvas,o)
    canvas=Image.alpha_composite(canvas,body)
    return canvas,mask

def line(d, pts, fill, width, joint='curve'):
    d.line(up(pts), fill=fill, width=int(width*S), joint=joint)

def poly(d, pts, fill=255): d.polygon(up(pts),fill=fill)

def ellipse(d, box, fill=255, outline=None, width=1):
    d.ellipse(tuple(int(v*S) for v in box),fill=fill,outline=outline,width=int(width*S))

def add_details(img, name, accent, detail_fn):
    lay=Image.new('RGBA',(WS,HS),(0,0,0,0)); d=ImageDraw.Draw(lay)
    detail_fn(d,accent)
    alpha=lay.getchannel('A').filter(ImageFilter.GaussianBlur(10))
    g=Image.new('RGBA',(WS,HS),accent+(0,)); g.putalpha(alpha.point(lambda p:min(115,p//2)))
    img=Image.alpha_composite(img,g); img=Image.alpha_composite(img,lay)
    return img

def draw_ember(maskd):
    poly(maskd,[(121,34),(128,17),(135,34),(145,49),(141,69),(149,82),(141,171),(133,184),(123,184),(115,171),(107,82),(115,69),(111,49)])
    poly(maskd,[(87,178),(116,168),(124,177),(110,188),(84,192),(66,185)])
    poly(maskd,[(169,178),(140,168),(132,177),(146,188),(172,192),(190,185)])
    poly(maskd,[(122,184),(134,184),(136,221),(132,232),(124,232),(120,221)])
    poly(maskd,[(119,231),(137,231),(143,239),(135,246),(121,246),(113,239)])

def det_ember(d,a):
    line(d,[(128,35),(128,172)],a+(225,),2)
    line(d,[(118,57),(124,72),(118,89),(124,106)],a+(180,),1.4)
    line(d,[(138,57),(132,72),(138,89),(132,106)],a+(180,),1.4)
    ellipse(d,(122,174,134,186),fill=a+(255,))
    for y in (192,200,208,216): line(d,[(121,y),(135,y-2)],a+(160,),1)

def draw_noct(maskd):
    poly(maskd,[(124,25),(132,14),(136,32),(134,168),(128,182),(120,168),(119,54)])
    poly(maskd,[(119,54),(111,67),(116,78),(111,91),(119,103)])
    poly(maskd,[(84,174),(111,162),(124,174),(112,185),(91,184),(73,177)])
    poly(maskd,[(172,174),(145,162),(132,174),(144,185),(165,184),(183,177)])
    poly(maskd,[(121,181),(135,181),(135,228),(121,228)])
    poly(maskd,[(118,228),(138,228),(145,237),(136,245),(120,245),(111,237)])

def det_noct(d,a):
    line(d,[(128,29),(128,168)],a+(235,),1.5)
    for y in (65,92,119,146):
        line(d,[(122,y),(128,y-7),(134,y)],a+(170,),1)
    ellipse(d,(120,169,136,185),fill=a+(220,))
    line(d,[(120,193),(136,191)],a+(150,),1)
    line(d,[(120,205),(136,203)],a+(150,),1)

def draw_bow(maskd):
    line(maskd,[(103,24),(91,42),(82,65),(79,90),(88,111),(107,126)],255,8)
    line(maskd,[(107,130),(88,145),(79,166),(82,191),(91,214),(103,232)],255,8)
    line(maskd,[(103,24),(112,32),(116,45)],255,5)
    line(maskd,[(103,232),(112,224),(116,211)],255,5)
    poly(maskd,[(103,113),(118,113),(121,143),(116,154),(106,154),(101,143)])
    line(maskd,[(111,31),(154,128),(111,225)],255,2)

def det_bow(d,a):
    ellipse(d,(104,120,118,134),fill=a+(245,))
    line(d,[(111,31),(154,128),(111,225)],a+(200,),1)
    line(d,[(96,49),(89,82),(92,109)],a+(150,),1)
    line(d,[(92,147),(89,176),(96,207)],a+(150,),1)
    line(d,[(116,126),(146,126)],a+(150,),1)

def draw_gaia(maskd):
    poly(maskd,[(124,101),(132,101),(133,236),(123,236)])
    poly(maskd,[(128,18),(147,43),(151,69),(142,93),(128,110),(114,93),(105,69),(109,43)])
    poly(maskd,[(116,92),(93,102),(104,112),(123,105)])
    poly(maskd,[(140,92),(163,102),(152,112),(133,105)])
    poly(maskd,[(120,234),(136,234),(141,242),(134,248),(122,248),(115,242)])

def det_gaia(d,a):
    line(d,[(128,26),(128,104)],a+(225,),2)
    line(d,[(128,48),(115,67),(128,83),(141,67),(128,48)],a+(170,),1)
    for y in (123,145,167,189,211):
        line(d,[(123,y),(133,y-3)],a+(130,),1)
    line(d,[(105,103),(119,99)],a+(140,),1)
    line(d,[(151,103),(137,99)],a+(140,),1)

def draw_astral(maskd):
    poly(maskd,[(82,41),(95,52),(104,78),(101,116),(92,151),(82,171),(75,151),(78,116),(72,81)])
    poly(maskd,[(174,41),(161,52),(152,78),(155,116),(164,151),(174,171),(181,151),(178,116),(184,81)])
    poly(maskd,[(64,169),(83,158),(100,169),(91,179),(69,181)])
    poly(maskd,[(192,169),(173,158),(156,169),(165,179),(187,181)])
    poly(maskd,[(77,178),(88,178),(90,228),(75,228)])
    poly(maskd,[(168,178),(179,178),(181,228),(166,228)])
    ellipse(maskd,(72,225,91,244),fill=255); ellipse(maskd,(165,225,184,244),fill=255)

def det_astral(d,a):
    line(d,[(84,51),(88,150)],a+(210,),1.5)
    line(d,[(172,51),(168,150)],a+(210,),1.5)
    for x in (82,174):
        for y in (190,202,214): line(d,[(x-6,y),(x+6,y-2)],a+(140,),1)
    ellipse(d,(77,161,89,173),fill=a+(220,)); ellipse(d,(167,161,179,173),fill=a+(220,))

spec={
 'emberfall_claymore':(draw_ember,det_ember,((76,24,12),(214,96,34),(255,156,74),(255,76,18))),
 'noctis_longsword':(draw_noct,det_noct,((18,13,30),(92,62,126),(183,106,246),(173,64,255))),
 'stormpiercer_recurve_bow':(draw_bow,det_bow,((15,37,52),(80,146,172),(148,236,255),(69,206,255))),
 'gaia_war_spear':(draw_gaia,det_gaia,((29,48,20),(112,142,58),(198,230,118),(125,211,85))),
 'astral_twin_daggers':(draw_astral,det_astral,((29,17,48),(111,62,150),(227,126,255),(200,78,255))),
}

ARM={
 'phoenix':((66,18,8),(151,48,14),(255,122,30)),
 'voidwalker':((17,11,29),(59,31,86),(181,77,238)),
 'titan':((27,41,27),(70,91,48),(164,196,92)),
 'celestial':((24,43,61),(74,115,145),(158,218,244)),
 'water_sovereign':((10,44,60),(32,105,129),(77,209,236)),
}

def armor(setn, leg=False):
    base,mid,glow=ARM[setn]
    im=Image.new('RGBA',(256,128),base+(255,)); px=im.load(); rnd=random.Random('arm355'+setn+str(leg))
    for y in range(128):
        for x in range(256):
            wave=7*math.sin((x*0.06)+(y*0.04))+4*math.sin(y*.11)
            n=rnd.randint(-4,4)
            light=max(0,1-y/128)*.17 + (x/256)*.05
            c=[]
            for i in range(3):
                v=base[i]*(1-light)+mid[i]*light+wave+n
                c.append(max(0,min(255,int(v))))
            px[x,y]=tuple(c)+(255,)
    d=ImageDraw.Draw(im,'RGBA')
    for yy in (30,62,94): d.line((0,yy,255,yy),fill=mid+(28,),width=2)
    for xx in (64,128,192): d.line((xx,0,xx,127),fill=mid+(18,),width=2)
    if setn=='phoenix':
        for x in range(24,240,48):
            d.arc((x-14,20,x+14,52),185,355,fill=glow+(150,),width=3)
            d.line((x,35,x-5,48),fill=glow+(115,),width=2); d.line((x,35,x+6,48),fill=glow+(85,),width=2)
    elif setn=='voidwalker':
        for x,y in [(28,29),(72,76),(118,37),(164,90),(210,51),(238,105)]:
            d.ellipse((x-2,y-2,x+2,y+2),fill=glow+(210,)); d.ellipse((x-5,y-5,x+5,y+5),outline=glow+(45,),width=1)
        d.arc((92,30,166,101),30,150,fill=glow+(80,),width=2)
    elif setn=='titan':
        for x in range(24,240,54):
            d.line((x,25,x+9,35),fill=glow+(105,),width=2); d.line((x+9,35,x,45),fill=glow+(105,),width=2)
            d.line((x,45,x-9,35),fill=glow+(75,),width=2); d.line((x-9,35,x,25),fill=glow+(75,),width=2)
    elif setn=='celestial':
        for x,y in [(24,33),(61,91),(105,47),(145,27),(186,75),(229,43)]:
            d.line((x-5,y,x+5,y),fill=glow+(145,),width=1); d.line((x,y-5,x,y+5),fill=glow+(145,),width=1)
            d.point((x,y),fill=(245,255,255,255))
    else:
        for x in range(12,252,40):
            d.arc((x-15,33,x+15,65),15,165,fill=glow+(140,),width=2)
            d.arc((x-15,61,x+15,93),195,345,fill=glow+(80,),width=2)
    im=im.resize((64,32),Image.Resampling.LANCZOS)
    return im

def armor_icon(setn,piece):
    base,mid,glow=ARM[setn]
    C=256
    im=Image.new('RGBA',(C,C),(0,0,0,0)); d=ImageDraw.Draw(im,'RGBA')
    fill=base+(255,); edge=mid+(255,); hi=glow+(245,)
    m=Image.new('L',(C,C),0); md=ImageDraw.Draw(m)
    if piece=='helmet':
        md.polygon([(68,70),(92,48),(164,48),(188,70),(178,150),(158,176),(98,176),(78,150)],fill=255)
        if setn in ('phoenix','voidwalker'): md.polygon([(76,66),(52,35),(90,56)],fill=255); md.polygon([(180,66),(204,35),(166,56)],fill=255)
    elif piece=='chest':
        md.polygon([(42,78),(80,48),(176,48),(214,78),(192,196),(64,196)],fill=255)
        md.polygon([(42,78),(16,104),(58,118)],fill=255);md.polygon([(214,78),(240,104),(198,118)],fill=255)
    elif piece=='legs':
        md.polygon([(64,52),(192,52),(184,112),(166,218),(118,218),(112,124),(90,218),(44,218),(68,112)],fill=255)
    else:
        md.polygon([(50,74),(104,74),(102,182),(42,214),(28,194)],fill=255); md.polygon([(152,74),(206,74),(228,194),(214,214),(154,182)],fill=255)
    glowm=m.filter(ImageFilter.GaussianBlur(16)); g=Image.new('RGBA',(C,C),glow+(0,)); g.putalpha(glowm.point(lambda p:min(115,p//2))); im=Image.alpha_composite(im,g)
    body=Image.new('RGBA',(C,C),fill); body.putalpha(m); im=Image.alpha_composite(im,body)
    ring=ImageChops.subtract(m.filter(ImageFilter.MaxFilter(9)),m.filter(ImageFilter.MinFilter(7))); eim=Image.new('RGBA',(C,C),mid+(0,)); eim.putalpha(ring); im=Image.alpha_composite(im,eim)
    d=ImageDraw.Draw(im,'RGBA')
    if piece=='helmet':
        d.polygon([(86,100),(170,100),(156,132),(128,145),(100,132)],fill=(10,10,15,220),outline=hi)
        d.line((128,62,128,96),fill=hi,width=5)
    elif piece=='chest':
        d.polygon([(128,72),(150,105),(128,160),(106,105)],outline=hi,fill=mid+(110,))
        d.line((80,92,110,112),fill=edge,width=5); d.line((176,92,146,112),fill=edge,width=5)
    elif piece=='legs':
        d.line((128,62,128,122),fill=hi,width=5); d.line((80,92,112,110),fill=edge,width=4); d.line((176,92,144,110),fill=edge,width=4)
    else:
        d.line((52,112,95,102),fill=hi,width=4);d.line((204,112,161,102),fill=hi,width=4)
    if setn=='phoenix':
        d.arc((95,110,161,180),190,350,fill=hi,width=5)
    elif setn=='voidwalker':
        d.ellipse((120,108,136,124),fill=hi)
    elif setn=='titan':
        d.rectangle((116,108,140,132),outline=hi,width=4)
    elif setn=='celestial':
        d.line((116,120,140,120),fill=hi,width=4);d.line((128,108,128,132),fill=hi,width=4)
    else:
        d.arc((104,112,152,148),10,170,fill=hi,width=4)
    return im.resize((64,64),Image.Resampling.LANCZOS)

def generate(outdir):
    global OUT
    OUT=Path(outdir); OUT.mkdir(parents=True,exist_ok=True)
    for name,(shape,detail,pal) in spec.items():
        img,mask=metal_sprite(name,shape,pal)
        img=add_details(img,name,pal[3],detail)
        streak=Image.new('RGBA',(WS,HS),(255,255,255,0)); sd=ImageDraw.Draw(streak)
        sd.line(up([(98,45),(145,205)]),fill=(255,255,255,42),width=2*S)
        streak.putalpha(ImageChops.multiply(streak.getchannel('A'),mask))
        img=Image.alpha_composite(img,streak).resize((W,H),Image.Resampling.LANCZOS)
        img.save(OUT/f'{name}.png')
    for setn in ARM:
        armor(setn,False).save(OUT/f'{setn}_1.png')
        armor(setn,True).save(OUT/f'{setn}_2.png')
        for piece in ('helmet','chest','legs','boots'):
            armor_icon(setn,piece).save(OUT/f'icon_{setn}_{piece}.png')
    return OUT

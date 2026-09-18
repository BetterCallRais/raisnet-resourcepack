from pathlib import Path

src=Path(".build/build_v220.py").read_text(encoding="utf-8")
src=src.replace("LegendaryRais-Java-26plus-v2.2.0-FIX.zip","LegendaryRais-Java-26plus-v2.4.0-FINAL.zip")
src=src.replace("LegendaryRais-Java-26plus-v2.2.0-FIX.sha1","LegendaryRais-Java-26plus-v2.4.0-FINAL.sha1")
src=src.replace("generated-v220","generated-v240")
src=src.replace("v2.2.0 FIX","v2.4.0 FINAL")

# 256px material textures + 4-frame 256px animated water
for name in ["dark_metal","blue_steel","cyan_rune","soul_sand","black_wrap","bone","void"]:
    src=src.replace(f'png(texdir/"{name}.png",64,64,',f'png(texdir/"{name}.png",256,256,')
src=src.replace("f=y//64; yy=y%64","f=y//256; yy=y%256")
src=src.replace('png(texdir/"water.png",64,256,water_anim)','png(texdir/"water.png",256,1024,water_anim)')
src=src.replace("HD Soul Tide + Abyss Leviathan","FINAL 256px Soul Tide + Abyss Leviathan")

old='''# ---------------- Soul Tide Katana V5 visual rebuild ----------------
s=[]
# pommel + handle core
s += [cube([6.7,-12,6.7],[9.3,-9.8,9.3],"dark"),
      cube([7.15,-11.6,7.15],[8.85,-10.0,8.85],"cyan")]
for y in [ -9.8,-8.0,-6.2,-4.4,-2.6,-0.8,1.0,2.8,4.6 ]:
    s += [cube([6.8,y,6.8],[9.2,min(6.0,y+1.65),9.2],"wrap"),
          cube([7.25,y,7.25],[8.75,min(6.0,y+1.65),8.75],"dark")]
    if y<4:
        s += [cube([6.5,y+.25,6.55],[9.5,y+.58,9.45],"cyan",([8,y+.42,8],"z",22.5 if int(y*10)%2==0 else -22.5))]
# 3D tsuba + soul sand spikes
s += [cube([2.4,5.6,5.6],[13.6,7.0,10.4],"dark"),
      cube([3.2,5.3,6.25],[12.8,7.3,9.75],"sand"),
      cube([5.0,5.55,5.35],[11.0,7.05,10.65],"steel"),
      cube([6.2,5.15,6.3],[9.8,7.5,9.7],"cyan")]
for side in (-1,1):
    x=8+side*5.2
    s += [cube([x-.55,4.7,7.0],[x+.55,7.1,9.0],"sand",([x,6.0,8],"z",22.5*side)),
          cube([x-.35,5.0,6.6],[x+.35,6.2,7.2],"cyan")]
# curved layered blade
for yi in range(7,31):
    t=(yi-7)/24.0
    center=8.0 + 1.55*(t**1.55)
    width=2.45*(1-t)+.72*t
    y2=min(32,yi+1.08)
    s += [cube([center-width,yi,7.08],[center+width,y2,8.92],"water"),
          cube([center-width-.34,yi,7.26],[center-width,y2,8.74],"cyan"),
          cube([center+width,yi,7.26],[center+width+.34,y2,8.74],"steel"),
          cube([center-.38,yi,6.72],[center+.38,y2,7.08],"dark")]
    if yi%3==0:
        s += [cube([center-.23,yi+.16,6.30],[center+.23,min(32,yi+.82),6.72],"cyan"),
              cube([center-width*.56,yi+.22,8.92],[center-width*.18,min(32,yi+.76),9.18],"water")]
# tip
s += [cube([8.95,30.6,7.25],[10.25,32,8.75],"cyan"),
      cube([9.35,31.0,7.45],[10.05,32,8.55],"water")]
wr(Path("assets/legendaryrais/models/item/soul_tide_katana.json"),json.dumps(mdl(s),separators=(",",":")))
'''

new='''# ---------------- Soul Tide Katana V6 FINAL 256px ----------------
s=[]
# slim black tsuka + cyan soul gem pommel
s += [cube([6.72,-12,6.72],[9.28,-9.65,9.28],"dark"),
      cube([7.05,-11.72,7.05],[8.95,-10.12,8.95],"cyan"),
      cube([7.42,-12.45,7.42],[8.58,-11.70,8.58],"steel")]
for n in range(16):
    y=-9.70+n*.92
    y2=min(5.10,y+.82)
    s += [cube([6.92,y,6.92],[9.08,y2,9.08],"wrap"),
          cube([7.28,y+.08,7.28],[8.72,y2-.06,8.72],"dark")]
    if n%2==0:
        s += [cube([6.58,y+.18,6.62],[9.42,min(5.1,y+.43),9.38],"cyan",([8,y+.31,8],"z",22.5 if n%4==0 else -22.5))]

# elegant compact tsuba, not a giant block
s += [cube([3.70,5.00,6.45],[12.30,6.05,9.55],"dark"),
      cube([4.35,4.78,6.82],[11.65,6.28,9.18],"steel"),
      cube([5.20,4.60,7.10],[10.80,6.42,8.90],"sand"),
      cube([6.15,4.42,6.55],[9.85,6.65,9.45],"cyan")]
for side in (-1,1):
    x=8+side*4.25
    s += [cube([x-.46,4.64,7.12],[x+.46,6.36,8.88],"steel",([x,5.5,8],"z",22.5*side)),
          cube([x-.27,4.86,6.74],[x+.27,5.86,7.18],"cyan")]

# long blue katana blade: slim, curved, continuous taper, needle-like kissaki
segments=50
for n in range(segments):
    yi=6.25+n*.505
    if yi>=31.75: break
    t=n/(segments-1)
    center=8.0 + 2.05*(t**1.58)
    # wide at habaki, very narrow at kissaki
    width=1.78*(1-t)+0.18*t
    thick=0.78*(1-t)+0.50*t
    y2=min(32.0,yi+.54)

    # animated ocean-blue core
    s += [cube([center-width,yi,8-thick],[center+width,y2,8+thick],"water")]
    # bright cyan cutting edge on the curved/front side
    s += [cube([center-width-.24,yi,7.58],[center-width,y2,8.42],"cyan")]
    # dark blue-steel mune/spine
    s += [cube([center+width,yi,7.62],[center+width+.25,y2,8.38],"steel")]
    # narrow black dorsal ridge adds depth
    s += [cube([center-.20,yi,7.18],[center+.20,y2,7.46],"dark")]

    # luminous hamon / soul current pattern
    if n%2==0:
        wave=.30*math.sin(n*.72)
        hx=center-width*.42+wave
        s += [cube([hx-.12,yi+.08,8.46],[hx+.18,min(32,yi+.38),8.70],"cyan")]
    if n%5==0:
        # soul droplets/runes along flat of blade
        rx=center+.15*math.sin(n)
        s += [cube([rx-.13,yi+.12,6.86],[rx+.13,min(32,yi+.42),7.18],"cyan")]

# very sharp final kissaki
s += [cube([9.72,31.18,7.50],[10.45,31.72,8.50],"water"),
      cube([10.05,31.68,7.68],[10.32,32.00,8.32],"cyan"),
      cube([9.88,31.45,7.20],[10.35,31.92,7.50],"steel")]

wr(Path("assets/legendaryrais/models/item/soul_tide_katana.json"),json.dumps(mdl(s),separators=(",",":")))
'''

if old not in src:
    raise RuntimeError("Soul Tide source block not found")
src=src.replace(old,new)
exec(compile(src,"build_v240_generated.py","exec"),{})

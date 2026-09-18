package id.raisnet.legendaryrais;

import net.kyori.adventure.text.Component;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.scheduler.BukkitRunnable;
import org.bukkit.util.Vector;
import java.util.*;

final class Skills {
 private final LegendaryRais pl;
 private final Map<UUID,Map<String,Long>> cd=new HashMap<>();
 private final Map<String,Long> debounce=new HashMap<>();
 private final Map<UUID,Integer> soulGauge=new HashMap<>(),abyssGauge=new HashMap<>();
 private final Map<UUID,Integer> marks=new HashMap<>();
 private static final Particle.DustOptions CYAN=new Particle.DustOptions(Color.fromRGB(35,225,255),1.35f);
 private static final Particle.DustOptions DEEP=new Particle.DustOptions(Color.fromRGB(15,95,210),1.25f);
 private static final Particle.DustOptions VOID=new Particle.DustOptions(Color.fromRGB(90,25,150),1.20f);
 Skills(LegendaryRais p){pl=p;}

 boolean soulUltimateReady(Player p){return soulGauge.getOrDefault(p.getUniqueId(),0)>=100;}
 boolean abyssUltimateReady(Player p){return abyssGauge.getOrDefault(p.getUniqueId(),0)>=100;}

 private boolean cast(Player p,String k){
  long n=System.currentTimeMillis(); String dk=p.getUniqueId()+":"+k;
  if(n-debounce.getOrDefault(dk,0L)<220)return false; debounce.put(dk,n);
  long until=cd.computeIfAbsent(p.getUniqueId(),x->new HashMap<>()).getOrDefault(k,0L);
  if(until>n){bar(p,"✖ "+k+" • "+String.format(Locale.US,"%.1f",(until-n)/1000d)+"s lagi");return false;}
  cd.get(p.getUniqueId()).put(k,n+Math.max(5,pl.getConfig().getInt("cooldown-seconds",30))*1000L);
  bar(p,"✦ "+k+" • CAST");
  return true;
 }
 private String left(Player p,String k){
  long r=cd.getOrDefault(p.getUniqueId(),Map.of()).getOrDefault(k,0L)-System.currentTimeMillis();
  return r<=0?"READY":String.format(Locale.US,"%.1fs",r/1000d);
 }
 void status(Player p){
  boolean s=pl.soul(p); int g=s?soulGauge.getOrDefault(p.getUniqueId(),0):abyssGauge.getOrDefault(p.getUniqueId(),0);
  if(s)bar(p,"SOUL TIDE | S1 "+left(p,"Abyssal Step")+" | S2 "+left(p,"Tidal Crescent")+" | S3 "+left(p,"Soul Undertow")+" | ULT "+left(p,"Drowned Domain")+" | "+g+"%");
  else bar(p,"LEVIATHAN | S1 "+left(p,"Abyssal Harpoon")+" | S2 "+left(p,"Leviathan Fang")+" | S3 "+left(p,"Maelstrom Prison")+" | ULT "+left(p,"Wrath Leviathan")+" | "+g+"%");
 }
 private void bar(Player p,String s){try{p.sendActionBar(Component.text(s));}catch(Throwable x){p.sendMessage(s);}}
 private int fxCount(int base){
  double m=Math.max(1.0,pl.getConfig().getDouble("effects.java.particle-multiplier",1.85));
  return Math.max(1,(int)Math.round(base*m));
 }
 private void part(World w,String n,Location l,int c,double ox,double oy,double oz,double sp){
  int count=fxCount(c);
  try{w.spawnParticle(Particle.valueOf(n),l,count,ox,oy,oz,sp);}catch(Throwable x){try{w.spawnParticle(Particle.SOUL,l,count,ox,oy,oz,sp);}catch(Throwable ignored){}}
 }
 private void dust(World w,Location l,int c,double ox,double oy,double oz,Particle.DustOptions d){
  try{w.spawnParticle(Particle.DUST,l,fxCount(c),ox,oy,oz,0,d);}catch(Throwable ignored){}
 }
 private void sound(World w,String n,Location l,float v,float pitch){try{w.playSound(l,Sound.valueOf(n),v,pitch);}catch(Throwable ignored){}}
 private void ring(World w,Location c,String p,double r,int pts,double phase){
  for(int i=0;i<pts;i++){double a=phase+Math.PI*2*i/pts;part(w,p,c.clone().add(Math.cos(a)*r,.08,Math.sin(a)*r),2,.04,.04,.04,.01);}
 }
 private void waterRing(World w,Location c,double r,int pts,double phase,boolean abyss){
  for(int i=0;i<pts;i++){
   double a=phase+Math.PI*2*i/pts; Location q=c.clone().add(Math.cos(a)*r,.08,Math.sin(a)*r);
   dust(w,q,2,.035,.035,.035,abyss?DEEP:CYAN);
   part(w,"SPLASH",q,2,.04,.04,.04,.02);
   if((i&3)==0)part(w,"BUBBLE_POP",q,1,.02,.02,.02,.01);
  }
 }
 private void helix(World w,Location c,double radius,double height,double phase,boolean abyss){
  for(int i=0;i<18;i++){
   double a=phase+i*.55; double y=(i/17.0)*height;
   Location q=c.clone().add(Math.cos(a)*radius,y,Math.sin(a)*radius);
   dust(w,q,2,.05,.05,.05,abyss?VOID:CYAN);
   part(w,"BUBBLE_COLUMN_UP",q,2,.06,.12,.06,.03);
  }
 }
 private List<LivingEntity> mobs(Location l,double r,Player owner){
  List<LivingEntity> o=new ArrayList<>(); for(Entity e:l.getWorld().getNearbyEntities(l,r,r,r))if(e instanceof LivingEntity le&&!e.getUniqueId().equals(owner.getUniqueId()))o.add(le); return o;
 }
 private double scaledDamage(double base){
  return base*Math.max(0.0,pl.getConfig().getDouble("skills.damage-multiplier",1.30));
 }
 private void dmg(LivingEntity t,double d,Player p){try{t.damage(scaledDamage(d),p);}catch(Throwable ignored){}}
 private void waterBurst(Player p,Location l,int scale,boolean abyss){
  World w=p.getWorld();
  part(w,"SPLASH",l,45*scale,1.05,.5,1.05,.16);
  part(w,"BUBBLE_POP",l,30*scale,.9,.55,.9,.12);
  part(w,"BUBBLE_COLUMN_UP",l,26*scale,.8,.9,.8,.08);
  part(w,"DRIPPING_WATER",l,24*scale,.9,.7,.9,.05);
  dust(w,l,22*scale,.75,.5,.75,abyss?DEEP:CYAN);
  dust(w,l,10*scale,.65,.45,.65,abyss?VOID:DEEP);
  part(w,"SOUL",l,10*scale,.7,.55,.7,.035);
  waterRing(w,l,1.3+scale*.28,28+scale*4,0,abyss);
  waterRing(w,l,2.0+scale*.35,34+scale*4,.35,abyss);
  sound(w,"ITEM_TRIDENT_RIPTIDE_2",l,1.2f,abyss?.78f:1.25f);
 }
 void walkFx(Player p,Location l){
  Location f=l.clone().add(0,.03,0); World w=p.getWorld();
  part(w,"SPLASH",f,20,.62,.03,.62,.08); part(w,"BUBBLE_POP",f,14,.52,.03,.52,.05);
  dust(w,f,8,.42,.02,.42,CYAN);
  waterRing(w,f,.78,16,System.currentTimeMillis()*.004,false);
 }

 void basicHit(Player p,LivingEntity t,String id){
  Location h=t.getLocation().add(0,1,0);
  if(LegendaryRais.SOUL.equals(id)){
   soulGauge.put(p.getUniqueId(),Math.min(100,soulGauge.getOrDefault(p.getUniqueId(),0)+10));
   part(p.getWorld(),"SPLASH",h,30,.5,.6,.5,.12);part(p.getWorld(),"BUBBLE_POP",h,20,.4,.5,.4,.09);dust(p.getWorld(),h,16,.35,.45,.35,CYAN);part(p.getWorld(),"SOUL",h,8,.3,.4,.3,.02);
  }else{
   abyssGauge.put(p.getUniqueId(),Math.min(100,abyssGauge.getOrDefault(p.getUniqueId(),0)+10));
   int m=marks.getOrDefault(t.getUniqueId(),0)+1;
   dust(p.getWorld(),h,12,.35,.45,.35,DEEP);part(p.getWorld(),"SOUL_FIRE_FLAME",h,10,.4,.5,.4,.03);
   if(m>=3){marks.remove(t.getUniqueId());part(p.getWorld(),"SOUL_FIRE_FLAME",h,40,.8,.8,.8,.06);part(p.getWorld(),"BUBBLE_POP",h,40,.8,.8,.8,.13);dust(p.getWorld(),h,24,.5,.6,.5,VOID);dmg(t,4,p);}
   else marks.put(t.getUniqueId(),m);
  }
 }

 void step(Player p){
  if(!cast(p,"Abyssal Step"))return; Location o=p.getLocation().add(0,1,0);waterBurst(p,o,1,false);
  Vector d=p.getEyeLocation().getDirection().normalize(); p.setVelocity(d.multiply(1.45).setY(Math.max(.12,d.getY()*.35)));
  new BukkitRunnable(){int i=0;public void run(){if(i++>14||!p.isOnline()){cancel();return;}Location q=p.getLocation().add(0,.8,0);part(p.getWorld(),"SPLASH",q,18,.4,.38,.4,.1);dust(p.getWorld(),q,10,.28,.3,.28,CYAN);waterRing(p.getWorld(),q,.65,14,i*.35,false);for(LivingEntity t:mobs(q,1.15,p))dmg(t,4.5,p);}}.runTaskTimer(pl,0,1);
 }
 void crescent(Player p){
  if(!cast(p,"Tidal Crescent"))return; World w=p.getWorld();Location o=p.getEyeLocation();Vector f=o.getDirection().setY(0).normalize(),r=new Vector(-f.getZ(),0,f.getX());waterBurst(p,o,1,false);
  Set<UUID> hit=new HashSet<>();
  for(int i=-18;i<=18;i++){double a=i*.065;double dist=4.6;Vector v=f.clone().multiply(Math.cos(a)*dist).add(r.clone().multiply(Math.sin(a)*dist));Location q=o.clone().add(v);part(w,"SPLASH",q,6,.14,.2,.14,.06);dust(w,q,4,.08,.12,.08,CYAN);if((i&2)==0)part(w,"SOUL_FIRE_FLAME",q,2,.08,.12,.08,.015);for(LivingEntity t:mobs(q,.95,p))if(hit.add(t.getUniqueId())){dmg(t,7,p);t.setVelocity(f.clone().multiply(.55).setY(.16));}}
 }
 void undertow(Player p){
  if(!cast(p,"Soul Undertow"))return; World w=p.getWorld();Location start=p.getLocation().clone();waterBurst(p,start.clone().add(0,.4,0),2,false);
  new BukkitRunnable(){int t=0;public void run(){if(t++>=80||!p.isOnline()){cancel();return;}Location cc=p.getLocation();double r=5.5;
   for(int k=0;k<6;k++){double a=t*.23+k*Math.PI/3;double rr=r*(1-k*.09);Location q=cc.clone().add(Math.cos(a)*rr,.15+(t%14)*.10,Math.sin(a)*rr);part(w,"BUBBLE_COLUMN_UP",q,8,.18,.55,.18,.08);dust(w,q,4,.1,.24,.1,CYAN);}
   if(t%2==0){waterRing(w,cc.clone().add(0,.12,0),2.2+(t%18)*.16,30,t*.15,false);helix(w,cc.clone().add(0,.1,0),2.6,3.7,t*.17,false);}
   for(LivingEntity x:mobs(cc,r,p)){Vector in=cc.toVector().subtract(x.getLocation().toVector());if(in.lengthSquared()>.01)in.normalize();x.setVelocity(x.getVelocity().multiply(.25).add(in.multiply(.22)).setY(.24));x.setFallDistance(0);if(t%20==0)dmg(x,1.5,p);}
  }}.runTaskTimer(pl,0,1);
 }
 void domain(Player p){
  int g=soulGauge.getOrDefault(p.getUniqueId(),0);if(g<100){bar(p,"ULT belum siap • Soul Gauge "+g+"%");return;}if(!cast(p,"Drowned Domain"))return;soulGauge.put(p.getUniqueId(),0);
  World w=p.getWorld();Location c=p.getLocation().clone();waterBurst(p,c,3,false);
  new BukkitRunnable(){int t=0;public void run(){
   if(t++>=130){
    for(LivingEntity x:mobs(c,7.5,p)){dmg(x,8,p);Vector v=x.getLocation().toVector().subtract(c.toVector());if(v.lengthSquared()>.01)v.normalize();x.setVelocity(v.multiply(.85).setY(.65));}
    waterBurst(p,c,5,false);for(int rr=1;rr<=6;rr++)waterRing(w,c,rr,36,rr*.22,false);cancel();return;
   }
   if((t&1)==0){double r1=1.5+(t%38)*.14;waterRing(w,c.clone().add(0,.08,0),r1,38,t*.15,false);waterRing(w,c.clone().add(0,1.2,0),6.2,34,-t*.11,false);helix(w,c.clone().add(0,.1,0),3.8,5.0,t*.13,false);}
   if(t%6==0)part(w,"FALLING_WATER",c.clone().add(0,3,0),55,6,2,6,.05);
   for(LivingEntity x:mobs(c,7,p)){Vector v=c.toVector().subtract(x.getLocation().toVector());if(v.lengthSquared()>.01)v.normalize();x.setVelocity(v.multiply(.18).setY(.13));}
  }}.runTaskTimer(pl,0,1);
 }

 void harpoon(Player p){
  if(!cast(p,"Abyssal Harpoon"))return; World w=p.getWorld();Location o=p.getEyeLocation();Vector d=o.getDirection().normalize();waterBurst(p,o,1,true);Set<UUID> hit=new HashSet<>();
  for(double n=.5;n<=16;n+=.35){Location q=o.clone().add(d.clone().multiply(n));part(w,"SOUL_FIRE_FLAME",q,4,.09,.09,.09,.015);part(w,"BUBBLE_POP",q,5,.1,.1,.1,.045);dust(w,q,3,.06,.06,.06,DEEP);
   if(((int)(n*10))%10<4)waterRing(w,q,.36,10,n*.2,true);
   for(LivingEntity x:mobs(q,.78,p))if(hit.add(x.getUniqueId())){dmg(x,7,p);Vector pull=p.getLocation().toVector().subtract(x.getLocation().toVector());if(pull.lengthSquared()>.01)x.setVelocity(pull.normalize().multiply(.75).setY(.18));return;}}
 }
 void fang(Player p){
  if(!cast(p,"Leviathan Fang"))return;World w=p.getWorld();Location o=p.getLocation().add(0,1,0);Vector f=p.getEyeLocation().getDirection().setY(0).normalize(),r=new Vector(-f.getZ(),0,f.getX());waterBurst(p,o,2,true);Set<UUID> h=new HashSet<>();
  for(double dist=1;dist<7;dist+=.4)for(int side=-3;side<=3;side++){Location q=o.clone().add(f.clone().multiply(dist)).add(r.clone().multiply(side*dist*.15));part(w,"SOUL_FIRE_FLAME",q,3,.1,.2,.1,.02);part(w,"SPLASH",q,3,.1,.15,.1,.05);dust(w,q,3,.08,.12,.08,side%2==0?DEEP:VOID);for(LivingEntity x:mobs(q,.9,p))if(h.add(x.getUniqueId())){dmg(x,8,p);x.setVelocity(f.clone().multiply(.58).setY(.2));}}
 }
 void maelstrom(Player p){
  if(!cast(p,"Maelstrom Prison"))return;World w=p.getWorld();Location c=p.getLocation().add(p.getEyeLocation().getDirection().setY(0).normalize().multiply(6));waterBurst(p,c,3,true);
  new BukkitRunnable(){int t=0;public void run(){if(t++>=105){waterBurst(p,c,4,true);for(LivingEntity x:mobs(c,6,p)){dmg(x,5,p);x.setVelocity(new Vector(0,.75,0));}cancel();return;}
   for(int k=0;k<7;k++){double a=t*.23+k*Math.PI*2/7;double r=5.8-(k*.5);Location q=c.clone().add(Math.cos(a)*r,(t%20)*.09,Math.sin(a)*r);part(w,"BUBBLE_COLUMN_UP",q,8,.18,.5,.18,.08);dust(w,q,4,.12,.26,.12,(k&1)==0?DEEP:VOID);}
   if((t&1)==0){waterRing(w,c.clone().add(0,.1,0),2.4+(t%20)*.15,32,t*.17,true);helix(w,c.clone().add(0,.1,0),3.0,4.6,t*.15,true);}
   for(LivingEntity x:mobs(c,6,p)){Vector in=c.toVector().subtract(x.getLocation().toVector());double dist=Math.max(.1,in.length());if(in.lengthSquared()>.01)in.normalize();Vector tan=new Vector(-in.getZ(),0,in.getX());x.setVelocity(in.multiply(.18+.02*dist).add(tan.multiply(.22)).setY(.11));if(t%20==0)dmg(x,1.4,p);}
  }}.runTaskTimer(pl,0,1);
 }
 void wrath(Player p){
  int g=abyssGauge.getOrDefault(p.getUniqueId(),0);if(g<100){bar(p,"ULT belum siap • Abyss Gauge "+g+"%");return;}if(!cast(p,"Wrath Leviathan"))return;abyssGauge.put(p.getUniqueId(),0);
  World w=p.getWorld();Location o=p.getEyeLocation().clone();Vector d=o.getDirection().normalize();waterBurst(p,o,4,true);
  new BukkitRunnable(){int t=0;Set<UUID> h=new HashSet<>();public void run(){
   if(t++>38){Location c=o.clone().add(d.clone().multiply(20));waterBurst(p,c,6,true);for(int rr=1;rr<=7;rr++)waterRing(w,c,rr,40,rr*.3,true);helix(w,c,5.2,7.0,t*.2,true);
    for(LivingEntity x:mobs(c,7,p)){dmg(x,10,p);Vector v=x.getLocation().toVector().subtract(c.toVector());if(v.lengthSquared()>.01)v.normalize();x.setVelocity(v.multiply(.95).setY(.65));}cancel();return;}
   Location head=o.clone().add(d.clone().multiply(t*.55));part(w,"SOUL_FIRE_FLAME",head,28,.9,.9,.9,.07);part(w,"BUBBLE_POP",head,32,1.0,1.0,1.0,.13);dust(w,head,18,.65,.65,.65,DEEP);dust(w,head,10,.55,.55,.55,VOID);waterRing(w,head,1.7,24,t*.24,true);
   for(int j=1;j<=3;j++){Location jaw=head.clone().add(0,j*.45,0);waterRing(w,jaw,1.15+j*.22,18,t*.18+j,true);}
   for(LivingEntity x:mobs(head,2.2,p))if(h.add(x.getUniqueId())){dmg(x,9,p);x.setVelocity(d.clone().multiply(.85).setY(.28));}
  }}.runTaskTimer(pl,0,1);
 }
}

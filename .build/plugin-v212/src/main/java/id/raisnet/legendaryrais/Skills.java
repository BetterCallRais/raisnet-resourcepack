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
 Skills(LegendaryRais p){pl=p;}

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
 private void part(World w,String n,Location l,int c,double ox,double oy,double oz,double sp){
  try{w.spawnParticle(Particle.valueOf(n),l,c,ox,oy,oz,sp);}catch(Throwable x){try{w.spawnParticle(Particle.SOUL,l,c,ox,oy,oz,sp);}catch(Throwable ignored){}}
 }
 private void sound(World w,String n,Location l,float v,float pitch){try{w.playSound(l,Sound.valueOf(n),v,pitch);}catch(Throwable ignored){}}
 private void ring(World w,Location c,String p,double r,int pts,double phase){
  for(int i=0;i<pts;i++){double a=phase+Math.PI*2*i/pts;part(w,p,c.clone().add(Math.cos(a)*r,.08,Math.sin(a)*r),2,.04,.04,.04,.01);}
 }
 private List<LivingEntity> mobs(Location l,double r,Player owner){
  List<LivingEntity> o=new ArrayList<>(); for(Entity e:l.getWorld().getNearbyEntities(l,r,r,r))if(e instanceof LivingEntity le&&!e.getUniqueId().equals(owner.getUniqueId()))o.add(le); return o;
 }
 private void dmg(LivingEntity t,double d,Player p){try{t.damage(d,p);}catch(Throwable ignored){}}
 private void waterBurst(Player p,Location l,int scale){
  World w=p.getWorld(); part(w,"SPLASH",l,30*scale,.8,.35,.8,.12);part(w,"BUBBLE_POP",l,24*scale,.7,.4,.7,.10);
  part(w,"BUBBLE_COLUMN_UP",l,18*scale,.6,.7,.6,.06);part(w,"SOUL",l,12*scale,.65,.55,.65,.035);part(w,"SOUL_FIRE_FLAME",l,8*scale,.5,.45,.5,.025);
  ring(w,l,"SPLASH",1.15+scale*.2,18,0);sound(w,"ITEM_TRIDENT_RIPTIDE_2",l,1f,1.2f);
 }
 void walkFx(Player p,Location l){
  Location f=l.clone().add(0,.06,0); World w=p.getWorld();
  part(w,"SPLASH",f,16,.58,.04,.58,.06); part(w,"BUBBLE_POP",f,12,.52,.03,.52,.05); part(w,"BUBBLE_COLUMN_UP",f,10,.42,.04,.42,.04);
  part(w,"SOUL",f,6,.4,.06,.4,.015); ring(w,f,"SPLASH",.72,14,System.currentTimeMillis()*.003);
 }

 void basicHit(Player p,LivingEntity t,String id){
  Location h=t.getLocation().add(0,1,0);
  if(LegendaryRais.SOUL.equals(id)){
   soulGauge.put(p.getUniqueId(),Math.min(100,soulGauge.getOrDefault(p.getUniqueId(),0)+8));
   part(p.getWorld(),"SPLASH",h,22,.4,.5,.4,.1);part(p.getWorld(),"BUBBLE_POP",h,15,.35,.45,.35,.08);part(p.getWorld(),"SOUL",h,8,.3,.4,.3,.02);
  }else{
   abyssGauge.put(p.getUniqueId(),Math.min(100,abyssGauge.getOrDefault(p.getUniqueId(),0)+8));
   int m=marks.getOrDefault(t.getUniqueId(),0)+1;
   if(m>=3){marks.remove(t.getUniqueId());part(p.getWorld(),"SOUL_FIRE_FLAME",h,35,.7,.7,.7,.05);part(p.getWorld(),"BUBBLE_POP",h,35,.7,.7,.7,.12);dmg(t,4,p);}
   else marks.put(t.getUniqueId(),m);
  }
 }

 void step(Player p){
  if(!cast(p,"Abyssal Step"))return; Location o=p.getLocation().add(0,1,0);waterBurst(p,o,1);
  Vector d=p.getEyeLocation().getDirection().normalize(); p.setVelocity(d.multiply(1.45).setY(Math.max(.12,d.getY()*.35)));
  new BukkitRunnable(){int i=0;public void run(){if(i++>12||!p.isOnline()){cancel();return;}Location q=p.getLocation().add(0,.8,0);part(p.getWorld(),"SPLASH",q,14,.35,.35,.35,.08);part(p.getWorld(),"SOUL",q,8,.3,.3,.3,.03);for(LivingEntity t:mobs(q,1.15,p))dmg(t,4.5,p);}}.runTaskTimer(pl,0,1);
 }
 void crescent(Player p){
  if(!cast(p,"Tidal Crescent"))return; World w=p.getWorld();Location o=p.getEyeLocation();Vector f=o.getDirection().setY(0).normalize(),r=new Vector(-f.getZ(),0,f.getX());waterBurst(p,o,1);
  Set<UUID> hit=new HashSet<>();
  for(int i=-12;i<=12;i++){double a=i*.075;Vector v=f.clone().multiply(Math.cos(a)*4.3).add(r.clone().multiply(Math.sin(a)*4.3));Location q=o.clone().add(v);part(w,"SPLASH",q,5,.12,.18,.12,.05);part(w,"SOUL_FIRE_FLAME",q,2,.08,.12,.08,.015);for(LivingEntity t:mobs(q,.9,p))if(hit.add(t.getUniqueId())){dmg(t,7,p);t.setVelocity(f.clone().multiply(.55).setY(.16));}}
 }
 void undertow(Player p){
  if(!cast(p,"Soul Undertow"))return; World w=p.getWorld();Location c=p.getLocation().clone();waterBurst(p,c.add(0,.4,0),2);
  new BukkitRunnable(){int t=0;public void run(){if(t++>=65||!p.isOnline()){cancel();return;}Location cc=p.getLocation();double r=5.5;
   for(int k=0;k<5;k++){double a=t*.22+k*Math.PI*2/5;Location q=cc.clone().add(Math.cos(a)*r*(1-k*.12),.2+(t%10)*.09,Math.sin(a)*r*(1-k*.12));part(w,"BUBBLE_COLUMN_UP",q,6,.15,.45,.15,.06);part(w,"SPLASH",q,4,.15,.1,.15,.05);}
   if(t%4==0)ring(w,cc.clone().add(0,.2,0),"SOUL",3.8,28,t*.14);
   for(LivingEntity x:mobs(cc,r,p)){Vector in=cc.toVector().subtract(x.getLocation().toVector());if(in.lengthSquared()>.01)in.normalize();x.setVelocity(x.getVelocity().multiply(.3).add(in.multiply(.22)).setY(.24));x.setFallDistance(0);if(t%20==0)dmg(x,1.5,p);}
  }}.runTaskTimer(pl,0,1);
 }
 void domain(Player p){
  int g=soulGauge.getOrDefault(p.getUniqueId(),0);if(g<100){bar(p,"ULT belum siap • Soul Gauge "+g+"%");return;}if(!cast(p,"Drowned Domain"))return;soulGauge.put(p.getUniqueId(),0);
  World w=p.getWorld();Location c=p.getLocation();waterBurst(p,c,3);
  new BukkitRunnable(){int t=0;public void run(){if(t++>=120){for(LivingEntity x:mobs(c,7,p)){dmg(x,8,p);Vector v=x.getLocation().toVector().subtract(c.toVector());if(v.lengthSquared()>.01)v.normalize();x.setVelocity(v.multiply(.8).setY(.55));}waterBurst(p,c,4);cancel();return;}
   ring(w,c.clone().add(0,.2,0),"SPLASH",2+(t%35)*.12,34,t*.13);ring(w,c.clone().add(0,.8,0),"SOUL_FIRE_FLAME",5.5,28,-t*.1);
   for(LivingEntity x:mobs(c,7,p)){Vector v=c.toVector().subtract(x.getLocation().toVector());if(v.lengthSquared()>.01)v.normalize();x.setVelocity(v.multiply(.18).setY(.13));}
  }}.runTaskTimer(pl,0,1);
 }

 void harpoon(Player p){
  if(!cast(p,"Abyssal Harpoon"))return; World w=p.getWorld();Location o=p.getEyeLocation();Vector d=o.getDirection().normalize();waterBurst(p,o,1);Set<UUID> hit=new HashSet<>();
  for(double n=.5;n<=15;n+=.45){Location q=o.clone().add(d.clone().multiply(n));part(w,"SOUL_FIRE_FLAME",q,3,.08,.08,.08,.01);part(w,"BUBBLE_POP",q,4,.1,.1,.1,.04);
   for(LivingEntity x:mobs(q,.75,p))if(hit.add(x.getUniqueId())){dmg(x,7,p);Vector pull=p.getLocation().toVector().subtract(x.getLocation().toVector());if(pull.lengthSquared()>.01)x.setVelocity(pull.normalize().multiply(.75).setY(.18));return;}}
 }
 void fang(Player p){
  if(!cast(p,"Leviathan Fang"))return;World w=p.getWorld();Location o=p.getLocation().add(0,1,0);Vector f=p.getEyeLocation().getDirection().setY(0).normalize(),r=new Vector(-f.getZ(),0,f.getX());waterBurst(p,o,2);Set<UUID> h=new HashSet<>();
  for(double dist=1;dist<6;dist+=.5)for(int side=-2;side<=2;side++){Location q=o.clone().add(f.clone().multiply(dist)).add(r.clone().multiply(side*dist*.18));part(w,"SOUL_FIRE_FLAME",q,4,.1,.2,.1,.02);part(w,"SPLASH",q,4,.1,.15,.1,.05);for(LivingEntity x:mobs(q,.9,p))if(h.add(x.getUniqueId())){dmg(x,8,p);x.setVelocity(f.clone().multiply(.55).setY(.18));}}
 }
 void maelstrom(Player p){
  if(!cast(p,"Maelstrom Prison"))return;World w=p.getWorld();Location c=p.getLocation().add(p.getEyeLocation().getDirection().setY(0).normalize().multiply(6));waterBurst(p,c,2);
  new BukkitRunnable(){int t=0;public void run(){if(t++>=90){waterBurst(p,c,3);for(LivingEntity x:mobs(c,6,p)){dmg(x,5,p);x.setVelocity(new Vector(0,.7,0));}cancel();return;}
   for(int k=0;k<6;k++){double a=t*.22+k*Math.PI/3;double r=5.5-(k*.55);Location q=c.clone().add(Math.cos(a)*r,(t%18)*.08,Math.sin(a)*r);part(w,"BUBBLE_COLUMN_UP",q,7,.18,.45,.18,.08);part(w,"SOUL",q,4,.15,.3,.15,.03);}
   for(LivingEntity x:mobs(c,6,p)){Vector in=c.toVector().subtract(x.getLocation().toVector());double dist=Math.max(.1,in.length());if(in.lengthSquared()>.01)in.normalize();Vector tan=new Vector(-in.getZ(),0,in.getX());x.setVelocity(in.multiply(.18+.02*dist).add(tan.multiply(.22)).setY(.10));if(t%20==0)dmg(x,1.4,p);}
  }}.runTaskTimer(pl,0,1);
 }
 void wrath(Player p){
  int g=abyssGauge.getOrDefault(p.getUniqueId(),0);if(g<100){bar(p,"ULT belum siap • Abyss Gauge "+g+"%");return;}if(!cast(p,"Wrath Leviathan"))return;abyssGauge.put(p.getUniqueId(),0);
  World w=p.getWorld();Location o=p.getEyeLocation();Vector d=o.getDirection().normalize();waterBurst(p,o,3);
  new BukkitRunnable(){int t=0;Set<UUID> h=new HashSet<>();public void run(){if(t++>30){Location c=o.clone().add(d.clone().multiply(18));waterBurst(p,c,5);for(LivingEntity x:mobs(c,7,p)){dmg(x,10,p);Vector v=x.getLocation().toVector().subtract(c.toVector());if(v.lengthSquared()>.01)v.normalize();x.setVelocity(v.multiply(.9).setY(.55));}cancel();return;}
   Location head=o.clone().add(d.clone().multiply(t*.6));part(w,"SOUL_FIRE_FLAME",head,22,.8,.8,.8,.06);part(w,"BUBBLE_POP",head,28,1,1,1,.12);ring(w,head,"SOUL",1.5,20,t*.2);
   for(LivingEntity x:mobs(head,2,p))if(h.add(x.getUniqueId())){dmg(x,9,p);x.setVelocity(d.clone().multiply(.8).setY(.25));}
  }}.runTaskTimer(pl,0,1);
 }
}

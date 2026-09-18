package id.raisnet.legendaryrais;

import net.kyori.adventure.text.Component;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.enchantments.Enchantment;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.Action;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.ProjectileLaunchEvent;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.Vector;
import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import java.lang.reflect.Method;
import java.util.*;

public final class LegendaryRais extends JavaPlugin implements Listener, CommandExecutor {
 static final String SOUL="soul_tide", LEV="abyss_leviathan";
 static final int SOUL_CMD=910041, LEV_CMD=910042;
 private NamespacedKey weaponKey;
 private Skills skills;
 private final Map<UUID,Long> walkFx=new HashMap<>();
 private final Set<UUID> tideWalking=new HashSet<>();
 private final Map<UUID,Double> tideY=new HashMap<>();
 private final Map<UUID,Float> oldWalkSpeed=new HashMap<>();
 private final Map<UUID,Boolean> oldGravity=new HashMap<>();
 private final Map<UUID,Long> lastSprint=new HashMap<>();
 private final Map<UUID,ItemDisplay> leviathanVisuals=new HashMap<>();
 private static final String GUI="LegendaryRais • Weapons";

 @Override public void onEnable(){
  saveDefaultConfig(); weaponKey=new NamespacedKey(this,"weapon_id"); skills=new Skills(this);
  getServer().getPluginManager().registerEvents(this,this);
  Objects.requireNonNull(getCommand("riswp")).setExecutor(this);
  Bukkit.getScheduler().runTaskTimer(this,this::tickSystems,1L,1L);
  getLogger().info("LegendaryRais 2.4.0-FINAL enabled");
 }

 @Override public void onDisable(){
  for(Player p:Bukkit.getOnlinePlayers()) stopTideWalk(p);
  for(ItemDisplay d:new ArrayList<>(leviathanVisuals.values())) if(d!=null&&d.isValid()) d.remove();
  leviathanVisuals.clear();
 }

 @Override public boolean onCommand(CommandSender s,Command c,String l,String[] a){
  if(!(s instanceof Player p)) return true;
  if(!p.isOp()&&!p.hasPermission("legendaryrais.admin")){p.sendMessage("§c/riswp hanya untuk operator.");return true;}
  Inventory inv=Bukkit.createInventory(null,27,GUI);
  inv.setItem(11,soulItem()); inv.setItem(15,levItem()); p.openInventory(inv); return true;
 }

 @EventHandler public void guiClick(InventoryClickEvent e){
  if(!GUI.equals(e.getView().getTitle()))return; e.setCancelled(true);
  if(!(e.getWhoClicked() instanceof Player p)||e.getCurrentItem()==null)return;
  if(!p.isOp()&&!p.hasPermission("legendaryrais.admin"))return;
  if(e.getSlot()==11){p.getInventory().addItem(soulItem());p.closeInventory();}
  if(e.getSlot()==15){p.getInventory().addItem(levItem());p.closeInventory();}
 }

 ItemStack soulItem(){
  ItemStack i=new ItemStack(Material.NETHERITE_SWORD); ItemMeta m=i.getItemMeta();
  m.displayName(Component.text("§b§lSoul Tide Katana §3V4"));
  m.lore(List.of(Component.text("§7LegendaryRais • Water Soul"),Component.text("§bPassive: Soul Tidewalker"),Component.text("§fS1 Right Click • Abyssal Step"),Component.text("§fS2 Sneak+Left • Tidal Crescent"),Component.text("§fS3 Sneak+Right • Soul Undertow"),Component.text("§bULT Sprint → Sneak+Right @ 100%")));
  finishMeta(m,SOUL,SOUL_CMD,"soultide:soul_tide_katana"); i.setItemMeta(m); return i;
 }
 ItemStack levItem(){
  ItemStack i=new ItemStack(Material.TRIDENT); ItemMeta m=i.getItemMeta();
  m.displayName(Component.text("§3§lAbyss Leviathan Trident §8V3"));
  m.lore(List.of(Component.text("§7LegendaryRais • Dark Abyss"),Component.text("§3Passive: Sovereign of the Abyss"),Component.text("§fS1 Right Click • Abyssal Harpoon"),Component.text("§fS2 Sneak+Left • Leviathan Fang"),Component.text("§fS3 Sneak+Right • Maelstrom Prison"),Component.text("§3ULT Sprint → Sneak+Right @ 100%")));
  try{m.addEnchant(Enchantment.LOYALTY,3,true);}catch(Throwable ignored){}
  finishMeta(m,LEV,LEV_CMD,"legendaryrais:abyss_leviathan_trident"); i.setItemMeta(m); return i;
 }
 private void finishMeta(ItemMeta m,String id,int cmd,String model){
  m.setUnbreakable(true); m.getPersistentDataContainer().set(weaponKey,PersistentDataType.STRING,id);
  try{m.setCustomModelData(cmd);}catch(Throwable ignored){}
  try{
   Method get=m.getClass().getMethod("getCustomModelDataComponent"); Object comp=get.invoke(m);
   comp.getClass().getMethod("setFloats",List.class).invoke(comp,List.of((float)cmd));
   try{comp.getClass().getMethod("setStrings",List.class).invoke(comp,List.of(model));}catch(Throwable ignored){}
   Method setter=null;
   for(Method x:m.getClass().getMethods())if(x.getName().equals("setCustomModelDataComponent")&&x.getParameterCount()==1){setter=x;break;}
   if(setter!=null)setter.invoke(m,comp);
  }catch(Throwable ignored){}
  try{m.getClass().getMethod("setItemModel",NamespacedKey.class).invoke(m,NamespacedKey.fromString(model));}catch(Throwable ignored){}
  try{m.getClass().getMethod("setEnchantmentGlintOverride",Boolean.class).invoke(m,Boolean.TRUE);}catch(Throwable ignored){}
  m.addItemFlags(ItemFlag.HIDE_UNBREAKABLE);
 }

 String weapon(ItemStack i){
  if(i==null||i.getType().isAir()||!i.hasItemMeta())return null;
  ItemMeta m=i.getItemMeta(); String id=m.getPersistentDataContainer().get(weaponKey,PersistentDataType.STRING);
  if(SOUL.equals(id)||LEV.equals(id)){repair(i,id);return id;}
  Integer cmd=null; try{if(m.hasCustomModelData())cmd=m.getCustomModelData();}catch(Throwable ignored){}
  if(cmd!=null&&cmd==SOUL_CMD){repair(i,SOUL);return SOUL;}
  if(cmd!=null&&cmd==LEV_CMD){repair(i,LEV);return LEV;}
  try{
   Object k=m.getClass().getMethod("getItemModel").invoke(m);
   if(k!=null){String s=k.toString();if(s.contains("soul_tide")){repair(i,SOUL);return SOUL;}if(s.contains("leviathan")){repair(i,LEV);return LEV;}}
  }catch(Throwable ignored){}
  String n=m.hasDisplayName()?m.getDisplayName().toLowerCase(Locale.ROOT):"";
  if(n.contains("soul tide")){repair(i,SOUL);return SOUL;}
  if(n.contains("leviathan")){repair(i,LEV);return LEV;}
  return null;
 }
 private void repair(ItemStack i,String id){
  ItemMeta m=i.getItemMeta(); if(m==null)return;
  if(SOUL.equals(id))finishMeta(m,SOUL,SOUL_CMD,"soultide:soul_tide_katana");
  else{try{m.addEnchant(Enchantment.LOYALTY,3,true);}catch(Throwable ignored){} finishMeta(m,LEV,LEV_CMD,"legendaryrais:abyss_leviathan_trident");}
  i.setItemMeta(m);
 }
 boolean soul(Player p){return SOUL.equals(weapon(p.getInventory().getItemInMainHand()));}
 boolean lev(Player p){return LEV.equals(weapon(p.getInventory().getItemInMainHand()));}

 @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
 public void interact(PlayerInteractEvent e){
  if(e.getHand()!=null&&e.getHand()!=EquipmentSlot.HAND)return;
  Player p=e.getPlayer(); String id=weapon(p.getInventory().getItemInMainHand()); if(id==null)return;
  Action a=e.getAction(); boolean r=a==Action.RIGHT_CLICK_AIR||a==Action.RIGHT_CLICK_BLOCK, l=a==Action.LEFT_CLICK_AIR||a==Action.LEFT_CLICK_BLOCK;
  if(!r&&!l)return;
  boolean ultCombo=p.isSneaking()&&recentSprint(p);
  if(SOUL.equals(id)){
   if(ultCombo&&r&&skills.soulUltimateReady(p))skills.domain(p);
   else if(p.isSneaking()&&r)skills.undertow(p);
   else if(p.isSneaking()&&l)skills.crescent(p);
   else if(r)skills.step(p);
   e.setCancelled(true);
  }else{
   if(ultCombo&&r&&skills.abyssUltimateReady(p)){skills.wrath(p);e.setCancelled(true);}
   else if(p.isSneaking()&&r){skills.maelstrom(p);e.setCancelled(true);}
   else if(p.isSneaking()&&l){skills.fang(p);e.setCancelled(true);}
   else if(r){skills.harpoon(p);}
  }
 }

 @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
 public void melee(EntityDamageByEntityEvent e){
  if(!(e.getDamager() instanceof Player p)||!(e.getEntity() instanceof LivingEntity t))return;
  String id=weapon(p.getInventory().getItemInMainHand()); if(id==null)return;
  if(p.isSneaking()){e.setCancelled(true);if(SOUL.equals(id))skills.crescent(p);else skills.fang(p);return;}
  double lethal=Math.max(40.0,getConfig().getDouble("combat.base-melee-damage",40.0));
  e.setDamage(lethal);
  skills.basicHit(p,t,id);
 }

 @EventHandler public void sprint(PlayerToggleSprintEvent e){
  if(e.isSprinting())lastSprint.put(e.getPlayer().getUniqueId(),System.currentTimeMillis());
 }
 private boolean recentSprint(Player p){
  return p.isSprinting()||System.currentTimeMillis()-lastSprint.getOrDefault(p.getUniqueId(),0L)<=1100L;
 }

 @EventHandler public void sneak(PlayerToggleSneakEvent e){if(e.isSneaking()&&(soul(e.getPlayer())||lev(e.getPlayer())))skills.status(e.getPlayer());}

 @EventHandler(ignoreCancelled=true)
 public void bedrockSwing(PlayerAnimationEvent e){
  Player p=e.getPlayer(); if(!isBedrock(p))return; String id=weapon(p.getInventory().getItemInMainHand()); if(id==null)return;
  if(p.isSneaking()){if(SOUL.equals(id))skills.crescent(p);else skills.fang(p);}
 }

 private boolean isBedrock(Player p){
  try{
   Class<?> c=Class.forName("org.geysermc.floodgate.api.FloodgateApi"); Object api=c.getMethod("getInstance").invoke(null);
   return Boolean.TRUE.equals(c.getMethod("isFloodgatePlayer",UUID.class).invoke(api,p.getUniqueId()));
  }catch(Throwable ignored){return false;}
 }

 @EventHandler(ignoreCancelled=true,priority=EventPriority.MONITOR)
 public void launched(ProjectileLaunchEvent e){
  if(!(e.getEntity() instanceof Trident tr))return;
  ItemStack stack=tr.getItemStack();
  if(!LEV.equals(weapon(stack)))return;
  for(Player viewer:Bukkit.getOnlinePlayers())viewer.hideEntity(this,tr);
  ItemDisplay d=tr.getWorld().spawn(tr.getLocation(),ItemDisplay.class);
  d.setItemStack(stack.clone());
  d.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.FIXED);
  d.setPersistent(false); d.setInvulnerable(true); d.setViewRange(2.5f);
  try{d.setInterpolationDuration(1);d.setTeleportDuration(1);}catch(Throwable ignored){}
  leviathanVisuals.put(tr.getUniqueId(),d);
 }

 @EventHandler public void onJoin(PlayerJoinEvent e){
  for(UUID id:leviathanVisuals.keySet()){
   Entity x=e.getPlayer().getWorld().getEntity(id);
   if(x!=null)e.getPlayer().hideEntity(this,x);
  }
 }

 @EventHandler(ignoreCancelled=true,priority=EventPriority.HIGHEST)
 public void waterWalk(PlayerMoveEvent e){
  Player p=e.getPlayer(); Location to=e.getTo(); if(to==null)return;
  if(!getConfig().getBoolean("water-walk.enabled",true)||!soul(p)||p.isFlying()||p.isGliding()){
   stopTideWalk(p); return;
  }

  // FINAL FIX: Soul Tide activates only on DIRECT water contact.
  // Water hidden under dirt/stone/planks will never activate it.
  if(!directWaterContact(to)){
   stopTideWalk(p); return;
  }

  double surface=directWaterSurface(to);
  if(Double.isNaN(surface)){stopTideWalk(p);return;}
  double target=surface+0.10;
  double dy=to.getY()-e.getFrom().getY();

  // Do not pull a deeply submerged player up to the surface.
  if(!tideWalking.contains(p.getUniqueId()) && Math.abs(to.getY()-target)>0.65)return;

  // Preserve normal player-controlled jumping.
  if(dy>0.055 && to.getY()>target+0.08){stopTideWalk(p);return;}

  UUID id=p.getUniqueId();
  if(!tideWalking.contains(id)){
   beginTideWalk(p,target);
   if(Math.abs(to.getY()-target)>0.055){
    Location n=to.clone(); n.setY(target); e.setTo(n);
   }
  }else{
   tideY.put(id,target);
   p.setGravity(false);
   p.setFallDistance(0f);
   try{p.setSwimming(false);}catch(Throwable ignored){}

   // Safety correction only. No constant packet snapping and NEVER X/Z steering.
   if(Math.abs(to.getY()-target)>0.38 && dy<=0.02){
    Location n=to.clone(); n.setY(target); e.setTo(n);
   }
  }

  long now=System.currentTimeMillis(),next=walkFx.getOrDefault(id,0L);
  if(getConfig().getBoolean("water-walk.effects",true)&&now>=next){
   walkFx.put(id,now+Math.max(70,getConfig().getLong("water-walk.effect-interval-ms",85)));
   skills.walkFx(p,e.getTo()==null?to:e.getTo());
  }
 }

 private boolean directWaterContact(Location l){
  World w=l.getWorld(); if(w==null)return false;
  Material feet=l.getBlock().getType();
  Material justBelow=l.clone().subtract(0,0.18,0).getBlock().getType();
  return feet==Material.WATER || justBelow==Material.WATER;
 }

 private double directWaterSurface(Location l){
  World w=l.getWorld(); if(w==null)return Double.NaN;
  Location probe=l.clone().subtract(0,0.18,0);
  int x=probe.getBlockX(), z=probe.getBlockZ();
  int y=probe.getBlockY();
  if(w.getBlockAt(x,y,z).getType()!=Material.WATER){
   y=l.getBlockY();
   if(w.getBlockAt(x,y,z).getType()!=Material.WATER)return Double.NaN;
  }
  // Only climb through contiguous water; never search downward through solid blocks.
  int top=y;
  while(top<w.getMaxHeight()-2 && w.getBlockAt(x,top+1,z).getType()==Material.WATER)top++;
  return top+1.0;
 }

 private void beginTideWalk(Player p,double y){
  UUID id=p.getUniqueId();
  if(tideWalking.add(id)){
   oldGravity.put(id,p.hasGravity());
   oldWalkSpeed.put(id,p.getWalkSpeed());
  }
  tideY.put(id,y);
  p.setGravity(false);
  p.setFallDistance(0f);
  try{p.setSwimming(false);}catch(Throwable ignored){}
 }

 private void stopTideWalk(Player p){
  UUID id=p.getUniqueId(); if(!tideWalking.remove(id))return;
  Boolean g=oldGravity.remove(id); Float s=oldWalkSpeed.remove(id); tideY.remove(id);
  if(g!=null)p.setGravity(g); else p.setGravity(true);
  if(s!=null&&Math.abs(p.getWalkSpeed()-s)>0.0001f)p.setWalkSpeed(s);
 }

 private void tickSystems(){
  // Smooth Soul Tide surface lock. No horizontal velocity or steering is ever applied.
  for(UUID id:new ArrayList<>(tideWalking)){
   Player p=Bukkit.getPlayer(id);
   if(p==null||!p.isOnline()||!soul(p)){if(p!=null)stopTideWalk(p);continue;}
   if(!directWaterContact(p.getLocation())){stopTideWalk(p);continue;}
   double surface=directWaterSurface(p.getLocation());
   if(Double.isNaN(surface)){stopTideWalk(p);continue;}
   double target=surface+0.10;
   tideY.put(id,target);
   p.setGravity(false);
   p.setFallDistance(0f);
   try{p.setSwimming(false);}catch(Throwable ignored){}

   // Rare safety correction only. X/Z remain exactly the player's current coordinates.
   if(Math.abs(p.getLocation().getY()-target)>0.42 && p.getVelocity().getY()<=0.05){
    Location n=p.getLocation().clone(); n.setY(target); p.teleport(n);
   }
  }

  // Custom flying visual for Abyss Leviathan. The real trident is hidden but still
  // handles collision, damage and Loyalty. The visible model is rotated from its
  // local +Y axis directly onto the projectile velocity, so it points forward.
  Iterator<Map.Entry<UUID,ItemDisplay>> it=leviathanVisuals.entrySet().iterator();
  while(it.hasNext()){
   Map.Entry<UUID,ItemDisplay> en=it.next(); ItemDisplay d=en.getValue();
   if(d==null||!d.isValid()){it.remove();continue;}
   Entity ent=d.getWorld().getEntity(en.getKey());
   if(!(ent instanceof Trident tr)||!tr.isValid()){
    d.remove(); it.remove(); continue;
   }
   for(Player viewer:Bukkit.getOnlinePlayers())if(viewer.getWorld().equals(tr.getWorld()))viewer.hideEntity(this,tr);

   Location l=tr.getLocation().clone();
   l.setYaw(0f); l.setPitch(0f);
   d.teleport(l);

   Vector v=tr.getVelocity();
   if(v.lengthSquared()>0.0005){
    Vector dir=v.clone().normalize();
    Quaternionf q=new Quaternionf().rotationTo(
      new Vector3f(0f,1f,0f),
      new Vector3f((float)dir.getX(),(float)dir.getY(),(float)dir.getZ())
    );
    d.setTransformation(new Transformation(
      new Vector3f(0f,0f,0f),
      q,
      new Vector3f(1f,1f,1f),
      new Quaternionf()
    ));
   }
  }
 }
}

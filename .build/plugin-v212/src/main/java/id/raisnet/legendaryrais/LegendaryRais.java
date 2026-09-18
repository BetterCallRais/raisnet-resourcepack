package id.raisnet.legendaryrais;

import net.kyori.adventure.text.Component;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.enchantments.Enchantment;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.Action;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.*;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.Vector;
import java.lang.reflect.Method;
import java.util.*;

public final class LegendaryRais extends JavaPlugin implements Listener, CommandExecutor {
 static final String SOUL="soul_tide", LEV="abyss_leviathan";
 static final int SOUL_CMD=910041, LEV_CMD=910042;
 private NamespacedKey weaponKey;
 private Skills skills;
 private final Map<UUID,Long> walkFx=new HashMap<>();
 private final Set<UUID> tideWalking=new HashSet<>();
 private static final String GUI="LegendaryRais • Weapons";

 @Override public void onEnable(){
  saveDefaultConfig(); weaponKey=new NamespacedKey(this,"weapon_id"); skills=new Skills(this);
  getServer().getPluginManager().registerEvents(this,this);
  Objects.requireNonNull(getCommand("riswp")).setExecutor(this);
  getLogger().info("LegendaryRais 2.1.3-FIX enabled");
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
  m.lore(List.of(Component.text("§7LegendaryRais • Water Soul"),Component.text("§bPassive: Soul Tidewalker"),Component.text("§fS1 Right Click • Abyssal Step"),Component.text("§fS2 Sneak+Left • Tidal Crescent"),Component.text("§fS3 Sneak+Right • Soul Undertow")));
  finishMeta(m,SOUL,SOUL_CMD,"soultide:soul_tide_katana"); i.setItemMeta(m); return i;
 }
 ItemStack levItem(){
  ItemStack i=new ItemStack(Material.TRIDENT); ItemMeta m=i.getItemMeta();
  m.displayName(Component.text("§3§lAbyss Leviathan Trident §8V3"));
  m.lore(List.of(Component.text("§7LegendaryRais • Dark Abyss"),Component.text("§3Passive: Sovereign of the Abyss"),Component.text("§fS1 Right Click • Abyssal Harpoon"),Component.text("§fS2 Sneak+Left • Leviathan Fang"),Component.text("§fS3 Sneak+Right • Maelstrom Prison")));
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
   m.getClass().getMethod("setCustomModelDataComponent",comp.getClass().getInterfaces().length>0?comp.getClass().getInterfaces()[0]:comp.getClass()).invoke(m,comp);
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
  if(SOUL.equals(id)){
   if(p.isSneaking()&&p.isSprinting()&&r)skills.domain(p);
   else if(p.isSneaking()&&r)skills.undertow(p);
   else if(p.isSneaking()&&l)skills.crescent(p);
   else if(r)skills.step(p);
   e.setCancelled(true);
  }else{
   if(p.isSneaking()&&p.isSprinting()&&r){skills.wrath(p);e.setCancelled(true);}
   else if(p.isSneaking()&&r){skills.maelstrom(p);e.setCancelled(true);}
   else if(p.isSneaking()&&l){skills.fang(p);e.setCancelled(true);}
   else if(r){skills.harpoon(p); /* allow vanilla trident charge/throw */ }
  }
 }

 @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
 public void melee(EntityDamageByEntityEvent e){
  if(!(e.getDamager() instanceof Player p)||!(e.getEntity() instanceof LivingEntity t))return;
  String id=weapon(p.getInventory().getItemInMainHand()); if(id==null)return;
  if(p.isSneaking()){e.setCancelled(true);if(SOUL.equals(id))skills.crescent(p);else skills.fang(p);return;}
  skills.basicHit(p,t,id);
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

 @EventHandler(ignoreCancelled=true,priority=EventPriority.HIGHEST)
 public void waterWalk(PlayerMoveEvent e){
  Player p=e.getPlayer();
  Location to=e.getTo();
  if(to==null){return;}
  if(!soul(p)||p.isFlying()||p.isGliding()){
   tideWalking.remove(p.getUniqueId());
   return;
  }

  Location from=e.getFrom();
  double surface=findWaterSurface(to);
  if(Double.isNaN(surface)){
   tideWalking.remove(p.getUniqueId());
   return;
  }

  /*
   * IMPORTANT:
   * X/Z are NEVER changed here. Those coordinates come entirely from the
   * player's own movement packet, so Soul Tide cannot steer or slide them.
   * We only stabilise the feet Y position when the player touches water.
   */
  double dy=to.getY()-from.getY();
  double toAbove=to.getY()-surface;
  double fromAbove=from.getY()-surface;

  // Let the player jump normally. Do not pull them back down while rising.
  if(dy>0.045 && fromAbove>=-0.18){
   tideWalking.add(p.getUniqueId());
   return;
  }

  // While still clearly above the surface (for example during a jump),
  // leave the complete player movement untouched until they fall back.
  if(toAbove>0.16){
   tideWalking.add(p.getUniqueId());
   return;
  }

  // Snap only vertically to the water surface. Preserve exact X, Z, yaw,
  // pitch and horizontal player input. No setVelocity() is used at all.
  Location stable=to.clone();
  stable.setY(surface);
  e.setTo(stable);
  tideWalking.add(p.getUniqueId());

  p.setFallDistance(0f);
  try{p.setSwimming(false);}catch(Throwable ignored){}

  long now=System.currentTimeMillis();
  long next=walkFx.getOrDefault(p.getUniqueId(),0L);
  if(now>=next){
   walkFx.put(p.getUniqueId(),now+Math.max(60,getConfig().getLong("water-walk.effect-interval-ms",90)));
   skills.walkFx(p,stable);
  }
 }

 private double findWaterSurface(Location l){
  World w=l.getWorld();
  if(w==null)return Double.NaN;
  int x=l.getBlockX(),z=l.getBlockZ(),base=l.getBlockY();

  // If already inside water, find the TOP of this water column so the
  // passive immediately rescues the player instead of letting them sink.
  for(int y=base+2;y>=base-6;y--){
   if(w.getBlockAt(x,y,z).getType()!=Material.WATER)continue;
   int top=y;
   while(top< w.getMaxHeight()-1 && w.getBlockAt(x,top+1,z).getType()==Material.WATER)top++;
   return top+1.015;
  }
  return Double.NaN;
 }
 private boolean isWater(Location l){return l.getBlock().getType()==Material.WATER;}
}

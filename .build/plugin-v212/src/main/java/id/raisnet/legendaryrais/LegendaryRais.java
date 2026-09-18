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
 private static final String GUI="LegendaryRais • Weapons";

 @Override public void onEnable(){
  saveDefaultConfig(); weaponKey=new NamespacedKey(this,"weapon_id"); skills=new Skills(this);
  getServer().getPluginManager().registerEvents(this,this);
  Objects.requireNonNull(getCommand("riswp")).setExecutor(this);
  getLogger().info("LegendaryRais 2.1.2-FIX enabled");
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
  Player p=e.getPlayer(); if(!soul(p)||e.getTo()==null)return;
  if(p.isFlying()||p.isGliding())return;
  Location from=e.getFrom(),to=e.getTo(); double surface=findWaterSurface(to);
  if(Double.isNaN(surface))return;
  double dy=to.getY()-from.getY();
  if(dy>0.18&&!isWater(to.clone().add(0,-0.15,0)))return;
  if(Math.abs(to.getY()-surface)<2.2){
   Location n=to.clone(); n.setY(surface); e.setTo(n);
   Vector v=p.getVelocity(); if(v.getY()<0)v.setY(0); p.setVelocity(v); p.setFallDistance(0); try{p.setSwimming(false);}catch(Throwable ignored){}
   long now=System.currentTimeMillis(),next=walkFx.getOrDefault(p.getUniqueId(),0L);
   if(now>=next){walkFx.put(p.getUniqueId(),now+Math.max(60,getConfig().getLong("water-walk.effect-interval-ms",90)));skills.walkFx(p,n);}
  }
 }
 private double findWaterSurface(Location l){
  int x=l.getBlockX(),z=l.getBlockZ(),start=(int)Math.floor(l.getY()+1.2);
  for(int y=start;y>=start-4;y--)if(l.getWorld().getBlockAt(x,y,z).getType()==Material.WATER)return y+1.03;
  return Double.NaN;
 }
 private boolean isWater(Location l){return l.getBlock().getType()==Material.WATER;}
}

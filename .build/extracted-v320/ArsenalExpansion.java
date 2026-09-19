package id.raisnet.legendaryrais;

import net.kyori.adventure.text.Component;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.Action;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataContainer;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitRunnable;
import org.bukkit.util.Vector;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * v3.2 realistic free-gacha expansion with wearable armor and max-health bonuses. The two premium water relics remain in LegendaryRais core
 * and intentionally keep dramatically higher damage than every item in this class.
 */
public final class ArsenalExpansion implements Listener, CommandExecutor {
    public static final String EMBERFALL = "emberfall_greatsword";
    public static final String NOCTIS = "noctis_reaper";
    public static final String STORMPIERCER = "stormpiercer_bow";
    public static final String GAIA = "gaia_thorn_spear";
    public static final String ASTRAL = "astral_rift_katars";

    public static final String PHOENIX = "phoenix";
    public static final String VOIDWALKER = "voidwalker";
    public static final String TITAN = "titan";
    public static final String CELESTIAL = "celestial";
    public static final String WATER_SOVEREIGN = "water_sovereign";

    private static final int EMBERFALL_CMD=910051, NOCTIS_CMD=910052, STORM_CMD=910053, GAIA_CMD=910054, ASTRAL_CMD=910055;
    private static final int FX_EMBER_RIFT=910201, FX_EMBER_METEOR=910202, FX_INFERNO=910203;
    private static final int FX_SHADE=910204, FX_HARVEST=910205, FX_ECLIPSE=910206;
    private static final int FX_GALE=910207, FX_CYCLONE=910208, FX_THUNDER=910209;
    private static final int FX_ROOT=910210, FX_STONE=910211, FX_SPIKE=910212;
    private static final int FX_RIFT=910213, FX_STAR=910214, FX_REND=910215;
    private static final int FX_PHOENIX=910220, FX_VOID=910221, FX_TITAN=910222, FX_CELESTIAL=910223, FX_WATER_ARMOR=910224;

    private final JavaPlugin plugin;
    private final NamespacedKey weaponKey, armorSetKey, armorPieceKey, armorHealthBaseKey, armorHealthMarkerKey;
    private final Map<UUID, Map<String,Long>> cooldowns = new ConcurrentHashMap<>();
    private final Set<UUID> internalDamage = Collections.newSetFromMap(new ConcurrentHashMap<>());

    public ArsenalExpansion(JavaPlugin plugin) {
        this.plugin=plugin;
        this.weaponKey=new NamespacedKey(plugin,"weapon_id");
        this.armorSetKey=new NamespacedKey(plugin,"armor_set");
        this.armorPieceKey=new NamespacedKey(plugin,"armor_piece");
        this.armorHealthBaseKey=new NamespacedKey(plugin,"armor_health_base");
        this.armorHealthMarkerKey=new NamespacedKey(plugin,"armor_health_active");
    }

    public void enable() {
        Bukkit.getPluginManager().registerEvents(this,plugin);
        PluginCommand give=plugin.getCommand("risgive"); if(give!=null)give.setExecutor(this);
        startArmorPassiveTask();
    }

    @Override public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        if(!cmd.getName().equalsIgnoreCase("risgive")) return false;
        if(!(sender instanceof ConsoleCommandSender) && !sender.isOp() && !sender.hasPermission("legendaryrais.give")) { sender.sendMessage("§cNo permission: legendaryrais.give"); return true; }
        if(args.length==1 && args[0].equalsIgnoreCase("list")) { sender.sendMessage("§bLegendaryRais IDs: §fsoul_tide, leviathan, emberfall, noctis, stormpiercer, gaia, astral, phoenix_set, voidwalker_set, titan_set, celestial_set, water_sovereign_set"); return true; }
        if(args.length<2) { sender.sendMessage("§e/risgive <player> <id> [amount] §7| /risgive list"); return true; }
        Player target=Bukkit.getPlayerExact(args[0]); if(target==null){sender.sendMessage("§cPlayer harus online: "+args[0]);return true;}
        String id=normalize(args[1]); int amount=1; if(args.length>2)try{amount=Math.max(1,Math.min(64,Integer.parseInt(args[2])));}catch(NumberFormatException ignored){}
        if(!giveById(target,id,amount)){sender.sendMessage("§cID tidak dikenal: "+args[1]+" §7Gunakan /risgive list");return true;}
        sender.sendMessage("§aDiberikan: §f"+id+" x"+amount+" §a→ §f"+target.getName());
        target.sendMessage("§6✦ §fKamu mendapatkan hadiah LegendaryRais: §e"+id+(amount>1?" x"+amount:"")); return true;
    }

    private String normalize(String raw){String x=raw.toLowerCase(Locale.ROOT).replace('-','_');return switch(x){
        case "soultide","soul","soul_tide","sovereign"->"soul_tide"; case "trident","leviathan","abyss"->"leviathan";
        case "ember","emberfall"->"emberfall"; case "noctis","reaper"->"noctis"; case "storm","stormpiercer","bow"->"stormpiercer";
        case "gaia","thorn"->"gaia"; case "astral","katars","rift"->"astral"; case "phoenix","phoenix_set"->"phoenix_set";
        case "void","voidwalker","voidwalker_set"->"voidwalker_set"; case "titan","titan_set"->"titan_set"; case "celestial","celestial_set"->"celestial_set";
        case "water","water_set","water_sovereign","water_sovereign_set","abyssal_regalia"->"water_sovereign_set"; default->x;};}

    private boolean giveById(Player p,String id,int amount){
        if(id.equals("soul_tide")||id.equals("leviathan")){p.sendMessage("§ePremium relic tetap diambil lewat §f/riswp§e agar authenticity tag core terjaga.");return true;}
        if(id.endsWith("_set")){String set=id.substring(0,id.length()-4);if(!Set.of(PHOENIX,VOIDWALKER,TITAN,CELESTIAL,WATER_SOVEREIGN).contains(set))return false;for(int n=0;n<amount;n++)for(String piece:List.of("helmet","chest","legs","boots"))giveSafe(p,createArmorPiece(set,piece));return true;}
        String wid=switch(id){case "emberfall"->EMBERFALL;case "noctis"->NOCTIS;case "stormpiercer"->STORMPIERCER;case "gaia"->GAIA;case "astral"->ASTRAL;default->null;};
        if(wid==null)return false;for(int n=0;n<amount;n++)giveSafe(p,createWeapon(wid));return true;
    }
    private void giveSafe(Player p,ItemStack item){Map<Integer,ItemStack> left=p.getInventory().addItem(item);for(ItemStack x:left.values())p.getWorld().dropItemNaturally(p.getLocation(),x);}

    private ItemStack createWeapon(String id){Material mat;String name,model;int cmd;List<String> lore;
        switch(id){
            case EMBERFALL->{mat=Material.NETHERITE_SWORD;name="§6§lEMBERFALL §c§lCLAYMORE";model="emberfall_claymore";cmd=EMBERFALL_CMD;lore=List.of("§7Free-Gacha Legendary • Realistic two-handed volcanic claymore.","","§6I §fBlazing Cleave §8• §7Right Click","§cII §fCinder Rush §8• §7Sneak + Left Click","§4III §fMeteor Breaker §8• §7Sneak + Right Click","","§7Damage: §eLegendary Gacha §8≪ Premium Water");}
            case NOCTIS->{mat=Material.NETHERITE_SWORD;name="§5§lNOCTIS §8§lLONGSWORD";model="noctis_longsword";cmd=NOCTIS_CMD;lore=List.of("§7Free-Gacha Legendary • Black knight longsword with an eclipse edge.","","§5I §fShadow Step §8• §7Right Click","§dII §fNight Sever §8• §7Sneak + Left Click","§8III §fEclipse Lock §8• §7Sneak + Right Click","","§7Damage: §eLegendary Gacha");}
            case STORMPIERCER->{mat=Material.BOW;name="§f§lSTORMPIERCER §b§lRECURVE BOW";model="stormpiercer_recurve_bow";cmd=STORM_CMD;lore=List.of("§7Free-Gacha Legendary • Realistic recurve war bow built around a storm core.","","§bI §fWindshot §8• §7Right Click","§fII §fThunder Volley §8• §7Sneak + Left Click","§9III §fTempest Mark §8• §7Sneak + Right Click","","§7Skill tidak membutuhkan arrow.");}
            case GAIA->{mat=Material.NETHERITE_SHOVEL;name="§2§lGAIA §a§lWAR SPEAR";model="gaia_war_spear";cmd=GAIA_CMD;lore=List.of("§7Free-Gacha Legendary • Realistic leaf-bladed war spear with an ancient oak haft.","","§2I §fRoot Thrust §8• §7Right Click","§aII §fStonewake §8• §7Sneak + Left Click","§6III §fEarthshatter Line §8• §7Sneak + Right Click","","§7Damage: §eLegendary Gacha");}
            case ASTRAL->{mat=Material.SHEARS;name="§d§lASTRAL §5§lTWIN DAGGERS";model="astral_twin_daggers";cmd=ASTRAL_CMD;lore=List.of("§7Free-Gacha Legendary • Paired realistic daggers forged around a small rift.","","§dI §fRift Dash §8• §7Right Click","§fII §fStar Fang §8• §7Sneak + Left Click","§5III §fAstral Rend §8• §7Sneak + Right Click","","§7Damage: §eLegendary Gacha");}
            default->{return new ItemStack(Material.BARRIER);}}
        ItemStack item=new ItemStack(mat);ItemMeta m=item.getItemMeta();if(m==null)return item;m.setDisplayName(name);m.setLore(lore);applyVisual(m,cmd,model);m.getPersistentDataContainer().set(weaponKey,PersistentDataType.STRING,id);item.setItemMeta(m);return item;
    }

    private ItemStack createArmorPiece(String set,String piece){
        Material mat=armorMaterial(set,piece);
        ItemStack item=new ItemStack(mat);
        ItemMeta m=item.getItemMeta(); if(m==null)return item;

        String color=switch(set){case PHOENIX->"§6";case VOIDWALKER->"§5";case TITAN->"§2";case WATER_SOVEREIGN->"§3";default->"§b";};
        String title=switch(set){case PHOENIX->"PHOENIX PLATE";case VOIDWALKER->"VOIDWALKER SET";case TITAN->"TITAN GUARD";case WATER_SOVEREIGN->"WATER SOVEREIGN REGALIA";default->"CELESTIAL KNIGHT";};

        List<String> lore=new ArrayList<>();
        lore.add(set.equals(WATER_SOVEREIGN)?"§bPremium Water Relic Armor":"§7Free-Gacha Legendary Armor");
        lore.add("");
        lore.add("§eFull Set Skill: §f"+armorSkillName(set));
        lore.add("§7Sneak + Drop/Q untuk cast.");
        lore.add("§7Drop dibatalkan saat skill aktif.");
        lore.add("");
        lore.addAll(armorPassiveLore(set));
        lore.add("§c❤ Max Health: §f+"+formatHearts(armorHealthPerPiece(set))+" hearts §7per piece");

        m.setDisplayName(color+"§l"+title+" §8• §f"+piece.toUpperCase(Locale.ROOT));
        m.setLore(lore);
        applyVisual(m,armorCmd(set,piece),"armor/"+set+"_"+piece);

        // Explicit slot + swappable fixes right-click equipping on modern Paper.
        try{
            var eq=m.getEquippable();
            eq.setSlot(armorSlot(piece));
            eq.setModel(new NamespacedKey("legendaryv32",set+"_set"));
            eq.setSwappable(true);
            eq.setDamageOnHurt(false);
            m.setEquippable(eq);
        }catch(Throwable ex){plugin.getLogger().warning("Could not apply equippable component to "+set+"/"+piece+": "+ex.getMessage());}

        m.getPersistentDataContainer().set(armorSetKey,PersistentDataType.STRING,set);
        m.getPersistentDataContainer().set(armorPieceKey,PersistentDataType.STRING,piece);
        item.setItemMeta(m);
        return item;
    }

    private EquipmentSlot armorSlot(String piece){
        return switch(piece){
            case "helmet"->EquipmentSlot.HEAD;
            case "chest"->EquipmentSlot.CHEST;
            case "legs"->EquipmentSlot.LEGS;
            default->EquipmentSlot.FEET;
        };
    }

    private double armorHealthPerPiece(String set){
        return switch(set){
            case WATER_SOVEREIGN->4.0; // +2 hearts per piece / +8 hearts full set
            case TITAN->3.0;           // +1.5 hearts per piece / +6 hearts full set
            case PHOENIX,CELESTIAL->2.0; // +1 heart per piece / +4 hearts full set
            case VOIDWALKER->1.5;      // +0.75 heart per piece / +3 hearts full set
            default->0.0;
        };
    }

    private String formatHearts(double hp){return String.format(Locale.US,"%.2f",hp/2.0).replaceAll("\\.?0+$","");}

    private double legendaryArmorHealthBonus(Player p){
        double bonus=0.0;
        ItemStack[] worn={p.getInventory().getHelmet(),p.getInventory().getChestplate(),p.getInventory().getLeggings(),p.getInventory().getBoots()};
        for(ItemStack i:worn){
            if(i==null||i.getType()==Material.AIR)continue;
            ItemMeta m=i.getItemMeta(); if(m==null)continue;
            String set=m.getPersistentDataContainer().get(armorSetKey,PersistentDataType.STRING);
            if(set!=null)bonus+=armorHealthPerPiece(set);
        }
        return bonus;
    }

    private void syncLegendaryHealth(Player p){
        try{
            PersistentDataContainer data=p.getPersistentDataContainer();
            double bonus=legendaryArmorHealthBonus(p);
            Double base=data.get(armorHealthBaseKey,PersistentDataType.DOUBLE);
            Integer active=data.get(armorHealthMarkerKey,PersistentDataType.INTEGER);
            if(bonus>0.0){
                if(base==null){
                    base=Math.max(1.0,p.getMaxHealth());
                    data.set(armorHealthBaseKey,PersistentDataType.DOUBLE,base);
                }
                data.set(armorHealthMarkerKey,PersistentDataType.INTEGER,1);
                double wanted=Math.max(1.0,base+bonus);
                if(Math.abs(p.getMaxHealth()-wanted)>.01)p.setMaxHealth(wanted);
            }else if(active!=null){
                if(base!=null)p.setMaxHealth(Math.max(1.0,base));
                data.remove(armorHealthBaseKey);
                data.remove(armorHealthMarkerKey);
                if(p.getHealth()>p.getMaxHealth())p.setHealth(p.getMaxHealth());
            }
        }catch(Throwable ex){plugin.getLogger().warning("Legendary armor health sync failed for "+p.getName()+": "+ex.getMessage());}
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void rightClickEquipLegendaryArmor(PlayerInteractEvent e){
        if(e.getHand()!=EquipmentSlot.HAND)return;
        Action action=e.getAction();
        if(action!=Action.RIGHT_CLICK_AIR&&action!=Action.RIGHT_CLICK_BLOCK)return;
        Player p=e.getPlayer(); ItemStack hand=p.getInventory().getItemInMainHand();
        if(hand==null||hand.getType()==Material.AIR)return;
        ItemMeta meta=hand.getItemMeta(); if(meta==null)return;
        String set=meta.getPersistentDataContainer().get(armorSetKey,PersistentDataType.STRING);
        String piece=meta.getPersistentDataContainer().get(armorPieceKey,PersistentDataType.STRING);
        if(set==null||piece==null)return;

        e.setCancelled(true);
        ItemStack old=switch(piece){
            case "helmet"->p.getInventory().getHelmet();
            case "chest"->p.getInventory().getChestplate();
            case "legs"->p.getInventory().getLeggings();
            default->p.getInventory().getBoots();
        };
        ItemStack equip=hand.clone(); equip.setAmount(1);
        switch(piece){
            case "helmet"->p.getInventory().setHelmet(equip);
            case "chest"->p.getInventory().setChestplate(equip);
            case "legs"->p.getInventory().setLeggings(equip);
            default->p.getInventory().setBoots(equip);
        }
        if(hand.getAmount()<=1)p.getInventory().setItemInMainHand(old==null?new ItemStack(Material.AIR):old);
        else{
            hand.setAmount(hand.getAmount()-1);p.getInventory().setItemInMainHand(hand);
            if(old!=null&&old.getType()!=Material.AIR)giveSafe(p,old);
        }
        Bukkit.getScheduler().runTask(plugin,()->syncLegendaryHealth(p));
        bar(p,"ARMOR EQUIPPED • "+set.toUpperCase(Locale.ROOT)+" • "+piece.toUpperCase(Locale.ROOT));
    }

    private List<String> armorPassiveLore(String set){
        return switch(set){
            case PHOENIX->List.of("§6✦ Passive: §eAshen Heart","§7Fire Resistance; regen saat HP kritis.");
            case VOIDWALKER->List.of("§5✦ Passive: §dNightstride","§7Speed + Night Vision; fall damage sangat berkurang.");
            case TITAN->List.of("§2✦ Passive: §aIron Mountain","§7Resistance konstan dan anti-burst.");
            case WATER_SOVEREIGN->List.of("§3✦ Passive: §bAbyssal Bulwark","§7Legendary basic hit = §c2.5 hearts§7.","§7Legendary skill hit = §c5 hearts§7.","§7Water Breathing + Dolphins Grace + regen di air.");
            default->List.of("§b✦ Passive: §fStarlight Grace","§7Regeneration ringan + Slow Falling.");
        };
    }
    private Material armorMaterial(String set,String piece){String p=switch(set){case PHOENIX->"GOLDEN_";case VOIDWALKER,WATER_SOVEREIGN->"NETHERITE_";case TITAN->"DIAMOND_";default->"IRON_";};String q=switch(piece){case "helmet"->"HELMET";case "chest"->"CHESTPLATE";case "legs"->"LEGGINGS";default->"BOOTS";};return Material.valueOf(p+q);}
    private int armorCmd(String set,String piece){int b=switch(set){case PHOENIX->920100;case VOIDWALKER->920104;case TITAN->920108;case CELESTIAL->920112;case WATER_SOVEREIGN->920116;default->920112;};return b+switch(piece){case "helmet"->1;case "chest"->2;case "legs"->3;default->4;};}
    private String armorSkillName(String set){return switch(set){case PHOENIX->"Phoenix Rebirth";case VOIDWALKER->"Void Slip";case TITAN->"Titan Bastion";case WATER_SOVEREIGN->"Throne of the Abyss";default->"Astral Sanctuary";};}

    private void applyVisual(ItemMeta m,int cmd,String model){m.setUnbreakable(true);try{m.setCustomModelData(cmd);}catch(Throwable ignored){}try{m.setItemModel(new NamespacedKey("legendaryv32",model));}catch(Throwable ignored){}try{m.setEnchantmentGlintOverride(true);}catch(Throwable ignored){}}
    private String weaponId(ItemStack item){if(item==null||item.getType()==Material.AIR)return "";ItemMeta m=item.getItemMeta();if(m==null)return "";String id=m.getPersistentDataContainer().get(weaponKey,PersistentDataType.STRING);return id==null?"":id;}
    private boolean expansionWeapon(String id){return Set.of(EMBERFALL,NOCTIS,STORMPIERCER,GAIA,ASTRAL).contains(id);}

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false) public void interact(PlayerInteractEvent e){if(e.getHand()!=null&&e.getHand()!=EquipmentSlot.HAND)return;Player p=e.getPlayer();String id=weaponId(p.getInventory().getItemInMainHand());if(!expansionWeapon(id))return;Action a=e.getAction();boolean right=a==Action.RIGHT_CLICK_AIR||a==Action.RIGHT_CLICK_BLOCK,left=a==Action.LEFT_CLICK_AIR||a==Action.LEFT_CLICK_BLOCK;if(p.isSneaking()&&right){e.setCancelled(true);cast(p,id,3);}else if(p.isSneaking()&&left){e.setCancelled(true);cast(p,id,2);}else if(!p.isSneaking()&&right){e.setCancelled(true);cast(p,id,1);}}
    @EventHandler(ignoreCancelled=true) public void melee(EntityDamageByEntityEvent e){if(!(e.getDamager() instanceof Player p)||!(e.getEntity() instanceof LivingEntity t))return;String id=weaponId(p.getInventory().getItemInMainHand());if(!expansionWeapon(id))return;if(internalDamage.contains(t.getUniqueId()))return;e.setDamage(Math.max(e.getDamage(),baseDamage(id)));hitFx(t,id);if(p.isSneaking()){e.setCancelled(true);cast(p,id,2);}}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void waterSovereignDamageCap(EntityDamageByEntityEvent e){
        if(!(e.getEntity() instanceof Player target))return;
        if(!WATER_SOVEREIGN.equals(fullSet(target)))return;

        Player attacker=null;
        if(e.getDamager() instanceof Player p)attacker=p;
        else if(e.getDamager() instanceof Projectile pr && pr.getShooter() instanceof Player p)attacker=p;
        if(attacker==null)return;

        String wid=weaponId(attacker.getInventory().getItemInMainHand());
        boolean legendary=expansionWeapon(wid)||wid.equals("soul_tide_katana_v4")||wid.equals("abyss_leviathan_trident_v3");
        if(!legendary)return;

        double raw=e.getDamage();
        double desired=raw>=55.0?10.0:5.0; // 5 damage = 2.5 hearts, 10 = 5 hearts.
        double healthBefore=target.getHealth();

        // Keep vanilla hurt animation/knockback, then correct the final health loss after armor/resistance.
        e.setDamage(Math.min(raw,desired));
        Bukkit.getScheduler().runTask(plugin,()->{
            if(!target.isValid()||target.isDead())return;
            double actual=Math.max(0.0,healthBefore-target.getHealth());
            double diff=desired-actual;
            if(Math.abs(diff)<0.01)return;
            double corrected=Math.max(0.0,Math.min(target.getMaxHealth(),target.getHealth()-diff));
            target.setHealth(corrected);
        });

        particle(target.getWorld(),"SPLASH",target.getLocation().clone().add(0,1,0),34,.65,.85,.65,.10);
        particle(target.getWorld(),"BUBBLE_POP",target.getLocation().clone().add(0,1,0),24,.5,.7,.5,.06);
        pulse(target.getWorld(),target.getLocation().clone().add(0,1,0),"fx_water_sovereign_guard",FX_WATER_ARMOR,2.15f,8,target.getLocation().getYaw(),0);
        bar(target,"ABYSSAL BULWARK • "+(desired/2.0)+" hearts");
    }

    @EventHandler(ignoreCancelled=true)
    public void armorEnvironmentalDefense(org.bukkit.event.entity.EntityDamageEvent e){
        if(!(e.getEntity() instanceof Player p))return;
        String set=fullSet(p); if(set==null)return;
        if(VOIDWALKER.equals(set)&&e.getCause()==org.bukkit.event.entity.EntityDamageEvent.DamageCause.FALL){
            e.setDamage(e.getDamage()*.18);
        }
    }

    @EventHandler(ignoreCancelled=true) public void swing(PlayerAnimationEvent e){Player p=e.getPlayer();if(!p.isSneaking())return;String id=weaponId(p.getInventory().getItemInMainHand());if(expansionWeapon(id))cast(p,id,2);}

    private double baseDamage(String id){return plugin.getConfig().getDouble("gacha."+cfg(id)+".base-hit",switch(id){case EMBERFALL->24;case NOCTIS->22;case STORMPIERCER->18;case GAIA->25;default->21;});}
    private String cfg(String id){return switch(id){case EMBERFALL->"emberfall";case NOCTIS->"noctis";case STORMPIERCER->"stormpiercer";case GAIA->"gaia";default->"astral";};}
    private double damage(String id,int skill){List<Double> v=plugin.getConfig().getDoubleList("gacha."+cfg(id)+".damage");double[] d=switch(id){case EMBERFALL->new double[]{85,110,140};case NOCTIS->new double[]{75,95,130};case STORMPIERCER->new double[]{65,90,120};case GAIA->new double[]{80,105,145};default->new double[]{70,100,135};};return v.size()>=3?v.get(skill-1):d[skill-1];}
    private int skillCd(int skill){List<Integer> v=plugin.getConfig().getIntegerList("gacha.cooldowns");return v.size()>=3?Math.max(1,v.get(skill-1)):new int[]{10,16,24}[skill-1];}
    private boolean ready(Player p,String key,int sec,String name){long now=System.currentTimeMillis();Map<String,Long> m=cooldowns.computeIfAbsent(p.getUniqueId(),u->new ConcurrentHashMap<>());long end=m.getOrDefault(key,0L);if(now<end){bar(p,name+" • "+String.format(Locale.US,"%.1fs",(end-now)/1000.0));return false;}m.put(key,now+sec*1000L);return true;}
    private void cast(Player p,String id,int skill){if(!ready(p,id+":"+skill,skillCd(skill),"Skill "+skill))return;switch(id){case EMBERFALL->ember(p,skill);case NOCTIS->noctis(p,skill);case STORMPIERCER->storm(p,skill);case GAIA->gaia(p,skill);case ASTRAL->astral(p,skill);}}

    private void ember(Player p,int s){double dmg=damage(EMBERFALL,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();if(s==1){Set<UUID> hit=new HashSet<>();for(int i=1;i<=12;i++){Location c=p.getLocation().clone().add(d.clone().multiply(i*.75));pulse(w,c,"fx_ember_rift",FX_EMBER_RIFT,1.25f,5,p.getLocation().getYaw(),0);particle(w,"FLAME",c,9,.25,.15,.25,.03);for(Entity e:w.getNearbyEntities(c,.9,.9,.9))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId())){hurt(l,dmg,p);l.setFireTicks(50);}}bar(p,"EMBERFALL • Blazing Cleave");}else if(s==2){Location c=p.getLocation().clone().add(d.clone().multiply(8));pulse(w,c.clone().add(0,5,0),"fx_ember_meteor",FX_EMBER_METEOR,3.4f,20,p.getLocation().getYaw(),0);new BukkitRunnable(){public void run(){blockFx(w,c.clone().add(0,.4,0),Material.MAGMA_BLOCK,2.4f,12);particle(w,"EXPLOSION_EMITTER",c,2,.1,.1,.1,0);for(Entity e:w.getNearbyEntities(c,4,3,4))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,dmg,p);l.setFireTicks(70);Vector v=l.getLocation().toVector().subtract(c.toVector());if(v.lengthSquared()>.01)l.setVelocity(v.normalize().multiply(.6).setY(.35));}}}.runTaskLater(plugin,18);bar(p,"EMBERFALL • Cinder Rush");}else{new BukkitRunnable(){int t=0;public void run(){if(!p.isOnline()||t++>40){cancel();return;}Location c=p.getLocation().clone().add(0,.2,0);pulse(w,c,"fx_inferno_crown",FX_INFERNO,2.8f,5,t*18,0);ring(w,c,"FLAME",3.2,24,t*.18);if(t%10==0)for(Entity e:w.getNearbyEntities(c,3.5,2.5,3.5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,dmg/3,p);l.setFireTicks(45);}}}.runTaskTimer(plugin,0,1);bar(p,"EMBERFALL • Meteor Breaker");}}
    private void noctis(Player p,int s){double dmg=damage(NOCTIS,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();if(s==1){Location from=p.getLocation().clone(),to=safeForward(p,6.5);for(int i=0;i<12;i++){Location q=from.clone().add(to.toVector().subtract(from.toVector()).multiply(i/11.0)).add(0,1,0);particle(w,"SCULK_SOUL",q,3,.15,.2,.15,.01);}for(Entity e:w.getNearbyEntities(from.clone().add(d.clone().multiply(3)),4,2.5,4))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId()))hurt(l,dmg,p);p.teleport(to);pulse(w,to.clone().add(0,1,0),"fx_shade_step",FX_SHADE,2.2f,10,p.getLocation().getYaw(),0);bar(p,"NOCTIS • Shadow Step");}else if(s==2){int hits=0;for(LivingEntity l:targets(p,6,6,true)){Vector n=l.getLocation().toVector().subtract(p.getLocation().toVector()).normalize();if(n.dot(d)<.25)continue;hurt(l,dmg,p);hits++;pulse(w,l.getLocation().clone().add(0,1,0),"fx_soul_harvest",FX_HARVEST,1.8f,8,0,0);}if(hits>0)p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+Math.min(10,hits*2.0)));bar(p,"NOCTIS • Night Sever • "+hits);}else{Location c=p.getLocation().clone().add(d.clone().multiply(5));new BukkitRunnable(){int t=0;public void run(){if(t++>55){cancel();return;}pulse(w,c,"fx_eclipse_cage",FX_ECLIPSE,3.3f,6,t*16,0);ring(w,c,"PORTAL",4,28,t*.12);if(t%15==0)for(Entity e:w.getNearbyEntities(c,4,3,4))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,dmg/3,p);try{l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,35,2,true,false,false));l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.DARKNESS,35,0,true,false,false));}catch(Throwable ignored){}}}}.runTaskTimer(plugin,0,1);bar(p,"NOCTIS • Eclipse Lock");}}
    private void storm(Player p,int s){double dmg=damage(STORMPIERCER,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();if(s==1){LivingEntity h=ray(p,d,18,1);beam(w,p.getEyeLocation(),d,18,"CLOUD","fx_gale_bolt",FX_GALE);if(h!=null){hurt(h,dmg,p);h.setVelocity(d.clone().multiply(1).setY(.18));}bar(p,"STORMPIERCER • Windshot");}else if(s==2){for(int k=-2;k<=2;k++){Vector v=rotateY(d,Math.toRadians(k*8));LivingEntity h=ray(p,v,15,.85);beam(w,p.getEyeLocation(),v,15,"CLOUD","fx_cyclone_volley",FX_CYCLONE);if(h!=null)hurt(h,dmg/2.2,p);}bar(p,"STORMPIERCER • Thunder Volley");}else{Location c=p.getLocation().clone().add(d.clone().multiply(9));pulse(w,c.clone().add(0,4,0),"fx_thunderhead",FX_THUNDER,4,24,0,0);new BukkitRunnable(){int t=0;public void run(){if(t++>30){cancel();return;}if(t%6==0){Location q=c.clone().add(t%12==0?2:-2,0,t%18==0?2:-2);w.strikeLightningEffect(q);for(Entity e:w.getNearbyEntities(q,2.5,3,2.5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId()))hurt(l,dmg/4,p);}}}.runTaskTimer(plugin,10,1);bar(p,"STORMPIERCER • Tempest Mark");}}
    private void gaia(Player p,int s){double dmg=damage(GAIA,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();if(s==1){Set<UUID> hit=new HashSet<>();for(int i=1;i<=10;i++){Location c=p.getLocation().clone().add(d.clone().multiply(i));blockFx(w,c,Material.MOSS_BLOCK,.75f,8);pulse(w,c.clone().add(0,.5,0),"fx_rootline",FX_ROOT,1.25f,6,0,0);for(Entity e:w.getNearbyEntities(c,1.1,1.5,1.1))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId())){hurt(l,dmg,p);try{l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,45,5,true,false,false));}catch(Throwable ignored){}}}bar(p,"GAIA • Root Thrust");}else if(s==2){try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,100,1,true,false,false));p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,100,1,true,false,false));}catch(Throwable ignored){}pulse(w,p.getLocation().clone().add(0,1,0),"fx_stoneguard",FX_STONE,3,18,0,0);for(Entity e:w.getNearbyEntities(p.getLocation(),3,2,3))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,dmg*.5,p);Vector v=l.getLocation().toVector().subtract(p.getLocation().toVector());if(v.lengthSquared()>.01)l.setVelocity(v.normalize().multiply(.55).setY(.25));}bar(p,"GAIA • Stonewake");}else{Location c=p.getLocation().clone().add(d.clone().multiply(5));for(int i=0;i<12;i++){double a=Math.PI*2*i/12;Location q=c.clone().add(Math.cos(a)*3,0,Math.sin(a)*3);blockFx(w,q,Material.POINTED_DRIPSTONE,1.1f,14);pulse(w,q.clone().add(0,1,0),"fx_worldspike",FX_SPIKE,1.7f,10,(float)Math.toDegrees(a),0);}for(Entity e:w.getNearbyEntities(c,4,3,4))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,dmg,p);l.setVelocity(new Vector(0,.75,0));}bar(p,"GAIA • Earthshatter Line");}}
    private void astral(Player p,int s){double dmg=damage(ASTRAL,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();if(s==1){LivingEntity t=nearest(p,8);Location from=p.getLocation().clone(),to=t!=null?t.getLocation().clone().subtract(d.clone().multiply(1.4)):safeForward(p,6);p.teleport(to);pulse(w,from.clone().add(0,1,0),"fx_rift_blink",FX_RIFT,2,10,0,0);pulse(w,to.clone().add(0,1,0),"fx_rift_blink",FX_RIFT,2.4f,10,180,0);if(t!=null)hurt(t,dmg,p);bar(p,"ASTRAL • Rift Dash");}else if(s==2){List<LivingEntity> ts=targets(p,10,6,false);for(int i=0;i<6;i++){double a=Math.PI*2*i/6;Location star=p.getLocation().clone().add(Math.cos(a)*2,1.4,Math.sin(a)*2);pulse(w,star,"fx_star_shards",FX_STAR,1,20,(float)Math.toDegrees(a),0);}new BukkitRunnable(){public void run(){int i=0;for(LivingEntity l:ts){if(l.isValid()&&!l.isDead()){hurt(l,dmg/Math.max(1,Math.min(3,ts.size())),p);pulse(w,l.getLocation().clone().add(0,1,0),"fx_star_shards",FX_STAR,1.6f,8,i++*45,0);}}}}.runTaskLater(plugin,12);bar(p,"ASTRAL • Star Fang");}else{Location c=p.getLocation().clone().add(d.clone().multiply(4));pulse(w,c.clone().add(0,1,0),"fx_dimension_rend",FX_REND,4.4f,18,p.getLocation().getYaw(),0);for(int axis=0;axis<2;axis++)for(int i=-5;i<=5;i++){Vector v=axis==0?d.clone().multiply(i):new Vector(-d.getZ(),0,d.getX()).normalize().multiply(i);particle(w,"END_ROD",c.clone().add(v).add(0,1,0),3,.1,.2,.1,.01);}for(Entity e:w.getNearbyEntities(c,5.5,3,5.5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,dmg,p);Vector v=l.getLocation().toVector().subtract(c.toVector());if(v.lengthSquared()>.01)l.setVelocity(v.normalize().multiply(-.35).setY(.18));}bar(p,"ASTRAL • Astral Rend");}}

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void armorDrop(PlayerDropItemEvent e){Player p=e.getPlayer();if(!p.isSneaking())return;String set=fullSet(p);if(set==null)return;e.setCancelled(true);armorSkill(p,set);}
    private String fullSet(Player p){String found=null;ItemStack[] a={p.getInventory().getHelmet(),p.getInventory().getChestplate(),p.getInventory().getLeggings(),p.getInventory().getBoots()};for(ItemStack i:a){if(i==null||i.getType()==Material.AIR)return null;ItemMeta m=i.getItemMeta();if(m==null)return null;String s=m.getPersistentDataContainer().get(armorSetKey,PersistentDataType.STRING);if(s==null)return null;if(found==null)found=s;else if(!found.equals(s))return null;}return found;}
    private void armorSkill(Player p,String set){
        int cd=plugin.getConfig().getInt("armor.cooldowns."+set,switch(set){case PHOENIX->45;case VOIDWALKER->32;case TITAN->40;case WATER_SOVEREIGN->30;default->38;});
        if(!ready(p,"armor:"+set,cd,armorSkillName(set)))return;World w=p.getWorld();
        switch(set){
            case PHOENIX->{pulse(w,p.getLocation().clone().add(0,1,0),"fx_phoenix_rebirth",FX_PHOENIX,4.5f,24,0,0);particle(w,"FLAME",p.getLocation().clone().add(0,1,0),120,1.5,1.2,1.5,.08);p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+10));try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,120,1,true,false,false));p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.FIRE_RESISTANCE,300,0,true,false,false));}catch(Throwable ignored){}for(Entity e:w.getNearbyEntities(p.getLocation(),4,3,4))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId()))hurt(l,80,p);}
            case VOIDWALKER->{Location from=p.getLocation().clone(),to=safeForward(p,8);pulse(w,from.clone().add(0,1,0),"fx_void_phase",FX_VOID,3,16,0,0);p.teleport(to);try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.INVISIBILITY,100,0,true,false,false));p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,100,0,true,false,false));}catch(Throwable ignored){}pulse(w,to.clone().add(0,1,0),"fx_void_phase",FX_VOID,3,16,180,0);}
            case TITAN->{Location c=p.getLocation().clone();pulse(w,c.clone().add(0,1,0),"fx_titan_bastion",FX_TITAN,4,22,0,0);blockFx(w,c,Material.STONE,3,12);try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,160,3,true,false,false));p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,120,1,true,false,false));}catch(Throwable ignored){}for(Entity e:w.getNearbyEntities(c,6,3,6))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,70,p);l.setVelocity(new Vector(0,.65,0));}}
            case WATER_SOVEREIGN->{Location c=p.getLocation().clone();pulse(w,c.clone().add(0,1.2,0),"fx_water_sovereign_guard",FX_WATER_ARMOR,5.2f,30,0,0);particle(w,"SPLASH",c.clone().add(0,1,0),160,2.0,1.2,2.0,.18);particle(w,"BUBBLE_POP",c.clone().add(0,1,0),100,1.6,1.0,1.6,.12);p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+8));try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,180,3,true,false,false));p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,140,1,true,false,false));p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,160,1,true,false,false));}catch(Throwable ignored){}new BukkitRunnable(){int t=0;public void run(){if(!p.isOnline()||t++>=8){cancel();return;}Location q=p.getLocation().clone();ring(w,q,"SPLASH",3.2,30,t*.35);for(Entity e:w.getNearbyEntities(q,4.5,3.2,4.5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){Vector away=l.getLocation().toVector().subtract(q.toVector());if(away.lengthSquared()>.01)away.normalize();l.setVelocity(away.multiply(.28).setY(.16));if(t%2==0)hurt(l,18,p);}}}.runTaskTimer(plugin,0,5);}
            default->{Location c=p.getLocation().clone();pulse(w,c.clone().add(0,2,0),"fx_celestial_sanctuary",FX_CELESTIAL,5,30,0,0);try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,140,1,true,false,false));p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,140,1,true,false,false));}catch(Throwable ignored){}new BukkitRunnable(){int n=0;public void run(){if(n++>=3){cancel();return;}ring(w,c,"END_ROD",5,36,n*.3);for(Entity e:w.getNearbyEntities(c,5,4,5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId()))hurt(l,55,p);}}.runTaskTimer(plugin,0,14);}
        }
        bar(p,"ARMOR • "+armorSkillName(set));
    }
    private void startArmorPassiveTask(){
        new BukkitRunnable(){
            public void run(){
                for(Player p:Bukkit.getOnlinePlayers()){
                    syncLegendaryHealth(p);
                    String set=fullSet(p); if(set==null)continue;
                    try{
                        switch(set){
                            case PHOENIX->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.FIRE_RESISTANCE,45,0,true,false,false));
                                if(p.getHealth()<=p.getMaxHealth()*.35)p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,45,0,true,false,false));
                            }
                            case VOIDWALKER->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SPEED,45,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION,240,0,true,false,false));
                            }
                            case TITAN->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,45,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,45,0,true,false,false));
                            }
                            case WATER_SOVEREIGN->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.WATER_BREATHING,80,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.DOLPHINS_GRACE,50,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,45,1,true,false,false));
                                if(p.isInWater()&&p.getHealth()<p.getMaxHealth())p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+1.0));
                            }
                            default->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,45,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOW_FALLING,45,0,true,false,false));
                            }
                        }
                    }catch(Throwable ignored){}
                }
            }
        }.runTaskTimer(plugin,20,20);
    }

    private void hurt(LivingEntity t,double amount,Player p){if(amount<=0||!t.isValid()||t.isDead())return;internalDamage.add(t.getUniqueId());try{t.damage(amount,p);}finally{internalDamage.remove(t.getUniqueId());}}
    private void hitFx(LivingEntity t,String id){
        Location c=t.getLocation().clone().add(0,1,0);World w=t.getWorld();
        switch(id){
            case EMBERFALL->{particle(w,"FLAME",c,24,.42,.38,.42,.06);particle(w,"LAVA",c,5,.28,.25,.28,.02);}
            case NOCTIS->{particle(w,"SCULK_SOUL",c,20,.38,.45,.38,.035);particle(w,"REVERSE_PORTAL",c,12,.3,.35,.3,.02);}
            case STORMPIERCER->{particle(w,"ELECTRIC_SPARK",c,22,.42,.5,.42,.08);particle(w,"CLOUD",c,10,.5,.25,.5,.02);}
            case GAIA->{particle(w,"COMPOSTER",c,22,.45,.38,.45,.04);particle(w,"SPORE_BLOSSOM_AIR",c,14,.55,.45,.55,.01);}
            default->{particle(w,"END_ROD",c,18,.35,.45,.35,.03);particle(w,"REVERSE_PORTAL",c,14,.4,.4,.4,.02);}
        }
    }
    private List<LivingEntity> targets(Player p,double r,int max,boolean los){List<LivingEntity> out=new ArrayList<>();for(Entity e:p.getWorld().getNearbyEntities(p.getLocation(),r,r,r)){if(!(e instanceof LivingEntity l)||l.getUniqueId().equals(p.getUniqueId())||!l.isValid()||l.isDead())continue;if(los&&!p.hasLineOfSight(l))continue;out.add(l);}out.sort(Comparator.comparingDouble(x->x.getLocation().distanceSquared(p.getLocation())));return out.size()>max?new ArrayList<>(out.subList(0,max)):out;}
    private LivingEntity nearest(Player p,double r){List<LivingEntity> l=targets(p,r,1,true);return l.isEmpty()?null:l.get(0);}
    private LivingEntity ray(Player p,Vector d,double range,double radius){Location o=p.getEyeLocation();for(double x=.5;x<=range;x+=.55){Location c=o.clone().add(d.clone().multiply(x));for(Entity e:p.getWorld().getNearbyEntities(c,radius,radius,radius))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&l.isValid()&&!l.isDead())return l;if(c.getBlock().getType().isSolid())break;}return null;}
    private Location safeForward(Player p,double dist){Location base=p.getLocation().clone();Vector d=p.getEyeLocation().getDirection().clone();d.setY(0);if(d.lengthSquared()<.01)d=new Vector(1,0,0);d.normalize();for(double x=dist;x>=1;x-=.5){Location q=base.clone().add(d.clone().multiply(x));if(!q.getBlock().getType().isSolid()&&!q.clone().add(0,1,0).getBlock().getType().isSolid())return q;}return base;}
    private Vector rotateY(Vector v,double a){double c=Math.cos(a),s=Math.sin(a);return new Vector(v.getX()*c-v.getZ()*s,v.getY(),v.getX()*s+v.getZ()*c).normalize();}
    private void beam(World w,Location o,Vector d,double range,String particle,String model,int cmd){for(double x=1;x<=range;x+=1){Location c=o.clone().add(d.clone().multiply(x));particle(w,particle,c,2,.08,.08,.08,.01);if(((int)x)%4==0)pulse(w,c,model,cmd,.75f,5,yaw(d),pitch(d));if(c.getBlock().getType().isSolid())break;}}

    private ItemStack fxItem(String model,int cmd){ItemStack i=new ItemStack(Material.PAPER);ItemMeta m=i.getItemMeta();if(m==null)return i;try{m.setCustomModelData(cmd);}catch(Throwable ignored){}try{m.setItemModel(new NamespacedKey("legendaryv32",model));}catch(Throwable ignored){}i.setItemMeta(m);return i;}
    private ItemDisplay display(World w,Location l,String model,int cmd,float scale,float yaw,float pitch){try{ItemDisplay d=w.spawn(l,ItemDisplay.class);d.setItemStack(fxItem(model,cmd));d.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.FIXED);d.setBillboard(Display.Billboard.CENTER);d.setBrightness(new Display.Brightness(15,15));d.setViewRange(64);d.setInterpolationDuration(3);d.setTeleportDuration(2);d.setRotation(yaw,pitch);var tr=d.getTransformation();tr.getScale().set(scale,scale,scale);d.setTransformation(tr);return d;}catch(Throwable ignored){return null;}}
    private void pulse(World w,Location l,String model,int cmd,float max,int life,float yaw,float pitch){ItemDisplay d=display(w,l,model,cmd,Math.max(.35f,max*.38f),yaw,pitch);if(d==null)return;new BukkitRunnable(){int t=0;public void run(){if(++t>=life||!d.isValid()){d.remove();cancel();return;}float p=t/(float)Math.max(1,life),sc=Math.max(.32f,max*(.52f+.58f*(float)Math.sin(Math.min(1,p*1.35)*Math.PI)));var tr=d.getTransformation();tr.getScale().set(sc,sc,sc);d.setTransformation(tr);d.setRotation(yaw+t*7,pitch);}}.runTaskTimer(plugin,1,1);}
    private void blockFx(World w,Location l,Material mat,float scale,int life){try{BlockDisplay d=w.spawn(l,BlockDisplay.class);d.setBlock(mat.createBlockData());d.setBrightness(new Display.Brightness(15,15));var tr=d.getTransformation();tr.getScale().set(scale,scale,scale);d.setTransformation(tr);new BukkitRunnable(){int t=0;public void run(){if(++t>=life||!d.isValid()){d.remove();cancel();}}}.runTaskTimer(plugin,1,1);}catch(Throwable ignored){}}
    private void particle(World w,String name,Location l,int count,double ox,double oy,double oz,double extra){try{Particle p=Particle.valueOf(name);w.spawnParticle(p,l,count,ox,oy,oz,extra);}catch(Throwable ignored){}}
    private void ring(World w,Location c,String name,double r,int points,double phase){for(int i=0;i<points;i++){double a=Math.PI*2*i/points+phase;particle(w,name,c.clone().add(Math.cos(a)*r,.15,Math.sin(a)*r),1,.02,.02,.02,0);}}
    private float yaw(Vector v){Vector n=v.clone().normalize();return(float)Math.toDegrees(Math.atan2(-n.getX(),n.getZ()));}private float pitch(Vector v){Vector n=v.clone().normalize();return(float)Math.toDegrees(-Math.asin(Math.max(-1,Math.min(1,n.getY()))));}
    private void bar(Player p,String s){try{p.sendActionBar(Component.text(s));}catch(Throwable ignored){p.sendMessage("§6[LegendaryRais] §f"+s);}}
}

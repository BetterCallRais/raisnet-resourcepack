package id.raisnet.legendaryrais;

import net.kyori.adventure.text.Component;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.attribute.AttributeInstance;
import org.bukkit.attribute.AttributeModifier;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.InventoryDragEvent;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.Action;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityShootBowEvent;
import org.bukkit.event.entity.ProjectileHitEvent;
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
 * v3.5 Legend GUI + FX Overhaul: 3D Java armor overlays, real MAX_HEALTH, weapon passives, unique armor skills and Bedrock parity. The two premium water relics remain in LegendaryRais core
 * and intentionally keep dramatically higher damage than every item in this class.
 */
public final class ArsenalExpansion implements Listener, CommandExecutor, TabCompleter {
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

    private static final String LEGEND_MENU_TITLE = "§0✦ Legendary Arsenal ✦";
    private final JavaPlugin plugin;
    private final NamespacedKey weaponKey, armorSetKey, armorPieceKey, armorHealthBaseKey, armorHealthMarkerKey, stormArrowKey, stormArrowTierKey;
    private final Map<UUID, Map<String,Long>> cooldowns = new ConcurrentHashMap<>();
    private final Set<UUID> internalDamage = Collections.newSetFromMap(new ConcurrentHashMap<>());
    private final Map<UUID,Map<String,Integer>> weaponPassiveStacks = new ConcurrentHashMap<>();
    private final Map<UUID,Map<String,ItemDisplay>> armorVisuals = new ConcurrentHashMap<>();

    public ArsenalExpansion(JavaPlugin plugin) {
        this.plugin=plugin;
        this.weaponKey=new NamespacedKey(plugin,"weapon_id");
        this.armorSetKey=new NamespacedKey(plugin,"armor_set");
        this.armorPieceKey=new NamespacedKey(plugin,"armor_piece");
        this.armorHealthBaseKey=new NamespacedKey(plugin,"armor_health_base");
        this.armorHealthMarkerKey=new NamespacedKey(plugin,"armor_health_active");
        this.stormArrowKey=new NamespacedKey(plugin,"stormpiercer_arrow");
        this.stormArrowTierKey=new NamespacedKey(plugin,"stormpiercer_arrow_tier");
    }

    public void enable() {
        Bukkit.getPluginManager().registerEvents(this,plugin);
        PluginCommand give=plugin.getCommand("risgive"); if(give!=null){give.setExecutor(this);give.setTabCompleter(this);}
        PluginCommand legend=plugin.getCommand("rislegend"); if(legend!=null){legend.setExecutor(this);legend.setTabCompleter(this);}
        startArmorPassiveTask();
        clearAllArmorVisuals(); // v3.5.2: detached ItemDisplay armor overlay removed; use real equippable model.
        runSelfCheck();
    }

    @Override public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        if(cmd.getName().equalsIgnoreCase("rislegend")){
            if(!(sender instanceof Player p)){sender.sendMessage("§c/rislegend hanya bisa dibuka oleh player.");return true;}
            if(!p.isOp()&&!p.hasPermission("legendaryrais.legend")&&!p.hasPermission("legendaryrais.admin")){
                p.sendMessage("§cNo permission: legendaryrais.legend");return true;
            }
            openLegendMenu(p);return true;
        }
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

    @Override public List<String> onTabComplete(CommandSender sender,Command cmd,String alias,String[] args){
        if(cmd.getName().equalsIgnoreCase("rislegend"))return Collections.emptyList();
        if(!cmd.getName().equalsIgnoreCase("risgive"))return Collections.emptyList();
        if(args.length==1){
            String q=args[0].toLowerCase(Locale.ROOT);
            return Bukkit.getOnlinePlayers().stream().map(Player::getName).filter(n->n.toLowerCase(Locale.ROOT).startsWith(q)).sorted().toList();
        }
        if(args.length==2){
            String q=args[1].toLowerCase(Locale.ROOT);
            return List.of("soul_tide","leviathan","emberfall","noctis","stormpiercer","gaia","astral","phoenix_set","voidwalker_set","titan_set","celestial_set","water_sovereign_set")
                    .stream().filter(x->x.startsWith(q)).toList();
        }
        return Collections.emptyList();
    }

    private void openLegendMenu(Player p){
        Inventory inv=Bukkit.createInventory(null,54,LEGEND_MENU_TITLE);
        ItemStack filler=menuItem(Material.BLACK_STAINED_GLASS_PANE,"§0 ",List.of());
        for(int i=0;i<inv.getSize();i++)inv.setItem(i,filler);

        inv.setItem(4,menuItem(Material.NETHER_STAR,"§d§lLEGENDARY ARSENAL §f§lV3.5",List.of(
                "§7Semua weapon + armor LegendaryRais.",
                "§aKlik item untuk mengambilnya.",
                "§bArmor set = langsung 4 piece.",
                "§8Semua item: unbreakable.")));

        if(plugin instanceof LegendaryRais core){
            ItemStack soul=core.createSoulTideKatana(true);appendLore(soul,List.of("","§aLEFT CLICK §7→ Ambil Soul Tide"));
            ItemStack levi=core.createLeviathanTrident(true);appendLore(levi,List.of("","§aLEFT CLICK §7→ Ambil Leviathan"));
            inv.setItem(10,soul);inv.setItem(11,levi);
        }
        inv.setItem(13,menuWeapon(EMBERFALL));inv.setItem(14,menuWeapon(NOCTIS));inv.setItem(15,menuWeapon(STORMPIERCER));inv.setItem(16,menuWeapon(GAIA));inv.setItem(17,menuWeapon(ASTRAL));

        inv.setItem(28,menuArmorSet(PHOENIX));inv.setItem(29,menuArmorSet(VOIDWALKER));inv.setItem(30,menuArmorSet(TITAN));inv.setItem(31,menuArmorSet(CELESTIAL));inv.setItem(32,menuArmorSet(WATER_SOVEREIGN));
        inv.setItem(49,menuItem(Material.BARRIER,"§cClose",List.of("§7Klik untuk menutup menu.")));
        p.openInventory(inv);
    }

    private ItemStack menuWeapon(String id){
        ItemStack i=createWeapon(id);appendLore(i,List.of("","§aLEFT CLICK §7→ Ambil weapon","§8Unbreakable • Legendary"));return i;
    }
    private ItemStack menuArmorSet(String set){
        ItemStack i=createArmorPiece(set,"chest");appendLore(i,List.of("","§aLEFT CLICK §7→ Ambil FULL SET","§7Helmet + Chest + Legs + Boots","§8Unbreakable • Legendary Defense"));return i;
    }
    private ItemStack menuItem(Material mat,String name,List<String> lore){
        ItemStack i=new ItemStack(mat);ItemMeta m=i.getItemMeta();if(m!=null){m.setDisplayName(name);m.setLore(lore);i.setItemMeta(m);}return i;
    }
    private void appendLore(ItemStack i,List<String> extra){
        ItemMeta m=i.getItemMeta();if(m==null)return;List<String> lore=m.getLore()==null?new ArrayList<>():new ArrayList<>(m.getLore());lore.addAll(extra);m.setLore(lore);i.setItemMeta(m);
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void legendMenuClick(InventoryClickEvent e){
        if(!LEGEND_MENU_TITLE.equals(e.getView().getTitle()))return;
        e.setCancelled(true);
        if(!(e.getWhoClicked() instanceof Player p))return;
        int slot=e.getRawSlot();
        if(slot==49){p.closeInventory();return;}
        if(plugin instanceof LegendaryRais core){
            if(slot==10){giveSafe(p,core.createSoulTideKatana(false));legendPickupFx(p,"§bSoul Tide Sovereign Blade");return;}
            if(slot==11){giveSafe(p,core.createLeviathanTrident(false));legendPickupFx(p,"§3Abyss Leviathan Trident");return;}
        }
        String wid=switch(slot){case 13->EMBERFALL;case 14->NOCTIS;case 15->STORMPIERCER;case 16->GAIA;case 17->ASTRAL;default->null;};
        if(wid!=null){giveSafe(p,createWeapon(wid));legendPickupFx(p,"§e"+wid);return;}
        String set=switch(slot){case 28->PHOENIX;case 29->VOIDWALKER;case 30->TITAN;case 31->CELESTIAL;case 32->WATER_SOVEREIGN;default->null;};
        if(set!=null){for(String piece:List.of("helmet","chest","legs","boots"))giveSafe(p,createArmorPiece(set,piece));legendPickupFx(p,"§6"+set.toUpperCase(Locale.ROOT)+" SET");}
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void legendMenuDrag(InventoryDragEvent e){
        if(!LEGEND_MENU_TITLE.equals(e.getView().getTitle()))return;
        for(int raw:e.getRawSlots())if(raw<e.getView().getTopInventory().getSize()){e.setCancelled(true);return;}
    }

    private void legendPickupFx(Player p,String what){
        Location c=p.getLocation().clone().add(0,1.0,0);
        particle(p.getWorld(),"END_ROD",c,24,.45,.7,.45,.05);sound(p.getWorld(),c,"minecraft:block.amethyst_block.chime",.9f,1.4f);
        p.sendMessage("§6✦ §aDiambil dari /rislegend: "+what);
    }

    private String normalize(String raw){String x=raw.toLowerCase(Locale.ROOT).replace('-','_');return switch(x){
        case "soultide","soul","soul_tide","sovereign"->"soul_tide"; case "trident","leviathan","abyss"->"leviathan";
        case "ember","emberfall"->"emberfall"; case "noctis","reaper"->"noctis"; case "storm","stormpiercer","bow"->"stormpiercer";
        case "gaia","thorn"->"gaia"; case "astral","katars","rift"->"astral"; case "phoenix","phoenix_set"->"phoenix_set";
        case "void","voidwalker","voidwalker_set"->"voidwalker_set"; case "titan","titan_set"->"titan_set"; case "celestial","celestial_set"->"celestial_set";
        case "water","water_set","water_sovereign","water_sovereign_set","abyssal_regalia"->"water_sovereign_set"; default->x;};}

    private boolean giveById(Player p,String id,int amount){
        if(id.equals("soul_tide")||id.equals("leviathan")){
            if(!(plugin instanceof LegendaryRais core))return false;
            for(int n=0;n<amount;n++)giveSafe(p,id.equals("soul_tide")?core.createSoulTideKatana(false):core.createLeviathanTrident(false));
            return true;
        }
        if(id.endsWith("_set")){String set=id.substring(0,id.length()-4);if(!Set.of(PHOENIX,VOIDWALKER,TITAN,CELESTIAL,WATER_SOVEREIGN).contains(set))return false;for(int n=0;n<amount;n++)for(String piece:List.of("helmet","chest","legs","boots"))giveSafe(p,createArmorPiece(set,piece));return true;}
        String wid=switch(id){case "emberfall"->EMBERFALL;case "noctis"->NOCTIS;case "stormpiercer"->STORMPIERCER;case "gaia"->GAIA;case "astral"->ASTRAL;default->null;};
        if(wid==null)return false;for(int n=0;n<amount;n++)giveSafe(p,createWeapon(wid));return true;
    }
    private void giveSafe(Player p,ItemStack item){Map<Integer,ItemStack> left=p.getInventory().addItem(item);for(ItemStack x:left.values())p.getWorld().dropItemNaturally(p.getLocation(),x);}

    private ItemStack createWeapon(String id){Material mat;String name,model;int cmd;List<String> lore;
        switch(id){
            case EMBERFALL->{mat=Material.NETHERITE_SWORD;name="§6§lEMBERFALL §c§lCLAYMORE";model="emberfall_claymore";cmd=EMBERFALL_CMD;lore=List.of("§7Free-Gacha Legendary • Realistic two-handed volcanic claymore.","","§6I §fBlazing Cleave §8• §7Right Click","§cII §fCinder Rush §8• §7Sneak + Left Click","§4III §fMeteor Breaker §8• §7Sneak + Right Click","","§6Passive §8• §fHeatbreaker §7• every 3 melee hits ignites an AOE burst.","§7Damage: §eLegendary Gacha §8≪ Premium Water");}
            case NOCTIS->{mat=Material.NETHERITE_SWORD;name="§5§lNOCTIS §8§lLONGSWORD";model="noctis_longsword";cmd=NOCTIS_CMD;lore=List.of("§7Free-Gacha Legendary • Black knight longsword with an eclipse edge.","","§5I §fShadow Step §8• §7Right Click","§dII §fNight Sever §8• §7Sneak + Left Click","§8III §fEclipse Lock §8• §7Sneak + Right Click","","§5Passive §8• §fExecution Mark §7• every 2 hits executes a shadow strike.","§7Damage: §eLegendary Gacha");}
            case STORMPIERCER->{mat=Material.BOW;name="§f§lSTORMPIERCER §b§lTEMPEST BOW";model="stormpiercer_recurve_bow";cmd=STORM_CMD;lore=List.of("§7Free-Gacha Legendary • Sleek storm-forged war bow.","","§bI §fExplosive Arrow §8• §7Draw + shoot normally","§7Arrow meledak saat mengenai entity / block, tanpa menghancurkan block.","§fII §fThunder Volley §8• §7Sneak + Left Click","§9III §fTempest Mark §8• §7Sneak + Right Click","","§bPassive §8• §fStatic Charge §7• every skill cast charges the next lightning hit.","§7Basic shot memakai arrow seperti bow normal.");}
            case GAIA->{mat=Material.NETHERITE_SHOVEL;name="§2§lGAIA §a§lWAR SPEAR";model="gaia_war_spear";cmd=GAIA_CMD;lore=List.of("§7Free-Gacha Legendary • Realistic leaf-bladed war spear with an ancient oak haft.","","§2I §fRoot Thrust §8• §7Right Click","§aII §fStonewake §8• §7Sneak + Left Click","§6III §fEarthshatter Line §8• §7Sneak + Right Click","","§2Passive §8• §fAncient Bark §7• melee stacks grant guard and root burst.","§7Damage: §eLegendary Gacha");}
            case ASTRAL->{mat=Material.SHEARS;name="§d§lASTRAL §5§lTWIN DAGGERS";model="astral_twin_daggers";cmd=ASTRAL_CMD;lore=List.of("§7Free-Gacha Legendary • Paired realistic daggers forged around a small rift.","","§dI §fRift Dash §8• §7Right Click","§fII §fStar Fang §8• §7Sneak + Left Click","§5III §fAstral Rend §8• §7Sneak + Right Click","","§dPassive §8• §fPhase Combo §7• every 4 melee hits blinks through the target.","§7Damage: §eLegendary Gacha");}
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
        lore.add("§9🛡 Defense: §f+"+formatStat(armorDefensePerPiece(set))+" Armor §8/ §f+"+formatStat(armorToughnessPerPiece(set))+" Toughness");
        lore.add("§b✦ Full set unlocks passive aura + active skill.");

        m.setDisplayName(color+"§l"+title+" §8• §f"+piece.toUpperCase(Locale.ROOT));
        m.setLore(lore);
        applyVisual(m,armorCmd(set,piece),"armor/"+set+"_"+piece);

        // Explicit slot + swappable fixes right-click equipping on modern Paper.
        try{
            var eq=m.getEquippable();
            eq.setSlot(armorSlot(piece));
            eq.setModel(new NamespacedKey("legendaryv34",set+"_set"));
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

    private double armorDefensePerPiece(String set){return switch(set){case PHOENIX->4.0;case VOIDWALKER->2.0;case TITAN->2.5;case CELESTIAL->3.0;case WATER_SOVEREIGN->2.5;default->0.0;};}
    private double armorToughnessPerPiece(String set){return switch(set){case PHOENIX,VOIDWALKER,CELESTIAL->2.0;case TITAN->3.0;case WATER_SOVEREIGN->4.0;default->0.0;};}
    private double armorKbPerPiece(String set){return switch(set){case PHOENIX,CELESTIAL->.02;case VOIDWALKER->.03;case TITAN->.04;case WATER_SOVEREIGN->.05;default->0.0;};}
    private String formatStat(double x){return String.format(Locale.US,"%.2f",x).replaceAll("\\.?0+$","");}

    private double[] legendaryArmorBonuses(Player p){
        double hp=0,armor=0,tough=0,kb=0;
        ItemStack[] worn={p.getInventory().getHelmet(),p.getInventory().getChestplate(),p.getInventory().getLeggings(),p.getInventory().getBoots()};
        for(ItemStack i:worn){
            if(i==null||i.getType()==Material.AIR)continue;
            ItemMeta m=i.getItemMeta();if(m==null)continue;
            String set=m.getPersistentDataContainer().get(armorSetKey,PersistentDataType.STRING);if(set==null)continue;
            hp+=armorHealthPerPiece(set);armor+=armorDefensePerPiece(set);tough+=armorToughnessPerPiece(set);kb+=armorKbPerPiece(set);
        }
        return new double[]{hp,armor,tough,kb};
    }

    private void syncBonusAttribute(Player p,Attribute attribute,String keyName,double amount){
        AttributeInstance inst=p.getAttribute(attribute);if(inst==null)return;
        NamespacedKey key=new NamespacedKey(plugin,keyName);
        for(AttributeModifier mod:new ArrayList<>(inst.getModifiers()))if(mod.getKey().equals(key))inst.removeModifier(mod);
        if(amount>0)inst.addTransientModifier(new AttributeModifier(key,amount,AttributeModifier.Operation.ADD_NUMBER));
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
            AttributeInstance max=p.getAttribute(Attribute.MAX_HEALTH);
            if(max==null)return;

            // Clean the old v3.5 setMaxHealth migration if it exists.
            PersistentDataContainer data=p.getPersistentDataContainer();
            Double legacyBase=data.get(armorHealthBaseKey,PersistentDataType.DOUBLE);
            if(legacyBase!=null){
                max.setBaseValue(Math.max(1.0,legacyBase));
                data.remove(armorHealthBaseKey);
                data.remove(armorHealthMarkerKey);
            }

            NamespacedKey oldKey=new NamespacedKey(plugin,"armor_health_bonus_v33");
            NamespacedKey key=new NamespacedKey(plugin,"armor_health_bonus_v34");
            for(AttributeModifier mod:new ArrayList<>(max.getModifiers())){
                if(mod.getKey().equals(oldKey)||mod.getKey().equals(key))max.removeModifier(mod);
            }

            double[] bonuses=legendaryArmorBonuses(p);
            double bonus=bonuses[0];
            if(bonus>0.0)max.addTransientModifier(new AttributeModifier(key,bonus,AttributeModifier.Operation.ADD_NUMBER));
            syncBonusAttribute(p,Attribute.ARMOR,"legend_armor_v35",bonuses[1]);
            syncBonusAttribute(p,Attribute.ARMOR_TOUGHNESS,"legend_toughness_v35",bonuses[2]);
            syncBonusAttribute(p,Attribute.KNOCKBACK_RESISTANCE,"legend_knockback_v35",bonuses[3]);

            double finalMax=max.getValue();
            if(p.getHealth()>finalMax)p.setHealth(Math.max(1.0,finalMax));
        }catch(Throwable ex){
            plugin.getLogger().warning("Legendary armor MAX_HEALTH sync failed for "+p.getName()+": "+ex.getMessage());
        }
    }

    @EventHandler public void armorHealthJoin(PlayerJoinEvent e){
        Bukkit.getScheduler().runTask(plugin,()->syncLegendaryHealth(e.getPlayer()));
    }

    @EventHandler(ignoreCancelled=false) public void armorHealthInventoryClick(InventoryClickEvent e){
        if(e.getWhoClicked() instanceof Player p)Bukkit.getScheduler().runTask(plugin,()->syncLegendaryHealth(p));
    }

    @EventHandler(ignoreCancelled=false) public void armorHealthInventoryDrag(InventoryDragEvent e){
        if(e.getWhoClicked() instanceof Player p)Bukkit.getScheduler().runTask(plugin,()->syncLegendaryHealth(p));
    }

    @EventHandler public void armorHealthBreak(PlayerItemBreakEvent e){
        Bukkit.getScheduler().runTask(plugin,()->syncLegendaryHealth(e.getPlayer()));
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

    private void applyVisual(ItemMeta m,int cmd,String model){m.setUnbreakable(true);try{m.setCustomModelData(cmd);}catch(Throwable ignored){}try{m.setItemModel(new NamespacedKey("legendaryv34",model));}catch(Throwable ignored){}try{m.setEnchantmentGlintOverride(true);}catch(Throwable ignored){}}
    private String weaponId(ItemStack item){if(item==null||item.getType()==Material.AIR)return "";ItemMeta m=item.getItemMeta();if(m==null)return "";String id=m.getPersistentDataContainer().get(weaponKey,PersistentDataType.STRING);return id==null?"":id;}
    private boolean expansionWeapon(String id){return Set.of(EMBERFALL,NOCTIS,STORMPIERCER,GAIA,ASTRAL).contains(id);}

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void protectLegendaryDurability(PlayerItemDamageEvent e){
        ItemStack i=e.getItem();ItemMeta m=i.getItemMeta();if(m==null)return;
        String wid=m.getPersistentDataContainer().get(weaponKey,PersistentDataType.STRING);
        String set=m.getPersistentDataContainer().get(armorSetKey,PersistentDataType.STRING);
        if(wid==null&&set==null)return;
        if(!m.isUnbreakable()){m.setUnbreakable(true);i.setItemMeta(m);}
        e.setCancelled(true);
    }

    private void runSelfCheck(){
        List<String> errors=new ArrayList<>();int checked=0;
        if(plugin.getCommand("rislegend")==null)errors.add("/rislegend missing from plugin.yml");
        if(plugin.getCommand("risgive")==null)errors.add("/risgive missing from plugin.yml");

        for(String id:List.of(EMBERFALL,NOCTIS,STORMPIERCER,GAIA,ASTRAL)){
            ItemStack i=createWeapon(id);checked++;
            ItemMeta m=i.getItemMeta();
            if(m==null||!m.isUnbreakable())errors.add("weapon "+id+" not unbreakable");
            if(m==null||!id.equals(m.getPersistentDataContainer().get(weaponKey,PersistentDataType.STRING)))errors.add("weapon "+id+" missing PDC");
        }

        for(String set:List.of(PHOENIX,VOIDWALKER,TITAN,CELESTIAL,WATER_SOVEREIGN))for(String piece:List.of("helmet","chest","legs","boots")){
            ItemStack i=createArmorPiece(set,piece);checked++;ItemMeta m=i.getItemMeta();
            if(m==null||!m.isUnbreakable())errors.add("armor "+set+"/"+piece+" not unbreakable");
            if(m==null||!set.equals(m.getPersistentDataContainer().get(armorSetKey,PersistentDataType.STRING)))errors.add("armor "+set+"/"+piece+" missing set PDC");
            if(i.getType()!=armorMaterial(set,piece))errors.add("armor "+set+"/"+piece+" wrong material");
            if(armorHealthPerPiece(set)<=0||armorDefensePerPiece(set)<=0||armorToughnessPerPiece(set)<=0)errors.add("armor "+set+" has invalid legendary stats");
            if(m!=null)try{
                Object eq=m.getEquippable();
                Object slot=eq.getClass().getMethod("getSlot").invoke(eq);
                if(slot!=armorSlot(piece))errors.add("armor "+set+"/"+piece+" wrong equip slot: "+slot);
            }catch(Throwable ex){errors.add("armor "+set+"/"+piece+" equippable validation failed");}
        }

        if(plugin instanceof LegendaryRais core){
            for(ItemStack i:List.of(core.createSoulTideKatana(false),core.createLeviathanTrident(false))){
                checked++;ItemMeta m=i.getItemMeta();if(m==null||!m.isUnbreakable())errors.add("premium Water relic not unbreakable");
            }
        }
        if(errors.isEmpty())plugin.getLogger().info("[SELF-CHECK] PASS • "+checked+" definitions • GUI registered • equip slots valid • Legendary stats valid • unbreakable.");
        else plugin.getLogger().severe("[SELF-CHECK] FAIL • "+errors.size()+" issue(s): "+String.join(" | ",errors));
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false) public void interact(PlayerInteractEvent e){
        if(e.getHand()!=null&&e.getHand()!=EquipmentSlot.HAND)return;
        Player p=e.getPlayer();
        String id=weaponId(p.getInventory().getItemInMainHand());
        if(!expansionWeapon(id))return;
        Action a=e.getAction();
        boolean right=a==Action.RIGHT_CLICK_AIR||a==Action.RIGHT_CLICK_BLOCK,left=a==Action.LEFT_CLICK_AIR||a==Action.LEFT_CLICK_BLOCK;
        if(STORMPIERCER.equals(id)){
            // v3.5.2: normal right click must remain vanilla bow draw/use.
            if(p.isSneaking()&&right){e.setCancelled(true);cast(p,id,3);}
            else if(p.isSneaking()&&left){e.setCancelled(true);cast(p,id,2);}
            return;
        }
        if(p.isSneaking()&&right){e.setCancelled(true);cast(p,id,3);}
        else if(p.isSneaking()&&left){e.setCancelled(true);cast(p,id,2);}
        else if(!p.isSneaking()&&right){e.setCancelled(true);cast(p,id,1);}
    }

    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true)
    public void stormpiercerShoot(EntityShootBowEvent e){
        if(!(e.getEntity() instanceof Player p))return;
        ItemStack bow=e.getBow();
        if(bow==null||!STORMPIERCER.equals(weaponId(bow)))return;
        if(e.getProjectile() instanceof AbstractArrow arrow){
            markStormArrow(arrow,1);
            arrow.setCritical(true);
            arrow.setPickupStatus(AbstractArrow.PickupStatus.DISALLOWED);
            bar(p,"STORMPIERCER • EXPLOSIVE ARROW");
        }
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void stormpiercerImpact(ProjectileHitEvent e){
        if(!(e.getEntity() instanceof AbstractArrow arrow))return;
        Integer tier=arrow.getPersistentDataContainer().get(stormArrowTierKey,PersistentDataType.INTEGER);
        if(tier==null||!arrow.getPersistentDataContainer().has(stormArrowKey,PersistentDataType.BYTE))return;
        if(!(arrow.getShooter() instanceof Player p))return;
        Location hit=arrow.getLocation().clone();
        World w=hit.getWorld(); if(w==null)return;
        double radius=tier>=2?3.8:3.25;
        double dmg=tier>=2?38.0:65.0;
        particle(w,"EXPLOSION_EMITTER",hit,1,.05,.05,.05,0);
        particle(w,"ELECTRIC_SPARK",hit,48,radius*.35,.7,radius*.35,.12);
        pulse(w,hit.clone().add(0,.25,0),"fx_thunderhead",FX_THUNDER,tier>=2?2.5f:2.1f,10,0,0);
        w.strikeLightningEffect(hit);
        sound(w,hit,"minecraft:entity.generic.explode",1.15f,tier>=2?.9f:1.05f);
        for(Entity ent:w.getNearbyEntities(hit,radius,radius,radius)){
            if(ent instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId()))hurt(l,dmg,p);
        }
        arrow.remove();
    }

    private void markStormArrow(AbstractArrow arrow,int tier){
        arrow.getPersistentDataContainer().set(stormArrowKey,PersistentDataType.BYTE,(byte)1);
        arrow.getPersistentDataContainer().set(stormArrowTierKey,PersistentDataType.INTEGER,tier);
    }

    private void launchStormVolleyArrow(Player p,Vector velocity,int tier){
        Arrow a=p.launchProjectile(Arrow.class,velocity);
        a.setCritical(true);
        a.setPickupStatus(AbstractArrow.PickupStatus.DISALLOWED);
        markStormArrow(a,tier);
    }
    @EventHandler(ignoreCancelled=true) public void melee(EntityDamageByEntityEvent e){if(!(e.getDamager() instanceof Player p)||!(e.getEntity() instanceof LivingEntity t))return;String id=weaponId(p.getInventory().getItemInMainHand());if(!expansionWeapon(id))return;if(internalDamage.contains(t.getUniqueId()))return;e.setDamage(Math.max(e.getDamage(),baseDamage(id)));hitFx(t,id);weaponPassive(p,t,id);if(p.isSneaking()){e.setCancelled(true);cast(p,id,2);}}
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
    private void cast(Player p,String id,int skill){
        if(!ready(p,id+":"+skill,skillCd(skill),"Skill "+skill))return;
        weaponCastSignature(p,id,skill);
        cinematicWeaponFx(p,id,skill);
        switch(id){case EMBERFALL->ember(p,skill);case NOCTIS->noctis(p,skill);case STORMPIERCER->storm(p,skill);case GAIA->gaia(p,skill);case ASTRAL->astral(p,skill);}
    }

    private int passiveStack(Player p,String id,int threshold){
        Map<String,Integer> map=weaponPassiveStacks.computeIfAbsent(p.getUniqueId(),u->new ConcurrentHashMap<>());
        int n=map.getOrDefault(id,0)+1;
        if(n>=threshold){map.put(id,0);return threshold;}
        map.put(id,n);return n;
    }

    private void weaponPassive(Player p,LivingEntity t,String id){
        World w=p.getWorld(); Location hit=t.getLocation().clone().add(0,1,0);
        switch(id){
            case EMBERFALL->{
                if(passiveStack(p,id,3)<3)return;
                pulse(w,hit,"fx_inferno_crown",FX_INFERNO,2.4f,10,p.getLocation().getYaw(),0);
                particle(w,"FLAME",hit,45,.65,.65,.65,.08);
                for(Entity e:w.getNearbyEntities(hit,2.8,2.4,2.8))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,18,p);l.setFireTicks(Math.max(l.getFireTicks(),70));}
                sound(w,hit,"minecraft:item.firecharge.use",1.0f,.78f);
                bar(p,"HEATBREAKER • AOE IGNITION");
            }
            case NOCTIS->{
                if(passiveStack(p,id,2)<2)return;
                pulse(w,hit,"fx_soul_harvest",FX_HARVEST,2.0f,9,180,0);
                hurt(t,18,p); p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+2.0));
                try{t.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.DARKNESS,45,0,true,false,false));}catch(Throwable ignored){}
                sound(w,hit,"minecraft:entity.warden.heartbeat",.6f,1.4f);
                bar(p,"EXECUTION MARK • SHADOW STRIKE");
            }
            case GAIA->{
                int n=passiveStack(p,id,3);
                try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,50,0,true,false,false));}catch(Throwable ignored){}
                if(n<3)return;
                pulse(w,hit,"fx_rootline",FX_ROOT,2.2f,10,0,0);
                try{t.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,55,6,true,false,false));}catch(Throwable ignored){}
                hurt(t,14,p); particle(w,"COMPOSTER",hit,30,.6,.4,.6,.03);
                bar(p,"ANCIENT BARK • ROOT BURST");
            }
            case ASTRAL->{
                if(passiveStack(p,id,4)<4)return;
                Vector dir=t.getLocation().getDirection().clone();dir.setY(0);if(dir.lengthSquared()<.01)dir=new Vector(0,0,1);else dir.normalize();
                Location behind=t.getLocation().clone().subtract(dir.multiply(1.45));
                if(!behind.getBlock().getType().isSolid()&&!behind.clone().add(0,1,0).getBlock().getType().isSolid())p.teleport(behind);
                pulse(w,hit,"fx_rift_blink",FX_RIFT,2.2f,10,90,0);hurt(t,22,p);
                sound(w,hit,"minecraft:entity.enderman.teleport",.8f,1.6f);bar(p,"PHASE COMBO • RIFT THROUGH");
            }
            default->{}
        }
    }

    private void weaponCastSignature(Player p,String id,int skill){
        if(!STORMPIERCER.equals(id))return;
        int n=passiveStack(p,"storm_static",3);
        if(n<3)return;
        Location c=p.getLocation().clone().add(0,1.2,0);
        particle(p.getWorld(),"ELECTRIC_SPARK",c,38,.7,.8,.7,.08);
        pulse(p.getWorld(),c,"fx_thunderhead",FX_THUNDER,2.1f,10,p.getLocation().getYaw(),0);
        try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SPEED,80,1,true,false,false));}catch(Throwable ignored){}
        sound(p.getWorld(),c,"minecraft:entity.lightning_bolt.thunder",.55f,1.6f);
        bar(p,"STATIC CHARGE • TEMPEST OVERDRIVE");
    }

    private void ember(Player p,int s){
        double dmg=damage(EMBERFALL,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();
        if(s==1){
            Set<UUID> hit=new HashSet<>();
            for(int k=-1;k<=1;k++){
                Vector slash=rotateY(d,Math.toRadians(k*13));
                for(int i=1;i<=10;i++){
                    Location c=p.getEyeLocation().clone().add(slash.clone().multiply(i*.85));
                    particle(w,"FLAME",c,7,.18,.14,.18,.02);
                    if(i%2==0)pulse(w,c,"fx_ember_rift",FX_EMBER_RIFT,1.1f,5,yaw(slash),pitch(slash));
                    for(Entity e:w.getNearbyEntities(c,.85,.85,.85))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId())){hurt(l,dmg,p);l.setFireTicks(70);}
                }
            }
            sound(w,p.getLocation(),"minecraft:entity.player.attack.sweep",1.2f,.65f);bar(p,"EMBERFALL • Blazing Cleave");
        }else if(s==2){
            Location from=p.getLocation().clone(),to=safeForward(p,8.5);Vector step=to.toVector().subtract(from.toVector());
            for(int i=0;i<=12;i++){Location q=from.clone().add(step.clone().multiply(i/12.0));particle(w,"FLAME",q.clone().add(0,.2,0),10,.25,.12,.25,.03);if(i%3==0)blockFx(w,q,Material.FIRE,.55f,8);}
            p.teleport(to);pulse(w,to.clone().add(0,1,0),"fx_ember_meteor",FX_EMBER_METEOR,2.8f,12,p.getLocation().getYaw(),0);
            for(Entity e:w.getNearbyEntities(to,3.5,2.5,3.5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,dmg,p);l.setFireTicks(90);Vector v=l.getLocation().toVector().subtract(to.toVector());if(v.lengthSquared()>.01)l.setVelocity(v.normalize().multiply(.55).setY(.25));}
            sound(w,to,"minecraft:item.firecharge.use",1.2f,.8f);bar(p,"EMBERFALL • Cinder Rush");
        }else{
            Location target=p.getLocation().clone().add(d.clone().multiply(7));
            pulse(w,target.clone().add(0,9,0),"fx_ember_meteor",FX_EMBER_METEOR,3.6f,24,p.getLocation().getYaw(),90);
            sound(w,target,"minecraft:entity.blaze.shoot",1.3f,.55f);
            new BukkitRunnable(){int t=0;public void run(){
                if(t++>=18){particle(w,"EXPLOSION_EMITTER",target,3,.2,.2,.2,0);pulse(w,target.clone().add(0,.5,0),"fx_inferno_crown",FX_INFERNO,5.2f,18,0,0);for(Entity e:w.getNearbyEntities(target,5,4,5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,dmg,p);l.setFireTicks(120);l.setVelocity(new Vector(0,.8,0));}cancel();return;}
                Location fall=target.clone().add(0,9-t*.5,0);particle(w,"FLAME",fall,16,.3,.3,.3,.04);
            }}.runTaskTimer(plugin,0,1);bar(p,"EMBERFALL • Meteor Breaker");
        }
    }
    private void noctis(Player p,int s){double dmg=damage(NOCTIS,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();if(s==1){Location from=p.getLocation().clone(),to=safeForward(p,6.5);for(int i=0;i<12;i++){Location q=from.clone().add(to.toVector().subtract(from.toVector()).multiply(i/11.0)).add(0,1,0);particle(w,"SCULK_SOUL",q,3,.15,.2,.15,.01);}for(Entity e:w.getNearbyEntities(from.clone().add(d.clone().multiply(3)),4,2.5,4))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId()))hurt(l,dmg,p);p.teleport(to);pulse(w,to.clone().add(0,1,0),"fx_shade_step",FX_SHADE,2.2f,10,p.getLocation().getYaw(),0);bar(p,"NOCTIS • Shadow Step");}else if(s==2){int hits=0;for(LivingEntity l:targets(p,6,6,true)){Vector n=l.getLocation().toVector().subtract(p.getLocation().toVector()).normalize();if(n.dot(d)<.25)continue;hurt(l,dmg,p);hits++;pulse(w,l.getLocation().clone().add(0,1,0),"fx_soul_harvest",FX_HARVEST,1.8f,8,0,0);}if(hits>0)p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+Math.min(10,hits*2.0)));bar(p,"NOCTIS • Night Sever • "+hits);}else{Location c=p.getLocation().clone().add(d.clone().multiply(5));new BukkitRunnable(){int t=0;public void run(){if(t++>55){cancel();return;}pulse(w,c,"fx_eclipse_cage",FX_ECLIPSE,3.3f,6,t*16,0);ring(w,c,"PORTAL",4,28,t*.12);if(t%15==0)for(Entity e:w.getNearbyEntities(c,4,3,4))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,dmg/3,p);try{l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,35,2,true,false,false));l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.DARKNESS,35,0,true,false,false));}catch(Throwable ignored){}}}}.runTaskTimer(plugin,0,1);bar(p,"NOCTIS • Eclipse Lock");}}
    private void storm(Player p,int s){
        double dmg=damage(STORMPIERCER,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();
        if(s==1){
            launchStormVolleyArrow(p,d.clone().multiply(3.25),1);
            bar(p,"STORMPIERCER • Explosive Arrow");
        }else if(s==2){
            for(int k=-2;k<=2;k++){
                Vector v=rotateY(d,Math.toRadians(k*6)).normalize().multiply(3.05);
                v.setY(v.getY()+Math.abs(k)*.015);
                launchStormVolleyArrow(p,v,2);
            }
            particle(w,"ELECTRIC_SPARK",p.getEyeLocation(),28,.45,.35,.45,.08);
            pulse(w,p.getLocation().clone().add(0,1.2,0),"fx_cyclone_volley",FX_CYCLONE,2.6f,12,p.getLocation().getYaw(),0);
            sound(w,p.getLocation(),"minecraft:entity.lightning_bolt.thunder",.7f,1.45f);
            bar(p,"STORMPIERCER • Thunder Volley • 5 EXPLOSIVE ARROWS");
        }else{
            Location c=p.getLocation().clone().add(d.clone().multiply(9));
            pulse(w,c.clone().add(0,4,0),"fx_thunderhead",FX_THUNDER,4,24,0,0);
            new BukkitRunnable(){int t=0;public void run(){
                if(t++>36){cancel();return;}
                if(t%6==0){
                    double a=t*.82;
                    Location q=c.clone().add(Math.cos(a)*2.4,0,Math.sin(a)*2.4);
                    w.strikeLightningEffect(q);
                    particle(w,"ELECTRIC_SPARK",q,34,.7,1.0,.7,.1);
                    for(Entity ent:w.getNearbyEntities(q,2.7,3,2.7))
                        if(ent instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId()))hurt(l,dmg/4,p);
                }
            }}.runTaskTimer(plugin,6,1);
            bar(p,"STORMPIERCER • Tempest Mark");
        }
    }
    private void gaia(Player p,int s){double dmg=damage(GAIA,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();if(s==1){Set<UUID> hit=new HashSet<>();for(int i=1;i<=10;i++){Location c=p.getLocation().clone().add(d.clone().multiply(i));blockFx(w,c,Material.MOSS_BLOCK,.75f,8);pulse(w,c.clone().add(0,.5,0),"fx_rootline",FX_ROOT,1.25f,6,0,0);for(Entity e:w.getNearbyEntities(c,1.1,1.5,1.1))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId())){hurt(l,dmg,p);try{l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,45,5,true,false,false));}catch(Throwable ignored){}}}bar(p,"GAIA • Root Thrust");}else if(s==2){try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,100,1,true,false,false));p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,100,1,true,false,false));}catch(Throwable ignored){}pulse(w,p.getLocation().clone().add(0,1,0),"fx_stoneguard",FX_STONE,3,18,0,0);for(Entity e:w.getNearbyEntities(p.getLocation(),3,2,3))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,dmg*.5,p);Vector v=l.getLocation().toVector().subtract(p.getLocation().toVector());if(v.lengthSquared()>.01)l.setVelocity(v.normalize().multiply(.55).setY(.25));}bar(p,"GAIA • Stonewake");}else{Set<UUID> hit=new HashSet<>();for(int i=1;i<=9;i++){Location q=p.getLocation().clone().add(d.clone().multiply(i*1.15));blockFx(w,q,Material.POINTED_DRIPSTONE,1.15f,16);pulse(w,q.clone().add(0,1.0,0),"fx_worldspike",FX_SPIKE,1.8f,10,yaw(d),0);particle(w,"COMPOSTER",q,12,.45,.25,.45,.02);for(Entity e:w.getNearbyEntities(q,1.25,2.5,1.25))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId())){hurt(l,dmg,p);l.setVelocity(new Vector(0,.82,0));}}sound(w,p.getLocation(),"minecraft:block.pointed_dripstone.land",1.2f,.65f);bar(p,"GAIA • Earthshatter Line");}}
    private void astral(Player p,int s){double dmg=damage(ASTRAL,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();if(s==1){LivingEntity t=nearest(p,8);Location from=p.getLocation().clone(),to=t!=null?t.getLocation().clone().subtract(d.clone().multiply(1.4)):safeForward(p,6);p.teleport(to);pulse(w,from.clone().add(0,1,0),"fx_rift_blink",FX_RIFT,2,10,0,0);pulse(w,to.clone().add(0,1,0),"fx_rift_blink",FX_RIFT,2.4f,10,180,0);if(t!=null)hurt(t,dmg,p);bar(p,"ASTRAL • Rift Dash");}else if(s==2){List<LivingEntity> ts=targets(p,10,6,false);for(int i=0;i<6;i++){double a=Math.PI*2*i/6;Location star=p.getLocation().clone().add(Math.cos(a)*2,1.4,Math.sin(a)*2);pulse(w,star,"fx_star_shards",FX_STAR,1,20,(float)Math.toDegrees(a),0);}new BukkitRunnable(){public void run(){int i=0;for(LivingEntity l:ts){if(l.isValid()&&!l.isDead()){hurt(l,dmg/Math.max(1,Math.min(3,ts.size())),p);pulse(w,l.getLocation().clone().add(0,1,0),"fx_star_shards",FX_STAR,1.6f,8,i++*45,0);}}}}.runTaskLater(plugin,12);bar(p,"ASTRAL • Star Fang");}else{Location c=p.getLocation().clone().add(d.clone().multiply(4));pulse(w,c.clone().add(0,1,0),"fx_dimension_rend",FX_REND,4.4f,18,p.getLocation().getYaw(),0);for(int axis=0;axis<2;axis++)for(int i=-5;i<=5;i++){Vector v=axis==0?d.clone().multiply(i):new Vector(-d.getZ(),0,d.getX()).normalize().multiply(i);particle(w,"END_ROD",c.clone().add(v).add(0,1,0),3,.1,.2,.1,.01);}for(Entity e:w.getNearbyEntities(c,5.5,3,5.5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){hurt(l,dmg,p);Vector v=l.getLocation().toVector().subtract(c.toVector());if(v.lengthSquared()>.01)l.setVelocity(v.normalize().multiply(-.35).setY(.18));}bar(p,"ASTRAL • Astral Rend");}}

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true) public void armorDrop(PlayerDropItemEvent e){Player p=e.getPlayer();if(!p.isSneaking())return;String set=fullSet(p);if(set==null)return;e.setCancelled(true);armorSkill(p,set);}
    private String fullSet(Player p){String found=null;ItemStack[] a={p.getInventory().getHelmet(),p.getInventory().getChestplate(),p.getInventory().getLeggings(),p.getInventory().getBoots()};for(ItemStack i:a){if(i==null||i.getType()==Material.AIR)return null;ItemMeta m=i.getItemMeta();if(m==null)return null;String s=m.getPersistentDataContainer().get(armorSetKey,PersistentDataType.STRING);if(s==null)return null;if(found==null)found=s;else if(!found.equals(s))return null;}return found;}
    private void cinematicWeaponFx(Player p,String id,int skill){
        World w=p.getWorld();Location base=p.getLocation().clone().add(0,1.0,0);
        int quality=Math.max(1,Math.min(4,plugin.getConfig().getInt("effects.quality",3)));
        String particle=switch(id){case EMBERFALL->"FLAME";case NOCTIS->"REVERSE_PORTAL";case STORMPIERCER->"ELECTRIC_SPARK";case GAIA->"SPORE_BLOSSOM_AIR";default->"END_ROD";};
        String model=switch(id){case EMBERFALL->skill==3?"fx_inferno_crown":skill==2?"fx_ember_meteor":"fx_ember_rift";case NOCTIS->skill==3?"fx_eclipse_cage":skill==2?"fx_soul_harvest":"fx_shade_step";case STORMPIERCER->skill==3?"fx_thunderhead":skill==2?"fx_cyclone_volley":"fx_gale_bolt";case GAIA->skill==3?"fx_worldspike":skill==2?"fx_stoneguard":"fx_rootline";default->skill==3?"fx_dimension_rend":skill==2?"fx_star_shards":"fx_rift_blink";};
        int cmd=switch(id){case EMBERFALL->skill==3?FX_INFERNO:skill==2?FX_EMBER_METEOR:FX_EMBER_RIFT;case NOCTIS->skill==3?FX_ECLIPSE:skill==2?FX_HARVEST:FX_SHADE;case STORMPIERCER->skill==3?FX_THUNDER:skill==2?FX_CYCLONE:FX_GALE;case GAIA->skill==3?FX_SPIKE:skill==2?FX_STONE:FX_ROOT;default->skill==3?FX_REND:skill==2?FX_STAR:FX_RIFT;};
        sound(w,base,switch(id){case EMBERFALL->"minecraft:entity.blaze.shoot";case NOCTIS->"minecraft:entity.warden.sonic_boom";case STORMPIERCER->"minecraft:entity.lightning_bolt.thunder";case GAIA->"minecraft:block.pointed_dripstone.land";default->"minecraft:block.amethyst_block.resonate";},.85f,skill==3?.65f:1.15f);
        new BukkitRunnable(){int t=0;public void run(){
            if(!p.isOnline()||t++>=10+skill*3){cancel();return;}
            Location c=p.getLocation().clone().add(0,1.0,0);
            double r=.75+t*.22+skill*.18;
            ring(w,c,particle,r,12+quality*6,t*.38);
            ring(w,c.clone().add(0,.55,0),particle,Math.max(.55,r*.72),10+quality*4,-t*.52);
            for(int i=0;i<quality*2;i++){
                double a=(Math.PI*2*i/(quality*2))+t*.44;
                Location q=c.clone().add(Math.cos(a)*r,.25+((i+t)%4)*.42,Math.sin(a)*r);
                particle(w,particle,q,2,.05,.05,.05,.01);
            }
            if(t%3==0)pulse(w,c.clone().add(0,.2,0),model,cmd,(float)(1.4+skill*.55+t*.045),6,p.getLocation().getYaw()+t*18,0);
            if(STORMPIERCER.equals(id)&&skill>=2&&t%5==0)w.strikeLightningEffect(c.clone().add(Math.cos(t)*r,0,Math.sin(t)*r));
            if(GAIA.equals(id)&&skill==3&&t%3==0)blockFx(w,c.clone().add(Math.cos(t*.8)*r,-1,Math.sin(t*.8)*r),Material.POINTED_DRIPSTONE,.65f,8);
        }}.runTaskTimer(plugin,0,1);
    }

    private void cinematicArmorFx(Player p,String set){
        World w=p.getWorld();Location c=p.getLocation().clone().add(0,1,0);
        String particle=switch(set){case PHOENIX->"FLAME";case VOIDWALKER->"REVERSE_PORTAL";case TITAN->"CLOUD";case WATER_SOVEREIGN->"BUBBLE_POP";default->"END_ROD";};
        String model=switch(set){case PHOENIX->"fx_phoenix_rebirth";case VOIDWALKER->"fx_void_phase";case TITAN->"fx_titan_bastion";case WATER_SOVEREIGN->"fx_water_sovereign_guard";default->"fx_celestial_sanctuary";};
        int cmd=switch(set){case PHOENIX->FX_PHOENIX;case VOIDWALKER->FX_VOID;case TITAN->FX_TITAN;case WATER_SOVEREIGN->FX_WATER_ARMOR;default->FX_CELESTIAL;};
        new BukkitRunnable(){int t=0;public void run(){
            if(!p.isOnline()||t++>=18){cancel();return;}
            Location q=p.getLocation().clone().add(0,1,0);double r=1.2+t*.18;
            ring(w,q,particle,r,28,t*.34);ring(w,q.clone().add(0,.7,0),particle,Math.max(.7,r*.65),20,-t*.45);
            if(t%2==0)pulse(w,q,model,cmd,(float)(2.0+t*.13),7,p.getLocation().getYaw()+t*20,0);
        }}.runTaskTimer(plugin,0,1);
    }

    private void armorSkill(Player p,String set){
        cinematicArmorFx(p,set);
        int cd=plugin.getConfig().getInt("armor.cooldowns."+set,switch(set){case PHOENIX->45;case VOIDWALKER->32;case TITAN->40;case WATER_SOVEREIGN->30;default->38;});
        if(!ready(p,"armor:"+set,cd,armorSkillName(set)))return;
        World w=p.getWorld();

        switch(set){
            case PHOENIX->{
                Location c=p.getLocation().clone();
                sound(w,c,"minecraft:entity.blaze.shoot",1.2f,.72f);
                p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+12));
                try{
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,140,2,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.FIRE_RESISTANCE,360,0,true,false,false));
                }catch(Throwable ignored){}
                new BukkitRunnable(){int t=0;public void run(){
                    if(!p.isOnline()||t++>=18){cancel();return;}
                    Location q=p.getLocation().clone().add(0,1,0);
                    double r=.8+t*.18;
                    ring(w,q,"FLAME",r,28,t*.22);
                    if(t%3==0)pulse(w,q,"fx_phoenix_rebirth",FX_PHOENIX,(float)Math.min(5.8,1.5+r),7,t*22,0);
                    if(t==8||t==14)for(Entity e:w.getNearbyEntities(q,5,3.5,5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                        hurt(l,48,p);l.setFireTicks(100);Vector v=l.getLocation().toVector().subtract(q.toVector());if(v.lengthSquared()>.01)l.setVelocity(v.normalize().multiply(.7).setY(.32));
                    }
                }}.runTaskTimer(plugin,0,2);
            }
            case VOIDWALKER->{
                Location from=p.getLocation().clone(),to=safeForward(p,10);
                Vector path=to.toVector().subtract(from.toVector());
                sound(w,from,"minecraft:entity.enderman.teleport",1.0f,.55f);
                for(int i=0;i<=8;i++){
                    Location q=from.clone().add(path.clone().multiply(i/8.0)).add(0,1,0);
                    pulse(w,q,"fx_void_phase",FX_VOID,1.4f,10,i*35,0);
                    particle(w,"REVERSE_PORTAL",q,18,.35,.5,.35,.03);
                }
                p.teleport(to);
                try{
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.INVISIBILITY,90,0,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,90,2,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SPEED,100,2,true,false,false));
                }catch(Throwable ignored){}
                for(Entity e:w.getNearbyEntities(to,4,3,4))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                    hurt(l,55,p);
                    try{l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.DARKNESS,80,0,true,false,false));l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.WEAKNESS,80,1,true,false,false));}catch(Throwable ignored){}
                }
                sound(w,to,"minecraft:entity.enderman.teleport",1.0f,1.35f);
            }
            case TITAN->{
                Location c=p.getLocation().clone();
                sound(w,c,"minecraft:entity.iron_golem.attack",1.25f,.62f);
                try{
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,220,4,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,180,2,true,false,false));
                }catch(Throwable ignored){}
                new BukkitRunnable(){int wave=0;public void run(){
                    if(wave++>=4){cancel();return;}
                    Location q=p.getLocation().clone();
                    double r=2.2+wave*1.15;
                    ring(w,q,"CLOUD",r,32,wave*.25);
                    pulse(w,q.clone().add(0,.7,0),"fx_titan_bastion",FX_TITAN,(float)(2.8+wave*.8),12,wave*35,0);
                    for(int i=0;i<10;i++){double a=Math.PI*2*i/10;Location b=q.clone().add(Math.cos(a)*r,0,Math.sin(a)*r);blockFx(w,b,Material.DEEPSLATE,1.05f,14);}
                    for(Entity e:w.getNearbyEntities(q,r+1,3,r+1))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                        double dist=l.getLocation().distance(q);if(Math.abs(dist-r)<1.6){hurt(l,32,p);Vector v=l.getLocation().toVector().subtract(q.toVector());if(v.lengthSquared()>.01)l.setVelocity(v.normalize().multiply(.75).setY(.55));}
                    }
                }}.runTaskTimer(plugin,0,7);
            }
            case WATER_SOVEREIGN->{
                Location c=p.getLocation().clone();
                sound(w,c,"minecraft:item.trident.thunder",1.15f,.85f);
                p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+10));
                try{
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,220,4,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,180,2,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,200,2,true,false,false));
                }catch(Throwable ignored){}
                new BukkitRunnable(){int t=0;public void run(){
                    if(!p.isOnline()||t++>=12){cancel();return;}
                    Location q=p.getLocation().clone();
                    ring(w,q,"SPLASH",3.2+(t%3)*.45,36,t*.43);
                    ring(w,q.clone().add(0,.5,0),"BUBBLE_POP",2.2,24,-t*.34);
                    pulse(w,q.clone().add(0,1.1,0),"fx_water_sovereign_guard",FX_WATER_ARMOR,4.4f,9,t*28,0);
                    for(Entity e:w.getNearbyEntities(q,5,3.5,5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                        Vector away=l.getLocation().toVector().subtract(q.toVector());if(away.lengthSquared()>.01)away.normalize();
                        if(t%2==0)l.setVelocity(away.multiply(.35).setY(.18));else l.setVelocity(away.multiply(-.16).setY(.08));
                        if(t%3==0)hurt(l,16,p);
                    }
                }}.runTaskTimer(plugin,0,5);
            }
            default->{
                sound(w,p.getLocation(),"minecraft:block.amethyst_block.chime",1.2f,1.4f);
                try{
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,180,2,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,180,2,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOW_FALLING,180,0,true,false,false));
                }catch(Throwable ignored){}
                new BukkitRunnable(){int t=0;public void run(){
                    if(!p.isOnline()||t++>=8){cancel();return;}
                    Location c=p.getLocation().clone();
                    for(int i=0;i<6;i++){double a=Math.PI*2*i/6+t*.31;Location star=c.clone().add(Math.cos(a)*4,2.0+Math.sin(a*2)*.6,Math.sin(a)*4);pulse(w,star,"fx_celestial_sanctuary",FX_CELESTIAL,1.2f,8,(float)Math.toDegrees(a),0);}
                    ring(w,c,"END_ROD",4.8,32,t*.3);
                    for(Entity e:w.getNearbyEntities(c,5,4,5)){
                        if(e instanceof Player ally){if(ally.getUniqueId().equals(p.getUniqueId())||ally.hasPermission("legendaryrais.ally"))ally.setHealth(Math.min(ally.getMaxHealth(),ally.getHealth()+1.0));}
                        else if(e instanceof LivingEntity l)hurt(l,22,p);
                    }
                }}.runTaskTimer(plugin,0,8);
            }
        }
        bar(p,"ARMOR • "+armorSkillName(set));
    }
    private ItemStack armorVisualItem(String set,String piece){
        ItemStack i=new ItemStack(Material.PAPER);
        ItemMeta m=i.getItemMeta(); if(m==null)return i;
        try{m.setItemModel(new NamespacedKey("legendaryv34","armor_visual/"+set+"_"+piece));}catch(Throwable ignored){}
        m.setDisplayName("§0.");
        i.setItemMeta(m);
        return i;
    }

    private String armorSetOf(ItemStack item){
        if(item==null||item.getType()==Material.AIR)return null;
        ItemMeta m=item.getItemMeta();if(m==null)return null;
        return m.getPersistentDataContainer().get(armorSetKey,PersistentDataType.STRING);
    }

    private ItemStack wornPiece(Player p,String piece){
        return switch(piece){
            case "helmet"->p.getInventory().getHelmet();
            case "chest"->p.getInventory().getChestplate();
            case "legs"->p.getInventory().getLeggings();
            default->p.getInventory().getBoots();
        };
    }

    private void startArmorVisualTask(){
        long period=Math.max(1L,plugin.getConfig().getLong("armor.java-3d-update-ticks",2L));
        new BukkitRunnable(){public void run(){
            if(!plugin.getConfig().getBoolean("armor.java-3d-overlay",true)){clearAllArmorVisuals();return;}
            Set<UUID> online=new HashSet<>();
            for(Player p:Bukkit.getOnlinePlayers()){online.add(p.getUniqueId());syncArmorVisuals(p);}
            for(UUID id:new HashSet<>(armorVisuals.keySet()))if(!online.contains(id))clearArmorVisuals(id);
        }}.runTaskTimer(plugin,2L,period);
    }

    private void syncArmorVisuals(Player p){
        if(p.isDead()||p.getGameMode()==GameMode.SPECTATOR){clearArmorVisuals(p.getUniqueId());return;}
        Map<String,ItemDisplay> map=armorVisuals.computeIfAbsent(p.getUniqueId(),u->new ConcurrentHashMap<>());
        for(String piece:List.of("helmet","chest","legs","boots")){
            ItemStack worn=wornPiece(p,piece);String set=armorSetOf(worn);
            ItemDisplay d=map.get(piece);
            if(set==null){
                if(d!=null){d.remove();map.remove(piece);}
                continue;
            }
            String tag=set+"|"+piece;
            if(d==null||!d.isValid()||!tag.equals(d.getPersistentDataContainer().get(new NamespacedKey(plugin,"armor_visual_tag"),PersistentDataType.STRING))){
                if(d!=null)d.remove();
                Location spawn=p.getLocation().clone().add(0,armorVisualYOffset(piece),0);
                try{
                    d=p.getWorld().spawn(spawn,ItemDisplay.class);
                    d.setPersistent(false);d.setGravity(false);d.setInvulnerable(true);
                    d.setItemStack(armorVisualItem(set,piece));
                    d.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.FIXED);
                    d.setBillboard(Display.Billboard.FIXED);
                    d.setViewRange(48f);
                    d.setInterpolationDuration(2);d.setTeleportDuration(2);
                    d.setBrightness(new Display.Brightness(15,15));
                    d.getPersistentDataContainer().set(new NamespacedKey(plugin,"armor_visual_tag"),PersistentDataType.STRING,tag);
                    var tr=d.getTransformation();
                    float sc=(float)armorVisualScale(piece);
                    tr.getScale().set(sc,sc,sc);d.setTransformation(tr);
                    map.put(piece,d);
                }catch(Throwable ex){if(d!=null)d.remove();continue;}
            }
            Location loc=p.getLocation().clone().add(0,armorVisualYOffset(piece),0);
            d.teleport(loc);
            float pitch=piece.equals("helmet")?Math.max(-38f,Math.min(38f,p.getLocation().getPitch()))*.22f:0f;
            d.setRotation(p.getLocation().getYaw(),pitch);
        }
        if(map.isEmpty())armorVisuals.remove(p.getUniqueId());
    }

    private double armorVisualYOffset(String piece){return switch(piece){case "helmet"->1.67;case "chest"->1.12;case "legs"->.64;default->.16;};}
    private double armorVisualScale(String piece){return switch(piece){case "helmet"->.72;case "chest"->.82;case "legs"->.78;default->.72;};}

    private void clearArmorVisuals(UUID id){
        Map<String,ItemDisplay> map=armorVisuals.remove(id);if(map==null)return;
        for(ItemDisplay d:map.values())if(d!=null&&d.isValid())d.remove();
    }
    private void clearAllArmorVisuals(){for(UUID id:new HashSet<>(armorVisuals.keySet()))clearArmorVisuals(id);}

    @EventHandler public void armorVisualQuit(PlayerQuitEvent e){
        clearArmorVisuals(e.getPlayer().getUniqueId());
        weaponPassiveStacks.remove(e.getPlayer().getUniqueId());
    }

    private void startArmorPassiveTask(){
        new BukkitRunnable(){
            public void run(){
                for(Player p:Bukkit.getOnlinePlayers()){
                    syncLegendaryHealth(p);
                    String set=fullSet(p); if(set==null)continue;
                    Location aura=p.getLocation().clone().add(0,1.0,0);
                    switch(set){
                        case PHOENIX->{particle(p.getWorld(),"FLAME",aura,5,.35,.45,.35,.01);}
                        case VOIDWALKER->{particle(p.getWorld(),"REVERSE_PORTAL",aura,5,.35,.5,.35,.01);}
                        case TITAN->{particle(p.getWorld(),"CLOUD",aura,3,.25,.15,.25,.01);}
                        case WATER_SOVEREIGN->{particle(p.getWorld(),"BUBBLE_POP",aura,5,.35,.45,.35,.02);}
                        default->{particle(p.getWorld(),"END_ROD",aura,4,.3,.45,.3,.01);}
                    }
                    try{
                        switch(set){
                            case PHOENIX->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.FIRE_RESISTANCE,45,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.STRENGTH,45,0,true,false,false));
                                if(p.getHealth()<=p.getMaxHealth()*.50)p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,45,1,true,false,false));
                            }
                            case VOIDWALKER->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SPEED,45,1,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION,240,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.JUMP_BOOST,45,0,true,false,false));
                            }
                            case TITAN->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,45,1,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,45,1,true,false,false));
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
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.LUCK,45,0,true,false,false));
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

    private ItemStack fxItem(String model,int cmd){ItemStack i=new ItemStack(Material.PAPER);ItemMeta m=i.getItemMeta();if(m==null)return i;try{m.setCustomModelData(cmd);}catch(Throwable ignored){}try{m.setItemModel(new NamespacedKey("legendaryv34",model));}catch(Throwable ignored){}i.setItemMeta(m);return i;}
    private ItemDisplay display(World w,Location l,String model,int cmd,float scale,float yaw,float pitch){try{ItemDisplay d=w.spawn(l,ItemDisplay.class);d.setItemStack(fxItem(model,cmd));d.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.FIXED);d.setBillboard(Display.Billboard.CENTER);d.setBrightness(new Display.Brightness(15,15));d.setViewRange(64);d.setInterpolationDuration(3);d.setTeleportDuration(2);d.setRotation(yaw,pitch);var tr=d.getTransformation();tr.getScale().set(scale,scale,scale);d.setTransformation(tr);return d;}catch(Throwable ignored){return null;}}
    private void pulse(World w,Location l,String model,int cmd,float max,int life,float yaw,float pitch){ItemDisplay d=display(w,l,model,cmd,Math.max(.35f,max*.38f),yaw,pitch);if(d==null)return;new BukkitRunnable(){int t=0;public void run(){if(++t>=life||!d.isValid()){d.remove();cancel();return;}float p=t/(float)Math.max(1,life),sc=Math.max(.32f,max*(.52f+.58f*(float)Math.sin(Math.min(1,p*1.35)*Math.PI)));var tr=d.getTransformation();tr.getScale().set(sc,sc,sc);d.setTransformation(tr);d.setRotation(yaw+t*7,pitch);}}.runTaskTimer(plugin,1,1);}
    private void blockFx(World w,Location l,Material mat,float scale,int life){try{BlockDisplay d=w.spawn(l,BlockDisplay.class);d.setBlock(mat.createBlockData());d.setBrightness(new Display.Brightness(15,15));var tr=d.getTransformation();tr.getScale().set(scale,scale,scale);d.setTransformation(tr);new BukkitRunnable(){int t=0;public void run(){if(++t>=life||!d.isValid()){d.remove();cancel();}}}.runTaskTimer(plugin,1,1);}catch(Throwable ignored){}}
    private void particle(World w,String name,Location l,int count,double ox,double oy,double oz,double extra){try{Particle p=Particle.valueOf(name);w.spawnParticle(p,l,count,ox,oy,oz,extra);}catch(Throwable ignored){}}
    private void sound(World w,Location l,String key,float volume,float pitch){try{w.playSound(l,key,volume,pitch);}catch(Throwable ignored){}}
    private void ring(World w,Location c,String name,double r,int points,double phase){for(int i=0;i<points;i++){double a=Math.PI*2*i/points+phase;particle(w,name,c.clone().add(Math.cos(a)*r,.15,Math.sin(a)*r),1,.02,.02,.02,0);}}
    private float yaw(Vector v){Vector n=v.clone().normalize();return(float)Math.toDegrees(Math.atan2(-n.getX(),n.getZ()));}private float pitch(Vector v){Vector n=v.clone().normalize();return(float)Math.toDegrees(-Math.asin(Math.max(-1,Math.min(1,n.getY()))));}
    private void bar(Player p,String s){try{p.sendActionBar(Component.text(s));}catch(Throwable ignored){p.sendMessage("§6[LegendaryRais] §f"+s);}}
}

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
import org.bukkit.util.RayTraceResult;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * v3.7.0 Recovery Stable: 3D Java armor overlays, real MAX_HEALTH, weapon passives, unique armor skills and Bedrock parity. The two premium water relics remain in LegendaryRais core
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

    private static final String LEGEND_MENU_TITLE = "§0✦ Legendary Arsenal • Ascension ✦";
    private final JavaPlugin plugin;
    private enum PerfMode { AUTO, LOW, BALANCED, CINEMATIC }
    private final NamespacedKey weaponKey, armorSetKey, armorPieceKey, armorHealthBaseKey, armorHealthMarkerKey, stormArrowKey, stormArrowTierKey, perfModeKey, assetVersionKey, helmetModeKey;
    private final Map<UUID, Map<String,Long>> cooldowns = new ConcurrentHashMap<>();
    private final Set<UUID> internalDamage = Collections.newSetFromMap(new ConcurrentHashMap<>());
    private final Map<UUID,Map<String,Integer>> weaponPassiveStacks = new ConcurrentHashMap<>();
    private final Map<UUID,Map<String,ItemDisplay>> armorVisuals = new ConcurrentHashMap<>();
    private final Map<UUID,Long> armorSetProcCd = new ConcurrentHashMap<>();
    private final Map<UUID,Long> lastSneakTap = new ConcurrentHashMap<>();
    private final Map<UUID,Long> armorPunchArmedUntil = new ConcurrentHashMap<>();
    private final Map<UUID,Boolean> bedrockCache = new ConcurrentHashMap<>();
    private final Map<UUID,Long> fxBudgetWindow = new ConcurrentHashMap<>();
    private final Map<UUID,Integer> fxBudgetUsed = new ConcurrentHashMap<>();
    private final Map<UUID,Long> displayBudgetWindow = new ConcurrentHashMap<>();
    private final Map<UUID,Integer> displayBudgetUsed = new ConcurrentHashMap<>();
    private final Map<UUID,Long> windLeapSafeUntil = new ConcurrentHashMap<>();

    public ArsenalExpansion(JavaPlugin plugin) {
        this.plugin=plugin;
        this.weaponKey=new NamespacedKey(plugin,"weapon_id");
        this.armorSetKey=new NamespacedKey(plugin,"armor_set");
        this.armorPieceKey=new NamespacedKey(plugin,"armor_piece");
        this.armorHealthBaseKey=new NamespacedKey(plugin,"armor_health_base");
        this.armorHealthMarkerKey=new NamespacedKey(plugin,"armor_health_active");
        this.stormArrowKey=new NamespacedKey(plugin,"stormpiercer_arrow");
        this.stormArrowTierKey=new NamespacedKey(plugin,"stormpiercer_arrow_tier");
        this.perfModeKey=new NamespacedKey(plugin,"performance_mode");
        this.assetVersionKey=new NamespacedKey(plugin,"asset_version");
        this.helmetModeKey=new NamespacedKey(plugin,"helmet_mode");
    }

    public void enable() {
        Bukkit.getPluginManager().registerEvents(this,plugin);
        PluginCommand give=plugin.getCommand("risgive"); if(give!=null){give.setExecutor(this);give.setTabCompleter(this);}
        PluginCommand legend=plugin.getCommand("rislegend"); if(legend!=null){legend.setExecutor(this);legend.setTabCompleter(this);}
        PluginCommand perf=plugin.getCommand("risperf"); if(perf!=null){perf.setExecutor(this);perf.setTabCompleter(this);}
        PluginCommand repair=plugin.getCommand("risrepair"); if(repair!=null){repair.setExecutor(this);repair.setTabCompleter(this);}
        PluginCommand helmet=plugin.getCommand("rishelmet"); if(helmet!=null){helmet.setExecutor(this);helmet.setTabCompleter(this);}
        startArmorPassiveTask();
        purgeLegacyArmorDisplays();
        clearAllArmorVisuals();
        startArmorVisualTask();
        runSelfCheck();
    }


    private void purgeLegacyArmorDisplays(){
        NamespacedKey legacyTag=new NamespacedKey(plugin,"armor_visual_tag");
        int removed=0;
        for(World w:Bukkit.getWorlds()){
            for(Entity e:w.getEntities()){
                if(!(e instanceof ItemDisplay d))continue;
                String tag=d.getPersistentDataContainer().get(legacyTag,PersistentDataType.STRING);
                if(tag!=null){d.remove();removed++;}
            }
        }
        if(removed>0)plugin.getLogger().info("[ARMOR-CLEANUP] Removed "+removed+" legacy detached armor display(s).");
    }

    @Override public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        if(cmd.getName().equalsIgnoreCase("rishelmet")){
            if(!(sender instanceof Player p)){sender.sendMessage("§c/rishelmet hanya untuk player.");return true;}
            String current=helmetMode(p);
            String mode=args.length==0?"TOGGLE":args[0].toUpperCase(Locale.ROOT);
            if(mode.equals("STATUS")){
                p.sendMessage("§bLegendary Helmet §8• §fMode: §e"+current+" §8• §7/rishelmet open|closed|toggle");
                return true;
            }
            if(mode.equals("TOGGLE"))mode=current.equals("OPEN")?"CLOSED":"OPEN";
            if(!mode.equals("OPEN")&&!mode.equals("CLOSED")){
                p.sendMessage("§cGunakan /rishelmet <open|closed|toggle|status>");return true;
            }
            p.getPersistentDataContainer().set(helmetModeKey,PersistentDataType.STRING,mode);
            boolean applied=applyHelmetMode(p,mode);
            p.sendMessage((applied?"§a":"§e")+"Helmet mode → §f"+mode+(applied?"":" §7(preference tersimpan; pakai Legendary helmet untuk melihatnya)"));
            return true;
        }
        if(cmd.getName().equalsIgnoreCase("risrepair")){
            if(!(sender instanceof Player p)){sender.sendMessage("§c/risrepair hanya untuk player.");return true;}
            int fixed=refreshAllLegendaryItems(p);
            if(plugin instanceof LegendaryRais core) fixed += core.repairWaterItems(p);
            applyHelmetMode(p,helmetMode(p));
            syncLegendaryHealth(p);
            p.sendMessage("§aLegendaryRais repair selesai. §f"+fixed+" §aitem diperbarui ke asset v3.6.7.");
            return true;
        }
        if(cmd.getName().equalsIgnoreCase("risperf")){
            if(!(sender instanceof Player p)){sender.sendMessage("§c/risperf hanya untuk player.");return true;}
            if(args.length==0||args[0].equalsIgnoreCase("status")){
                PerfMode effective=effectivePerf(p);
                String saved=p.getPersistentDataContainer().get(perfModeKey,PersistentDataType.STRING);
                p.sendMessage("§bLegendaryRais Performance §8• §fMode: §e"+(saved==null?"AUTO":saved)+" §8→ §a"+effective+" §8• §7Bedrock: "+(isBedrock(p)?"§aYES":"§cNO"));
                p.sendMessage("§7/risperf low §8| §7balanced §8| §7cinematic §8| §7auto");
                return true;
            }
            String raw=args[0].toUpperCase(Locale.ROOT);
            try{
                PerfMode m=PerfMode.valueOf(raw);
                p.getPersistentDataContainer().set(perfModeKey,PersistentDataType.STRING,m.name());
                p.sendMessage("§aPerformance mode → §f"+m+" §8(§7effective: §e"+effectivePerf(p)+"§8)");
                return true;
            }catch(IllegalArgumentException ex){
                p.sendMessage("§cMode: low, balanced, cinematic, auto");return true;
            }
        }
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
        if(cmd.getName().equalsIgnoreCase("rishelmet")){
            if(args.length==1){String q=args[0].toLowerCase(Locale.ROOT);return List.of("open","closed","toggle","status").stream().filter(x->x.startsWith(q)).toList();}
            return Collections.emptyList();
        }
        if(cmd.getName().equalsIgnoreCase("risrepair"))return Collections.emptyList();
        if(cmd.getName().equalsIgnoreCase("risperf")){
            if(args.length==1){String q=args[0].toLowerCase(Locale.ROOT);return List.of("auto","low","balanced","cinematic","status").stream().filter(x->x.startsWith(q)).toList();}
            return Collections.emptyList();
        }
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

        inv.setItem(4,menuItem(Material.NETHER_STAR,"§d§lLEGENDARY ARSENAL §f§lV3.6.5",List.of(
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
            case EMBERFALL->{mat=Material.NETHERITE_SWORD;name="§6§lEMBERFALL §c§lCLAYMORE §8[§6FIRE§8]";model="emberfall_claymore";cmd=EMBERFALL_CMD;lore=List.of("§7Element: §6FIRE §8• §7True 3D volcanic greatsword.","","§6I §fFlame Crescent §8• §7Right Click","§cII §fInferno Rush §8• §7Sneak + Left Click","§4III §fSolar Eruption §8• §7Sneak + Right Click","","§6Passive §8• §fHeatbreaker §7• hit ke-3 memicu combustion AOE.","§7Skill tier damage: §e60% dari Water Relic.");}
            case NOCTIS->{mat=Material.NETHERITE_SWORD;name="§5§lNOCTIS §8§lLONGSWORD §8[§5VOID§8]";model="noctis_longsword";cmd=NOCTIS_CMD;lore=List.of("§7Element: §5VOID §8• §7Elegant null-forged longsword.","","§5I §fNull Step §8• §7Right Click","§dII §fGravity Rend §8• §7Sneak + Left Click","§8III §fNull Domain §8• §7Sneak + Right Click","","§5Passive §8• §fNull Mark §7• hit ke-3 memicu void collapse.","§7Skill tier damage: §e60% dari Water Relic.");}
            case STORMPIERCER->{mat=Material.BOW;name="§f§lSTORMPIERCER §b§lSOVEREIGN ARC BOW §8[§bELECTRO§8]";model="stormpiercer_recurve_bow";cmd=STORM_CMD;lore=List.of("§7Element: §bELECTRO §8• §7Vanilla bow behaviour + custom true 3D model.","","§bI §fArc Detonation §8• §7Hold/aim/release seperti bow biasa","§7Impact block/entity = pure explosion + knockback, tanpa block damage.","§fII §fChain Volley §8• §7Sneak + Left Click","§9III §fOvercharge Field §8• §7Sneak + Right Click","","§bPassive §8• §fStatic Core §7• hit ke-3 memberi electro overdrive.","§7Skill tier damage: §e60% dari Water Relic.");}
            case GAIA->{mat=Material.NETHERITE_SHOVEL;name="§f§lZEPHYA §a§lSOVEREIGN WIND SPEAR §8[§fWIND§8]";model="gaia_war_spear";cmd=GAIA_CMD;lore=List.of("§7Element: §fWIND §8• §7Long royal true 3D spear.","","§fI §fWindburst §8• §7Right Click","§aII §fSky Cutter §8• §7Sneak + Left Click","§fIII §fTempest Ascension §8• §7Sneak + Right Click","","§fPassive §8• §fTailwind §7• hit ke-4 memicu wind burst + speed.","§7Skill tier damage: §e60% dari Water Relic.");}
            case ASTRAL->{mat=Material.NETHERITE_AXE;name="§b§lASTRAL FROST §f§lGLACIAL GREATAXE §8[§bICE§8]";model="astral_frost_greataxe";cmd=ASTRAL_CMD;lore=List.of("§7Element: §bICE §8• §7Long two-handed crystalline great axe.","","§bI §fFrost Cleave §8• §7Right Click","§fII §fGlacier Fang §8• §7Sneak + Left Click","§bIII §fAbsolute Zero §8• §7Sneak + Right Click","","§bPassive §8• §fFrostbite §7• hit ke-3 freeze + shatter target.","§7Skill tier damage: §e60% dari Water Relic.");}
            default->{return new ItemStack(Material.BARRIER);}}
        ItemStack item=new ItemStack(mat);ItemMeta m=item.getItemMeta();if(m==null)return item;m.setDisplayName(name);m.setLore(lore);applyWeaponVisualV368(m,cmd,model);m.getPersistentDataContainer().set(weaponKey,PersistentDataType.STRING,id);m.getPersistentDataContainer().set(assetVersionKey,PersistentDataType.INTEGER,370);item.setItemMeta(m);return item;
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
        lore.add("§eSkill I: §f"+armorPunchSkillName(set));
        lore.add("§7Double Sneak §8→ §fTangan kosong §8→ §cPukul target");
        lore.add("§eSkill II: §f"+armorUtilitySkillName(set));
        lore.add("§7Double Sneak §8→ §fKlik kanan");
        lore.add("");
        lore.addAll(armorPassiveLore(set));
        lore.add("§c❤ Max Health: §f+"+formatHearts(armorHealthPerPiece(set))+" hearts §7per piece");
        lore.add("§9🛡 Defense: §f+"+formatStat(armorDefensePerPiece(set))+" Armor §8/ §f+"+formatStat(armorToughnessPerPiece(set))+" Toughness");
        lore.add("§b✦ Full set unlocks passive aura + active skill.");
        if(piece.equals("helmet"))lore.add("§d✦ Visor: §f/rishelmet open §8/ §fclosed");

        m.setDisplayName(color+"§l"+title+" §8• §f"+piece.toUpperCase(Locale.ROOT));
        m.setLore(lore);
        String itemModel=piece.equals("helmet")?"armor/"+set+"_helmet_closed":"armor/"+set+"_"+piece;
        applyArmorVisualV369(m,armorCmd(set,piece),itemModel);

        // Explicit slot + swappable fixes right-click equipping on modern Paper.
        try{
            var eq=m.getEquippable();
            eq.setSlot(armorSlot(piece));
            eq.setModel(new NamespacedKey("legendaryv369",piece.equals("helmet")?set+"_helmet_closed":set+"_set"));
            eq.setSwappable(true);
            eq.setDamageOnHurt(false);
            m.setEquippable(eq);
        }catch(Throwable ex){plugin.getLogger().warning("Could not apply equippable component to "+set+"/"+piece+": "+ex.getMessage());}

        m.getPersistentDataContainer().set(armorSetKey,PersistentDataType.STRING,set);
        m.getPersistentDataContainer().set(armorPieceKey,PersistentDataType.STRING,piece);
        m.getPersistentDataContainer().set(assetVersionKey,PersistentDataType.INTEGER,370);
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
        Bukkit.getScheduler().runTaskLater(plugin,()->{
            Player p=e.getPlayer();
            int fixed=refreshAllLegendaryItems(p);
            syncLegendaryHealth(p);
            if(fixed>0)p.sendMessage("§bLegendaryRais §8• §a"+fixed+" item lama diperbarui ke asset v3.6.3.");
        },5L);
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
            case PHOENIX->List.of(
                "§6✦ Passive: §eAshen Sovereignty","§7Fire immune • strength • emergency regeneration.",
                "§6✦ 4-Set: §eCinder Retaliation","§7Saat dihantam, attacker dapat burn burst (cooldown internal)."
            );
            case VOIDWALKER->List.of(
                "§5✦ Passive: §dPhaseborn","§7Speed • night vision • fall damage sangat rendah.",
                "§5✦ 4-Set: §dNull Veil","§7Legendary hit berat direduksi dan meninggalkan void afterimage."
            );
            case TITAN->List.of(
                "§2✦ Passive: §aColossus Frame","§7Resistance • absorption • knockback sangat rendah.",
                "§2✦ 4-Set: §aUnbreakable Core","§7Legendary damage cap paling kuat dari semua set."
            );
            case WATER_SOVEREIGN->List.of(
                "§3✦ Passive: §bAbyssal Regalia","§7Water Breathing • Dolphin's Grace • regen di air.",
                "§3✦ 4-Set: §bDeep Current Barrier","§7Legendary damage dinormalisasi + barrier pulse."
            );
            default->List.of(
                "§b✦ Passive: §fStarforged Grace","§7Regeneration • slow falling • radiant sustain.",
                "§b✦ 4-Set: §fAegis Constellation","§7Legendary hit dinormalisasi + heal pulse berkala."
            );
        };
    }
    private Material armorMaterial(String set,String piece){String p=switch(set){case PHOENIX->"GOLDEN_";case VOIDWALKER,WATER_SOVEREIGN->"NETHERITE_";case TITAN->"DIAMOND_";default->"IRON_";};String q=switch(piece){case "helmet"->"HELMET";case "chest"->"CHESTPLATE";case "legs"->"LEGGINGS";default->"BOOTS";};return Material.valueOf(p+q);}
    private int armorCmd(String set,String piece){int b=switch(set){case PHOENIX->920100;case VOIDWALKER->920104;case TITAN->920108;case CELESTIAL->920112;case WATER_SOVEREIGN->920116;default->920112;};return b+switch(piece){case "helmet"->1;case "chest"->2;case "legs"->3;default->4;};}
    private String armorSkillName(String set){return armorUtilitySkillName(set);}
    private String armorPunchSkillName(String set){return switch(set){
        case PHOENIX->"Blazing Knuckle";
        case VOIDWALKER->"Void Impact";
        case TITAN->"Colossus Fist";
        case WATER_SOVEREIGN->"Tidal Crash";
        default->"Starbreaker Palm";
    };}
    private String armorUtilitySkillName(String set){return switch(set){
        case PHOENIX->"Rebirth Flare";
        case VOIDWALKER->"Phase Rift";
        case TITAN->"Titan Bastion";
        case WATER_SOVEREIGN->"Abyssal Guard";
        default->"Celestial Ward";
    };}

    private String helmetMode(Player p){
        String m=p.getPersistentDataContainer().get(helmetModeKey,PersistentDataType.STRING);
        return "OPEN".equalsIgnoreCase(m)?"OPEN":"CLOSED";
    }

    private boolean applyHelmetMode(Player p,String mode){
        ItemStack helmet=p.getInventory().getHelmet();
        if(helmet==null||helmet.getType()==Material.AIR)return false;
        ItemMeta meta=helmet.getItemMeta();if(meta==null)return false;
        String set=meta.getPersistentDataContainer().get(armorSetKey,PersistentDataType.STRING);
        String piece=meta.getPersistentDataContainer().get(armorPieceKey,PersistentDataType.STRING);
        if(set==null||!"helmet".equals(piece)||!Set.of(PHOENIX,VOIDWALKER,TITAN,CELESTIAL,WATER_SOVEREIGN).contains(set))return false;
        String suffix="OPEN".equalsIgnoreCase(mode)?"open":"closed";
        try{meta.setItemModel(new NamespacedKey("legendaryv369","armor/"+set+"_helmet_"+suffix));}catch(Throwable ignored){}
        try{
            var eq=meta.getEquippable();
            eq.setSlot(EquipmentSlot.HEAD);
            eq.setModel(new NamespacedKey("legendaryv369",set+"_helmet_"+suffix));
            eq.setSwappable(true);
            eq.setDamageOnHurt(false);
            meta.setEquippable(eq);
        }catch(Throwable ex){plugin.getLogger().warning("Helmet visor model update failed for "+set+": "+ex.getMessage());}
        meta.getPersistentDataContainer().set(helmetModeKey,PersistentDataType.STRING,suffix.toUpperCase(Locale.ROOT));
        meta.getPersistentDataContainer().set(assetVersionKey,PersistentDataType.INTEGER,370);
        helmet.setItemMeta(meta);
        p.getInventory().setHelmet(helmet);
        return true;
    }

    private int refreshAllLegendaryItems(Player p){
        int fixed=0;
        PlayerInventory inv=p.getInventory();
        for(int slot=0;slot<inv.getSize();slot++){
            ItemStack old=inv.getItem(slot);
            ItemStack fresh=refreshLegendaryItem(old);
            if(fresh!=old){inv.setItem(slot,fresh);fixed++;}
        }
        Inventory ender=p.getEnderChest();
        for(int slot=0;slot<ender.getSize();slot++){
            ItemStack old=ender.getItem(slot);
            ItemStack fresh=refreshLegendaryItem(old);
            if(fresh!=old){ender.setItem(slot,fresh);fixed++;}
        }
        return fixed;
    }

    private ItemStack refreshLegendaryItem(ItemStack old){
        if(old==null||old.getType()==Material.AIR)return old;
        ItemMeta meta=old.getItemMeta();if(meta==null)return old;
        Integer ver=meta.getPersistentDataContainer().get(assetVersionKey,PersistentDataType.INTEGER);
        String wid=meta.getPersistentDataContainer().get(weaponKey,PersistentDataType.STRING);
        if(expansionWeapon(wid)){
            Material expected=switch(wid){
                case EMBERFALL,NOCTIS->Material.NETHERITE_SWORD;
                case STORMPIERCER->Material.BOW;
                case GAIA->Material.NETHERITE_SHOVEL;
                case ASTRAL->Material.NETHERITE_AXE;
                default->old.getType();
            };
            if(ver!=null&&ver>=370&&old.getType()==expected)return old;
            ItemStack fresh=createWeapon(wid);fresh.setAmount(old.getAmount());return fresh;
        }
        String set=meta.getPersistentDataContainer().get(armorSetKey,PersistentDataType.STRING);
        String piece=meta.getPersistentDataContainer().get(armorPieceKey,PersistentDataType.STRING);
        if(set!=null&&piece!=null&&Set.of(PHOENIX,VOIDWALKER,TITAN,CELESTIAL,WATER_SOVEREIGN).contains(set)){
            Material expected=armorMaterial(set,piece);
            if(ver!=null&&ver>=370&&old.getType()==expected)return old;
            ItemStack fresh=createArmorPiece(set,piece);fresh.setAmount(old.getAmount());
            if("helmet".equals(piece)){
                String im=meta.getPersistentDataContainer().get(helmetModeKey,PersistentDataType.STRING);
                if("OPEN".equalsIgnoreCase(im)){
                    ItemMeta fm=fresh.getItemMeta();
                    if(fm!=null){
                        try{fm.setItemModel(new NamespacedKey("legendaryv369","armor/"+set+"_helmet_open"));}catch(Throwable ignored){}
                        try{var eq=fm.getEquippable();eq.setSlot(EquipmentSlot.HEAD);eq.setModel(new NamespacedKey("legendaryv369",set+"_helmet_open"));eq.setSwappable(true);eq.setDamageOnHurt(false);fm.setEquippable(eq);}catch(Throwable ignored){}
                        fm.getPersistentDataContainer().set(helmetModeKey,PersistentDataType.STRING,"OPEN");fresh.setItemMeta(fm);
                    }
                }
            }
            return fresh;
        }
        return old;
    }

    private void applyArmorVisualV369(ItemMeta m,int cmd,String model){
        m.setUnbreakable(true);
        try{m.setCustomModelData(cmd);}catch(Throwable ignored){}
        try{m.setItemModel(new NamespacedKey("legendaryv369",model));}catch(Throwable ignored){}
        try{m.setEnchantmentGlintOverride(true);}catch(Throwable ignored){}
    }

    private void applyWeaponVisualV368(ItemMeta m,int cmd,String model){
        m.setUnbreakable(true);
        try{m.setCustomModelData(cmd);}catch(Throwable ignored){}
        try{m.setItemModel(new NamespacedKey("legendaryv368",model));}catch(Throwable ignored){}
        try{m.setEnchantmentGlintOverride(true);}catch(Throwable ignored){}
    }

    private void applyVisual(ItemMeta m,int cmd,String model){m.setUnbreakable(true);try{m.setCustomModelData(cmd);}catch(Throwable ignored){}try{m.setItemModel(new NamespacedKey("legendaryv34",model));}catch(Throwable ignored){}try{m.setEnchantmentGlintOverride(true);}catch(Throwable ignored){}}
    private String weaponId(ItemStack item){
        if(item==null||item.getType()==Material.AIR)return "";
        ItemMeta m=item.getItemMeta();if(m==null)return "";
        String id=m.getPersistentDataContainer().get(weaponKey,PersistentDataType.STRING);
        if(id==null)return "";
        Integer ver=m.getPersistentDataContainer().get(assetVersionKey,PersistentDataType.INTEGER);
        if(expansionWeapon(id)&&(ver==null||ver<370)){
            ItemStack fresh=createWeapon(id);
            item.setType(fresh.getType());
            item.setItemMeta(fresh.getItemMeta());
        }
        return id;
    }
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
        if(plugin.getCommand("risperf")==null)errors.add("/risperf missing from plugin.yml");
        if(plugin.getCommand("risrepair")==null)errors.add("/risrepair missing from plugin.yml");
        if(plugin.getCommand("rishelmet")==null)errors.add("/rishelmet missing from plugin.yml");
        if(plugin.getConfig().getLong("armor.input.double-sneak-window-ms",1000L)<900L)errors.add("double-sneak window too short");
        if(!plugin.getConfig().getBoolean("armor.java-3d-overlay",true))errors.add("Java 3D armor overlay disabled");
        if(!createWeapon(ASTRAL).getType().equals(Material.NETHERITE_AXE))errors.add("Astral Frost must use NETHERITE_AXE base");
        if(!createWeapon(STORMPIERCER).getType().equals(Material.BOW))errors.add("Stormpiercer must remain vanilla BOW base");

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

    private boolean tryArmorUtility(Player p){
        long until=armorPunchArmedUntil.getOrDefault(p.getUniqueId(),0L);
        if(System.currentTimeMillis()>until)return false;
        String set=fullSet(p);
        if(set==null){armorPunchArmedUntil.remove(p.getUniqueId());return false;}
        String heldWeapon=weaponId(p.getInventory().getItemInMainHand());
        if(expansionWeapon(heldWeapon)||heldWeapon.equals("soul_tide_katana_v4")||heldWeapon.equals("abyss_leviathan_trident_v3"))return false;
        armorPunchArmedUntil.remove(p.getUniqueId());
        armorUtilitySkill(p,set);
        return true;
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void armorUtilityEntityRightClick(PlayerInteractEntityEvent e){
        if(e.getHand()!=EquipmentSlot.HAND)return;
        if(tryArmorUtility(e.getPlayer()))e.setCancelled(true);
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void armorUtilityAtEntityRightClick(PlayerInteractAtEntityEvent e){
        if(e.getHand()!=EquipmentSlot.HAND)return;
        if(tryArmorUtility(e.getPlayer()))e.setCancelled(true);
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void interact(PlayerInteractEvent e){
        if(e.getHand()!=null&&e.getHand()!=EquipmentSlot.HAND)return;
        Player p=e.getPlayer();Action a=e.getAction();
        boolean right=a==Action.RIGHT_CLICK_AIR||a==Action.RIGHT_CLICK_BLOCK;
        boolean left=a==Action.LEFT_CLICK_AIR||a==Action.LEFT_CLICK_BLOCK;

        if(right&&tryArmorUtility(p)){
            e.setCancelled(true);
            return;
        }

        String id=weaponId(p.getInventory().getItemInMainHand());
        if(!expansionWeapon(id))return;
        if(STORMPIERCER.equals(id)){
            // Critical crossplay rule: normal right-click is NEVER cancelled, preserving vanilla bow draw/aim.
            if(p.isSneaking()&&right){e.setCancelled(true);cast(p,id,3);}
            else if(p.isSneaking()&&left){e.setCancelled(true);cast(p,id,2);}
            return;
        }
        if(p.isSneaking()&&right){e.setCancelled(true);cast(p,id,3);}
        else if(p.isSneaking()&&left){e.setCancelled(true);cast(p,id,2);}
        else if(!p.isSneaking()&&right){e.setCancelled(true);cast(p,id,1);}
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void stormpiercerShoot(EntityShootBowEvent e){
        if(!(e.getEntity() instanceof Player p))return;
        ItemStack bow=e.getBow();
        if(bow==null||!STORMPIERCER.equals(weaponId(bow)))return;
        if(e.getProjectile() instanceof AbstractArrow arrow){
            markStormArrow(arrow,1);
            arrow.setDamage(0.0); // v3.5.5: explosion damage is authoritative; prevent vanilla+explosion double hit.
            arrow.setCritical(false);
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
        Location hit=arrow.getLocation().clone();World w=hit.getWorld();if(w==null)return;

        double radius=tier>=2?3.25:3.8;
        double dmg=tier>=2?52.0:plugin.getConfig().getDouble("gacha.stormpiercer.arrow-impact-damage",195.0);

        // Pure magical explosion: visuals + damage + knockback only. Never call createExplosion().
        particle(w,"FLASH",hit.clone().add(0,.35,0),3,.05,.05,.05,0);
        particle(w,"EXPLOSION_EMITTER",hit,2,.08,.08,.08,0);
        particle(w,"EXPLOSION",hit,10,.72,.52,.72,.035);
        particle(w,"ELECTRIC_SPARK",hit,56,radius*.34,.8,radius*.34,.12);
        ring(w,hit.clone().add(0,.18,0),"END_ROD",Math.max(1.8,radius*.72),26,0);
        pulse(w,hit.clone().add(0,.3,0),"fx_thunderhead",FX_THUNDER,tier>=2?2.4f:3.0f,10,0,0);
        sound(w,hit,"minecraft:entity.generic.explode",1.5f,.82f);
        sound(w,hit,"minecraft:entity.end_crystal.explode",1.15f,1.08f);

        for(Entity ent:w.getNearbyEntities(hit,radius,radius,radius)){
            if(!(ent instanceof LivingEntity l)||l.getUniqueId().equals(p.getUniqueId()))continue;
            hurt(l,dmg,p);
            Vector kb=l.getLocation().toVector().subtract(hit.toVector());if(kb.lengthSquared()<.01)kb=new Vector(0,0,1);
            kb.normalize().multiply(tier>=2?.62:.90).setY(tier>=2?.26:.35);
            l.setVelocity(kb);
        }
        arrow.remove();
    }

    private void markStormArrow(AbstractArrow arrow,int tier){
        arrow.getPersistentDataContainer().set(stormArrowKey,PersistentDataType.BYTE,(byte)1);
        arrow.getPersistentDataContainer().set(stormArrowTierKey,PersistentDataType.INTEGER,tier);
    }

    private void launchStormVolleyArrow(Player p,Vector velocity,int tier){
        Arrow a=p.launchProjectile(Arrow.class,velocity);
        a.setDamage(0.0);
        a.setCritical(false);
        a.setPickupStatus(AbstractArrow.PickupStatus.DISALLOWED);
        markStormArrow(a,tier);
    }
    @EventHandler(priority=EventPriority.HIGH,ignoreCancelled=true)
    public void melee(EntityDamageByEntityEvent e){
        if(!(e.getDamager() instanceof Player p)||!(e.getEntity() instanceof LivingEntity t))return;
        String id=weaponId(p.getInventory().getItemInMainHand());if(!expansionWeapon(id))return;
        if(internalDamage.contains(t.getUniqueId()))return;
        e.setDamage(Math.max(e.getDamage(),baseDamage(id)));
        hitFx(t,id);weaponPassive(p,t,id);
        // Sneak-left skill is handled by PlayerAnimationEvent. Never cancel the real melee hit.
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void legendaryArmorDamageGuard(EntityDamageByEntityEvent e){
        if(!(e.getEntity() instanceof Player target))return;
        String set=fullSet(target);if(set==null)return;

        Player attacker=null;
        if(e.getDamager() instanceof Player p)attacker=p;
        else if(e.getDamager() instanceof Projectile pr&&pr.getShooter() instanceof Player p)attacker=p;
        if(attacker==null)return;

        String wid=weaponId(attacker.getInventory().getItemInMainHand());
        boolean legendary=expansionWeapon(wid)||wid.equals("soul_tide_katana_v4")||wid.equals("abyss_leviathan_trident_v3");
        if(!legendary)return;

        double raw=e.getDamage();
        boolean skill=internalDamage.contains(target.getUniqueId())||raw>=55.0;
        double desired=switch(set){
            case TITAN->skill?9.6:5.2;
            case CELESTIAL->skill?10.2:5.8;
            case WATER_SOVEREIGN->skill?10.4:6.0;
            case VOIDWALKER->skill?10.8:6.2;
            case PHOENIX->skill?11.2:6.6;
            default->skill?10.4:6.0;
        };
        double beforeHealth=target.getHealth(),beforeAbsorb=target.getAbsorptionAmount();
        e.setDamage(Math.min(raw,desired));

        Bukkit.getScheduler().runTask(plugin,()->{
            if(!target.isValid()||target.isDead())return;
            double poolBefore=beforeHealth+beforeAbsorb;
            double poolNow=target.getHealth()+target.getAbsorptionAmount();
            double actual=Math.max(0.0,poolBefore-poolNow);
            double shortfall=desired-actual;
            if(shortfall<=.01)return;
            double absorb=target.getAbsorptionAmount();
            double fromAbsorb=Math.min(absorb,shortfall);
            if(fromAbsorb>0){target.setAbsorptionAmount(Math.max(0.0,absorb-fromAbsorb));shortfall-=fromAbsorb;}
            if(shortfall>0&&target.isValid()&&!target.isDead())target.setHealth(Math.max(0.0,target.getHealth()-shortfall));
        });

        Location c=target.getLocation().clone().add(0,1,0);
        switch(set){
            case PHOENIX->particle(target.getWorld(),"FLAME",c,18,.45,.55,.45,.04);
            case VOIDWALKER->particle(target.getWorld(),"REVERSE_PORTAL",c,18,.45,.55,.45,.02);
            case TITAN->particle(target.getWorld(),"CLOUD",c,16,.38,.35,.38,.03);
            case WATER_SOVEREIGN->particle(target.getWorld(),"BUBBLE_POP",c,20,.45,.55,.45,.05);
            default->particle(target.getWorld(),"END_ROD",c,14,.4,.5,.4,.025);
        }
        bar(target,"LEGEND ARMOR • "+set.toUpperCase(Locale.ROOT)+" • "+String.format(Locale.US,"%.1f",desired/2.0)+" hearts");
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void legendaryArmorPhysicalGuard(EntityDamageByEntityEvent e){
        if(!(e.getEntity() instanceof Player target))return;
        String set=fullSet(target);if(set==null)return;
        if(!(e.getDamager() instanceof Player attacker))return;

        String wid=weaponId(attacker.getInventory().getItemInMainHand());
        boolean legendary=expansionWeapon(wid)||"soul_tide_katana_v4".equals(wid)||"abyss_leviathan_trident_v3".equals(wid);
        if(legendary)return; // handled by legendaryArmorDamageGuard

        boolean mace=attacker.getInventory().getItemInMainHand().getType()==Material.MACE;
        double multiplier=switch(set){
            case TITAN->.50;
            case WATER_SOVEREIGN->.56;
            case CELESTIAL->.60;
            case VOIDWALKER->.62;
            case PHOENIX->.65;
            default->.65;
        };
        double capped=e.getDamage()*multiplier;
        if(mace){
            double maceCap=switch(set){
                case TITAN->6.0;              // max 3 hearts raw before vanilla mitigation
                case WATER_SOVEREIGN->7.0;
                case CELESTIAL->7.5;
                case VOIDWALKER->8.0;
                case PHOENIX->9.0;
                default->9.0;
            };
            capped=Math.min(capped,maceCap);
            bar(target,"MACE GUARD • "+set.toUpperCase(Locale.ROOT)+" • MAX "+String.format(Locale.US,"%.1f",maceCap/2.0)+" hearts");
        }
        e.setDamage(Math.min(e.getDamage(),capped));
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void armorHeavyMobGuard(EntityDamageByEntityEvent e){
        if(!(e.getEntity() instanceof Player p)||!(e.getDamager() instanceof IronGolem))return;
        String set=fullSet(p);if(set==null)return;
        double mitigation=switch(set){
            case TITAN->.35;
            case WATER_SOVEREIGN->.24;
            case CELESTIAL->.22;
            case VOIDWALKER->.20;
            case PHOENIX->.18;
            default->0.0;
        };
        e.setDamage(e.getDamage()*(1.0-mitigation));
        if(mitigation>0)bar(p,"HEAVY GUARD • "+set.toUpperCase(Locale.ROOT)+" • -"+(int)Math.round(mitigation*100)+"%");
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void windLeapFallGuard(org.bukkit.event.entity.EntityDamageEvent e){
        if(!(e.getEntity() instanceof Player p)||e.getCause()!=org.bukkit.event.entity.EntityDamageEvent.DamageCause.FALL)return;
        long until=windLeapSafeUntil.getOrDefault(p.getUniqueId(),0L);
        if(System.currentTimeMillis()>until)return;
        windLeapSafeUntil.remove(p.getUniqueId());
        p.setFallDistance(0f);
        e.setCancelled(true);
        particle(p.getWorld(),"GUST",p.getLocation().clone().add(0,.15,0),10,.45,.12,.45,.04);
    }

    @EventHandler(ignoreCancelled=true)
    public void armorEnvironmentalDefense(org.bukkit.event.entity.EntityDamageEvent e){
        if(!(e.getEntity() instanceof Player p))return;
        String set=fullSet(p); if(set==null)return;
        if(VOIDWALKER.equals(set)&&e.getCause()==org.bukkit.event.entity.EntityDamageEvent.DamageCause.FALL)e.setDamage(e.getDamage()*.12);
        if(TITAN.equals(set)&&(e.getCause()==org.bukkit.event.entity.EntityDamageEvent.DamageCause.FALL||e.getCause()==org.bukkit.event.entity.EntityDamageEvent.DamageCause.BLOCK_EXPLOSION||e.getCause()==org.bukkit.event.entity.EntityDamageEvent.DamageCause.ENTITY_EXPLOSION))e.setDamage(e.getDamage()*.45);
        if(PHOENIX.equals(set)&&e.getCause()==org.bukkit.event.entity.EntityDamageEvent.DamageCause.FIRE)e.setCancelled(true);
        if(PHOENIX.equals(set)&&e.getCause()==org.bukkit.event.entity.EntityDamageEvent.DamageCause.FIRE_TICK)e.setCancelled(true);
    }

    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true)
    public void armorSetRetaliation(EntityDamageByEntityEvent e){
        if(!(e.getEntity() instanceof Player p))return;
        String set=fullSet(p); if(set==null)return;
        long now=System.currentTimeMillis(),until=armorSetProcCd.getOrDefault(p.getUniqueId(),0L);
        if(now<until)return;
        armorSetProcCd.put(p.getUniqueId(),now+8000L);
        if(PHOENIX.equals(set)){
            LivingEntity a=null;
            if(e.getDamager() instanceof LivingEntity l)a=l;
            else if(e.getDamager() instanceof Projectile pr&&pr.getShooter() instanceof LivingEntity l)a=l;
            if(a!=null){a.setFireTicks(Math.max(a.getFireTicks(),80));particle(p.getWorld(),"FLAME",a.getLocation().clone().add(0,1,0),30,.5,.6,.5,.06);}
        }else if(VOIDWALKER.equals(set)){
            particle(p.getWorld(),"REVERSE_PORTAL",p.getLocation().clone().add(0,1,0),28,.55,.7,.55,.03);
            try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SPEED,50,2,true,false,false));}catch(Throwable ignored){}
        }else if(TITAN.equals(set)){
            try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,70,0,true,false,false));}catch(Throwable ignored){}
        }else if(CELESTIAL.equals(set)){
            p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+2.0));
            particle(p.getWorld(),"END_ROD",p.getLocation().clone().add(0,1,0),18,.5,.65,.5,.02);
        }else if(WATER_SOVEREIGN.equals(set)){
            try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,55,2,true,false,false));}catch(Throwable ignored){}
            particle(p.getWorld(),"BUBBLE_POP",p.getLocation().clone().add(0,1,0),24,.5,.65,.5,.05);
        }
    }

    @EventHandler(ignoreCancelled=true) public void swing(PlayerAnimationEvent e){Player p=e.getPlayer();if(!p.isSneaking())return;String id=weaponId(p.getInventory().getItemInMainHand());if(expansionWeapon(id))cast(p,id,2);}

    private double baseDamage(String id){
        return plugin.getConfig().getDouble("gacha."+cfg(id)+".base-hit",switch(id){
            case EMBERFALL->26.4;   // 60% of Leviathan 44
            case NOCTIS->22.8;      // 60% of Soul Tide 38
            case STORMPIERCER->22.8;
            case GAIA->24.0;
            default->22.8;
        });
    }
    private String cfg(String id){return switch(id){case EMBERFALL->"emberfall";case NOCTIS->"noctis";case STORMPIERCER->"stormpiercer";case GAIA->"gaia";default->"astral";};}
    private double damage(String id,int skill){
        List<Double> v=plugin.getConfig().getDoubleList("gacha."+cfg(id)+".damage");
        double[] d={390.0,390.0,390.0}; // 650 water-tier * 0.60
        return v.size()>=3?v.get(skill-1):d[skill-1];
    }
    private int skillCd(String id,int skill){
        List<Integer> v=plugin.getConfig().getIntegerList("gacha."+cfg(id)+".cooldowns");
        int[] d=switch(id){
            case EMBERFALL->new int[]{9,15,24};
            case NOCTIS->new int[]{8,14,22};
            case STORMPIERCER->new int[]{7,13,21};
            case GAIA->new int[]{6,11,18};
            default->new int[]{8,15,23};
        };
        return v.size()>=3?Math.max(1,v.get(skill-1)):d[skill-1];
    }
    private boolean ready(Player p,String key,int sec,String name){long now=System.currentTimeMillis();Map<String,Long> m=cooldowns.computeIfAbsent(p.getUniqueId(),u->new ConcurrentHashMap<>());long end=m.getOrDefault(key,0L);if(now<end){bar(p,name+" • "+String.format(Locale.US,"%.1fs",(end-now)/1000.0));return false;}m.put(key,now+sec*1000L);return true;}
    private String elementName(String id){return switch(id){
        case EMBERFALL->"FIRE";
        case NOCTIS->"VOID";
        case STORMPIERCER->"ELECTRO";
        case GAIA->"WIND";
        default->"ICE";
    };}

    private void cast(Player p,String id,int skill){
        if(!ready(p,id+":"+skill,skillCd(id,skill),elementName(id)+" • Skill "+skill))return;
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
                particle(w,"FLAME",hit,52,.72,.72,.72,.09);
                particle(w,"LAVA",hit,8,.35,.28,.35,.03);
                for(Entity e:w.getNearbyEntities(hit,3.0,2.5,3.0))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                    hurt(l,64,p);l.setFireTicks(Math.max(l.getFireTicks(),100));
                }
                sound(w,hit,"minecraft:item.firecharge.use",1.1f,.72f);
                bar(p,"[FIRE] HEATBREAKER • COMBUSTION");
            }
            case NOCTIS->{
                if(passiveStack(p,id,3)<3)return;
                pulse(w,hit,"fx_eclipse_cage",FX_ECLIPSE,2.2f,10,180,0);
                hurt(t,58,p);
                try{
                    t.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.DARKNESS,55,0,true,false,false));
                    t.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.WEAKNESS,55,1,true,false,false));
                }catch(Throwable ignored){}
                sound(w,hit,"minecraft:entity.warden.heartbeat",.7f,.72f);
                bar(p,"[VOID] NULL MARK • COLLAPSE");
            }
            case STORMPIERCER->{
                if(passiveStack(p,id,3)<3)return;
                particle(w,"ELECTRIC_SPARK",hit,48,.6,.7,.6,.10);
                pulse(w,hit,"fx_thunderhead",FX_THUNDER,2.4f,9,0,0);
                try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SPEED,80,1,true,false,false));}catch(Throwable ignored){}
                bar(p,"[ELECTRO] STATIC CORE • OVERCHARGED");
            }
            case GAIA->{
                if(passiveStack(p,id,4)<4)return;
                particle(w,"GUST",hit,10,.7,.5,.7,.06);
                particle(w,"CLOUD",hit,34,.8,.5,.8,.08);
                Vector push=t.getLocation().toVector().subtract(p.getLocation().toVector());
                if(push.lengthSquared()>.01)t.setVelocity(push.normalize().multiply(1.15).setY(.38));
                hurt(t,52,p);
                try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SPEED,70,1,true,false,false));}catch(Throwable ignored){}
                bar(p,"[WIND] TAILWIND • BURST");
            }
            case ASTRAL->{
                if(passiveStack(p,id,3)<3)return;
                particle(w,"SNOWFLAKE",hit,44,.6,.75,.6,.04);
                blockFx(w,hit.clone().add(0,-.6,0),Material.PACKED_ICE,1.0f,12);
                hurt(t,56,p);
                try{
                    t.setFreezeTicks(Math.max(t.getFreezeTicks(),100));
                    t.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,70,4,true,false,false));
                }catch(Throwable ignored){}
                bar(p,"[ICE] FROSTBITE • SHATTER");
            }
            default->{}
        }
    }

    private void weaponCastSignature(Player p,String id,int skill){
        if(!STORMPIERCER.equals(id))return;
        int n=passiveStack(p,"storm_static",3);
        if(n<3)return;
        Location c=p.getLocation().clone().add(0,1.2,0);
        particle(p.getWorld(),"ELECTRIC_SPARK",c,52,.75,.9,.75,.10);
        pulse(p.getWorld(),c,"fx_thunderhead",FX_THUNDER,2.3f,10,p.getLocation().getYaw(),0);
        try{p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SPEED,90,1,true,false,false));}catch(Throwable ignored){}
        sound(p.getWorld(),c,"minecraft:entity.lightning_bolt.thunder",.55f,1.65f);
        bar(p,"[ELECTRO] STATIC CORE • CHARGED");
    }

    private void ember(Player p,int s){
        double dmg=damage(EMBERFALL,s); World w=p.getWorld(); Vector d=p.getEyeLocation().getDirection().normalize();
        if(s==1){
            Set<UUID> hit=new HashSet<>();
            for(int k=-2;k<=2;k++){
                Vector slash=rotateY(d,Math.toRadians(k*8));
                for(int i=1;i<=11;i++){
                    Location c=p.getEyeLocation().clone().add(slash.clone().multiply(i*.78));
                    particle(w,"FLAME",c,7,.16,.14,.16,.025);
                    if(i%3==0)pulse(w,c,"fx_ember_rift",FX_EMBER_RIFT,1.0f,5,yaw(slash),pitch(slash));
                    for(Entity e:w.getNearbyEntities(c,.8,.9,.8))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId())){
                        hurt(l,dmg,p);l.setFireTicks(110);
                    }
                }
            }
            sound(w,p.getLocation(),"minecraft:entity.player.attack.sweep",1.2f,.62f);
            bar(p,"[FIRE] EMBERFALL • FLAME CRESCENT");
        }else if(s==2){
            Location from=p.getLocation().clone(),to=safeForward(p,9.0);Vector step=to.toVector().subtract(from.toVector());
            Set<UUID> hit=new HashSet<>();
            for(int i=0;i<=14;i++){
                Location q=from.clone().add(step.clone().multiply(i/14.0));
                particle(w,"FLAME",q.clone().add(0,.25,0),12,.28,.15,.28,.035);
                if(i%3==0)pulse(w,q.clone().add(0,.5,0),"fx_ember_meteor",FX_EMBER_METEOR,1.3f,6,p.getLocation().getYaw(),0);
                for(Entity e:w.getNearbyEntities(q,1.25,1.7,1.25))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId())){
                    hurt(l,dmg,p);l.setFireTicks(120);
                }
            }
            p.teleport(to);
            particle(w,"EXPLOSION_EMITTER",to,1,.1,.1,.1,0);
            pulse(w,to.clone().add(0,.7,0),"fx_inferno_crown",FX_INFERNO,3.4f,12,0,0);
            sound(w,to,"minecraft:item.firecharge.use",1.25f,.74f);
            bar(p,"[FIRE] EMBERFALL • INFERNO RUSH");
        }else{
            Location c=p.getLocation().clone().add(d.clone().multiply(7));
            pulse(w,c.clone().add(0,.5,0),"fx_inferno_crown",FX_INFERNO,5.0f,18,0,0);
            new BukkitRunnable(){int t=0;public void run(){
                if(t++>=28){cancel();return;}
                double r=1.0+t*.15;
                ring(w,c,"FLAME",r,28,t*.28);
                if(t%7==0){
                    particle(w,"EXPLOSION",c,4,.5,.25,.5,.02);
                    for(Entity e:w.getNearbyEntities(c,Math.min(5.2,r+1),3.5,Math.min(5.2,r+1)))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                        hurt(l,dmg/4.0,p);l.setFireTicks(140);
                    }
                }
            }}.runTaskTimer(plugin,0,1);
            sound(w,c,"minecraft:entity.blaze.shoot",1.35f,.55f);
            bar(p,"[FIRE] EMBERFALL • SOLAR ERUPTION");
        }
    }
    private void noctis(Player p,int s){
        double dmg=damage(NOCTIS,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();
        if(s==1){
            Location from=p.getLocation().clone(),to=safeForward(p,7.5);
            for(int i=0;i<=12;i++){
                Location q=from.clone().add(to.toVector().subtract(from.toVector()).multiply(i/12.0)).add(0,1,0);
                particle(w,"REVERSE_PORTAL",q,7,.18,.22,.18,.02);
            }
            Set<UUID> hit=new HashSet<>();
            for(Entity e:w.getNearbyEntities(from.clone().add(d.clone().multiply(3.5)),4.2,2.7,4.2))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId()))hurt(l,dmg,p);
            p.teleport(to);pulse(w,to.clone().add(0,1,0),"fx_shade_step",FX_SHADE,2.5f,10,p.getLocation().getYaw(),0);
            sound(w,to,"minecraft:entity.enderman.teleport",1.0f,.72f);
            bar(p,"[VOID] NOCTIS • NULL STEP");
        }else if(s==2){
            Location c=p.getLocation().clone().add(d.clone().multiply(5));
            pulse(w,c.clone().add(0,1,0),"fx_soul_harvest",FX_HARVEST,3.0f,12,0,0);
            for(int t=0;t<4;t++)ring(w,c.clone().add(0,.35*t,0),"REVERSE_PORTAL",1.4+t*.55,24,t*.45);
            for(Entity e:w.getNearbyEntities(c,5,3,5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                Vector pull=c.toVector().subtract(l.getLocation().toVector());if(pull.lengthSquared()>.01)l.setVelocity(pull.normalize().multiply(.85).setY(.12));
                hurt(l,dmg,p);
                try{l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.WEAKNESS,70,1,true,false,false));}catch(Throwable ignored){}
            }
            sound(w,c,"minecraft:entity.warden.sonic_boom",.75f,.62f);
            bar(p,"[VOID] NOCTIS • GRAVITY REND");
        }else{
            Location c=p.getLocation().clone().add(d.clone().multiply(5));
            new BukkitRunnable(){int t=0;public void run(){
                if(t++>=60){cancel();return;}
                ring(w,c,"REVERSE_PORTAL",4.4,34,t*.20);
                if(t%10==0)pulse(w,c.clone().add(0,1,0),"fx_eclipse_cage",FX_ECLIPSE,4.0f,10,t*9,0);
                if(t%12==0)for(Entity e:w.getNearbyEntities(c,4.5,3.5,4.5))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                    hurt(l,dmg/5.0,p);
                    try{
                        l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.DARKNESS,45,0,true,false,false));
                        l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,45,2,true,false,false));
                    }catch(Throwable ignored){}
                }
            }}.runTaskTimer(plugin,0,1);
            sound(w,c,"minecraft:entity.warden.heartbeat",1.0f,.55f);
            bar(p,"[VOID] NOCTIS • NULL DOMAIN");
        }
    }
    private void storm(Player p,int s){
        double dmg=damage(STORMPIERCER,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();
        if(s==1){
            launchStormVolleyArrow(p,d.clone().multiply(3.35),1);
            bar(p,"[ELECTRO] STORMPIERCER • ARC IMPACT");
        }else if(s==2){
            for(int k=-2;k<=2;k++){
                Vector v=rotateY(d,Math.toRadians(k*5)).normalize().multiply(3.15);
                v.setY(v.getY()+Math.abs(k)*.012);
                launchStormVolleyArrow(p,v,2);
            }
            particle(w,"ELECTRIC_SPARK",p.getEyeLocation(),46,.5,.4,.5,.10);
            pulse(w,p.getLocation().clone().add(0,1.2,0),"fx_thunderhead",FX_THUNDER,2.8f,12,p.getLocation().getYaw(),0);
            sound(w,p.getLocation(),"minecraft:entity.lightning_bolt.thunder",.72f,1.55f);
            bar(p,"[ELECTRO] STORMPIERCER • CHAIN VOLLEY");
        }else{
            Location c=p.getLocation().clone().add(d.clone().multiply(8));
            pulse(w,c.clone().add(0,1.2,0),"fx_thunderhead",FX_THUNDER,4.5f,20,0,0);
            new BukkitRunnable(){int t=0;public void run(){
                if(t++>=44){cancel();return;}
                ring(w,c,"ELECTRIC_SPARK",3.8,30,t*.35);
                if(t%8==0){
                    particle(w,"FLASH",c.clone().add(0,1,0),2,.2,.2,.2,0);
                    for(Entity e:w.getNearbyEntities(c,4.2,3.2,4.2))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId()))hurt(l,dmg/5.0,p);
                }
            }}.runTaskTimer(plugin,0,1);
            sound(w,c,"minecraft:entity.lightning_bolt.thunder",1.0f,.8f);
            bar(p,"[ELECTRO] STORMPIERCER • OVERCHARGE FIELD");
        }
    }
    private void gaia(Player p,int s){
        double dmg=damage(GAIA,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();
        if(s==1){
            RayTraceResult groundHit=null;
            try{groundHit=w.rayTraceBlocks(p.getEyeLocation(),d,plugin.getConfig().getDouble("gacha.gaia.windburst-ground-leap.ray-distance",5.5),FluidCollisionMode.NEVER,true);}catch(Throwable ignored){}
            if(d.getY()<-0.18&&groundHit!=null){
                Vector horizontal=d.clone().setY(0);
                if(horizontal.lengthSquared()<.01)horizontal=p.getLocation().getDirection().setY(0);
                if(horizontal.lengthSquared()<.01)horizontal=new Vector(0,0,1);
                horizontal.normalize().multiply(plugin.getConfig().getDouble("gacha.gaia.windburst-ground-leap.horizontal",1.15));
                double vertical=plugin.getConfig().getDouble("gacha.gaia.windburst-ground-leap.vertical",1.55);
                p.setFallDistance(0f);
                p.setVelocity(horizontal.setY(vertical));
                windLeapSafeUntil.put(p.getUniqueId(),System.currentTimeMillis()+plugin.getConfig().getLong("gacha.gaia.windburst-ground-leap.no-fall-ms",5000L));
                Location burst=groundHit.getHitPosition().toLocation(w).add(0,.15,0);
                particle(w,"GUST",burst,22,.65,.18,.65,.09);
                particle(w,"CLOUD",burst,38,.85,.20,.85,.08);
                ring(w,burst,"CLOUD",1.6,28,0);
                pulse(w,burst.clone().add(0,.35,0),"fx_gale_bolt",FX_GALE,3.1f,10,p.getLocation().getYaw(),90);
                sound(w,burst,"minecraft:entity.wind_charge.wind_burst",1.55f,.72f);
                bar(p,"[WIND] ZEPHYA • GROUND WINDBURST LEAP");
                return;
            }
            Location origin=p.getEyeLocation().clone();
            Set<UUID> hit=new HashSet<>();
            for(int i=1;i<=9;i++){
                Location c=origin.clone().add(d.clone().multiply(i*.95));
                double r=.35+i*.20;
                ring(w,c,"CLOUD",r,18,i*.44);
                particle(w,"GUST",c,3,.15,.15,.15,.03);
                for(Entity e:w.getNearbyEntities(c,r,.9,r))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId())){
                    hurt(l,dmg,p);Vector push=d.clone().multiply(1.35).setY(.36);l.setVelocity(push);
                }
            }
            pulse(w,p.getLocation().clone().add(d.clone().multiply(3)).add(0,1,0),"fx_gale_bolt",FX_GALE,2.8f,10,yaw(d),0);
            sound(w,p.getLocation(),"minecraft:entity.wind_charge.wind_burst",1.2f,.82f);
            bar(p,"[WIND] GAIA • WINDBURST");
        }else if(s==2){
            Set<UUID> hit=new HashSet<>();
            for(int k=-1;k<=1;k++){
                Vector blade=rotateY(d,Math.toRadians(k*14));
                for(int i=1;i<=14;i++){
                    Location q=p.getEyeLocation().clone().add(blade.clone().multiply(i*.72));
                    particle(w,"SWEEP_ATTACK",q,1,.03,.03,.03,0);
                    particle(w,"CLOUD",q,3,.12,.10,.12,.01);
                    for(Entity e:w.getNearbyEntities(q,.8,.8,.8))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId()))hurt(l,dmg,p);
                }
            }
            pulse(w,p.getLocation().clone().add(d.clone().multiply(5)).add(0,1,0),"fx_cyclone_volley",FX_CYCLONE,3.1f,11,yaw(d),0);
            sound(w,p.getLocation(),"minecraft:entity.player.attack.sweep",1.25f,1.55f);
            bar(p,"[WIND] GAIA • SKY CUTTER");
        }else{
            Location c=p.getLocation().clone();
            new BukkitRunnable(){int t=0;public void run(){
                if(t++>=42){cancel();return;}
                double r=1.5+Math.min(3.8,t*.10);
                ring(w,c,"CLOUD",r,34,t*.42);
                ring(w,c.clone().add(0,1.2,0),"GUST",Math.max(.8,r*.72),22,-t*.55);
                if(t%7==0)for(Entity e:w.getNearbyEntities(c,r+1,4,r+1))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                    Vector v=l.getLocation().toVector().subtract(c.toVector());if(v.lengthSquared()>.01)v.normalize();
                    l.setVelocity(v.multiply(.35).setY(.82));hurt(l,dmg/6.0,p);
                }
            }}.runTaskTimer(plugin,0,1);
            pulse(w,c.clone().add(0,1,0),"fx_cyclone_volley",FX_CYCLONE,4.6f,18,0,0);
            sound(w,c,"minecraft:entity.wind_charge.wind_burst",1.4f,.62f);
            bar(p,"[WIND] GAIA • TEMPEST ASCENSION");
        }
    }
    private void astral(Player p,int s){
        double dmg=damage(ASTRAL,s);World w=p.getWorld();Vector d=p.getEyeLocation().getDirection().normalize();
        if(s==1){
            Location from=p.getLocation().clone(),to=safeForward(p,6.8);
            p.teleport(to);
            particle(w,"SNOWFLAKE",from.clone().add(0,1,0),36,.5,.6,.5,.04);
            particle(w,"SNOWFLAKE",to.clone().add(0,1,0),44,.6,.7,.6,.04);
            Set<UUID> hit=new HashSet<>();
            for(Entity e:w.getNearbyEntities(to,3.2,2.4,3.2))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId())){
                hurt(l,dmg,p);
                try{l.setFreezeTicks(Math.max(l.getFreezeTicks(),120));l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,65,3,true,false,false));}catch(Throwable ignored){}
            }
            pulse(w,to.clone().add(0,1,0),"fx_frost_shard",FX_ROOT,2.7f,10,p.getLocation().getYaw(),0);
            sound(w,to,"minecraft:block.glass.break",1.0f,1.55f);
            bar(p,"[ICE] ASTRAL • FROST DASH");
        }else if(s==2){
            Set<UUID> hit=new HashSet<>();
            for(int i=1;i<=10;i++){
                Location q=p.getLocation().clone().add(d.clone().multiply(i*1.05));
                blockFx(w,q,Material.PACKED_ICE,.85f,12);
                particle(w,"SNOWFLAKE",q.clone().add(0,1,0),16,.3,.75,.3,.03);
                if(i%2==0)pulse(w,q.clone().add(0,1.0,0),"fx_glacier_fang",FX_STONE,1.7f,8,yaw(d),0);
                for(Entity e:w.getNearbyEntities(q,1.15,2.0,1.15))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&hit.add(l.getUniqueId())){
                    hurt(l,dmg,p);try{l.setFreezeTicks(Math.max(l.getFreezeTicks(),160));l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,90,4,true,false,false));}catch(Throwable ignored){}
                }
            }
            sound(w,p.getLocation(),"minecraft:block.glass.break",1.15f,.72f);
            bar(p,"[ICE] ASTRAL • GLACIER FANG");
        }else{
            Location c=p.getLocation().clone().add(d.clone().multiply(4));
            pulse(w,c.clone().add(0,1,0),"fx_absolute_zero",FX_SPIKE,5.0f,20,0,0);
            new BukkitRunnable(){int t=0;public void run(){
                if(t++>=52){cancel();return;}
                double r=Math.min(5.5,1.0+t*.12);
                ring(w,c,"SNOWFLAKE",r,34,t*.22);
                if(t%10==0)for(Entity e:w.getNearbyEntities(c,r,3.5,r))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                    hurt(l,dmg/6.0,p);
                    try{l.setFreezeTicks(Math.max(l.getFreezeTicks(),200));l.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,55,6,true,false,false));}catch(Throwable ignored){}
                }
            }}.runTaskTimer(plugin,0,1);
            sound(w,c,"minecraft:block.amethyst_block.resonate",1.0f,.55f);
            bar(p,"[ICE] ASTRAL • ABSOLUTE ZERO");
        }
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void armorDrop(PlayerDropItemEvent e){
        // v3.6.1: dropping/sneaking no longer activates armor. Active skill requires full set,
        // double-sneak arming, empty main hand, then a punch on a living target.
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void armorDoubleSneak(PlayerToggleSneakEvent e){
        if(!e.isSneaking())return;
        Player p=e.getPlayer();String set=fullSet(p);if(set==null)return;
        long now=System.currentTimeMillis(),last=lastSneakTap.getOrDefault(p.getUniqueId(),0L);
        lastSneakTap.put(p.getUniqueId(),now);
        long configured=plugin.getConfig().getLong("armor.input.double-sneak-window-ms",1000L);
        long window=Math.max(configured,isBedrock(p)?1400L:950L);
        if(now-last>window)return;
        long armConfigured=plugin.getConfig().getLong("armor.input.punch-arm-ms",6000L);
        long armedFor=Math.max(armConfigured,isBedrock(p)?7500L:6000L);
        armorPunchArmedUntil.put(p.getUniqueId(),now+armedFor);
        bar(p,set.toUpperCase(Locale.ROOT)+" ARMED • LEFT: "+armorPunchSkillName(set)+" • RIGHT: "+armorUtilitySkillName(set));
        sound(p.getWorld(),p.getLocation(),"minecraft:block.beacon.activate",.65f,1.55f);
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void armorPunchHit(EntityDamageByEntityEvent e){
        if(!(e.getDamager() instanceof Player p)||!(e.getEntity() instanceof LivingEntity target))return;
        long until=armorPunchArmedUntil.getOrDefault(p.getUniqueId(),0L);
        if(System.currentTimeMillis()>until)return;
        String set=fullSet(p);if(set==null){armorPunchArmedUntil.remove(p.getUniqueId());return;}
        ItemStack hand=p.getInventory().getItemInMainHand();
        if(hand!=null&&hand.getType()!=Material.AIR)return;
        int cd=plugin.getConfig().getInt("armor.cooldowns.skill1."+set,switch(set){case PHOENIX->16;case VOIDWALKER->15;case TITAN->18;case WATER_SOVEREIGN->16;default->17;});
        if(!ready(p,"armor:punch:"+set,cd,armorPunchSkillName(set))){armorPunchArmedUntil.remove(p.getUniqueId());return;}
        armorPunchArmedUntil.remove(p.getUniqueId());
        e.setCancelled(true);
        armorPunch(p,target,set);
    }

    private void armorPunch(Player p,LivingEntity target,String set){
        World w=p.getWorld();Location hit=target.getLocation().clone().add(0,1,0);
        Vector away=target.getLocation().toVector().subtract(p.getLocation().toVector());away.setY(0);
        if(away.lengthSquared()<.01)away=p.getLocation().getDirection().setY(0);
        if(away.lengthSquared()<.01)away=new Vector(1,0,0);away.normalize();

        switch(set){
            case TITAN->{
                target.setVelocity(away.clone().multiply(3.15).setY(.72));
                hurt(target,plugin.getConfig().getDouble("armor.damage.skill1.titan",7.0),p);
                try{target.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,45,1,true,false,false));}catch(Throwable ignored){}
                particle(w,"CLOUD",hit,52,.8,.45,.8,.08);pulse(w,hit,"fx_titan_bastion",FX_TITAN,3.4f,10,yaw(away),0);
                sound(w,hit,"minecraft:entity.iron_golem.attack",1.25f,.55f);
            }
            case PHOENIX->{
                target.setVelocity(away.clone().multiply(1.15).setY(.30));
                target.setFireTicks(Math.max(target.getFireTicks(),100));hurt(target,plugin.getConfig().getDouble("armor.damage.skill1.phoenix",6.0),p);
                particle(w,"FLAME",hit,48,.65,.7,.65,.08);particle(w,"LAVA",hit,6,.3,.3,.3,.02);
                pulse(w,hit,"fx_phoenix_rebirth",FX_PHOENIX,2.8f,9,yaw(away),0);
                sound(w,hit,"minecraft:item.firecharge.use",1.0f,.70f);
            }
            case VOIDWALKER->{
                target.setVelocity(away.clone().multiply(.45).setY(.12));hurt(target,plugin.getConfig().getDouble("armor.damage.skill1.voidwalker",5.0),p);
                try{
                    target.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.DARKNESS,70,0,true,false,false));
                    target.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.WEAKNESS,70,1,true,false,false));
                }catch(Throwable ignored){}
                Location behind=target.getLocation().clone().subtract(away.clone().multiply(1.3));if(!behind.getBlock().getType().isSolid())p.teleport(behind);
                particle(w,"REVERSE_PORTAL",hit,42,.65,.75,.65,.04);pulse(w,hit,"fx_void_phase",FX_VOID,2.7f,9,yaw(away),0);
                sound(w,hit,"minecraft:entity.enderman.teleport",.9f,.65f);
            }
            case WATER_SOVEREIGN->{
                target.setVelocity(away.clone().multiply(1.45).setY(.34));hurt(target,plugin.getConfig().getDouble("armor.damage.skill1.water_sovereign",5.0),p);
                try{target.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS,65,2,true,false,false));}catch(Throwable ignored){}
                Vector pull=away.clone().multiply(-.55).setY(.12);
                Bukkit.getScheduler().runTaskLater(plugin,()->{if(target.isValid()&&!target.isDead())target.setVelocity(pull);},8L);
                particle(w,"SPLASH",hit,46,.75,.65,.75,.08);pulse(w,hit,"fx_water_sovereign_guard",FX_WATER_ARMOR,3.0f,9,yaw(away),0);
                sound(w,hit,"minecraft:item.trident.hit",1.0f,.75f);
            }
            default->{
                target.setVelocity(away.clone().multiply(.85).setY(.58));hurt(target,plugin.getConfig().getDouble("armor.damage.skill1.celestial",4.0),p);
                p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+3.0));
                particle(w,"END_ROD",hit,34,.6,.7,.6,.04);pulse(w,hit,"fx_celestial_sanctuary",FX_CELESTIAL,2.8f,9,yaw(away),0);
                sound(w,hit,"minecraft:block.amethyst_block.resonate",1.0f,1.25f);
            }
        }
        bar(p,"ARMOR SKILL I • "+armorPunchSkillName(set));
    }

    private String fullSet(Player p){String found=null;ItemStack[] a={p.getInventory().getHelmet(),p.getInventory().getChestplate(),p.getInventory().getLeggings(),p.getInventory().getBoots()};for(ItemStack i:a){if(i==null||i.getType()==Material.AIR)return null;ItemMeta m=i.getItemMeta();if(m==null)return null;String s=m.getPersistentDataContainer().get(armorSetKey,PersistentDataType.STRING);if(s==null)return null;if(found==null)found=s;else if(!found.equals(s))return null;}return found;}
    private void cinematicWeaponFx(Player p,String id,int skill){
        World w=p.getWorld();Location base=p.getLocation().clone().add(0,1.0,0);
        int quality=Math.max(1,Math.min(4,plugin.getConfig().getInt("effects.quality",4)));
        String particle=switch(id){
            case EMBERFALL->"FLAME";
            case NOCTIS->"REVERSE_PORTAL";
            case STORMPIERCER->"ELECTRIC_SPARK";
            case GAIA->"CLOUD";
            default->"SNOWFLAKE";
        };
        String model=switch(id){
            case EMBERFALL->skill==3?"fx_inferno_crown":skill==2?"fx_ember_meteor":"fx_ember_rift";
            case NOCTIS->skill==3?"fx_eclipse_cage":skill==2?"fx_soul_harvest":"fx_shade_step";
            case STORMPIERCER->"fx_thunderhead";
            case GAIA->skill==1?"fx_gale_bolt":"fx_cyclone_volley";
            default->skill==3?"fx_absolute_zero":skill==2?"fx_glacier_fang":"fx_frost_shard";
        };
        int cmd=switch(id){
            case EMBERFALL->skill==3?FX_INFERNO:skill==2?FX_EMBER_METEOR:FX_EMBER_RIFT;
            case NOCTIS->skill==3?FX_ECLIPSE:skill==2?FX_HARVEST:FX_SHADE;
            case STORMPIERCER->FX_THUNDER;
            case GAIA->skill==1?FX_GALE:FX_CYCLONE;
            default->skill==3?FX_SPIKE:skill==2?FX_STONE:FX_ROOT;
        };
        sound(w,base,switch(id){
            case EMBERFALL->"minecraft:entity.blaze.shoot";
            case NOCTIS->"minecraft:entity.warden.sonic_boom";
            case STORMPIERCER->"minecraft:entity.lightning_bolt.thunder";
            case GAIA->"minecraft:entity.wind_charge.wind_burst";
            default->"minecraft:block.glass.break";
        },.82f,skill==3?.62f:1.12f);
        new BukkitRunnable(){int t=0;public void run(){
            if(!p.isOnline()||t++>=8+skill*2){cancel();return;}
            Location c=p.getLocation().clone().add(0,1.0,0);
            double r=.72+t*.18+skill*.15;
            ring(w,c,particle,r,10+quality*4,t*.38);
            if(t%3==0)pulse(w,c,model,cmd,(float)(1.5+r*.42),6,p.getLocation().getYaw()+t*18,0);
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

    private void armorUtilitySkill(Player p,String set){
        int cd=plugin.getConfig().getInt("armor.cooldowns.skill2."+set,switch(set){case PHOENIX->32;case VOIDWALKER->27;case TITAN->34;case WATER_SOVEREIGN->29;default->31;});
        if(!ready(p,"armor:utility:"+set,cd,armorUtilitySkillName(set)))return;
        cinematicArmorFx(p,set);
        World w=p.getWorld();Location c=p.getLocation().clone();

        switch(set){
            case PHOENIX->{
                p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+6.0));
                try{
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,100,1,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.FIRE_RESISTANCE,180,0,true,false,false));
                }catch(Throwable ignored){}
                pulse(w,c.clone().add(0,1,0),"fx_phoenix_rebirth",FX_PHOENIX,3.6f,12,0,0);
                for(Entity ent:w.getNearbyEntities(c,4,3,4))if(ent instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                    l.setFireTicks(Math.max(l.getFireTicks(),80));hurt(l,plugin.getConfig().getDouble("armor.damage.skill2.phoenix",4.0),p);
                }
                sound(w,c,"minecraft:entity.blaze.shoot",1.05f,.82f);
            }
            case VOIDWALKER->{
                Location from=p.getLocation().clone(),to=safeForward(p,8.0);
                Vector path=to.toVector().subtract(from.toVector());
                for(int i=0;i<=6;i++){Location q=from.clone().add(path.clone().multiply(i/6.0)).add(0,1,0);particle(w,"REVERSE_PORTAL",q,12,.25,.35,.25,.025);}
                p.teleport(to);
                try{
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.INVISIBILITY,55,0,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SPEED,70,2,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,45,0,true,false,false));
                }catch(Throwable ignored){}
                pulse(w,to.clone().add(0,1,0),"fx_void_phase",FX_VOID,3.0f,10,p.getLocation().getYaw(),0);
                sound(w,to,"minecraft:entity.enderman.teleport",1.0f,1.15f);
            }
            case TITAN->{
                try{
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,100,1,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,100,1,true,false,false));
                }catch(Throwable ignored){}
                pulse(w,c.clone().add(0,1,0),"fx_titan_bastion",FX_TITAN,4.0f,13,0,0);
                ring(w,c,"CLOUD",3.3,26,0);
                for(Entity ent:w.getNearbyEntities(c,3.4,2.8,3.4))if(ent instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())){
                    Vector v=l.getLocation().toVector().subtract(c.toVector());v.setY(0);if(v.lengthSquared()>.01)l.setVelocity(v.normalize().multiply(.65).setY(.18));
                }
                sound(w,c,"minecraft:block.anvil.land",.95f,.62f);
            }
            case WATER_SOVEREIGN->{
                try{
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,100,0,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,100,0,true,false,false));
                }catch(Throwable ignored){}
                pulse(w,c.clone().add(0,1,0),"fx_water_sovereign_guard",FX_WATER_ARMOR,3.7f,12,0,0);
                new BukkitRunnable(){int t=0;public void run(){
                    if(!p.isOnline()||t++>=20){cancel();return;}
                    Location q=p.getLocation().clone().add(0,1,0);
                    if(t%4==0)ring(w,q,"BUBBLE_POP",2.3,18,t*.35);
                    for(Entity ent:w.getNearbyEntities(q,2.7,2.2,2.7)){
                        if(ent instanceof Projectile pr&&!Objects.equals(pr.getShooter(),p)){
                            Vector v=pr.getVelocity().multiply(-.70);if(v.lengthSquared()>.01)pr.setVelocity(v);
                        }
                    }
                }}.runTaskTimer(plugin,0,5);
                sound(w,c,"minecraft:item.trident.return",1.0f,.85f);
            }
            default->{
                try{
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,120,1,true,false,false));
                    p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.ABSORPTION,100,0,true,false,false));
                }catch(Throwable ignored){}
                pulse(w,c.clone().add(0,1.2,0),"fx_celestial_sanctuary",FX_CELESTIAL,3.8f,12,0,0);
                new BukkitRunnable(){int t=0;public void run(){
                    if(!p.isOnline()||t++>=4){cancel();return;}
                    Location q=p.getLocation().clone();
                    ring(w,q,"END_ROD",4.0,22,t*.45);
                    for(Entity ent:w.getNearbyEntities(q,4,3,4)){
                        if(ent instanceof Player ally&&(ally.getUniqueId().equals(p.getUniqueId())||ally.hasPermission("legendaryrais.ally")))ally.setHealth(Math.min(ally.getMaxHealth(),ally.getHealth()+1.0));
                        else if(ent instanceof LivingEntity l)hurt(l,plugin.getConfig().getDouble("armor.damage.skill2.celestial-pulse",1.5),p);
                    }
                }}.runTaskTimer(plugin,0,10);
                sound(w,c,"minecraft:block.amethyst_block.chime",1.0f,1.35f);
            }
        }
        bar(p,"ARMOR SKILL II • "+armorUtilitySkillName(set));
    }
    private ItemStack armorVisualItem(String set,String piece){
        ItemStack i=new ItemStack(Material.PAPER);
        ItemMeta m=i.getItemMeta(); if(m==null)return i;
        try{m.setItemModel(new NamespacedKey("legendaryv369","armor_visual/"+set+"_"+piece));}catch(Throwable ignored){}
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
        if(isBedrock(p)||p.isDead()||p.getGameMode()==GameMode.SPECTATOR){clearArmorVisuals(p.getUniqueId());return;}
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
                    d.setInterpolationDuration(1);d.setTeleportDuration(1);
                    d.setBrightness(new Display.Brightness(15,15));
                    d.getPersistentDataContainer().set(new NamespacedKey(plugin,"armor_visual_tag"),PersistentDataType.STRING,tag);
                    for(Player viewer:Bukkit.getOnlinePlayers())if(isBedrock(viewer))try{viewer.hideEntity(plugin,d);}catch(Throwable ignored){}
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
        lastSneakTap.remove(e.getPlayer().getUniqueId());
        armorPunchArmedUntil.remove(e.getPlayer().getUniqueId());
        bedrockCache.remove(e.getPlayer().getUniqueId());
        fxBudgetWindow.remove(e.getPlayer().getUniqueId());fxBudgetUsed.remove(e.getPlayer().getUniqueId());
        displayBudgetWindow.remove(e.getPlayer().getUniqueId());displayBudgetUsed.remove(e.getPlayer().getUniqueId());
        windLeapSafeUntil.remove(e.getPlayer().getUniqueId());
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
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,45,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.STRENGTH,45,0,true,false,false));
                                if(p.getHealth()<=p.getMaxHealth()*.50)p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,45,1,true,false,false));
                            }
                            case VOIDWALKER->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,45,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SPEED,45,1,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.NIGHT_VISION,240,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.JUMP_BOOST,45,0,true,false,false));
                            }
                            case TITAN->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,45,0,true,false,false));
                            }
                            case WATER_SOVEREIGN->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.WATER_BREATHING,80,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.DOLPHINS_GRACE,50,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,45,1,true,false,false));
                                if(p.isInWater()&&p.getHealth()<p.getMaxHealth())p.setHealth(Math.min(p.getMaxHealth(),p.getHealth()+1.0));
                            }
                            default->{
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.RESISTANCE,45,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.REGENERATION,45,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOW_FALLING,45,0,true,false,false));
                                p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.LUCK,45,0,true,false,false));
                            }
                        }
                    }catch(Throwable ignored){}
                }
            }
        }.runTaskTimer(plugin,20,60);
    }

    private void hurt(LivingEntity t,double amount,Player p){if(amount<=0||!t.isValid()||t.isDead())return;internalDamage.add(t.getUniqueId());try{t.damage(amount,p);}finally{internalDamage.remove(t.getUniqueId());}}
    private void hitFx(LivingEntity t,String id){
        Location c=t.getLocation().clone().add(0,1,0);World w=t.getWorld();
        switch(id){
            case EMBERFALL->{particle(w,"FLAME",c,28,.45,.42,.45,.07);particle(w,"LAVA",c,5,.25,.22,.25,.02);}
            case NOCTIS->{particle(w,"REVERSE_PORTAL",c,24,.4,.48,.4,.025);particle(w,"SCULK_SOUL",c,8,.25,.3,.25,.02);}
            case STORMPIERCER->{particle(w,"ELECTRIC_SPARK",c,30,.45,.55,.45,.10);particle(w,"FLASH",c,1,.05,.05,.05,0);}
            case GAIA->{particle(w,"GUST",c,7,.45,.35,.45,.04);particle(w,"CLOUD",c,24,.55,.35,.55,.04);}
            default->{particle(w,"SNOWFLAKE",c,30,.45,.55,.45,.04);blockFx(w,c.clone().add(0,-.7,0),Material.PACKED_ICE,.65f,8);}
        }
    }
    private List<LivingEntity> targets(Player p,double r,int max,boolean los){List<LivingEntity> out=new ArrayList<>();for(Entity e:p.getWorld().getNearbyEntities(p.getLocation(),r,r,r)){if(!(e instanceof LivingEntity l)||l.getUniqueId().equals(p.getUniqueId())||!l.isValid()||l.isDead())continue;if(los&&!p.hasLineOfSight(l))continue;out.add(l);}out.sort(Comparator.comparingDouble(x->x.getLocation().distanceSquared(p.getLocation())));return out.size()>max?new ArrayList<>(out.subList(0,max)):out;}
    private LivingEntity nearest(Player p,double r){List<LivingEntity> l=targets(p,r,1,true);return l.isEmpty()?null:l.get(0);}
    private LivingEntity ray(Player p,Vector d,double range,double radius){Location o=p.getEyeLocation();for(double x=.5;x<=range;x+=.55){Location c=o.clone().add(d.clone().multiply(x));for(Entity e:p.getWorld().getNearbyEntities(c,radius,radius,radius))if(e instanceof LivingEntity l&&!l.getUniqueId().equals(p.getUniqueId())&&l.isValid()&&!l.isDead())return l;if(c.getBlock().getType().isSolid())break;}return null;}
    private Location safeForward(Player p,double dist){Location base=p.getLocation().clone();Vector d=p.getEyeLocation().getDirection().clone();d.setY(0);if(d.lengthSquared()<.01)d=new Vector(1,0,0);d.normalize();for(double x=dist;x>=1;x-=.5){Location q=base.clone().add(d.clone().multiply(x));if(!q.getBlock().getType().isSolid()&&!q.clone().add(0,1,0).getBlock().getType().isSolid())return q;}return base;}
    private Vector rotateY(Vector v,double a){double c=Math.cos(a),s=Math.sin(a);return new Vector(v.getX()*c-v.getZ()*s,v.getY(),v.getX()*s+v.getZ()*c).normalize();}
    private void beam(World w,Location o,Vector d,double range,String particle,String model,int cmd){for(double x=1;x<=range;x+=1){Location c=o.clone().add(d.clone().multiply(x));particle(w,particle,c,2,.08,.08,.08,.01);if(((int)x)%4==0)pulse(w,c,model,cmd,.75f,5,yaw(d),pitch(d));if(c.getBlock().getType().isSolid())break;}}

    private boolean isBedrock(Player p){
        return bedrockCache.computeIfAbsent(p.getUniqueId(),id->{
            try{
                Class<?> api=Class.forName("org.geysermc.floodgate.api.FloodgateApi");
                Object inst=api.getMethod("getInstance").invoke(null);
                Object result=api.getMethod("isFloodgatePlayer",UUID.class).invoke(inst,id);
                return result instanceof Boolean b&&b;
            }catch(Throwable ignored){return false;}
        });
    }

    private PerfMode effectivePerf(Player p){
        String s=p.getPersistentDataContainer().get(perfModeKey,PersistentDataType.STRING);
        PerfMode configured=PerfMode.AUTO;
        if(s!=null)try{configured=PerfMode.valueOf(s);}catch(Throwable ignored){}
        if(configured!=PerfMode.AUTO)return configured;
        return isBedrock(p)?PerfMode.LOW:PerfMode.CINEMATIC;
    }

    private int particleBudget(Player p,int requested){
        PerfMode m=effectivePerf(p);long now=System.currentTimeMillis();UUID id=p.getUniqueId();
        long ws=fxBudgetWindow.getOrDefault(id,0L);
        if(now-ws>=1000L){fxBudgetWindow.put(id,now);fxBudgetUsed.put(id,0);}
        int cap=switch(m){case LOW->220;case BALANCED->600;case CINEMATIC->1600;default->220;};
        int used=fxBudgetUsed.getOrDefault(id,0);int left=Math.max(0,cap-used);int grant=Math.min(requested,left);
        fxBudgetUsed.put(id,used+grant);return grant;
    }

    private boolean allowDisplay(Player p){
        PerfMode m=effectivePerf(p);if(m==PerfMode.LOW)return false;
        if(m==PerfMode.CINEMATIC)return true;
        long now=System.currentTimeMillis();UUID id=p.getUniqueId();long ws=displayBudgetWindow.getOrDefault(id,0L);
        if(now-ws>=1000L){displayBudgetWindow.put(id,now);displayBudgetUsed.put(id,0);}
        int used=displayBudgetUsed.getOrDefault(id,0);if(used>=10)return false;displayBudgetUsed.put(id,used+1);return true;
    }

    private ItemStack fxItem(String model,int cmd){ItemStack i=new ItemStack(Material.PAPER);ItemMeta m=i.getItemMeta();if(m==null)return i;try{m.setCustomModelData(cmd);}catch(Throwable ignored){}try{m.setItemModel(new NamespacedKey("legendaryv34",model));}catch(Throwable ignored){}i.setItemMeta(m);return i;}
    private ItemDisplay display(World w,Location l,String model,int cmd,float scale,float yaw,float pitch){
        try{
            ItemDisplay d=w.spawn(l,ItemDisplay.class);d.setItemStack(fxItem(model,cmd));d.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.FIXED);
            d.setBillboard(Display.Billboard.CENTER);d.setBrightness(new Display.Brightness(15,15));d.setViewRange(48);
            d.setInterpolationDuration(3);d.setTeleportDuration(2);d.setRotation(yaw,pitch);
            var tr=d.getTransformation();tr.getScale().set(scale,scale,scale);d.setTransformation(tr);
            for(Player viewer:w.getPlayers()){
                if(viewer.getLocation().distanceSquared(l)>48*48||!allowDisplay(viewer))viewer.hideEntity(plugin,d);
            }
            return d;
        }catch(Throwable ignored){return null;}
    }
    private void pulse(World w,Location l,String model,int cmd,float max,int life,float yaw,float pitch){ItemDisplay d=display(w,l,model,cmd,Math.max(.35f,max*.38f),yaw,pitch);if(d==null)return;new BukkitRunnable(){int t=0;public void run(){if(++t>=life||!d.isValid()){d.remove();cancel();return;}float p=t/(float)Math.max(1,life),sc=Math.max(.32f,max*(.52f+.58f*(float)Math.sin(Math.min(1,p*1.35)*Math.PI)));var tr=d.getTransformation();tr.getScale().set(sc,sc,sc);d.setTransformation(tr);d.setRotation(yaw+t*7,pitch);}}.runTaskTimer(plugin,1,1);}
    private void blockFx(World w,Location l,Material mat,float scale,int life){
        try{
            BlockDisplay d=w.spawn(l,BlockDisplay.class);d.setBlock(mat.createBlockData());d.setBrightness(new Display.Brightness(15,15));
            var tr=d.getTransformation();tr.getScale().set(scale,scale,scale);d.setTransformation(tr);
            for(Player viewer:w.getPlayers())if(viewer.getLocation().distanceSquared(l)>40*40||effectivePerf(viewer)==PerfMode.LOW||!allowDisplay(viewer))viewer.hideEntity(plugin,d);
            new BukkitRunnable(){int t=0;public void run(){if(++t>=life||!d.isValid()){d.remove();cancel();}}}.runTaskTimer(plugin,1,1);
        }catch(Throwable ignored){}
    }
    private void particle(World w,String name,Location l,int count,double ox,double oy,double oz,double extra){
        try{
            Particle particle=Particle.valueOf(name);
            for(Player viewer:w.getPlayers()){
                PerfMode mode=effectivePerf(viewer);
                double range=mode==PerfMode.LOW?28.0:mode==PerfMode.BALANCED?40.0:56.0;
                if(viewer.getLocation().distanceSquared(l)>range*range)continue;
                double scale=mode==PerfMode.LOW?.24:mode==PerfMode.BALANCED?.55:1.0;
                int wanted=Math.max(1,(int)Math.ceil(count*scale));
                if(mode==PerfMode.LOW)wanted=Math.min(wanted,12);
                else if(mode==PerfMode.BALANCED)wanted=Math.min(wanted,28);
                int send=particleBudget(viewer,wanted);if(send<=0)continue;
                viewer.spawnParticle(particle,l,send,ox,oy,oz,extra);
            }
        }catch(Throwable ignored){}
    }
    private void sound(World w,Location l,String key,float volume,float pitch){try{w.playSound(l,key,volume,pitch);}catch(Throwable ignored){}}
    private void ring(World w,Location c,String name,double r,int points,double phase){for(int i=0;i<points;i++){double a=Math.PI*2*i/points+phase;particle(w,name,c.clone().add(Math.cos(a)*r,.15,Math.sin(a)*r),1,.02,.02,.02,0);}}
    private float yaw(Vector v){Vector n=v.clone().normalize();return(float)Math.toDegrees(Math.atan2(-n.getX(),n.getZ()));}private float pitch(Vector v){Vector n=v.clone().normalize();return(float)Math.toDegrees(-Math.asin(Math.max(-1,Math.min(1,n.getY()))));}
    private void bar(Player p,String s){try{p.sendActionBar(Component.text(s));}catch(Throwable ignored){p.sendMessage("§6[LegendaryRais] §f"+s);}}
}

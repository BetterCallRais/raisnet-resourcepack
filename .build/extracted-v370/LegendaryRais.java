package id.raisnet.legendaryrais;

import net.kyori.adventure.text.Component;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.Action;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.ProjectileHitEvent;
import org.bukkit.event.entity.ProjectileLaunchEvent;
import org.bukkit.projectiles.ProjectileSource;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataContainer;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitRunnable;
import org.bukkit.util.Vector;

import java.lang.reflect.Method;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public final class LegendaryRais extends JavaPlugin implements Listener, CommandExecutor {
    private static final String MENU_TITLE = "§0✦ LegendaryRais Arsenal ✦";
    private static final String WEAPON_SOUL_TIDE = "soul_tide_katana_v4";
    private static final String WEAPON_LEVIATHAN = "abyss_leviathan_trident_v3";
    private static final int SOUL_TIDE_SLOT = 11;
    private static final int LEVIATHAN_SLOT = 15;
    private static final int SOUL_TIDE_MODEL_DATA = 910041;
    private static final int LEVIATHAN_MODEL_DATA = 910042;
    private static final int FX_SOUL_SLASH_MODEL_DATA = 910101;
    private static final int FX_TIDAL_CRESCENT_MODEL_DATA = 910102;
    private static final int FX_UNDERTOW_MODEL_DATA = 910103;
    private static final int FX_DOMAIN_MODEL_DATA = 910104;
    private static final int FX_LEVIATHAN_FANG_MODEL_DATA = 910105;
    private static final int FX_MAELSTROM_MODEL_DATA = 910106;
    private static final int FX_LEVIATHAN_IMPACT_MODEL_DATA = 910107;
    private static final int FX_LIGHTNING_SPEAR_MODEL_DATA = 910108;
    private static final int FX_LEVIATHAN_PROJECTILE_MODEL_DATA = 910109;

    private NamespacedKey weaponKey;
    private NamespacedKey menuKey;
    private NamespacedKey thrownLeviathanKey;
    private NamespacedKey impactDoneKey;
    private NamespacedKey smoothLeviathanKey;
    private NamespacedKey waterAssetVersionKey;

    private enum Skill {
        ABYSSAL_STEP("Skill I", "Abyssal Step", "cooldowns.abyssal-step"),
        TIDAL_CRESCENT("Skill II", "Tidal Crescent", "cooldowns.tidal-crescent"),
        SOUL_UNDERTOW("Skill III", "Soul Undertow", "cooldowns.soul-undertow"),
        DROWNED_DOMAIN("Ultimate", "Domain of the Drowned Souls", "cooldowns.drowned-domain"),
        ABYSSAL_HARPOON("Skill I", "Abyssal Harpoon", "leviathan.cooldowns.abyssal-harpoon"),
        LEVIATHAN_FANG("Skill II", "Leviathan Fang", "leviathan.cooldowns.leviathan-fang"),
        MAELSTROM_PRISON("Skill III", "Maelstrom Prison", "leviathan.cooldowns.maelstrom-prison"),
        WRATH_LEVIATHAN("Ultimate", "Wrath of the Leviathan", "leviathan.cooldowns.wrath-of-the-leviathan");

        final String slot;
        final String display;
        final String configKey;

        Skill(String slot, String display, String configKey) {
            this.slot = slot;
            this.display = display;
            this.configKey = configKey;
        }
    }

    private final Map<UUID, EnumMap<Skill, Long>> cooldowns = new ConcurrentHashMap<>();
    private final Map<UUID, Long> inputDebounce = new ConcurrentHashMap<>();
    private final Map<UUID, Long> waterWalkFx = new ConcurrentHashMap<>();
    private final Map<UUID, Long> tidewalkerJumpGrace = new ConcurrentHashMap<>();
    private final Map<UUID, Long> recentMelee = new ConcurrentHashMap<>();
    private final Map<UUID, Long> pendingBedrockTap = new ConcurrentHashMap<>();
    private final Map<UUID, Integer> soulGauge = new ConcurrentHashMap<>();
    private final Map<UUID, Integer> comboHits = new ConcurrentHashMap<>();
    private final Map<UUID, Long> comboExpiry = new ConcurrentHashMap<>();
    private final Map<UUID, Integer> abyssGauge = new ConcurrentHashMap<>();
    private final Map<UUID, Integer> abyssMarks = new ConcurrentHashMap<>();
    private final Set<UUID> internalDamageTargets = Collections.newSetFromMap(new ConcurrentHashMap<>());
    private final Set<UUID> impactedProjectiles = Collections.newSetFromMap(new ConcurrentHashMap<>());
    private final Set<UUID> tidewalkerNoGravity = Collections.newSetFromMap(new ConcurrentHashMap<>());

    @Override
    public void onEnable() {
        saveDefaultConfig();
        applyV300ConfigMigration();
        weaponKey = new NamespacedKey(this, "weapon_id");
        menuKey = new NamespacedKey(this, "menu_weapon_id");
        thrownLeviathanKey = new NamespacedKey(this, "leviathan_thrown");
        impactDoneKey = new NamespacedKey(this, "leviathan_impact_done");
        smoothLeviathanKey = new NamespacedKey(this, "leviathan_smooth_carrier");
        waterAssetVersionKey = new NamespacedKey(this, "water_asset_version");
        Bukkit.getPluginManager().registerEvents(this, this);

        PluginCommand command = getCommand("riswp");
        if (command != null) command.setExecutor(this);
        new ArsenalExpansion(this).enable();

        getLogger().info("LegendaryRais v3.7.0 RECOVERY STABLE enabled. Reliable damage floors + Mace defense + Java 3D armor overlays + Bedrock legacy mapping compatibility active.");
        getLogger().info("/rislegend is the primary admin arsenal GUI; /riswp remains a legacy alias.");
        getLogger().info("Cooldowns: 30s default per active skill. Java + Geyser/Floodgate input supported.");
    }

    private void applyV300ConfigMigration() {
        int version = getConfig().getInt("config-version", 0);
        if (version >= 370) return;
        getConfig().set("gacha.gaia.windburst-ground-leap.ray-distance", 5.5);
        getConfig().set("gacha.gaia.windburst-ground-leap.horizontal", 1.15);
        getConfig().set("gacha.gaia.windburst-ground-leap.vertical", 1.55);
        getConfig().set("gacha.gaia.windburst-ground-leap.no-fall-ms", 5000L);
        getConfig().set("armor.damage.skill1.phoenix", 6.0);
        getConfig().set("armor.damage.skill1.voidwalker", 5.0);
        getConfig().set("armor.damage.skill1.titan", 7.0);
        getConfig().set("armor.damage.skill1.celestial", 4.0);
        getConfig().set("armor.damage.skill1.water_sovereign", 5.0);
        getConfig().set("armor.damage.skill2.phoenix", 4.0);
        getConfig().set("armor.damage.skill2.celestial-pulse", 1.5);
        getConfig().set("config-version", 370);
        getConfig().set("weapon-use-requires-op", false);
        getConfig().set("base-hit.sword", 38.0);
        getConfig().set("base-hit.trident", 44.0);
        getConfig().set("abyssal-step.damage", 650.0);
        getConfig().set("tidal-crescent.damage", 650.0);
        getConfig().set("soul-undertow.damage", 650.0);
        getConfig().set("soul-undertow.swirl-force", 0.36);
        getConfig().set("combo.soul-break-bonus-damage", 42.0);
        getConfig().set("ultimate.pulse-damage", 165.0);
        getConfig().set("ultimate.collapse-damage", 900.0);
        getConfig().set("leviathan.cooldowns.abyssal-harpoon", 1);
        getConfig().set("leviathan.cooldowns.leviathan-fang", 8);
        getConfig().set("leviathan.cooldowns.maelstrom-prison", 12);
        getConfig().set("leviathan.cooldowns.wrath-of-the-leviathan", 20);
        getConfig().set("leviathan.thrown.projectile-damage", 650.0);
        getConfig().set("leviathan.thrown.impact-bonus-damage", 650.0);
        getConfig().set("leviathan.thrown.lightning-aoe-damage", 320.0);
        getConfig().set("leviathan.thrown.lightning-radius", 5.8);
        getConfig().set("leviathan.thrown.gauge-on-throw", 6);
        getConfig().set("leviathan.thrown.gauge-on-impact", 16);
        getConfig().set("leviathan.thrown.max-flight-ticks", 34);
        getConfig().set("leviathan.thrown.blocks-per-tick", 1.28);
        getConfig().set("leviathan.thrown.hit-radius", 1.15);
        getConfig().set("leviathan.thrown.projectile-scale", 1.15);
        getConfig().set("leviathan.leviathan-fang.damage", 650.0);
        getConfig().set("leviathan.maelstrom-prison.pulse-damage", 165.0);
        getConfig().set("leviathan.ultimate.charge-damage", 650.0);
        getConfig().set("leviathan.ultimate.collapse-damage", 1000.0);
        getConfig().set("water-walk.jump-grace-ms", 780L);
        getConfig().set("water-walk.jump-velocity", 0.42);
        getConfig().set("water-walk.jump-forward-multiplier", 1.08);
        getConfig().set("armor.java-3d-overlay", true);
        getConfig().set("armor.java-3d-update-ticks", 1);
        getConfig().set("effects.quality", 4);
        getConfig().set("gacha.cooldowns.skill-1", 10);
        getConfig().set("gacha.cooldowns.skill-2", 16);
        getConfig().set("gacha.cooldowns.skill-3", 24);
        getConfig().set("armor.cooldowns.phoenix", 45);
        getConfig().set("armor.cooldowns.voidwalker", 32);
        getConfig().set("armor.cooldowns.titan", 40);
        getConfig().set("armor.cooldowns.celestial", 38);
        getConfig().set("armor.cooldowns.water_sovereign", 30);
        getConfig().set("gacha.emberfall.base-hit",26.4);
        getConfig().set("gacha.noctis.base-hit",22.8);
        getConfig().set("gacha.stormpiercer.base-hit",22.8);
        getConfig().set("gacha.gaia.base-hit",24.0);
        getConfig().set("gacha.astral.base-hit",22.8);
        for(String k:List.of("emberfall","noctis","stormpiercer","gaia","astral"))getConfig().set("gacha."+k+".damage",List.of(390.0,390.0,390.0));
        getConfig().set("gacha.emberfall.cooldowns",List.of(9,15,24));
        getConfig().set("gacha.noctis.cooldowns",List.of(8,14,22));
        getConfig().set("gacha.stormpiercer.cooldowns",List.of(7,13,21));
        getConfig().set("gacha.gaia.cooldowns",List.of(6,11,18));
        getConfig().set("gacha.astral.cooldowns",List.of(8,15,23));
        getConfig().set("gacha.stormpiercer.arrow-impact-damage",195.0);
        getConfig().set("armor.cooldowns.skill1.phoenix",16);
        getConfig().set("armor.cooldowns.skill1.voidwalker",15);
        getConfig().set("armor.cooldowns.skill1.titan",18);
        getConfig().set("armor.cooldowns.skill1.celestial",17);
        getConfig().set("armor.cooldowns.skill1.water_sovereign",16);
        getConfig().set("armor.cooldowns.skill2.phoenix",32);
        getConfig().set("armor.cooldowns.skill2.voidwalker",27);
        getConfig().set("armor.cooldowns.skill2.titan",34);
        getConfig().set("armor.cooldowns.skill2.celestial",31);
        getConfig().set("armor.cooldowns.skill2.water_sovereign",29);
        getConfig().set("performance.auto-bedrock-mode","LOW");
        getConfig().set("performance.low.particle-scale",0.24);
        getConfig().set("performance.balanced.particle-scale",0.55);
        getConfig().set("performance.low.hide-heavy-displays",true);
        getConfig().set("armor.input.double-sneak-window-ms",1000L);
        getConfig().set("armor.input.punch-arm-ms",6000L);
        saveConfig();
        getLogger().info("Migrated LegendaryRais config to v3.6.5 Weapon Rig & Armor Skill Hotfix defaults.");
    }

    @Override
    public void onDisable() {
        for (UUID id : new HashSet<>(tidewalkerNoGravity)) {
            Player p = Bukkit.getPlayer(id);
            if (p != null) restoreTidewalkerGravity(p);
        }
        cooldowns.clear();
        inputDebounce.clear();
        waterWalkFx.clear();
        tidewalkerJumpGrace.clear();
        recentMelee.clear();
        pendingBedrockTap.clear();
        soulGauge.clear();
        comboHits.clear();
        comboExpiry.clear();
        abyssGauge.clear();
        abyssMarks.clear();
        internalDamageTargets.clear();
        impactedProjectiles.clear();
        tidewalkerNoGravity.clear();
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player player)) {
            sender.sendMessage("§cCommand ini hanya bisa digunakan oleh player.");
            return true;
        }
        if (!isAdmin(player)) {
            player.sendMessage("§c/riswp hanya dapat digunakan oleh operator/admin LegendaryRais.");
            return true;
        }
        if (args.length > 0 && args[0].equalsIgnoreCase("reload")) {
            reloadConfig();
            player.sendMessage("§bLegendaryRais §7config berhasil di-reload.");
            return true;
        }
        player.sendMessage("§7/riswp sekarang legacy alias. Membuka §e/rislegend§7...");
        Bukkit.dispatchCommand(player,"rislegend");
        return true;
    }

    private boolean isAdmin(Player player) {
        return player.isOp() || player.hasPermission("legendaryrais.admin");
    }

    private boolean canUseWeapon(Player player) {
        return !getConfig().getBoolean("weapon-use-requires-op", false) || isAdmin(player);
    }

    private void openWeaponMenu(Player player) {
        Inventory inv = Bukkit.createInventory(null, 27, MENU_TITLE);
        ItemStack filler = named(Material.BLACK_STAINED_GLASS_PANE, "§0 ", Collections.emptyList());
        for (int i = 0; i < inv.getSize(); i++) inv.setItem(i, filler);

        inv.setItem(SOUL_TIDE_SLOT, createSoulTideKatana(true));
        inv.setItem(LEVIATHAN_SLOT, createLeviathanTrident(true));
        ItemStack info = named(Material.SOUL_LANTERN, "§b§lLEGENDARYRAIS ARSENAL",
                Arrays.asList(
                        "§7/riswp hanya untuk OP/admin.",
                        "§aPlayer biasa tetap bisa memakai senjata",
                        "§ajika mereka mempunyai Soul Tide asli.",
                        "",
                        "§bSkill I §8• §fRight Click / Tap §8→ §3Abyssal Step",
                        "§bSkill II §8• §fSneak + Left Click §8→ §3Tidal Crescent",
                        "§bSkill III §8• §fSneak + Right Click §8→ §3Soul Undertow",
                        "§dUltimate §8• §fSprint + Sneak + Right Click §8→ §5Drowned Souls",
                        "§3Passive §8• §fSoul Tidewalker §8→ §bWalk on Water",
                        "§3Combo §8• §f3 hit §8→ §bSoul Break",
                        "",
                        "§7Cooldown V6: Sword 30s • Spear 1/8/12/20s.",
                        "",
                        "§3Abyss Leviathan V6: Harpoon • Fang • Maelstrom • Wrath"
                ));
        inv.setItem(22, info);
        player.openInventory(inv);
    }

    private ItemStack named(Material material, String name, List<String> lore) {
        ItemStack item = new ItemStack(material);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(name);
            if (lore != null && !lore.isEmpty()) meta.setLore(lore);
            item.setItemMeta(meta);
        }
        return item;
    }

    ItemStack createSoulTideKatana(boolean menuCopy) {
        ItemStack item = new ItemStack(Material.NETHERITE_SWORD);
        ItemMeta meta = item.getItemMeta();
        if (meta == null) return item;

        meta.setDisplayName("§b§lSOUL TIDE §3§lSOVEREIGN BLADE §8[V6]");
        meta.setLore(Arrays.asList(
                "§7Legendary longsword forged from a drowned sovereign soul-current.",
                "",
                "§b✦ Skill I: §3Abyssal Step",
                "§7Right Click / Tap: dash menjadi arus air dan",
                "§7menebas target yang dilewati.",
                "",
                "§b✦ Skill II: §3Tidal Crescent",
                "§7Sneak + Left Click: slash sabit soul-water",
                "§7meluncur ke depan dan menembus beberapa target.",
                "",
                "§b✦ Skill III: §3Soul Undertow",
                "§7Sneak + Right Click: target sekitar diangkat",
                "§7dan diseret arus seperti bubble column Soul Sand.",
                "",
                "§d✦ Ultimate: §5Domain of the Drowned Souls",
                "§7Soul Gauge 100 + Sprint + Sneak + Right Click.",
                "§7Menciptakan domain arus spiritual lalu Tidal Collapse.",
                "",
                "§3✦ Passive: §bSoul Tidewalker",
                "§7Tidak tenggelam dan dapat berjalan di atas air.",
                "",
                "§3✦ Combo: §bSoul Break",
                "§7Hit ketiga memecahkan arus pada target.",
                "",
                "§fCooldown tiap active skill: §b30 detik §8(default)",
                "§7Action bar menampilkan sisa cooldown saat input skill.",
                "",
                menuCopy ? "§eKlik untuk mengambil Legendary Sword." : "§8LegendaryRais • Tradeable Legendary Weapon"
        ));
        applyLegendaryVisualMeta(meta, SOUL_TIDE_MODEL_DATA, "legendaryv368", "soul_tide", false);

        PersistentDataContainer pdc = meta.getPersistentDataContainer();
        pdc.set(weaponKey, PersistentDataType.STRING, WEAPON_SOUL_TIDE);
        pdc.set(waterAssetVersionKey, PersistentDataType.INTEGER, 368);
        if (menuCopy) pdc.set(menuKey, PersistentDataType.STRING, WEAPON_SOUL_TIDE);
        item.setItemMeta(meta);
        return item;
    }

    ItemStack createLeviathanTrident(boolean menuCopy) {
        ItemStack item = new ItemStack(Material.TRIDENT);
        ItemMeta meta = item.getItemMeta();
        if (meta == null) return item;

        meta.setDisplayName("§3§lABYSS LEVIATHAN §8§lTRIDENT §b[V6]");
        meta.setLore(Arrays.asList(
                "§7A dark relic forged from the sovereign bones of the abyss.",
                "",
                "§b✦ Skill I: §3Abyssal Harpoon",
                "§7Right Click / Tap: tembak harpoon abyss,",
                "§7tarik target atau tarik dirimu ke titik benturan.",
                "",
                "§b✦ Skill II: §3Leviathan Fang",
                "§7Sneak + Left Click: rahang Leviathan menerkam",
                "§7area cone dan menumpuk Abyss Mark.",
                "",
                "§b✦ Skill III: §3Maelstrom Prison",
                "§7Sneak + Right Click: penjara vortex yang",
                "§7memutar dan menarik musuh ke pusat pusaran.",
                "",
                "§d✦ Ultimate: §5Wrath of the Leviathan",
                "§7Abyss Gauge 100 + Sprint + Sneak + Right Click.",
                "§7Leviathan spectral menerjang lalu Abyss Collapse.",
                "",
                "§3✦ Passive: §bSovereign of the Abyss",
                "§7Water Breathing + gerak air lebih cepat saat di air.",
                "§73 Abyss Mark memicu Leviathan Bite.",
                "",
                "§fCooldown tiap active skill: §b30 detik §8(default)",
                menuCopy ? "§eKlik untuk mengambil trident." : "§8LegendaryRais • Tradeable Legendary Weapon"
        ));
        applyLegendaryVisualMeta(meta, LEVIATHAN_MODEL_DATA, "legendaryv368", "leviathan", true);
        PersistentDataContainer pdc = meta.getPersistentDataContainer();
        pdc.set(weaponKey, PersistentDataType.STRING, WEAPON_LEVIATHAN);
        pdc.set(waterAssetVersionKey, PersistentDataType.INTEGER, 368);
        if (menuCopy) pdc.set(menuKey, PersistentDataType.STRING, WEAPON_LEVIATHAN);
        item.setItemMeta(meta);
        return item;
    }

    private boolean isLeviathan(ItemStack item) {
        return matchesLegendaryWeapon(item, Material.TRIDENT, WEAPON_LEVIATHAN, LEVIATHAN_MODEL_DATA,
                "legendaryv368:leviathan", true);
    }

    private boolean isSoulTide(ItemStack item) {
        return matchesLegendaryWeapon(item, Material.NETHERITE_SWORD, WEAPON_SOUL_TIDE, SOUL_TIDE_MODEL_DATA,
                "legendaryv368:soul_tide", false);
    }

    private boolean matchesLegendaryWeapon(ItemStack item, Material material, String weaponId, int modelData,
                                            String itemModelKey, boolean loyalty) {
        if (item == null || item.getType() != material) return false;
        ItemMeta meta = item.getItemMeta();
        if (meta == null) return false;

        String id = meta.getPersistentDataContainer().get(weaponKey, PersistentDataType.STRING);
        if (weaponId.equals(id)) {
            ensureLegendaryRuntimeMeta(item, weaponId, modelData, itemModelKey, loyalty);
            return true;
        }

        // Migration / self-heal path for weapons created by older LegendaryRais builds.
        // Recognise either the modern item_model, the old Soul Tide Katana model, or legacy CMD.
        String currentModel = readItemModel(meta);
        boolean oldSoulModel = WEAPON_SOUL_TIDE.equals(weaponId) && ("soultide:soul_tide_katana".equals(currentModel) || "soultide:soul_tide_sovereign_blade".equals(currentModel));
        if (itemModelKey.equals(currentModel) || oldSoulModel || modelData == readCustomModelNumber(meta)) {
            meta.getPersistentDataContainer().set(weaponKey, PersistentDataType.STRING, weaponId);
            meta.getPersistentDataContainer().set(waterAssetVersionKey, PersistentDataType.INTEGER, 368);
            String[] key = itemModelKey.split(":", 2);
            applyLegendaryVisualMeta(meta, modelData, key[0], key[1], loyalty);
            if (WEAPON_SOUL_TIDE.equals(weaponId)) meta.setDisplayName("§b§lSOUL TIDE §3§lSOVEREIGN BLADE §8[V6]");
            if (WEAPON_LEVIATHAN.equals(weaponId)) meta.setDisplayName("§3§lABYSS LEVIATHAN §8§lTRIDENT §b[V6]");
            item.setItemMeta(meta);
            return true;
        }
        return false;
    }

    private void ensureLegendaryRuntimeMeta(ItemStack item, String weaponId, int modelData, String itemModelKey, boolean loyalty) {
        ItemMeta meta = item.getItemMeta();
        if (meta == null) return;
        boolean needsRepair = !itemModelKey.equals(readItemModel(meta)) || readCustomModelNumber(meta) != modelData || !readUnbreakable(meta);
        if (needsRepair || loyalty) {
            String[] key = itemModelKey.split(":", 2);
            meta.getPersistentDataContainer().set(weaponKey, PersistentDataType.STRING, weaponId);
            meta.getPersistentDataContainer().set(waterAssetVersionKey, PersistentDataType.INTEGER, 368);
            applyLegendaryVisualMeta(meta, modelData, key[0], key[1], loyalty);
            if (WEAPON_SOUL_TIDE.equals(weaponId)) meta.setDisplayName("§b§lSOUL TIDE §3§lSOVEREIGN BLADE §8[V6]");
            if (WEAPON_LEVIATHAN.equals(weaponId)) meta.setDisplayName("§3§lABYSS LEVIATHAN §8§lTRIDENT §b[V6]");
            item.setItemMeta(meta);
        }
    }

    private void applyLegendaryVisualMeta(ItemMeta meta, int modelData, String namespace, String path, boolean loyalty) {
        meta.setUnbreakable(true);

        // Legacy path (Paper 1.21.1 / ViaVersion translation).
        try { meta.setCustomModelData(modelData); } catch (Throwable ignored) {}

        // Modern custom_model_data component: explicitly set both floats[0] and strings[0].
        // This makes range_dispatch/select resource-pack fallbacks reliable on 1.21.4+ / 26.x.
        try {
            Method getter = meta.getClass().getMethod("getCustomModelDataComponent");
            Object component = getter.invoke(meta);
            Method setFloats = component.getClass().getMethod("setFloats", List.class);
            setFloats.invoke(component, Collections.singletonList((float) modelData));
            try {
                Method setStrings = component.getClass().getMethod("setStrings", List.class);
                setStrings.invoke(component, Collections.singletonList(namespace + ":" + path));
            } catch (Throwable ignored) {}
            for (Method m : meta.getClass().getMethods()) {
                if (m.getName().equals("setCustomModelDataComponent") && m.getParameterCount() == 1) {
                    m.invoke(meta, component);
                    break;
                }
            }
        } catch (Throwable ignored) {}

        // Strongest modern path: direct minecraft:item_model component.
        try {
            Method setItemModel = meta.getClass().getMethod("setItemModel", NamespacedKey.class);
            setItemModel.invoke(meta, new NamespacedKey(namespace, path));
        } catch (Throwable ignored) {}

        try {
            Method glint = meta.getClass().getMethod("setEnchantmentGlintOverride", Boolean.class);
            glint.invoke(meta, Boolean.TRUE);
        } catch (Throwable ignored) {}

        if (loyalty) applyLoyalty(meta);
    }

    private void applyLoyalty(ItemMeta meta) {
        try {
            Class<?> enchantmentClass = Class.forName("org.bukkit.enchantments.Enchantment");
            Object loyalty = enchantmentClass.getField("LOYALTY").get(null);
            for (Method m : meta.getClass().getMethods()) {
                if (m.getName().equals("addEnchant") && m.getParameterCount() == 3) {
                    m.invoke(meta, loyalty, 3, true);
                    return;
                }
            }
        } catch (Throwable ignored) {}
    }

    private String readItemModel(ItemMeta meta) {
        try {
            Method getItemModel = meta.getClass().getMethod("getItemModel");
            Object key = getItemModel.invoke(meta);
            return key == null ? "" : key.toString();
        } catch (Throwable ignored) { return ""; }
    }

    private int readCustomModelNumber(ItemMeta meta) {
        // Modern component first.
        try {
            Method getter = meta.getClass().getMethod("getCustomModelDataComponent");
            Object component = getter.invoke(meta);
            Method getFloats = component.getClass().getMethod("getFloats");
            Object result = getFloats.invoke(component);
            if (result instanceof List<?> list && !list.isEmpty() && list.get(0) instanceof Number number) {
                return Math.round(number.floatValue());
            }
        } catch (Throwable ignored) {}
        // Legacy integer fallback.
        try {
            Method has = meta.getClass().getMethod("hasCustomModelData");
            if (Boolean.TRUE.equals(has.invoke(meta))) {
                Method get = meta.getClass().getMethod("getCustomModelData");
                Object value = get.invoke(meta);
                if (value instanceof Number n) return n.intValue();
            }
        } catch (Throwable ignored) {}
        return Integer.MIN_VALUE;
    }

    private boolean readUnbreakable(ItemMeta meta) {
        try {
            Method method = meta.getClass().getMethod("isUnbreakable");
            return Boolean.TRUE.equals(method.invoke(meta));
        } catch (Throwable ignored) { return false; }
    }

    int repairWaterItems(Player player) {
        int fixed = 0;
        PlayerInventory inv = player.getInventory();
        for (int slot = 0; slot < inv.getSize(); slot++) {
            ItemStack old = inv.getItem(slot);
            ItemStack fresh = refreshWaterItem(old);
            if (fresh != old) { inv.setItem(slot, fresh); fixed++; }
        }
        Inventory ender = player.getEnderChest();
        for (int slot = 0; slot < ender.getSize(); slot++) {
            ItemStack old = ender.getItem(slot);
            ItemStack fresh = refreshWaterItem(old);
            if (fresh != old) { ender.setItem(slot, fresh); fixed++; }
        }
        return fixed;
    }

    private ItemStack refreshWaterItem(ItemStack old) {
        if (old == null || old.getType() == Material.AIR) return old;
        ItemMeta meta = old.getItemMeta();
        if (meta == null) return old;
        String id = meta.getPersistentDataContainer().get(weaponKey, PersistentDataType.STRING);
        String model = readItemModel(meta);
        int cmd = readCustomModelNumber(meta);
        boolean soul = WEAPON_SOUL_TIDE.equals(id) || "legendaryv368:soul_tide".equals(model) || "soultide:soul_tide_sovereign_blade".equals(model) ||
                "soultide:soul_tide_katana".equals(model) || cmd == SOUL_TIDE_MODEL_DATA;
        boolean levi = WEAPON_LEVIATHAN.equals(id) || "legendaryv368:leviathan".equals(model) || "legendaryrais:abyss_leviathan_trident".equals(model) ||
                cmd == LEVIATHAN_MODEL_DATA;
        if (!soul && !levi) return old;
        Integer ver = meta.getPersistentDataContainer().get(waterAssetVersionKey, PersistentDataType.INTEGER);
        String expected = soul ? "legendaryv368:soul_tide" : "legendaryv368:leviathan";
        Material material = soul ? Material.NETHERITE_SWORD : Material.TRIDENT;
        if (ver != null && ver >= 368 && expected.equals(model) && old.getType() == material && readUnbreakable(meta)) return old;
        ItemStack fresh = soul ? createSoulTideKatana(false) : createLeviathanTrident(false);
        fresh.setAmount(old.getAmount());
        return fresh;
    }

    @EventHandler
    public void onWaterAssetJoin(PlayerJoinEvent event) {
        new BukkitRunnable() {
            @Override public void run() {
                Player p = event.getPlayer();
                if (!p.isOnline()) return;
                int fixed = repairWaterItems(p);
                if (fixed > 0) {
                    p.sendMessage("§bLegendaryRais §8• §a" + fixed + " Water Relic item diperbarui ke asset v3.6.8.");
                    getLogger().info("[WATER-ASSET-MIGRATION] " + p.getName() + " refreshed " + fixed + " item(s).");
                }
            }
        }.runTaskLater(this, 8L);
    }

    @EventHandler(ignoreCancelled = true)
    public void onMenuClick(InventoryClickEvent event) {
        if (!MENU_TITLE.equals(event.getView().getTitle())) return;
        event.setCancelled(true);
        if (!(event.getWhoClicked() instanceof Player player)) return;
        if (!isAdmin(player)) {
            player.closeInventory();
            return;
        }
        ItemStack clicked = event.getCurrentItem();
        if (clicked == null || clicked.getType() == Material.AIR) return;
        ItemMeta meta = clicked.getItemMeta();
        if (meta == null) return;
        String id = meta.getPersistentDataContainer().get(menuKey, PersistentDataType.STRING);
        if (!WEAPON_SOUL_TIDE.equals(id) && !WEAPON_LEVIATHAN.equals(id)) return;

        if (player.getInventory().firstEmpty() == -1) {
            player.sendMessage("§cInventory penuh. Kosongkan 1 slot dulu.");
            return;
        }
        if (WEAPON_SOUL_TIDE.equals(id)) {
            player.getInventory().addItem(createSoulTideKatana(false));
            player.sendMessage("§b✦ §fSoul Tide Sovereign Blade §7ditambahkan ke inventory.");
        } else {
            player.getInventory().addItem(createLeviathanTrident(false));
            player.sendMessage("§3✦ §fAbyss Leviathan Trident V6 §7ditambahkan ke inventory.");
        }
        player.closeInventory();
        playSound(player.getWorld(), player.getLocation(), "BLOCK_CONDUIT_ACTIVATE", 1.0f, 1.20f);
    }

    @EventHandler(ignoreCancelled = true)
    public void onMenuDrag(InventoryDragEvent event) {
        if (MENU_TITLE.equals(event.getView().getTitle())) event.setCancelled(true);
    }

    // ---------------------------------------------------------------------
    // Input / control layer
    // ---------------------------------------------------------------------

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void onInteract(PlayerInteractEvent event) {
        Player player = event.getPlayer();
        if (event.getHand() != null && event.getHand() != EquipmentSlot.HAND) return;
        ItemStack held = player.getInventory().getItemInMainHand();
        boolean soul = isSoulTide(held);
        boolean leviathan = isLeviathan(held);
        if (!soul && !leviathan) return;
        if (!canUseWeapon(player)) {
            actionBar(player, "Legendary weapon terkunci untuk operator oleh config server.");
            return;
        }

        Action action = event.getAction();
        boolean right = action == Action.RIGHT_CLICK_AIR || action == Action.RIGHT_CLICK_BLOCK;
        boolean left = action == Action.LEFT_CLICK_AIR || action == Action.LEFT_CLICK_BLOCK;
        if (!right && !left) return;

        boolean handled = false;
        if (soul) {
            if (player.isSneaking() && player.isSprinting() && right) { handled = true; useDrownedDomain(player); }
            else if (player.isSneaking() && right) { handled = true; useSoulUndertow(player, isBedrock(player) ? "bedrock-sneak-use" : "java-sneak-right"); }
            else if (player.isSneaking() && left) { handled = true; useTidalCrescent(player); }
            else if (!player.isSneaking() && right) { handled = true; useAbyssalStep(player); }
        } else {
            if (player.isSneaking() && player.isSprinting() && right) { handled = true; useWrathLeviathan(player); }
            else if (player.isSneaking() && right) { handled = true; useMaelstromPrison(player); }
            else if (player.isSneaking() && left) { handled = true; useLeviathanFang(player); }
            else if (!player.isSneaking() && right) {
                // V6 custom projectile: no vanilla Trident entity and the weapon never leaves inventory.
                handled = true;
                useAbyssalHarpoon(player);
            }
        }
        if (handled) event.setCancelled(true);
    }

    @EventHandler(ignoreCancelled = true)
    public void onBedrockArmSwing(PlayerAnimationEvent event) {
        Player player = event.getPlayer();
        if (!isBedrock(player)) return;
        ItemStack held = player.getInventory().getItemInMainHand();
        boolean soul = isSoulTide(held);
        boolean leviathan = isLeviathan(held);
        if (!soul && !leviathan) return;
        if (!canUseWeapon(player)) return;

        if (player.isSneaking()) {
            if (soul) useTidalCrescent(player); else useLeviathanFang(player);
            return;
        }
        long token = System.nanoTime();
        UUID id = player.getUniqueId();
        pendingBedrockTap.put(id, token);
        new BukkitRunnable() {
            @Override public void run() {
                if (!player.isOnline()) return;
                if (!Objects.equals(pendingBedrockTap.get(id), token)) return;
                long meleeAt = recentMelee.getOrDefault(id, 0L);
                if (System.currentTimeMillis() - meleeAt < 180L) return;
                if (player.isSneaking()) return;
                ItemStack now = player.getInventory().getItemInMainHand();
                if (isSoulTide(now)) useAbyssalStep(player);
                else if (isLeviathan(now)) showLeviathanStatus(player);
            }
        }.runTaskLater(this, 1L);
    }

    @EventHandler(ignoreCancelled = true)
    public void onSneakStatus(PlayerToggleSneakEvent event) {
        if (!event.isSneaking()) return;
        Player player = event.getPlayer();
        ItemStack held = player.getInventory().getItemInMainHand();
        if (isSoulTide(held)) showFullStatus(player);
        else if (isLeviathan(held)) showLeviathanStatus(player);
    }

    // ---------------------------------------------------------------------
    // Combo + Soul Gauge
    // ---------------------------------------------------------------------

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void onWeaponMelee(EntityDamageByEntityEvent event) {
        if (!(event.getDamager() instanceof Player player)) return;
        if (!(event.getEntity() instanceof LivingEntity target)) return;
        ItemStack held = player.getInventory().getItemInMainHand();
        boolean soul = isSoulTide(held);
        boolean leviathan = isLeviathan(held);
        if (!soul && !leviathan) return;
        if (!canUseWeapon(player)) return;
        recentMelee.put(player.getUniqueId(), System.currentTimeMillis());
        pendingBedrockTap.remove(player.getUniqueId());
        if (internalDamageTargets.contains(target.getUniqueId())) return;

        // Legendary base-hit floor: normal melee must feel legendary too.
        if (soul) {
            event.setDamage(Math.max(event.getDamage(), getConfig().getDouble("base-hit.sword", 38.0)));
        } else if (leviathan) {
            event.setDamage(Math.max(event.getDamage(), getConfig().getDouble("base-hit.trident", 44.0)));
        }
        spawnWaterImpactFx(target, player, leviathan);

        if (player.isSneaking()) {
            // Keep the legendary base melee hit. Skill damage is additional, not a replacement.
            if (soul) useTidalCrescent(player); else useLeviathanFang(player);
            return;
        }

        if (leviathan) {
            addAbyssGauge(player, getConfig().getInt("leviathan.passive.gauge-per-hit", 7));
            int marks = abyssMarks.getOrDefault(target.getUniqueId(), 0) + 1;
            if (marks >= 3) {
                abyssMarks.remove(target.getUniqueId());
                double bite = Math.max(0.0, getConfig().getDouble("leviathan.passive.three-mark-bonus-damage", 4.0));
                Location hit = target.getLocation().clone().add(0, 1.0, 0);
                spawn(target.getWorld(), "SOUL_FIRE_FLAME", hit, 30, 0.75, 0.65, 0.75, 0.04);
                spawn(target.getWorld(), "BUBBLE_POP", hit, 38, 0.8, 0.55, 0.8, 0.12);
                spawnRing(target.getWorld(), hit, "SOUL", 1.0, 18, 0.0);
                playSound(target.getWorld(), hit, "ENTITY_ELDER_GUARDIAN_CURSE", 0.7f, 0.65f);
                if (bite > 0) damageInternal(target, bite, player);
                addAbyssGauge(player, getConfig().getInt("leviathan.passive.gauge-three-mark", 12));
                actionBar(player, "LEVIATHAN BITE • Abyss Gauge " + getAbyssGauge(player) + "/" + maxAbyssGauge());
            } else {
                abyssMarks.put(target.getUniqueId(), marks);
                actionBar(player, "Abyss Mark " + marks + "/3 • Abyss Gauge " + getAbyssGauge(player) + "/" + maxAbyssGauge());
            }
            return;
        }

        long now = System.currentTimeMillis();
        UUID id = player.getUniqueId();
        int combo = now <= comboExpiry.getOrDefault(id, 0L) ? comboHits.getOrDefault(id, 0) + 1 : 1;
        if (combo > 3) combo = 1;
        comboHits.put(id, combo);
        comboExpiry.put(id, now + Math.max(800L, getConfig().getLong("combo.reset-ms", 2500L)));
        if (combo == 1) {
            addGauge(player, getConfig().getInt("combo.gauge-hit-1", 5));
            spawn(target.getWorld(), "SPLASH", target.getLocation().clone().add(0, 1.0, 0), 12, 0.35, 0.45, 0.35, 0.05);
        } else if (combo == 2) {
            addGauge(player, getConfig().getInt("combo.gauge-hit-2", 7));
            spawn(target.getWorld(), "BUBBLE", target.getLocation().clone().add(0, 1.0, 0), 16, 0.4, 0.55, 0.4, 0.04);
            spawn(target.getWorld(), "SOUL", target.getLocation().clone().add(0, 1.0, 0), 6, 0.3, 0.4, 0.3, 0.01);
        } else {
            addGauge(player, getConfig().getInt("combo.gauge-hit-3", 12));
            comboHits.put(id, 0);
            double bonus = Math.max(0.0, getConfig().getDouble("combo.soul-break-bonus-damage", 3.0));
            Location hit = target.getLocation().clone().add(0, 0.9, 0);
            spawn(target.getWorld(), "SPLASH", hit, 42, 0.72, 0.65, 0.72, 0.16);
            spawn(target.getWorld(), "SOUL_FIRE_FLAME", hit, 18, 0.55, 0.5, 0.55, 0.025);
            spawn(target.getWorld(), "BUBBLE_POP", hit, 28, 0.58, 0.45, 0.58, 0.10);
            playSound(target.getWorld(), hit, "ITEM_TRIDENT_RIPTIDE_2", 0.8f, 1.2f);
            if (bonus > 0) damageInternal(target, bonus, player);
            Vector kb = target.getLocation().toVector().subtract(player.getLocation().toVector());
            if (kb.lengthSquared() > 0.0001) target.setVelocity(kb.normalize().multiply(0.38).setY(0.18));
        }
        actionBar(player, "Combo " + combo + "/3 • Soul Gauge " + getGauge(player) + "/" + maxGauge());
    }

    private int getGauge(Player player) {
        return soulGauge.getOrDefault(player.getUniqueId(), 0);
    }

    private int maxGauge() {
        return Math.max(1, getConfig().getInt("ultimate.max-gauge", 100));
    }

    private void addGauge(Player player, int amount) {
        if (amount <= 0) return;
        UUID id = player.getUniqueId();
        soulGauge.put(id, Math.min(maxGauge(), getGauge(player) + amount));
    }

    // ---------------------------------------------------------------------
    // Skill I - Abyssal Step
    // ---------------------------------------------------------------------

    private void useAbyssalStep(Player player) {
        if (!beginInput(player, Skill.ABYSSAL_STEP, 250L)) return;
        if (!isReady(player, Skill.ABYSSAL_STEP)) return;
        startCooldown(player, Skill.ABYSSAL_STEP);

        final Vector dir = player.getEyeLocation().getDirection().clone();
        if (dir.lengthSquared() < 0.001) dir.setX(1.0);
        dir.normalize();
        dir.setY(Math.max(-0.08, Math.min(0.16, dir.getY() * 0.35)));
        final int ticks = Math.max(5, getConfig().getInt("abyssal-step.duration-ticks", 10));
        final double speed = clamp(getConfig().getDouble("abyssal-step.speed", 0.82), 0.25, 1.35);
        final double damage = Math.max(0.0, getConfig().getDouble("abyssal-step.damage", 6.0));
        final double hitRadius = clamp(getConfig().getDouble("abyssal-step.hit-radius", 1.45), 0.5, 3.0);
        final Set<UUID> hit = new HashSet<>();

        playSound(player.getWorld(), player.getLocation(), "ITEM_TRIDENT_RIPTIDE_3", 1.0f, 1.55f);
        playSound(player.getWorld(), player.getLocation(), "BLOCK_CONDUIT_ACTIVATE", 0.65f, 1.75f);
        actionBar(player, "Skill I • Abyssal Step digunakan • cooldown " + cooldownSeconds(Skill.ABYSSAL_STEP) + "s");
        spawnFxPulse(player.getWorld(), player.getLocation().clone().add(0, 1.15, 0), "fx_soul_slash", FX_SOUL_SLASH_MODEL_DATA, 2.8f, 12, player.getLocation().getYaw(), 0f);

        new BukkitRunnable() {
            int tick = 0;
            @Override
            public void run() {
                tick++;
                if (!player.isOnline() || !isSoulTide(player.getInventory().getItemInMainHand()) || tick > ticks) {
                    cancel();
                    return;
                }
                Vector motion = dir.clone().multiply(speed);
                player.setVelocity(motion);
                player.setFallDistance(0f);
                Location p = player.getLocation().clone().add(0, 0.85, 0);
                World world = player.getWorld();
                spawn(world, "SPLASH", p, 22, 0.45, 0.42, 0.45, 0.12);
                spawn(world, "BUBBLE", p, 18, 0.42, 0.38, 0.42, 0.08);
                spawn(world, "SOUL_FIRE_FLAME", p, 5, 0.28, 0.30, 0.28, 0.015);
                if (tick % 3 == 0) {
                    spawnFxPulse(world, p, "fx_soul_slash", FX_SOUL_SLASH_MODEL_DATA, 2.1f, 7,
                            player.getLocation().getYaw() + tick * 21f, 0f);
                }

                for (Entity e : world.getNearbyEntities(p, hitRadius, hitRadius, hitRadius)) {
                    if (!(e instanceof LivingEntity target)) continue;
                    if (target.getUniqueId().equals(player.getUniqueId()) || hit.contains(target.getUniqueId())) continue;
                    if (!target.isValid() || target.isDead()) continue;
                    hit.add(target.getUniqueId());
                    damageInternal(target, damage, player);
                    target.setVelocity(dir.clone().multiply(0.52).setY(0.16));
                    addGauge(player, getConfig().getInt("abyssal-step.gauge-per-hit", 4));
                    Location h = target.getLocation().clone().add(0, 1.0, 0);
                    spawn(world, "SPLASH", h, 36, 0.55, 0.55, 0.55, 0.16);
                    spawn(world, "SOUL", h, 13, 0.4, 0.45, 0.4, 0.025);
                    playSound(world, h, "ENTITY_PLAYER_SPLASH_HIGH_SPEED", 0.8f, 1.4f);
                }
            }
        }.runTaskTimer(this, 0L, 1L);
    }

    // ---------------------------------------------------------------------
    // Skill II - Tidal Crescent
    // ---------------------------------------------------------------------

    private void useTidalCrescent(Player player) {
        if (!beginInput(player, Skill.TIDAL_CRESCENT, 250L)) return;
        if (!isReady(player, Skill.TIDAL_CRESCENT)) return;
        startCooldown(player, Skill.TIDAL_CRESCENT);

        final Location origin = player.getEyeLocation().clone().add(0, -0.25, 0);
        final World world = player.getWorld();
        final Vector dir = player.getLocation().getDirection().clone();
        dir.setY(Math.max(-0.08, Math.min(0.10, dir.getY() * 0.25)));
        if (dir.lengthSquared() < 0.001) dir.setX(1.0);
        dir.normalize();
        final Vector side = new Vector(-dir.getZ(), 0, dir.getX()).normalize();
        final int travelTicks = Math.max(8, getConfig().getInt("tidal-crescent.travel-ticks", 18));
        final double step = clamp(getConfig().getDouble("tidal-crescent.blocks-per-tick", 0.82), 0.35, 1.35);
        final double damage = Math.max(0, getConfig().getDouble("tidal-crescent.damage", 7.0));
        final double width = clamp(getConfig().getDouble("tidal-crescent.width", 1.65), 0.7, 3.2);
        final Set<UUID> hit = new HashSet<>();

        playSound(world, origin, "ITEM_TRIDENT_THROW", 1.0f, 0.72f);
        playSound(world, origin, "ENTITY_PLAYER_SPLASH_HIGH_SPEED", 1.0f, 1.25f);
        actionBar(player, "Skill II • Tidal Crescent digunakan • cooldown " + cooldownSeconds(Skill.TIDAL_CRESCENT) + "s");
        spawnFxPulse(world, origin.clone().add(dir.clone().multiply(1.3)), "fx_tidal_crescent", FX_TIDAL_CRESCENT_MODEL_DATA,
                3.0f, 12, player.getLocation().getYaw(), 0f);

        new BukkitRunnable() {
            int tick = 0;
            @Override
            public void run() {
                tick++;
                if (tick > travelTicks || !player.isOnline()) {
                    cancel();
                    return;
                }
                Location center = origin.clone().add(dir.clone().multiply(tick * step));
                if (tick % 2 == 0) {
                    spawnFxPulse(world, center, "fx_tidal_crescent", FX_TIDAL_CRESCENT_MODEL_DATA,
                            2.55f, 5, player.getLocation().getYaw(), 0f);
                }
                double phase = tick * 0.38;
                for (int i = -7; i <= 7; i++) {
                    double t = i / 7.0;
                    double horizontal = t * width;
                    double curve = (1.0 - Math.abs(t)) * 0.62;
                    Location arc = center.clone().add(side.clone().multiply(horizontal)).add(0, curve, 0);
                    spawn(world, "SPLASH", arc, 2, 0.04, 0.04, 0.04, 0.015);
                    if ((i + tick) % 2 == 0) spawn(world, "SOUL", arc, 1, 0.025, 0.025, 0.025, 0.0);
                    if ((i + tick) % 3 == 0) spawn(world, "BUBBLE", arc.clone().add(0, Math.sin(phase + i) * 0.08, 0), 1, 0.02, 0.02, 0.02, 0.0);
                }

                for (Entity e : world.getNearbyEntities(center, width + 0.45, 1.55, width + 0.45)) {
                    if (!(e instanceof LivingEntity target)) continue;
                    if (target.getUniqueId().equals(player.getUniqueId()) || hit.contains(target.getUniqueId())) continue;
                    if (!target.isValid() || target.isDead()) continue;
                    hit.add(target.getUniqueId());
                    damageInternal(target, damage, player);
                    Vector knock = dir.clone().multiply(0.44).add(new Vector(0, 0.16, 0));
                    target.setVelocity(knock);
                    addGauge(player, getConfig().getInt("tidal-crescent.gauge-per-hit", 5));
                    Location h = target.getLocation().clone().add(0, 1.0, 0);
                    spawn(world, "SPLASH", h, 32, 0.62, 0.55, 0.62, 0.16);
                    spawn(world, "BUBBLE_POP", h, 14, 0.44, 0.40, 0.44, 0.08);
                    playSound(world, h, "BLOCK_SOUL_SAND_BREAK", 0.7f, 1.35f);
                }
            }
        }.runTaskTimer(this, 0L, 1L);
    }

    // ---------------------------------------------------------------------
    // Skill III - Soul Undertow
    // ---------------------------------------------------------------------

    private void useSoulUndertow(Player caster, String inputSource) {
        if (!beginInput(caster, Skill.SOUL_UNDERTOW, 250L)) return;
        if (!isReady(caster, Skill.SOUL_UNDERTOW)) return;

        double radius = getConfig().getDouble("soul-undertow.radius", 12.0);
        if (isWaterAt(caster.getLocation(), 0.0) || isWaterAt(caster.getLocation(), -0.25)) {
            radius += Math.max(0, getConfig().getDouble("soul-undertow.water-radius-bonus", 3.0));
        }
        int maxTargets = Math.max(1, getConfig().getInt("soul-undertow.max-targets", 6));
        List<LivingEntity> targets = findTargets(caster, radius, maxTargets, true);
        if (targets.isEmpty()) {
            castNoTargetEffect(caster);
            actionBar(caster, "Skill III • tidak ada target • cooldown tidak dipakai");
            return;
        }

        startCooldown(caster, Skill.SOUL_UNDERTOW);
        Location origin = caster.getEyeLocation().clone();
        Vector flowDirection = caster.getLocation().getDirection().clone();
        flowDirection.setY(0.10);
        if (flowDirection.lengthSquared() < 0.0001) flowDirection = new Vector(1, 0.1, 0);
        flowDirection.normalize();

        castStartEffect(caster, targets.size());
        spawnFxPulse(caster.getWorld(), caster.getLocation().clone().add(0, 1.0, 0), "fx_undertow_ring", FX_UNDERTOW_MODEL_DATA,
                4.2f, 42, caster.getLocation().getYaw(), 0f);
        for (LivingEntity fxTarget : targets) {
            spawnFxPulse(fxTarget.getWorld(), fxTarget.getLocation().clone().add(0, 1.0, 0), "fx_undertow_ring", FX_UNDERTOW_MODEL_DATA,
                    2.2f, 36, caster.getLocation().getYaw(), 0f);
        }
        int index = 0;
        for (LivingEntity target : targets) {
            renderSoulStream(origin, target.getLocation().clone().add(0, 1.0, 0), index++);
            startUndertow(caster, target, flowDirection.clone(), index);
        }
        addGauge(caster, Math.min(18, targets.size() * getConfig().getInt("soul-undertow.gauge-per-target", 3)));
        actionBar(caster, "Skill III • Soul Undertow menangkap " + targets.size() + " target • cooldown " + cooldownSeconds(Skill.SOUL_UNDERTOW) + "s");
        getLogger().fine("Soul Undertow triggered by " + caster.getUniqueId() + " using " + inputSource);
    }

    private void startUndertow(Player caster, LivingEntity target, Vector flowDirection, int seed) {
        final int duration = Math.max(20, getConfig().getInt("soul-undertow.duration-ticks", 54));
        final double damage = Math.max(0.0, getConfig().getDouble("soul-undertow.damage", 8.0));
        final double drag = Math.max(0.02, getConfig().getDouble("soul-undertow.current-force", 0.18));
        final double lift = Math.max(0.02, getConfig().getDouble("soul-undertow.upward-force", 0.15));

        new BukkitRunnable() {
            int tick = 0;
            boolean damaged = false;

            @Override
            public void run() {
                tick++;
                if (!caster.isOnline() || !target.isValid() || target.isDead() || target.getWorld() != caster.getWorld()) {
                    cancel();
                    return;
                }
                if (tick > duration) {
                    finishUndertow(target, flowDirection);
                    cancel();
                    return;
                }

                World world = target.getWorld();
                Location base = target.getLocation().clone();
                Location center = base.clone().add(0, Math.min(1.15, 0.55 + target.getHeight() * 0.35), 0);
                double phase = tick * 0.55 + seed * 1.3;
                double ringRadius = 0.72 + 0.12 * Math.sin(tick * 0.25);

                for (int ring = 0; ring < 3; ring++) {
                    double a = phase + ring * (Math.PI * 2.0 / 3.0);
                    Location swirl = center.clone().add(Math.cos(a) * ringRadius, ((tick + ring * 5) % 18) / 10.0 - 0.6, Math.sin(a) * ringRadius);
                    spawn(world, "BUBBLE_COLUMN_UP", swirl, 2, 0.05, 0.08, 0.05, 0.02);
                    spawn(world, "SOUL", swirl, 1, 0.03, 0.03, 0.03, 0.0);
                    if ((tick + ring) % 2 == 0) spawn(world, "SPLASH", swirl, 2, 0.08, 0.07, 0.08, 0.03);
                }

                if (tick % 3 == 0) {
                    spawn(world, "CURRENT_DOWN", base.clone().add(0, 0.25, 0), 8, 0.45, 0.15, 0.45, 0.03);
                    spawn(world, "SOUL_FIRE_FLAME", center, 3, 0.32, 0.35, 0.32, 0.01);
                }

                Vector sideways = new Vector(-flowDirection.getZ(), 0, flowDirection.getX()).normalize();
                double wobble = Math.sin(phase) * 0.085;
                Vector radial = target.getLocation().toVector().subtract(caster.getLocation().toVector()); radial.setY(0);
                Vector vortex = radial.lengthSquared() > 0.001 ? new Vector(-radial.getZ(),0,radial.getX()).normalize() : sideways.clone();
                double swirlForce = clamp(getConfig().getDouble("soul-undertow.swirl-force",0.36),0.0,0.75);
                Vector desired = flowDirection.clone().multiply(drag*0.72).add(sideways.multiply(wobble))
                        .add(vortex.multiply(swirlForce)).add(new Vector(0,lift+0.08+Math.sin(tick*0.32)*0.055,0));
                Vector current = target.getVelocity().clone().multiply(0.42);
                target.setVelocity(current.add(desired));
                target.setFallDistance(0f);

                if (!damaged && tick >= Math.min(duration - 10, 24)) {
                    damaged = true;
                    if (damage > 0) damageInternal(target, damage, caster);
                    playSound(world, center, "ENTITY_PLAYER_SPLASH_HIGH_SPEED", 1.1f, 0.72f);
                    playSound(world, center, "BLOCK_SOUL_SAND_BREAK", 1.0f, 0.66f);
                    spawn(world, "SPLASH", center, 45, 0.85, 0.7, 0.85, 0.18);
                    spawn(world, "SOUL", center, 28, 0.65, 0.7, 0.65, 0.05);
                }
            }
        }.runTaskTimer(this, 0L, 1L);
    }

    private void finishUndertow(LivingEntity target, Vector direction) {
        World world = target.getWorld();
        Location loc = target.getLocation().clone().add(0, 0.8, 0);
        target.setFallDistance(0f);
        target.setVelocity(direction.clone().multiply(0.38).add(new Vector(0, 0.16, 0)));
        spawn(world, "SPLASH", loc, 65, 1.0, 0.8, 1.0, 0.22);
        spawn(world, "BUBBLE_POP", loc, 35, 0.8, 0.7, 0.8, 0.14);
        spawn(world, "SOUL", loc, 22, 0.75, 0.8, 0.75, 0.05);
        playSound(world, loc, "ITEM_TRIDENT_RIPTIDE_3", 0.9f, 1.25f);
    }

    // ---------------------------------------------------------------------
    // Ultimate - Domain of the Drowned Souls
    // ---------------------------------------------------------------------

    private void useDrownedDomain(Player caster) {
        if (!beginInput(caster, Skill.DROWNED_DOMAIN, 300L)) return;
        if (!isReady(caster, Skill.DROWNED_DOMAIN)) return;
        if (getGauge(caster) < maxGauge()) {
            actionBar(caster, "Ultimate belum siap • Soul Gauge " + getGauge(caster) + "/" + maxGauge());
            return;
        }

        soulGauge.put(caster.getUniqueId(), 0);
        startCooldown(caster, Skill.DROWNED_DOMAIN);
        final int duration = Math.max(60, getConfig().getInt("ultimate.duration-ticks", 120));
        final double radius = clamp(getConfig().getDouble("ultimate.radius", 9.0), 4.0, 16.0);
        final int maxTargets = Math.max(1, getConfig().getInt("ultimate.max-targets", 12));
        final double pulseDamage = Math.max(0.0, getConfig().getDouble("ultimate.pulse-damage", 2.0));
        final double collapseDamage = Math.max(0.0, getConfig().getDouble("ultimate.collapse-damage", 9.0));
        final Set<UUID> domainTargets = new HashSet<>();

        Location start = caster.getLocation().clone();
        spawn(caster.getWorld(), "SOUL", start.clone().add(0, 1.0, 0), 80, 2.0, 1.5, 2.0, 0.08);
        spawn(caster.getWorld(), "SPLASH", start.clone().add(0, 0.2, 0), 110, 2.4, 0.3, 2.4, 0.22);
        playSound(caster.getWorld(), start, "BLOCK_CONDUIT_ACTIVATE", 1.4f, 0.55f);
        playSound(caster.getWorld(), start, "ITEM_TRIDENT_THUNDER", 0.8f, 1.35f);
        actionBar(caster, "ULTIMATE • Domain of the Drowned Souls • Soul Gauge 0/" + maxGauge() + " • cooldown " + cooldownSeconds(Skill.DROWNED_DOMAIN) + "s");
        spawnFxPulse(caster.getWorld(), caster.getLocation().clone().add(0, 0.35, 0), "fx_domain_sigil", FX_DOMAIN_MODEL_DATA,
                7.5f, Math.max(70, getConfig().getInt("ultimate.duration-ticks", 120)), caster.getLocation().getYaw(), 90f);

        new BukkitRunnable() {
            int tick = 0;
            @Override
            public void run() {
                tick++;
                if (!caster.isOnline() || tick > duration) {
                    if (caster.isOnline()) collapse();
                    cancel();
                    return;
                }

                Location center = caster.getLocation().clone().add(0, 0.15, 0);
                World world = caster.getWorld();
                double phase = tick * 0.16;
                for (int ring = 0; ring < 3; ring++) {
                    double rr = radius * (0.45 + ring * 0.24);
                    int points = 14 + ring * 4;
                    for (int i = 0; i < points; i++) {
                        double a = (Math.PI * 2 * i / points) + phase * (ring % 2 == 0 ? 1 : -1);
                        Location p = center.clone().add(Math.cos(a) * rr, 0.12 + Math.sin(a * 2 + phase) * 0.18, Math.sin(a) * rr);
                        spawn(world, ring == 1 ? "SOUL" : "BUBBLE_COLUMN_UP", p, 1, 0.04, 0.06, 0.04, 0.015);
                        if ((i + tick + ring) % 4 == 0) spawn(world, "SPLASH", p, 2, 0.08, 0.06, 0.08, 0.03);
                    }
                }

                List<LivingEntity> targets = findTargets(caster, radius, maxTargets, false);
                for (LivingEntity target : targets) {
                    domainTargets.add(target.getUniqueId());
                    Vector toCenter = center.toVector().subtract(target.getLocation().toVector());
                    double dist = Math.max(0.35, toCenter.length());
                    if (toCenter.lengthSquared() > 0.0001) toCenter.normalize();
                    Vector tangent = new Vector(-toCenter.getZ(), 0, toCenter.getX());
                    if (tangent.lengthSquared() > 0.0001) tangent.normalize();
                    double pull = Math.min(0.28, 0.10 + dist * 0.018);
                    Vector velocity = toCenter.multiply(Math.min(0.42,pull+0.10)).add(tangent.multiply(0.34)).add(new Vector(0,0.16,0));
                    target.setVelocity(target.getVelocity().clone().multiply(0.34).add(velocity));
                    target.setFallDistance(0f);
                    Location tloc = target.getLocation().clone().add(0, 0.9, 0);
                    spawn(world, "BUBBLE", tloc, 5, 0.38, 0.48, 0.38, 0.035);
                    if (tick % 3 == 0) spawn(world, "SOUL_FIRE_FLAME", tloc, 2, 0.28, 0.38, 0.28, 0.01);
                    if (pulseDamage > 0 && tick % 20 == 0) damageInternal(target, pulseDamage, caster);
                }

                if (tick % 20 == 0) {
                    playSound(world, center, "BLOCK_BUBBLE_COLUMN_UPWARDS_INSIDE", 0.9f, 0.72f + (tick / 20) * 0.04f);
                }
            }

            private void collapse() {
                Location center = caster.getLocation().clone().add(0, 0.6, 0);
                World world = caster.getWorld();
                spawnRing(world, center, "SPLASH", radius, 48, 0.0);
                spawnRing(world, center, "SOUL", radius * 0.72, 36, 0.45);
                spawn(world, "BUBBLE_POP", center, 120, radius * 0.65, 1.5, radius * 0.65, 0.24);
                spawn(world, "SOUL_FIRE_FLAME", center, 80, radius * 0.45, 1.8, radius * 0.45, 0.06);
                playSound(world, center, "ITEM_TRIDENT_RIPTIDE_3", 1.4f, 0.45f);
                playSound(world, center, "BLOCK_RESPAWN_ANCHOR_DEPLETE", 1.0f, 1.45f);

                for (Entity e : world.getNearbyEntities(center, radius, radius, radius)) {
                    if (!(e instanceof LivingEntity target)) continue;
                    if (target.getUniqueId().equals(caster.getUniqueId())) continue;
                    if (!target.isValid() || target.isDead()) continue;
                    Vector inward = center.toVector().subtract(target.getLocation().toVector());
                    if (inward.lengthSquared() > 0.0001) inward.normalize();
                    target.setVelocity(inward.multiply(0.62).setY(0.28));
                    if (collapseDamage > 0) damageInternal(target, collapseDamage, caster);
                }
                actionBar(caster, "Tidal Collapse selesai • Ultimate cooldown " + formatRemaining(caster, Skill.DROWNED_DOMAIN));
            }
        }.runTaskTimer(this, 0L, 1L);
    }

    // ---------------------------------------------------------------------
    // Abyss Leviathan Trident V6
    // ---------------------------------------------------------------------

    private int getAbyssGauge(Player player) { return abyssGauge.getOrDefault(player.getUniqueId(), 0); }
    private int maxAbyssGauge() { return Math.max(1, getConfig().getInt("leviathan.ultimate.max-gauge", 100)); }
    private void addAbyssGauge(Player player, int amount) {
        if (amount <= 0) return;
        abyssGauge.put(player.getUniqueId(), Math.min(maxAbyssGauge(), getAbyssGauge(player) + amount));
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onLeviathanLaunch(ProjectileLaunchEvent event) {
        if (!(event.getEntity() instanceof Trident trident)) return;
        ProjectileSource shooter = trident.getShooter();
        if (!(shooter instanceof Player player)) return;
        if (!isLeviathan(trident.getItemStack())) return;
        event.setCancelled(true);
        actionBar(player, "Leviathan V6 memakai custom spear projectile • Right Click untuk melempar.");
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onLeviathanImpact(ProjectileHitEvent event) {
        if (!(event.getEntity() instanceof Trident trident)) return;
        Integer marker = trident.getPersistentDataContainer().get(thrownLeviathanKey, PersistentDataType.INTEGER);
        if (marker == null || marker != 1) return;
        UUID projectileId = trident.getUniqueId();
        Integer already = trident.getPersistentDataContainer().get(impactDoneKey, PersistentDataType.INTEGER);
        if ((already != null && already == 1) || !impactedProjectiles.add(projectileId)) return;
        trident.getPersistentDataContainer().set(impactDoneKey, PersistentDataType.INTEGER, 1);

        ProjectileSource shooter = trident.getShooter();
        Player player = shooter instanceof Player ? (Player) shooter : null;
        Location impact;
        Entity hitEntity = event.getHitEntity();
        if (hitEntity != null) impact = hitEntity.getLocation().clone().add(0, Math.min(1.0, hitEntity instanceof LivingEntity ? ((LivingEntity) hitEntity).getHeight() * 0.45 : 0.5), 0);
        else if (event.getHitBlock() != null) impact = event.getHitBlock().getLocation().clone().add(0.5, 0.7, 0.5);
        else impact = trident.getLocation().clone();

        World world = impact.getWorld();
        if (world == null) return;
        try { world.strikeLightningEffect(impact); } catch (Throwable ignored) {}
        playSound(world, impact, "ITEM_TRIDENT_THUNDER", 1.8f, 0.72f);
        playSound(world, impact, "BLOCK_RESPAWN_ANCHOR_DEPLETE", 1.15f, 0.62f);
        spawnFxPulse(world, impact.clone().add(0, 0.35, 0), "fx_leviathan_impact", FX_LEVIATHAN_IMPACT_MODEL_DATA,
                5.0f, 22, trident.getLocation().getYaw(), 90f);
        spawnFxPulse(world, impact.clone().add(0, 2.0, 0), "fx_lightning_spear", FX_LIGHTNING_SPEAR_MODEL_DATA,
                5.6f, 16, trident.getLocation().getYaw(), 0f);

        if (player != null) {
            double direct = Math.max(0.0, getConfig().getDouble("leviathan.thrown.impact-bonus-damage", 10.0));
            double aoe = Math.max(0.0, getConfig().getDouble("leviathan.thrown.lightning-aoe-damage", 8.0));
            double radius = clamp(getConfig().getDouble("leviathan.thrown.lightning-radius", 4.5), 1.0, 10.0);
            if (hitEntity instanceof LivingEntity target && !target.getUniqueId().equals(player.getUniqueId())) {
                damageInternal(target, direct, player);
                target.setVelocity(target.getVelocity().clone().add(new Vector(0, 0.38, 0)));
            }
            for (Entity e : world.getNearbyEntities(impact, radius, radius, radius)) {
                if (!(e instanceof LivingEntity living)) continue;
                if (living.getUniqueId().equals(player.getUniqueId())) continue;
                if (hitEntity != null && living.getUniqueId().equals(hitEntity.getUniqueId())) continue;
                if (!living.isValid() || living.isDead()) continue;
                damageInternal(living, aoe, player);
                Vector away = living.getLocation().toVector().subtract(impact.toVector());
                if (away.lengthSquared() > 0.001) away.normalize();
                living.setVelocity(away.multiply(0.58).setY(0.28));
            }
            addAbyssGauge(player, getConfig().getInt("leviathan.thrown.gauge-on-impact", 14));
            actionBar(player, "LEVIATHAN IMPACT • PETIR MENYAMBAR • Abyss Gauge " + getAbyssGauge(player) + "/" + maxAbyssGauge());
        }
        new BukkitRunnable() { @Override public void run() { impactedProjectiles.remove(projectileId); } }.runTaskLater(this, 240L);
    }

    private void useAbyssalHarpoon(Player player) {
        if (!beginInput(player, Skill.ABYSSAL_HARPOON, 120L)) return;
        if (!isReady(player, Skill.ABYSSAL_HARPOON)) return;
        startCooldown(player, Skill.ABYSSAL_HARPOON);
        final Location origin = player.getEyeLocation().clone().add(0,-0.10,0);
        final Vector direction = origin.getDirection().clone().normalize();
        final World world = player.getWorld();
        final int maxTicks = Math.max(12,getConfig().getInt("leviathan.thrown.max-flight-ticks",40));
        final double speed = clamp(getConfig().getDouble("leviathan.thrown.blocks-per-tick",1.28),0.65,2.2);
        final float scale = (float)clamp(getConfig().getDouble("leviathan.thrown.projectile-scale",1.15),0.55,2.2);
        final Location launch = origin.clone().add(direction.clone().multiply(1.25));

        Snowball carrier = world.spawn(launch, Snowball.class);
        carrier.setShooter(player);
        carrier.setGravity(false);
        carrier.setSilent(true);
        try { carrier.setItem(new ItemStack(Material.AIR)); } catch (Throwable ignored) {}
        carrier.getPersistentDataContainer().set(smoothLeviathanKey, PersistentDataType.BYTE, (byte)1);
        carrier.setVelocity(direction.clone().multiply(speed));

        final Object display = spawnProjectileDisplay(world, launch.clone(), direction, scale);
        if (display instanceof Entity displayEntity) {
            try { carrier.addPassenger(displayEntity); } catch (Throwable ignored) {}
        }

        addAbyssGauge(player,getConfig().getInt("leviathan.thrown.gauge-on-throw",6));
        playSound(world,player.getLocation(),"ITEM_TRIDENT_THROW",1.35f,0.52f);
        spawnFxPulse(world,launch,"fx_lightning_spear",FX_LIGHTNING_SPEAR_MODEL_DATA,2.8f,9,player.getLocation().getYaw(),0f);
        actionBar(player,"LEVIATHAN SPEAR • SMOOTH PROJECTILE • weapon tetap di tangan");

        new BukkitRunnable(){ int tick=0; @Override public void run(){
            if(!carrier.isValid() || carrier.isDead()){ cancel(); return; }
            tick++;
            Location pos=carrier.getLocation();
            Vector vel=carrier.getVelocity();
            if(vel.lengthSquared()>0.001) updateProjectileRotation(display,vel);
            spawn(world,"SPLASH",pos,4,.14,.11,.14,.04);
            spawn(world,"BUBBLE",pos,3,.11,.09,.11,.025);
            if(tick>=maxTicks){
                Vector dir=vel.lengthSquared()>0.001?vel.clone().normalize():direction;
                impactCustomLeviathan(player,pos.clone(),null,dir);
                removeCarrierAndDisplay(carrier,display);
                cancel();
            }
        }}.runTaskTimer(this,0L,1L);
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onSmoothLeviathanImpact(ProjectileHitEvent event) {
        if (!(event.getEntity() instanceof Snowball carrier)) return;
        Byte marker=carrier.getPersistentDataContainer().get(smoothLeviathanKey,PersistentDataType.BYTE);
        if(marker==null || marker!=1) return;
        ProjectileSource shooter=carrier.getShooter();
        if(!(shooter instanceof Player player)) { carrier.remove(); return; }
        Vector velocity=carrier.getVelocity();
        Vector dir=velocity.lengthSquared()>0.001?velocity.clone().normalize():player.getEyeLocation().getDirection().normalize();
        LivingEntity direct=event.getHitEntity() instanceof LivingEntity l?l:null;
        Location impact=direct!=null?direct.getLocation().clone().add(0,Math.min(1.1,direct.getHeight()*.45),0):carrier.getLocation().clone();
        List<Entity> passengers=new ArrayList<>(carrier.getPassengers());
        carrier.eject();
        for(Entity passenger:passengers) passenger.remove();
        carrier.remove();
        impactCustomLeviathan(player,impact,direct,dir);
    }

    private void removeCarrierAndDisplay(Snowball carrier,Object display){
        try{carrier.eject();}catch(Throwable ignored){}
        removeFxDisplay(display);
        try{carrier.remove();}catch(Throwable ignored){}
    }

    private void updateProjectileRotation(Object display,Vector velocity){
        if(display==null)return;
        try{display.getClass().getMethod("setRotation",float.class,float.class).invoke(display,directionYaw(velocity),directionPitch(velocity)+90f);}catch(Throwable ignored){}
    }

    private void impactCustomLeviathan(Player player, Location impact, LivingEntity directTarget, Vector direction){
        World world=impact.getWorld(); if(world==null)return;
        try{world.strikeLightningEffect(impact);}catch(Throwable ignored){}
        playSound(world,impact,"ITEM_TRIDENT_THUNDER",1.9f,.68f); playSound(world,impact,"BLOCK_RESPAWN_ANCHOR_DEPLETE",1.25f,.55f);
        spawnFxPulse(world,impact.clone().add(0,.35,0),"fx_leviathan_impact",FX_LEVIATHAN_IMPACT_MODEL_DATA,7.2f,25,player.getLocation().getYaw(),90f);
        spawnFxPulse(world,impact.clone().add(0,1.5,0),"fx_lightning_spear",FX_LIGHTNING_SPEAR_MODEL_DATA,6f,15,player.getLocation().getYaw(),0f);
        spawnWaterVolumeFx(world,impact.clone().add(0,.7,0),2f,10);
        spawn(world,"SPLASH",impact.clone().add(0,.6,0),120,1.8,1.1,1.8,.28);
        double direct=Math.max(0,getConfig().getDouble("leviathan.thrown.impact-bonus-damage",650.0));
        double aoe=Math.max(0,getConfig().getDouble("leviathan.thrown.lightning-aoe-damage",320.0));
        double radius=clamp(getConfig().getDouble("leviathan.thrown.lightning-radius",5.8),1,12);
        if(directTarget!=null && !directTarget.getUniqueId().equals(player.getUniqueId())){damageInternal(directTarget,direct,player); directTarget.setVelocity(direction.clone().multiply(.85).setY(.48)); spawnWaterImpactFx(directTarget,player,true);}
        for(Entity e:world.getNearbyEntities(impact,radius,radius,radius)){
            if(!(e instanceof LivingEntity living)||living.getUniqueId().equals(player.getUniqueId())||(directTarget!=null&&living.getUniqueId().equals(directTarget.getUniqueId()))||!living.isValid()||living.isDead())continue;
            damageInternal(living,aoe,player);
            Vector inward=impact.toVector().subtract(living.getLocation().toVector()); if(inward.lengthSquared()>.001)inward.normalize();
            Vector tangent=new Vector(-inward.getZ(),0,inward.getX()); if(tangent.lengthSquared()>.001)tangent.normalize();
            living.setVelocity(inward.multiply(.28).add(tangent.multiply(.58)).setY(.35)); spawnWaterImpactFx(living,player,true);
        }
        addAbyssGauge(player,getConfig().getInt("leviathan.thrown.gauge-on-impact",16));
    }

    private void useLeviathanFang(Player player) {
        if (!beginInput(player, Skill.LEVIATHAN_FANG, 250L)) return;
        if (!isReady(player, Skill.LEVIATHAN_FANG)) return;
        startCooldown(player, Skill.LEVIATHAN_FANG);
        final Vector look = player.getEyeLocation().getDirection().normalize();
        final Location origin = player.getLocation().clone().add(0,1.0,0);
        final double range = clamp(getConfig().getDouble("leviathan.leviathan-fang.range", 7.5), 3.0, 12.0);
        final double damage = Math.max(0.0, getConfig().getDouble("leviathan.leviathan-fang.damage", 8.0));
        World world = player.getWorld();
        for (int layer=1; layer<=7; layer++) {
            double dist = layer * (range/7.0);
            Location c = origin.clone().add(look.clone().multiply(dist));
            double rr = 0.35 + layer*0.22;
            spawnRing(world, c, layer%2==0 ? "SOUL" : "SOUL_FIRE_FLAME", rr, 10+layer, layer*0.35);
            spawn(world, "SPLASH", c, 8, rr*0.4,0.25,rr*0.4,0.08);
        }
        int hits=0;
        for (Entity e : world.getNearbyEntities(origin, range, range, range)) {
            if (!(e instanceof LivingEntity target) || e.getUniqueId().equals(player.getUniqueId()) || !target.isValid() || target.isDead()) continue;
            Vector to = target.getLocation().clone().add(0,0.8,0).toVector().subtract(origin.toVector());
            double dist = to.length(); if (dist > range || dist < 0.1) continue;
            Vector n = to.clone().normalize();
            if (n.dot(look) < 0.58) continue;
            damageInternal(target, damage, player); hits++;
            int marks = abyssMarks.getOrDefault(target.getUniqueId(), 0)+1;
            if (marks >= 3) {
                abyssMarks.remove(target.getUniqueId());
                double bonus = Math.max(0.0, getConfig().getDouble("leviathan.passive.three-mark-bonus-damage", 4.0));
                if (bonus>0) damageInternal(target, bonus, player);
                spawn(world, "BUBBLE_POP", target.getLocation().clone().add(0,1,0), 35,0.65,0.5,0.65,0.13);
                playSound(world, target.getLocation(), "ENTITY_ELDER_GUARDIAN_CURSE", 0.7f,0.7f);
            } else abyssMarks.put(target.getUniqueId(), marks);
            target.setVelocity(look.clone().multiply(0.55).setY(0.18));
        }
        addAbyssGauge(player, hits * getConfig().getInt("leviathan.leviathan-fang.gauge-per-hit", 8));
        playSound(world, origin, "ITEM_TRIDENT_RIPTIDE_2", 1.1f, 0.55f);
        actionBar(player, "Skill II • Leviathan Fang • " + hits + " target • cooldown " + cooldownSeconds(Skill.LEVIATHAN_FANG) + "s");
        spawnFxPulse(player.getWorld(), player.getEyeLocation().clone().add(player.getEyeLocation().getDirection().normalize().multiply(3.0)),
                "fx_leviathan_fang", FX_LEVIATHAN_FANG_MODEL_DATA, 4.2f, 18, player.getLocation().getYaw(), 0f);
    }

    private void useMaelstromPrison(Player player) {
        if (!beginInput(player, Skill.MAELSTROM_PRISON, 250L)) return;
        if (!isReady(player, Skill.MAELSTROM_PRISON)) return;
        startCooldown(player, Skill.MAELSTROM_PRISON);
        Vector forward = player.getEyeLocation().getDirection().clone(); forward.setY(0); if (forward.lengthSquared()<0.01) forward.setX(1); forward.normalize();
        final Location center = player.getLocation().clone().add(forward.multiply(getConfig().getDouble("leviathan.maelstrom-prison.distance", 6.0))).add(0,0.25,0);
        final double radius = clamp(getConfig().getDouble("leviathan.maelstrom-prison.radius", 6.5),3.0,12.0);
        final int duration = Math.max(30,getConfig().getInt("leviathan.maelstrom-prison.duration-ticks",70));
        final double pulseDamage = Math.max(0,getConfig().getDouble("leviathan.maelstrom-prison.pulse-damage",2.0));
        actionBar(player, "Skill III • Maelstrom Prison digunakan • cooldown " + cooldownSeconds(Skill.MAELSTROM_PRISON) + "s");
        spawnFxPulse(player.getWorld(), center.clone().add(0, 0.4, 0), "fx_maelstrom", FX_MAELSTROM_MODEL_DATA, 6.0f,
                Math.max(40, getConfig().getInt("leviathan.maelstrom-prison.duration-ticks", 70)), player.getLocation().getYaw(), 90f);
        playSound(player.getWorld(), center, "BLOCK_CONDUIT_ACTIVATE", 1.1f,0.5f);
        new BukkitRunnable(){ int tick=0; final Set<UUID> hit=new HashSet<>();
            @Override public void run(){
                if (!player.isOnline() || tick++>=duration) {
                    if (player.isOnline()) { spawn(center.getWorld(),"BUBBLE_POP",center.clone().add(0,1,0),100,radius*0.6,1.2,radius*0.6,0.2); playSound(center.getWorld(),center,"ITEM_TRIDENT_RIPTIDE_3",1.2f,0.45f); }
                    cancel(); return;
                }
                World world=center.getWorld(); double phase=tick*0.22;
                for(int ring=0;ring<3;ring++){ double rr=radius*(0.35+ring*0.28); spawnRing(world,center.clone().add(0,0.15+ring*0.18,0), ring==1?"SOUL":"BUBBLE_COLUMN_UP", rr, 16+ring*6, phase*(ring%2==0?1:-1)); }
                for(Entity e:world.getNearbyEntities(center,radius,radius,radius)){
                    if(!(e instanceof LivingEntity target)||e.getUniqueId().equals(player.getUniqueId())||!target.isValid()||target.isDead()) continue;
                    Vector inward=center.toVector().subtract(target.getLocation().toVector()); double dist=Math.max(.3,inward.length()); if(inward.lengthSquared()>0.001) inward.normalize();
                    Vector tangent=new Vector(-inward.getZ(),0,inward.getX()); if(tangent.lengthSquared()>0.001)tangent.normalize();
                    target.setVelocity(target.getVelocity().multiply(.35).add(inward.multiply(Math.min(.46,.18+dist*.032))).add(tangent.multiply(.46)).add(new Vector(0,.18,0)));
                    target.setFallDistance(0f); hit.add(target.getUniqueId());
                    if(pulseDamage>0 && tick%20==0) damageInternal(target,pulseDamage,player);
                }
                if(tick%20==0) playSound(world,center,"BLOCK_BUBBLE_COLUMN_UPWARDS_INSIDE",.9f,.6f);
            }
        }.runTaskTimer(this,0L,1L);
        addAbyssGauge(player, getConfig().getInt("leviathan.maelstrom-prison.gauge-on-cast", 8));
    }

    private void useWrathLeviathan(Player player) {
        if (!beginInput(player, Skill.WRATH_LEVIATHAN, 300L)) return;
        if (!isReady(player, Skill.WRATH_LEVIATHAN)) return;
        if (getAbyssGauge(player) < maxAbyssGauge()) { actionBar(player,"Ultimate belum siap • Abyss Gauge "+getAbyssGauge(player)+"/"+maxAbyssGauge()); return; }
        abyssGauge.put(player.getUniqueId(),0); startCooldown(player,Skill.WRATH_LEVIATHAN);
        final World world=player.getWorld(); final Location origin=player.getLocation().clone().add(0,1.0,0); final Vector dir=player.getEyeLocation().getDirection().clone().normalize();
        final double damage=Math.max(0,getConfig().getDouble("leviathan.ultimate.charge-damage",10.0));
        final double collapse=Math.max(0,getConfig().getDouble("leviathan.ultimate.collapse-damage",12.0));
        final double length=clamp(getConfig().getDouble("leviathan.ultimate.length",18.0),8.0,30.0);
        final double radius=clamp(getConfig().getDouble("leviathan.ultimate.radius",7.0),3.0,14.0);
        actionBar(player,"ULTIMATE • Wrath of the Leviathan • Abyss Gauge 0/"+maxAbyssGauge()+" • cooldown "+cooldownSeconds(Skill.WRATH_LEVIATHAN)+"s");
        spawnFxPulse(player.getWorld(), player.getEyeLocation().clone().add(player.getEyeLocation().getDirection().normalize().multiply(3.2)),
                "fx_lightning_spear", FX_LIGHTNING_SPEAR_MODEL_DATA, 6.0f, 34, player.getLocation().getYaw(), 0f);
        spawnFxPulse(player.getWorld(), player.getLocation().clone().add(0, 0.4, 0),
                "fx_leviathan_impact", FX_LEVIATHAN_IMPACT_MODEL_DATA, 7.0f, 42, player.getLocation().getYaw(), 90f);
        playSound(world,origin,"ITEM_TRIDENT_THUNDER",1.4f,.55f); spawn(world,"SOUL",origin,80,1.8,1.2,1.8,.07);
        new BukkitRunnable(){ int tick=0; final Set<UUID> hit=new HashSet<>();
            @Override public void run(){
                tick++; if(!player.isOnline()||tick>28){ collapse(); cancel(); return; }
                double t=Math.min(length,tick*(length/22.0)); Location head=origin.clone().add(dir.clone().multiply(t));
                spawn(world,"SOUL_FIRE_FLAME",head,20,.75,.75,.75,.04); spawn(world,"BUBBLE_POP",head,24,.9,.8,.9,.10);
                spawnRing(world,head,"SOUL",1.4,18,tick*.35);
                for(Entity e:world.getNearbyEntities(head,2.4,2.4,2.4)){ if(!(e instanceof LivingEntity target)||e.getUniqueId().equals(player.getUniqueId())||hit.contains(e.getUniqueId()))continue; hit.add(e.getUniqueId()); damageInternal(target,damage,player); target.setVelocity(dir.clone().multiply(.8).setY(.28)); }
            }
            private void collapse(){
                Location c=origin.clone().add(dir.clone().multiply(length)); spawnRing(world,c,"SOUL",radius,48,0); spawnRing(world,c,"SPLASH",radius*.72,36,.5); spawn(world,"BUBBLE_POP",c,150,radius*.6,1.6,radius*.6,.25); spawn(world,"SOUL_FIRE_FLAME",c,90,radius*.45,1.8,radius*.45,.06); playSound(world,c,"BLOCK_RESPAWN_ANCHOR_DEPLETE",1.3f,.65f);
                for(Entity e:world.getNearbyEntities(c,radius,radius,radius)){ if(!(e instanceof LivingEntity target)||e.getUniqueId().equals(player.getUniqueId()))continue; Vector away=target.getLocation().toVector().subtract(c.toVector()); if(away.lengthSquared()>0.001) away.normalize(); target.setVelocity(away.multiply(.72).setY(.42)); if(collapse>0) damageInternal(target,collapse,player); }
            }
        }.runTaskTimer(this,0L,1L);
    }

    private void showLeviathanStatus(Player player) {
        String status = "S1 " + formatRemaining(player, Skill.ABYSSAL_HARPOON)
                + " | S2 " + formatRemaining(player, Skill.LEVIATHAN_FANG)
                + " | S3 " + formatRemaining(player, Skill.MAELSTROM_PRISON)
                + " | ULT " + formatRemaining(player, Skill.WRATH_LEVIATHAN)
                + " • Abyss " + getAbyssGauge(player) + "/" + maxAbyssGauge();
        actionBar(player, status);
    }

    // ---------------------------------------------------------------------
    // Tidewalker passive
    // ---------------------------------------------------------------------

    @EventHandler(ignoreCancelled = true)
    public void onWaterWalk(PlayerMoveEvent event) {
        Player player=event.getPlayer();
        if(!isTidewalkerReady(player)){ restoreTidewalkerGravity(player); return; }
        if(tidewalkerJumpGraceActive(player)){ restoreTidewalkerGravity(player); return; }

        Location to=event.getTo(); if(to==null)return;
        Double surface=findWaterSurfaceY(to);
        if(surface==null){ restoreTidewalkerGravity(player); return; }

        double delta=surface-to.getY();

        // Coming up from below: gently lift to the surface once. No horizontal injection.
        if(delta>1.10){
            restoreTidewalkerGravity(player);
            Vector v=player.getVelocity().clone();
            v.setY(Math.min(.26,Math.max(.12,delta*.16)));
            player.setVelocity(v);
            player.setFallDistance(0f);
            setPlayerBooleanState(player,"setSwimming",false);
            renderWaterWalkFx(player,true);
            return;
        }

        // Player intentionally jumped above the surface: let vanilla gravity own the jump/fall.
        if(delta < -0.55){ restoreTidewalkerGravity(player); return; }

        Input input=player.getCurrentInput();
        if(input.isSneak()){ restoreTidewalkerGravity(player); return; }

        if(!tidewalkerNoGravity.contains(player.getUniqueId())){
            try{player.setGravity(false);tidewalkerNoGravity.add(player.getUniqueId());}catch(Throwable ignored){}
            // One snap only when entering Tidewalker. Repeated per-packet Y locking caused the old rubber-band.
            if(Math.abs(to.getY()-surface)>.06){
                Location snap=to.clone(); snap.setY(surface); event.setTo(snap);
            }
        }

        if(input.isJump()){
            beginTidewalkerJump(player,input);
            return;
        }

        Vector move=tidewalkerInputVelocity(player,input);
        move.setY(0.0);
        player.setVelocity(move);
        player.setFallDistance(0f);
        setPlayerBooleanState(player,"setSwimming",false);
        renderWaterWalkFx(player,false);
    }

    @EventHandler(ignoreCancelled = true)
    public void onTidewalkerInput(PlayerInputEvent event) {
        Player player=event.getPlayer();
        if(!tidewalkerNoGravity.contains(player.getUniqueId()))return;
        if(!isTidewalkerReady(player)){restoreTidewalkerGravity(player);return;}

        Input input=event.getInput();
        if(input.isSneak()){restoreTidewalkerGravity(player);return;}
        if(input.isJump()){
            beginTidewalkerJump(player,input);
            return;
        }

        Vector move=tidewalkerInputVelocity(player,input);
        move.setY(0.0);
        player.setVelocity(move);
    }

    private boolean tidewalkerJumpGraceActive(Player player){
        long now=System.currentTimeMillis();
        long until=tidewalkerJumpGrace.getOrDefault(player.getUniqueId(),0L);
        if(until<=now){tidewalkerJumpGrace.remove(player.getUniqueId());return false;}
        return true;
    }

    private void beginTidewalkerJump(Player player, Input input){
        long grace=Math.max(450L,getConfig().getLong("water-walk.jump-grace-ms",780L));
        double jumpY=Math.max(.34,Math.min(.62,getConfig().getDouble("water-walk.jump-velocity",.42)));
        double forwardMul=Math.max(.75,Math.min(1.45,getConfig().getDouble("water-walk.jump-forward-multiplier",1.08)));

        tidewalkerJumpGrace.put(player.getUniqueId(),System.currentTimeMillis()+grace);
        restoreTidewalkerGravity(player);

        Vector jump=tidewalkerInputVelocity(player,input).multiply(forwardMul);
        jump.setY(jumpY);
        player.setVelocity(jump);
        player.setFallDistance(0f);
        setPlayerBooleanState(player,"setSwimming",false);

        Location feet=player.getLocation().clone().add(0,.08,0);
        spawn(player.getWorld(),"SPLASH",feet,22,.55,.08,.55,.10);
        spawn(player.getWorld(),"BUBBLE_POP",feet,14,.48,.06,.48,.07);
        spawnRing(player.getWorld(),feet,"SOUL",.95,16,System.currentTimeMillis()*.0012);
        playSound(player.getWorld(),feet,"ENTITY_PLAYER_SPLASH_HIGH_SPEED",.52f,1.35f);
    }

    private boolean isTidewalkerReady(Player player){
        return getConfig().getBoolean("water-walk.enabled",true)
                && isSoulTide(player.getInventory().getItemInMainHand())
                && canUseWeapon(player)
                && !player.isSneaking()
                && !booleanPlayerState(player,"isFlying")
                && !booleanPlayerState(player,"isGliding");
    }

    private Vector tidewalkerInputVelocity(Player player, Input input){
        Vector forward=player.getLocation().getDirection().clone(); forward.setY(0);
        if(forward.lengthSquared()<0.0001)forward=new Vector(0,0,1); else forward.normalize();
        Vector right=new Vector(-forward.getZ(),0,forward.getX());

        double fb=(input.isForward()?1.0:0.0)-(input.isBackward()?1.0:0.0);
        double lr=(input.isRight()?1.0:0.0)-(input.isLeft()?1.0:0.0);
        Vector move=forward.multiply(fb).add(right.multiply(lr));

        if(move.lengthSquared()<0.0001)return new Vector(0,0,0);
        move.normalize();

        double walkScale=Math.max(.35,Math.min(2.5,player.getWalkSpeed()/0.2f));
        double speed=(input.isSprint()?.285:.215)*walkScale;
        if(input.isBackward()&&!input.isForward())speed*=.82;
        return move.multiply(speed);
    }

    private Double findWaterSurfaceY(Location loc){
        World w=loc.getWorld(); if(w==null)return null;
        int x=loc.getBlockX(),z=loc.getBlockZ(); int from=loc.getBlockY()-2,to=Math.min(w.getMaxHeight()-2,loc.getBlockY()+18);
        Double found=null;
        for(int y=from;y<=to;y++){
            Material here=w.getBlockAt(x,y,z).getType(),above=w.getBlockAt(x,y+1,z).getType();
            if(here==Material.WATER && above!=Material.WATER){found=y+1.015;break;}
        }
        return found;
    }

    private void restoreTidewalkerGravity(Player player){
        if(player==null)return;
        if(tidewalkerNoGravity.remove(player.getUniqueId())){try{player.setGravity(true);}catch(Throwable ignored){}}
    }

    @EventHandler public void onTidewalkerSlotChange(PlayerItemHeldEvent event){
        Player p=event.getPlayer(); new BukkitRunnable(){@Override public void run(){if(!isSoulTide(p.getInventory().getItemInMainHand()))restoreTidewalkerGravity(p);}}.runTaskLater(this,1L);
    }
    @EventHandler public void onTidewalkerQuit(PlayerQuitEvent event){Player p=event.getPlayer();restoreTidewalkerGravity(p);tidewalkerJumpGrace.remove(p.getUniqueId());}

    private void renderWaterWalkFx(Player player, boolean rising) {
        if (!getConfig().getBoolean("water-walk.effects", true)) return;
        long now = System.currentTimeMillis();
        long interval = Math.max(50L, getConfig().getLong("water-walk.effect-interval-ms", 120L));
        long next = waterWalkFx.getOrDefault(player.getUniqueId(), 0L);
        if (now < next) return;
        waterWalkFx.put(player.getUniqueId(), now + interval);

        Location feet = player.getLocation().clone().add(0, 0.08, 0);
        World world = player.getWorld();
        spawn(world, "BUBBLE_COLUMN_UP", feet, rising ? 12 : 7, 0.38, 0.08, 0.38, 0.035);
        spawn(world, "BUBBLE_POP", feet, 7, 0.42, 0.05, 0.42, 0.04);
        spawn(world, "SPLASH", feet, rising ? 12 : 8, 0.48, 0.06, 0.48, 0.07);
        spawnRing(world, feet, "SOUL", 0.72, 12, now * 0.0008);

        long soundInterval = Math.max(200L, getConfig().getLong("water-walk.sound-interval-ms", 650L));
        if ((now / soundInterval) != ((now - interval) / soundInterval)) {
            playSound(world, feet, "BLOCK_BUBBLE_COLUMN_UPWARDS_INSIDE", 0.32f, rising ? 1.20f : 1.48f);
        }
    }

    @EventHandler(ignoreCancelled = true)
    public void onLeviathanWaterMove(PlayerMoveEvent event) {
        Player player = event.getPlayer();
        if (!isLeviathan(player.getInventory().getItemInMainHand())) return;
        if (!canUseWeapon(player)) return;
        boolean inWater = booleanPlayerState(player, "isInWater") || isWaterAt(player.getLocation(), 0.0);
        if (!inWater) return;
        try {
            player.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.WATER_BREATHING, 45, 0, true, false, false));
            player.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.DOLPHINS_GRACE, 30, 0, true, false, false));
        } catch (Throwable ignored) {}
        if (event.getTo() != null && event.getFrom().distanceSquared(event.getTo()) > 0.0002) {
            Location p = player.getLocation().clone().add(0,0.8,0);
            spawn(player.getWorld(), "BUBBLE", p, 5, .35,.45,.35,.03);
            if (System.currentTimeMillis() % 4 == 0) spawn(player.getWorld(), "SOUL", p, 2,.25,.35,.25,.01);
        }
    }

    private void spawnWaterImpactFx(LivingEntity target, Player source, boolean leviathan){
        if(target==null||!target.isValid())return; World world=target.getWorld();
        Location hit=target.getLocation().clone().add(0,Math.min(1.0,target.getHeight()*.45),0);
        spawn(world,"SPLASH",hit,leviathan?56:42,.75,.60,.75,.18); spawn(world,"BUBBLE_POP",hit,leviathan?34:24,.62,.55,.62,.12);
        spawnFxPulse(world,hit,leviathan?"fx_leviathan_impact":"fx_soul_slash",leviathan?FX_LEVIATHAN_IMPACT_MODEL_DATA:FX_SOUL_SLASH_MODEL_DATA,leviathan?2.4f:2.0f,7,source==null?0f:source.getLocation().getYaw(),0f);
        spawnWaterVolumeFx(world,hit,leviathan?1.05f:.85f,5);
    }
    private void spawnWaterVolumeFx(World world, Location location, float scale, int lifetime){
        if(world==null||location==null)return;
        try{
            Class<?> c=Class.forName("org.bukkit.entity.BlockDisplay"); Object d=world.getClass().getMethod("spawn",Location.class,Class.class).invoke(world,location,c);
            Class<?> bd=Class.forName("org.bukkit.block.data.BlockData"); d.getClass().getMethod("setBlock",bd).invoke(d,Material.WATER.createBlockData());
            Object tr=d.getClass().getMethod("getTransformation").invoke(d); Object sv=tr.getClass().getMethod("getScale").invoke(tr);
            sv.getClass().getMethod("set",float.class,float.class,float.class).invoke(sv,scale,scale,scale);
            d.getClass().getMethod("setTransformation",Class.forName("org.bukkit.util.Transformation")).invoke(d,tr);
            new BukkitRunnable(){int t=0;@Override public void run(){if(++t>=Math.max(2,lifetime)){try{d.getClass().getMethod("remove").invoke(d);}catch(Throwable ignored){}cancel();}}}.runTaskTimer(this,1L,1L);
        }catch(Throwable ignored){}
    }
    private Object spawnProjectileDisplay(World world, Location loc, Vector dir, float scale){
        Object d=spawnFxDisplay(world,loc,"fx_leviathan_projectile",FX_LEVIATHAN_PROJECTILE_MODEL_DATA,scale,directionYaw(dir),directionPitch(dir)+90f);
        if(d!=null){try{Class<?> b=Class.forName("org.bukkit.entity.Display$Billboard"); @SuppressWarnings({"unchecked","rawtypes"}) Object fixed=Enum.valueOf((Class<Enum>)b,"FIXED"); d.getClass().getMethod("setBillboard",b).invoke(d,fixed);}catch(Throwable ignored){} updateProjectileDisplay(d,loc,dir,scale);}
        return d;
    }
    private void updateProjectileDisplay(Object d, Location l, Vector v, float s){updateFxDisplay(d,l,s,directionYaw(v),directionPitch(v)+90f);}
    private float directionYaw(Vector v){Vector n=v.clone().normalize();return(float)Math.toDegrees(Math.atan2(-n.getX(),n.getZ()));}
    private float directionPitch(Vector v){Vector n=v.clone().normalize();return(float)Math.toDegrees(-Math.asin(Math.max(-1,Math.min(1,n.getY()))));}

    // ---------------------------------------------------------------------
    // V6 custom-model FX (ItemDisplay + transient WATER BlockDisplay).

    // Reflection keeps the plugin tolerant across Paper 1.21.x / newer display APIs.
    // ---------------------------------------------------------------------

    private ItemStack createFxItem(String modelPath, int modelData) {
        ItemStack item = new ItemStack(Material.PAPER);
        ItemMeta meta = item.getItemMeta();
        if (meta == null) return item;
        try { meta.setCustomModelData(modelData); } catch (Throwable ignored) {}
        try {
            Method setItemModel = meta.getClass().getMethod("setItemModel", NamespacedKey.class);
            setItemModel.invoke(meta, new NamespacedKey("legendaryrais", modelPath));
        } catch (Throwable ignored) {}
        try {
            Method getter = meta.getClass().getMethod("getCustomModelDataComponent");
            Object component = getter.invoke(meta);
            component.getClass().getMethod("setFloats", List.class).invoke(component, Collections.singletonList((float) modelData));
            try { component.getClass().getMethod("setStrings", List.class).invoke(component, Collections.singletonList("legendaryrais:" + modelPath)); } catch (Throwable ignored) {}
            for (Method m : meta.getClass().getMethods()) {
                if (m.getName().equals("setCustomModelDataComponent") && m.getParameterCount() == 1) { m.invoke(meta, component); break; }
            }
        } catch (Throwable ignored) {}
        item.setItemMeta(meta);
        return item;
    }

    private Object spawnFxDisplay(World world, Location location, String modelPath, int modelData, float scale, float yaw, float pitch) {
        if (world == null || location == null) return null;
        try {
            Class<?> displayClass = Class.forName("org.bukkit.entity.ItemDisplay");
            Method spawnMethod = world.getClass().getMethod("spawn", Location.class, Class.class);
            Object display = spawnMethod.invoke(world, location, displayClass);
            display.getClass().getMethod("setItemStack", ItemStack.class).invoke(display, createFxItem(modelPath, modelData));
            try {
                Class<?> transformEnum = Class.forName("org.bukkit.entity.ItemDisplay$ItemDisplayTransform");
                @SuppressWarnings({"unchecked","rawtypes"}) Object fixed = Enum.valueOf((Class<Enum>) transformEnum, "FIXED");
                display.getClass().getMethod("setItemDisplayTransform", transformEnum).invoke(display, fixed);
            } catch (Throwable ignored) {}
            try {
                Class<?> billboardEnum = Class.forName("org.bukkit.entity.Display$Billboard");
                @SuppressWarnings({"unchecked","rawtypes"}) Object center = Enum.valueOf((Class<Enum>) billboardEnum, "CENTER");
                display.getClass().getMethod("setBillboard", billboardEnum).invoke(display, center);
            } catch (Throwable ignored) {}
            try {
                Class<?> brightnessClass = Class.forName("org.bukkit.entity.Display$Brightness");
                Object brightness = brightnessClass.getConstructor(int.class, int.class).newInstance(15, 15);
                display.getClass().getMethod("setBrightness", brightnessClass).invoke(display, brightness);
            } catch (Throwable ignored) {}
            try { display.getClass().getMethod("setViewRange", float.class).invoke(display, 64.0f); } catch (Throwable ignored) {}
            try { display.getClass().getMethod("setInterpolationDuration", int.class).invoke(display, 4); } catch (Throwable ignored) {}
            try { display.getClass().getMethod("setTeleportDuration", int.class).invoke(display, 2); } catch (Throwable ignored) {}
            updateFxDisplay(display, location, scale, yaw, pitch);
            return display;
        } catch (Throwable ignored) {
            return null;
        }
    }

    private void updateFxDisplay(Object display, Location location, float scale, float yaw, float pitch) {
        if (display == null) return;
        try { display.getClass().getMethod("teleport", Location.class).invoke(display, location); } catch (Throwable ignored) {}
        try { display.getClass().getMethod("setRotation", float.class, float.class).invoke(display, yaw, pitch); } catch (Throwable ignored) {}
        try {
            Object transformation = display.getClass().getMethod("getTransformation").invoke(display);
            Object scaleVector = transformation.getClass().getMethod("getScale").invoke(transformation);
            scaleVector.getClass().getMethod("set", float.class, float.class, float.class).invoke(scaleVector, scale, scale, scale);
            Class<?> transformationClass = Class.forName("org.bukkit.util.Transformation");
            display.getClass().getMethod("setTransformation", transformationClass).invoke(display, transformation);
        } catch (Throwable ignored) {}
    }

    private void removeFxDisplay(Object display) {
        if (display == null) return;
        try { display.getClass().getMethod("remove").invoke(display); } catch (Throwable ignored) {}
    }

    private void spawnFxPulse(World world, Location location, String modelPath, int modelData, float maxScale,
                              int lifetimeTicks, float yaw, float pitch) {
        final Object display = spawnFxDisplay(world, location, modelPath, modelData, Math.max(0.35f, maxScale * 0.38f), yaw, pitch);
        if (display == null) return;
        new BukkitRunnable() {
            int tick = 0;
            @Override public void run() {
                tick++;
                if (tick >= lifetimeTicks) { removeFxDisplay(display); cancel(); return; }
                float progress = tick / (float) Math.max(1, lifetimeTicks);
                float pulse = (float) Math.sin(Math.min(1.0, progress * 1.35) * Math.PI);
                float scale = Math.max(0.32f, maxScale * (0.52f + 0.58f * pulse));
                updateFxDisplay(display, location, scale, yaw + tick * 7.0f, pitch);
            }
        }.runTaskTimer(this, 1L, 1L);
    }

    // ---------------------------------------------------------------------
    // Cooldown/action bar status
    // ---------------------------------------------------------------------

    private boolean beginInput(Player player, Skill skill, long debounceMs) {
        long now = System.currentTimeMillis();
        long until = inputDebounce.getOrDefault(player.getUniqueId(), 0L);
        if (now < until) return false;
        inputDebounce.put(player.getUniqueId(), now + debounceMs);
        return true;
    }

    private boolean isReady(Player player, Skill skill) {
        long remaining = remainingMillis(player, skill);
        if (remaining <= 0) return true;
        actionBar(player, skill.slot + " • " + skill.display + " • bisa digunakan lagi dalam " + secondsText(remaining) + " detik");
        return false;
    }

    private void startCooldown(Player player, Skill skill) {
        long readyAt = System.currentTimeMillis() + cooldownSeconds(skill) * 1000L;
        cooldowns.computeIfAbsent(player.getUniqueId(), id -> new EnumMap<>(Skill.class)).put(skill, readyAt);
    }

    private long remainingMillis(Player player, Skill skill) {
        EnumMap<Skill, Long> map = cooldowns.get(player.getUniqueId());
        if (map == null) return 0L;
        return Math.max(0L, map.getOrDefault(skill, 0L) - System.currentTimeMillis());
    }

    private int cooldownSeconds(Skill skill) {
        return Math.max(1, getConfig().getInt(skill.configKey, 30));
    }

    private String formatRemaining(Player player, Skill skill) {
        long ms = remainingMillis(player, skill);
        return ms <= 0 ? "READY" : secondsText(ms) + "s";
    }

    private String secondsText(long millis) {
        return String.format(Locale.US, "%.1f", Math.max(0L, millis) / 1000.0);
    }

    private void showFullStatus(Player player) {
        String status = "S1 " + formatRemaining(player, Skill.ABYSSAL_STEP)
                + " | S2 " + formatRemaining(player, Skill.TIDAL_CRESCENT)
                + " | S3 " + formatRemaining(player, Skill.SOUL_UNDERTOW)
                + " | ULT " + formatRemaining(player, Skill.DROWNED_DOMAIN)
                + " • Soul " + getGauge(player) + "/" + maxGauge();
        actionBar(player, status);
    }

    private void actionBar(Player player, String text) {
        if (!getConfig().getBoolean("actionbar.enabled", true)) return;
        try {
            player.sendActionBar(Component.text(text));
        } catch (Throwable ignored) {
            player.sendMessage("§b[LegendaryRais] §7" + text);
        }
    }

    // ---------------------------------------------------------------------
    // Shared target/effect helpers
    // ---------------------------------------------------------------------

    private List<LivingEntity> findTargets(Player caster, double radius, int maxTargets, boolean lineOfSight) {
        boolean targetPlayers = getConfig().getBoolean("targeting.players", true);
        boolean targetMobs = getConfig().getBoolean("targeting.mobs", true);
        List<LivingEntity> found = new ArrayList<>();
        for (Entity entity : caster.getWorld().getNearbyEntities(caster.getLocation(), radius, radius, radius)) {
            if (!(entity instanceof LivingEntity living)) continue;
            if (entity.getUniqueId().equals(caster.getUniqueId())) continue;
            if (!living.isValid() || living.isDead()) continue;
            if (living instanceof Player && !targetPlayers) continue;
            if (!(living instanceof Player) && !targetMobs) continue;
            if (lineOfSight && !caster.hasLineOfSight(entity)) continue;
            found.add(living);
        }
        found.sort(Comparator.comparingDouble(e -> e.getLocation().distanceSquared(caster.getLocation())));
        if (found.size() > maxTargets) return new ArrayList<>(found.subList(0, maxTargets));
        return found;
    }

    private void castNoTargetEffect(Player caster) {
        World world = caster.getWorld();
        Location loc = caster.getLocation().clone().add(0, 1.0, 0);
        spawn(world, "SOUL", loc, 18, 0.7, 0.7, 0.7, 0.02);
        spawn(world, "SPLASH", loc, 28, 0.9, 0.4, 0.9, 0.12);
        playSound(world, loc, "BLOCK_SOUL_SAND_BREAK", 0.8f, 0.8f);
    }

    private void castStartEffect(Player caster, int targets) {
        World world = caster.getWorld();
        Location feet = caster.getLocation().clone().add(0, 0.15, 0);
        spawn(world, "BUBBLE_COLUMN_UP", feet, 45, 1.0, 0.2, 1.0, 0.08);
        spawn(world, "SOUL", feet.clone().add(0, 1.0, 0), 30, 1.0, 1.0, 1.0, 0.04);
        spawn(world, "SPLASH", feet.clone().add(0, 0.6, 0), 50, 1.3, 0.6, 1.3, 0.16);
        playSound(world, feet, "ITEM_TRIDENT_RIPTIDE_3", 1.2f, 0.72f);
        playSound(world, feet, "BLOCK_BUBBLE_COLUMN_UPWARDS_INSIDE", 1.1f, 0.88f);
        playSound(world, feet, "BLOCK_CONDUIT_ACTIVATE", 0.9f, 1.45f);
    }

    private void renderSoulStream(Location from, Location to, int offsetSeed) {
        World world = from.getWorld();
        if (world == null || to.getWorld() != world) return;
        Vector delta = to.toVector().subtract(from.toVector());
        double distance = Math.max(0.01, delta.length());
        Vector sideDir = delta.clone().normalize();
        Vector side = new Vector(-sideDir.getZ(), 0, sideDir.getX());
        if (side.lengthSquared() < 0.001) side = new Vector(1, 0, 0);
        side.normalize();
        Vector up = new Vector(0, 1, 0);
        int steps = Math.min(48, Math.max(12, (int) (distance * 4.0)));
        for (int i = 0; i <= steps; i++) {
            double t = i / (double) steps;
            Location p = from.clone().add(delta.clone().multiply(t));
            double angle = t * Math.PI * 8.0 + offsetSeed * 0.75;
            double r = 0.18 + 0.12 * Math.sin(t * Math.PI);
            Vector helix = side.clone().multiply(Math.cos(angle) * r).add(up.clone().multiply(Math.sin(angle) * r));
            p.add(helix);
            spawn(world, "BUBBLE", p, 1, 0.03, 0.03, 0.03, 0.01);
            if (i % 2 == 0) spawn(world, "SOUL", p, 1, 0.02, 0.02, 0.02, 0.0);
            if (i % 3 == 0) spawn(world, "SPLASH", p, 2, 0.07, 0.07, 0.07, 0.02);
        }
    }

    private void spawnRing(World world, Location center, String particleName, double radius, int points, double phase) {
        if (world == null || points <= 0) return;
        for (int i = 0; i < points; i++) {
            double a = (Math.PI * 2.0 * i / points) + phase;
            Location p = center.clone().add(Math.cos(a) * radius, 0, Math.sin(a) * radius);
            spawn(world, particleName, p, 1, 0.025, 0.025, 0.025, 0.0);
        }
    }

    private void damageInternal(LivingEntity target, double amount, Player source) {
        if (amount <= 0 || target == null || !target.isValid() || target.isDead()) return;
        UUID id = target.getUniqueId();
        internalDamageTargets.add(id);
        try {
            target.damage(amount, source);
        } finally {
            internalDamageTargets.remove(id);
        }
    }

    private void spawn(World world, String particleName, Location location, int count,
                       double ox, double oy, double oz, double extra) {
        if (!getConfig().getBoolean("legacy-particles.enabled", false)) return;
        Particle particle = particle(particleName);
        if (particle == null || world == null) return;
        try {
            world.spawnParticle(particle, location, count, ox, oy, oz, extra);
        } catch (Throwable ignored) {
        }
    }

    private Particle particle(String name) {
        try {
            return Particle.valueOf(name);
        } catch (Throwable ignored) {
            if (name.equals("SPLASH")) {
                try { return Particle.valueOf("WATER_SPLASH"); } catch (Throwable ignored2) {}
            }
            return null;
        }
    }

    private void playSound(World world, Location location, String soundName, float volume, float pitch) {
        try {
            Sound sound = Sound.valueOf(soundName);
            world.playSound(location, sound, volume, pitch);
        } catch (Throwable ignored) {
        }
    }

    private boolean booleanPlayerState(Player player, String methodName) {
        try {
            Object result = player.getClass().getMethod(methodName).invoke(player);
            return result instanceof Boolean && (Boolean) result;
        } catch (Throwable ignored) {
            return false;
        }
    }

    private void setPlayerBooleanState(Player player, String methodName, boolean value) {
        try {
            player.getClass().getMethod(methodName, boolean.class).invoke(player, value);
        } catch (Throwable ignored) {
        }
    }

    private boolean isWaterAt(Location base, double yOffset) {
        try {
            Location sample = base.clone().add(0, yOffset, 0);
            Object block = sample.getClass().getMethod("getBlock").invoke(sample);
            if (block == null) return false;
            Object material = block.getClass().getMethod("getType").invoke(block);
            if (material == null) return false;
            String name = material.toString();
            if (isWaterMaterialName(name)) return true;
            try {
                Object blockData = block.getClass().getMethod("getBlockData").invoke(block);
                if (blockData != null) {
                    Class<?> waterlogged = Class.forName("org.bukkit.block.data.Waterlogged");
                    if (waterlogged.isInstance(blockData)) {
                        Object result = waterlogged.getMethod("isWaterlogged").invoke(blockData);
                        if (result instanceof Boolean && (Boolean) result) return true;
                    }
                }
            } catch (Throwable ignored) {
            }
        } catch (Throwable ignored) {
        }
        return false;
    }

    private boolean isWaterMaterialName(String name) {
        return "WATER".equals(name)
                || "BUBBLE_COLUMN".equals(name)
                || "KELP".equals(name)
                || "KELP_PLANT".equals(name)
                || "SEAGRASS".equals(name)
                || "TALL_SEAGRASS".equals(name);
    }

    private double clamp(double value, double min, double max) {
        return Math.max(min, Math.min(max, value));
    }

    private boolean isBedrock(Player player) {
        UUID uuid = player.getUniqueId();
        try {
            Class<?> geyser = Class.forName("org.geysermc.geyser.api.GeyserApi");
            Object api = geyser.getMethod("api").invoke(null);
            if (api != null) {
                try {
                    Object result = api.getClass().getMethod("isBedrockPlayer", UUID.class).invoke(api, uuid);
                    if (result instanceof Boolean b) return b;
                } catch (NoSuchMethodException ignored) {
                    Object connection = api.getClass().getMethod("connectionByUuid", UUID.class).invoke(api, uuid);
                    if (connection != null) return true;
                }
            }
        } catch (Throwable ignored) {
        }
        try {
            Class<?> floodgate = Class.forName("org.geysermc.floodgate.api.FloodgateApi");
            Object api = floodgate.getMethod("getInstance").invoke(null);
            Object result = api.getClass().getMethod("isFloodgatePlayer", UUID.class).invoke(api, uuid);
            return result instanceof Boolean && (Boolean) result;
        } catch (Throwable ignored) {
        }
        return false;
    }
}

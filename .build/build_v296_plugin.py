from pathlib import Path
import base64, zipfile, shutil, re

root = Path(".build/v296-src")
zip_path = Path(".build/v296-source.zip")
if root.exists(): shutil.rmtree(root)
parts = [Path(f".build/v294-source-part-{i:02d}.b64").read_text().strip() for i in range(4)]
zip_path.write_bytes(base64.b64decode("".join(parts)))
with zipfile.ZipFile(zip_path) as z:
    if z.testzip(): raise RuntimeError("source zip corrupt")
    z.extractall(root)

p = root/"src/main/java/id/raisnet/legendaryrais/LegendaryRais.java"
s = p.read_text(encoding="utf-8")
def must(old,new):
    global s
    if old not in s: raise RuntimeError("missing pattern: "+old[:80])
    s=s.replace(old,new)

must("private static final int FX_LIGHTNING_SPEAR_MODEL_DATA = 910108;",
     "private static final int FX_LIGHTNING_SPEAR_MODEL_DATA = 910108;\n    private static final int FX_LEVIATHAN_PROJECTILE_MODEL_DATA = 910109;")
must("LegendaryRais v2.9.0 REWORK enabled. Soul Tide Sovereign Blade + Abyss Leviathan Trident registered.",
     "LegendaryRais v2.9.6 ABSOLUTE WATER REWORK enabled. HD Sovereign Blade + HD Abyss Leviathan registered.")
s=s.replace("§8[V5]","§8[V6]").replace("§b[V5]","§b[V6]").replace("Abyss Leviathan Trident V5","Abyss Leviathan Trident V6").replace("§3Abyss Leviathan V5:","§3Abyss Leviathan V6:")
s=s.replace("§7Semua active skill cooldown: §f30 detik§7 (default).","§7Cooldown V6: Sword 30s • Spear 1/8/12/20s.")

must("        saveDefaultConfig();", "        saveDefaultConfig();\n        applyV296ConfigMigration();")

migration = r'''    private void applyV296ConfigMigration() {
        int version = getConfig().getInt("config-version", 0);
        if (version >= 296) return;
        getConfig().set("config-version", 296);
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
        getConfig().set("leviathan.thrown.blocks-per-tick", 1.55);
        getConfig().set("leviathan.thrown.hit-radius", 1.15);
        getConfig().set("leviathan.thrown.projectile-scale", 1.15);
        getConfig().set("leviathan.leviathan-fang.damage", 650.0);
        getConfig().set("leviathan.maelstrom-prison.pulse-damage", 165.0);
        getConfig().set("leviathan.ultimate.charge-damage", 650.0);
        getConfig().set("leviathan.ultimate.collapse-damage", 1000.0);
        saveConfig();
        getLogger().info("Migrated existing LegendaryRais config to v2.9.6 ABSOLUTE WATER defaults.");
    }

'''
anchor = "    @Override\n    public void onDisable() {"
if anchor not in s: raise RuntimeError("onDisable anchor missing")
s=s.replace(anchor, migration + anchor)

must("""            else if (!player.isSneaking() && right) {
                // V5: allow vanilla trident charging/throwing. ProjectileLaunchEvent owns Skill I.
                handled = false;
                actionBar(player, isReady(player, Skill.ABYSSAL_HARPOON)
                        ? "Skill I • Abyssal Harpoon READY • lepas lemparan untuk memanggil petir"
                        : "Skill I • Abyssal Harpoon • cooldown " + formatRemaining(player, Skill.ABYSSAL_HARPOON));
            }""",
"""            else if (!player.isSneaking() && right) {
                // V6 custom projectile: no vanilla Trident entity and the weapon never leaves inventory.
                handled = true;
                useAbyssalHarpoon(player);
            }""")

must("""        if (soul) {
            event.setDamage(Math.max(event.getDamage(), getConfig().getDouble("base-hit.sword", 14.0)));
        } else if (leviathan) {
            event.setDamage(Math.max(event.getDamage(), getConfig().getDouble("base-hit.trident", 16.0)));
        }
""",
"""        if (soul) {
            event.setDamage(Math.max(event.getDamage(), getConfig().getDouble("base-hit.sword", 38.0)));
        } else if (leviathan) {
            event.setDamage(Math.max(event.getDamage(), getConfig().getDouble("base-hit.trident", 44.0)));
        }
        spawnWaterImpactFx(target, player, leviathan);
""")

a=s.index("    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)\n    public void onLeviathanLaunch")
b=s.index("    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)\n    public void onLeviathanImpact",a)
s=s[:a]+"""    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onLeviathanLaunch(ProjectileLaunchEvent event) {
        if (!(event.getEntity() instanceof Trident trident)) return;
        ProjectileSource shooter = trident.getShooter();
        if (!(shooter instanceof Player player)) return;
        if (!isLeviathan(trident.getItemStack())) return;
        event.setCancelled(true);
        actionBar(player, "Leviathan V6 memakai custom spear projectile • Right Click untuk melempar.");
    }

"""+s[b:]

a=s.index("    private void useAbyssalHarpoon(Player player) {")
b=s.index("    private void useLeviathanFang(Player player) {",a)
s=s[:a]+r'''    private void useAbyssalHarpoon(Player player) {
        if (!beginInput(player, Skill.ABYSSAL_HARPOON, 120L)) return;
        if (!isReady(player, Skill.ABYSSAL_HARPOON)) return;
        startCooldown(player, Skill.ABYSSAL_HARPOON);
        final Location origin = player.getEyeLocation().clone().add(0,-0.10,0);
        final Vector direction = origin.getDirection().clone().normalize();
        final World world = player.getWorld();
        final int maxTicks = Math.max(12,getConfig().getInt("leviathan.thrown.max-flight-ticks",34));
        final double speed = clamp(getConfig().getDouble("leviathan.thrown.blocks-per-tick",1.55),0.65,2.8);
        final double hitRadius = clamp(getConfig().getDouble("leviathan.thrown.hit-radius",1.15),0.55,2.4);
        final float scale = (float)clamp(getConfig().getDouble("leviathan.thrown.projectile-scale",1.15),0.55,2.2);
        final Location pos = origin.clone().add(direction.clone().multiply(1.3));
        final Object display = spawnProjectileDisplay(world,pos,direction,scale);
        addAbyssGauge(player,getConfig().getInt("leviathan.thrown.gauge-on-throw",6));
        playSound(world,player.getLocation(),"ITEM_TRIDENT_THROW",1.35f,0.52f);
        spawnFxPulse(world,pos,"fx_lightning_spear",FX_LIGHTNING_SPEAR_MODEL_DATA,2.8f,9,player.getLocation().getYaw(),0f);
        actionBar(player,"LEVIATHAN SPEAR • custom projectile • weapon tetap di tangan");
        new BukkitRunnable(){int tick=0; @Override public void run(){
            if(!player.isOnline() || tick++>=maxTicks){ impactCustomLeviathan(player,pos,null,direction); removeFxDisplay(display); cancel(); return; }
            for(int sub=0;sub<2;sub++){
                pos.add(direction.clone().multiply(speed*.5));
                updateProjectileDisplay(display,pos,direction,scale);
                spawn(world,"SPLASH",pos,7,.20,.16,.20,.08); spawn(world,"BUBBLE",pos,5,.16,.13,.16,.05);
                for(Entity e:world.getNearbyEntities(pos,hitRadius,hitRadius,hitRadius)){
                    if(!(e instanceof LivingEntity target) || target.getUniqueId().equals(player.getUniqueId()) || !target.isValid() || target.isDead()) continue;
                    impactCustomLeviathan(player,target.getLocation().clone().add(0,Math.min(1.1,target.getHeight()*.45),0),target,direction);
                    removeFxDisplay(display); cancel(); return;
                }
                try{ if(pos.getBlock().getType().isSolid()){ impactCustomLeviathan(player,pos.clone(),null,direction); removeFxDisplay(display); cancel(); return; } }catch(Throwable ignored){}
            }
        }}.runTaskTimer(this,0L,1L);
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

'''+s[b:]

must("""                Vector desired = flowDirection.clone().multiply(drag)
                        .add(sideways.multiply(wobble))
                        .add(new Vector(0, lift + Math.sin(tick * 0.32) * 0.035, 0));""",
"""                Vector radial = target.getLocation().toVector().subtract(caster.getLocation().toVector()); radial.setY(0);
                Vector vortex = radial.lengthSquared() > 0.001 ? new Vector(-radial.getZ(),0,radial.getX()).normalize() : sideways.clone();
                double swirlForce = clamp(getConfig().getDouble("soul-undertow.swirl-force",0.36),0.0,0.75);
                Vector desired = flowDirection.clone().multiply(drag*0.72).add(sideways.multiply(wobble))
                        .add(vortex.multiply(swirlForce)).add(new Vector(0,lift+0.08+Math.sin(tick*0.32)*0.055,0));""")
s=s.replace("toCenter.multiply(pull).add(tangent.multiply(0.11)).add(new Vector(0, 0.095, 0))",
            "toCenter.multiply(Math.min(0.42,pull+0.10)).add(tangent.multiply(0.34)).add(new Vector(0,0.16,0))")
s=s.replace("inward.multiply(Math.min(.32,.12+dist*.025))).add(tangent.multiply(.18)).add(new Vector(0,.10,0))",
            "inward.multiply(Math.min(.46,.18+dist*.032))).add(tangent.multiply(.46)).add(new Vector(0,.18,0))")

m=re.search(r'        // Use the player\'s actual movement delta as direction, then compensate water drag\.[\s\S]*?        player\.setVelocity\(velocity\);',s)
if not m: raise RuntimeError("waterwalk block missing")
water='''        // V6: never manufacture X/Z movement; WASD fully controls horizontal direction.
        Location to = event.getTo();
        if (to != null) {
            Vector delta = to.toVector().subtract(event.getFrom().toVector()); delta.setY(0);
            if (delta.lengthSquared() < 0.000002) { velocity.setX(0.0); velocity.setZ(0.0); }
        }
        player.setVelocity(velocity);'''
s=s[:m.start()]+water+s[m.end():]

marker="    // ---------------------------------------------------------------------\n    // V5 custom-model FX (ItemDisplay). These are resource-pack models, not particle spam."
helpers=r'''    private void spawnWaterImpactFx(LivingEntity target, Player source, boolean leviathan){
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
'''
if marker not in s: raise RuntimeError("FX marker missing")
s=s.replace(marker,helpers)
p.write_text(s,encoding="utf-8")

cfg=root/"src/main/resources/config.yml"
c=cfg.read_text()
if not c.startswith("config-version: 296"):
    c="config-version: 296\n"+c
repls={
"# LegendaryRais v2.9.0 REWORK — Sword + Leviathan visual/damage rework":"# LegendaryRais v2.9.6 ABSOLUTE WATER REWORK — Paper 26.1.2 build 74",
"  sword: 14.0":"  sword: 38.0","  trident: 16.0":"  trident: 44.0",
"  damage: 12.0":"  damage: 650.0","  damage: 14.0":"  damage: 650.0","  damage: 16.0":"  damage: 650.0",
"  soul-break-bonus-damage: 6.0":"  soul-break-bonus-damage: 42.0",
"  pulse-damage: 4.0":"  pulse-damage: 165.0","  collapse-damage: 20.0":"  collapse-damage: 900.0",
"    abyssal-harpoon: 30":"    abyssal-harpoon: 1","    leviathan-fang: 30":"    leviathan-fang: 8",
"    maelstrom-prison: 30":"    maelstrom-prison: 12","    wrath-of-the-leviathan: 30":"    wrath-of-the-leviathan: 20",
"    projectile-damage: 18.0":"    projectile-damage: 650.0","    impact-bonus-damage: 10.0":"    impact-bonus-damage: 650.0",
"    lightning-aoe-damage: 8.0":"    lightning-aoe-damage: 320.0","    lightning-radius: 4.5":"    lightning-radius: 5.8",
"    damage: 18.0":"    damage: 650.0","    pulse-damage: 4.0":"    pulse-damage: 165.0",
"    charge-damage: 22.0":"    charge-damage: 650.0","    collapse-damage: 28.0":"    collapse-damage: 1000.0"}
for a,b in repls.items(): c=c.replace(a,b)
c=c.replace("  upward-force: 0.17\n","  upward-force: 0.17\n  swirl-force: 0.36\n")
c=c.replace("    gauge-on-impact: 14\n","    gauge-on-impact: 16\n    max-flight-ticks: 34\n    blocks-per-tick: 1.55\n    hit-radius: 1.15\n    projectile-scale: 1.15\n")
cfg.write_text(c)

pom=root/"pom.xml"; x=pom.read_text().replace("<version>2.9.0</version>","<version>2.9.6</version>",1).replace("<maven.compiler.release>21</maven.compiler.release>","<maven.compiler.release>25</maven.compiler.release>").replace("<version>1.21.1-R0.1-SNAPSHOT</version>","<version>26.1.2.build.74-stable</version>"); pom.write_text(x)
py=root/"src/main/resources/plugin.yml"; y=py.read_text().replace("version: 2.9.0","version: 2.9.6").replace("api-version: '1.21'","api-version: '26.1.2'").replace("Sovereign Blade + Leviathan Impact Rework.","ABSOLUTE WATER REWORK • HD weapons + custom spear projectile."); py.write_text(y)
print("V296_SOURCE_READY")

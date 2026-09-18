from pathlib import Path
import zipfile, json, hashlib, shutil

base = Path("LegendaryRais-Java-26plus-v2.1.zip")
work = Path(".build/work-v2112")
out = Path("LegendaryRais-Java-26plus-v2.1.2-FIX.zip")
sha_out = Path("LegendaryRais-Java-26plus-v2.1.2-FIX.sha1")
if work.exists():
    shutil.rmtree(work)
work.mkdir(parents=True)

with zipfile.ZipFile(base, "r") as z:
    z.extractall(work)

# Modern 26.1/26.2 item definitions.
mc_items = work / "assets/minecraft/items"
mc_items.mkdir(parents=True, exist_ok=True)

(mc_items / "netherite_sword.json").write_text(json.dumps({
  "hand_animation_on_swap": True,
  "model": {
    "type": "minecraft:range_dispatch",
    "property": "minecraft:custom_model_data",
    "index": 0,
    "entries": [
      {"threshold": 910041.0, "model": {"type":"minecraft:model","model":"soultide:item/soul_tide_katana"}},
      {"threshold": 910042.0, "model": {"type":"minecraft:model","model":"minecraft:item/netherite_sword"}}
    ],
    "fallback":{"type":"minecraft:model","model":"minecraft:item/netherite_sword"}
  }
}, indent=2), encoding="utf-8")

(mc_items / "trident.json").write_text(json.dumps({
  "hand_animation_on_swap": True,
  "model": {
    "type": "minecraft:range_dispatch",
    "property": "minecraft:custom_model_data",
    "index": 0,
    "entries": [
      {"threshold": 910042.0, "model": {"type":"minecraft:model","model":"legendaryrais:item/abyss_leviathan_trident"}},
      {"threshold": 910043.0, "model": {"type":"minecraft:model","model":"minecraft:item/trident"}}
    ],
    "fallback":{"type":"minecraft:model","model":"minecraft:item/trident"}
  }
}, indent=2), encoding="utf-8")

# Legacy 1.21/1.21.1 CMD overrides too, so ViaVersion users aren't stuck on vanilla.
legacy_models = work / "assets/minecraft/models/item"
legacy_models.mkdir(parents=True, exist_ok=True)
(legacy_models / "netherite_sword.json").write_text(json.dumps({
  "parent":"minecraft:item/handheld",
  "textures":{"layer0":"minecraft:item/netherite_sword"},
  "overrides":[{"predicate":{"custom_model_data":910041},"model":"soultide:item/soul_tide_katana"}]
}, indent=2), encoding="utf-8")
(legacy_models / "trident.json").write_text(json.dumps({
  "parent":"minecraft:item/generated",
  "textures":{"layer0":"minecraft:item/trident"},
  "overrides":[{"predicate":{"custom_model_data":910042},"model":"legendaryrais:item/abyss_leviathan_trident"}]
}, indent=2), encoding="utf-8")

# Multi-version metadata: 1.21/1.21.1 (34) through 26.2 (88).
(work / "pack.mcmeta").write_text(json.dumps({
  "pack":{
    "pack_format":34,
    "supported_formats":{"min_inclusive":34,"max_inclusive":88},
    "min_format":[34,0],
    "max_format":[88,0],
    "description":"LegendaryRais v2.1.2 FIX • Soul Tide V4 + Abyss Leviathan V3 • Java 1.21.1–26.2"
  }
}, indent=2), encoding="utf-8")

if out.exists():
    out.unlink()
files = sorted(p for p in work.rglob("*") if p.is_file())
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in files:
        z.write(p, p.relative_to(work).as_posix())

digest = hashlib.sha1(out.read_bytes()).hexdigest()
sha_out.write_text(digest + "\n", encoding="utf-8")
print("BUILT", out, out.stat().st_size, digest)

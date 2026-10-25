Drop part Model kits here named by catalog id (e.g. rusty_cage.model.json).
Assembler.buildModel clones ReplicatedStorage.AssemblerAssets.Parts/<partId>.

Regen multi-Part kits:
  python tools/generate_part_models.py
  python tools/emit_catalog_bay.py
  python tools/verify_part_coverage.py

Each kit is a Model with Root + multiple Parts (panels/barrels/joints/feet).
Accent* Parts get rarity tint at assemble time. Never ship single-cube parts.

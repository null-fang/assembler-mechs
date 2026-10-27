Drop part Model kits here named by catalog id (e.g. rusty_cage.model.json).
Assembler.buildModel clones ReplicatedStorage.AssemblerAssets.Parts/<partId>.

Regen multi-Part kits:
  python tools/generate_part_models.py
  python tools/emit_catalog_bay.py
  python tools/verify_part_coverage.py

Contract (Shared/Assembler/KitContract.luau + Sockets.luau):
- Model with Root at socket origin (PrimaryPart). Never ship single-cube parts.
- Accent* / Glow* = rarity neon language (color kits).
- Textured kits: SurfaceAppearance/Texture/Decal OR Attribute AssemblerTextured=true
  on hull Parts — Assembler will not recolor those (keeps Studio/cloud textures).
- Pivot uses Sockets.defs offsets; do not bake world pad transforms into kits.

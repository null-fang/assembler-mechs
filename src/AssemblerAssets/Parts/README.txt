Drop part Model kits here named by catalog id (e.g. rusty_cage.model.json).
Assembler.buildModel clones ReplicatedStorage.AssemblerAssets.Parts/<partId>.

Regen multi-Part kits:
  python tools/generate_textures.py
  python tools/generate_part_models.py
  python tools/emit_catalog_bay.py
  python tools/verify_part_coverage.py
  python tools/smoke_textured_kits.py

Contract (Shared/Assembler/KitContract.luau + Sockets.luau + TextureIds):
- Model with Root at socket origin (PrimaryPart). Never ship single-cube parts.
- Parts carry Attributes.TextureRole (tools/texture_ids.json); TextureApply stamps textures.
- Accent* / Glow* = rarity neon language when not textured.
- Textured kits: SurfaceAppearance/Texture/Decal OR Attribute AssemblerTextured=true
  on hull Parts — Assembler will not recolor those (keeps Studio/cloud textures).
- Templates: AssemblerAssets/Textures; runtime: Shared.Assembler.TextureIds / TextureApply.
- Pivot uses Sockets.defs offsets; do not bake world pad transforms into kits.
- Never leave Color3-only as the end state once the texture pack is wired.

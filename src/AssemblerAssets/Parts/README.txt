Drop part Model kits here named by catalog id (e.g. rusty_cage.model.json).
Assembler.buildModel clones ReplicatedStorage.AssemblerAssets.Parts/<partId>.

Art direction: SuperMechs-inspired 3D (chibi proportions, readable weapons, combat pose).
Bold paint + gunmetal joints + Glow/Visor emissives — not hazard-tape cubes.

Regen:
  python3 tools/generate_textures.py
  python3 tools/generate_part_models.py
  python3 tools/emit_catalog_bay.py
  python3 tools/verify_part_coverage.py
  python3 tools/smoke_textured_kits.py
  python3 tools/render_mech_preview.py

Contract: Shared/Assembler/KitContract.luau + Sockets.luau + TextureIds.
- Root at socket origin. Multi-Part silhouettes only.
- Attributes.TextureRole → TextureApply (embed bake when rbxassetid empty).
- Accent*/Glow* rarity neon; hull textures not team-washed.

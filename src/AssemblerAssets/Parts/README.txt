Drop part Model kits here named by catalog id (e.g. rusty_cage.model.json).
Assembler.buildModel clones ReplicatedStorage.AssemblerAssets.Parts/<partId>.

Art direction: SuperMechs-inspired 3D (chibi proportions, readable weapons, combat pose).
Bold paint + gunmetal joints + Glow/Visor emissives — not hazard-tape cubes / T-pose blobs.

Showcase / art bar:
  ../Showcase/HeroStarterMech.model.json — hand-authored combat-ready hero (quality bar).

Regen:
  python tools/generate_textures.py
  python tools/generate_part_models.py
  python tools/author_hero_mech.py
  python tools/emit_catalog_bay.py
  python tools/verify_part_coverage.py
  python tools/smoke_textured_kits.py
  python tools/render_mech_preview.py

Contract: Shared/Assembler/KitContract.luau + Sockets.luau + TextureIds.
- Root at socket origin. Multi-Part silhouettes only.
- Attributes.TextureRole → TextureApply (embed bake when rbxassetid empty).
- Accent*/Glow* rarity neon; hull textures not team-washed.
- Combat crouch sockets (no T-pose). Starter kits overwritten by author_hero_mech.py after generate.

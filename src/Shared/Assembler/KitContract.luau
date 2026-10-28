-- Stable contract for AssemblerAssets.Parts/<catalogPartId> kits.
-- SuperMechs-inspired 3D: chibi proportions, readable weapons, combat pose — not T-pose boxes.

local KitContract = {}

-- Required:
--   Model named by catalog PartId (Rojo file stem)
--   Child BasePart "Root" at local origin (socket attach). Assembler sets PrimaryPart + Transparency=1.
--   Multi-Part silhouette (never a lone cube). Assembler PivotTo's the Model at Sockets.defs[socket].
--   Silhouette language: bold paint hull + gunmetal joints + Glow*/Visor emissives.
--   Guns read as guns (barrels/tubes), pods as tube grids, blades as blades, legs as legs.
--
-- Pose (Shared.Assembler.Sockets):
--   Combat crouch — knees forward, arms/weapons ready, shoulder pods aim forward. Not a T-pose.
--   TORSO_HEIGHT ≈ 3.85 studs above pad.
--
-- Quality bar:
--   AssemblerAssets/Showcase/HeroStarterMech + starter kits from tools/author_hero_mech.py.
--
-- Rarity language:
--   Accent* / Glow* Parts — Assembler neon-tints Color3 by rarity (Texture maps left alone).
--
-- Texture pack (tools/texture_ids.json + Shared.Assembler.TextureIds / TextureApply):
--   Keys: metal_plate, scratched_steel, hazard_stripe, matte_rubber, carbon_dark, emissive_strip
--   Parts stamp Attribute TextureRole=<key>; TextureApply bakes TexturePixels when rbxassetid empty.
--   Hull Color3 stays paint; do not team-tint textured body parts.

KitContract.ROOT_NAME = "Root"
KitContract.TEXTURED_ATTR = "AssemblerTextured"
KitContract.ACCENT_PREFIX = "Accent"
KitContract.GLOW_PREFIX = "Glow"
-- Themed mech lines (Shared.Themes.ThemeIds / MechLine):
--   Optional Attribute ThemeLine on kits; Assembler copies onto assembled mech Model.
KitContract.THEME_LINE_ATTR = "ThemeLine"

return KitContract


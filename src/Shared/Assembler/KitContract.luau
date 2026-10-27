-- Stable contract for AssemblerAssets.Parts/<catalogPartId> kits.
-- Textured kit pipeline + Studio texture pack must honor this; Integrator keeps it green.

local KitContract = {}

-- Required:
--   Model named by catalog PartId (Rojo file stem)
--   Child BasePart "Root" at local origin (socket attach). Assembler sets PrimaryPart + Transparency=1.
--   Multi-Part silhouette (never a lone cube). Assembler PivotTo's the Model at Sockets.defs[socket].
--
-- Optional rarity language (color kits):
--   Accent* / Glow* Parts — Assembler may neon-tint by rarity.
--
-- Optional textured language (quality kits):
--   SurfaceAppearance / Texture / Decal under hull Parts, OR Attribute AssemblerTextured=true
--   Assembler will NOT mutate Color/Material on those Parts (team tint skipped).
--   Accent*/Glow* may still neon if they are NOT marked textured.
-- Texture pack contract (tools/texture_ids.json + Shared.Assembler.TextureIds):
--   Keys: metal_plate, scratched_steel, hazard_stripe, matte_rubber, carbon_dark, emissive_strip
--   Parts may carry Attribute TextureRole=<key>; TextureApply stamps from AssemblerAssets.Textures
--   or embeds (TexturePixels) until rbxassetid is filled after Studio upload.
--
-- Sockets (Shared.Assembler.Sockets): Torso, LeftHip, RightHip, LowerLeft, LowerRight,
-- ShoulderLeft, ShoulderRight, Battery, CPU, Drone. Local +Y up; feet toward -Y from torso.
-- TORSO_HEIGHT = 4.5 studs above pad surface.

KitContract.ROOT_NAME = "Root"
KitContract.TEXTURED_ATTR = "AssemblerTextured"
KitContract.ACCENT_PREFIX = "Accent"
KitContract.GLOW_PREFIX = "Glow"

return KitContract

Assembler showcase mechs — dense SM-inspired 3D art bars (original shapes).

HeroStarterMech — olive scrap hero quality bar (combat crouch).
ThemeScrapMech  — Yardbone scrapyard rust/olive refine.
ThemeArcticMech — Rimevault white/ice-blue frost line.
ThemeDesertMech — Duneplate sand/ochre heat line.
ThemeNeonMech   — Voltframe cyan/magenta night line.

Combat-ready pose (bent knees, planted feet, weapons forward).
Front = +Z (visor faces camera). Regen:

  python3 tools/generate_part_models.py
  python3 tools/author_hero_mech.py
  python3 tools/author_theme_mechs.py
  python3 tools/emit_catalog_bay.py
  python3 tools/verify_part_coverage.py

Synced via Rojo to ReplicatedStorage.AssemblerAssets.Showcase.

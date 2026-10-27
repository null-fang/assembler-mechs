# Assembler

Build a mech from modular parts. Fight turn-based 1v1 in 3D arenas — PvE campaign first (~10 NPC ladder), PvP infra from day one.

**Design plan** lives in the Cursor Project Context (`docs/assembler-design-plan.md`).

| | |
| --- | --- |
| GitHub | [`null-fang/assembler-mechs`](https://github.com/null-fang/assembler-mechs) |
| Branch | `cursor/combat-slice-774e` |
| Roblox Place owner (later) | **Eman99Mason** |

## Playtest (Bob)

1. `git fetch origin && git checkout cursor/combat-slice-774e && git pull origin cursor/combat-slice-774e`
2. `aftman install` then `rojo serve` (or `rojo build -o Assembler.rbxlx` and open the place)
3. Studio → Rojo Connect → **Play Solo**
4. You spawn in the **mech bay lobby** (floor, hangar). Primary mech is on the **Garage pedestal**.
5. Walk to the cyan **Campaign** terminal → **Open** → start fight **1**.
6. Teleport to Scrap Pit / Dry Dock / Night Yard; mechs on **PadA/PadB**; turn HUD + side camera.
7. Win/lose → return to lobby with common + XP. Optional: Garage pedestal (or HUD Garage) to swap parts.

## Combat rules

- **2 AP / turn** — move and/or fire, then End turn.
- Integrity / Temperature (overheat skips) / Battery (energy guns dark while recharging).
- Damage: Physical / Heat / Energy. Soft overweight Integrity penalty.

## Layout

```
src/Workspace/     Lobby + Arenas (Rojo maps)
src/AssemblerAssets/Parts   205 multi-Part kits (clone-by-PartId)
src/AssemblerAssets/Showcase HeroStarterMech combat-ready art bar (SM-like 3D)
src/AssemblerAssets/Textures Industrial pack templates (TextureIds contract)
assets/textures/            Source PNGs (metal/steel/hazard/rubber/carbon/emissive)
src/Shared/        Combat, Assembler, Parts, Modes, Economy, World/Tags, Session/Phase
src/Server/World/  ArenaService, LobbyPrompts, WorldBootstrap (CollectionService tags)
src/Server/Parts/  InventoryService
src/Client/        CombatHud, GarageHud, JoinHud, KitPreload, SessionBridge
```

Integrator hooks for parallel workers: `Shared/World/Tags`, player attrs `AssemblerPhase` / `AssemblerArena`, `Client/SessionBridge.onChanged`, `Shared/Util/Maid`.

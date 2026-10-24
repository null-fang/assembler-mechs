# Assembler

Build a mech from modular parts. Fight turn-based 1v1 in 3D arenas — PvE campaign first (~10 NPC ladder), PvP infra from day one. Open crates, pick one of three cards, climb rarities. SuperMechs-shaped combat (Integrity, Temperature, Battery; Physical / Heat / Energy) with Roblox presentation and a Ball vs Ball–style pick-3 loop.

**Design plan** lives in the Cursor Project Context (`docs/assembler-design-plan.md`) — not duplicated here.

| | |
| --- | --- |
| GitHub | [`null-fang/assembler-mechs`](https://github.com/null-fang/assembler-mechs) |
| Roblox Place owner (later) | **Eman99Mason** |

## Combat quick rules (stub)

- **AP (action points):** ~**2 AP per turn** (SuperMechs-like). Spend AP to move and/or attack.
- **Resources:** Integrity (HP), Temperature, Battery Life.
- **Damage triad:** Physical / mechanical, Heat, Energy.
- **Weight:** Every part has weight; chassis has capacity (soft overweight penalty preferred; see code comments).

## Open with Rojo + Studio

1. Install [Aftman](https://github.com/LPGhatguy/aftman), then from this repo:
   ```bash
   aftman install
   ```
2. Start Rojo:
   ```bash
   rojo serve
   ```
3. In Roblox Studio (account **Eman99Mason** when publishing), install the [Rojo plugin](https://rojo.space/docs/v7/getting-started/installation/), open a blank place (or sync into your experience), and **Connect** to the serve address (default `localhost:34872`).
4. Optional: `rojo build -o Assembler.rbxlx` for a one-shot place file.

Wally is present but unused until packages are needed (`wally install` when you add deps).

## Layout

```
src/
  Shared/   — types + pure logic (combat, parts, economy, modes)
  Server/   — campaign ladder, matchmaking stub, economy, combat host
  Client/   — thin entry; UI later
```

Scaffold only — no full combat sim, models, or polished UI yet.

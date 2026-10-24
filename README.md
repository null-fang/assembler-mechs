# Assembler

Build a mech from modular parts. Fight turn-based 1v1 in 3D arenas — PvE campaign first (~10 NPC ladder), PvP infra from day one. Open crates, pick one of three cards, climb rarities. SuperMechs-shaped combat (Integrity, Temperature, Battery; Physical / Heat / Energy) with Roblox presentation and a Ball vs Ball–style pick-3 loop.

**Design plan** lives in the Cursor Project Context (`docs/assembler-design-plan.md`) — not duplicated here.

| | |
| --- | --- |
| GitHub | [`null-fang/assembler-mechs`](https://github.com/null-fang/assembler-mechs) |
| Roblox Place owner (later) | **Eman99Mason** |

## Combat quick rules

- **AP:** **2 actions per turn.** Spend AP to move and/or fire; End Turn hands it off.
- **Core Integrity:** 0 = scrap.
- **Core Temperature:** overheat → skip your next turn. (Freeze = Phase 2.)
- **Battery Life:** 0 → energy weapons dark for a few moves while recharging. (Over-Voltage = Phase 2.)
- **Damage:** Physical / Heat / Energy.
- **Weight:** soft Integrity penalty when over chassis capacity.

## Play the first slice (Studio + Rojo)

1. `aftman install` then `rojo serve` (or `rojo build -o Assembler.rbxlx`).
2. Connect the Rojo plugin in Studio (account **Eman99Mason** when publishing).
3. Play Solo — left HUD lists the campaign ladder. Start fight 1, spend AP, End Turn, climb.

## Layout

```
src/
  Shared/
    Combat/   — Types, MechState, Resolver, NpcBrain
    Parts/    — Slots, Catalog, StarterMech, CratePick3
    Modes/    — BattleMode, BattleOpponent
    Economy/  — Currency, Rewards, SellDuplicate
  Server/
    Combat/   — CombatHost (PvE + PvP entry)
    Campaign/ — Ladder (~10 NPCs), CampaignService
    PvP/      — Matchmaking stub
    Remotes   — fight remotes
  Client/
    CombatHud — rough campaign + turn UI
```

PvP matchmaking stays a stub; both modes share `Resolver` / `CombatHost`.

#!/usr/bin/env python3
"""Offline smoke for Bob path: lobby → crate → garage → campaign → arena → return."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"  ok  {msg}")


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def need(rel: str, needles: list[str]) -> None:
    text = read(rel)
    for n in needles:
        if n not in text:
            fail(f"{rel} missing {n}")


def find_named(node: dict, want: str) -> list[dict]:
    hits: list[dict] = []
    if node.get("Name") == want:
        hits.append(node)
    for child in node.get("Children", []):
        hits.extend(find_named(child, want))
    return hits


def main() -> None:
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "smoke_integration.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr)
        fail("smoke_integration")

    # 1) Lobby world hooks
    lobby = json.loads(read("src/Workspace/Lobby.model.json"))
    for name in ("GaragePedestal", "CampaignTerminal", "SpawnLocation"):
        if not find_named(lobby, name):
            fail(f"lobby missing {name}")
    ok("lobby pedestal / terminal / spawn")

    # 2) Crate path (extend existing CrateHud — no second modal)
    need(
        "src/Client/CrateHud.luau",
        ["PickCrate", "GetCrate", "ModalMouse", "Motions", "rarity"],
    )
    need(
        "src/Server/Economy/CrateService.luau",
        ["ensureStarter", "grantFightDrop", "pick", "CratePick3"],
    )
    need("src/Server/World/LobbyPrompts.luau", ["StarterCrate", "OpenCrate", "CratePrompt"])
    need("src/Client/CombatHud.luau", ["function CombatHud.openCrate", "OpenCrate.OnClientEvent"])
    ok("crate path (HUD + service + world prompt)")

    # 3) Garage path
    need(
        "src/Client/GarageHud.luau",
        ["SellPart", "sellConfirm", "ModalMouse", "compare", "EquipPart"],
    )
    need("src/Server/init.server.luau", ["SellPart.OnServerInvoke", "spawnGaragePreview"])
    need("src/Server/Parts/InventoryService.luau", ["removePart", "grantPart"])
    ok("garage equip / sell / compare")

    # 4) Campaign path
    need(
        "src/Client/CombatHud.luau",
        ["function CombatHud.openCampaign", "ListCampaign", "StartFight", "Motions.popIn"],
    )
    need("src/Server/Campaign/Ladder.luau", ["Tin Rook", "Gate Weld", "taunt"])
    need("src/Client/OnboardingHud.luau", ["campaign", "garage", "crate"])
    ok("campaign + onboarding")

    # 5) Arena fight path
    need(
        "src/Server/World/ArenaService.luau",
        ["spawnFight", "PadA", "PadB", "teleportPlayerToArena", "teleportPlayerToLobby"],
    )
    need(
        "src/Client/CombatHud.luau",
        ["BattleCamera.startForArena", "CombatJuice", "SubmitAction", "YOUR TURN"],
    )
    need("src/Client/CombatJuice.luau", ["leanMech", "showBanner", "setOverheat"])
    need("src/Server/init.server.luau", ["PlayerSession.toCombat", "PlayerSession.toLobby"])
    for arena in ("ScrapPit", "DryDock", "NightYard"):
        data = json.loads(read(f"src/Workspace/Arenas/{arena}.model.json"))
        for pad in ("PadA", "PadB"):
            if not find_named(data, pad):
                fail(f"{arena}.{pad}")
    ok("arena pads + combat juice + session phase")

    # 6) Return / payout / topbar
    need(
        "src/Client/CombatHud.luau",
        ["onReturnLobby", "ReturnLobby", "RewardSheet", "TopbarHud.setVisible(true)"],
    )
    need("src/Client/RewardSheet.luau", ["ModalMouse", "Crate chance", "WIN PAYOUT"])
    need(
        "src/Client/TopbarHud.luau",
        ["AccountLevel", "WalletUpdated", "openCrate", "bgTopbar"],
    )
    need("src/Shared/Progress/AccountLevel.luau", ["fromXp", "xpForLevel"])
    need("src/Client/UI/Motions.luau", ["popIn", "revealStagger", "pulse"])
    need("src/Client/UI/SoundHooks.luau", ["play", "telegraph", "drone", "spark"])
    need("src/Shared/UI/Theme.luau", ["bgTopbar", "rareCoin"])
    need("src/Shared/Economy/DailyLogin.luau", ["rewardForStreak", "BASE_COMMON"])
    need("src/Server/Economy/DailyLoginService.luau", ["claim", "status"])
    need("src/Client/DailyHud.luau", ["ClaimDaily", "DailyChip"])
    need("src/Client/PvpHud.luau", ["QueuePvP", "Ghost spar", "StartGhostSpar"])
    need("src/Shared/Parts/ThemedStarters.luau", ["ScrapBay", "ForgeYard", "clientList"])
    need("src/Shared/Economy/Rewards.luau", ["isGuaranteedCrate", "guaranteedCrate"])
    need("src/Server/Campaign/Ladder.luau", ["guaranteedCrateWin", "pacing", "threat", "elements"])
    need("src/Shared/Combat/Elements.luau", ["GLYPH", "SHORT", "color"])
    need("src/Client/CombatJuice.luau", ["spawnHitSparks", "telegraphMove", "showDroneTick"])
    ok("return lobby + reward sheet + modern topbar + gameplay depth")

    # 7) Remotes contract for the loop
    remotes = read("src/Server/Remotes.luau")
    for name in (
        "GetBootstrap",
        "GetCrate",
        "PickCrate",
        "OpenCrate",
        "GetInventory",
        "EquipPart",
        "SellPart",
        "ListCampaign",
        "StartFight",
        "SubmitAction",
        "FightSettled",
        "ReturnLobby",
        "WalletUpdated",
        "OpenCampaign",
        "OpenGarage",
        "ClaimDaily",
        "GetDaily",
        "QueuePvP",
        "LeaveQueue",
        "StartGhostSpar",
        "ListThemes",
        "OpenPvP",
    ):
        if name not in remotes:
            fail(f"Remotes missing {name}")
    ok("remotes for full loop")

    # 8) Join bar still exposes Campaign / Garage / Crate / PvP
    join = read("src/Client/JoinHud.luau")
    for needle in ('id = "campaign"', 'id = "garage"', 'id = "crate"', 'id = "pvp"', "openCrate", "THEMED STARTERS"):
        if needle not in join:
            fail(f"JoinHud missing {needle}")
    ok("join bar campaign / garage / crate / pvp + themes")

    print("PLAYTEST LOOP PASS — lobby→crate→garage→campaign→arena→return")


if __name__ == "__main__":
    main()

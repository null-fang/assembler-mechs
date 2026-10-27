#!/usr/bin/env python3
"""Offline smoke for lobby→arena→return + integrator hooks."""
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


def kit_ids() -> set[str]:
    parts = ROOT / "src" / "AssemblerAssets" / "Parts"
    return {p.name[: -len(".model.json")] for p in parts.glob("*.model.json")}


def find_named(node: dict, want: str) -> list[dict]:
    hits: list[dict] = []
    if node.get("Name") == want:
        hits.append(node)
    for child in node.get("Children", []):
        hits.extend(find_named(child, want))
    return hits


def main() -> None:
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "verify_part_coverage.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(r.stdout.strip())
    if r.returncode != 0:
        fail("verify_part_coverage")

    kits = kit_ids()
    if len(kits) < 149:
        fail(f"expected ≥149 kits, got {len(kits)}")
    ok(f"{len(kits)} kits on disk")

    starter = [
        "rusty_cage",
        "workboot_l",
        "workboot_r",
        "snap_arm",
        "rivet_gun",
        "brick_shoulder",
        "desk_brick",
        "scrap_cpu",
        "floor_bit",
    ]
    miss = [i for i in starter if i not in kits]
    if miss:
        fail(f"starter kits missing: {miss}")
    ok("starter kits present")

    lobby = json.loads((ROOT / "src/Workspace/Lobby.model.json").read_text())
    if not find_named(lobby, "GaragePedestal"):
        fail("GaragePedestal")
    if not find_named(lobby, "CampaignTerminal"):
        fail("CampaignTerminal")
    ok("lobby hooks")

    for arena in ("ScrapPit", "DryDock", "NightYard"):
        data = json.loads((ROOT / f"src/Workspace/Arenas/{arena}.model.json").read_text())
        for pad in ("PadA", "PadB"):
            hits = find_named(data, pad)
            if not hits:
                fail(f"{arena}.{pad}")
            kids = {c.get("Name") for c in hits[0].get("Children", [])}
            if "Spawn" not in kids:
                fail(f"{arena}.{pad}.Spawn")
        ok(f"{arena} pads")

    must_exist = {
        "src/Shared/World/Tags.luau": ["AssemblerGaragePedestal", "AssemblerPadA"],
        "src/Shared/Session/Phase.luau": ["AssemblerPhase", "Lobby", "Combat"],
        "src/Shared/Util/Maid.luau": ["DoCleaning", "Connect"],
        "src/Server/World/WorldBootstrap.luau": ["tagWorld", "tagMech", "CollectionService"],
        "src/Server/Session/PlayerSession.luau": ["toLobby", "toCombat"],
        "src/Client/KitPreload.luau": ["PreloadAsync"],
        "src/Client/SessionBridge.luau": ["ATTR_PHASE", "onChanged", "SessionBridge.start"],
        "src/Server/World/ArenaService.luau": ["spawnGaragePreview", "spawnFight", "WorldBootstrap"],
        "src/Server/World/LobbyPrompts.luau": ["Maid", "Tags"],
        "src/Server/init.server.luau": ["PlayerSession", "SUBMIT_MIN_GAP"],
        "src/Client/init.client.luau": ["KitPreload", "SessionBridge", "CombatHud"],
        "src/Client/CombatHud.luau": ["JoinHud.mount", "ModalMouse", "ReturnLobby"],
        "src/Shared/Assembler/Assembler.luau": ["tryAssetClone", "not torsoFromKit"],
    }
    for rel, needles in must_exist.items():
        text = (ROOT / rel).read_text()
        for n in needles:
            if n not in text:
                fail(f"{rel} missing {n}")
    ok("integrator + flow modules")

    print("SMOKE PASS — lobby→arena→return hooks green")


if __name__ == "__main__":
    main()

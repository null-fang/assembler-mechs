-- Abstraction over NPC script vs remote player.
-- Combat sim takes BattleOpponent + loadout → FighterState; same resolver for PvE and PvP.

local BattleMode = require(script.Parent.BattleMode)
local Slots = require(script.Parent.Parent.Parts.Slots)

export type OpponentKind = "Npc" | "Player"

export type BattleOpponent = {
	id: string,
	displayName: string,
	kind: OpponentKind,
	mode: BattleMode.BattleMode,
	mechId: string?,
	-- Optional prebuilt loadout (NPCs always set this; players resolve from inventory).
	loadout: Slots.EquippedLoadout?,
}

local BattleOpponent = {}

function BattleOpponent.fromNpc(
	id: string,
	displayName: string,
	mechId: string?,
	loadout: Slots.EquippedLoadout?
): BattleOpponent
	return {
		id = id,
		displayName = displayName,
		kind = "Npc",
		mode = BattleMode.PvE,
		mechId = mechId,
		loadout = loadout,
	}
end

function BattleOpponent.fromPlayer(
	userId: number,
	displayName: string,
	mechId: string?,
	loadout: Slots.EquippedLoadout?
): BattleOpponent
	return {
		id = tostring(userId),
		displayName = displayName,
		kind = "Player",
		mode = BattleMode.PvP,
		mechId = mechId,
		loadout = loadout,
	}
end

return BattleOpponent

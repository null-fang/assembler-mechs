-- Abstraction over NPC script vs remote player. Combat sim should take this,
-- not a concrete Player or NPC table, so PvE ladder and PvP arena share one resolver.

local BattleMode = require(script.Parent.BattleMode)

export type OpponentKind = "Npc" | "Player"

export type BattleOpponent = {
	id: string,
	displayName: string,
	kind: OpponentKind,
	mode: BattleMode.BattleMode,
	-- Mech loadout / combat snapshot filled by later combat work.
	mechId: string?,
}

local BattleOpponent = {}

function BattleOpponent.fromNpc(id: string, displayName: string, mechId: string?): BattleOpponent
	return {
		id = id,
		displayName = displayName,
		kind = "Npc",
		mode = BattleMode.PvE,
		mechId = mechId,
	}
end

function BattleOpponent.fromPlayer(userId: number, displayName: string, mechId: string?): BattleOpponent
	return {
		id = tostring(userId),
		displayName = displayName,
		kind = "Player",
		mode = BattleMode.PvP,
		mechId = mechId,
	}
end

return BattleOpponent

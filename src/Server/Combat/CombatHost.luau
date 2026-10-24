-- Server combat host stub. Full turn resolver comes later.
-- Takes BattleOpponent so PvE and PvP share one path.

local BattleMode = require(game.ReplicatedStorage.Shared.Modes.BattleMode)
local BattleOpponent = require(game.ReplicatedStorage.Shared.Modes.BattleOpponent)
local CombatTypes = require(game.ReplicatedStorage.Shared.Combat.Types)

local CombatHost = {}

export type BattleSession = {
	mode: BattleMode.BattleMode,
	attacker: BattleOpponent.BattleOpponent,
	defender: BattleOpponent.BattleOpponent,
	turnBudget: CombatTypes.TurnBudget,
}

function CombatHost.beginSession(
	mode: BattleMode.BattleMode,
	attacker: BattleOpponent.BattleOpponent,
	defender: BattleOpponent.BattleOpponent
): BattleSession
	local ap = CombatTypes.DEFAULT_AP_PER_TURN
	return {
		mode = mode,
		attacker = attacker,
		defender = defender,
		turnBudget = {
			apMax = ap,
			apRemaining = ap,
		},
	}
end

-- Placeholder: spend AP for a move or attack. No damage resolution yet.
function CombatHost.spendAP(session: BattleSession, cost: number): boolean
	if cost < 0 or session.turnBudget.apRemaining < cost then
		return false
	end
	session.turnBudget.apRemaining -= cost
	return true
end

return CombatHost

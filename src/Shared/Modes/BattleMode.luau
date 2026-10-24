-- Dual-mode battle infra from day one (PvE shippable first; PvP hooks ready).

export type BattleMode = "PvE" | "PvP"

local BattleMode = {}

BattleMode.PvE = "PvE" :: BattleMode
BattleMode.PvP = "PvP" :: BattleMode

function BattleMode.isValid(mode: string): boolean
	return mode == BattleMode.PvE or mode == BattleMode.PvP
end

return BattleMode

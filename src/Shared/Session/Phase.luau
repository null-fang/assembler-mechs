-- Player attribute contract for lobby ↔ combat lifecycle.
-- Juice / onboarding / UI can listen via GetAttributeChangedSignal — no extra remotes.

local Phase = {}

Phase.ATTR_PHASE = "AssemblerPhase"
Phase.ATTR_ARENA = "AssemblerArena"
Phase.ATTR_FIGHT = "AssemblerFightIndex"

Phase.Lobby = "Lobby"
Phase.Combat = "Combat"

export type PhaseName = "Lobby" | "Combat"

function Phase.read(player: Player): PhaseName
	local v = player:GetAttribute(Phase.ATTR_PHASE)
	if v == Phase.Combat then
		return Phase.Combat
	end
	return Phase.Lobby
end

return Phase

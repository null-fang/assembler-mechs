-- Server writer for Shared.Session.Phase player attributes.

local Phase = require(game.ReplicatedStorage.Shared.Session.Phase)

local PlayerSession = {}

function PlayerSession.toLobby(player: Player)
	player:SetAttribute(Phase.ATTR_PHASE, Phase.Lobby)
	player:SetAttribute(Phase.ATTR_ARENA, "")
	player:SetAttribute(Phase.ATTR_FIGHT, 0)
end

function PlayerSession.toCombat(player: Player, arenaId: string?, fightIndex: number?)
	player:SetAttribute(Phase.ATTR_PHASE, Phase.Combat)
	player:SetAttribute(Phase.ATTR_ARENA, arenaId or "")
	player:SetAttribute(Phase.ATTR_FIGHT, fightIndex or 0)
end

return PlayerSession

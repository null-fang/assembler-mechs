-- PvP matchmaking / arena stub. Not in first shippable content, but hooks exist.
-- Target later: 1v1, 3 lives from mech slots, soft power-band matchmaking.

local BattleMode = require(game.ReplicatedStorage.Shared.Modes.BattleMode)
local BattleOpponent = require(game.ReplicatedStorage.Shared.Modes.BattleOpponent)

export type QueueEntry = {
	userId: number,
	displayName: string,
	powerBand: number, -- stub; formula later
}

export type MatchPair = {
	mode: BattleMode.BattleMode,
	a: BattleOpponent.BattleOpponent,
	b: BattleOpponent.BattleOpponent,
}

local Matchmaking = {}

local queue: { QueueEntry } = {}

function Matchmaking.enqueue(entry: QueueEntry)
	table.insert(queue, entry)
end

function Matchmaking.clearQueue()
	table.clear(queue)
end

-- Stub: pair first two in queue. No rating logic yet.
function Matchmaking.tryPair(): MatchPair?
	if #queue < 2 then
		return nil
	end
	local a = table.remove(queue, 1) :: QueueEntry
	local b = table.remove(queue, 1) :: QueueEntry
	return {
		mode = BattleMode.PvP,
		a = BattleOpponent.fromPlayer(a.userId, a.displayName, nil),
		b = BattleOpponent.fromPlayer(b.userId, b.displayName, nil),
	}
end

return Matchmaking

-- Thin PvP queue stub. No full matchmaking — shares CombatHost / Resolver.
-- Solo players can spar a ghost foe (same resolver path, mode = PvP).

local BattleMode = require(game.ReplicatedStorage.Shared.Modes.BattleMode)
local BattleOpponent = require(game.ReplicatedStorage.Shared.Modes.BattleOpponent)
local Catalog = require(game.ReplicatedStorage.Shared.Parts.Catalog)
local Slots = require(game.ReplicatedStorage.Shared.Parts.Slots)

export type QueueEntry = {
	userId: number,
	displayName: string,
	powerBand: number, -- stub; formula later
	joinedAt: number,
}

export type MatchPair = {
	mode: BattleMode.BattleMode,
	a: BattleOpponent.BattleOpponent,
	b: BattleOpponent.BattleOpponent,
}

export type QueueStatus = {
	inQueue: boolean,
	position: number?,
	queueSize: number,
	waitingFor: string,
}

local Matchmaking = {}

local queue: { QueueEntry } = {}

local function ghostLoadout(): Slots.EquippedLoadout
	return {
		torso = Catalog.require("plate_box"),
		leftLeg = Catalog.require("workboot_l"),
		rightLeg = Catalog.require("workboot_r"),
		lowerLeft = Catalog.asWeapon("snap_arm", "LowerLeft"),
		lowerRight = Catalog.asWeapon("rivet_gun", "LowerRight"),
		shoulderLeft = nil,
		shoulderRight = Catalog.asWeapon("brick_shoulder", "ShoulderRight"),
		chips = { Catalog.require("thick_skin") },
		battery = Catalog.require("desk_brick"),
		cpu = Catalog.require("scrap_cpu"),
		drone = Catalog.require("floor_bit"),
	}
end

function Matchmaking.enqueue(entry: QueueEntry)
	for _, e in queue do
		if e.userId == entry.userId then
			return
		end
	end
	entry.joinedAt = entry.joinedAt or os.clock()
	table.insert(queue, entry)
end

function Matchmaking.dequeue(userId: number): boolean
	for i, e in queue do
		if e.userId == userId then
			table.remove(queue, i)
			return true
		end
	end
	return false
end

function Matchmaking.isQueued(userId: number): boolean
	for _, e in queue do
		if e.userId == userId then
			return true
		end
	end
	return false
end

function Matchmaking.queueSize(): number
	return #queue
end

function Matchmaking.status(userId: number): QueueStatus
	local pos = nil
	for i, e in queue do
		if e.userId == userId then
			pos = i
			break
		end
	end
	return {
		inQueue = pos ~= nil,
		position = pos,
		queueSize = #queue,
		waitingFor = if pos ~= nil then "Opponent (stub — no full matchmaking)" else "Idle",
	}
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

-- Practice spar: ghost foe through the same PvP resolver path.
function Matchmaking.ghostOpponent(displayName: string?): BattleOpponent.BattleOpponent
	return BattleOpponent.fromNpc("ghost-pvp", displayName or "Queue Ghost", "ghost-mech", ghostLoadout())
end

return Matchmaking

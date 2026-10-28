-- Server combat host. Owns live battles; PvE and PvP share Resolver.

local BattleMode = require(game.ReplicatedStorage.Shared.Modes.BattleMode)
local BattleOpponent = require(game.ReplicatedStorage.Shared.Modes.BattleOpponent)
local MechState = require(game.ReplicatedStorage.Shared.Combat.MechState)
local Resolver = require(game.ReplicatedStorage.Shared.Combat.Resolver)
local NpcBrain = require(game.ReplicatedStorage.Shared.Combat.NpcBrain)
local Types = require(game.ReplicatedStorage.Shared.Combat.Types)

local CombatHost = {}

export type LiveBattle = {
	battleId: string,
	userId: number?,
	fightIndex: number?,
	battle: Resolver.Battle,
	-- Side A is always the local/initiating player for PvE.
	playerSide: Resolver.BattleSide,
}

local sessions: { [string]: LiveBattle } = {}
local nextId = 1

local function newBattleId(): string
	local id = ("battle-%d"):format(nextId)
	nextId += 1
	return id
end

local function fighterFromOpponent(opp: BattleOpponent.BattleOpponent, position: number): MechState.FighterState
	local loadout = opp.loadout
	assert(loadout, ("Opponent %s missing loadout"):format(opp.id))
	return MechState.fromLoadout(opp.id, opp.displayName, loadout, position)
end

function CombatHost.beginPvE(
	userId: number,
	playerOpponent: BattleOpponent.BattleOpponent,
	npcOpponent: BattleOpponent.BattleOpponent,
	fightIndex: number?
): LiveBattle
	local sideA = fighterFromOpponent(playerOpponent, 2)
	local sideB = fighterFromOpponent(npcOpponent, Types.ARENA_TILES - 1)
	local battle = Resolver.createBattle(BattleMode.PvE, sideA, sideB)
	local live: LiveBattle = {
		battleId = newBattleId(),
		userId = userId,
		fightIndex = fightIndex,
		battle = battle,
		playerSide = "A",
	}
	sessions[live.battleId] = live
	return live
end

-- PvP entry uses the same resolver path; matchmaking fills opponents later.
-- Optional userId binds the session for ghost-spar / thin queue stubs.
function CombatHost.beginPvP(
	oppA: BattleOpponent.BattleOpponent,
	oppB: BattleOpponent.BattleOpponent,
	userId: number?
): LiveBattle
	local sideA = fighterFromOpponent(oppA, 2)
	local sideB = fighterFromOpponent(oppB, Types.ARENA_TILES - 1)
	local battle = Resolver.createBattle(BattleMode.PvP, sideA, sideB)
	local live: LiveBattle = {
		battleId = newBattleId(),
		userId = userId,
		fightIndex = nil,
		battle = battle,
		playerSide = "A",
	}
	sessions[live.battleId] = live
	return live
end

function CombatHost.get(battleId: string): LiveBattle?
	return sessions[battleId]
end

function CombatHost.getForUser(userId: number): LiveBattle?
	for _, live in sessions do
		if live.userId == userId and live.battle.outcome == "Ongoing" then
			return live
		end
	end
	return nil
end

function CombatHost.release(battleId: string)
	sessions[battleId] = nil
end

local function ensurePlayerTurn(live: LiveBattle): (boolean, string?)
	if live.battle.outcome ~= "Ongoing" then
		return false, "Fight over"
	end
	if live.battle.activeSide ~= live.playerSide then
		return false, "Not your turn"
	end
	return true, nil
end

-- After the player ends their turn, run NPC turns until it's the player's turn again (or fight ends).
function CombatHost.advanceNpcIfNeeded(live: LiveBattle)
	local battle = live.battle
	local guard = 0
	while battle.outcome == "Ongoing" and battle.activeSide ~= live.playerSide do
		NpcBrain.playTurn(battle)
		guard += 1
		if guard > 6 then
			break
		end
	end
end

function CombatHost.applyPlayerAction(live: LiveBattle, action: Types.BattleAction): (boolean, string?)
	local okTurn, turnErr = ensurePlayerTurn(live)
	if not okTurn then
		return false, turnErr
	end
	local ok, err = Resolver.applyAction(live.battle, action)
	if not ok then
		return false, err
	end
	if action.kind == "EndTurn" or live.battle.activeSide ~= live.playerSide then
		CombatHost.advanceNpcIfNeeded(live)
	end
	return true, nil
end

function CombatHost.snapshot(live: LiveBattle): { [string]: any }
	local snap = Resolver.snapshot(live.battle)
	snap.battleId = live.battleId
	snap.fightIndex = live.fightIndex
	snap.playerSide = live.playerSide
	local legal = {}
	if live.battle.outcome == "Ongoing" and live.battle.activeSide == live.playerSide then
		for _, a in Resolver.listLegalActions(live.battle) do
			table.insert(legal, a)
		end
	end
	snap.legalActions = legal
	return snap
end

return CombatHost

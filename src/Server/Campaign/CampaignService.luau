-- Player campaign progress + start/resolve fights.

local Ladder = require(script.Parent.Ladder)
local CombatHost = require(script.Parent.Parent.Combat.CombatHost)
local EconomyService = require(script.Parent.Parent.Economy.EconomyService)
local CrateService = require(script.Parent.Parent.Economy.CrateService)
local InventoryService = require(script.Parent.Parent.Parts.InventoryService)
local ArenaService = require(script.Parent.Parent.World.ArenaService)
local BattleMode = require(game.ReplicatedStorage.Shared.Modes.BattleMode)
local Rewards = require(game.ReplicatedStorage.Shared.Economy.Rewards)
local SoftStarter = require(game.ReplicatedStorage.Shared.Parts.StarterMech)

local CampaignService = {}

local progressByUser = {}
local displayNames: { [number]: string } = {}
local ladderCache = Ladder.buildFirstSlice()

function CampaignService.rememberDisplayName(userId: number, displayName: string)
	displayNames[userId] = displayName
end

function CampaignService.getProgress(userId)
	local p = progressByUser[userId]
	if not p then
		p = { highestCleared = 0, xp = 0 }
		progressByUser[userId] = p
	end
	return p
end

function CampaignService.listFights(userId)
	local progress = CampaignService.getProgress(userId)
	local list = {}
	for _, fight in ladderCache do
		local arenaId = ArenaService.pickArenaForFight(fight.index)
		table.insert(list, {
			index = fight.index,
			name = fight.opponent.displayName,
			blurb = fight.blurb,
			taunt = fight.taunt,
			rewardCommon = fight.rewardCommonWin,
			crateChanceWin = Rewards.crateChance(fight.index, true),
			unlocked = fight.index <= progress.highestCleared + 1,
			cleared = fight.index <= progress.highestCleared,
			arenaId = arenaId,
		})
	end
	return list
end

function CampaignService.startFight(userId, displayName, fightIndex)
	if fightIndex < 1 or fightIndex > #ladderCache then
		return nil, "Bad fight index"
	end
	local progress = CampaignService.getProgress(userId)
	if fightIndex > progress.highestCleared + 1 then
		return nil, "Fight locked"
	end
	if CombatHost.getForUser(userId) then
		return nil, "Already in a fight"
	end

	CampaignService.rememberDisplayName(userId, displayName)

	local fight = ladderCache[fightIndex]
	local loadout = InventoryService.activeLoadout(userId)
	if not SoftStarter.isLegal(loadout) then
		InventoryService.grantStarter(userId)
		loadout = InventoryService.activeLoadout(userId)
		if not SoftStarter.isLegal(loadout) then
			return nil, "Mech not legal — equip torso, matched legs, and a weapon"
		end
	end

	local playerOpp = {
		id = tostring(userId),
		displayName = displayName,
		kind = "Player",
		mode = BattleMode.PvE,
		mechId = "primary",
		loadout = loadout,
	}

	local live = CombatHost.beginPvE(userId, playerOpp, fight.opponent, fightIndex)
	local npcLoadout = fight.opponent.loadout
	if npcLoadout then
		local arenaId = ArenaService.spawnFight(
			loadout,
			displayName,
			npcLoadout,
			fight.opponent.displayName,
			fightIndex
		)
		;(live :: any).arenaId = arenaId
	end
	;(live :: any).taunt = fight.taunt
	;(live :: any).npcName = fight.opponent.displayName
	return live, nil
end

function CampaignService.settleIfFinished(userId, live)
	local battle = live.battle
	if battle.outcome == "Ongoing" then
		return nil
	end

	local won = battle.outcome == "SideAWins"
	local fightIndex = live.fightIndex or 1
	local seed = userId * 19 + fightIndex * 41 + (if won then 7 else 2)
	local reward = Rewards.forCampaignFight(fightIndex, won, seed)
	EconomyService.addCommon(userId, reward.common)

	local progress = CampaignService.getProgress(userId)
	progress.xp += reward.xp
	if won and fightIndex > progress.highestCleared then
		progress.highestCleared = fightIndex
	end

	local crateOffer = nil
	if reward.crateDrop then
		crateOffer = CrateService.grantFightDrop(userId, fightIndex)
	end

	local result = {
		won = won,
		common = reward.common,
		xp = reward.xp,
		crateChance = reward.crateChance,
		crateDrop = reward.crateDrop and crateOffer ~= nil,
		highestCleared = progress.highestCleared,
		totalXp = progress.xp,
		walletCommon = EconomyService.getWallet(userId).common,
		arenaId = (live :: any).arenaId,
		npcName = (live :: any).npcName,
		taunt = (live :: any).taunt,
	}
	CombatHost.release(live.battleId)
	ArenaService.clearLiveMechs()
	local loadout = InventoryService.activeLoadout(userId)
	ArenaService.spawnGaragePreview(loadout, displayNames[userId] or "Your mech")
	return result
end

return CampaignService

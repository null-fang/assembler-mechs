-- Fight rewards: common currency + XP + crate roll chance.
-- Wins pay more than losses. Mid-ladder fights guarantee a crate on win.
-- Loss payouts stay soft so pacing never feels like a hard reset.

export type FightReward = {
	common: number,
	xp: number,
	won: boolean,
	crateChance: number, -- 0–1, for UI
	crateDrop: boolean, -- rolled this fight
	guaranteedCrate: boolean,
}

local Rewards = {}

-- Win crates locked in on these ladder indices (Hot Rivet, Peg Runner, Bolt Maw, Gate Weld).
local GUARANTEED_CRATE = {
	[3] = true,
	[5] = true,
	[7] = true,
	[10] = true,
}

local function clamp01(n: number): number
	return math.clamp(n, 0, 1)
end

function Rewards.isGuaranteedCrate(fightIndex: number, won: boolean): boolean
	return won and GUARANTEED_CRATE[fightIndex] == true
end

-- Deterministic-ish roll so replay feels stable per fight index + win flag + seed.
function Rewards.rollCrate(fightIndex: number, won: boolean, seed: number?): boolean
	if Rewards.isGuaranteedCrate(fightIndex, won) then
		return true
	end
	local chance = Rewards.crateChance(fightIndex, won)
	local s = seed or (fightIndex * 17 + (if won then 91 else 3))
	local r = (math.floor(s * 9301 + 49297) % 233280) / 233280
	return r < chance
end

function Rewards.crateChance(fightIndex: number, won: boolean): number
	if Rewards.isGuaranteedCrate(fightIndex, won) then
		return 1
	end
	if won then
		return clamp01(0.28 + fightIndex * 0.04)
	end
	-- Soft loss consolation: low but visible chance so losses aren't dead air.
	return clamp01(0.08 + fightIndex * 0.012)
end

function Rewards.forCampaignFight(fightIndex: number, won: boolean, seed: number?): FightReward
	local baseCommon = 40 + fightIndex * 12
	-- Milestone fights bump win payout so pacing reads clearer.
	if GUARANTEED_CRATE[fightIndex] then
		baseCommon += 20
	end
	local baseXp = 15 + fightIndex * 5
	local crateChance = Rewards.crateChance(fightIndex, won)
	local crateDrop = Rewards.rollCrate(fightIndex, won, seed)
	local guaranteed = Rewards.isGuaranteedCrate(fightIndex, won)
	if won then
		return {
			common = baseCommon,
			xp = baseXp,
			won = true,
			crateChance = crateChance,
			crateDrop = crateDrop,
			guaranteedCrate = guaranteed,
		}
	end
	-- Losses keep ~30% common / ~40% XP so the ladder never feels punishing.
	return {
		common = math.max(12, math.floor(baseCommon * 0.3)),
		xp = math.max(5, math.floor(baseXp * 0.4)),
		won = false,
		crateChance = crateChance,
		crateDrop = crateDrop,
		guaranteedCrate = false,
	}
end

return Rewards

-- Fight rewards: common currency + XP + crate roll chance.
-- Wins pay more than losses. Crate chance is higher on a win.

export type FightReward = {
	common: number,
	xp: number,
	won: boolean,
	crateChance: number, -- 0–1, for UI
	crateDrop: boolean, -- rolled this fight
}

local Rewards = {}

local function clamp01(n: number): number
	return math.clamp(n, 0, 1)
end

-- Deterministic-ish roll so replay feels stable per fight index + win flag + seed.
function Rewards.rollCrate(fightIndex: number, won: boolean, seed: number?): boolean
	local chance = Rewards.crateChance(fightIndex, won)
	local s = seed or (fightIndex * 17 + (if won then 91 else 3))
	local r = (math.floor(s * 9301 + 49297) % 233280) / 233280
	return r < chance
end

function Rewards.crateChance(fightIndex: number, won: boolean): number
	if won then
		return clamp01(0.28 + fightIndex * 0.04)
	end
	return clamp01(0.06 + fightIndex * 0.015)
end

function Rewards.forCampaignFight(fightIndex: number, won: boolean, seed: number?): FightReward
	local baseCommon = 40 + fightIndex * 12
	local baseXp = 15 + fightIndex * 5
	local crateChance = Rewards.crateChance(fightIndex, won)
	local crateDrop = Rewards.rollCrate(fightIndex, won, seed)
	if won then
		return {
			common = baseCommon,
			xp = baseXp,
			won = true,
			crateChance = crateChance,
			crateDrop = crateDrop,
		}
	end
	return {
		common = math.floor(baseCommon * 0.25),
		xp = math.floor(baseXp * 0.35),
		won = false,
		crateChance = crateChance,
		crateDrop = crateDrop,
	}
end

return Rewards

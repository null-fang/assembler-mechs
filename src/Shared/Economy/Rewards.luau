-- Fight rewards: common currency + XP stub.

export type FightReward = {
	common: number,
	xp: number,
	won: boolean,
}

local Rewards = {}

-- XP is stubbed for account level later; still grant numbers so UI can show them.
function Rewards.forCampaignFight(fightIndex: number, won: boolean): FightReward
	local baseCommon = 40 + fightIndex * 12
	local baseXp = 15 + fightIndex * 5
	if won then
		return {
			common = baseCommon,
			xp = baseXp,
			won = true,
		}
	end
	return {
		common = math.floor(baseCommon * 0.25),
		xp = math.floor(baseXp * 0.35),
		won = false,
	}
end

return Rewards

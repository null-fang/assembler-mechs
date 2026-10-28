-- Soft daily claim. In-memory per user; swap for DataStore later.

local DailyLogin = require(game.ReplicatedStorage.Shared.Economy.DailyLogin)
local EconomyService = require(script.Parent.EconomyService)
local CrateService = require(script.Parent.CrateService)

local DailyLoginService = {}

type State = {
	lastClaimDay: string?,
	streak: number,
}

local byUser: { [number]: State } = {}

local function state(userId: number): State
	local s = byUser[userId]
	if not s then
		s = { lastClaimDay = nil, streak = 0 }
		byUser[userId] = s
	end
	return s
end

local function yesterdayKey(): string
	return DailyLogin.dayKey(os.time() - 86400)
end

function DailyLoginService.status(userId: number)
	local s = state(userId)
	local today = DailyLogin.dayKey()
	local claimedToday = s.lastClaimDay == today
	local nextStreak = if claimedToday
		then s.streak
		elseif s.lastClaimDay == yesterdayKey() then s.streak + 1
		else 1
	local preview = DailyLogin.rewardForStreak(if claimedToday then math.max(1, s.streak) else nextStreak)
	return {
		claimedToday = claimedToday,
		streak = s.streak,
		nextStreak = nextStreak,
		dayKey = today,
		preview = preview,
	}
end

function DailyLoginService.claim(userId: number): (boolean, string?, any?)
	local s = state(userId)
	local today = DailyLogin.dayKey()
	if s.lastClaimDay == today then
		return false, "Already claimed today", nil
	end

	local nextStreak = if s.lastClaimDay == yesterdayKey() then s.streak + 1 else 1
	nextStreak = math.min(nextStreak, DailyLogin.STREAK_CAP)
	local reward = DailyLogin.rewardForStreak(nextStreak)

	EconomyService.addCommon(userId, reward.common)
	local crateOffer = nil
	if reward.crate then
		crateOffer = CrateService.grantFightDrop(userId, 0)
		-- If a fight crate is already pending, still paid coins; note missed crate.
	end

	s.lastClaimDay = today
	s.streak = nextStreak

	return true, nil, {
		common = reward.common,
		crate = crateOffer ~= nil,
		streak = s.streak,
		label = reward.label,
		wallet = EconomyService.getWallet(userId),
		cratePending = crateOffer ~= nil,
	}
end

return DailyLoginService

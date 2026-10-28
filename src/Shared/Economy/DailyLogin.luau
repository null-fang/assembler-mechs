-- Soft daily / login reward (modern Roblox pattern). Common + maybe 1 crate.
-- Stub: no DataStore yet; day key is UTC YYYY-MM-DD via os.date.

export type DailyReward = {
	common: number,
	crate: boolean,
	streakBonusCommon: number,
	label: string,
}

local DailyLogin = {}

DailyLogin.BASE_COMMON = 80
DailyLogin.STREAK_BONUS_PER_DAY = 15
DailyLogin.STREAK_CAP = 7
-- Grant a crate on day 1 and every 3rd streak day (3, 6, …).
DailyLogin.CRATE_STREAK_INTERVAL = 3

function DailyLogin.dayKey(unix: number?): string
	return os.date("!%Y-%m-%d", unix or os.time()) :: string
end

function DailyLogin.rewardForStreak(streak: number): DailyReward
	local s = math.clamp(math.max(1, streak), 1, DailyLogin.STREAK_CAP)
	local bonus = (s - 1) * DailyLogin.STREAK_BONUS_PER_DAY
	local crate = s == 1 or (s % DailyLogin.CRATE_STREAK_INTERVAL == 0)
	return {
		common = DailyLogin.BASE_COMMON + bonus,
		crate = crate,
		streakBonusCommon = bonus,
		label = if crate then "Daily · coins + crate" else "Daily · coins",
	}
end

return DailyLogin

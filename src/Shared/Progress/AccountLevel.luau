-- Account level from XP. Soft gates only in first slice.

export type LevelInfo = {
	level: number,
	xp: number,
	xpIntoLevel: number,
	xpForNext: number,
	progress: number, -- 0..1 toward next level
}

local AccountLevel = {}

-- ~100 XP per early level, mild curve.
function AccountLevel.xpForLevel(level: number): number
	local lv = math.max(1, math.floor(level))
	return 80 + (lv - 1) * 25
end

function AccountLevel.fromXp(totalXp: number): LevelInfo
	local xp = math.max(0, math.floor(totalXp or 0))
	local level = 1
	local remaining = xp
	while true do
		local need = AccountLevel.xpForLevel(level)
		if remaining < need then
			return {
				level = level,
				xp = xp,
				xpIntoLevel = remaining,
				xpForNext = need,
				progress = if need > 0 then remaining / need else 0,
			}
		end
		remaining -= need
		level += 1
		if level > 99 then
			return {
				level = 99,
				xp = xp,
				xpIntoLevel = need,
				xpForNext = need,
				progress = 1,
			}
		end
	end
end

return AccountLevel

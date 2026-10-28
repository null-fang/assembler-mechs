-- Extension points for gameplay-content-depth worker.
-- Ladder / crates / rewards stay authoritative elsewhere; this documents stable shapes.

export type FightContent = {
	index: number,
	name: string,
	blurb: string,
	taunt: string?,
	arenaTheme: string?, -- ThemeIds.ARENA_THEMES or override
	mechLine: string?, -- ThemeIds.MECH_LINES preferred foe look
	rewardCommonWin: number?,
	crateChanceBonus: number?,
}

export type CratePoolHook = {
	poolId: string,
	partIds: { string },
	themeLine: string?,
}

local ContentHooks = {}

ContentHooks.FIRST_SLICE_COUNT = 10
ContentHooks.ATTR_FIGHT_THEME = "FightTheme"

-- Placeholders the content worker replaces / expands (empty = use Ladder defs).
ContentHooks.extraFights = {} :: { FightContent }
ContentHooks.cratePools = {} :: { CratePoolHook }

function ContentHooks.listExtraFights(): { FightContent }
	return ContentHooks.extraFights
end

function ContentHooks.listCratePools(): { CratePoolHook }
	return ContentHooks.cratePools
end

return ContentHooks

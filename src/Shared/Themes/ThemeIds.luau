-- Stable theme keys for themed mech lines + arena theme sets.
-- Workers fill art/content; Integrator keeps ids + attribute names green.

local ThemeIds = {}

-- Mech / part visual lines (Attribute ThemeLine on kits + assembled mechs).
ThemeIds.MECH_LINES = {
	"ScrapBay", -- starter rusty / common scrap
	"NeonDock", -- cyan emissive / glass
	"ForgeYard", -- heat / slag / furnace
	"IceRail", -- frost / ski
	"VoltCage", -- arc / pulse / neural
	"BunkerLine", -- heavy plate / vault
} :: { string }

-- Arena mood keys (Attribute ThemeId on arena Models).
ThemeIds.ARENA_THEMES = {
	"ScrapPit",
	"DryDock",
	"NightYard",
} :: { string }

-- Default map: Rojo arena model name → ThemeId (arena theme worker may override).
ThemeIds.arenaDefault = {
	ScrapPit = "ScrapPit",
	DryDock = "DryDock",
	NightYard = "NightYard",
} :: { [string]: string }

ThemeIds.ATTR_MECH_LINE = "ThemeLine"
ThemeIds.ATTR_ARENA_THEME = "ThemeId"
ThemeIds.ATTR_FIGHT_THEME = "FightTheme"

function ThemeIds.isMechLine(id: string): boolean
	for _, key in ThemeIds.MECH_LINES do
		if key == id then
			return true
		end
	end
	return false
end

function ThemeIds.arenaThemeFor(arenaId: string): string
	return ThemeIds.arenaDefault[arenaId] or arenaId
end

return ThemeIds

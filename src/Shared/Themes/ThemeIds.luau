-- Stable theme keys for themed mech lines + arena theme sets.
-- Workers fill art/content; Integrator keeps ids + attribute names green.

local ThemeIds = {}

-- Mech / part visual lines (Attribute ThemeLine on kits + assembled mechs).
-- Display names: Yardbone / Rimevault / Duneplate / Voltframe (+ legacy bay lines).
ThemeIds.MECH_LINES = {
	"Yardbone", -- scrap rust/olive (was ScrapBay)
	"Rimevault", -- arctic white/ice (was IceRail)
	"Duneplate", -- desert sand/ochre
	"Voltframe", -- neon cyan/magenta night (was NeonDock / VoltCage)
	"ForgeYard", -- heat / slag / furnace sibling
	"BunkerLine", -- heavy plate / vault sibling
} :: { string }

-- Alias → canonical (Integrator hooks + older stamps).
ThemeIds.MECH_LINE_ALIASES = {
	ScrapBay = "Yardbone",
	IceRail = "Rimevault",
	NeonDock = "Voltframe",
	VoltCage = "Voltframe",
	ForgeYard = "ForgeYard",
	BunkerLine = "BunkerLine",
} :: { [string]: string }

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

function ThemeIds.canonicalizeMechLine(id: string): string
	return ThemeIds.MECH_LINE_ALIASES[id] or id
end

function ThemeIds.isMechLine(id: string): boolean
	local canon = ThemeIds.canonicalizeMechLine(id)
	for _, key in ThemeIds.MECH_LINES do
		if key == canon or key == id then
			return true
		end
	end
	return false
end

function ThemeIds.arenaThemeFor(arenaId: string): string
	return ThemeIds.arenaDefault[arenaId] or arenaId
end

return ThemeIds

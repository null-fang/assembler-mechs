-- Elemental damage triad helpers for HUD icons / telegraphs.

local Types = require(script.Parent.Types)
local Theme = require(script.Parent.Parent.UI.Theme)

local Elements = {}

Elements.ORDER = { "Physical", "Heat", "Energy" } :: { Types.DamageType }

Elements.SHORT = {
	Physical = "PHY",
	Heat = "HEAT",
	Energy = "NRG",
}

Elements.GLYPH = {
	Physical = "●",
	Heat = "▲",
	Energy = "◆",
}

function Elements.color(damageType: Types.DamageType): Color3
	if damageType == "Heat" then
		return Theme.colors.temperature
	elseif damageType == "Energy" then
		return Theme.colors.battery
	end
	return Theme.colors.strokeBright
end

function Elements.label(damageType: Types.DamageType): string
	return ("%s %s"):format(Elements.GLYPH[damageType] or "·", Elements.SHORT[damageType] or damageType)
end

return Elements

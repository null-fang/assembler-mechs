-- Themed mech line contract for catalog kits + assembled previews.
-- Themed-mech-line worker stamps ThemeLine on Parts; Assembler copies to mech Model.

local ThemeIds = require(script.Parent.ThemeIds)

local MechLine = {}

MechLine.ATTR = ThemeIds.ATTR_MECH_LINE

-- Heuristic starter mapping until catalog gets explicit theme fields.
local ID_HINTS = {
	{ "frost", "IceRail" },
	{ "ski", "IceRail" },
	{ "ice", "IceRail" },
	{ "volt", "VoltCage" },
	{ "arc", "VoltCage" },
	{ "pulse", "VoltCage" },
	{ "neural", "VoltCage" },
	{ "neon", "NeonDock" },
	{ "glass", "NeonDock" },
	{ "prism", "NeonDock" },
	{ "forge", "ForgeYard" },
	{ "furnace", "ForgeYard" },
	{ "slag", "ForgeYard" },
	{ "torch", "ForgeYard" },
	{ "heat", "ForgeYard" },
	{ "bunker", "BunkerLine" },
	{ "vault", "BunkerLine" },
	{ "plate", "BunkerLine" },
	{ "iron", "BunkerLine" },
}

function MechLine.fromPartId(partId: string): string
	local lower = string.lower(partId)
	for _, pair in ID_HINTS do
		if string.find(lower, pair[1], 1, true) then
			return pair[2]
		end
	end
	return "ScrapBay"
end

function MechLine.readFromInstance(inst: Instance): string?
	local v = inst:GetAttribute(MechLine.ATTR)
	if typeof(v) == "string" and ThemeIds.isMechLine(v) then
		return v
	end
	return nil
end

function MechLine.applyToMech(model: Model, line: string)
	if not ThemeIds.isMechLine(line) then
		line = "ScrapBay"
	end
	model:SetAttribute(MechLine.ATTR, line)
end

return MechLine

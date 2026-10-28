-- Themed mech line contract for catalog kits + assembled previews.
-- Themed-mech-line worker stamps ThemeLine on Parts; Assembler copies to mech Model.

local ThemeIds = require(script.Parent.ThemeIds)

local MechLine = {}

MechLine.ATTR = ThemeIds.ATTR_MECH_LINE

-- Heuristic mapping from part id → ThemeIds.MECH_LINES (Yardbone / Rimevault / Duneplate / Voltframe).
local ID_HINTS = {
	{ "rime", "Rimevault" },
	{ "frost", "Rimevault" },
	{ "glacer", "Rimevault" },
	{ "cryo", "Rimevault" },
	{ "ice_", "Rimevault" },
	{ "snow", "Rimevault" },
	{ "ski", "Rimevault" },
	{ "dune", "Duneplate" },
	{ "ochre", "Duneplate" },
	{ "sandal", "Duneplate" },
	{ "sand_", "Duneplate" },
	{ "dust", "Duneplate" },
	{ "dry_cell", "Duneplate" },
	{ "heat_skirt", "Duneplate" },
	{ "sun_rack", "Duneplate" },
	{ "volt", "Voltframe" },
	{ "neon", "Voltframe" },
	{ "night", "Voltframe" },
	{ "mag_", "Voltframe" },
	{ "pulseleg", "Voltframe" },
	{ "cyan", "Voltframe" },
	{ "glow_beetle", "Voltframe" },
	{ "prism", "Voltframe" },
	{ "arc_", "Voltframe" },
	{ "slag", "ForgeYard" },
	{ "furnace", "ForgeYard" },
	{ "torch", "ForgeYard" },
	{ "ember", "ForgeYard" },
	{ "bunker", "BunkerLine" },
	{ "vault", "BunkerLine" },
	{ "yardbone", "Yardbone" },
	{ "cinder", "Yardbone" },
	{ "rust_", "Yardbone" },
	{ "scrap_", "Yardbone" },
	{ "rusty", "Yardbone" },
}

function MechLine.fromPartId(partId: string): string
	local lower = string.lower(partId)
	for _, pair in ID_HINTS do
		if string.find(lower, pair[1], 1, true) then
			return ThemeIds.canonicalizeMechLine(pair[2])
		end
	end
	return "Yardbone"
end

function MechLine.readFromInstance(inst: Instance): string?
	local v = inst:GetAttribute(MechLine.ATTR)
	if typeof(v) == "string" and ThemeIds.isMechLine(v) then
		return ThemeIds.canonicalizeMechLine(v)
	end
	return nil
end

function MechLine.applyToMech(model: Model, line: string)
	if not ThemeIds.isMechLine(line) then
		line = "Yardbone"
	else
		line = ThemeIds.canonicalizeMechLine(line)
	end
	model:SetAttribute(MechLine.ATTR, line)
end

return MechLine

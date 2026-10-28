-- Themed starter browse for mech bay. Keys align with Shared/Themes/ThemeIds.MECH_LINES
-- so art workers' ThemeLine stamps match bay browse rows. Torso hints track Showcase kits.

local ThemeIds = require(script.Parent.Parent.Themes.ThemeIds)

export type ThemeStatus = "live" | "preview" | "coming"

export type ThemedStarter = {
	id: string, -- ThemeIds mech line
	name: string,
	tagline: string,
	accent: string,
	status: ThemeStatus,
	torsoHint: string?,
	showcase: string?,
	unlockNote: string,
}

local ThemedStarters = {}

-- One browse row per ThemeIds.MECH_LINES entry.
ThemedStarters.list = {
	{
		id = "ScrapBay",
		name = "Scrap Bay",
		tagline = "Default bolts. What you spawn with.",
		accent = "scrap",
		status = "live",
		torsoHint = "rusty_cage",
		showcase = "ThemeScrapMech",
		unlockNote = "Equipped on Primary. Yardbone showcase is the art bar.",
	},
	{
		id = "ForgeYard",
		name = "Forge Yard",
		tagline = "Heat fists and slag plating.",
		accent = "ember",
		status = "preview",
		torsoHint = "slagspine",
		showcase = "ThemeDesertMech",
		unlockNote = "Kits landed — browse only until bay apply wires.",
	},
	{
		id = "IceRail",
		name = "Ice Rail",
		tagline = "Rime vault. Quiet frost frames.",
		accent = "frost",
		status = "preview",
		torsoHint = "rimevault",
		showcase = "ThemeArcticMech",
		unlockNote = "Kits landed — browse only until bay apply wires.",
	},
	{
		id = "VoltCage",
		name = "Volt Cage",
		tagline = "Voltframe night arc.",
		accent = "arc",
		status = "preview",
		torsoHint = "voltframe",
		showcase = "ThemeNeonMech",
		unlockNote = "Kits landed — browse only until bay apply wires.",
	},
	{
		id = "NeonDock",
		name = "Neon Dock",
		tagline = "Nightspine emissive line.",
		accent = "toxin",
		status = "preview",
		torsoHint = "nightspine",
		showcase = "ThemeNeonMech",
		unlockNote = "Kits landed — browse only until bay apply wires.",
	},
	{
		id = "BunkerLine",
		name = "Bunker Line",
		tagline = "Duneplate heavy hull.",
		accent = "void",
		status = "preview",
		torsoHint = "duneplate",
		showcase = "ThemeDesertMech",
		unlockNote = "Kits landed — browse only until bay apply wires.",
	},
} :: { ThemedStarter }

function ThemedStarters.clientList()
	local out = {}
	for _, t in ThemedStarters.list do
		assert(ThemeIds.isMechLine(t.id), "ThemedStarter id must be ThemeIds.MECH_LINES")
		table.insert(out, {
			id = t.id,
			name = t.name,
			tagline = t.tagline,
			accent = t.accent,
			status = t.status,
			torsoHint = t.torsoHint,
			showcase = t.showcase,
			unlockNote = t.unlockNote,
			canApply = t.status == "live",
		})
	end
	return out
end

return ThemedStarters

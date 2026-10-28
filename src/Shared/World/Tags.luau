-- CollectionService tag names for world hooks.
-- Env / juice / UI workers should FindFirstChild *or* GetTagged — tags are the stable API.

local Tags = {
	Lobby = "AssemblerLobby",
	CampaignTerminal = "AssemblerCampaignTerminal",
	GaragePedestal = "AssemblerGaragePedestal",
	StarterCrate = "AssemblerStarterCrate",
	Arena = "AssemblerArena",
	PadA = "AssemblerPadA",
	PadB = "AssemblerPadB",
	ArenaOrigin = "AssemblerArenaOrigin",
	Mech = "AssemblerMech",
	GaragePreview = "AssemblerGaragePreview",
	-- Theme / content workers: GetTagged these for themed lines + arena sets.
	MechLine = "AssemblerMechLine",
	ArenaTheme = "AssemblerArenaTheme",
}

return Tags


-- CollectionService tag names for world hooks.
-- Env / juice / UI workers should FindFirstChild *or* GetTagged — tags are the stable API.

local Tags = {
	Lobby = "AssemblerLobby",
	CampaignTerminal = "AssemblerCampaignTerminal",
	GaragePedestal = "AssemblerGaragePedestal",
	Arena = "AssemblerArena",
	PadA = "AssemblerPadA",
	PadB = "AssemblerPadB",
	ArenaOrigin = "AssemblerArenaOrigin",
	Mech = "AssemblerMech",
	GaragePreview = "AssemblerGaragePreview",
}

return Tags

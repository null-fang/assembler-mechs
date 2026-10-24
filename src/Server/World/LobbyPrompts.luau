-- ProximityPrompts on Rojo lobby hooks: CampaignTerminal + GaragePedestal.

local ArenaService = require(script.Parent.ArenaService)

local LobbyPrompts = {}

local function ensurePrompt(parent: BasePart, name: string, actionText: string, objectText: string): ProximityPrompt
	local existing = parent:FindFirstChild(name)
	if existing and existing:IsA("ProximityPrompt") then
		return existing
	end
	if existing then
		existing:Destroy()
	end
	local pr = Instance.new("ProximityPrompt")
	pr.Name = name
	pr.ActionText = actionText
	pr.ObjectText = objectText
	pr.HoldDuration = 0
	pr.MaxActivationDistance = 14
	pr.RequiresLineOfSight = false
	pr.Parent = parent
	return pr
end

function LobbyPrompts.wire(remotes)
	if not ArenaService.ensureWorld() then
		warn("[Assembler] LobbyPrompts: maps missing")
		return
	end

	local lobby = ArenaService.getLobby()
	if not lobby then
		return
	end

	local terminal = lobby:FindFirstChild("CampaignTerminal", true)
	if terminal and terminal:IsA("BasePart") then
		local pr = ensurePrompt(terminal, "CampaignPrompt", "Open", "Campaign")
		pr.Triggered:Connect(function(player)
			remotes.OpenCampaign:FireClient(player)
		end)
	else
		warn("[Assembler] CampaignTerminal missing")
	end

	local pedestal = ArenaService.getGaragePedestal()
	if pedestal then
		local pr = ensurePrompt(pedestal, "GaragePrompt", "Open", "Garage")
		pr.Triggered:Connect(function(player)
			remotes.OpenGarage:FireClient(player)
		end)
	else
		warn("[Assembler] GaragePedestal missing")
	end

	print("[Assembler] Lobby prompts wired (Campaign + Garage)")
end

return LobbyPrompts

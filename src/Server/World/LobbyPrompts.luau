-- ProximityPrompts on Rojo lobby hooks: CampaignTerminal + GaragePedestal.
-- Idempotent: Maid cleans prior wiring if Rojo remounts / wire() re-runs.

local CollectionService = game:GetService("CollectionService")

local ArenaService = require(script.Parent.ArenaService)
local Maid = require(game.ReplicatedStorage.Shared.Util.Maid)
local Tags = require(game.ReplicatedStorage.Shared.World.Tags)

local LobbyPrompts = {}

local maid: Maid.Maid? = nil

local function ensurePrompt(parent: BasePart, name: string, actionText: string, objectText: string): ProximityPrompt
	local existing = parent:FindFirstChild(name)
	if existing and existing:IsA("ProximityPrompt") then
		existing.ActionText = actionText
		existing.ObjectText = objectText
		existing.HoldDuration = 0
		existing.MaxActivationDistance = 14
		existing.RequiresLineOfSight = false
		pcall(function()
			existing.Exclusivity = Enum.ProximityPromptExclusivity.OnePerButton
		end)
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
	pcall(function()
		pr.Exclusivity = Enum.ProximityPromptExclusivity.OnePerButton
	end)
	pr.Parent = parent
	return pr
end

local function firstTaggedOrNamed(tag: string, lobby: Instance, name: string): BasePart?
	for _, inst in CollectionService:GetTagged(tag) do
		if inst:IsA("BasePart") and inst:IsDescendantOf(lobby) then
			return inst
		end
	end
	local found = lobby:FindFirstChild(name, true)
	if found and found:IsA("BasePart") then
		return found
	end
	return nil
end

function LobbyPrompts.wire(remotes)
	if maid then
		maid:DoCleaning()
	end
	maid = Maid.new()

	if not ArenaService.ensureWorld() then
		warn("[Assembler] LobbyPrompts: maps missing")
		return
	end

	local lobby = ArenaService.getLobby()
	if not lobby then
		return
	end

	local terminal = firstTaggedOrNamed(Tags.CampaignTerminal, lobby, "CampaignTerminal")
	if terminal then
		local pr = ensurePrompt(terminal, "CampaignPrompt", "Open", "Campaign")
		maid:Connect(pr.Triggered, function(player)
			remotes.OpenCampaign:FireClient(player)
		end)
	else
		warn("[Assembler] CampaignTerminal missing")
	end

	local pedestal = firstTaggedOrNamed(Tags.GaragePedestal, lobby, "GaragePedestal")
		or ArenaService.getGaragePedestal()
	if pedestal then
		local pr = ensurePrompt(pedestal, "GaragePrompt", "Open", "Garage")
		maid:Connect(pr.Triggered, function(player)
			remotes.OpenGarage:FireClient(player)
		end)
	else
		warn("[Assembler] GaragePedestal missing")
	end

	print("[Assembler] Lobby prompts wired (Campaign + Garage, tagged)")
end

return LobbyPrompts

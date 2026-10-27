-- ProximityPrompts + modern billboards on CampaignTerminal / GaragePedestal / StarterCrate.
-- Idempotent: Maid cleans prior wiring if Rojo remounts / wire() re-runs.

local CollectionService = game:GetService("CollectionService")

local ArenaService = require(script.Parent.ArenaService)
local Maid = require(game.ReplicatedStorage.Shared.Util.Maid)
local Tags = require(game.ReplicatedStorage.Shared.World.Tags)

local LobbyPrompts = {}

local maid: Maid.Maid? = nil

local ThemeColors = {
	cyan = Color3.fromRGB(56, 196, 204),
	amber = Color3.fromRGB(232, 168, 56),
	panel = Color3.fromRGB(12, 16, 22),
	dim = Color3.fromRGB(148, 162, 180),
}

local function stylePrompt(pr: ProximityPrompt, accent: Color3)
	pr.HoldDuration = 0
	pr.MaxActivationDistance = 16
	pr.RequiresLineOfSight = false
	pr.Style = Enum.ProximityPromptStyle.Default
	pr.UIOffset = Vector2.new(0, -10)
	pr:SetAttribute("Accent", accent:ToHex())
	pr.KeyboardKeyCode = Enum.KeyCode.E
	pr.GamepadKeyCode = Enum.KeyCode.ButtonX
	pcall(function()
		pr.Exclusivity = Enum.ProximityPromptExclusivity.OnePerButton
	end)
end

local function ensurePrompt(
	parent: BasePart,
	name: string,
	actionText: string,
	objectText: string,
	accent: Color3
): ProximityPrompt
	local existing = parent:FindFirstChild(name)
	if existing and existing:IsA("ProximityPrompt") then
		existing.ActionText = actionText
		existing.ObjectText = objectText
		stylePrompt(existing, accent)
		return existing
	end
	if existing then
		existing:Destroy()
	end
	local pr = Instance.new("ProximityPrompt")
	pr.Name = name
	pr.ActionText = actionText
	pr.ObjectText = objectText
	stylePrompt(pr, accent)
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

local function ensureBillboard(parent: BasePart, name: string, title: string, subtitle: string, accent: Color3)
	local existing = parent:FindFirstChild(name)
	if existing then
		existing:Destroy()
	end
	local bb = Instance.new("BillboardGui")
	bb.Name = name
	bb.Size = UDim2.fromOffset(180, 48)
	bb.StudsOffset = Vector3.new(0, parent.Size.Y * 0.5 + 3.2, 0)
	bb.AlwaysOnTop = false
	bb.MaxDistance = 72
	bb.Parent = parent

	local frame = Instance.new("Frame")
	frame.Size = UDim2.fromScale(1, 1)
	frame.BackgroundColor3 = ThemeColors.panel
	frame.BackgroundTransparency = 0.18
	frame.BorderSizePixel = 0
	frame.Parent = bb
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 6)
	corner.Parent = frame
	local stroke = Instance.new("UIStroke")
	stroke.Color = accent
	stroke.Thickness = 1.5
	stroke.Transparency = 0.25
	stroke.Parent = frame

	local strip = Instance.new("Frame")
	strip.Size = UDim2.new(0, 3, 1, -8)
	strip.Position = UDim2.new(0, 4, 0, 4)
	strip.BackgroundColor3 = accent
	strip.BorderSizePixel = 0
	strip.Parent = frame

	local titleL = Instance.new("TextLabel")
	titleL.Size = UDim2.new(1, -16, 0, 22)
	titleL.Position = UDim2.new(0, 12, 0, 4)
	titleL.BackgroundTransparency = 1
	titleL.Font = Enum.Font.Oswald
	titleL.TextSize = 16
	titleL.TextColor3 = accent
	titleL.TextXAlignment = Enum.TextXAlignment.Left
	titleL.Text = title
	titleL.Parent = frame

	local subL = Instance.new("TextLabel")
	subL.Size = UDim2.new(1, -16, 0, 16)
	subL.Position = UDim2.new(0, 12, 0, 26)
	subL.BackgroundTransparency = 1
	subL.Font = Enum.Font.BuilderSans
	subL.TextSize = 11
	subL.TextColor3 = ThemeColors.dim
	subL.TextXAlignment = Enum.TextXAlignment.Left
	subL.Text = subtitle
	subL.Parent = frame

	return bb
end

local function ensureStarterCrate(lobby: Model): BasePart
	local existing = lobby:FindFirstChild("StarterCrate")
	if existing and existing:IsA("BasePart") then
		return existing
	end
	if existing then
		existing:Destroy()
	end

	local pedestal = lobby:FindFirstChild("GaragePedestal", true)
	local best: BasePart? = nil
	local bestDist = math.huge
	local origin = if pedestal and pedestal:IsA("BasePart") then pedestal.Position else Vector3.new(0, 1, 8)
	for _, child in lobby:GetChildren() do
		if child:IsA("BasePart") and string.sub(child.Name, 1, 5) == "Crate" then
			local d = (child.Position - origin).Magnitude
			if d < bestDist then
				bestDist = d
				best = child
			end
		end
	end

	local part: BasePart
	if best and bestDist < 40 then
		part = best:Clone()
		part.Name = "StarterCrate"
		part.Position = origin + Vector3.new(-10, 0.4, -6)
		part.Size = Vector3.new(3.2, 2.6, 3.2)
		part.Parent = lobby
	else
		part = Instance.new("Part")
		part.Name = "StarterCrate"
		part.Anchored = true
		part.Size = Vector3.new(3.2, 2.6, 3.2)
		part.Position = origin + Vector3.new(-10, 1.5, -6)
		part.Color = Color3.fromRGB(120, 88, 48)
		part.Material = Enum.Material.Wood
		part.TopSurface = Enum.SurfaceType.Smooth
		part.BottomSurface = Enum.SurfaceType.Smooth
		part.Parent = lobby
	end
	return part
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
		ensureBillboard(terminal, "CampaignBillboard", "CAMPAIGN", "NPC ladder · E", ThemeColors.cyan)
		local pr = ensurePrompt(terminal, "CampaignPrompt", "Open", "Campaign", ThemeColors.cyan)
		maid:Connect(pr.Triggered, function(player)
			remotes.OpenCampaign:FireClient(player)
		end)
	else
		warn("[Assembler] CampaignTerminal missing")
	end

	local pedestal = firstTaggedOrNamed(Tags.GaragePedestal, lobby, "GaragePedestal")
		or ArenaService.getGaragePedestal()
	if pedestal then
		ensureBillboard(pedestal, "GarageBillboard", "GARAGE", "Build bay · E", ThemeColors.amber)
		local pr = ensurePrompt(pedestal, "GaragePrompt", "Open", "Garage", ThemeColors.amber)
		maid:Connect(pr.Triggered, function(player)
			remotes.OpenGarage:FireClient(player)
		end)
	else
		warn("[Assembler] GaragePedestal missing")
	end

	local crate = ensureStarterCrate(lobby)
	if not CollectionService:HasTag(crate, Tags.StarterCrate) then
		CollectionService:AddTag(crate, Tags.StarterCrate)
	end
	ensureBillboard(crate, "CrateBillboard", "CRATE", "Pick one of three · E", ThemeColors.amber)
	local cratePrompt = ensurePrompt(crate, "CratePrompt", "Open", "Starter crate", ThemeColors.amber)
	maid:Connect(cratePrompt.Triggered, function(player)
		if remotes.OpenCrate then
			remotes.OpenCrate:FireClient(player)
		end
	end)

	print("[Assembler] Lobby prompts wired (Campaign + Garage + Crate, tagged)")
end

return LobbyPrompts

-- Create Remotes folder under ReplicatedStorage for client ↔ server fight loop.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Remotes = {}

local folder: Folder

local function remoteEvent(name: string): RemoteEvent
	local existing = folder:FindFirstChild(name)
	if existing and existing:IsA("RemoteEvent") then
		return existing
	end
	local re = Instance.new("RemoteEvent")
	re.Name = name
	re.Parent = folder
	return re
end

local function remoteFunction(name: string): RemoteFunction
	local existing = folder:FindFirstChild(name)
	if existing and existing:IsA("RemoteFunction") then
		return existing
	end
	local rf = Instance.new("RemoteFunction")
	rf.Name = name
	rf.Parent = folder
	return rf
end

function Remotes.init()
	local existing = ReplicatedStorage:FindFirstChild("AssemblerRemotes")
	if existing and existing:IsA("Folder") then
		folder = existing
	else
		folder = Instance.new("Folder")
		folder.Name = "AssemblerRemotes"
		folder.Parent = ReplicatedStorage
	end

	Remotes.GetBootstrap = remoteFunction("GetBootstrap")
	Remotes.ListCampaign = remoteFunction("ListCampaign")
	Remotes.StartFight = remoteFunction("StartFight")
	Remotes.SubmitAction = remoteFunction("SubmitAction")
	Remotes.GetBattle = remoteFunction("GetBattle")
	Remotes.GetInventory = remoteFunction("GetInventory")
	Remotes.EquipPart = remoteFunction("EquipPart")
	Remotes.UnequipPart = remoteFunction("UnequipPart")
	Remotes.CompleteOnboarding = remoteFunction("CompleteOnboarding")
	Remotes.GetCrate = remoteFunction("GetCrate")
	Remotes.PickCrate = remoteFunction("PickCrate")
	Remotes.SellPart = remoteFunction("SellPart")
	Remotes.ClaimDaily = remoteFunction("ClaimDaily")
	Remotes.GetDaily = remoteFunction("GetDaily")
	Remotes.ListThemes = remoteFunction("ListThemes")
	Remotes.QueuePvP = remoteFunction("QueuePvP")
	Remotes.LeaveQueue = remoteFunction("LeaveQueue")
	Remotes.GetQueueStatus = remoteFunction("GetQueueStatus")
	Remotes.StartGhostSpar = remoteFunction("StartGhostSpar")

	Remotes.BattleUpdated = remoteEvent("BattleUpdated")
	Remotes.FightSettled = remoteEvent("FightSettled")
	Remotes.InventoryUpdated = remoteEvent("InventoryUpdated")
	Remotes.WalletUpdated = remoteEvent("WalletUpdated")
	Remotes.OpenCampaign = remoteEvent("OpenCampaign")
	Remotes.OpenGarage = remoteEvent("OpenGarage")
	Remotes.OpenCrate = remoteEvent("OpenCrate")
	Remotes.OpenPvP = remoteEvent("OpenPvP")
	Remotes.ReturnLobby = remoteEvent("ReturnLobby")
	Remotes.DailyClaimed = remoteEvent("DailyClaimed")
	Remotes.QueueUpdated = remoteEvent("QueueUpdated")
end

return Remotes

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

	Remotes.BattleUpdated = remoteEvent("BattleUpdated")
	Remotes.FightSettled = remoteEvent("FightSettled")
end

return Remotes

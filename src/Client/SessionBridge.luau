-- Mirror server Player attributes (Shared.Session.Phase) for HUD / juice hooks.
-- Does not own UI chrome — UI/gacha and combat-juice workers can subscribe too.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Phase = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Session"):WaitForChild("Phase"))

local SessionBridge = {}

local player = Players.LocalPlayer
local listeners: { (phase: string, arena: string, fight: number) -> () } = {}

local function snapshot()
	local phase = player:GetAttribute(Phase.ATTR_PHASE)
	if typeof(phase) ~= "string" then
		phase = Phase.Lobby
	end
	local arena = player:GetAttribute(Phase.ATTR_ARENA)
	if typeof(arena) ~= "string" then
		arena = ""
	end
	local fight = player:GetAttribute(Phase.ATTR_FIGHT)
	if typeof(fight) ~= "number" then
		fight = 0
	end
	return phase :: string, arena :: string, fight :: number
end

local function emit()
	local phase, arena, fight = snapshot()
	for _, cb in listeners do
		task.spawn(cb, phase, arena, fight)
	end
end

function SessionBridge.onChanged(cb: (phase: string, arena: string, fight: number) -> ())
	table.insert(listeners, cb)
	task.defer(function()
		local phase, arena, fight = snapshot()
		cb(phase, arena, fight)
	end)
end

function SessionBridge.get()
	return snapshot()
end

function SessionBridge.start()
	player:GetAttributeChangedSignal(Phase.ATTR_PHASE):Connect(emit)
	player:GetAttributeChangedSignal(Phase.ATTR_ARENA):Connect(emit)
	player:GetAttributeChangedSignal(Phase.ATTR_FIGHT):Connect(emit)
end

return SessionBridge

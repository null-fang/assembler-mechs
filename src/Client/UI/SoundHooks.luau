-- Optional UI sound hooks. No asset pack required — silent until SoundIds set.

local SoundService = game:GetService("SoundService")

local SoundHooks = {}

local enabled = true
local group: SoundGroup? = nil

-- Leave empty; fill later with uploaded SoundIds.
local IDS = {
	click = "",
	hover = "",
	open = "",
	close = "",
	crateReveal = "",
	cratePick = "",
	equip = "",
	sell = "",
	damage = "",
	turn = "",
	win = "",
	loss = "",
}

local function ensureGroup(): SoundGroup
	if group and group.Parent then
		return group
	end
	local existing = SoundService:FindFirstChild("AssemblerUI")
	if existing and existing:IsA("SoundGroup") then
		group = existing
		return group
	end
	group = Instance.new("SoundGroup")
	group.Name = "AssemblerUI"
	group.Volume = 0.55
	group.Parent = SoundService
	return group
end

function SoundHooks.setEnabled(on: boolean)
	enabled = on
end

function SoundHooks.isEnabled(): boolean
	return enabled
end

function SoundHooks.play(kind: string)
	if not enabled then
		return
	end
	local id = IDS[kind]
	if not id or id == "" then
		return
	end
	local s = Instance.new("Sound")
	s.SoundId = id
	s.Volume = 0.7
	s.SoundGroup = ensureGroup()
	s.Parent = ensureGroup()
	s:Play()
	s.Ended:Connect(function()
		s:Destroy()
	end)
end

return SoundHooks

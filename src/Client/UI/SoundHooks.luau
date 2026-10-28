-- Optional UI / combat sound hook bank. No asset pack required — silent until SoundIds set.
-- Expand kinds here; wire asset IDs in Studio without code changes beyond this table.

local SoundService = game:GetService("SoundService")

local SoundHooks = {}

local enabled = true
local group: SoundGroup? = nil

-- Leave empty; fill later with uploaded SoundIds.
local IDS = {
	-- UI
	click = "",
	hover = "",
	open = "",
	close = "",
	equip = "",
	sell = "",
	upgrade = "",
	daily = "",
	queue = "",
	dequeue = "",
	-- Crate
	crateReveal = "",
	cratePick = "",
	-- Combat
	damage = "",
	hit = "",
	spark = "",
	move = "",
	fire = "",
	telegraph = "",
	drone = "",
	turn = "",
	overheat = "",
	battery = "",
	win = "",
	loss = "",
}

local VOL = {
	hover = 0.35,
	click = 0.55,
	spark = 0.45,
	drone = 0.5,
	telegraph = 0.4,
	daily = 0.65,
	queue = 0.6,
	hit = 0.7,
	damage = 0.7,
	fire = 0.65,
	win = 0.8,
	loss = 0.75,
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

function SoundHooks.kinds(): { string }
	local keys = {}
	for k in IDS do
		table.insert(keys, k)
	end
	table.sort(keys)
	return keys
end

function SoundHooks.setId(kind: string, soundId: string)
	if IDS[kind] ~= nil then
		IDS[kind] = soundId
	end
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
	s.Volume = VOL[kind] or 0.7
	s.SoundGroup = ensureGroup()
	s.Parent = ensureGroup()
	s:Play()
	s.Ended:Connect(function()
		s:Destroy()
	end)
end

return SoundHooks

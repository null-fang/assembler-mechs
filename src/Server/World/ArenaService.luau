-- Mount assembled mechs on lobby GaragePedestal and arena PadA/PadB.
-- Maps come from Rojo Workspace (Lobby + Arenas/*); no void fallback pads.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")
local Assembler = require(game.ReplicatedStorage.Shared.Assembler.Assembler)
local SoftSlots = require(game.ReplicatedStorage.Shared.Parts.Slots)
local WorldBootstrap = require(script.Parent.WorldBootstrap)

local ArenaService = {}

export type ArenaId = "ScrapPit" | "DryDock" | "NightYard"

ArenaService.ARENA_ORDER = { "ScrapPit", "DryDock", "NightYard" } :: { ArenaId }

local activeArenaId: ArenaId? = nil
local MECHS_NAME = "LiveMechs"
local GARAGE_MECH_NAME = "GaragePreviewMech"
local HERO_SHOWCASE_NAME = "HeroStarterShowcase"

local function waitChild(parent: Instance, name: string, timeout: number?): Instance?
	local existing = parent:FindFirstChild(name)
	if existing then
		return existing
	end
	local ok, result = pcall(function()
		return parent:WaitForChild(name, timeout or 5)
	end)
	if ok then
		return result
	end
	return nil
end

function ArenaService.getLobby(): Model?
	local lobby = Workspace:FindFirstChild("Lobby")
	if lobby and lobby:IsA("Model") then
		return lobby
	end
	return nil
end

function ArenaService.getArenasFolder(): Folder?
	local folder = Workspace:FindFirstChild("Arenas")
	if folder and folder:IsA("Folder") then
		return folder
	end
	return nil
end

function ArenaService.getArenaModel(arenaId: ArenaId): Model?
	local folder = ArenaService.getArenasFolder()
	if not folder then
		return nil
	end
	local model = folder:FindFirstChild(arenaId)
	if model and model:IsA("Model") then
		return model
	end
	return nil
end

function ArenaService.pickArenaForFight(fightIndex: number): ArenaId
	local list = ArenaService.ARENA_ORDER
	return list[((fightIndex - 1) % #list) + 1]
end

local function ensureMechsFolder(parent: Instance): Folder
	local existing = parent:FindFirstChild(MECHS_NAME)
	if existing and existing:IsA("Folder") then
		return existing
	end
	if existing then
		existing:Destroy()
	end
	local f = Instance.new("Folder")
	f.Name = MECHS_NAME
	f.Parent = parent
	return f
end

local function findPad(arena: Model, name: string): BasePart?
	local pad = arena:FindFirstChild(name, true)
	if pad and pad:IsA("BasePart") then
		return pad
	end
	return nil
end

function ArenaService.getPad(arenaId: ArenaId, side: "A" | "B"): BasePart?
	local arena = ArenaService.getArenaModel(arenaId)
	if not arena then
		return nil
	end
	return findPad(arena, if side == "A" then "PadA" else "PadB")
end

function ArenaService.getGaragePedestal(): BasePart?
	local lobby = ArenaService.getLobby()
	if not lobby then
		return nil
	end
	local pedestal = lobby:FindFirstChild("GaragePedestal", true)
	if pedestal and pedestal:IsA("BasePart") then
		return pedestal
	end
	return nil
end

-- Top-center of a pad/pedestal (foot plane).
local function surfacePoint(part: BasePart): Vector3
	return part.Position + Vector3.new(0, part.Size.Y * 0.5, 0)
end

-- Prefer named Attachment world position XZ; keep surface Y for feet.
local function mountPoint(part: BasePart, attachmentName: string?): Vector3
	local surface = surfacePoint(part)
	if attachmentName then
		local att = part:FindFirstChild(attachmentName)
		if att and att:IsA("Attachment") then
			local wp = att.WorldPosition
			return Vector3.new(wp.X, surface.Y, wp.Z)
		end
	end
	return surface
end

local function facingToward(from: Vector3, toward: Vector3): Vector3
	local delta = toward - from
	if delta.Magnitude < 0.05 then
		return Vector3.new(0, 0, -1)
	end
	return Vector3.new(delta.X, 0, delta.Z).Unit
end

local function addNameplate(model: Model, displayName: string)
	local root = model.PrimaryPart
	if not root then
		return
	end
	local bb = Instance.new("BillboardGui")
	bb.Name = "Nameplate"
	bb.Size = UDim2.fromOffset(160, 36)
	bb.StudsOffset = Vector3.new(0, 5.5, 0)
	bb.AlwaysOnTop = true
	bb.Parent = root
	local label = Instance.new("TextLabel")
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundTransparency = 0.35
	label.BackgroundColor3 = Color3.fromRGB(10, 12, 16)
	label.Text = displayName
	label.TextColor3 = Color3.fromRGB(235, 235, 235)
	label.Font = Enum.Font.GothamMedium
	label.TextSize = 14
	label.Parent = bb
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 4)
	corner.Parent = label
end

local function placeOn(
	parent: Instance,
	loadout: SoftSlots.EquippedLoadout,
	displayName: string,
	mount: Vector3,
	facing: Vector3,
	side: string?,
	teamTint: Color3?,
	attrs: { [string]: any }?
): Model
	local model = Assembler.buildModel(loadout, {
		name = "Mech_" .. (side or "X") .. "_" .. displayName,
		anchored = true,
		teamTint = teamTint,
	})
	model:PivotTo(Assembler.worldCFrameAt(mount, facing))
	if side then
		model:SetAttribute("Side", side)
	end
	model:SetAttribute("DisplayName", displayName)
	if attrs then
		for k, v in attrs do
			model:SetAttribute(k, v)
		end
	end
	model.Parent = parent
	addNameplate(model, displayName)
	local isPreview = attrs ~= nil and attrs.Preview == true
	WorldBootstrap.tagMech(model, isPreview)
	return model
end

function ArenaService.ensureWorld(): boolean
	-- Wait briefly for Rojo maps; do not invent void pads.
	local lobby = waitChild(Workspace, "Lobby", 8)
	local arenas = waitChild(Workspace, "Arenas", 8)
	if not lobby or not arenas then
		warn("[Assembler] Lobby/Arenas missing — Rojo maps not synced yet")
		return false
	end
	WorldBootstrap.tagWorld(lobby, arenas)
	return true
end

function ArenaService.clearArenaMechs(arenaId: ArenaId?)
	local id = arenaId or activeArenaId
	if not id then
		-- Clear all arenas' live mechs
		local folder = ArenaService.getArenasFolder()
		if folder then
			for _, arena in folder:GetChildren() do
				local live = arena:FindFirstChild(MECHS_NAME)
				if live then
					live:ClearAllChildren()
				end
			end
		end
		return
	end
	local arena = ArenaService.getArenaModel(id)
	if arena then
		local live = ensureMechsFolder(arena)
		live:ClearAllChildren()
	end
end

function ArenaService.clearLiveMechs()
	ArenaService.clearArenaMechs(activeArenaId)
	activeArenaId = nil
end

function ArenaService.spawnFight(
	playerLoadout: SoftSlots.EquippedLoadout,
	playerName: string,
	npcLoadout: SoftSlots.EquippedLoadout,
	npcName: string,
	fightIndex: number?
): ArenaId?
	ArenaService.ensureWorld()
	local arenaId = ArenaService.pickArenaForFight(fightIndex or 1)
	local arena = ArenaService.getArenaModel(arenaId)
	local padA = ArenaService.getPad(arenaId, "A")
	local padB = ArenaService.getPad(arenaId, "B")
	if not arena or not padA or not padB then
		warn("[Assembler] Arena pads missing for", arenaId)
		return nil
	end

	-- Hide garage preview while fighting.
	ArenaService.clearGaragePreview()

	ArenaService.clearArenaMechs(arenaId)
	activeArenaId = arenaId
	local live = ensureMechsFolder(arena)

	local mountA = mountPoint(padA, "Spawn")
	local mountB = mountPoint(padB, "Spawn")
	placeOn(
		live,
		playerLoadout,
		playerName,
		mountA,
		facingToward(mountA, mountB),
		"A",
		Color3.fromRGB(90, 140, 200),
		{ ArenaId = arenaId, Preview = false }
	)
	placeOn(
		live,
		npcLoadout,
		npcName,
		mountB,
		facingToward(mountB, mountA),
		"B",
		Color3.fromRGB(200, 100, 80),
		{ ArenaId = arenaId, Preview = false }
	)
	return arenaId
end

function ArenaService.clearGaragePreview()
	local lobby = ArenaService.getLobby()
	if not lobby then
		return
	end
	local existing = lobby:FindFirstChild(GARAGE_MECH_NAME)
	if existing then
		existing:Destroy()
	end
	-- Also clear any old LiveMechs previews under lobby
	local live = lobby:FindFirstChild(MECHS_NAME)
	if live then
		for _, child in live:GetChildren() do
			if child:GetAttribute("Preview") then
				child:Destroy()
			end
		end
	end
end

-- Hand-authored SM-like hero (AssemblerAssets.Showcase) — art bar beside the garage.
local function ensureHeroShowcase(lobby: Instance, pedestal: BasePart, facing: Vector3)
	local existing = lobby:FindFirstChild(HERO_SHOWCASE_NAME)
	if existing then
		return
	end
	local assets = ReplicatedStorage:FindFirstChild("AssemblerAssets")
	local folder = if assets then assets:FindFirstChild("Showcase") else nil
	local template = if folder then folder:FindFirstChild("HeroStarterMech") else nil
	if not (template and template:IsA("Model")) then
		return
	end
	local clone = template:Clone()
	clone.Name = HERO_SHOWCASE_NAME
	local root = clone:FindFirstChild("Root")
	if root and root:IsA("BasePart") then
		clone.PrimaryPart = root
		root.Transparency = 1
	end
	for _, d in clone:GetDescendants() do
		if d:IsA("BasePart") then
			d.Anchored = true
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
			d.Massless = true
		end
	end
	local side = Vector3.new(-facing.Z, 0, facing.X)
	if side.Magnitude < 0.05 then
		side = Vector3.new(1, 0, 0)
	else
		side = side.Unit
	end
	local mount = mountPoint(pedestal, "MechRoot") + side * 10
	clone:PivotTo(Assembler.worldCFrameAt(mount, facing))
	clone:SetAttribute("Preview", true)
	clone:SetAttribute("ArtBar", true)
	clone.Parent = lobby
	addNameplate(clone, "Hero art bar")
	WorldBootstrap.tagMech(clone, true)
end

function ArenaService.spawnGaragePreview(loadout: SoftSlots.EquippedLoadout, displayName: string)
	ArenaService.ensureWorld()
	-- Don't overwrite while a fight is active.
	if activeArenaId then
		return
	end
	local pedestal = ArenaService.getGaragePedestal()
	local lobby = ArenaService.getLobby()
	if not pedestal or not lobby then
		warn("[Assembler] GaragePedestal missing")
		return
	end

	ArenaService.clearGaragePreview()

	local mount = mountPoint(pedestal, "MechRoot")
	-- Face toward lobby spawn / bay entrance (−Z).
	local facing = Vector3.new(0, 0, -1)
	local spawn = lobby:FindFirstChild("SpawnLocation")
	if spawn and spawn:IsA("BasePart") then
		facing = facingToward(mount, spawn.Position)
	end

	local model = placeOn(
		lobby,
		loadout,
		displayName,
		mount,
		facing,
		"Garage",
		Color3.fromRGB(90, 140, 200),
		{ Preview = true }
	)
	model.Name = GARAGE_MECH_NAME
	ensureHeroShowcase(lobby, pedestal, facing)
end

function ArenaService.teleportPlayerToLobby(player: Player)
	local lobby = ArenaService.getLobby()
	if not lobby then
		return
	end
	local spawn = lobby:FindFirstChild("SpawnLocation")
	local character = player.Character
	if not character then
		return
	end
	local hrp = character:FindFirstChild("HumanoidRootPart")
	if not (hrp and hrp:IsA("BasePart")) then
		return
	end
	if spawn and spawn:IsA("BasePart") then
		hrp.CFrame = spawn.CFrame + Vector3.new(0, 3, 0)
	else
		local pedestal = ArenaService.getGaragePedestal()
		if pedestal then
			hrp.CFrame = CFrame.new(pedestal.Position + Vector3.new(0, 6, -14))
		end
	end
end

function ArenaService.teleportPlayerToArena(player: Player, arenaId: ArenaId?)
	local id = arenaId or activeArenaId
	if not id then
		return
	end
	local pad = ArenaService.getPad(id, "A")
	if not pad then
		return
	end
	local character = player.Character
	if not character then
		return
	end
	local hrp = character:FindFirstChild("HumanoidRootPart")
	if hrp and hrp:IsA("BasePart") then
		-- Stand beside PadA, looking at the lane.
		local padB = ArenaService.getPad(id, "B")
		local side = Vector3.new(0, 0, 14)
		if padB then
			local along = facingToward(pad.Position, padB.Position)
			side = Vector3.new(-along.Z, 0, along.X) * 14
		end
		local pos = surfacePoint(pad) + side + Vector3.new(0, 4, 0)
		local look = if padB then padB.Position else (pos + Vector3.new(0, 0, -1))
		hrp.CFrame = CFrame.lookAt(pos, Vector3.new(look.X, pos.Y, look.Z))
	end
end

-- Back-compat name used by older server entry.
function ArenaService.teleportPlayerNearArena(player: Player)
	if activeArenaId then
		ArenaService.teleportPlayerToArena(player, activeArenaId)
	else
		ArenaService.teleportPlayerToLobby(player)
	end
end

function ArenaService.getActiveArenaId(): ArenaId?
	return activeArenaId
end

return ArenaService

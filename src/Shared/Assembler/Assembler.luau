-- Build a visible low-poly mech Model from an equipped loadout.
-- Colored Block parts on sockets — readable silhouette at combat distance.

local Sockets = require(script.Parent.Sockets)
local Slots = require(script.Parent.Parent.Parts.Slots)
local Catalog = require(script.Parent.Parent.Parts.Catalog)

local Assembler = {}

export type BuildOptions = {
	name: string?,
	-- Anchor all parts (arena display).
	anchored: boolean?,
	-- Tint multiplier for NPC vs player (optional slight shift).
	teamTint: Color3?,
}

local function rarityEdge(rarity: Slots.PartRarity): Color3
	if rarity == "Rare" then
		return Color3.fromRGB(210, 170, 70)
	elseif rarity == "Uncommon" then
		return Color3.fromRGB(140, 170, 120)
	end
	return Color3.fromRGB(40, 40, 44)
end

local function makeBlock(
	parent: Model,
	name: string,
	size: Vector3,
	cframe: CFrame,
	color: Color3,
	rarity: Slots.PartRarity,
	anchored: boolean
): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = cframe
	p.Color = color
	p.Material = Enum.Material.SmoothPlastic
	p.Anchored = anchored
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent

	-- Thin selection box for uncommon/rare so rarity reads at distance.
	if rarity ~= "Common" then
		local box = Instance.new("SelectionBox")
		box.Adornee = p
		box.Color3 = rarityEdge(rarity)
		box.LineThickness = 0.03
		box.Transparency = 0.35
		box.Parent = p
	end

	return p
end

local function socketCFrame(torsoCF: CFrame, socket: Sockets.SocketDef): CFrame
	local rot = socket.rotationDeg
	local extra = CFrame.identity
	if rot then
		extra = CFrame.Angles(math.rad(rot.X), math.rad(rot.Y), math.rad(rot.Z))
	end
	return torsoCF * CFrame.new(socket.offset) * extra
end

local function tint(color: Color3, teamTint: Color3?): Color3
	if not teamTint then
		return color
	end
	return color:Lerp(teamTint, 0.18)
end

local function attachPart(
	model: Model,
	torsoCF: CFrame,
	socketName: Sockets.SocketName,
	partDef: Slots.PartDef?,
	anchored: boolean,
	teamTint: Color3?
)
	if not partDef then
		return
	end
	local catalogPart = partDef :: Catalog.CatalogPart
	local socket = Sockets.get(socketName)
	local size = (catalogPart.visual and catalogPart.visual.size) or socket.defaultSize
	local color = tint(
		(catalogPart.visual and catalogPart.visual.color) or Color3.fromRGB(120, 120, 120),
		teamTint
	)
	local cf = socketCFrame(torsoCF, socket)
	makeBlock(model, socketName .. "_" .. partDef.id, size, cf, color, partDef.rarity, anchored)
end

-- Place model so foot plane rests on padTopY at worldPosition.xz.
function Assembler.worldCFrameAt(padPosition: Vector3, facing: Vector3?): CFrame
	local look = facing or Vector3.new(0, 0, -1)
	if look.Magnitude < 0.05 then
		look = Vector3.new(0, 0, -1)
	end
	look = Vector3.new(look.X, 0, look.Z).Unit
	-- Torso center height above pad surface.
	local origin = Vector3.new(padPosition.X, padPosition.Y + Sockets.TORSO_HEIGHT, padPosition.Z)
	return CFrame.lookAt(origin, origin + look)
end

function Assembler.buildModel(loadout: SoftSlots.EquippedLoadout, opts: BuildOptions?): Model
	local options = opts or {}
	local anchored = if options.anchored == nil then true else options.anchored
	local teamTint = options.teamTint

	local model = Instance.new("Model")
	model.Name = options.name or "AssembledMech"

	-- Build around identity; caller :PivotTo the result.
	local torsoCF = CFrame.new(0, 0, 0)

	-- Head nub for silhouette readability (not a slot — pure visual).
	if loadout.torso then
		local torso = loadout.torso :: Catalog.CatalogPart
		attachPart(model, torsoCF, "Torso", loadout.torso, anchored, teamTint)
		local headColor = tint(
			(torso.visual and torso.visual.color or Color3.fromRGB(120, 100, 80)):Lerp(Color3.new(1, 1, 1), 0.15),
			teamTint
		)
		makeBlock(
			model,
			"HeadNub",
			Vector3.new(1.6, 1.1, 1.6),
			torsoCF * CFrame.new(0, 2.15, 0.1),
			headColor,
			torso.rarity,
			anchored
		)
	end

	attachPart(model, torsoCF, "LeftHip", loadout.leftLeg, anchored, teamTint)
	attachPart(model, torsoCF, "RightHip", loadout.rightLeg, anchored, teamTint)
	attachPart(model, torsoCF, "LowerLeft", loadout.lowerLeft, anchored, teamTint)
	attachPart(model, torsoCF, "LowerRight", loadout.lowerRight, anchored, teamTint)
	attachPart(model, torsoCF, "ShoulderLeft", loadout.shoulderLeft, anchored, teamTint)
	attachPart(model, torsoCF, "ShoulderRight", loadout.shoulderRight, anchored, teamTint)
	attachPart(model, torsoCF, "Battery", loadout.battery, anchored, teamTint)
	attachPart(model, torsoCF, "CPU", loadout.cpu, anchored, teamTint)
	attachPart(model, torsoCF, "Drone", loadout.drone, anchored, teamTint)

	-- Tiny chip markers on torso face (non-combat visual only).
	for i, chip in loadout.chips do
		local c = chip :: Catalog.CatalogPart
		local color = tint((c.visual and c.visual.color) or Color3.fromRGB(80, 100, 80), teamTint)
		local x = -0.55 + (i - 1) * 0.7
		makeBlock(
			model,
			"Chip_" .. tostring(i),
			Vector3.new(0.45, 0.2, 0.35),
			torsoCF * CFrame.new(x, 0.4, 1.35),
			color,
			chip.rarity,
			anchored
		)
	end

	local primary = model:FindFirstChild("Torso_" .. ((loadout.torso and loadout.torso.id) or ""))
	if primary and primary:IsA("BasePart") then
		model.PrimaryPart = primary
	else
		local any = model:FindFirstChildWhichIsA("BasePart")
		if any then
			model.PrimaryPart = any
		end
	end

	model:SetAttribute("Assembled", true)
	if loadout.torso then
		model:SetAttribute("TorsoId", loadout.torso.id)
	end

	return model
end

-- Serialize loadout to part ids for remotes / rebuild.
function Assembler.loadoutToIds(loadout: SoftSlots.EquippedLoadout): { [string]: any }
	local function idOf(p: SoftSlots.PartDef?): string?
		return if p then p.id else nil
	end
	local chips = {}
	for _, c in loadout.chips do
		table.insert(chips, c.id)
	end
	return {
		torso = idOf(loadout.torso),
		leftLeg = idOf(loadout.leftLeg),
		rightLeg = idOf(loadout.rightLeg),
		lowerLeft = idOf(loadout.lowerLeft),
		lowerRight = idOf(loadout.lowerRight),
		shoulderLeft = idOf(loadout.shoulderLeft),
		shoulderRight = idOf(loadout.shoulderRight),
		battery = idOf(loadout.battery),
		cpu = idOf(loadout.cpu),
		drone = idOf(loadout.drone),
		chips = chips,
	}
end

function Assembler.loadoutFromIds(ids: { [string]: any }): SoftSlots.EquippedLoadout
	local function req(id: any): SoftSlots.PartDef?
		if typeof(id) ~= "string" then
			return nil
		end
		return Catalog.require(id)
	end
	local function weapon(id: any, slot: SoftSlots.SlotKind): SoftSlots.PartDef?
		if typeof(id) ~= "string" then
			return nil
		end
		return Catalog.asWeapon(id, slot)
	end
	local chips = {}
	if typeof(ids.chips) == "table" then
		for _, cid in ids.chips do
			if typeof(cid) == "string" then
				table.insert(chips, Catalog.require(cid))
			end
		end
	end
	return {
		torso = req(ids.torso),
		leftLeg = req(ids.leftLeg),
		rightLeg = req(ids.rightLeg),
		lowerLeft = weapon(ids.lowerLeft, "LowerLeft"),
		lowerRight = weapon(ids.lowerRight, "LowerRight"),
		shoulderLeft = weapon(ids.shoulderLeft, "ShoulderLeft"),
		shoulderRight = weapon(ids.shoulderRight, "ShoulderRight"),
		chips = chips,
		battery = req(ids.battery),
		cpu = req(ids.cpu),
		drone = req(ids.drone),
	}
end

return Assembler

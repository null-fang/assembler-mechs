-- Build a visible low-poly mech Model from an equipped loadout.
-- Prefers authored multi-Part kits under ReplicatedStorage.AssemblerAssets.Parts
-- (named by catalog PartId). Falls back to articulated blocks/cylinders.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Sockets = require(script.Parent.Sockets)
local Slots = require(script.Parent.Parent.Parts.Slots)
local Catalog = require(script.Parent.Parent.Parts.Catalog)

local Assembler = {}

export type BuildOptions = {
	name: string?,
	anchored: boolean?,
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

local function tryAssetClone(partId: string): Instance?
	local assets = ReplicatedStorage:FindFirstChild("AssemblerAssets")
	if not assets then
		return nil
	end
	local partsFolder = assets:FindFirstChild("Parts")
	if not partsFolder then
		return nil
	end
	local template = partsFolder:FindFirstChild(partId)
	if not template then
		return nil
	end
	return template:Clone()
end

local function tint(color: Color3, teamTint: Color3?): Color3
	if not teamTint then
		return color
	end
	return color:Lerp(teamTint, 0.18)
end

local function resolvePrimary(model: Model): BasePart?
	local root = model:FindFirstChild("Root")
	if root and root:IsA("BasePart") then
		root.Transparency = 1
		model.PrimaryPart = root
		return root
	end
	local any = model:FindFirstChildWhichIsA("BasePart", true)
	if any then
		model.PrimaryPart = any
		return any
	end
	return nil
end

local function polishAuthoredModel(
	asset: Model,
	rarity: Slots.PartRarity,
	teamTint: Color3?,
	anchored: boolean
)
	resolvePrimary(asset)
	for _, d in asset:GetDescendants() do
		if d:IsA("BasePart") then
			d.Anchored = anchored
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
			d.Massless = true
			if d.Name == "Root" then
				d.Transparency = 1
			elseif string.sub(d.Name, 1, 6) == "Accent" then
				local edge = rarityEdge(rarity)
				if rarity == "Common" then
					d.Color = tint(d.Color, teamTint)
				else
					d.Color = tint(d.Color:Lerp(edge, 0.55), teamTint)
					d.Material = Enum.Material.Neon
				end
			elseif teamTint then
				d.Color = tint(d.Color, teamTint)
			end
		end
	end
	if rarity ~= "Common" then
		local root = asset.PrimaryPart
		if root then
			local box = Instance.new("SelectionBox")
			box.Adornee = root
			box.Color3 = rarityEdge(rarity)
			box.LineThickness = 0.04
			box.Transparency = 0.45
			box.Parent = asset
		end
	end
end

local function makeBlock(
	parent: Model,
	name: string,
	size: Vector3,
	cframe: CFrame,
	color: Color3,
	rarity: Slots.PartRarity,
	anchored: boolean,
	shape: Enum.PartType?
): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = cframe
	p.Color = color
	p.Material = Enum.Material.SmoothPlastic
	p.Shape = shape or Enum.PartType.Block
	p.Anchored = anchored
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent

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

local function shapeForSocket(socketName: Sockets.SocketName): Enum.PartType?
	if socketName == "LeftHip" or socketName == "RightHip" then
		return Enum.PartType.Cylinder
	end
	if socketName == "Drone" then
		return Enum.PartType.Ball
	end
	return nil
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
	local cf = socketCFrame(torsoCF, socket)

	-- Real multi-Part kits from AssemblerAssets.Parts/<partId>, if synced.
	local asset = tryAssetClone(partDef.id)
	if asset then
		if asset:IsA("Model") then
			asset.Name = socketName .. "_" .. partDef.id
			asset:SetAttribute("PartId", partDef.id)
			polishAuthoredModel(asset, partDef.rarity, teamTint, anchored)
			asset.Parent = model
			asset:PivotTo(cf)
			return
		elseif asset:IsA("BasePart") then
			asset.Name = socketName .. "_" .. partDef.id
			asset.CFrame = cf
			asset.Anchored = anchored
			asset.CanCollide = false
			if teamTint then
				asset.Color = tint(asset.Color, teamTint)
			end
			asset.Parent = model
			return
		end
	end

	local size = (catalogPart.visual and catalogPart.visual.size) or socket.defaultSize
	local color = tint(
		(catalogPart.visual and catalogPart.visual.color) or Color3.fromRGB(120, 120, 120),
		teamTint
	)
	local shape = shapeForSocket(socketName)
	-- Cylinders in Roblox are X-aligned; spin legs upright.
	local partCF = cf
	if shape == Enum.PartType.Cylinder then
		partCF = cf * CFrame.Angles(0, 0, math.rad(90))
		size = Vector3.new(size.Y, size.X, size.Z)
	end
	makeBlock(model, socketName .. "_" .. partDef.id, size, partCF, color, partDef.rarity, anchored, shape)

	-- Extra articulation so limbs/weapons read less like loose cubes.
	if socketName == "LeftHip" or socketName == "RightHip" then
		local foot = makeBlock(
			model,
			socketName .. "_Foot",
			Vector3.new(size.Z * 0.9, 0.45, size.Y * 1.15),
			cf * CFrame.new(0, -size.X * 0.55, 0.15),
			color:Lerp(Color3.new(0, 0, 0), 0.2),
			partDef.rarity,
			anchored,
			nil
		)
		local _ = foot
	elseif socketName == "LowerLeft" or socketName == "LowerRight" or socketName == "ShoulderLeft" or socketName == "ShoulderRight" then
		makeBlock(
			model,
			socketName .. "_Barrel",
			Vector3.new(size.X * 0.55, size.Y * 0.55, size.Z * 0.55),
			cf * CFrame.new(0, 0, -size.Z * 0.55),
			color:Lerp(Color3.new(1, 1, 1), 0.12),
			partDef.rarity,
			anchored,
			Enum.PartType.Cylinder
		)
	end
end

function Assembler.worldCFrameAt(padPosition: Vector3, facing: Vector3?): CFrame
	local look = facing or Vector3.new(0, 0, -1)
	if look.Magnitude < 0.05 then
		look = Vector3.new(0, 0, -1)
	end
	look = Vector3.new(look.X, 0, look.Z).Unit
	local origin = Vector3.new(padPosition.X, padPosition.Y + Sockets.TORSO_HEIGHT, padPosition.Z)
	return CFrame.lookAt(origin, origin + look)
end

function Assembler.buildModel(loadout: Slots.EquippedLoadout, opts: BuildOptions?): Model
	local options = opts or {}
	local anchored = if options.anchored == nil then true else options.anchored
	local teamTint = options.teamTint

	local model = Instance.new("Model")
	model.Name = options.name or "AssembledMech"

	local torsoCF = CFrame.new(0, 0, 0)

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
			anchored,
			nil
		)
		-- Shoulder fairings for silhouette
		makeBlock(
			model,
			"PauldronL",
			Vector3.new(1.2, 0.7, 1.4),
			torsoCF * CFrame.new(-2.0, 1.1, 0),
			headColor:Lerp(Color3.new(0, 0, 0), 0.15),
			torso.rarity,
			anchored,
			nil
		)
		makeBlock(
			model,
			"PauldronR",
			Vector3.new(1.2, 0.7, 1.4),
			torsoCF * CFrame.new(2.0, 1.1, 0),
			headColor:Lerp(Color3.new(0, 0, 0), 0.15),
			torso.rarity,
			anchored,
			nil
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

	for i, chip in loadout.chips do
		local c = chip :: Catalog.CatalogPart
		local x = -0.55 + (i - 1) * 0.7
		local chipCF = torsoCF * CFrame.new(x, 0.4, 1.35)
		local chipAsset = tryAssetClone(chip.id)
		if chipAsset and chipAsset:IsA("Model") then
			chipAsset.Name = "Chip_" .. tostring(i) .. "_" .. chip.id
			polishAuthoredModel(chipAsset, chip.rarity, teamTint, anchored)
			chipAsset.Parent = model
			chipAsset:PivotTo(chipCF)
		else
			local color = tint((c.visual and c.visual.color) or Color3.fromRGB(80, 100, 80), teamTint)
			makeBlock(
				model,
				"Chip_" .. tostring(i),
				Vector3.new(0.45, 0.2, 0.35),
				chipCF,
				color,
				chip.rarity,
				anchored,
				nil
			)
		end
	end

	-- Prefer authored torso Root as mech PrimaryPart for PivotTo.
	local torsoChild = if loadout.torso then model:FindFirstChild("Torso_" .. loadout.torso.id) else nil
	if torsoChild and torsoChild:IsA("Model") then
		local root = torsoChild:FindFirstChild("Root")
		if root and root:IsA("BasePart") then
			model.PrimaryPart = root
		elseif torsoChild.PrimaryPart then
			model.PrimaryPart = torsoChild.PrimaryPart
		end
	elseif torsoChild and torsoChild:IsA("BasePart") then
		model.PrimaryPart = torsoChild
	else
		local any = model:FindFirstChildWhichIsA("BasePart", true)
		if any then
			model.PrimaryPart = any
		end
	end

	model:SetAttribute("Assembled", true)
	if loadout.torso then
		model:SetAttribute("TorsoId", loadout.torso.id)
	end
	model:SetAttribute("UsesPartModels", ReplicatedStorage:FindFirstChild("AssemblerAssets") ~= nil)

	return model
end

function Assembler.loadoutToIds(loadout: Slots.EquippedLoadout): { [string]: any }
	local function idOf(p: Slots.PartDef?): string?
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

function Assembler.loadoutFromIds(ids: { [string]: any }): Slots.EquippedLoadout
	local function req(id: any): Slots.PartDef?
		if typeof(id) ~= "string" then
			return nil
		end
		return Catalog.require(id)
	end
	local function weapon(id: any, slot: Slots.SlotKind): Slots.PartDef?
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

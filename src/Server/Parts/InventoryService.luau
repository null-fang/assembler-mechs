-- Inventory + equip. Starter grants a complete basic mech on Primary.

local SoftSlots = require(game.ReplicatedStorage.Shared.Parts.Slots)
local SoftStarter = require(game.ReplicatedStorage.Shared.Parts.StarterMech)
local Catalog = require(game.ReplicatedStorage.Shared.Parts.Catalog)
local Assembler = require(game.ReplicatedStorage.Shared.Assembler.Assembler)

local InventoryService = {}

export type OwnedPart = {
	uid: string,
	partId: string,
	equippedOn: SoftSlots.MechBaySlotId?,
	equipField: string?,
}

export type MechBay = {
	id: SoftSlots.MechBaySlotId,
	name: string,
	unlocked: boolean,
	loadout: SoftSlots.EquippedLoadout,
	equippedUids: { [string]: string },
}

export type PlayerInventory = {
	parts: { OwnedPart },
	bays: { [SoftSlots.MechBaySlotId]: MechBay },
	activeBay: SoftSlots.MechBaySlotId,
	starterGranted: boolean,
	nextUid: number,
}

local inventories: { [number]: PlayerInventory } = {}

local function newUid(inv: PlayerInventory): string
	local id = ("p-%d"):format(inv.nextUid)
	inv.nextUid += 1
	return id
end

local function makeBay(id: SoftSlots.MechBaySlotId, unlocked: boolean): MechBay
	return {
		id = id,
		name = id,
		unlocked = unlocked,
		loadout = SoftSlots.emptyLoadout(),
		equippedUids = {},
	}
end

function InventoryService.get(userId: number): PlayerInventory
	local inv = inventories[userId]
	if not inv then
		inv = {
			parts = {},
			bays = {
				Primary = makeBay("Primary", true),
				Secondary = makeBay("Secondary", false),
				Tertiary = makeBay("Tertiary", false),
			},
			activeBay = "Primary",
			starterGranted = false,
			nextUid = 1,
		}
		inventories[userId] = inv
	end
	return inv
end

local function findOwned(inv: PlayerInventory, uid: string): OwnedPart?
	for _, p in inv.parts do
		if p.uid == uid then
			return p
		end
	end
	return nil
end

local function bagClone(inv: PlayerInventory, partId: string): OwnedPart
	local owned: OwnedPart = {
		uid = newUid(inv),
		partId = partId,
		equippedOn = nil,
		equipField = nil,
	}
	table.insert(inv.parts, owned)
	return owned
end

local function clearEquipMark(inv: PlayerInventory, uid: string)
	local owned = findOwned(inv, uid)
	if owned then
		owned.equippedOn = nil
		owned.equipField = nil
	end
end

local function setEquipMark(inv: PlayerInventory, uid: string, bayId: SoftSlots.MechBaySlotId, field: string)
	local owned = findOwned(inv, uid)
	if owned then
		owned.equippedOn = bayId
		owned.equipField = field
	end
end

local function rebuildChipMarks(inv: PlayerInventory, bay: MechBay, chipUids: { string })
	for k in bay.equippedUids do
		if string.sub(k, 1, 5) == "chip:" then
			bay.equippedUids[k] = nil
		end
	end
	for i, uid in chipUids do
		local field = "chip:" .. tostring(i)
		bay.equippedUids[field] = uid
		setEquipMark(inv, uid, bay.id, field)
	end
end

local function unequipField(inv: PlayerInventory, bay: MechBay, field: string)
	if string.sub(field, 1, 5) == "chip:" then
		local idx = tonumber(string.sub(field, 6))
		if not idx then
			return
		end
		local chipUids = {}
		for i, chip in bay.loadout.chips do
			local f = "chip:" .. tostring(i)
			local uid = bay.equippedUids[f]
			if i ~= idx and chip and uid then
				table.insert(chipUids, uid)
			elseif i == idx and uid then
				clearEquipMark(inv, uid)
			end
		end
		local newChips = {}
		for i, chip in bay.loadout.chips do
			if i ~= idx then
				table.insert(newChips, chip)
			end
		end
		bay.loadout.chips = newChips
		rebuildChipMarks(inv, bay, chipUids)
		return
	end

	local prevUid = bay.equippedUids[field]
	if prevUid then
		clearEquipMark(inv, prevUid)
		bay.equippedUids[field] = nil
	end
	(bay.loadout :: any)[field] = nil
end

function InventoryService.grantStarter(userId: number)
	local inv = InventoryService.get(userId)
	if inv.starterGranted then
		return
	end

	local uidByPartId: { [string]: string } = {}
	for _, partId in SoftStarter.GRANT_IDS do
		local owned = bagClone(inv, partId)
		if not uidByPartId[partId] then
			uidByPartId[partId] = owned.uid
		end
	end

	local bay = inv.bays.Primary
	bay.loadout = SoftSlots.emptyLoadout()
	bay.equippedUids = {}

	local function bind(field: string, partId: string, slotOverride: SoftSlots.SlotKind?)
		local uid = uidByPartId[partId]
		if not uid then
			return
		end
		local placed: SoftSlots.PartDef
		if slotOverride then
			placed = Catalog.asWeapon(partId, slotOverride)
		else
			placed = Catalog.require(partId)
		end
		(bay.loadout :: any)[field] = placed
		bay.equippedUids[field] = uid
		setEquipMark(inv, uid, "Primary", field)
	end

	bind("torso", "rusty_cage")
	bind("leftLeg", "workboot_l")
	bind("rightLeg", "workboot_r")
	bind("lowerLeft", "snap_arm", "LowerLeft")
	bind("lowerRight", "rivet_gun", "LowerRight")
	bind("shoulderRight", "brick_shoulder", "ShoulderRight")
	bind("battery", "desk_brick")
	bind("cpu", "scrap_cpu")
	bind("drone", "floor_bit")

	bay.loadout.chips = {
		Catalog.require("thick_skin"),
		Catalog.require("heat_sink_chip"),
	}
	rebuildChipMarks(inv, bay, {
		uidByPartId["thick_skin"],
		uidByPartId["heat_sink_chip"],
	})

	inv.activeBay = "Primary"
	inv.starterGranted = true
end

function InventoryService.activeLoadout(userId: number): SoftSlots.EquippedLoadout
	local inv = InventoryService.get(userId)
	if not inv.starterGranted then
		InventoryService.grantStarter(userId)
		inv = InventoryService.get(userId)
	end
	return inv.bays[inv.activeBay].loadout
end

function InventoryService.equip(userId: number, uid: string, target: string): (boolean, string?)
	local inv = InventoryService.get(userId)
	local owned = findOwned(inv, uid)
	if not owned then
		return false, "Part not owned"
	end
	local catalogPart = Catalog.require(owned.partId)
	local bay = inv.bays[inv.activeBay]
	if not bay.unlocked then
		return false, "Bay locked"
	end
	if owned.equippedOn and owned.equippedOn ~= inv.activeBay then
		return false, "Equipped on another mech"
	end

	-- Chip path
	if target == "Chip" or string.sub(target, 1, 5) == "chip:" then
		if catalogPart.slot ~= "Chip" then
			return false, "Not a chip"
		end
		if owned.equipField then
			unequipField(inv, bay, owned.equipField)
		end
		if #bay.loadout.chips >= SoftSlots.MAX_CHIPS then
			return false, "Chip slots full"
		end
		local chipUids = {}
		for i = 1, #bay.loadout.chips do
			table.insert(chipUids, bay.equippedUids["chip:" .. tostring(i)])
		end
		table.insert(bay.loadout.chips, Catalog.require(owned.partId))
		table.insert(chipUids, uid)
		rebuildChipMarks(inv, bay, chipUids)
		return true, nil
	end

	local field = target
	local slotKind = SoftSlots.slotForField(field)
	if not slotKind then
		return false, "Bad slot"
	end
	if not SoftSlots.canOccupy(catalogPart, slotKind) then
		return false, "Wrong slot"
	end

	if owned.equipField and owned.equipField ~= field then
		unequipField(inv, bay, owned.equipField)
	end
	unequipField(inv, bay, field)

	local placed: SoftSlots.PartDef
	if SoftSlots.isLowerSlot(slotKind) or SoftSlots.isShoulderSlot(slotKind) then
		placed = Catalog.asWeapon(owned.partId, slotKind)
	else
		placed = Catalog.require(owned.partId)
	end
	(bay.loadout :: any)[field] = placed
	bay.equippedUids[field] = uid
	setEquipMark(inv, uid, inv.activeBay, field)
	return true, nil
end

function InventoryService.unequip(userId: number, field: string): (boolean, string?)
	local inv = InventoryService.get(userId)
	local bay = inv.bays[inv.activeBay]
	if string.sub(field, 1, 5) == "chip:" then
		if not bay.equippedUids[field] then
			return false, "Empty"
		end
		unequipField(inv, bay, field)
		return true, nil
	end
	if not bay.equippedUids[field] and (bay.loadout :: any)[field] == nil then
		return false, "Empty"
	end
	unequipField(inv, bay, field)
	return true, nil
end

function InventoryService.loadoutSummary(userId: number)
	local loadout = InventoryService.activeLoadout(userId)
	local function nameOf(part)
		return if part then part.name else nil
	end
	return {
		torso = nameOf(loadout.torso),
		legs = (nameOf(loadout.leftLeg) or "?") .. " / " .. (nameOf(loadout.rightLeg) or "?"),
		lowerLeft = nameOf(loadout.lowerLeft),
		lowerRight = nameOf(loadout.lowerRight),
		shoulderLeft = nameOf(loadout.shoulderLeft),
		shoulderRight = nameOf(loadout.shoulderRight),
		battery = nameOf(loadout.battery),
		cpu = nameOf(loadout.cpu),
		drone = nameOf(loadout.drone),
		chips = #loadout.chips,
		legal = SoftStarter.isLegal(loadout),
		weight = SoftSlots.sumWeight(loadout),
		bay = InventoryService.get(userId).activeBay,
		ids = Assembler.loadoutToIds(loadout),
	}
end

function InventoryService.clientSnapshot(userId: number)
	local inv = InventoryService.get(userId)
	if not inv.starterGranted then
		InventoryService.grantStarter(userId)
		inv = InventoryService.get(userId)
	end
	local bay = inv.bays[inv.activeBay]
	local owned = {}
	for _, p in inv.parts do
		local cat = Catalog.require(p.partId)
		table.insert(owned, {
			uid = p.uid,
			partId = p.partId,
			equippedOn = p.equippedOn,
			equipField = p.equipField,
			summary = Catalog.summary(cat),
		})
	end
	local equipped = {}
	for field, uid in bay.equippedUids do
		equipped[field] = uid
	end
	return {
		activeBay = inv.activeBay,
		bays = {
			{ id = "Primary", name = "Primary", unlocked = inv.bays.Primary.unlocked },
			{ id = "Secondary", name = "Secondary", unlocked = inv.bays.Secondary.unlocked },
			{ id = "Tertiary", name = "Tertiary", unlocked = inv.bays.Tertiary.unlocked },
		},
		owned = owned,
		equipped = equipped,
		loadout = InventoryService.loadoutSummary(userId),
		loadoutIds = Assembler.loadoutToIds(bay.loadout),
		maxChips = SoftSlots.MAX_CHIPS,
	}
end

InventoryService.DEFAULT_CHASSIS_CAPACITY = {
	weightCapacity = 110,
}

return InventoryService

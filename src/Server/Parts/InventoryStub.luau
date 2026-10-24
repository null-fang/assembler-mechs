-- Parts inventory. Grants starter mech on first touch.

local SoftSlots = require(game.ReplicatedStorage.Shared.Parts.Slots)
local SoftCrate = require(game.ReplicatedStorage.Shared.Parts.CratePick3)
local SoftStarter = require(game.ReplicatedStorage.Shared.Parts.StarterMech)

local InventoryStub = {}

local inventories = {}

local function emptyLoadout()
	return {
		torso = nil,
		leftLeg = nil,
		rightLeg = nil,
		lowerLeft = nil,
		lowerRight = nil,
		shoulderLeft = nil,
		shoulderRight = nil,
		chips = {},
		battery = nil,
		cpu = nil,
		drone = nil,
	}
end

local function bagPart(inv, part)
	if part then
		table.insert(inv.parts, part)
	end
end

function InventoryStub.get(userId)
	local inv = inventories[userId]
	if not inv then
		inv = {
			parts = {},
			loadout = emptyLoadout(),
			starterGranted = false,
		}
		inventories[userId] = inv
	end
	return inv
end

function InventoryStub.grantStarter(userId)
	local inv = InventoryStub.get(userId)
	if inv.starterGranted then
		return
	end
	local loadout = SoftStarter.buildLoadout()
	inv.loadout = loadout
	bagPart(inv, loadout.torso)
	bagPart(inv, loadout.leftLeg)
	bagPart(inv, loadout.rightLeg)
	bagPart(inv, loadout.lowerLeft)
	bagPart(inv, loadout.lowerRight)
	bagPart(inv, loadout.shoulderLeft)
	bagPart(inv, loadout.shoulderRight)
	bagPart(inv, loadout.battery)
	bagPart(inv, loadout.cpu)
	bagPart(inv, loadout.drone)
	for _, chip in loadout.chips do
		table.insert(inv.parts, chip)
	end
	inv.starterGranted = true
end

function InventoryStub.applyCratePick(userId, result)
	local inv = InventoryStub.get(userId)
	table.insert(inv.parts, result.chosen)
end

function InventoryStub.loadoutSummary(userId)
	local inv = InventoryStub.get(userId)
	if not inv.starterGranted then
		InventoryStub.grantStarter(userId)
		inv = InventoryStub.get(userId)
	end
	local lo = inv.loadout
	local function nameOf(part)
		return if part then part.name else nil
	end
	return {
		torso = nameOf(lo.torso),
		legs = (nameOf(lo.leftLeg) or "?") .. " / " .. (nameOf(lo.rightLeg) or "?"),
		lowerLeft = nameOf(lo.lowerLeft),
		lowerRight = nameOf(lo.lowerRight),
		shoulderLeft = nameOf(lo.shoulderLeft),
		shoulderRight = nameOf(lo.shoulderRight),
		battery = nameOf(lo.battery),
		cpu = nameOf(lo.cpu),
		drone = nameOf(lo.drone),
		chips = #lo.chips,
		legal = SoftStarter.isLegal(lo),
		weight = SoftSlots.sumWeight(lo),
	}
end

InventoryStub.DEFAULT_CHASSIS_CAPACITY = {
	weightCapacity = 110,
}

-- Keep CratePick3 referenced for future wiring.
local _ = SoftCrate

return InventoryStub

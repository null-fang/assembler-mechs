-- Parts inventory stub. Wire crate picks + equip + sell here later.

local Slots = require(game.ReplicatedStorage.Shared.Parts.Slots)
local CratePick3 = require(game.ReplicatedStorage.Shared.Parts.CratePick3)

local InventoryStub = {}

export type PlayerInventory = {
	parts: { Slots.PartDef },
	loadout: Slots.EquippedLoadout,
}

local inventories: { [number]: PlayerInventory } = {}

function InventoryStub.get(userId: number): PlayerInventory
	local inv = inventories[userId]
	if not inv then
		inv = {
			parts = {},
			loadout = {
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
			},
		}
		inventories[userId] = inv
	end
	return inv
end

function InventoryStub.applyCratePick(userId: number, result: CratePick3.CratePickResult)
	local inv = InventoryStub.get(userId)
	table.insert(inv.parts, result.chosen)
end

-- Chassis capacity stub for overweight checks (soft penalty preferred).
InventoryStub.DEFAULT_CHASSIS_CAPACITY = {
	weightCapacity = 100,
} :: Slots.ChassisCapacity

return InventoryStub

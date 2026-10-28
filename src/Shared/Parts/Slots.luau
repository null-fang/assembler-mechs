-- Part slots + weight fields. Chassis capacity stub for overweight checks.

export type SlotKind =
	"Torso"
	| "LeftLeg"
	| "RightLeg"
	| "LowerLeft" -- arm / close weapon
	| "LowerRight"
	| "ShoulderLeft" -- top / longer range
	| "ShoulderRight"
	| "Chip"
	| "Battery"
	| "CPU"
	| "Drone"

-- Lower vs shoulder are not interchangeable.
-- Dual-leg specials (spider/treads) occupy both leg slots — handled later.

export type PartRarity = "Common" | "Uncommon" | "Rare" | "Epic" | "Legendary" | "Mythic" | "Blessed" | "Relic"

-- Soft contributions stacked onto torso baselines at fight start.
export type PartContrib = {
	integrity: number?,
	temperatureMax: number?,
	cooling: number?,
	batteryMax: number?,
	batteryRegen: number?,
}

-- Visual hints for the Assembler (low-poly blocks).
export type PartVisual = {
	color: Color3,
	-- Optional size override (studs). Defaults come from socket templates.
	size: Vector3?,
}

export type PartDef = {
	id: string,
	name: string,
	slot: SlotKind,
	rarity: PartRarity,
	weight: number, -- every part has weight (SuperMechs-like)
	-- Sell stub: common-currency worth when selling duplicates.
	sellWorth: number,
	level: number?,
	tooltip: string?,
	contrib: PartContrib?,
	visual: PartVisual?,
	-- Legs: matched biped rules (same type; same variant required).
	legType: string?, -- e.g. "biped"
	legVariant: string?, -- e.g. "workboot" / "sprint" — L/R cannot mix variants
	-- Weapons: which mount class they belong to (Lower ≠ Shoulder).
	mountClass: ("Lower" | "Shoulder")?,
}

export type ChassisCapacity = {
	weightCapacity: number, -- soft-cap reference; soft penalty preferred when over
}

export type EquippedLoadout = {
	torso: PartDef?,
	leftLeg: PartDef?,
	rightLeg: PartDef?,
	lowerLeft: PartDef?,
	lowerRight: PartDef?,
	shoulderLeft: PartDef?,
	shoulderRight: PartDef?,
	chips: { PartDef }, -- first slice: 2–4
	battery: PartDef?,
	cpu: PartDef?,
	drone: PartDef?,
}

-- Mech bay slots (3 lives in PvP later). First slice uses Primary only.
export type MechBaySlotId = "Primary" | "Secondary" | "Tertiary"

local Slots = {}

Slots.MECH_BAY_SLOTS = { "Primary", "Secondary", "Tertiary" } :: { MechBaySlotId }
Slots.MAX_CHIPS = 2 -- first slice

Slots.LOADOUT_FIELDS = {
	"torso",
	"leftLeg",
	"rightLeg",
	"lowerLeft",
	"lowerRight",
	"shoulderLeft",
	"shoulderRight",
	"battery",
	"cpu",
	"drone",
} :: { string }

function Slots.emptyLoadout(): EquippedLoadout
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

function Slots.sumWeight(loadout: EquippedLoadout): number
	local total = 0
	local function add(part: PartDef?)
		if part then
			total += part.weight
		end
	end
	add(loadout.torso)
	add(loadout.leftLeg)
	add(loadout.rightLeg)
	add(loadout.lowerLeft)
	add(loadout.lowerRight)
	add(loadout.shoulderLeft)
	add(loadout.shoulderRight)
	add(loadout.battery)
	add(loadout.cpu)
	add(loadout.drone)
	for _, chip in loadout.chips do
		total += chip.weight
	end
	return total
end

function Slots.sumContrib(loadout: EquippedLoadout): PartContrib
	local out: PartContrib = {
		integrity = 0,
		temperatureMax = 0,
		cooling = 0,
		batteryMax = 0,
		batteryRegen = 0,
	}
	local function fold(part: PartDef?)
		if not part or not part.contrib then
			return
		end
		local c = part.contrib
		out.integrity = (out.integrity or 0) + (c.integrity or 0)
		out.temperatureMax = (out.temperatureMax or 0) + (c.temperatureMax or 0)
		out.cooling = (out.cooling or 0) + (c.cooling or 0)
		out.batteryMax = (out.batteryMax or 0) + (c.batteryMax or 0)
		out.batteryRegen = (out.batteryRegen or 0) + (c.batteryRegen or 0)
	end
	fold(loadout.torso)
	fold(loadout.leftLeg)
	fold(loadout.rightLeg)
	fold(loadout.lowerLeft)
	fold(loadout.lowerRight)
	fold(loadout.shoulderLeft)
	fold(loadout.shoulderRight)
	fold(loadout.battery)
	fold(loadout.cpu)
	fold(loadout.drone)
	for _, chip in loadout.chips do
		fold(chip)
	end
	return out
end

function Slots.slotForField(field: string): SlotKind?
	local map = {
		torso = "Torso",
		leftLeg = "LeftLeg",
		rightLeg = "RightLeg",
		lowerLeft = "LowerLeft",
		lowerRight = "LowerRight",
		shoulderLeft = "ShoulderLeft",
		shoulderRight = "ShoulderRight",
		battery = "Battery",
		cpu = "CPU",
		drone = "Drone",
	}
	return map[field]
end

function Slots.fieldForSlot(slot: SlotKind): string?
	local map = {
		Torso = "torso",
		LeftLeg = "leftLeg",
		RightLeg = "rightLeg",
		LowerLeft = "lowerLeft",
		LowerRight = "lowerRight",
		ShoulderLeft = "shoulderLeft",
		ShoulderRight = "shoulderRight",
		Battery = "battery",
		CPU = "cpu",
		Drone = "drone",
	}
	return map[slot]
end

function Slots.isLowerSlot(slot: SlotKind): boolean
	return slot == "LowerLeft" or slot == "LowerRight"
end

function Slots.isShoulderSlot(slot: SlotKind): boolean
	return slot == "ShoulderLeft" or slot == "ShoulderRight"
end

-- Can this catalog part occupy the target equip slot?
function Slots.canOccupy(part: PartDef, targetSlot: SlotKind): boolean
	if part.slot == "Chip" then
		return targetSlot == "Chip"
	end
	if part.mountClass == "Lower" then
		return Slots.isLowerSlot(targetSlot)
	end
	if part.mountClass == "Shoulder" then
		return Slots.isShoulderSlot(targetSlot)
	end
	return part.slot == targetSlot
end

-- Matched biped: same type + same variant on L/R.
function Slots.legsCompatible(left: PartDef?, right: PartDef?): boolean
	if not left or not right then
		return false
	end
	if left.legType ~= right.legType then
		return false
	end
	if left.legVariant ~= right.legVariant then
		return false
	end
	return true
end

return Slots

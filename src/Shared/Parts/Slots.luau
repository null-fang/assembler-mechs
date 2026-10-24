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

export type PartDef = {
	id: string,
	name: string,
	slot: SlotKind,
	rarity: PartRarity,
	weight: number, -- every part has weight (SuperMechs-like)
	-- Sell stub: common-currency worth when selling duplicates.
	sellWorth: number,
	level: number?,
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

local Slots = {}

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

return Slots

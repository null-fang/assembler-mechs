-- Minimal part catalog for the first combat slice.
-- Names: short, worn, human — not epic-poem.

local Slots = require(script.Parent.Slots)
local Types = require(script.Parent.Parent.Combat.Types)

export type CatalogPart = Slots.PartDef & {
	tooltip: string,
	-- Optional combat payloads (present when relevant to slot).
	torsoStats: {
		integrity: number,
		temperatureMax: number,
		cooling: number,
		batteryMax: number,
		batteryRegen: number,
		weightCapacity: number,
		resistPhysical: number,
		resistHeat: number,
		resistEnergy: number,
	}?,
	legStats: {
		moveRange: number,
	}?,
	weaponStats: Types.WeaponStats?,
	chipStats: {
		resistPhysical: number?,
		resistHeat: number?,
		resistEnergy: number?,
		coolingBonus: number?,
		integrityBonus: number?,
	}?,
	batteryStats: {
		batteryMaxBonus: number,
		batteryRegenBonus: number,
	}?,
	cpuStats: {
		-- Soft stub: processing gate for software later.
		tier: number,
	}?,
	droneStats: Types.DroneStats?,
}

local function part(def: CatalogPart): CatalogPart
	return def
end

local Catalog = {}

Catalog.parts = {
	-- Chassis
	rusty_cage = part({
		id = "rusty_cage",
		name = "Rusty Cage",
		slot = "Torso",
		rarity = "Common",
		weight = 28,
		sellWorth = 40,
		level = 1,
		tooltip = "Beaten frame. Holds together.",
		torsoStats = {
			integrity = 220,
			temperatureMax = 100,
			cooling = 18,
			batteryMax = 80,
			batteryRegen = 12,
			weightCapacity = 110,
			resistPhysical = 4,
			resistHeat = 2,
			resistEnergy = 2,
		},
	}),
	plate_box = part({
		id = "plate_box",
		name = "Plate Box",
		slot = "Torso",
		rarity = "Uncommon",
		weight = 34,
		sellWorth = 70,
		level = 1,
		tooltip = "Heavier shell. Cooler head.",
		torsoStats = {
			integrity = 280,
			temperatureMax = 110,
			cooling = 22,
			batteryMax = 90,
			batteryRegen = 14,
			weightCapacity = 125,
			resistPhysical = 8,
			resistHeat = 4,
			resistEnergy = 3,
		},
	}),

	-- Legs (matched biped pair — same id family, L/R copies)
	workboot_l = part({
		id = "workboot_l",
		name = "Workboot Stride L",
		slot = "LeftLeg",
		rarity = "Common",
		weight = 10,
		sellWorth = 20,
		level = 1,
		tooltip = "Steady walk. Two tiles a step.",
		legStats = { moveRange = 2 },
	}),
	workboot_r = part({
		id = "workboot_r",
		name = "Workboot Stride R",
		slot = "RightLeg",
		rarity = "Common",
		weight = 10,
		sellWorth = 20,
		level = 1,
		tooltip = "Steady walk. Two tiles a step.",
		legStats = { moveRange = 2 },
	}),
	sprint_peg_l = part({
		id = "sprint_peg_l",
		name = "Sprint Peg L",
		slot = "LeftLeg",
		rarity = "Uncommon",
		weight = 8,
		sellWorth = 35,
		level = 1,
		tooltip = "Light legs. Three tiles a step.",
		legStats = { moveRange = 3 },
	}),
	sprint_peg_r = part({
		id = "sprint_peg_r",
		name = "Sprint Peg R",
		slot = "RightLeg",
		rarity = "Uncommon",
		weight = 8,
		sellWorth = 35,
		level = 1,
		tooltip = "Light legs. Three tiles a step.",
		legStats = { moveRange = 3 },
	}),

	-- Lower / arm weapons (close / mid)
	snap_arm = part({
		id = "snap_arm",
		name = "Snap Arm",
		slot = "LowerLeft", -- catalog template; equip copies assign side
		rarity = "Common",
		weight = 8,
		sellWorth = 25,
		level = 1,
		tooltip = "Short physical slap. Cheap on the pack.",
		weaponStats = {
			damageType = "Physical",
			damage = 28,
			heatCost = 4,
			batteryCost = 0,
			rangeMin = 1,
			rangeMax = 2,
			apCost = 1,
			tooltip = "Physical. Range 1–2. No battery.",
		},
	}),
	rivet_gun = part({
		id = "rivet_gun",
		name = "Rivet Gun",
		slot = "LowerRight",
		rarity = "Common",
		weight = 9,
		sellWorth = 28,
		level = 1,
		tooltip = "Mechanical chatter. Close in.",
		weaponStats = {
			damageType = "Physical",
			damage = 22,
			heatCost = 2,
			batteryCost = 0,
			rangeMin = 1,
			rangeMax = 3,
			apCost = 1,
			tooltip = "Physical. Range 1–3. No battery.",
		},
	}),
	ember_fist = part({
		id = "ember_fist",
		name = "Ember Fist",
		slot = "LowerLeft",
		rarity = "Uncommon",
		weight = 10,
		sellWorth = 45,
		level = 1,
		tooltip = "Hot punch. Cooks both of you a bit.",
		weaponStats = {
			damageType = "Heat",
			damage = 20,
			heatCost = 14,
			batteryCost = 4,
			rangeMin = 1,
			rangeMax = 2,
			apCost = 1,
			tooltip = "Heat. Range 1–2. Warms the core.",
		},
	}),

	-- Shoulder / top weapons (longer)
	brick_shoulder = part({
		id = "brick_shoulder",
		name = "Brick Shoulder",
		slot = "ShoulderRight",
		rarity = "Common",
		weight = 14,
		sellWorth = 30,
		level = 1,
		tooltip = "Heavy physical lob. Needs room.",
		weaponStats = {
			damageType = "Physical",
			damage = 36,
			heatCost = 6,
			batteryCost = 0,
			rangeMin = 2,
			rangeMax = 5,
			apCost = 1,
			tooltip = "Physical. Range 2–5.",
		},
	}),
	arc_rail = part({
		id = "arc_rail",
		name = "Arc Rail",
		slot = "ShoulderLeft",
		rarity = "Uncommon",
		weight = 12,
		sellWorth = 50,
		level = 1,
		tooltip = "Energy lance. Dies when the pack is empty.",
		weaponStats = {
			damageType = "Energy",
			damage = 32,
			heatCost = 3,
			batteryCost = 18,
			rangeMin = 2,
			rangeMax = 6,
			apCost = 1,
			tooltip = "Energy. Range 2–6. Needs battery.",
		},
	}),
	long_bite = part({
		id = "long_bite",
		name = "Long Bite",
		slot = "ShoulderRight",
		rarity = "Rare",
		weight = 15,
		sellWorth = 80,
		level = 1,
		tooltip = "Far heat spit. Don't cook yourself.",
		weaponStats = {
			damageType = "Heat",
			damage = 30,
			heatCost = 20,
			batteryCost = 8,
			rangeMin = 3,
			rangeMax = 7,
			apCost = 1,
			tooltip = "Heat. Range 3–7. Hot barrel.",
		},
	}),

	-- Chips
	thick_skin = part({
		id = "thick_skin",
		name = "Chip: Thick Skin",
		slot = "Chip",
		rarity = "Common",
		weight = 2,
		sellWorth = 15,
		level = 1,
		tooltip = "Soaks a little physical.",
		chipStats = { resistPhysical = 6, integrityBonus = 15 },
	}),
	heat_sink_chip = part({
		id = "heat_sink_chip",
		name = "Chip: Sink Pad",
		slot = "Chip",
		rarity = "Common",
		weight = 2,
		sellWorth = 15,
		level = 1,
		tooltip = "Extra cooling tick.",
		chipStats = { coolingBonus = 6, resistHeat = 4 },
	}),
	wire_wrap = part({
		id = "wire_wrap",
		name = "Chip: Wire Wrap",
		slot = "Chip",
		rarity = "Uncommon",
		weight = 2,
		sellWorth = 25,
		level = 1,
		tooltip = "Blunts energy hits.",
		chipStats = { resistEnergy = 8 },
	}),

	-- Battery / CPU
	desk_brick = part({
		id = "desk_brick",
		name = "Desk Brick Battery",
		slot = "Battery",
		rarity = "Common",
		weight = 6,
		sellWorth = 20,
		level = 1,
		tooltip = "Office surplus. Keeps the lights on.",
		batteryStats = { batteryMaxBonus = 20, batteryRegenBonus = 4 },
	}),
	bay_cell = part({
		id = "bay_cell",
		name = "Bay Cell",
		slot = "Battery",
		rarity = "Uncommon",
		weight = 7,
		sellWorth = 40,
		level = 1,
		tooltip = "Bigger pack. Faster trickle.",
		batteryStats = { batteryMaxBonus = 35, batteryRegenBonus = 8 },
	}),
	scrap_cpu = part({
		id = "scrap_cpu",
		name = "Scrap CPU",
		slot = "CPU",
		rarity = "Common",
		weight = 3,
		sellWorth = 18,
		level = 1,
		tooltip = "Runs the basics. Software later.",
		cpuStats = { tier = 1 },
	}),

	-- Drone (optional)
	floor_bit = part({
		id = "floor_bit",
		name = "Floor Bit",
		slot = "Drone",
		rarity = "Common",
		weight = 5,
		sellWorth = 22,
		level = 1,
		tooltip = "Wheeled pest. Fires after your turn.",
		droneStats = {
			damageType = "Physical",
			damage = 12,
			heatCost = 0,
			batteryCost = 2,
			rangeMax = 4,
			tooltip = "End of turn. Physical. Range ≤4.",
		},
	}),
	spark_moth = part({
		id = "spark_moth",
		name = "Spark Moth",
		slot = "Drone",
		rarity = "Uncommon",
		weight = 4,
		sellWorth = 40,
		level = 1,
		tooltip = "Air spark. Nips battery foes.",
		droneStats = {
			damageType = "Energy",
			damage = 14,
			heatCost = 2,
			batteryCost = 6,
			rangeMax = 5,
			tooltip = "End of turn. Energy. Range ≤5.",
		},
	}),
} :: { [string]: CatalogPart }

function Catalog.get(id: string): CatalogPart?
	return Catalog.parts[id]
end

function Catalog.require(id: string): CatalogPart
	local p = Catalog.parts[id]
	assert(p, ("Unknown part id: %s"):format(id))
	return p
end

-- Clone a catalog weapon into a specific lower/shoulder slot.
function Catalog.asWeapon(id: string, slot: Slots.SlotKind): CatalogPart
	local base = Catalog.require(id)
	local clone: CatalogPart = table.clone(base)
	clone.slot = slot
	if base.weaponStats then
		clone.weaponStats = table.clone(base.weaponStats)
	end
	return clone
end

return Catalog

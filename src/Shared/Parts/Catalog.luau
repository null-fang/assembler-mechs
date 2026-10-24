-- Part catalog for the first combat slice (common–rare).
-- Names: short, worn, human — not epic-poem.

local Slots = require(script.Parent.Slots)
local Types = require(script.Parent.Parent.Combat.Types)

export type CatalogPart = Slots.PartDef & {
	tooltip: string,
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
		tier: number,
	}?,
	droneStats: Types.DroneStats?,
}

local function rgb(r: number, g: number, b: number): Color3
	return Color3.fromRGB(r, g, b)
end

local function part(def: CatalogPart): CatalogPart
	return def
end

local Catalog = {}

Catalog.parts = {
	-- ── Chassis / Torso ──────────────────────────────────────────────
	rusty_cage = part({
		id = "rusty_cage",
		name = "Rusty Cage",
		slot = "Torso",
		rarity = "Common",
		weight = 28,
		sellWorth = 40,
		level = 1,
		tooltip = "Beaten frame. Holds together.",
		contrib = { integrity = 220, temperatureMax = 100, cooling = 18, batteryMax = 80, batteryRegen = 12 },
		visual = { color = rgb(140, 96, 72), size = Vector3.new(4.2, 3.2, 2.6) },
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
		contrib = { integrity = 280, temperatureMax = 110, cooling = 22, batteryMax = 90, batteryRegen = 14 },
		visual = { color = rgb(92, 104, 118), size = Vector3.new(4.4, 3.4, 2.8) },
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
	tin_can = part({
		id = "tin_can",
		name = "Tin Can",
		slot = "Torso",
		rarity = "Rare",
		weight = 26,
		sellWorth = 95,
		level = 1,
		tooltip = "Light shell. Pack breathes easier.",
		contrib = { integrity = 240, temperatureMax = 105, cooling = 20, batteryMax = 100, batteryRegen = 16 },
		visual = { color = rgb(168, 174, 160), size = Vector3.new(3.8, 3.0, 2.4) },
		torsoStats = {
			integrity = 240,
			temperatureMax = 105,
			cooling = 20,
			batteryMax = 100,
			batteryRegen = 16,
			weightCapacity = 118,
			resistPhysical = 3,
			resistHeat = 5,
			resistEnergy = 6,
		},
	}),

	-- ── Legs (matched biped — same type + variant) ───────────────────
	workboot_l = part({
		id = "workboot_l",
		name = "Workboot Stride L",
		slot = "LeftLeg",
		rarity = "Common",
		weight = 10,
		sellWorth = 20,
		level = 1,
		tooltip = "Steady walk. Two tiles a step.",
		legType = "biped",
		legVariant = "workboot",
		contrib = { integrity = 8, cooling = 1 },
		visual = { color = rgb(78, 62, 48), size = Vector3.new(1.4, 2.8, 1.6) },
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
		legType = "biped",
		legVariant = "workboot",
		contrib = { integrity = 8, cooling = 1 },
		visual = { color = rgb(78, 62, 48), size = Vector3.new(1.4, 2.8, 1.6) },
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
		legType = "biped",
		legVariant = "sprint",
		contrib = { integrity = 4 },
		visual = { color = rgb(110, 88, 54), size = Vector3.new(1.1, 3.2, 1.2) },
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
		legType = "biped",
		legVariant = "sprint",
		contrib = { integrity = 4 },
		visual = { color = rgb(110, 88, 54), size = Vector3.new(1.1, 3.2, 1.2) },
		legStats = { moveRange = 3 },
	}),
	stump_l = part({
		id = "stump_l",
		name = "Stump Walker L",
		slot = "LeftLeg",
		rarity = "Rare",
		weight = 14,
		sellWorth = 55,
		level = 1,
		tooltip = "Heavy feet. Hard to shove. Slow.",
		legType = "biped",
		legVariant = "stump",
		contrib = { integrity = 18, temperatureMax = 4 },
		visual = { color = rgb(64, 58, 52), size = Vector3.new(1.8, 2.2, 1.8) },
		legStats = { moveRange = 1 },
	}),
	stump_r = part({
		id = "stump_r",
		name = "Stump Walker R",
		slot = "RightLeg",
		rarity = "Rare",
		weight = 14,
		sellWorth = 55,
		level = 1,
		tooltip = "Heavy feet. Hard to shove. Slow.",
		legType = "biped",
		legVariant = "stump",
		contrib = { integrity = 18, temperatureMax = 4 },
		visual = { color = rgb(64, 58, 52), size = Vector3.new(1.8, 2.2, 1.8) },
		legStats = { moveRange = 1 },
	}),

	-- ── Lower / arm weapons (close / mid) ────────────────────────────
	snap_arm = part({
		id = "snap_arm",
		name = "Snap Arm",
		slot = "LowerLeft",
		rarity = "Common",
		weight = 8,
		sellWorth = 25,
		level = 1,
		tooltip = "Short physical slap. Cheap on the pack.",
		mountClass = "Lower",
		contrib = { integrity = 2 },
		visual = { color = rgb(120, 118, 110), size = Vector3.new(1.2, 1.0, 2.4) },
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
		mountClass = "Lower",
		contrib = { integrity = 2 },
		visual = { color = rgb(98, 102, 108), size = Vector3.new(1.1, 0.9, 2.6) },
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
		mountClass = "Lower",
		contrib = { cooling = -1 },
		visual = { color = rgb(196, 92, 42), size = Vector3.new(1.3, 1.2, 2.2) },
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
	needle_jab = part({
		id = "needle_jab",
		name = "Needle Jab",
		slot = "LowerLeft",
		rarity = "Rare",
		weight = 7,
		sellWorth = 60,
		level = 1,
		tooltip = "Thin energy poke. Needs juice.",
		mountClass = "Lower",
		contrib = { batteryRegen = 1 },
		visual = { color = rgb(72, 160, 188), size = Vector3.new(0.9, 0.8, 2.8) },
		weaponStats = {
			damageType = "Energy",
			damage = 26,
			heatCost = 2,
			batteryCost = 10,
			rangeMin = 1,
			rangeMax = 3,
			apCost = 1,
			tooltip = "Energy. Range 1–3. Sips battery.",
		},
	}),

	-- ── Shoulder / top weapons (longer) ──────────────────────────────
	brick_shoulder = part({
		id = "brick_shoulder",
		name = "Brick Shoulder",
		slot = "ShoulderRight",
		rarity = "Common",
		weight = 14,
		sellWorth = 30,
		level = 1,
		tooltip = "Heavy physical lob. Needs room.",
		mountClass = "Shoulder",
		contrib = { integrity = 4 },
		visual = { color = rgb(108, 100, 92), size = Vector3.new(1.8, 1.2, 2.8) },
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
		mountClass = "Shoulder",
		contrib = { batteryMax = 4 },
		visual = { color = rgb(56, 140, 196), size = Vector3.new(1.4, 1.0, 3.2) },
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
		mountClass = "Shoulder",
		contrib = { temperatureMax = 6 },
		visual = { color = rgb(204, 78, 36), size = Vector3.new(1.5, 1.1, 3.4) },
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
	slag_tube = part({
		id = "slag_tube",
		name = "Slag Tube",
		slot = "ShoulderLeft",
		rarity = "Rare",
		weight = 16,
		sellWorth = 75,
		level = 1,
		tooltip = "Ugly heat mortar. Short fuse.",
		mountClass = "Shoulder",
		contrib = { cooling = -2, integrity = 3 },
		visual = { color = rgb(160, 64, 40), size = Vector3.new(1.7, 1.4, 2.6) },
		weaponStats = {
			damageType = "Heat",
			damage = 38,
			heatCost = 24,
			batteryCost = 4,
			rangeMin = 2,
			rangeMax = 4,
			apCost = 1,
			tooltip = "Heat. Range 2–4. Cooks the barrel.",
		},
	}),

	-- ── Chips ────────────────────────────────────────────────────────
	thick_skin = part({
		id = "thick_skin",
		name = "Chip: Thick Skin",
		slot = "Chip",
		rarity = "Common",
		weight = 2,
		sellWorth = 15,
		level = 1,
		tooltip = "Soaks a little physical.",
		contrib = { integrity = 15 },
		visual = { color = rgb(90, 120, 90) },
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
		contrib = { cooling = 6 },
		visual = { color = rgb(90, 110, 140) },
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
		contrib = { batteryMax = 4 },
		visual = { color = rgb(70, 130, 150) },
		chipStats = { resistEnergy = 8 },
	}),
	grease_film = part({
		id = "grease_film",
		name = "Chip: Grease Film",
		slot = "Chip",
		rarity = "Rare",
		weight = 2,
		sellWorth = 40,
		level = 1,
		tooltip = "Slips physical. Adds a little juice.",
		contrib = { batteryRegen = 2, integrity = 8 },
		visual = { color = rgb(140, 130, 60) },
		chipStats = { resistPhysical = 4, integrityBonus = 8 },
	}),

	-- ── Battery / CPU ────────────────────────────────────────────────
	desk_brick = part({
		id = "desk_brick",
		name = "Desk Brick Battery",
		slot = "Battery",
		rarity = "Common",
		weight = 6,
		sellWorth = 20,
		level = 1,
		tooltip = "Office surplus. Keeps the lights on.",
		contrib = { batteryMax = 20, batteryRegen = 4 },
		visual = { color = rgb(48, 52, 58), size = Vector3.new(1.6, 1.0, 0.8) },
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
		contrib = { batteryMax = 35, batteryRegen = 8 },
		visual = { color = rgb(40, 72, 88), size = Vector3.new(1.8, 1.2, 0.9) },
		batteryStats = { batteryMaxBonus = 35, batteryRegenBonus = 8 },
	}),
	deep_cell = part({
		id = "deep_cell",
		name = "Deep Cell",
		slot = "Battery",
		rarity = "Rare",
		weight = 9,
		sellWorth = 70,
		level = 1,
		tooltip = "Dense pack. Slow to cook dry.",
		contrib = { batteryMax = 50, batteryRegen = 6 },
		visual = { color = rgb(32, 96, 110), size = Vector3.new(2.0, 1.4, 1.0) },
		batteryStats = { batteryMaxBonus = 50, batteryRegenBonus = 6 },
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
		contrib = { cooling = 1 },
		visual = { color = rgb(60, 80, 60), size = Vector3.new(0.8, 0.4, 0.8) },
		cpuStats = { tier = 1 },
	}),
	bay_cpu = part({
		id = "bay_cpu",
		name = "Bay CPU",
		slot = "CPU",
		rarity = "Uncommon",
		weight = 3,
		sellWorth = 35,
		level = 1,
		tooltip = "Cleaner clock. Still no software tree.",
		contrib = { cooling = 2, batteryRegen = 1 },
		visual = { color = rgb(50, 100, 70), size = Vector3.new(0.9, 0.4, 0.9) },
		cpuStats = { tier = 2 },
	}),

	-- ── Drone (optional) ─────────────────────────────────────────────
	floor_bit = part({
		id = "floor_bit",
		name = "Floor Bit",
		slot = "Drone",
		rarity = "Common",
		weight = 5,
		sellWorth = 22,
		level = 1,
		tooltip = "Wheeled pest. Fires after your turn.",
		contrib = { integrity = 2 },
		visual = { color = rgb(100, 90, 70), size = Vector3.new(1.2, 0.7, 1.4) },
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
		contrib = { batteryMax = 2 },
		visual = { color = rgb(180, 200, 80), size = Vector3.new(1.0, 0.6, 1.2) },
		droneStats = {
			damageType = "Energy",
			damage = 14,
			heatCost = 2,
			batteryCost = 6,
			rangeMax = 5,
			tooltip = "End of turn. Energy. Range ≤5.",
		},
	}),
	heal_beep = part({
		id = "heal_beep",
		name = "Heal Beep",
		slot = "Drone",
		rarity = "Rare",
		weight = 5,
		sellWorth = 65,
		level = 1,
		tooltip = "Shoulder sit. Soft heat tick for foes.",
		contrib = { cooling = 2, integrity = 4 },
		visual = { color = rgb(80, 160, 120), size = Vector3.new(1.1, 0.8, 1.1) },
		droneStats = {
			damageType = "Heat",
			damage = 10,
			heatCost = 0,
			batteryCost = 4,
			rangeMax = 3,
			tooltip = "End of turn. Heat. Range ≤3.",
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

function Catalog.allIds(): { string }
	local ids = {}
	for id in Catalog.parts do
		table.insert(ids, id)
	end
	table.sort(ids)
	return ids
end

-- Clone a catalog weapon into a specific lower/shoulder slot.
function Catalog.asWeapon(id: string, slot: Slots.SlotKind): CatalogPart
	local base = Catalog.require(id)
	local clone: CatalogPart = table.clone(base)
	clone.slot = slot
	if base.weaponStats then
		clone.weaponStats = table.clone(base.weaponStats)
	end
	if base.contrib then
		clone.contrib = table.clone(base.contrib)
	end
	if base.visual then
		clone.visual = table.clone(base.visual)
	end
	return clone
end

-- Deep-ish clone for inventory ownership (same stats, independent table).
function Catalog.clonePart(id: string): CatalogPart
	local base = Catalog.require(id)
	local clone: CatalogPart = table.clone(base)
	if base.torsoStats then
		clone.torsoStats = table.clone(base.torsoStats)
	end
	if base.legStats then
		clone.legStats = table.clone(base.legStats)
	end
	if base.weaponStats then
		clone.weaponStats = table.clone(base.weaponStats)
	end
	if base.chipStats then
		clone.chipStats = table.clone(base.chipStats)
	end
	if base.batteryStats then
		clone.batteryStats = table.clone(base.batteryStats)
	end
	if base.cpuStats then
		clone.cpuStats = table.clone(base.cpuStats)
	end
	if base.droneStats then
		clone.droneStats = table.clone(base.droneStats)
	end
	if base.contrib then
		clone.contrib = table.clone(base.contrib)
	end
	if base.visual then
		clone.visual = table.clone(base.visual)
	end
	return clone
end

-- Compact client-safe summary of a part.
function Catalog.summary(part: CatalogPart): { [string]: any }
	local weapon = part.weaponStats
	return {
		id = part.id,
		name = part.name,
		slot = part.slot,
		rarity = part.rarity,
		weight = part.weight,
		tooltip = part.tooltip,
		mountClass = part.mountClass,
		legType = part.legType,
		legVariant = part.legVariant,
		damageType = if weapon then weapon.damageType else nil,
		damage = if weapon then weapon.damage else nil,
		rangeMin = if weapon then weapon.rangeMin else nil,
		rangeMax = if weapon then weapon.rangeMax else nil,
	}
end

return Catalog

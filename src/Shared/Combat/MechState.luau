-- Build a fighter's combat snapshot from an equipped loadout.
-- Pure data — no Roblox instances.

local Types = require(script.Parent.Types)
local Slots = require(script.Parent.Parent.Parts.Slots)
local Catalog = require(script.Parent.Parent.Parts.Catalog)

export type EquippedWeapon = {
	slot: string,
	partId: string,
	name: string,
	stats: Types.WeaponStats,
}

export type EquippedDrone = {
	partId: string,
	name: string,
	stats: Types.DroneStats,
}

export type FighterState = {
	id: string,
	displayName: string,
	resources: Types.CombatResources,
	cooling: number,
	batteryRegen: number,
	resistPhysical: number,
	resistHeat: number,
	resistEnergy: number,
	weight: Types.WeightStatus,
	moveRange: number,
	position: number,
	skipNextTurn: boolean,
	-- Moves left while energy weapons are dark (Battery Life hit 0).
	batteryRechargeMoves: number,
	weapons: { EquippedWeapon },
	drone: EquippedDrone?,
}

local MechState = {}

local function addWeapon(list: { EquippedWeapon }, part: Slots.PartDef?, slotName: string)
	if not part then
		return
	end
	local catalogPart = part :: Catalog.CatalogPart
	local stats = catalogPart.weaponStats
	if not stats then
		return
	end
	table.insert(list, {
		slot = slotName,
		partId = part.id,
		name = part.name,
		stats = stats,
	})
end

function MechState.fromLoadout(
	id: string,
	displayName: string,
	loadout: Slots.EquippedLoadout,
	position: number
): FighterState
	local torso = loadout.torso :: Catalog.CatalogPart?
	assert(torso and torso.torsoStats, "Loadout needs a torso with torsoStats")
	local ts = torso.torsoStats

	local integrityMax = ts.integrity
	local temperatureMax = ts.temperatureMax
	local cooling = ts.cooling
	local batteryMax = ts.batteryMax
	local batteryRegen = ts.batteryRegen
	local capacity = ts.weightCapacity
	local resistP = ts.resistPhysical
	local resistH = ts.resistHeat
	local resistE = ts.resistEnergy

	for _, chip in loadout.chips do
		local c = chip :: Catalog.CatalogPart
		local cs = c.chipStats
		if cs then
			resistP += cs.resistPhysical or 0
			resistH += cs.resistHeat or 0
			resistE += cs.resistEnergy or 0
			cooling += cs.coolingBonus or 0
			integrityMax += cs.integrityBonus or 0
		end
	end

	if loadout.battery then
		local b = loadout.battery :: Catalog.CatalogPart
		if b.batteryStats then
			batteryMax += b.batteryStats.batteryMaxBonus
			batteryRegen += b.batteryStats.batteryRegenBonus
		end
	end

	local currentWeight = Slots.sumWeight(loadout)
	local over = math.max(0, currentWeight - capacity)
	local integrityPenalty = over * Types.OVERWEIGHT_INTEGRITY_PER_UNIT
	integrityMax = math.max(1, integrityMax - integrityPenalty)

	local moveRange = 2
	local left = loadout.leftLeg :: Catalog.CatalogPart?
	local right = loadout.rightLeg :: Catalog.CatalogPart?
	if left and left.legStats then
		moveRange = left.legStats.moveRange
	end
	if right and right.legStats then
		-- Matched pair: use the lower of the two (mismatch safety).
		moveRange = math.min(moveRange, right.legStats.moveRange)
	end

	local weapons: { EquippedWeapon } = {}
	addWeapon(weapons, loadout.lowerLeft, "LowerLeft")
	addWeapon(weapons, loadout.lowerRight, "LowerRight")
	addWeapon(weapons, loadout.shoulderLeft, "ShoulderLeft")
	addWeapon(weapons, loadout.shoulderRight, "ShoulderRight")

	local drone: EquippedDrone? = nil
	if loadout.drone then
		local d = loadout.drone :: Catalog.CatalogPart
		if d.droneStats then
			drone = {
				partId = d.id,
				name = d.name,
				stats = d.droneStats,
			}
		end
	end

	return {
		id = id,
		displayName = displayName,
		resources = {
			integrity = integrityMax,
			integrityMax = integrityMax,
			temperature = 0,
			temperatureMax = temperatureMax,
			battery = batteryMax,
			batteryMax = batteryMax,
		},
		cooling = cooling,
		batteryRegen = batteryRegen,
		resistPhysical = resistP,
		resistHeat = resistH,
		resistEnergy = resistE,
		weight = {
			current = currentWeight,
			capacity = capacity,
			overWeight = over > 0,
			integrityPenalty = integrityPenalty,
		},
		moveRange = moveRange,
		position = position,
		skipNextTurn = false,
		batteryRechargeMoves = 0,
		weapons = weapons,
		drone = drone,
	}
end

function MechState.findWeapon(fighter: FighterState, slot: string): EquippedWeapon?
	for _, w in fighter.weapons do
		if w.slot == slot then
			return w
		end
	end
	return nil
end

function MechState.distance(a: FighterState, b: FighterState): number
	return math.abs(a.position - b.position)
end

return MechState

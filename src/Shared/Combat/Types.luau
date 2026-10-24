-- Shared combat types for Assembler (scaffold — no full sim yet).
-- AP default: ~2 action points per turn (SuperMechs-like).
-- Weight: every part has weight; chassis capacity stub; soft overweight
-- penalty preferred (Integrity loss when over cap) — hard equip block TBD.

export type DamageType = "Physical" | "Heat" | "Energy"

export type Integrity = number -- Core Integrity (HP); 0 = dead
export type Temperature = number -- Core Temperature
export type Battery = number -- Battery Life (combat energy)
export type Weight = number -- Part / loadout weight units
export type AP = number -- Action points remaining this turn

export type CombatResources = {
	integrity: Integrity,
	integrityMax: Integrity,
	temperature: Temperature,
	temperatureMax: Temperature,
	battery: Battery,
	batteryMax: Battery,
}

export type DamagePacket = {
	amount: number,
	damageType: DamageType,
}

-- Soft vs hard overweight: prefer soft penalty like SuperMechs (Integrity
-- loss when over capacity). Hard "can't field" ceiling is still open.
export type WeightStatus = {
	current: Weight,
	capacity: Weight,
	overWeight: boolean,
}

export type TurnBudget = {
	apMax: AP, -- locked default ~2
	apRemaining: AP,
}

local Types = {}

Types.DEFAULT_AP_PER_TURN = 2 :: AP

return Types

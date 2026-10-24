-- Shared combat types for Assembler.
-- AP default: ~2 action points per turn (SuperMechs-like).
-- Weight: soft overweight Integrity penalty (SM-style). Hard field ceiling TBD.
-- Phase 2 stubs: Freeze (temp floor lock) and Over-Voltage (battery overcharge).

export type DamageType = "Physical" | "Heat" | "Energy"

export type Integrity = number -- Core Integrity (HP); 0 = dead
export type Temperature = number -- Core Temperature
export type Battery = number -- Battery Life (combat energy)
export type Weight = number
export type AP = number

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

export type WeightStatus = {
	current: Weight,
	capacity: Weight,
	overWeight: boolean,
	-- Soft penalty applied to integrityMax at battle start.
	integrityPenalty: number,
}

export type TurnBudget = {
	apMax: AP,
	apRemaining: AP,
}

export type RangeBand = number -- tiles; distance = abs(posA - posB)

export type WeaponStats = {
	damageType: DamageType,
	damage: number,
	heatCost: number,
	batteryCost: number,
	rangeMin: RangeBand,
	rangeMax: RangeBand,
	apCost: AP,
	-- Short tooltip shown in UI.
	tooltip: string,
}

export type DroneStats = {
	damageType: DamageType,
	damage: number,
	heatCost: number,
	batteryCost: number,
	rangeMax: RangeBand,
	tooltip: string,
}

export type ActionKind = "Move" | "Fire" | "EndTurn"

export type MoveAction = {
	kind: "Move",
	-- Delta along the 1D arena line (negative = toward lower tiles).
	delta: number,
}

export type FireAction = {
	kind: "Fire",
	weaponSlot: string, -- e.g. "LowerLeft", "ShoulderRight"
}

export type EndTurnAction = {
	kind: "EndTurn",
}

export type BattleAction = MoveAction | FireAction | EndTurnAction

export type BattleOutcome = "Ongoing" | "SideAWins" | "SideBWins"

local Types = {}

Types.DEFAULT_AP_PER_TURN = 2 :: AP

-- Soft overweight: Integrity max lost per weight unit over capacity.
Types.OVERWEIGHT_INTEGRITY_PER_UNIT = 8

-- When Battery Life hits 0, energy weapons stay dark for this many of *your* moves
-- (Fire or Move that spends AP) while the pack recharges.
Types.BATTERY_RECHARGE_MOVES = 3

-- Arena length in tiles (1-indexed positions).
Types.ARENA_TILES = 8

-- Phase 2 — not implemented this slice:
-- Types.FREEZE_TEMP_FLOOR = 0  -- too cold → lock mech/melee/move
-- Types.OVER_VOLTAGE_THRESHOLD = ... -- overcharged battery failure

return Types

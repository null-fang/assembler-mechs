-- Turn-based combat resolver. Shared by PvE ladder and PvP (same sim).
-- Resources: Core Integrity, Core Temperature, Battery Life.
-- Damage triad: Physical / Heat / Energy.
-- Freeze + Over-Voltage: Phase 2 (comments only below).

local Types = require(script.Parent.Types)
local MechState = require(script.Parent.MechState)
local BattleMode = require(script.Parent.Parent.Modes.BattleMode)

export type BattleSide = "A" | "B"

export type LogLine = {
	text: string,
	side: BattleSide?,
}

export type Battle = {
	mode: BattleMode.BattleMode,
	sideA: MechState.FighterState,
	sideB: MechState.FighterState,
	activeSide: BattleSide,
	turnBudget: Types.TurnBudget,
	outcome: Types.BattleOutcome,
	turnIndex: number,
	log: { LogLine },
}

local Resolver = {}

local function otherSide(side: BattleSide): BattleSide
	return if side == "A" then "B" else "A"
end

local function fighter(battle: Battle, side: BattleSide): MechState.FighterState
	return if side == "A" then battle.sideA else battle.sideB
end

local function pushLog(battle: Battle, text: string, side: BattleSide?)
	table.insert(battle.log, { text = text, side = side })
	-- Cap log so clients don't drown.
	while #battle.log > 40 do
		table.remove(battle.log, 1)
	end
end

local function resistFor(f: MechState.FighterState, damageType: Types.DamageType): number
	if damageType == "Physical" then
		return f.resistPhysical
	elseif damageType == "Heat" then
		return f.resistHeat
	else
		return f.resistEnergy
	end
end

local function applyIntegrityDamage(target: MechState.FighterState, amount: number): number
	local dealt = math.max(0, amount)
	target.resources.integrity = math.max(0, target.resources.integrity - dealt)
	return dealt
end

local function applyHeatToTarget(target: MechState.FighterState, heat: number)
	-- Heat damage type also pushes Core Temperature (after resist on Integrity hit).
	target.resources.temperature += math.max(0, heat)
end

local function resolveDamage(
	battle: Battle,
	attacker: MechState.FighterState,
	target: MechState.FighterState,
	packet: Types.DamagePacket,
	label: string
)
	local resist = resistFor(target, packet.damageType)
	local incoming = math.max(1, packet.amount - resist)
	local dealt = applyIntegrityDamage(target, incoming)

	if packet.damageType == "Heat" then
		-- Portion of heat weapon damage bleeds into temperature.
		applyHeatToTarget(target, math.floor(packet.amount * 0.35))
	end

	pushLog(
		battle,
		("%s hits %s for %d %s"):format(label, target.displayName, dealt, packet.damageType),
		nil
	)

	if target.resources.integrity <= 0 then
		pushLog(battle, ("%s is scrap."):format(target.displayName), nil)
	end
end

local function checkOutcome(battle: Battle)
	local aDead = battle.sideA.resources.integrity <= 0
	local bDead = battle.sideB.resources.integrity <= 0
	if aDead and bDead then
		-- Simultaneous scrap: defender (B) wins the tie for now.
		battle.outcome = "SideBWins"
	elseif aDead then
		battle.outcome = "SideBWins"
	elseif bDead then
		battle.outcome = "SideAWins"
	end
end

local function spendBattery(attacker: MechState.FighterState, cost: number): boolean
	if cost <= 0 then
		return true
	end
	if attacker.batteryRechargeMoves > 0 then
		return false
	end
	if attacker.resources.battery < cost then
		return false
	end
	attacker.resources.battery -= cost
	if attacker.resources.battery <= 0 then
		attacker.resources.battery = 0
		attacker.batteryRechargeMoves = Types.BATTERY_RECHARGE_MOVES
	end
	return true
end

local function addSelfHeat(attacker: MechState.FighterState, heat: number)
	attacker.resources.temperature += math.max(0, heat)
end

local function tickBatteryRechargeOnMove(attacker: MechState.FighterState)
	if attacker.batteryRechargeMoves > 0 then
		attacker.batteryRechargeMoves -= 1
	end
end

local function refreshTurnBudget(battle: Battle)
	local ap = Types.DEFAULT_AP_PER_TURN
	battle.turnBudget = {
		apMax = ap,
		apRemaining = ap,
	}
end

function Resolver.createBattle(
	mode: BattleMode.BattleMode,
	sideA: MechState.FighterState,
	sideB: MechState.FighterState
): Battle
	local battle: Battle = {
		mode = mode,
		sideA = sideA,
		sideB = sideB,
		activeSide = "A",
		turnBudget = {
			apMax = Types.DEFAULT_AP_PER_TURN,
			apRemaining = Types.DEFAULT_AP_PER_TURN,
		},
		outcome = "Ongoing",
		turnIndex = 1,
		log = {},
	}
	pushLog(battle, ("Fight start — %s vs %s"):format(sideA.displayName, sideB.displayName), nil)
	if sideA.weight.overWeight then
		pushLog(
			battle,
			("%s is overweight (−%d Integrity)."):format(sideA.displayName, sideA.weight.integrityPenalty),
			"A"
		)
	end
	if sideB.weight.overWeight then
		pushLog(
			battle,
			("%s is overweight (−%d Integrity)."):format(sideB.displayName, sideB.weight.integrityPenalty),
			"B"
		)
	end
	return battle
end

function Resolver.getActive(battle: Battle): MechState.FighterState
	return fighter(battle, battle.activeSide)
end

function Resolver.getFoe(battle: Battle): MechState.FighterState
	return fighter(battle, otherSide(battle.activeSide))
end

local function canFireWeapon(
	attacker: MechState.FighterState,
	foe: MechState.FighterState,
	weapon: MechState.EquippedWeapon
): (boolean, string?)
	local dist = MechState.distance(attacker, foe)
	local s = weapon.stats
	if dist < s.rangeMin or dist > s.rangeMax then
		return false, "Out of range"
	end
	if s.damageType == "Energy" and attacker.batteryRechargeMoves > 0 then
		return false, "Pack recharging — energy guns dark"
	end
	if s.batteryCost > 0 and attacker.batteryRechargeMoves > 0 then
		return false, "Pack recharging"
	end
	if s.batteryCost > 0 and attacker.resources.battery < s.batteryCost then
		return false, "Not enough battery"
	end
	return true, nil
end

function Resolver.listLegalActions(battle: Battle): { Types.BattleAction }
	if battle.outcome ~= "Ongoing" then
		return {}
	end
	local actions: { Types.BattleAction } = {}
	local self = Resolver.getActive(battle)
	local foe = Resolver.getFoe(battle)

	if self.skipNextTurn then
		-- Overheated: only EndTurn is legal (forced cool).
		table.insert(actions, { kind = "EndTurn" })
		return actions
	end

	if battle.turnBudget.apRemaining > 0 then
		-- Moves toward / away within moveRange, staying on arena.
		for delta = -self.moveRange, self.moveRange do
			if delta ~= 0 then
				local dest = self.position + delta
				if dest >= 1 and dest <= Types.ARENA_TILES and dest ~= foe.position then
					table.insert(actions, { kind = "Move", delta = delta })
				end
			end
		end

		for _, weapon in self.weapons do
			local ok = canFireWeapon(self, foe, weapon)
			if ok and battle.turnBudget.apRemaining >= weapon.stats.apCost then
				table.insert(actions, { kind = "Fire", weaponSlot = weapon.slot })
			end
		end
	end

	table.insert(actions, { kind = "EndTurn" })
	return actions
end

local function fireDrone(battle: Battle, ownerSide: BattleSide)
	local owner = fighter(battle, ownerSide)
	local foe = fighter(battle, otherSide(ownerSide))
	local drone = owner.drone
	if not drone then
		return
	end
	if owner.resources.integrity <= 0 or foe.resources.integrity <= 0 then
		return
	end
	local dist = MechState.distance(owner, foe)
	if dist > drone.stats.rangeMax then
		pushLog(battle, ("%s's %s is out of reach."):format(owner.displayName, drone.name), ownerSide)
		return
	end
	if drone.stats.damageType == "Energy" and owner.batteryRechargeMoves > 0 then
		pushLog(battle, ("%s's drone stays dark — pack charging."):format(owner.displayName), ownerSide)
		return
	end
	if drone.stats.batteryCost > 0 then
		if not spendBattery(owner, drone.stats.batteryCost) then
			pushLog(battle, ("%s's drone needs battery."):format(owner.displayName), ownerSide)
			return
		end
	end
	addSelfHeat(owner, drone.stats.heatCost)
	resolveDamage(battle, owner, foe, {
		amount = drone.stats.damage,
		damageType = drone.stats.damageType,
	}, owner.displayName .. "'s " .. drone.name)
end

local function endOfTurnTicks(battle: Battle, side: BattleSide)
	local f = fighter(battle, side)

	-- Cooling tick.
	f.resources.temperature = math.max(0, f.resources.temperature - f.cooling)

	-- Battery regen (always trickle; energy weapons stay dark until recharge moves clear).
	f.resources.battery = math.min(f.resources.batteryMax, f.resources.battery + f.batteryRegen)

	-- Overheat check: still over cap after cooling → skip next turn.
	if f.resources.temperature > f.resources.temperatureMax then
		f.skipNextTurn = true
		-- Dump heat toward cap so they can recover.
		f.resources.temperature = f.resources.temperatureMax
		pushLog(battle, ("%s overheated — next turn skipped."):format(f.displayName), side)
	end

	-- Phase 2: Freeze — if temperature hits a deep floor, lock move/melee.
	-- Phase 2: Over-Voltage — if battery is forced past max, punish recovery / explode.
end

local function beginSideTurn(battle: Battle, side: BattleSide)
	battle.activeSide = side
	refreshTurnBudget(battle)
	local f = fighter(battle, side)

	if f.skipNextTurn then
		pushLog(battle, ("%s sits out — cooling off."):format(f.displayName), side)
		-- Consume the skip: they EndTurn immediately via AI / forced path.
		return
	end

	pushLog(battle, ("%s's turn (%d AP)."):format(f.displayName, battle.turnBudget.apRemaining), side)
	if f.batteryRechargeMoves > 0 then
		pushLog(
			battle,
			("Energy guns dark — %d moves left on charge."):format(f.batteryRechargeMoves),
			side
		)
	end
end

function Resolver.applyAction(battle: Battle, action: Types.BattleAction): (boolean, string?)
	if battle.outcome ~= "Ongoing" then
		return false, "Fight over"
	end

	local self = Resolver.getActive(battle)
	local foe = Resolver.getFoe(battle)

	if action.kind == "EndTurn" then
		if self.skipNextTurn then
			self.skipNextTurn = false
			pushLog(battle, ("%s finishes the cool-down."):format(self.displayName), battle.activeSide)
		end

		fireDrone(battle, battle.activeSide)
		checkOutcome(battle)
		if battle.outcome ~= "Ongoing" then
			return true, nil
		end

		endOfTurnTicks(battle, battle.activeSide)
		checkOutcome(battle)
		if battle.outcome ~= "Ongoing" then
			return true, nil
		end

		local nextSide = otherSide(battle.activeSide)
		if nextSide == "A" then
			battle.turnIndex += 1
		end
		beginSideTurn(battle, nextSide)

		-- If the next side is skipping, auto-resolve their forced EndTurn once.
		-- Caller (host/AI) should keep applying; we don't recurse here.
		return true, nil
	end

	if self.skipNextTurn then
		return false, "Overheated — only End Turn"
	end

	if action.kind == "Move" then
		local cost = 1
		if battle.turnBudget.apRemaining < cost then
			return false, "No AP left"
		end
		local dest = self.position + action.delta
		if math.abs(action.delta) > self.moveRange or action.delta == 0 then
			return false, "Can't step that far"
		end
		if dest < 1 or dest > Types.ARENA_TILES then
			return false, "Off the arena"
		end
		if dest == foe.position then
			return false, "Tile occupied"
		end
		self.position = dest
		battle.turnBudget.apRemaining -= cost
		tickBatteryRechargeOnMove(self)
		pushLog(
			battle,
			("%s moves to tile %d (range %d)."):format(
				self.displayName,
				self.position,
				MechState.distance(self, foe)
			),
			battle.activeSide
		)
		return true, nil
	end

	if action.kind == "Fire" then
		local weapon = MechState.findWeapon(self, action.weaponSlot)
		if not weapon then
			return false, "No weapon there"
		end
		local ok, reason = canFireWeapon(self, foe, weapon)
		if not ok then
			return false, reason
		end
		local cost = weapon.stats.apCost
		if battle.turnBudget.apRemaining < cost then
			return false, "No AP left"
		end
		if not spendBattery(self, weapon.stats.batteryCost) then
			return false, "Not enough battery"
		end
		addSelfHeat(self, weapon.stats.heatCost)
		battle.turnBudget.apRemaining -= cost
		tickBatteryRechargeOnMove(self)

		resolveDamage(battle, self, foe, {
			amount = weapon.stats.damage,
			damageType = weapon.stats.damageType,
		}, self.displayName .. "'s " .. weapon.name)

		if self.batteryRechargeMoves == Types.BATTERY_RECHARGE_MOVES and weapon.stats.batteryCost > 0 then
			pushLog(battle, ("Battery empty — energy guns dark for %d moves."):format(Types.BATTERY_RECHARGE_MOVES), battle.activeSide)
		end

		checkOutcome(battle)
		return true, nil
	end

	return false, "Unknown action"
end

-- Snapshot for remotes / UI (plain tables).
function Resolver.snapshot(battle: Battle): { [string]: any }
	local function sideSnap(f: MechState.FighterState)
		local weaponList = {}
		for _, w in f.weapons do
			table.insert(weaponList, {
				slot = w.slot,
				name = w.name,
				damageType = w.stats.damageType,
				damage = w.stats.damage,
				rangeMin = w.stats.rangeMin,
				rangeMax = w.stats.rangeMax,
				batteryCost = w.stats.batteryCost,
				tooltip = w.stats.tooltip,
			})
		end
		return {
			id = f.id,
			displayName = f.displayName,
			integrity = f.resources.integrity,
			integrityMax = f.resources.integrityMax,
			temperature = f.resources.temperature,
			temperatureMax = f.resources.temperatureMax,
			battery = f.resources.battery,
			batteryMax = f.resources.batteryMax,
			position = f.position,
			skipNextTurn = f.skipNextTurn,
			batteryRechargeMoves = f.batteryRechargeMoves,
			overWeight = f.weight.overWeight,
			weapons = weaponList,
			droneName = if f.drone then f.drone.name else nil,
		}
	end
	return {
		mode = battle.mode,
		activeSide = battle.activeSide,
		turnIndex = battle.turnIndex,
		apRemaining = battle.turnBudget.apRemaining,
		apMax = battle.turnBudget.apMax,
		outcome = battle.outcome,
		sideA = sideSnap(battle.sideA),
		sideB = sideSnap(battle.sideB),
		distance = MechState.distance(battle.sideA, battle.sideB),
		log = battle.log,
	}
end

return Resolver

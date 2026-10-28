-- Campaign ladder: 10 NPC fights, escalating, no bosses.
-- Richer fight cards: threat, elements, pacing, mid-ladder crate guarantees.

local BattleOpponent = require(game.ReplicatedStorage.Shared.Modes.BattleOpponent)
local Catalog = require(game.ReplicatedStorage.Shared.Parts.Catalog)
local Slots = require(game.ReplicatedStorage.Shared.Parts.Slots)
local Rewards = require(game.ReplicatedStorage.Shared.Economy.Rewards)
local MechLine = require(game.ReplicatedStorage.Shared.Themes.MechLine)
local ContentHooks = require(game.ReplicatedStorage.Shared.Campaign.ContentHooks)

export type PacingBeat = "warmup" | "pressure" | "spike" | "finale"

export type LadderFight = {
	index: number,
	opponent: BattleOpponent.BattleOpponent,
	rewardCommonWin: number,
	rewardCommonLoss: number,
	blurb: string,
	taunt: string,
	threat: number, -- 1–5
	elements: { string }, -- dominant damage types
	pacing: PacingBeat,
	guaranteedCrateWin: boolean,
	lossHint: string,
	winHint: string,
	mechLine: string?,
}

local Ladder = {}

Ladder.FIRST_SLICE_COUNT = 10

-- Mid-ladder crate milestones (win only).
Ladder.CRATE_MILESTONES = { [3] = true, [5] = true, [7] = true, [10] = true }

local function loadout(parts: {
	torso: string,
	leftLeg: string,
	rightLeg: string,
	lowerLeft: string?,
	lowerRight: string?,
	shoulderLeft: string?,
	shoulderRight: string?,
	chips: { string }?,
	battery: string?,
	cpu: string?,
	drone: string?,
}): Slots.EquippedLoadout
	local chips: { Slots.PartDef } = {}
	local chipIds = parts.chips or {}
	for _, id in chipIds do
		table.insert(chips, Catalog.require(id))
	end
	return {
		torso = Catalog.require(parts.torso),
		leftLeg = Catalog.require(parts.leftLeg),
		rightLeg = Catalog.require(parts.rightLeg),
		lowerLeft = if parts.lowerLeft then Catalog.asWeapon(parts.lowerLeft, "LowerLeft") else nil,
		lowerRight = if parts.lowerRight then Catalog.asWeapon(parts.lowerRight, "LowerRight") else nil,
		shoulderLeft = if parts.shoulderLeft then Catalog.asWeapon(parts.shoulderLeft, "ShoulderLeft") else nil,
		shoulderRight = if parts.shoulderRight
			then Catalog.asWeapon(parts.shoulderRight, "ShoulderRight")
			else nil,
		chips = chips,
		battery = if parts.battery then Catalog.require(parts.battery) else nil,
		cpu = if parts.cpu then Catalog.require(parts.cpu) else nil,
		drone = if parts.drone then Catalog.require(parts.drone) else nil,
	}
end

-- Light deterministic swap keeps fights from feeling identical on replay.
local function maybeSwap(baseId: string, pool: { string }, fightIndex: number, every: number?): string
	local n = every or 2
	if fightIndex % n ~= 0 then
		return baseId
	end
	return pool[((fightIndex - 1) % #pool) + 1]
end

local function collectElements(built: Slots.EquippedLoadout): { string }
	local seen: { [string]: boolean } = {}
	local order: { string } = {}
	local function add(w)
		if not w or not w.weaponStats then
			return
		end
		local dt = w.weaponStats.damageType
		if dt and not seen[dt] then
			seen[dt] = true
			table.insert(order, dt)
		end
	end
	add(built.lowerLeft)
	add(built.lowerRight)
	add(built.shoulderLeft)
	add(built.shoulderRight)
	if built.drone and built.drone.droneStats then
		local dt = built.drone.droneStats.damageType
		if dt and not seen[dt] then
			seen[dt] = true
			table.insert(order, dt)
		end
	end
	if #order == 0 then
		table.insert(order, "Physical")
	end
	return order
end

function Ladder.buildFirstSlice(): { LadderFight }
	-- Invented bay scrap — short names, human taunts, distinct kits + pacing beats.
	local defs = {
		{
			name = "Tin Rook",
			blurb = "First day. Barely bolted.",
			taunt = "Don't dent me.",
			threat = 1,
			pacing = "warmup",
			lossHint = "Learn the lane. Soft payout still lands.",
			winHint = "Warmup clear. Keep climbing.",
			parts = {
				torso = "rusty_cage",
				leftLeg = "workboot_l",
				rightLeg = "workboot_r",
				lowerLeft = "snap_arm",
				battery = "desk_brick",
				cpu = "scrap_cpu",
			},
		},
		{
			name = "Scrap Mouse",
			blurb = "Runs light. Hits soft. Drone ticks.",
			taunt = "Too slow.",
			threat = 1,
			pacing = "warmup",
			lossHint = "Watch the floor bit on end-turn.",
			winHint = "Pressure starts next.",
			parts = {
				torso = "tin_can",
				leftLeg = "digit_l",
				rightLeg = "digit_r",
				lowerLeft = "needle_jab",
				lowerRight = "rivet_gun",
				battery = "desk_brick",
				cpu = "scrap_cpu",
				chips = { "thick_skin" },
				drone = "floor_bit",
			},
		},
		{
			name = "Hot Rivet",
			blurb = "Likes warm metal. Mid crate on win.",
			taunt = "Smell that?",
			threat = 2,
			pacing = "pressure",
			lossHint = "Cool between swings — heat stacks.",
			winHint = "Milestone crate unlocked.",
			parts = {
				torso = "hot_box",
				leftLeg = "workboot_l",
				rightLeg = "workboot_r",
				lowerLeft = "ember_fist",
				lowerRight = "torch_palm",
				battery = "desk_brick",
				cpu = "scrap_cpu",
				chips = { "heat_sink_chip" },
			},
		},
		{
			name = "Cold Span",
			blurb = "Keeps range. Doesn't chat.",
			taunt = "…",
			threat = 2,
			pacing = "pressure",
			lossHint = "Close the gap before nail rack fires.",
			winHint = "Range lesson learned.",
			parts = {
				torso = "mesh_cage",
				leftLeg = "stump_l",
				rightLeg = "stump_r",
				lowerRight = "hook_arm",
				shoulderRight = "nail_rack",
				battery = "desk_brick",
				cpu = "scrap_cpu",
				drone = "floor_bit",
			},
		},
		{
			name = "Peg Runner",
			blurb = "Longer legs. Still learning. Crate win.",
			taunt = "Keep up.",
			threat = 3,
			pacing = "spike",
			lossHint = "They step farther — match move range.",
			winHint = "Mid-ladder crate secured.",
			parts = {
				torso = "scrap_weld",
				leftLeg = "sprint_peg_l",
				rightLeg = "sprint_peg_r",
				lowerLeft = "cleaver_arm",
				shoulderRight = "brick_shoulder",
				battery = "desk_brick",
				cpu = "scrap_cpu",
				chips = { "grease_film" },
				drone = "spark_moth",
			},
		},
		{
			name = "Dust Arc",
			blurb = "Arc practice. Pack runs hot.",
			taunt = "Stand still.",
			threat = 3,
			pacing = "pressure",
			lossHint = "Energy guns need battery — don't empty early.",
			winHint = "Bay packs outscale desk bricks.",
			parts = {
				torso = "painted_crate",
				leftLeg = "mud_l",
				rightLeg = "mud_r",
				lowerLeft = "snap_arm",
				shoulderLeft = "arc_rail",
				battery = "bay_cell",
				cpu = "bay_cpu",
				chips = { "wire_wrap" },
				drone = "floor_bit",
			},
		},
		{
			name = "Bolt Maw",
			blurb = "Two arms and a temper. Crate win.",
			taunt = "Come closer.",
			threat = 4,
			pacing = "spike",
			lossHint = "Don't eat both lower mounts in one turn.",
			winHint = "Spike cleared — crate paid.",
			parts = {
				torso = "iron_locker",
				leftLeg = "claw_l",
				rightLeg = "claw_r",
				lowerLeft = "drill_punch",
				lowerRight = "pipe_club",
				shoulderRight = "twin_pipe",
				battery = "bay_cell",
				cpu = "scrap_cpu",
				chips = { "thick_skin" },
				drone = "orb_drone",
			},
		},
		{
			name = "Lane Bite",
			blurb = "Closes fast. Don't give space.",
			taunt = "No room left.",
			threat = 4,
			pacing = "pressure",
			lossHint = "Backstep when they close to melee.",
			winHint = "Space control paid off.",
			parts = {
				torso = "plate_box",
				leftLeg = "sprint_peg_l",
				rightLeg = "sprint_peg_r",
				lowerLeft = "slag_glove",
				lowerRight = "ember_fist",
				shoulderRight = "box_launcher",
				battery = "bay_cell",
				cpu = "bay_cpu",
				chips = { "heat_sink_chip" },
				drone = "glow_moth",
			},
		},
		{
			name = "Frame Check",
			blurb = "Bay QA. Mean on purpose.",
			taunt = "QA says fail.",
			threat = 4,
			pacing = "spike",
			lossHint = "Heal beep ticks — finish before it stacks.",
			winHint = "One fight left.",
			parts = {
				torso = "lattice_frame",
				leftLeg = "workboot_l",
				rightLeg = "workboot_r",
				lowerLeft = "cleaver_arm",
				lowerRight = "rivet_gun",
				shoulderLeft = "long_bite",
				battery = "bay_cell",
				cpu = "bay_cpu",
				chips = { "thick_skin", "wire_wrap" },
				drone = "heal_beep",
			},
		},
		{
			name = "Gate Weld",
			blurb = "End of the starter ladder. Better bolts — not a boss.",
			taunt = "End of the line.",
			threat = 5,
			pacing = "finale",
			lossHint = "Full kit — chip resist and cool between fires.",
			winHint = "Ladder clear. Finale crate.",
			parts = {
				torso = "bunker_shell",
				leftLeg = "needle_leg_l",
				rightLeg = "needle_leg_r",
				lowerLeft = "drill_punch",
				lowerRight = "torch_palm",
				shoulderLeft = "needle_pike",
				shoulderRight = "furnace_spit",
				battery = "deep_cell",
				cpu = "bay_cpu",
				chips = { "thick_skin", "heat_sink_chip" },
				drone = "spark_moth",
			},
		},
	}

	local fights: { LadderFight } = {}
	for i, def in defs do
		local p = table.clone(def.parts)
		if p.lowerLeft then
			p.lowerLeft = maybeSwap(p.lowerLeft, { "snap_arm", "ember_fist", "cleaver_arm", "hook_arm" }, i, 3)
		end
		if p.lowerRight and i % 4 == 0 then
			p.lowerRight = maybeSwap(p.lowerRight, { "rivet_gun", "pipe_club", "torch_palm", "drill_punch" }, i, 1)
		end
		local built = loadout(p)
		local winReward = Rewards.forCampaignFight(i, true, i * 100)
		local lossReward = Rewards.forCampaignFight(i, false, i * 100)
		local torsoId = if built.torso then built.torso.id else "rusty_cage"
		local hook = ContentHooks.extraFights[i]
		local mechLine = (hook and hook.mechLine) or MechLine.fromPartId(torsoId)
		table.insert(fights, {
			index = i,
			opponent = BattleOpponent.fromNpc(("npc-%02d"):format(i), def.name, ("mech-%02d"):format(i), built),
			rewardCommonWin = winReward.common,
			rewardCommonLoss = lossReward.common,
			blurb = def.blurb,
			taunt = def.taunt,
			threat = def.threat,
			elements = collectElements(built),
			pacing = def.pacing :: PacingBeat,
			guaranteedCrateWin = Ladder.CRATE_MILESTONES[i] == true,
			lossHint = def.lossHint,
			winHint = def.winHint,
			mechLine = mechLine,
		})
	end
	return fights
end

function Ladder.getFight(index: number): LadderFight?
	local all = Ladder.buildFirstSlice()
	return all[index]
end

return Ladder

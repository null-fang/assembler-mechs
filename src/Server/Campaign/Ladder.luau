-- Campaign ladder: 10 NPC fights, escalating, no bosses.
-- Distinct names, short taunts, loadout variety. No daily fuel gate.

local BattleOpponent = require(game.ReplicatedStorage.Shared.Modes.BattleOpponent)
local Catalog = require(game.ReplicatedStorage.Shared.Parts.Catalog)
local Slots = require(game.ReplicatedStorage.Shared.Parts.Slots)
local Rewards = require(game.ReplicatedStorage.Shared.Economy.Rewards)

export type LadderFight = {
	index: number,
	opponent: BattleOpponent.BattleOpponent,
	rewardCommonWin: number,
	blurb: string,
	taunt: string,
}

local Ladder = {}

Ladder.FIRST_SLICE_COUNT = 10

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

function Ladder.buildFirstSlice(): { LadderFight }
	-- Invented bay scrap — short names, human taunts, distinct kits.
	local defs = {
		{
			name = "Tin Rook",
			blurb = "First day. Barely bolted.",
			taunt = "Don't dent me.",
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
			blurb = "Runs light. Hits soft.",
			taunt = "Too slow.",
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
			blurb = "Likes warm metal.",
			taunt = "Smell that?",
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
			blurb = "Longer legs. Still learning.",
			taunt = "Keep up.",
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
			blurb = "Two arms and a temper.",
			taunt = "Come closer.",
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
		local reward = Rewards.forCampaignFight(i, true, i * 100)
		table.insert(fights, {
			index = i,
			opponent = BattleOpponent.fromNpc(("npc-%02d"):format(i), def.name, ("mech-%02d"):format(i), built),
			rewardCommonWin = reward.common,
			blurb = def.blurb,
			taunt = def.taunt,
		})
	end
	return fights
end

function Ladder.getFight(index: number): LadderFight?
	local all = Ladder.buildFirstSlice()
	return all[index]
end

return Ladder

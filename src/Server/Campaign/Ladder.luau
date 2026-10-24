-- Campaign ladder: ~10 NPC fights, escalating, no bosses.
-- No daily fuel gate — Battery Life is the combat energy resource.

local BattleOpponent = require(game.ReplicatedStorage.Shared.Modes.BattleOpponent)
local Catalog = require(game.ReplicatedStorage.Shared.Parts.Catalog)
local Slots = require(game.ReplicatedStorage.Shared.Parts.Slots)
local Rewards = require(game.ReplicatedStorage.Shared.Economy.Rewards)

export type LadderFight = {
	index: number,
	opponent: BattleOpponent.BattleOpponent,
	rewardCommonWin: number,
	blurb: string,
}

local Ladder = {}

type SoftLoadout = Slots.EquippedLoadout

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
}): SoftLoadout
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


-- Scripted loadouts; a few fights swap one part from a small pool for light variety.
local function maybeSwapWeapon(baseId: string, pool: { string }, fightIndex: number): string
	if fightIndex % 3 ~= 0 then
		return baseId
	end
	local pick = pool[((fightIndex - 1) % #pool) + 1]
	return pick
end

function Ladder.buildFirstSlice(): { LadderFight }
	local defs = {
		{
			name = "Bay Rookie",
			blurb = "First day. Barely bolted.",
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
			name = "Scrap Runner",
			blurb = "Runs light. Hits soft.",
			parts = {
				torso = "rusty_cage",
				leftLeg = "workboot_l",
				rightLeg = "workboot_r",
				lowerLeft = "snap_arm",
				lowerRight = "rivet_gun",
				battery = "desk_brick",
				cpu = "scrap_cpu",
				chips = { "thick_skin" },
			},
		},
		{
			name = "Hot Rivet",
			blurb = "Likes the smell of warm metal.",
			parts = {
				torso = "rusty_cage",
				leftLeg = "workboot_l",
				rightLeg = "workboot_r",
				lowerLeft = "ember_fist",
				lowerRight = "rivet_gun",
				battery = "desk_brick",
				cpu = "scrap_cpu",
				chips = { "heat_sink_chip" },
			},
		},
		{
			name = "Cold Welder",
			blurb = "Keeps range. Doesn't chat.",
			parts = {
				torso = "rusty_cage",
				leftLeg = "workboot_l",
				rightLeg = "workboot_r",
				lowerRight = "rivet_gun",
				shoulderRight = "brick_shoulder",
				battery = "desk_brick",
				cpu = "scrap_cpu",
				drone = "floor_bit",
			},
		},
		{
			name = "Grid Walker",
			blurb = "Longer legs. Still learning.",
			parts = {
				torso = "rusty_cage",
				leftLeg = "sprint_peg_l",
				rightLeg = "sprint_peg_r",
				lowerLeft = "snap_arm",
				shoulderRight = "brick_shoulder",
				battery = "desk_brick",
				cpu = "scrap_cpu",
				chips = { "thick_skin" },
				drone = "floor_bit",
			},
		},
		{
			name = "Dust Shoulder",
			blurb = "Arc Rail practice. Pack runs hot.",
			parts = {
				torso = "rusty_cage",
				leftLeg = "workboot_l",
				rightLeg = "workboot_r",
				lowerLeft = "snap_arm",
				shoulderLeft = "arc_rail",
				battery = "bay_cell",
				cpu = "scrap_cpu",
				chips = { "wire_wrap" },
				drone = "floor_bit",
			},
		},
		{
			name = "Bolt Hungry",
			blurb = "Two arms and a temper.",
			parts = {
				torso = "rusty_cage",
				leftLeg = "workboot_l",
				rightLeg = "workboot_r",
				lowerLeft = "ember_fist",
				lowerRight = "rivet_gun",
				shoulderRight = "brick_shoulder",
				battery = "bay_cell",
				cpu = "scrap_cpu",
				chips = { "thick_skin" },
				drone = "floor_bit",
			},
		},
		{
			name = "Lane Closer",
			blurb = "Closes fast. Don't give space.",
			parts = {
				torso = "rusty_cage",
				leftLeg = "sprint_peg_l",
				rightLeg = "sprint_peg_r",
				lowerLeft = "ember_fist",
				lowerRight = "rivet_gun",
				shoulderRight = "brick_shoulder",
				battery = "bay_cell",
				cpu = "scrap_cpu",
				chips = { "heat_sink_chip" },
				drone = "floor_bit",
			},
		},
		{
			name = "Frame Tester",
			blurb = "Bay QA. Mean on purpose.",
			parts = {
				torso = "plate_box",
				leftLeg = "workboot_l",
				rightLeg = "workboot_r",
				lowerLeft = "snap_arm",
				lowerRight = "rivet_gun",
				shoulderLeft = "arc_rail",
				battery = "bay_cell",
				cpu = "scrap_cpu",
				chips = { "thick_skin" },
				drone = "floor_bit",
			},
		},
		{
			name = "Gate Keeper",
			blurb = "End of the starter ladder. No boss — just better bolts.",
			parts = {
				torso = "plate_box",
				leftLeg = "sprint_peg_l",
				rightLeg = "sprint_peg_r",
				lowerLeft = "ember_fist",
				lowerRight = "rivet_gun",
				shoulderRight = "brick_shoulder",
				battery = "bay_cell",
				cpu = "scrap_cpu",
				chips = { "thick_skin", "heat_sink_chip" },
				drone = "floor_bit",
			},
		},
	}

	local fights: { LadderFight } = {}
	for i, def in defs do
		local p = table.clone(def.parts)
		-- Light random-ish swap on a few fights (deterministic by index).
		if p.lowerLeft then
			p.lowerLeft = maybeSwapWeapon(p.lowerLeft, { "snap_arm", "ember_fist", "rivet_gun" }, i)
		end
		local built = loadout(p)
		local reward = Rewards.forCampaignFight(i, true)
		table.insert(fights, {
			index = i,
			opponent = BattleOpponent.fromNpc(("npc-%02d"):format(i), def.name, ("mech-%02d"):format(i), built),
			rewardCommonWin = reward.common,
			blurb = def.blurb,
		})
	end
	return fights
end

function Ladder.getFight(index: number): LadderFight?
	local all = Ladder.buildFirstSlice()
	return all[index]
end

return Ladder

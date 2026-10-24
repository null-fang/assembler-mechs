-- Campaign ladder stub: ~10 NPC fights, no bosses in first slice.
-- No daily fuel gate for MVP — Battery Life is the combat "fuel".

local BattleOpponent = require(game.ReplicatedStorage.Shared.Modes.BattleOpponent)

export type LadderFight = {
	index: number, -- 1..10 for first slice
	opponent: BattleOpponent.BattleOpponent,
	rewardCommon: number,
}

local Ladder = {}

-- Placeholder NPC names — brief, human. Replace with catalog later.
local NPC_NAMES = {
	"Bay Rookie",
	"Scrap Runner",
	"Hot Rivet",
	"Cold Welder",
	"Grid Walker",
	"Dust Shoulder",
	"Bolt Hungry",
	"Lane Closer",
	"Frame Tester",
	"Gate Keeper",
}

function Ladder.buildFirstSlice(): { LadderFight }
	local fights = {}
	for i, name in NPC_NAMES do
		table.insert(fights, {
			index = i,
			opponent = BattleOpponent.fromNpc(("npc-%02d"):format(i), name, nil),
			rewardCommon = 50 + (i * 10),
		})
	end
	return fights
end

Ladder.FIRST_SLICE_COUNT = 10

return Ladder

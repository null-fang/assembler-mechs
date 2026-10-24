-- Simple NPC brain for campaign fights. Same action space as players.

local Resolver = require(script.Parent.Resolver)
local MechState = require(script.Parent.MechState)
local Types = require(script.Parent.Types)

local NpcBrain = {}

function NpcBrain.pickAction(battle: Resolver.Battle): Types.BattleAction
	local actions = Resolver.listLegalActions(battle)
	assert(#actions > 0, "NPC has no legal actions")

	local self = Resolver.getActive(battle)
	local foe = Resolver.getFoe(battle)

	if self.skipNextTurn then
		return { kind = "EndTurn" }
	end

	-- Prefer the hardest legal shot.
	local bestFire: Types.FireAction? = nil
	local bestDmg = -1
	for _, a in actions do
		if a.kind == "Fire" then
			local w = MechState.findWeapon(self, a.weaponSlot)
			if w and w.stats.damage > bestDmg then
				bestDmg = w.stats.damage
				bestFire = a
			end
		end
	end
	if bestFire then
		return bestFire
	end

	-- No shot: close distance if too far for any weapon; else back off if too close.
	local dist = MechState.distance(self, foe)
	local wantCloser = true
	local minRange = math.huge
	for _, w in self.weapons do
		minRange = math.min(minRange, w.stats.rangeMin)
		if dist >= w.stats.rangeMin and dist <= w.stats.rangeMax then
			wantCloser = false
		end
	end
	if dist < minRange then
		wantCloser = false
	end

	local bestMove: Types.MoveAction? = nil
	local bestScore = -math.huge
	for _, a in actions do
		if a.kind == "Move" then
			local newPos = self.position + a.delta
			local newDist = math.abs(newPos - foe.position)
			local score = if wantCloser then -newDist else newDist
			if score > bestScore then
				bestScore = score
				bestMove = a
			end
		end
	end
	if bestMove and battle.turnBudget.apRemaining > 0 then
		return bestMove
	end

	return { kind = "EndTurn" }
end

-- Run the active NPC until they EndTurn or the fight ends.
function NpcBrain.playTurn(battle: Resolver.Battle): number
	local steps = 0
	while battle.outcome == "Ongoing" do
		local action = NpcBrain.pickAction(battle)
		local ok = Resolver.applyAction(battle, action)
		if not ok then
			Resolver.applyAction(battle, { kind = "EndTurn" })
			steps += 1
			break
		end
		steps += 1
		if action.kind == "EndTurn" then
			break
		end
		if steps > 8 then
			Resolver.applyAction(battle, { kind = "EndTurn" })
			break
		end
	end
	return steps
end

return NpcBrain

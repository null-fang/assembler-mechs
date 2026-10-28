-- Pick-3 crate offers: starter + fight drops. Grants chosen part into inventory.

local Catalog = require(game.ReplicatedStorage.Shared.Parts.Catalog)
local CratePick3 = require(game.ReplicatedStorage.Shared.Parts.CratePick3)
local InventoryService = require(script.Parent.Parent.Parts.InventoryService)

local CrateService = {}

export type OfferCard = {
	index: number,
	partId: string,
	name: string,
	rarity: string,
	slot: string,
	tooltip: string?,
	weight: number,
}

export type PendingOffer = {
	crateId: string,
	source: string, -- "starter" | "fight"
	options: { OfferCard },
}

local pending: { [number]: PendingOffer? } = {}
local starterGranted: { [number]: boolean } = {}
local nextCrate = 1

-- Short pool of spare parts for pick-3 (not the whole catalog dump).
local POOL = {
	"ember_fist",
	"needle_jab",
	"hook_arm",
	"cleaver_arm",
	"drill_punch",
	"spray_can",
	"nail_rack",
	"box_launcher",
	"wire_wrap",
	"grease_film",
	"thick_skin",
	"heat_sink_chip",
	"bay_cell",
	"scrap_cpu",
	"floor_bit",
	"spark_moth",
	"brick_shoulder",
	"arc_rail",
	"plate_box",
	"long_bite",
	"deep_cell",
	"heal_beep",
	"chatter_gun",
	"mace_arm",
	"scout_mite",
	"gale_mg",
	"pulse_moth",
} :: { string }

local function pickThree(seed: number): { string }
	local bag = table.clone(POOL)
	local picks = {}
	local s = seed
	for _ = 1, 3 do
		if #bag == 0 then
			break
		end
		s = (s * 1103515245 + 12345) % 2147483648
		local idx = (s % #bag) + 1
		table.insert(picks, bag[idx])
		table.remove(bag, idx)
	end
	while #picks < 3 do
		table.insert(picks, "wire_wrap")
	end
	return picks
end

local function toCards(partIds: { string }): { OfferCard }
	local cards = {}
	for i, id in partIds do
		local p = Catalog.require(id)
		table.insert(cards, {
			index = i,
			partId = id,
			name = p.name,
			rarity = p.rarity,
			slot = p.slot,
			tooltip = p.tooltip,
			weight = p.weight,
		})
	end
	return cards
end

function CrateService.getPending(userId: number): PendingOffer?
	return pending[userId]
end

function CrateService.hasStarter(userId: number): boolean
	return starterGranted[userId] == true
end

function CrateService.ensureStarter(userId: number): PendingOffer?
	if starterGranted[userId] then
		return pending[userId]
	end
	if pending[userId] then
		return pending[userId]
	end
	local crateId = ("crate-starter-%d"):format(nextCrate)
	nextCrate += 1
	local offer: PendingOffer = {
		crateId = crateId,
		source = "starter",
		options = toCards(pickThree(userId * 13 + 7)),
	}
	pending[userId] = offer
	starterGranted[userId] = true
	return offer
end

function CrateService.grantFightDrop(userId: number, fightIndex: number): PendingOffer?
	-- Don't overwrite an unopened offer; queue as replace only if empty.
	if pending[userId] then
		return nil
	end
	local crateId = ("crate-fight-%d-%d"):format(fightIndex, nextCrate)
	nextCrate += 1
	local offer: PendingOffer = {
		crateId = crateId,
		source = "fight",
		options = toCards(pickThree(userId * 31 + fightIndex * 97)),
	}
	pending[userId] = offer
	return offer
end

function CrateService.pick(userId: number, choiceIndex: number): (boolean, string?, any?)
	local offer = pending[userId]
	if not offer then
		return false, "No crate open", nil
	end
	local defs = {}
	for _, card in offer.options do
		table.insert(defs, Catalog.require(card.partId))
	end
	local result = CratePick3.pick({
		crateId = offer.crateId,
		options = defs,
	}, choiceIndex)
	if not result then
		return false, "Bad pick", nil
	end

	local owned = InventoryService.grantPart(userId, result.chosen.id)
	pending[userId] = nil
	return true, nil, {
		crateId = offer.crateId,
		chosen = {
			uid = owned.uid,
			partId = result.chosen.id,
			name = result.chosen.name,
			rarity = result.chosen.rarity,
			slot = result.chosen.slot,
		},
		inventory = InventoryService.clientSnapshot(userId),
	}
end

function CrateService.clientSnapshot(userId: number)
	local offer = pending[userId]
	return {
		pending = offer,
		starterReady = starterGranted[userId] == true and offer ~= nil and offer.source == "starter",
	}
end

return CrateService

-- Pick-3 crates: reveal 3 cards, keep 1 (Ball vs Ball–style structure).
-- First session: grant/open 3 standard crates (wired later).

local Slots = require(script.Parent.Slots)

export type CrateOffer = {
	crateId: string,
	options: { Slots.PartDef }, -- exactly 3 when rolled
}

export type CratePickResult = {
	crateId: string,
	chosen: Slots.PartDef,
	discarded: { Slots.PartDef },
}

local CratePick3 = {}

-- Stub: caller supplies three rolled parts; player picks index 1–3.
function CratePick3.pick(offer: CrateOffer, choiceIndex: number): CratePickResult?
	if #offer.options ~= 3 then
		return nil
	end
	if choiceIndex < 1 or choiceIndex > 3 then
		return nil
	end
	local chosen = offer.options[choiceIndex]
	local discarded = {}
	for i, part in offer.options do
		if i ~= choiceIndex then
			table.insert(discarded, part)
		end
	end
	return {
		crateId = offer.crateId,
		chosen = chosen,
		discarded = discarded,
	}
end

return CratePick3

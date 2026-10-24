-- Duplicate policy (locked): sell for common currency by part worth.
-- Player-to-player trade is future — stub sell only.

local Currency = require(script.Parent.Currency)
local Slots = require(script.Parent.Parent.Parts.Slots)

export type SellResult = {
	partId: string,
	commonGained: number,
	wallet: Currency.Wallet,
}

local SellDuplicate = {}

function SellDuplicate.sell(part: Slots.PartDef, wallet: Currency.Wallet): SellResult
	local gained = math.max(0, part.sellWorth)
	wallet.common += gained
	return {
		partId = part.id,
		commonGained = gained,
		wallet = wallet,
	}
end

return SellDuplicate

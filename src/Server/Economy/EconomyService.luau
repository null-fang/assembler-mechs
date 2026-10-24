-- Server economy stub: common currency + sell-duplicate path.

local Currency = require(game.ReplicatedStorage.Shared.Economy.Currency)
local SellDuplicate = require(game.ReplicatedStorage.Shared.Economy.SellDuplicate)
local Slots = require(game.ReplicatedStorage.Shared.Parts.Slots)

local EconomyService = {}

-- In-memory wallets for scaffold; replace with DataStore later.
local wallets: { [number]: Currency.Wallet } = {}

function EconomyService.getWallet(userId: number): Currency.Wallet
	local w = wallets[userId]
	if not w then
		w = Currency.empty()
		wallets[userId] = w
	end
	return w
end

function EconomyService.addCommon(userId: number, amount: number)
	local w = EconomyService.getWallet(userId)
	w.common += math.max(0, amount)
end

function EconomyService.sellDuplicate(userId: number, part: Slots.PartDef): SellDuplicate.SellResult
	local w = EconomyService.getWallet(userId)
	return SellDuplicate.sell(part, w)
end

return EconomyService

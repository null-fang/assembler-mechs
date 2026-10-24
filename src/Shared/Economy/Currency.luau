-- Currencies. MVP uses Common heavily; Rare/Premium stubs for later.

export type CurrencyKind = "Common" | "Rare" | "Premium"

export type Wallet = {
	common: number,
	rare: number,
	premium: number,
}

local Currency = {}

function Currency.empty(): Wallet
	return {
		common = 0,
		rare = 0,
		premium = 0,
	}
end

return Currency

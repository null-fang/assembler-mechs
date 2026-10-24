-- Assembler server entry — campaign combat slice.

local Players = game:GetService("Players")

local Remotes = require(script.Remotes)
local Ladder = require(script.Campaign.Ladder)
local Matchmaking = require(script.PvP.Matchmaking)
local CampaignService = require(script.Campaign.CampaignService)
local CombatHost = require(script.Combat.CombatHost)
local EconomyService = require(script.Economy.EconomyService)
local InventoryStub = require(script.Parts.InventoryStub)

Remotes.init()

local firstSlice = Ladder.buildFirstSlice()
print(("[Assembler] Campaign ladder ready: %d NPC fights (no bosses)"):format(#firstSlice))
print("[Assembler] PvP matchmaking stub loaded (shared combat path intact)")

Players.PlayerAdded:Connect(function(player)
	InventoryStub.grantStarter(player.UserId)
	EconomyService.getWallet(player.UserId)
	CampaignService.getProgress(player.UserId)
end)

for _, player in Players:GetPlayers() do
	InventoryStub.grantStarter(player.UserId)
end

Remotes.GetBootstrap.OnServerInvoke = function(player)
	return {
		wallet = EconomyService.getWallet(player.UserId),
		progress = CampaignService.getProgress(player.UserId),
		loadout = InventoryStub.loadoutSummary(player.UserId),
		ladderCount = Ladder.FIRST_SLICE_COUNT,
	}
end

Remotes.ListCampaign.OnServerInvoke = function(player)
	return CampaignService.listFights(player.UserId)
end

Remotes.StartFight.OnServerInvoke = function(player, fightIndex)
	if typeof(fightIndex) ~= "number" then
		return { ok = false, error = "Bad index" }
	end
	local live, err = CampaignService.startFight(player.UserId, player.DisplayName, math.floor(fightIndex))
	if not live then
		return { ok = false, error = err or "Could not start" }
	end
	local snap = CombatHost.snapshot(live)
	Remotes.BattleUpdated:FireClient(player, snap)
	return { ok = true, battle = snap }
end

Remotes.GetBattle.OnServerInvoke = function(player)
	local live = CombatHost.getForUser(player.UserId)
	if not live then
		return { ok = false, error = "No active fight" }
	end
	return { ok = true, battle = CombatHost.snapshot(live) }
end

Remotes.SubmitAction.OnServerInvoke = function(player, action)
	if typeof(action) ~= "table" or typeof(action.kind) ~= "string" then
		return { ok = false, error = "Bad action" }
	end
	local live = CombatHost.getForUser(player.UserId)
	if not live then
		return { ok = false, error = "No active fight" }
	end

	local ok, err = CombatHost.applyPlayerAction(live, action)
	if not ok then
		return { ok = false, error = err or "Rejected", battle = CombatHost.snapshot(live) }
	end

	local snap = CombatHost.snapshot(live)
	Remotes.BattleUpdated:FireClient(player, snap)

	local settled = CampaignService.settleIfFinished(player.UserId, live)
	if settled then
		Remotes.FightSettled:FireClient(player, settled)
		return { ok = true, battle = snap, settled = settled }
	end

	return { ok = true, battle = snap }
end

-- Keep PvP stub reachable without breaking the shared path.
local _ = Matchmaking

print("[Assembler] Server ready — enter a campaign fight from the client HUD")

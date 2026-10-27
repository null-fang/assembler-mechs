-- Assembler server entry — lobby world + campaign combat + mech bay.

local Players = game:GetService("Players")

local Remotes = require(script.Remotes)
local Ladder = require(script.Campaign.Ladder)
local Matchmaking = require(script.PvP.Matchmaking)
local CampaignService = require(script.Campaign.CampaignService)
local CombatHost = require(script.Combat.CombatHost)
local EconomyService = require(script.Economy.EconomyService)
local CrateService = require(script.Economy.CrateService)
local InventoryService = require(script.Parts.InventoryService)
local OnboardingService = require(script.Onboarding.OnboardingService)
local ArenaService = require(script.World.ArenaService)
local LobbyPrompts = require(script.World.LobbyPrompts)
local PlayerSession = require(script.Session.PlayerSession)

Remotes.init()

-- Soft rate limit for turn submits (modern remote hygiene).
local lastSubmitAt: { [number]: number } = {}
local SUBMIT_MIN_GAP = 0.05

task.spawn(function()
	if ArenaService.ensureWorld() then
		print("[Assembler] Lobby + Arenas found — GaragePedestal / PadA / PadB ready")
		LobbyPrompts.wire(Remotes)
	end
end)

local firstSlice = Ladder.buildFirstSlice()
print(("[Assembler] Campaign ladder ready: %d NPC fights (no bosses)"):format(#firstSlice))
print("[Assembler] PvP matchmaking stub loaded (shared combat path intact)")

local function refreshPreview(player: Player)
	CampaignService.rememberDisplayName(player.UserId, player.DisplayName)
	local loadout = InventoryService.activeLoadout(player.UserId)
	ArenaService.spawnGaragePreview(loadout, player.DisplayName)
end

Players.PlayerAdded:Connect(function(player)
	PlayerSession.toLobby(player)
	InventoryService.grantStarter(player.UserId)
	EconomyService.getWallet(player.UserId)
	CampaignService.getProgress(player.UserId)
	OnboardingService.get(player.UserId)
	CrateService.ensureStarter(player.UserId)
	CampaignService.rememberDisplayName(player.UserId, player.DisplayName)
	task.defer(function()
		refreshPreview(player)
	end)
	player.CharacterAdded:Connect(function()
		task.wait(0.5)
		-- Don't yank mid-fight if character respawns during combat.
		if player:GetAttribute("AssemblerPhase") == "Combat" then
			local arenaId = player:GetAttribute("AssemblerArena")
			if typeof(arenaId) == "string" and arenaId ~= "" then
				ArenaService.teleportPlayerToArena(player, arenaId :: any)
				return
			end
		end
		ArenaService.teleportPlayerToLobby(player)
	end)
	if player.Character then
		task.defer(function()
			ArenaService.teleportPlayerToLobby(player)
		end)
	end
end)

for _, player in Players:GetPlayers() do
	InventoryService.grantStarter(player.UserId)
	CrateService.ensureStarter(player.UserId)
	task.defer(function()
		refreshPreview(player)
	end)
end

Remotes.GetBootstrap.OnServerInvoke = function(player)
	return {
		wallet = EconomyService.getWallet(player.UserId),
		progress = CampaignService.getProgress(player.UserId),
		loadout = InventoryService.loadoutSummary(player.UserId),
		inventory = InventoryService.clientSnapshot(player.UserId),
		ladderCount = Ladder.FIRST_SLICE_COUNT,
		activeArena = ArenaService.getActiveArenaId(),
		onboarding = OnboardingService.clientSnapshot(player.UserId),
		crate = CrateService.clientSnapshot(player.UserId),
	}
end

Remotes.CompleteOnboarding.OnServerInvoke = function(player, stepId)
	if typeof(stepId) ~= "string" then
		return OnboardingService.clientSnapshot(player.UserId)
	end
	OnboardingService.complete(player.UserId, stepId)
	return OnboardingService.clientSnapshot(player.UserId)
end

Remotes.GetCrate.OnServerInvoke = function(player)
	CrateService.ensureStarter(player.UserId)
	return CrateService.clientSnapshot(player.UserId)
end

Remotes.PickCrate.OnServerInvoke = function(player, choiceIndex)
	if typeof(choiceIndex) ~= "number" then
		return { ok = false, error = "Bad pick" }
	end
	local ok, err, payload = CrateService.pick(player.UserId, math.floor(choiceIndex))
	if not ok then
		return { ok = false, error = err or "Pick failed" }
	end
	OnboardingService.complete(player.UserId, "crate")
	if payload and payload.inventory then
		Remotes.InventoryUpdated:FireClient(player, payload.inventory)
	end
	refreshPreview(player)
	return {
		ok = true,
		chosen = payload and payload.chosen,
		inventory = payload and payload.inventory,
		onboarding = OnboardingService.clientSnapshot(player.UserId),
	}
end

Remotes.GetInventory.OnServerInvoke = function(player)
	return InventoryService.clientSnapshot(player.UserId)
end

Remotes.EquipPart.OnServerInvoke = function(player, uid, target)
	if typeof(uid) ~= "string" or typeof(target) ~= "string" then
		return { ok = false, error = "Bad args" }
	end
	local ok, err = InventoryService.equip(player.UserId, uid, target)
	if not ok then
		return { ok = false, error = err or "Equip failed" }
	end
	refreshPreview(player)
	local snap = InventoryService.clientSnapshot(player.UserId)
	Remotes.InventoryUpdated:FireClient(player, snap)
	return { ok = true, inventory = snap }
end

Remotes.UnequipPart.OnServerInvoke = function(player, field)
	if typeof(field) ~= "string" then
		return { ok = false, error = "Bad args" }
	end
	local ok, err = InventoryService.unequip(player.UserId, field)
	if not ok then
		return { ok = false, error = err or "Unequip failed" }
	end
	refreshPreview(player)
	local snap = InventoryService.clientSnapshot(player.UserId)
	Remotes.InventoryUpdated:FireClient(player, snap)
	return { ok = true, inventory = snap }
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
	local arenaId = (live :: any).arenaId
	PlayerSession.toCombat(player, arenaId, math.floor(fightIndex))
	if arenaId then
		ArenaService.teleportPlayerToArena(player, arenaId)
	end
	local snap = CombatHost.snapshot(live)
	snap.arenaId = arenaId
	snap.taunt = (live :: any).taunt
	snap.npcName = (live :: any).npcName
	Remotes.BattleUpdated:FireClient(player, snap)
	return { ok = true, battle = snap, arenaId = arenaId }
end

Remotes.GetBattle.OnServerInvoke = function(player)
	local live = CombatHost.getForUser(player.UserId)
	if not live then
		return { ok = false, error = "No active fight" }
	end
	local snap = CombatHost.snapshot(live)
	snap.taunt = (live :: any).taunt
	snap.npcName = (live :: any).npcName
	return { ok = true, battle = snap }
end

Remotes.SubmitAction.OnServerInvoke = function(player, action)
	if typeof(action) ~= "table" or typeof(action.kind) ~= "string" then
		return { ok = false, error = "Bad action" }
	end
	local now = os.clock()
	local prev = lastSubmitAt[player.UserId]
	if prev and now - prev < SUBMIT_MIN_GAP then
		return { ok = false, error = "Slow down" }
	end
	lastSubmitAt[player.UserId] = now

	local live = CombatHost.getForUser(player.UserId)
	if not live then
		return { ok = false, error = "No active fight" }
	end

	local ok, err = CombatHost.applyPlayerAction(live, action)
	if not ok then
		return { ok = false, error = err or "Rejected", battle = CombatHost.snapshot(live) }
	end

	local snap = CombatHost.snapshot(live)
	snap.taunt = (live :: any).taunt
	snap.npcName = (live :: any).npcName
	Remotes.BattleUpdated:FireClient(player, snap)

	local settled = CampaignService.settleIfFinished(player.UserId, live)
	if settled then
		PlayerSession.toLobby(player)
		Remotes.FightSettled:FireClient(player, settled)
		-- Longer hold so banner + reward sheet can land before lobby return.
		task.delay(3.4, function()
			if player.Parent then
				ArenaService.teleportPlayerToLobby(player)
				Remotes.ReturnLobby:FireClient(player, settled)
			end
		end)
		return { ok = true, battle = snap, settled = settled }
	end

	return { ok = true, battle = snap }
end

local _ = Matchmaking

print("[Assembler] Server ready — walk Campaign / Garage / Starter crate")

-- Lobby join chrome + campaign modal + battle overlay.
-- Menus unlock mouse via ModalMouse; combat keeps cursor free for move clicks.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local BattleCamera = require(script.Parent:WaitForChild("BattleCamera"))
local LobbyCamera = require(script.Parent:WaitForChild("LobbyCamera"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))
local JoinHud = require(script.Parent:WaitForChild("JoinHud"))

local CombatHud = {}

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local remotesFolder = ReplicatedStorage:WaitForChild("AssemblerRemotes")
local GetBootstrap = remotesFolder:WaitForChild("GetBootstrap")
local ListCampaign = remotesFolder:WaitForChild("ListCampaign")
local StartFight = remotesFolder:WaitForChild("StartFight")
local SubmitAction = remotesFolder:WaitForChild("SubmitAction")
local BattleUpdated = remotesFolder:WaitForChild("BattleUpdated")
local FightSettled = remotesFolder:WaitForChild("FightSettled")
local OpenCampaign = remotesFolder:WaitForChild("OpenCampaign")
local OpenGarage = remotesFolder:WaitForChild("OpenGarage")
local ReturnLobby = remotesFolder:WaitForChild("ReturnLobby")

local GarageHud

local screen
local campaignRoot
local battleRoot
local statusLabel
local logLabel
local resourceLabel
local actionFolder
local fightButtons
local inBattle = false

local function setStatus(text)
	if statusLabel then
		statusLabel.Text = text
	end
	JoinHud.setStatus(text)
end

local function clearChildren(frame)
	for _, child in frame:GetChildren() do
		if child:IsA("GuiButton") or (child:IsA("TextLabel") and child.Name == "FightRow") then
			child:Destroy()
		end
	end
end

local function refreshBootstrap()
	local ok, boot = pcall(function()
		return GetBootstrap:InvokeServer()
	end)
	if not ok or not boot then
		JoinHud.setWallet("Assembler Bay")
		return
	end
	JoinHud.setWallet(("Common %d · XP %d · Cleared %d/%d"):format(
		boot.wallet.common,
		boot.progress.xp,
		boot.progress.highestCleared,
		boot.ladderCount
	))
	if not inBattle then
		local lo = boot.loadout
		setStatus(("Primary ready: %s · V for look · Campaign / Garage"):format(lo.torso or "mech"))
	end
	if GarageHud and boot.inventory then
		GarageHud.applySnapshot(boot.inventory)
	end
	JoinHud.refresh()
end

local function hideCampaign()
	campaignRoot.Visible = false
	ModalMouse.pop("campaign")
end

local function startFight(index: number)
	setStatus("Deploying…")
	hideCampaign()
	JoinHud.closePanels()
	local result = StartFight:InvokeServer(index)
	if not result or not result.ok then
		setStatus((result and result.error) or "Could not start")
		return
	end
	if result.arenaId then
		LobbyCamera.stop()
		BattleCamera.startForArena(result.arenaId)
	end
	CombatHud.renderBattle(result.battle)
end

function CombatHud.openCampaign()
	if inBattle then
		return
	end
	if GarageHud and GarageHud.isOpen() then
		GarageHud.setOpen(false)
	end
	JoinHud.closePanels()
	campaignRoot.Visible = true
	ModalMouse.push("campaign")
	clearChildren(fightButtons)
	local fights = ListCampaign:InvokeServer()
	local y = 0
	local lockedShown = false
	for _, fight in fights do
		if fight.unlocked then
			local tag = if fight.cleared then " · cleared" else ""
			local arena = if fight.arenaId then (" · " .. fight.arenaId) else ""
			local row = Theme.button(
				fightButtons,
				("%d. %s%s%s  (+%d)"):format(fight.index, fight.name, tag, arena, fight.rewardCommon),
				UDim2.new(1, -8, 0, 34),
				UDim2.new(0, 4, 0, y),
				{ bg = Theme.colors.bgRaised }
			)
			row.Name = "FightRow"
			row.TextXAlignment = Enum.TextXAlignment.Left
			local pad = Instance.new("UIPadding")
			pad.PaddingLeft = UDim.new(0, 10)
			pad.Parent = row
			row.MouseButton1Click:Connect(function()
				startFight(fight.index)
			end)
			row.MouseEnter:Connect(function()
				setStatus(fight.blurb)
			end)
			y += 38
		elseif not lockedShown then
			local row = Theme.label(
				fightButtons,
				("Next: %d. %s — clear an open fight first."):format(fight.index, fight.name),
				UDim2.new(1, -8, 0, 28),
				UDim2.new(0, 4, 0, y),
				13,
				{ color = Theme.colors.textMuted }
			)
			row.Name = "FightRow"
			lockedShown = true
			y += 32
		end
	end
	fightButtons.CanvasSize = UDim2.new(0, 0, 0, y)
	setStatus("Starter mech ready. Pick a fight.")
end

local function formatSide(side)
	return ("%s  HP %d/%d  Temp %d/%d  Bat %d/%d"):format(
		side.displayName,
		side.integrity,
		side.integrityMax,
		side.temperature,
		side.temperatureMax,
		side.battery,
		side.batteryMax
	)
end

local function renderLog(log)
	local lines = {}
	local start = math.max(1, #(log or {}) - 7)
	for i = start, #(log or {}) do
		table.insert(lines, log[i].text)
	end
	logLabel.Text = table.concat(lines, "\n")
end

local function clearActions()
	for _, child in actionFolder:GetChildren() do
		if child:IsA("GuiButton") then
			child:Destroy()
		end
	end
end

local function actionLabel(action)
	if action.kind == "EndTurn" then
		return "End turn"
	elseif action.kind == "Move" then
		local sign = if action.delta > 0 then "+" else ""
		return ("Move %s%d"):format(sign, action.delta)
	elseif action.kind == "Fire" then
		return "Fire " .. action.weaponSlot
	end
	return action.kind
end

local function submit(action)
	local result = SubmitAction:InvokeServer(action)
	if not result or not result.ok then
		setStatus((result and result.error) or "Action failed")
		if result and result.battle then
			CombatHud.renderBattle(result.battle)
		end
		return
	end
	CombatHud.renderBattle(result.battle)
	if result.settled then
		CombatHud.onSettled(result.settled)
	end
end

function CombatHud.renderBattle(battle)
	inBattle = true
	hideCampaign()
	JoinHud.setVisible(false)
	JoinHud.closePanels()
	battleRoot.Visible = true
	ModalMouse.setCombatClickMode(true)
	if GarageHud and GarageHud.isOpen() then
		GarageHud.setOpen(false)
	end
	if battle.arenaId then
		LobbyCamera.stop()
		BattleCamera.startForArena(battle.arenaId)
	end

	local you = if battle.playerSide == "A" then battle.sideA else battle.sideB
	local foe = if battle.playerSide == "A" then battle.sideB else battle.sideA

	resourceLabel.Text = table.concat({
		("%s · Turn %d · AP %d/%d · Range %d"):format(
			battle.arenaId or "Arena",
			battle.turnIndex,
			battle.apRemaining,
			battle.apMax,
			battle.distance
		),
		formatSide(you),
		formatSide(foe),
	}, "\n")

	if you.batteryRechargeMoves and you.batteryRechargeMoves > 0 then
		setStatus(("Energy guns dark — %d moves on charge"):format(you.batteryRechargeMoves))
	elseif you.skipNextTurn then
		setStatus("Overheated — end turn to cool")
	elseif battle.activeSide == battle.playerSide then
		setStatus("Your turn — two actions this turn")
	else
		setStatus("Waiting…")
	end

	renderLog(battle.log or {})
	clearActions()
	if battle.outcome ~= "Ongoing" then
		return
	end

	for i, action in battle.legalActions or {} do
		local col = (i - 1) % 3
		local row = math.floor((i - 1) / 3)
		local btn = Theme.button(
			actionFolder,
			actionLabel(action),
			UDim2.new(0, 120, 0, 32),
			UDim2.new(0, 8 + col * 128, 0, row * 36),
			{ bg = Theme.colors.bgRaised }
		)
		local captured = action
		btn.MouseButton1Click:Connect(function()
			submit(captured)
		end)
	end
end

function CombatHud.onSettled(settled)
	local verb = if settled.won then "Win" else "Loss"
	setStatus(("%s · +%d common · +%d XP — returning to bay…"):format(verb, settled.common, settled.xp))
end

function CombatHud.onReturnLobby(settled)
	inBattle = false
	battleRoot.Visible = false
	JoinHud.setVisible(true)
	ModalMouse.setCombatClickMode(false)
	BattleCamera.stop()
	LobbyCamera.start()
	if settled then
		local verb = if settled.won then "Win" else "Loss"
		setStatus(("%s recorded. +%d common · +%d XP"):format(verb, settled.common, settled.xp))
	end
	refreshBootstrap()
end

function CombatHud.mount(garageModule)
	GarageHud = garageModule

	screen = Instance.new("ScreenGui")
	screen.Name = "AssemblerHud"
	screen.ResetOnSpawn = false
	screen.IgnoreGuiInset = true
	screen.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	screen.Parent = playerGui

	ModalMouse.bind(screen)
	ModalMouse.onStateChanged(function(menuOpen, combat)
		LobbyCamera.setMenuBlocking(menuOpen or combat)
	end)

	if GarageHud then
		GarageHud.mount(screen)
	end

	JoinHud.mount(screen, {
		openCampaign = function()
			CombatHud.openCampaign()
		end,
		openGarage = function()
			if GarageHud then
				GarageHud.setOpen(true)
			end
		end,
		isBusy = function()
			return inBattle
		end,
	})

	-- Hidden status sink used during battle (Join bar hidden)
	statusLabel = Instance.new("TextLabel")
	statusLabel.Name = "StatusSink"
	statusLabel.Size = UDim2.new(0, 0, 0, 0)
	statusLabel.BackgroundTransparency = 1
	statusLabel.TextTransparency = 1
	statusLabel.Text = ""
	statusLabel.Parent = screen

	-- Campaign panel
	campaignRoot = Theme.panel(screen, "CampaignPanel", UDim2.new(0, 400, 0, 440), UDim2.new(0, 24, 0.5, -220))
	campaignRoot.Visible = false

	Theme.label(campaignRoot, "Campaign", UDim2.new(1, -16, 0, 26), UDim2.new(0, 14, 0, 12), 18, {
		font = Theme.fonts.title,
		color = Theme.colors.cyan,
	})
	Theme.label(
		campaignRoot,
		"Open fights only. Starter mech is already yours.",
		UDim2.new(1, -28, 0, 36),
		UDim2.new(0, 14, 0, 40),
		12,
		{ color = Theme.colors.textDim }
	)

	local campaignFrame = Instance.new("Frame")
	campaignFrame.Size = UDim2.new(1, -16, 1, -110)
	campaignFrame.Position = UDim2.new(0, 8, 0, 82)
	campaignFrame.BackgroundTransparency = 1
	campaignFrame.Parent = campaignRoot

	fightButtons = Instance.new("ScrollingFrame")
	fightButtons.Size = UDim2.new(1, 0, 1, 0)
	fightButtons.BackgroundTransparency = 1
	fightButtons.ScrollBarThickness = 4
	fightButtons.BorderSizePixel = 0
	fightButtons.CanvasSize = UDim2.new(0, 0, 0, 0)
	fightButtons.Parent = campaignFrame

	local closeC = Theme.button(campaignRoot, "Close", UDim2.new(0, 72, 0, 28), UDim2.new(1, -86, 1, -42), {
		bg = Theme.colors.bgInset,
	})
	closeC.MouseButton1Click:Connect(function()
		hideCampaign()
		refreshBootstrap()
	end)

	-- Battle overlay (bottom-left) — mouse free via combat click mode
	battleRoot = Theme.panel(screen, "BattlePanel", UDim2.new(0, 420, 0, 320), UDim2.new(0, 16, 1, -336))
	battleRoot.Visible = false

	resourceLabel = Theme.label(battleRoot, "", UDim2.new(1, -16, 0, 70), UDim2.new(0, 8, 0, 8), 12)
	logLabel = Theme.label(battleRoot, "", UDim2.new(1, -16, 0, 100), UDim2.new(0, 8, 0, 80), 12, {
		color = Theme.colors.textDim,
	})
	actionFolder = Instance.new("Frame")
	actionFolder.Size = UDim2.new(1, -8, 0, 110)
	actionFolder.Position = UDim2.new(0, 0, 0, 190)
	actionFolder.BackgroundTransparency = 1
	actionFolder.Parent = battleRoot

	OpenCampaign.OnClientEvent:Connect(function()
		CombatHud.openCampaign()
	end)
	OpenGarage.OnClientEvent:Connect(function()
		if GarageHud then
			GarageHud.setOpen(true)
		end
	end)
	BattleUpdated.OnClientEvent:Connect(function(battle)
		CombatHud.renderBattle(battle)
	end)
	FightSettled.OnClientEvent:Connect(function(settled)
		CombatHud.onSettled(settled)
	end)
	ReturnLobby.OnClientEvent:Connect(function(settled)
		CombatHud.onReturnLobby(settled)
	end)

	LobbyCamera.start()
	refreshBootstrap()
	print("[Assembler] Join HUD + third-person lobby camera (V toggles look)")
end

return CombatHud

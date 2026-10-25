-- Lobby join chrome + campaign modal + battle overlay with real bars + move cards.
-- Menus unlock mouse via ModalMouse; combat keeps cursor free for move clicks.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local BattleCamera = require(script.Parent:WaitForChild("BattleCamera"))
local LobbyCamera = require(script.Parent:WaitForChild("LobbyCamera"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))
local JoinHud = require(script.Parent:WaitForChild("JoinHud"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))
local TweenUtil = require(script.Parent:WaitForChild("UI"):WaitForChild("TweenUtil"))
local ResourceBar = require(script.Parent:WaitForChild("UI"):WaitForChild("ResourceBar"))
local Tooltip = require(script.Parent:WaitForChild("UI"):WaitForChild("Tooltip"))

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
local campaignRest = UDim2.new(0, 24, 0.5, -230)
local fightList: ScrollingFrame
local battleRoot
local battleRest = UDim2.new(0, 18, 1, -358)
local statusSink
local logLabel
local headerMeta: TextLabel
local actionFolder
local youBlock
local foeBlock
local inBattle = false

local function setStatus(text)
	if statusSink then
		statusSink.Text = text
	end
	JoinHud.setStatus(text)
end

local function clearFightRows()
	for _, child in fightList:GetChildren() do
		if child:IsA("GuiObject") and not child:IsA("UIListLayout") and not child:IsA("UIPadding") then
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
	if not campaignRoot.Visible then
		ModalMouse.pop("campaign")
		return
	end
	ModalMouse.pop("campaign")
	TweenUtil.closeTo(
		campaignRoot,
		UDim2.new(0, campaignRest.X.Offset - 20, 0.5, campaignRest.Y.Offset),
		campaignRest,
		function()
			campaignRoot.BackgroundTransparency = Theme.transparency.panel
		end
	)
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
	ModalMouse.push("campaign")
	clearFightRows()
	local fights = ListCampaign:InvokeServer()
	local lockedShown = false
	local order = 0
	for _, fight in fights do
		order += 1
		if fight.unlocked then
			local card = Instance.new("Frame")
			card.Name = "Fight_" .. tostring(fight.index)
			card.Size = UDim2.new(1, -6, 0, 66)
			card.BackgroundColor3 = Theme.colors.bgRaised
			card.BorderSizePixel = 0
			card.LayoutOrder = order
			card.Parent = fightList
			Theme.corner(card, Theme.radii.sm)
			Theme.stroke(card, if fight.cleared then Theme.colors.cyanDeep else Theme.colors.stroke, 1)

			local idx = Instance.new("TextLabel")
			idx.Size = UDim2.new(0, 36, 0, 36)
			idx.Position = UDim2.new(0, 10, 0.5, -18)
			idx.BackgroundColor3 = if fight.cleared then Theme.colors.cyanDeep else Theme.colors.bgInset
			idx.BorderSizePixel = 0
			idx.Font = Theme.fonts.title
			idx.TextSize = 18
			idx.TextColor3 = if fight.cleared then Theme.colors.text else Theme.colors.cyan
			idx.Text = tostring(fight.index)
			idx.Parent = card
			Theme.corner(idx, Theme.radii.sm)

			Theme.label(card, fight.name, UDim2.new(1, -170, 0, 22), UDim2.new(0, 56, 0, 10), 14, {
				font = Theme.fonts.button,
			})
			local bits = {}
			if fight.arenaId then
				table.insert(bits, fight.arenaId)
			end
			if fight.cleared then
				table.insert(bits, "cleared")
			end
			Theme.label(card, table.concat(bits, " · "), UDim2.new(1, -170, 0, 18), UDim2.new(0, 56, 0, 34), 11, {
				color = Theme.colors.textDim,
			})

			local reward = Instance.new("TextLabel")
			reward.Size = UDim2.new(0, 70, 0, 22)
			reward.Position = UDim2.new(1, -82, 0, 10)
			reward.BackgroundColor3 = Theme.colors.bgInset
			reward.BorderSizePixel = 0
			reward.Font = Theme.fonts.mono
			reward.TextSize = 11
			reward.TextColor3 = Theme.colors.accent
			reward.Text = ("+%d"):format(fight.rewardCommon or 0)
			reward.Parent = card
			Theme.corner(reward, Theme.radii.sm)

			local deploy = Button.create(
				card,
				if fight.cleared then "Replay" else "Fight",
				UDim2.new(0, 70, 0, 26),
				UDim2.new(1, -82, 1, -34),
				if fight.cleared then "secondary" else "cyan"
			)
			local index = fight.index
			local blurb = fight.blurb or "Deploy and fight."
			Tooltip.attach(deploy, blurb)
			deploy.MouseButton1Click:Connect(function()
				startFight(index)
			end)
			card.MouseEnter:Connect(function()
				setStatus(blurb)
			end)
		elseif not lockedShown then
			lockedShown = true
			local hint = Theme.label(
				fightList,
				("Next: %d. %s — clear an open fight first."):format(fight.index, fight.name),
				UDim2.new(1, -6, 0, 32),
				UDim2.new(0, 0, 0, 0),
				12,
				{ color = Theme.colors.textMuted }
			)
			hint.Name = "NextLocked"
			hint.LayoutOrder = order
		end
	end
	setStatus("Starter mech ready. Pick a fight.")
	campaignRoot.BackgroundTransparency = Theme.transparency.panel
	TweenUtil.openFrom(
		campaignRoot,
		UDim2.new(0, campaignRest.X.Offset - 28, 0.5, campaignRest.Y.Offset),
		campaignRest,
		Theme.transparency.panel
	)
end

local function renderLog(log)
	local lines = {}
	local start = math.max(1, #(log or {}) - 5)
	for i = start, #(log or {}) do
		table.insert(lines, log[i].text)
	end
	logLabel.Text = table.concat(lines, "\n")
end

local function clearActions()
	for _, child in actionFolder:GetChildren() do
		if child:IsA("GuiObject") and not child:IsA("UIGridLayout") then
			child:Destroy()
		end
	end
end

local function actionTitle(action): string
	if action.kind == "EndTurn" then
		return "End turn"
	elseif action.kind == "Move" then
		local sign = if action.delta > 0 then "+" else ""
		return ("Move %s%d"):format(sign, action.delta)
	elseif action.kind == "Fire" then
		return "Fire"
	end
	return action.kind
end

local function actionSubtitle(action, you): string
	if action.kind == "EndTurn" then
		return "Cool & recharge"
	elseif action.kind == "Move" then
		return "1 AP · step the lane"
	elseif action.kind == "Fire" then
		local slot = action.weaponSlot
		if you and you.weapons then
			for _, w in you.weapons do
				if w.slot == slot then
					return ("%s · %s %d"):format(w.name, w.damageType, w.damage)
				end
			end
		end
		return slot or "Weapon"
	end
	return ""
end

local function actionTip(action, you): string
	if action.kind == "EndTurn" then
		return "End your turn. Cool down a bit."
	elseif action.kind == "Move" then
		return "Step along the lane."
	elseif action.kind == "Fire" then
		local slot = action.weaponSlot
		if you and you.weapons then
			for _, w in you.weapons do
				if w.slot == slot then
					return w.tooltip or w.name
				end
			end
		end
		return "Fire weapon"
	end
	return ""
end

local function actionAccent(action): Color3
	if action.kind == "EndTurn" then
		return Theme.colors.accent
	elseif action.kind == "Move" then
		return Theme.colors.cyan
	elseif action.kind == "Fire" then
		return Theme.colors.danger
	end
	return Theme.colors.strokeBright
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
	if campaignRoot.Visible then
		campaignRoot.Visible = false
		campaignRoot.Position = campaignRest
		ModalMouse.pop("campaign")
	end
	JoinHud.setVisible(false)
	JoinHud.closePanels()
	if not battleRoot.Visible then
		TweenUtil.openFrom(
			battleRoot,
			UDim2.new(0, battleRest.X.Offset, 1, battleRest.Y.Offset + 28),
			battleRest,
			Theme.transparency.panel
		)
	else
		battleRoot.Visible = true
	end
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

	headerMeta.Text = ("%s · Turn %d · AP %d/%d · Range %d"):format(
		battle.arenaId or "Arena",
		battle.turnIndex,
		battle.apRemaining,
		battle.apMax,
		battle.distance
	)
	youBlock.setFromSide(you)
	foeBlock.setFromSide(foe)
	renderLog(battle.log or {})

	if you.batteryRechargeMoves and you.batteryRechargeMoves > 0 then
		setStatus(("Energy guns dark — %d moves on charge"):format(you.batteryRechargeMoves))
	elseif you.skipNextTurn then
		setStatus("Overheated — end turn to cool")
	elseif battle.activeSide == battle.playerSide then
		setStatus("Your turn — two actions")
	else
		setStatus("Waiting…")
	end

	clearActions()
	if battle.outcome ~= "Ongoing" then
		return
	end

	for i, action in battle.legalActions or {} do
		local card = Instance.new("TextButton")
		card.Name = "Action_" .. i
		card.BackgroundColor3 = Theme.colors.bgRaised
		card.BorderSizePixel = 0
		card.AutoButtonColor = false
		card.Text = ""
		card.LayoutOrder = i
		card.Parent = actionFolder
		Theme.corner(card, Theme.radii.sm)
		local stroke = Theme.stroke(card, Theme.colors.stroke, 1)

		local accent = Instance.new("Frame")
		accent.Size = UDim2.new(0, 3, 1, 0)
		accent.BackgroundColor3 = actionAccent(action)
		accent.BorderSizePixel = 0
		accent.Parent = card

		local title = Instance.new("TextLabel")
		title.Size = UDim2.new(1, -14, 0, 18)
		title.Position = UDim2.new(0, 10, 0, 4)
		title.BackgroundTransparency = 1
		title.Font = Theme.fonts.button
		title.TextSize = 13
		title.TextColor3 = Theme.colors.text
		title.TextXAlignment = Enum.TextXAlignment.Left
		title.Text = actionTitle(action)
		title.Parent = card

		local sub = Instance.new("TextLabel")
		sub.Size = UDim2.new(1, -14, 0, 16)
		sub.Position = UDim2.new(0, 10, 0, 22)
		sub.BackgroundTransparency = 1
		sub.Font = Theme.fonts.body
		sub.TextSize = 10
		sub.TextColor3 = Theme.colors.textDim
		sub.TextXAlignment = Enum.TextXAlignment.Left
		sub.TextTruncate = Enum.TextTruncate.AtEnd
		sub.Text = actionSubtitle(action, you)
		sub.Parent = card

		Tooltip.attach(card, actionTip(action, you))

		local captured = action
		local hovering = false
		card.MouseEnter:Connect(function()
			hovering = true
			TweenUtil.play(card, Theme.tween.hover, { BackgroundColor3 = Theme.colors.bgHover })
			TweenUtil.play(stroke, Theme.tween.hover, { Color = Theme.colors.strokeFocus })
		end)
		card.MouseLeave:Connect(function()
			hovering = false
			TweenUtil.play(card, Theme.tween.hover, { BackgroundColor3 = Theme.colors.bgRaised })
			TweenUtil.play(stroke, Theme.tween.hover, { Color = Theme.colors.stroke })
		end)
		card.MouseButton1Down:Connect(function()
			TweenUtil.play(card, Theme.tween.press, { BackgroundColor3 = Theme.colors.bgPress })
		end)
		card.MouseButton1Up:Connect(function()
			TweenUtil.play(card, Theme.tween.press, {
				BackgroundColor3 = if hovering then Theme.colors.bgHover else Theme.colors.bgRaised,
			})
		end)
		card.MouseButton1Click:Connect(function()
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
	battleRoot.Position = battleRest
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
	Tooltip.bind(screen)
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

	statusSink = Instance.new("TextLabel")
	statusSink.Name = "StatusSink"
	statusSink.Size = UDim2.new(0, 0, 0, 0)
	statusSink.BackgroundTransparency = 1
	statusSink.TextTransparency = 1
	statusSink.Text = ""
	statusSink.Parent = screen

	-- Campaign panel — fight cards, unlocked only + one next hint
	campaignRoot = Theme.panel(screen, "CampaignPanel", UDim2.new(0, 400, 0, 460), campaignRest, Theme.colors.cyan)
	campaignRoot.Visible = false

	Theme.label(campaignRoot, "CAMPAIGN", UDim2.new(1, -100, 0, 24), UDim2.new(0, 16, 0, 12), 18, {
		font = Theme.fonts.display,
		color = Theme.colors.cyan,
	})
	Theme.label(
		campaignRoot,
		"Open fights only. Starter mech is already yours.",
		UDim2.new(1, -28, 0, 32),
		UDim2.new(0, 16, 0, 40),
		12,
		{ color = Theme.colors.textDim }
	)

	fightList = Instance.new("ScrollingFrame")
	fightList.Name = "Fights"
	fightList.Size = UDim2.new(1, -20, 1, -110)
	fightList.Position = UDim2.new(0, 10, 0, 78)
	fightList.BackgroundTransparency = 1
	fightList.ScrollBarThickness = 3
	fightList.ScrollBarImageColor3 = Theme.colors.cyanDeep
	fightList.BorderSizePixel = 0
	fightList.AutomaticCanvasSize = Enum.AutomaticSize.Y
	fightList.CanvasSize = UDim2.new(0, 0, 0, 0)
	fightList.Parent = campaignRoot
	local fightLayout = Instance.new("UIListLayout")
	fightLayout.Padding = UDim.new(0, 8)
	fightLayout.SortOrder = Enum.SortOrder.LayoutOrder
	fightLayout.Parent = fightList

	local closeC = Button.create(campaignRoot, "Close", UDim2.new(0, 72, 0, 28), UDim2.new(1, -86, 1, -42), "ghost")
	closeC.MouseButton1Click:Connect(function()
		hideCampaign()
		refreshBootstrap()
	end)

	-- Battle overlay — resource bars + move cards
	battleRoot = Theme.panel(screen, "BattlePanel", UDim2.new(0, 520, 0, 340), battleRest, Theme.colors.danger)
	battleRoot.Visible = false

	Theme.label(battleRoot, "COMBAT", UDim2.new(0, 120, 0, 20), UDim2.new(0, 16, 0, 10), 16, {
		font = Theme.fonts.display,
		color = Theme.colors.danger,
	})
	headerMeta = Theme.label(battleRoot, "", UDim2.new(1, -28, 0, 16), UDim2.new(0, 16, 0, 34), 11, {
		font = Theme.fonts.mono,
		color = Theme.colors.cyan,
	})

	youBlock = ResourceBar.sideBlock(battleRoot, "You", UDim2.new(0.5, -16, 0, 90), UDim2.new(0, 12, 0, 56))
	foeBlock = ResourceBar.sideBlock(battleRoot, "Foe", UDim2.new(0.5, -16, 0, 90), UDim2.new(0.5, 4, 0, 56))

	logLabel = Instance.new("TextLabel")
	logLabel.Name = "Log"
	logLabel.Size = UDim2.new(1, -24, 0, 70)
	logLabel.Position = UDim2.new(0, 12, 0, 154)
	logLabel.BackgroundColor3 = Theme.colors.bgInset
	logLabel.BackgroundTransparency = 0.15
	logLabel.BorderSizePixel = 0
	logLabel.Font = Theme.fonts.body
	logLabel.TextSize = 11
	logLabel.TextColor3 = Theme.colors.textDim
	logLabel.TextXAlignment = Enum.TextXAlignment.Left
	logLabel.TextYAlignment = Enum.TextYAlignment.Top
	logLabel.TextWrapped = true
	logLabel.Text = ""
	logLabel.Parent = battleRoot
	Theme.corner(logLabel, Theme.radii.sm)
	local logPad = Instance.new("UIPadding")
	logPad.PaddingTop = UDim.new(0, 6)
	logPad.PaddingLeft = UDim.new(0, 8)
	logPad.PaddingRight = UDim.new(0, 8)
	logPad.Parent = logLabel

	actionFolder = Instance.new("Frame")
	actionFolder.Name = "Actions"
	actionFolder.Size = UDim2.new(1, -20, 0, 100)
	actionFolder.Position = UDim2.new(0, 10, 0, 232)
	actionFolder.BackgroundTransparency = 1
	actionFolder.Parent = battleRoot
	local grid = Instance.new("UIGridLayout")
	grid.CellSize = UDim2.new(0, 158, 0, 44)
	grid.CellPadding = UDim2.new(0, 8, 0, 8)
	grid.SortOrder = Enum.SortOrder.LayoutOrder
	grid.Parent = actionFolder

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
	print("[Assembler] UI redesign — Theme panels, rarity, bars, ModalMouse intact")
end

return CombatHud

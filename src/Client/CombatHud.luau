-- Lobby join chrome + campaign modal + battle overlay with real bars + move cards.
-- Menus unlock mouse via ModalMouse; combat keeps cursor free for move clicks.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local BattleCamera = require(script.Parent:WaitForChild("BattleCamera"))
local LobbyCamera = require(script.Parent:WaitForChild("LobbyCamera"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))
local JoinHud = require(script.Parent:WaitForChild("JoinHud"))
local TopbarHud = require(script.Parent:WaitForChild("TopbarHud"))
local SessionBridge = require(script.Parent:WaitForChild("SessionBridge"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))
local TweenUtil = require(script.Parent:WaitForChild("UI"):WaitForChild("TweenUtil"))
local Motions = require(script.Parent:WaitForChild("UI"):WaitForChild("Motions"))
local ResourceBar = require(script.Parent:WaitForChild("UI"):WaitForChild("ResourceBar"))
local Tooltip = require(script.Parent:WaitForChild("UI"):WaitForChild("Tooltip"))
local CombatJuice = require(script.Parent:WaitForChild("CombatJuice"))
local RewardSheet = require(script.Parent:WaitForChild("RewardSheet"))
local CrateHud = require(script.Parent:WaitForChild("CrateHud"))
local OnboardingHud = require(script.Parent:WaitForChild("OnboardingHud"))
local DailyHud = require(script.Parent:WaitForChild("DailyHud"))
local PvpHud = require(script.Parent:WaitForChild("PvpHud"))
local SoundHooks = require(script.Parent:WaitForChild("UI"):WaitForChild("SoundHooks"))
local Elements = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Combat"):WaitForChild("Elements"))

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
local OpenCrate = remotesFolder:WaitForChild("OpenCrate")
local ReturnLobby = remotesFolder:WaitForChild("ReturnLobby")

local GarageHud
local tauntLabel: TextLabel?

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
local apPips: Frame?
local turnHint: TextLabel?
local lastPlayerTurn: boolean? = nil
local inBattle = false

local function setStatus(text)
	if statusSink then
		statusSink.Text = text
	end
	JoinHud.setStatus(text)
end

local function renderApPips(remaining: number, maxAp: number)
	if not apPips then
		return
	end
	for _, child in apPips:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	local n = math.max(1, maxAp or 2)
	for i = 1, n do
		local pip = Instance.new("Frame")
		pip.Size = UDim2.new(0, 14, 0, 14)
		pip.BackgroundColor3 = if i <= remaining then Theme.colors.accent else Theme.colors.bgInset
		pip.BorderSizePixel = 0
		pip.LayoutOrder = i
		pip.Parent = apPips
		Theme.corner(pip, 7)
		Theme.stroke(pip, if i <= remaining then Theme.colors.accentSoft else Theme.colors.stroke, 1)
	end
end

local function makeSilhouette(parent: Instance, silhouette: any?, cleared: boolean)
	local host = Instance.new("Frame")
	host.Size = UDim2.new(0, 44, 0, 52)
	host.Position = UDim2.new(0, 8, 0.5, -26)
	host.BackgroundColor3 = Theme.colors.silhouette
	host.BorderSizePixel = 0
	host.Parent = parent
	Theme.corner(host, Theme.radii.sm)
	Theme.stroke(host, if cleared then Theme.colors.cyanDeep else Theme.colors.silhouetteStroke, 1)
	local torso = Instance.new("Frame")
	torso.Size = UDim2.new(0, 18, 0, 20)
	torso.Position = UDim2.new(0.5, -9, 0, 10)
	torso.BackgroundColor3 = Theme.colors.strokeBright
	torso.BackgroundTransparency = 0.25
	torso.BorderSizePixel = 0
	torso.Parent = host
	Theme.corner(torso, 2)
	local head = Instance.new("Frame")
	head.Size = UDim2.new(0, 10, 0, 8)
	head.Position = UDim2.new(0.5, -5, 0, 3)
	head.BackgroundColor3 = Theme.colors.strokeBright
	head.BackgroundTransparency = 0.2
	head.BorderSizePixel = 0
	head.Parent = host
	local legL = Instance.new("Frame")
	legL.Size = UDim2.new(0, 6, 0, 12)
	legL.Position = UDim2.new(0.5, -10, 0, 32)
	legL.BackgroundColor3 = Theme.colors.stroke
	legL.BorderSizePixel = 0
	legL.Parent = host
	local legR = Instance.new("Frame")
	legR.Size = UDim2.new(0, 6, 0, 12)
	legR.Position = UDim2.new(0.5, 4, 0, 32)
	legR.BackgroundColor3 = Theme.colors.stroke
	legR.BorderSizePixel = 0
	legR.Parent = host
	if silhouette and silhouette.hasShoulder then
		local shoulder = Instance.new("Frame")
		shoulder.Size = UDim2.new(0, 8, 0, 6)
		shoulder.Position = UDim2.new(0.5, 6, 0, 12)
		shoulder.BackgroundColor3 = Theme.colors.accentSoft
		shoulder.BackgroundTransparency = 0.3
		shoulder.BorderSizePixel = 0
		shoulder.Parent = host
	end
	if silhouette and silhouette.hasDrone then
		local drone = Instance.new("Frame")
		drone.Size = UDim2.new(0, 7, 0, 7)
		drone.Position = UDim2.new(0, 4, 0, 6)
		drone.BackgroundColor3 = Theme.colors.cyan
		drone.BackgroundTransparency = 0.35
		drone.BorderSizePixel = 0
		drone.Parent = host
		Theme.corner(drone, 3)
	end
	if cleared then
		local check = Instance.new("TextLabel")
		check.Size = UDim2.new(1, 0, 0, 14)
		check.Position = UDim2.new(0, 0, 1, -14)
		check.BackgroundTransparency = 1
		check.Font = Theme.fonts.mono
		check.TextSize = 10
		check.TextColor3 = Theme.colors.cyan
		check.Text = "OK"
		check.Parent = host
	end
end

local function rewardChip(parent: Instance, text: string, color: Color3, x: number, y: number, width: number?)
	local f = Instance.new("Frame")
	f.Size = UDim2.new(0, width or 58, 0, 18)
	f.Position = UDim2.new(1, x, 0, y)
	f.BackgroundColor3 = Theme.colors.bgInset
	f.BorderSizePixel = 0
	f.Parent = parent
	Theme.corner(f, Theme.radii.sm)
	Theme.stroke(f, color, 1)
	local l = Instance.new("TextLabel")
	l.Size = UDim2.new(1, 0, 1, 0)
	l.BackgroundTransparency = 1
	l.Font = Theme.fonts.mono
	l.TextSize = 10
	l.TextColor3 = color
	l.Text = text
	l.Parent = f
end

local function threatPips(parent: Instance, threat: number, x: number, y: number)
	local n = math.clamp(threat or 1, 1, 5)
	for i = 1, 5 do
		local pip = Instance.new("Frame")
		pip.Size = UDim2.new(0, 8, 0, 8)
		pip.Position = UDim2.new(0, x + (i - 1) * 10, 0, y)
		pip.BackgroundColor3 = if i <= n then Theme.colors.danger else Theme.colors.bgInset
		pip.BorderSizePixel = 0
		pip.Parent = parent
		Theme.corner(pip, 4)
	end
end

local function elementRow(parent: Instance, elements: { string }?, x: number, y: number)
	if not elements then
		return
	end
	for i, dt in elements do
		local chip = Instance.new("TextLabel")
		chip.Size = UDim2.new(0, 40, 0, 14)
		chip.Position = UDim2.new(0, x + (i - 1) * 44, 0, y)
		chip.BackgroundColor3 = Theme.colors.bgInset
		chip.BackgroundTransparency = 0.2
		chip.BorderSizePixel = 0
		chip.Font = Theme.fonts.mono
		chip.TextSize = 9
		chip.TextColor3 = Elements.color(dt :: any)
		chip.Text = Elements.SHORT[dt] or dt
		chip.Parent = parent
		Theme.corner(chip, 3)
		Theme.stroke(chip, Elements.color(dt :: any), 1)
	end
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
	TopbarHud.apply(boot.wallet, boot.progress)
	JoinHud.setWallet(("Common %d · Rare %d · Cleared %d/%d"):format(
		boot.wallet.common,
		boot.wallet.rare or 0,
		boot.progress.highestCleared,
		boot.ladderCount
	))
	if not inBattle then
		local lo = boot.loadout
		setStatus(("Primary ready: %s · Campaign / Garage / Crate"):format(lo.torso or "mech"))
	end
	if GarageHud and boot.inventory then
		GarageHud.applySnapshot(boot.inventory)
	end
	if boot.onboarding then
		OnboardingHud.apply(boot.onboarding)
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
	if CrateHud.isOpen() then
		CrateHud.setOpen(false)
	end
	JoinHud.closePanels()
	ModalMouse.push("campaign")
	OnboardingHud.notifyOpened("campaign")
	clearFightRows()
	local fights = ListCampaign:InvokeServer()
	local order = 0
	for _, fight in fights do
		order += 1
		local card = Instance.new("Frame")
		card.Name = "Fight_" .. tostring(fight.index)
		card.Size = UDim2.new(1, -6, 0, 96)
		card.BackgroundColor3 = if fight.unlocked then Theme.colors.bgRaised else Theme.colors.locked
		card.BorderSizePixel = 0
		card.LayoutOrder = order
		card.Parent = fightList
		Theme.corner(card, Theme.radii.sm)
		local strokeColor = Theme.colors.stroke
		if fight.nextUp then
			strokeColor = Theme.colors.accent
		elseif fight.cleared then
			strokeColor = Theme.colors.cyanDeep
		elseif fight.unlocked then
			strokeColor = Theme.colors.strokeBright
		end
		Theme.stroke(card, strokeColor, if fight.nextUp or (fight.unlocked and not fight.cleared) then 1.5 else 1)

		makeSilhouette(card, fight.silhouette, fight.cleared == true)

		local titleBits = ("%d. %s"):format(fight.index, fight.name)
		if fight.pacing then
			titleBits ..= (" · %s"):format(fight.pacing)
		end
		Theme.label(
			card,
			titleBits,
			UDim2.new(1, -200, 0, 18),
			UDim2.new(0, 60, 0, 6),
			13,
			{
				font = Theme.fonts.button,
				color = if fight.unlocked then Theme.colors.text else Theme.colors.textMuted,
			}
		)
		threatPips(card, fight.threat or 1, 60, 26)
		elementRow(card, fight.elements, 118, 24)

		local bits = {}
		if fight.taunt and fight.taunt ~= "" then
			table.insert(bits, '"' .. fight.taunt .. '"')
		elseif fight.blurb then
			table.insert(bits, fight.blurb)
		end
		if fight.nextUp then
			table.insert(bits, "NEXT")
		elseif fight.cleared then
			table.insert(bits, "cleared")
		elseif not fight.unlocked then
			table.insert(bits, "locked")
		end
		Theme.label(card, table.concat(bits, " · "), UDim2.new(1, -200, 0, 28), UDim2.new(0, 60, 0, 40), 11, {
			color = Theme.colors.textDim,
		})
		local paceLine = if fight.guaranteedCrateWin
			then ("Win crate locked · loss ~+%d"):format(fight.rewardCommonLoss or 12)
			else ("Loss ~+%d common"):format(fight.rewardCommonLoss or 12)
		Theme.label(card, paceLine, UDim2.new(1, -200, 0, 16), UDim2.new(0, 60, 0, 68), 10, {
			color = Theme.colors.textMuted,
		})

		rewardChip(card, ("+%d"):format(fight.rewardCommon or 0), Theme.colors.commonCoin, -140, 6)
		rewardChip(card, ("+%d XP"):format(fight.rewardXp or 0), Theme.colors.xpFill, -76, 6)
		if fight.guaranteedCrateWin then
			rewardChip(card, "CRATE", Theme.colors.accent, -140, 28, 58)
		end

		if fight.unlocked then
			local deploy = Button.create(
				card,
				if fight.cleared then "Replay" else "Fight",
				UDim2.new(0, 70, 0, 26),
				UDim2.new(1, -82, 1, -34),
				if fight.cleared then "secondary" else "cyan"
			)
			local index = fight.index
			local blurb = fight.blurb or "Deploy and fight."
			local tip = blurb
			if fight.winHint then
				tip ..= "\nWin: " .. fight.winHint
			end
			if fight.lossHint then
				tip ..= "\nLoss: " .. fight.lossHint
			end
			Tooltip.attach(deploy, tip)
			deploy.MouseButton1Click:Connect(function()
				SoundHooks.play("click")
				startFight(index)
			end)
			card.MouseEnter:Connect(function()
				setStatus(blurb)
			end)
		else
			Theme.label(card, "LOCKED", UDim2.new(0, 70, 0, 18), UDim2.new(1, -82, 1, -32), 11, {
				font = Theme.fonts.mono,
				color = Theme.colors.textMuted,
				align = Enum.TextXAlignment.Center,
			})
		end
	end
	setStatus("Pick a fight. Mid-ladder crates on 3 / 5 / 7 / 10.")
	campaignRoot.BackgroundTransparency = Theme.transparency.panel
	TweenUtil.openFrom(
		campaignRoot,
		UDim2.new(0, campaignRest.X.Offset - 28, 0.5, campaignRest.Y.Offset),
		campaignRest,
		Theme.transparency.panel
	)
	Motions.popIn(campaignRoot, 0.94)
end

function CombatHud.openCrate()
	if inBattle then
		return
	end
	if GarageHud and GarageHud.isOpen() then
		GarageHud.setOpen(false)
	end
	hideCampaign()
	JoinHud.closePanels()
	CrateHud.setOpen(true)
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

local function weaponFor(action, you)
	if action.kind ~= "Fire" or not you or not you.weapons then
		return nil
	end
	for _, w in you.weapons do
		if w.slot == action.weaponSlot then
			return w
		end
	end
	return nil
end

local function actionTitle(action, you): string
	if action.kind == "EndTurn" then
		return "End turn"
	elseif action.kind == "Move" then
		local sign = if action.delta > 0 then "+" else ""
		return ("Move %s%d"):format(sign, action.delta)
	elseif action.kind == "Fire" then
		local w = weaponFor(action, you)
		if w then
			return ("%s %s"):format(Elements.GLYPH[w.damageType] or "·", w.name)
		end
		return "Fire"
	end
	return action.kind
end

local function actionSubtitle(action, you): string
	if action.kind == "EndTurn" then
		local drone = if you and you.droneName then (" · drone %s"):format(you.droneName) else ""
		return "Cool & recharge" .. drone
	elseif action.kind == "Move" then
		return "1 AP · telegraph lane"
	elseif action.kind == "Fire" then
		local w = weaponFor(action, you)
		if w then
			return ("%s · %s %d"):format(Elements.SHORT[w.damageType] or w.damageType, w.damageType, w.damage)
		end
		return action.weaponSlot or "Weapon"
	end
	return ""
end

local function actionTip(action, you): string
	if action.kind == "EndTurn" then
		local tip = "End your turn. Cool down a bit."
		if you and you.droneName then
			tip ..= (" Drone %s ticks."):format(you.droneName)
		end
		return tip
	elseif action.kind == "Move" then
		return "Step along the lane. Hover previews destination."
	elseif action.kind == "Fire" then
		local w = weaponFor(action, you)
		if w then
			return (w.tooltip or w.name) .. (" [%s]"):format(Elements.label(w.damageType))
		end
		return "Fire weapon"
	end
	return ""
end

local function actionAccent(action, you): Color3
	if action.kind == "EndTurn" then
		return Theme.colors.accent
	elseif action.kind == "Move" then
		return Theme.colors.cyan
	elseif action.kind == "Fire" then
		local w = weaponFor(action, you)
		if w then
			return Elements.color(w.damageType)
		end
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
	TopbarHud.setVisible(false)
	JoinHud.closePanels()
	if CrateHud.isOpen() then
		CrateHud.setOpen(false)
	end
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

	headerMeta.Text = ("%s · Turn %d · Range %d"):format(
		battle.arenaId or "Arena",
		battle.turnIndex,
		battle.distance
	)
	renderApPips(battle.apRemaining or 0, battle.apMax or 2)
	local yourTurn = battle.activeSide == battle.playerSide and battle.outcome == "Ongoing"
	if turnHint then
		turnHint.Text = if yourTurn then "YOUR TURN" else "ENEMY"
		turnHint.TextColor3 = if yourTurn then Theme.colors.accent else Theme.colors.danger
		turnHint.Visible = true
	end
	if lastPlayerTurn ~= yourTurn then
		lastPlayerTurn = yourTurn
		if turnHint then
			Motions.pulse(turnHint, 1.08)
		end
	end
	if tauntLabel then
		if battle.taunt and battle.npcName then
			tauntLabel.Text = ('%s: "%s"'):format(battle.npcName, battle.taunt)
			tauntLabel.Visible = true
		elseif battle.taunt then
			tauntLabel.Text = '"' .. battle.taunt .. '"'
			tauntLabel.Visible = true
		else
			tauntLabel.Visible = false
		end
	end
	youBlock.setFromSide(you)
	foeBlock.setFromSide(foe)
	renderLog(battle.log or {})
	CombatJuice.onBattle(battle)

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
		accent.BackgroundColor3 = actionAccent(action, you)
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
		title.Text = actionTitle(action, you)
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
			if captured.kind == "Move" and you then
				CombatJuice.telegraphMove(you.position, foe.position, (you.position or 1) + captured.delta)
			end
		end)
		card.MouseLeave:Connect(function()
			hovering = false
			TweenUtil.play(card, Theme.tween.hover, { BackgroundColor3 = Theme.colors.bgRaised })
			TweenUtil.play(stroke, Theme.tween.hover, { Color = Theme.colors.stroke })
			if captured.kind == "Move" then
				CombatJuice.updateLane(you and you.position, foe and foe.position)
			end
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
			if captured.kind == "Fire" then
				SoundHooks.play("fire")
			elseif captured.kind == "Move" then
				SoundHooks.play("move")
			end
			submit(captured)
		end)
	end
end

function CombatHud.onSettled(settled)
	local verb = if settled.won then "Win" else "Loss"
	local hint = settled.pacingHint
	setStatus(("%s · +%d common · +%d XP — payout…"):format(verb, settled.common, settled.xp))
	local sub = if settled.crateDrop
		then (if settled.guaranteedCrate then "Milestone crate." else "Crate dropped.")
		else (hint or "Bay pays out.")
	CombatJuice.showBanner(settled.won == true, sub)
	task.delay(0.75, function()
		RewardSheet.show(settled)
	end)
end

function CombatHud.onReturnLobby(settled)
	inBattle = false
	lastPlayerTurn = nil
	battleRoot.Visible = false
	battleRoot.Position = battleRest
	JoinHud.setVisible(true)
	TopbarHud.setVisible(true)
	ModalMouse.setCombatClickMode(false)
	BattleCamera.stop()
	LobbyCamera.start()
	CombatJuice.clear()
	if settled and not RewardSheet.isOpen() then
		RewardSheet.show(settled)
	end
	if settled then
		local verb = if settled.won then "Win" else "Loss"
		local rareBit = if (settled.rare or 0) > 0 then (" · +%d rare"):format(settled.rare) else ""
		setStatus(("%s recorded. +%d common%s · +%d XP"):format(verb, settled.common, rareBit, settled.xp))
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

	TopbarHud.mount(screen, {
		openCrate = function()
			CombatHud.openCrate()
		end,
	})

	CombatJuice.mount(screen)
	DailyHud.mount(screen, {
		onRefresh = function()
			refreshBootstrap()
		end,
	})
	RewardSheet.mount(screen)
	CrateHud.mount(screen, {
		onPicked = function(result)
			OnboardingHud.notifyOpened("crate")
			if result and result.onboarding then
				OnboardingHud.apply(result.onboarding)
			end
			refreshBootstrap()
		end,
	})
	OnboardingHud.mount(screen, {
		openCampaign = function()
			CombatHud.openCampaign()
		end,
		openGarage = function()
			if GarageHud then
				GarageHud.setOpen(true)
			end
		end,
		openCrate = function()
			CombatHud.openCrate()
		end,
	})

	if GarageHud then
		GarageHud.mount(screen)
		GarageHud.onOpened(function()
			OnboardingHud.notifyOpened("garage")
		end)
		GarageHud.onWallet(function()
			refreshBootstrap()
		end)
	end

	PvpHud.mount(screen, {
		isBusy = function()
			return inBattle
		end,
		onSpar = function(result)
			if result.arenaId then
				LobbyCamera.stop()
				BattleCamera.startForArena(result.arenaId)
			end
			if result.battle then
				CombatHud.renderBattle(result.battle)
			end
		end,
	})

	JoinHud.mount(screen, {
		openCampaign = function()
			CombatHud.openCampaign()
		end,
		openGarage = function()
			if GarageHud then
				GarageHud.setOpen(true)
			end
		end,
		openCrate = function()
			CombatHud.openCrate()
		end,
		openPvP = function()
			if GarageHud and GarageHud.isOpen() then
				GarageHud.setOpen(false)
			end
			hideCampaign()
			PvpHud.setOpen(true)
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

	campaignRoot = Theme.panel(screen, "CampaignPanel", UDim2.new(0, 460, 0, 560), campaignRest, Theme.colors.cyan)
	campaignRoot.Visible = false

	Theme.label(campaignRoot, "CAMPAIGN", UDim2.new(1, -100, 0, 24), UDim2.new(0, 16, 0, 12), 18, {
		font = Theme.fonts.display,
		color = Theme.colors.cyan,
	})
	Theme.label(
		campaignRoot,
		"Threat · elements · pacing. Crates on 3/5/7/10.",
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
	headerMeta = Theme.label(battleRoot, "", UDim2.new(1, -160, 0, 16), UDim2.new(0, 16, 0, 34), 11, {
		font = Theme.fonts.mono,
		color = Theme.colors.cyan,
	})
	turnHint = Theme.label(battleRoot, "", UDim2.new(0, 90, 0, 16), UDim2.new(1, -100, 0, 12), 12, {
		font = Theme.fonts.display,
		color = Theme.colors.accent,
		align = Enum.TextXAlignment.Right,
	})
	turnHint.Visible = false
	Theme.label(battleRoot, "AP", UDim2.new(0, 24, 0, 14), UDim2.new(1, -110, 0, 34), 11, {
		font = Theme.fonts.mono,
		color = Theme.colors.textMuted,
	})
	apPips = Instance.new("Frame")
	apPips.Name = "ApPips"
	apPips.Size = UDim2.new(0, 80, 0, 16)
	apPips.Position = UDim2.new(1, -86, 0, 34)
	apPips.BackgroundTransparency = 1
	apPips.Parent = battleRoot
	local pipLayout = Instance.new("UIListLayout")
	pipLayout.FillDirection = Enum.FillDirection.Horizontal
	pipLayout.Padding = UDim.new(0, 6)
	pipLayout.Parent = apPips

	youBlock = ResourceBar.sideBlock(battleRoot, "You", UDim2.new(0.5, -16, 0, 90), UDim2.new(0, 12, 0, 56))
	foeBlock = ResourceBar.sideBlock(battleRoot, "Foe", UDim2.new(0.5, -16, 0, 90), UDim2.new(0.5, 4, 0, 56))
	CombatJuice.bindSideBlocks(youBlock, foeBlock)

	tauntLabel = Theme.label(battleRoot, "", UDim2.new(1, -28, 0, 16), UDim2.new(0, 16, 0, 148), 11, {
		font = Theme.fonts.body,
		color = Theme.colors.accentSoft,
	})
	tauntLabel.Visible = false
	tauntLabel.TextTruncate = Enum.TextTruncate.AtEnd

	logLabel = Instance.new("TextLabel")
	logLabel.Name = "Log"
	logLabel.Size = UDim2.new(1, -24, 0, 58)
	logLabel.Position = UDim2.new(0, 12, 0, 166)
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
	actionFolder.Position = UDim2.new(0, 10, 0, 232) -- move cards stay bottom-anchored
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
	OpenCrate.OnClientEvent:Connect(function()
		CombatHud.openCrate()
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
	SessionBridge.onChanged(function(phase, arena, _fight)
		-- Attribute-driven phase (juice/onboarding can subscribe the same bridge).
		if phase == "Combat" and arena ~= "" then
			setStatus(("In combat · %s"):format(arena))
		elseif phase == "Lobby" and not inBattle then
			refreshBootstrap()
		end
	end)
	refreshBootstrap()
	print("[Assembler] Gameplay depth — campaign cards, daily, PvP stub, combat juice")
end

return CombatHud

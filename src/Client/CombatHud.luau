-- Campaign + combat overlay — secondary to the 3D lobby/arenas.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

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

local GarageHud

local screen
local campaignFrame
local battleFrame
local statusLabel
local logLabel
local resourceLabel
local actionFolder
local fightButtons
local walletLabel

local function makeTextButton(parent, text, size, pos)
	local b = Instance.new("TextButton")
	b.Size = size
	b.Position = pos
	b.BackgroundColor3 = Color3.fromRGB(40, 44, 52)
	b.BorderSizePixel = 0
	b.TextColor3 = Color3.fromRGB(230, 230, 230)
	b.Font = Enum.Font.GothamMedium
	b.TextSize = 14
	b.Text = text
	b.AutoButtonColor = true
	b.Parent = parent
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 4)
	corner.Parent = b
	return b
end

local function makeLabel(parent, text, size, pos, textSize)
	local l = Instance.new("TextLabel")
	l.Size = size
	l.Position = pos
	l.BackgroundTransparency = 1
	l.TextColor3 = Color3.fromRGB(220, 220, 220)
	l.Font = Enum.Font.Gotham
	l.TextSize = textSize or 14
	l.TextXAlignment = Enum.TextXAlignment.Left
	l.TextYAlignment = Enum.TextYAlignment.Top
	l.TextWrapped = true
	l.Text = text
	l.Parent = parent
	return l
end

local function clearChildren(frame)
	for _, child in frame:GetChildren() do
		if child:IsA("GuiButton") or (child:IsA("TextLabel") and child.Name == "FightRow") then
			child:Destroy()
		end
	end
end

local function setStatus(text)
	statusLabel.Text = text
end

local function showCampaign()
	campaignFrame.Visible = true
	battleFrame.Visible = false
end

local function showBattle()
	campaignFrame.Visible = false
	battleFrame.Visible = true
	if GarageHud and GarageHud.isOpen() then
		GarageHud.setOpen(false)
	end
end

local function refreshBootstrap()
	local boot = GetBootstrap:InvokeServer()
	walletLabel.Text = ("Common: %d   XP: %d   Cleared: %d/%d"):format(
		boot.wallet.common,
		boot.progress.xp,
		boot.progress.highestCleared,
		boot.ladderCount
	)
	local lo = boot.loadout
	statusLabel.Text = ("Primary: %s · %s · %s"):format(
		lo.torso or "?",
		lo.legs or "?",
		lo.drone or "no drone"
	)
	if GarageHud and boot.inventory then
		GarageHud.applySnapshot(boot.inventory)
	end
end

local function refreshCampaignList()
	clearChildren(fightButtons)
	local fights = ListCampaign:InvokeServer()
	for i, fight in fights do
		local label = fight.name
		if fight.arenaId then
			label = label .. "  [" .. fight.arenaId .. "]"
		end
		if fight.cleared then
			label = label .. "  (cleared)"
		elseif not fight.unlocked then
			label = label .. "  (locked)"
		end
		local row = makeTextButton(
			fightButtons,
			("%d. %s"):format(fight.index, label),
			UDim2.new(1, -8, 0, 32),
			UDim2.new(0, 4, 0, (i - 1) * 36)
		)
		row.Name = "FightRow"
		if not fight.unlocked then
			row.BackgroundColor3 = Color3.fromRGB(28, 28, 30)
			row.TextColor3 = Color3.fromRGB(120, 120, 120)
			row.Active = false
			row.AutoButtonColor = false
		else
			row.MouseButton1Click:Connect(function()
				setStatus("Starting fight " .. fight.index .. "…")
				local result = StartFight:InvokeServer(fight.index)
				if not result.ok then
					setStatus(result.error or "Could not start")
					return
				end
				showBattle()
				CombatHud.renderBattle(result.battle)
				if result.arenaId then
					setStatus("Arena: " .. result.arenaId)
				end
			end)
		end
		row.MouseEnter:Connect(function()
			if fight.unlocked then
				setStatus(fight.blurb .. "  ·  win +" .. tostring(fight.rewardCommon) .. " common")
			end
		end)
	end
	fightButtons.CanvasSize = UDim2.new(0, 0, 0, #fights * 36)
end

local function formatSide(side)
	return ("%s  HP %d/%d  Temp %d/%d  Bat %d/%d  Tile %d"):format(
		side.displayName,
		side.integrity,
		side.integrityMax,
		side.temperature,
		side.temperatureMax,
		side.battery,
		side.batteryMax,
		side.position
	)
end

local function renderLog(log)
	local lines = {}
	local start = math.max(1, #log - 8)
	for i = start, #log do
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
	if not result.ok then
		setStatus(result.error or "Action failed")
		if result.battle then
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
	showBattle()
	local you = if battle.playerSide == "A" then battle.sideA else battle.sideB
	local foe = if battle.playerSide == "A" then battle.sideB else battle.sideA

	local arenaLine = if battle.arenaId then ("Arena " .. battle.arenaId) else "Arena"
	resourceLabel.Text = table.concat({
		arenaLine
			.. " · Turn "
			.. tostring(battle.turnIndex)
			.. " · AP "
			.. tostring(battle.apRemaining)
			.. "/"
			.. tostring(battle.apMax),
		"Range " .. tostring(battle.distance),
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

	local actions = battle.legalActions or {}
	for i, action in actions do
		local col = (i - 1) % 3
		local row = math.floor((i - 1) / 3)
		local btn = makeTextButton(
			actionFolder,
			actionLabel(action),
			UDim2.new(0, 120, 0, 32),
			UDim2.new(0, col * 128, 0, row * 36)
		)
		local captured = action
		btn.MouseButton1Click:Connect(function()
			submit(captured)
		end)
	end
end

function CombatHud.onSettled(settled)
	local verb = if settled.won then "Win" else "Loss"
	setStatus(("%s · +%d common · +%d XP"):format(verb, settled.common, settled.xp))
	task.delay(1.2, function()
		showCampaign()
		refreshBootstrap()
		refreshCampaignList()
	end)
end

function CombatHud.mount(garageModule)
	GarageHud = garageModule

	screen = Instance.new("ScreenGui")
	screen.Name = "AssemblerHud"
	screen.ResetOnSpawn = false
	screen.Parent = playerGui

	if GarageHud then
		GarageHud.mount(screen)
	end

	-- Compact left panel — world stays visible.
	local root = Instance.new("Frame")
	root.Size = UDim2.new(0, 380, 0, 460)
	root.Position = UDim2.new(0, 12, 0, 12)
	root.BackgroundColor3 = Color3.fromRGB(18, 20, 24)
	root.BackgroundTransparency = 0.12
	root.BorderSizePixel = 0
	root.Parent = screen
	local rootCorner = Instance.new("UICorner")
	rootCorner.CornerRadius = UDim.new(0, 8)
	rootCorner.Parent = root

	makeLabel(root, "Assembler", UDim2.new(1, -100, 0, 28), UDim2.new(0, 12, 0, 8), 22).Font =
		Enum.Font.GothamBold
	walletLabel = makeLabel(root, "", UDim2.new(1, -16, 0, 20), UDim2.new(0, 12, 0, 36), 13)
	statusLabel = makeLabel(root, "", UDim2.new(1, -16, 0, 36), UDim2.new(0, 12, 0, 56), 13)

	local garageBtn = makeTextButton(root, "Garage", UDim2.new(0, 72, 0, 26), UDim2.new(1, -84, 0, 10))
	garageBtn.BackgroundColor3 = Color3.fromRGB(55, 72, 96)
	garageBtn.MouseButton1Click:Connect(function()
		if GarageHud then
			GarageHud.toggle()
		end
	end)

	campaignFrame = Instance.new("Frame")
	campaignFrame.Size = UDim2.new(1, -16, 1, -108)
	campaignFrame.Position = UDim2.new(0, 8, 0, 100)
	campaignFrame.BackgroundTransparency = 1
	campaignFrame.Parent = root

	makeLabel(campaignFrame, "Campaign ladder", UDim2.new(1, 0, 0, 22), UDim2.new(0, 4, 0, 0), 16).Font =
		Enum.Font.GothamMedium

	fightButtons = Instance.new("ScrollingFrame")
	fightButtons.Size = UDim2.new(1, 0, 1, -28)
	fightButtons.Position = UDim2.new(0, 0, 0, 28)
	fightButtons.BackgroundTransparency = 1
	fightButtons.ScrollBarThickness = 4
	fightButtons.BorderSizePixel = 0
	fightButtons.Parent = campaignFrame

	battleFrame = Instance.new("Frame")
	battleFrame.Size = UDim2.new(1, -16, 1, -108)
	battleFrame.Position = UDim2.new(0, 8, 0, 100)
	battleFrame.BackgroundTransparency = 1
	battleFrame.Visible = false
	battleFrame.Parent = root

	resourceLabel = makeLabel(battleFrame, "", UDim2.new(1, 0, 0, 90), UDim2.new(0, 0, 0, 0), 12)
	logLabel = makeLabel(battleFrame, "", UDim2.new(1, 0, 0, 140), UDim2.new(0, 0, 0, 96), 12)
	logLabel.TextColor3 = Color3.fromRGB(170, 180, 190)

	actionFolder = Instance.new("Frame")
	actionFolder.Size = UDim2.new(1, 0, 0, 120)
	actionFolder.Position = UDim2.new(0, 0, 0, 250)
	actionFolder.BackgroundTransparency = 1
	actionFolder.Parent = battleFrame

	local back = makeTextButton(
		battleFrame,
		"Finish the fight on the pads",
		UDim2.new(1, 0, 0, 28),
		UDim2.new(0, 0, 1, -32)
	)
	back.MouseButton1Click:Connect(function()
		setStatus("Fire / move / End turn until someone's scrap.")
	end)

	BattleUpdated.OnClientEvent:Connect(function(battle)
		CombatHud.renderBattle(battle)
	end)

	FightSettled.OnClientEvent:Connect(function(settled)
		CombatHud.onSettled(settled)
	end)

	refreshBootstrap()
	refreshCampaignList()
	showCampaign()
	print("[Assembler] HUD mounted — Garage + campaign over lobby/arenas")
end

return CombatHud

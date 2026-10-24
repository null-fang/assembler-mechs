-- World-first HUD: thin lobby hint, campaign from terminal, battle overlay + camera.
-- No locked-mechs wall as the first thing you see.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BattleCamera = require(script.Parent:WaitForChild("BattleCamera"))

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
local hintBar
local campaignRoot
local campaignFrame
local battleRoot
local statusLabel
local logLabel
local resourceLabel
local actionFolder
local fightButtons
local walletLabel
local inBattle = false

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

local function refreshBootstrap()
	local ok, boot = pcall(function()
		return GetBootstrap:InvokeServer()
	end)
	if not ok or not boot then
		walletLabel.Text = "Assembler Bay"
		return
	end
	walletLabel.Text = ("Common %d · XP %d · Cleared %d/%d"):format(
		boot.wallet.common,
		boot.progress.xp,
		boot.progress.highestCleared,
		boot.ladderCount
	)
	if not inBattle then
		local lo = boot.loadout
		setStatus(
			("Primary ready: %s · walk to Campaign (cyan) or Garage pedestal"):format(lo.torso or "mech")
		)
	end
	if GarageHud and boot.inventory then
		GarageHud.applySnapshot(boot.inventory)
	end
end

local function hideCampaign()
	campaignRoot.Visible = false
end

local function startFight(index: number)
	setStatus("Deploying…")
	hideCampaign()
	local result = StartFight:InvokeServer(index)
	if not result or not result.ok then
		setStatus((result and result.error) or "Could not start")
		return
	end
	if result.arenaId then
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
	campaignRoot.Visible = true
	clearChildren(fightButtons)
	local fights = ListCampaign:InvokeServer()
	local y = 0
	local lockedShown = false
	for _, fight in fights do
		if fight.unlocked then
			local tag = if fight.cleared then " · cleared" else ""
			local arena = if fight.arenaId then (" · " .. fight.arenaId) else ""
			local row = makeTextButton(
				fightButtons,
				("%d. %s%s%s  (+%d)"):format(fight.index, fight.name, tag, arena, fight.rewardCommon),
				UDim2.new(1, -8, 0, 34),
				UDim2.new(0, 4, 0, y)
			)
			row.Name = "FightRow"
			row.MouseButton1Click:Connect(function()
				startFight(fight.index)
			end)
			row.MouseEnter:Connect(function()
				setStatus(fight.blurb)
			end)
			y += 38
		elseif not lockedShown then
			local row = makeLabel(
				fightButtons,
				("Next: %d. %s — clear an open fight first."):format(fight.index, fight.name),
				UDim2.new(1, -8, 0, 28),
				UDim2.new(0, 4, 0, y),
				13
			)
			row.Name = "FightRow"
			row.TextColor3 = Color3.fromRGB(130, 130, 140)
			lockedShown = true
			y += 32
		end
	end
	fightButtons.CanvasSize = UDim2.new(0, 0, 0, y)
	setStatus("Your starter mech is equipped. Pick a fight.")
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
	hintBar.Visible = false
	battleRoot.Visible = true
	if GarageHud and GarageHud.isOpen() then
		GarageHud.setOpen(false)
	end
	if battle.arenaId then
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
		local btn = makeTextButton(
			actionFolder,
			actionLabel(action),
			UDim2.new(0, 120, 0, 32),
			UDim2.new(0, 8 + col * 128, 0, row * 36)
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
	hintBar.Visible = true
	BattleCamera.stop()
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
	screen.Parent = playerGui

	if GarageHud then
		GarageHud.mount(screen)
	end

	-- Thin lobby chrome (not a locked-mechs wall)
	hintBar = Instance.new("Frame")
	hintBar.Name = "HintBar"
	hintBar.Size = UDim2.new(0, 440, 0, 78)
	hintBar.Position = UDim2.new(0, 16, 0, 16)
	hintBar.BackgroundColor3 = Color3.fromRGB(14, 16, 20)
	hintBar.BackgroundTransparency = 0.12
	hintBar.BorderSizePixel = 0
	hintBar.Parent = screen
	local hc = Instance.new("UICorner")
	hc.CornerRadius = UDim.new(0, 8)
	hc.Parent = hintBar

	makeLabel(hintBar, "Assembler", UDim2.new(1, -100, 0, 24), UDim2.new(0, 12, 0, 6), 18).Font =
		Enum.Font.GothamBold
	walletLabel = makeLabel(hintBar, "", UDim2.new(1, -16, 0, 18), UDim2.new(0, 12, 0, 30), 13)
	statusLabel = makeLabel(hintBar, "", UDim2.new(1, -16, 0, 24), UDim2.new(0, 12, 0, 50), 13)

	local garageBtn = makeTextButton(hintBar, "Garage", UDim2.new(0, 72, 0, 26), UDim2.new(1, -84, 0, 8))
	garageBtn.BackgroundColor3 = Color3.fromRGB(55, 72, 96)
	garageBtn.MouseButton1Click:Connect(function()
		if GarageHud then
			GarageHud.toggle()
		end
	end)

	-- Campaign panel (hidden until terminal)
	campaignRoot = Instance.new("Frame")
	campaignRoot.Name = "CampaignPanel"
	campaignRoot.Size = UDim2.new(0, 380, 0, 420)
	campaignRoot.Position = UDim2.new(0, 16, 0, 106)
	campaignRoot.BackgroundColor3 = Color3.fromRGB(16, 18, 22)
	campaignRoot.BackgroundTransparency = 0.06
	campaignRoot.BorderSizePixel = 0
	campaignRoot.Visible = false
	campaignRoot.Parent = screen
	local cc = Instance.new("UICorner")
	cc.CornerRadius = UDim.new(0, 8)
	cc.Parent = campaignRoot

	makeLabel(campaignRoot, "Campaign ladder", UDim2.new(1, -16, 0, 24), UDim2.new(0, 12, 0, 10), 16).Font =
		Enum.Font.GothamMedium
	makeLabel(
		campaignRoot,
		"Open fights only. Primary mech is already built — no locked bay wall.",
		UDim2.new(1, -16, 0, 36),
		UDim2.new(0, 12, 0, 36),
		12
	)

	campaignFrame = Instance.new("Frame")
	campaignFrame.Size = UDim2.new(1, -16, 1, -100)
	campaignFrame.Position = UDim2.new(0, 8, 0, 76)
	campaignFrame.BackgroundTransparency = 1
	campaignFrame.Parent = campaignRoot

	fightButtons = Instance.new("ScrollingFrame")
	fightButtons.Size = UDim2.new(1, 0, 1, 0)
	fightButtons.BackgroundTransparency = 1
	fightButtons.ScrollBarThickness = 4
	fightButtons.BorderSizePixel = 0
	fightButtons.Parent = campaignFrame

	local closeC = makeTextButton(campaignRoot, "Close", UDim2.new(0, 72, 0, 28), UDim2.new(1, -84, 1, -40))
	closeC.MouseButton1Click:Connect(function()
		hideCampaign()
		refreshBootstrap()
	end)

	-- Battle overlay (bottom-left)
	battleRoot = Instance.new("Frame")
	battleRoot.Name = "BattlePanel"
	battleRoot.Size = UDim2.new(0, 420, 0, 320)
	battleRoot.Position = UDim2.new(0, 16, 1, -336)
	battleRoot.BackgroundColor3 = Color3.fromRGB(16, 18, 22)
	battleRoot.BackgroundTransparency = 0.08
	battleRoot.BorderSizePixel = 0
	battleRoot.Visible = false
	battleRoot.Parent = screen
	local bc = Instance.new("UICorner")
	bc.CornerRadius = UDim.new(0, 8)
	bc.Parent = battleRoot

	resourceLabel = makeLabel(battleRoot, "", UDim2.new(1, -16, 0, 70), UDim2.new(0, 8, 0, 8), 12)
	logLabel = makeLabel(battleRoot, "", UDim2.new(1, -16, 0, 100), UDim2.new(0, 8, 0, 80), 12)
	logLabel.TextColor3 = Color3.fromRGB(170, 180, 190)
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

	refreshBootstrap()
	print("[Assembler] World-first HUD — use Campaign terminal / Garage pedestal")
end

return CombatHud

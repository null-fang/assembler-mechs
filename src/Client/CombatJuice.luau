-- Combat feel: mech lean/recoil, integrity flash, overheat edge, battery dim, win/loss banner.

local TweenService = game:GetService("TweenService")
local Workspace = game:GetService("Workspace")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local TweenUtil = require(script.Parent:WaitForChild("UI"):WaitForChild("TweenUtil"))

local CombatJuice = {}

local screen: ScreenGui?
local overheatEdge: Frame?
local batteryDim: Frame?
local bannerRoot: Frame?
local bannerLabel: TextLabel?
local bannerSub: TextLabel?

local lastSnap: any = nil
local sideBlocks: { you: any?, foe: any? } = { you = nil, foe = nil }
local basePivots: { [Model]: CFrame } = {}

local leanInfo = TweenInfo.new(0.12, Enum.EasingStyle.Back, Enum.EasingDirection.Out)
local recoverInfo = TweenInfo.new(0.22, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local flashInfo = TweenInfo.new(0.08, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local bannerInfo = TweenInfo.new(0.28, Enum.EasingStyle.Back, Enum.EasingDirection.Out)

local function findLiveMech(side: string): Model?
	local arenas = Workspace:FindFirstChild("Arenas")
	if not arenas then
		return nil
	end
	for _, arena in arenas:GetChildren() do
		local live = arena:FindFirstChild("LiveMechs")
		if live then
			for _, child in live:GetChildren() do
				if child:IsA("Model") and child:GetAttribute("Side") == side then
					return child
				end
			end
		end
	end
	return nil
end

local function tweenPivot(model: Model, from: CFrame, to: CFrame, info: TweenInfo)
	local holder = Instance.new("CFrameValue")
	holder.Value = from
	local conn = holder.Changed:Connect(function(value)
		if model.Parent then
			model:PivotTo(value)
		end
	end)
	local tw = TweenService:Create(holder, info, { Value = to })
	tw.Completed:Connect(function()
		conn:Disconnect()
		holder:Destroy()
		if model.Parent then
			model:PivotTo(to)
		end
	end)
	tw:Play()
end

local function leanMech(side: string, towardEnemy: boolean)
	local model = findLiveMech(side)
	if not model then
		return
	end
	local base = basePivots[model]
	if not base then
		base = model:GetPivot()
		basePivots[model] = base
	end
	local yaw = if towardEnemy then -0.18 else 0.14
	local pitch = if towardEnemy then -0.08 else 0.05
	local punch = base * CFrame.Angles(pitch, 0, yaw)
	tweenPivot(model, model:GetPivot(), punch, leanInfo)
	task.delay(0.12, function()
		if model.Parent then
			tweenPivot(model, model:GetPivot(), base, recoverInfo)
		end
	end)
end

local function flashIntegrity(block)
	if not block or not block.root then
		return
	end
	local stroke = block.root:FindFirstChildOfClass("UIStroke")
	local fill
	local bar = block.root:FindFirstChild("Bar_integrity")
	if bar then
		local track = bar:FindFirstChildWhichIsA("Frame")
		if track then
			fill = track:FindFirstChild("Fill")
		end
	end
	if fill and fill:IsA("GuiObject") then
		local orig = fill.BackgroundColor3
		fill.BackgroundColor3 = Theme.colors.text
		TweenUtil.play(fill, flashInfo, { BackgroundColor3 = Theme.colors.danger })
		task.delay(0.1, function()
			if fill.Parent then
				TweenUtil.play(fill, Theme.tween.bar, { BackgroundColor3 = Theme.colors.integrity })
			end
		end)
		local _ = orig
	end
	if stroke then
		TweenUtil.play(stroke, flashInfo, { Color = Theme.colors.danger, Thickness = 2.5 })
		task.delay(0.18, function()
			if stroke.Parent then
				TweenUtil.play(stroke, Theme.tween.hover, { Color = Theme.colors.stroke, Thickness = 1 })
			end
		end)
	end
end

local function setOverheat(active: boolean)
	if not overheatEdge then
		return
	end
	local goal = if active then 0.35 else 1
	TweenUtil.play(overheatEdge, Theme.tween.open, { BackgroundTransparency = goal })
	for _, child in overheatEdge:GetChildren() do
		if child:IsA("GuiObject") then
			TweenUtil.play(child, Theme.tween.open, { BackgroundTransparency = goal })
		end
	end
end

local function setBatteryDim(active: boolean)
	if not batteryDim then
		return
	end
	TweenUtil.play(batteryDim, Theme.tween.open, {
		BackgroundTransparency = if active then 0.55 else 1,
	})
end

function CombatJuice.bindSideBlocks(youBlock, foeBlock)
	sideBlocks.you = youBlock
	sideBlocks.foe = foeBlock
end

function CombatJuice.mount(parentGui: ScreenGui)
	screen = parentGui

	overheatEdge = Instance.new("Frame")
	overheatEdge.Name = "OverheatEdge"
	overheatEdge.Size = UDim2.fromScale(1, 1)
	overheatEdge.BackgroundTransparency = 1
	overheatEdge.BackgroundColor3 = Theme.colors.danger
	overheatEdge.BorderSizePixel = 0
	overheatEdge.ZIndex = 20
	overheatEdge.Parent = parentGui

	local function edge(name: string, size: UDim2, pos: UDim2)
		local f = Instance.new("Frame")
		f.Name = name
		f.Size = size
		f.Position = pos
		f.BackgroundColor3 = Theme.colors.temperature
		f.BackgroundTransparency = 1
		f.BorderSizePixel = 0
		f.ZIndex = 21
		f.Parent = overheatEdge
		return f
	end
	edge("Top", UDim2.new(1, 0, 0, 28), UDim2.new(0, 0, 0, 0))
	edge("Bottom", UDim2.new(1, 0, 0, 28), UDim2.new(0, 0, 1, -28))
	edge("Left", UDim2.new(0, 22, 1, 0), UDim2.new(0, 0, 0, 0))
	edge("Right", UDim2.new(0, 22, 1, 0), UDim2.new(1, -22, 0, 0))

	batteryDim = Instance.new("Frame")
	batteryDim.Name = "BatteryDim"
	batteryDim.Size = UDim2.fromScale(1, 1)
	batteryDim.BackgroundColor3 = Color3.fromRGB(4, 10, 22)
	batteryDim.BackgroundTransparency = 1
	batteryDim.BorderSizePixel = 0
	batteryDim.ZIndex = 19
	batteryDim.Parent = parentGui

	bannerRoot = Instance.new("Frame")
	bannerRoot.Name = "OutcomeBanner"
	bannerRoot.Size = UDim2.new(0, 420, 0, 110)
	bannerRoot.Position = UDim2.new(0.5, -210, 0.28, 0)
	bannerRoot.BackgroundColor3 = Theme.colors.bgPanel
	bannerRoot.BackgroundTransparency = 0.08
	bannerRoot.BorderSizePixel = 0
	bannerRoot.Visible = false
	bannerRoot.ZIndex = 40
	bannerRoot.Parent = parentGui
	Theme.corner(bannerRoot, Theme.radii.lg)
	Theme.stroke(bannerRoot, Theme.colors.strokeBright, 1.5)

	bannerLabel = Instance.new("TextLabel")
	bannerLabel.Size = UDim2.new(1, -24, 0, 48)
	bannerLabel.Position = UDim2.new(0, 12, 0, 18)
	bannerLabel.BackgroundTransparency = 1
	bannerLabel.Font = Theme.fonts.display
	bannerLabel.TextSize = 36
	bannerLabel.TextColor3 = Theme.colors.ok
	bannerLabel.Text = "WIN"
	bannerLabel.ZIndex = 41
	bannerLabel.Parent = bannerRoot

	bannerSub = Instance.new("TextLabel")
	bannerSub.Size = UDim2.new(1, -24, 0, 24)
	bannerSub.Position = UDim2.new(0, 12, 0, 68)
	bannerSub.BackgroundTransparency = 1
	bannerSub.Font = Theme.fonts.body
	bannerSub.TextSize = 14
	bannerSub.TextColor3 = Theme.colors.textDim
	bannerSub.Text = "Returning to bay…"
	bannerSub.ZIndex = 41
	bannerSub.Parent = bannerRoot
end

function CombatJuice.clear()
	lastSnap = nil
	table.clear(basePivots)
	setOverheat(false)
	setBatteryDim(false)
	if bannerRoot then
		bannerRoot.Visible = false
	end
end

function CombatJuice.showBanner(won: boolean, subtext: string?)
	if not bannerRoot or not bannerLabel or not bannerSub then
		return
	end
	bannerLabel.Text = if won then "VICTORY" else "DEFEAT"
	bannerLabel.TextColor3 = if won then Theme.colors.ok else Theme.colors.danger
	bannerSub.Text = subtext or (if won then "Bay pays out." else "Scrap it. Try again.")
	bannerRoot.Visible = true
	bannerRoot.Size = UDim2.new(0, 360, 0, 90)
	bannerRoot.BackgroundTransparency = 0.4
	TweenService:Create(bannerRoot, bannerInfo, {
		Size = UDim2.new(0, 420, 0, 110),
		BackgroundTransparency = 0.08,
	}):Play()
end

function CombatJuice.hideBanner()
	if bannerRoot then
		bannerRoot.Visible = false
	end
end

function CombatJuice.onBattle(battle)
	if not battle then
		return
	end
	local you = if battle.playerSide == "A" then battle.sideA else battle.sideB
	local foe = if battle.playerSide == "A" then battle.sideB else battle.sideA
	local youSide = battle.playerSide
	local foeSide = if youSide == "A" then "B" else "A"

	if lastSnap then
		local prevYou = if lastSnap.playerSide == "A" then lastSnap.sideA else lastSnap.sideB
		local prevFoe = if lastSnap.playerSide == "A" then lastSnap.sideB else lastSnap.sideA
		if you and prevYou and (you.integrity or 0) < (prevYou.integrity or 0) then
			flashIntegrity(sideBlocks.you)
			leanMech(youSide, false)
		end
		if foe and prevFoe and (foe.integrity or 0) < (prevFoe.integrity or 0) then
			flashIntegrity(sideBlocks.foe)
			leanMech(youSide, true)
			leanMech(foeSide, false)
		end
	end

	setOverheat(you ~= nil and you.skipNextTurn == true)
	setBatteryDim(you ~= nil and (you.batteryRechargeMoves or 0) > 0)

	if battle.outcome and battle.outcome ~= "Ongoing" then
		local won = battle.outcome == "SideAWins" and battle.playerSide == "A"
			or battle.outcome == "SideBWins" and battle.playerSide == "B"
		-- Banner is also driven from settle; keep a soft flash if settle races.
		if not (bannerRoot and bannerRoot.Visible) then
			CombatJuice.showBanner(won, "Hold for payout…")
		end
	end

	lastSnap = battle
end

return CombatJuice

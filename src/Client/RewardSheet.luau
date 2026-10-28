-- Post-fight payout sheet: currency / XP / crate chance. Win > loss amounts.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))
local TweenUtil = require(script.Parent:WaitForChild("UI"):WaitForChild("TweenUtil"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))

local RewardSheet = {}

local root: Frame?
local title: TextLabel?
local lines: Frame?
local rest = UDim2.new(0.5, -190, 0.42, -90)
local onDismiss: (() -> ())?
local open = false

local function clearLines()
	if not lines then
		return
	end
	for _, child in lines:GetChildren() do
		if child:IsA("GuiObject") and not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
end

local function row(label: string, value: string, color: Color3?)
	if not lines then
		return
	end
	local f = Instance.new("Frame")
	f.Size = UDim2.new(1, -4, 0, 28)
	f.BackgroundTransparency = 1
	f.Parent = lines

	local l = Instance.new("TextLabel")
	l.Size = UDim2.new(0.55, 0, 1, 0)
	l.BackgroundTransparency = 1
	l.Font = Theme.fonts.body
	l.TextSize = 14
	l.TextColor3 = Theme.colors.textDim
	l.TextXAlignment = Enum.TextXAlignment.Left
	l.Text = label
	l.Parent = f

	local v = Instance.new("TextLabel")
	v.Size = UDim2.new(0.45, 0, 1, 0)
	v.Position = UDim2.new(0.55, 0, 0, 0)
	v.BackgroundTransparency = 1
	v.Font = Theme.fonts.mono
	v.TextSize = 15
	v.TextColor3 = color or Theme.colors.text
	v.TextXAlignment = Enum.TextXAlignment.Right
	v.Text = value
	v.Parent = f
end

function RewardSheet.mount(parentGui: ScreenGui)
	root = Theme.panel(parentGui, "RewardSheet", UDim2.new(0, 380, 0, 260), rest, Theme.colors.accent)
	root.Visible = false
	root.ZIndex = 45

	title = Theme.label(root, "PAYOUT", UDim2.new(1, -24, 0, 28), UDim2.new(0, 16, 0, 12), 22, {
		font = Theme.fonts.display,
		color = Theme.colors.accent,
	})

	lines = Instance.new("Frame")
	lines.Name = "Lines"
	lines.Size = UDim2.new(1, -32, 0, 140)
	lines.Position = UDim2.new(0, 16, 0, 52)
	lines.BackgroundTransparency = 1
	lines.Parent = root
	local layout = Instance.new("UIListLayout")
	layout.Padding = UDim.new(0, 6)
	layout.Parent = lines

	local close = Button.create(root, "Continue", UDim2.new(0, 120, 0, 32), UDim2.new(0.5, -60, 1, -48), "primary")
	close.MouseButton1Click:Connect(function()
		RewardSheet.hide()
	end)
end

function RewardSheet.show(settled: any, dismissCb: (() -> ())?)
	if not root or not title or not lines then
		return
	end
	onDismiss = dismissCb
	open = true
	ModalMouse.push("reward")
	clearLines()
	local won = settled and settled.won
	title.Text = if won then "WIN PAYOUT" else "LOSS PAYOUT"
	title.TextColor3 = if won then Theme.colors.ok else Theme.colors.danger

	row("Common", ("+%d"):format(settled.common or 0), Theme.colors.accent)
	row("XP", ("+%d"):format(settled.xp or 0), Theme.colors.cyan)
	local chance = settled.crateChance or 0
	row("Crate chance", ("%d%%"):format(math.floor(chance * 100 + 0.5)), Theme.colors.textDim)
	if settled.crateDrop then
		row("Crate", "Dropped — open in bay", Theme.colors.ok)
	else
		row("Crate", "No drop", Theme.colors.textMuted)
	end
	if settled.walletCommon then
		row("Wallet", tostring(settled.walletCommon), Theme.colors.text)
	end

	root.BackgroundTransparency = Theme.transparency.panel
	TweenUtil.openFrom(root, UDim2.new(0.5, -190, 0.42, -70), rest, Theme.transparency.panel)
end

function RewardSheet.hide()
	if not open or not root then
		return
	end
	open = false
	ModalMouse.pop("reward")
	TweenUtil.closeTo(root, UDim2.new(0.5, -190, 0.42, -50), rest)
	local cb = onDismiss
	onDismiss = nil
	if cb then
		cb()
	end
end

function RewardSheet.isOpen(): boolean
	return open
end

return RewardSheet

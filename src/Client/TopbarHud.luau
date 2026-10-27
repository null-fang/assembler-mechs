-- Always-on hub topbar: brand, common/rare, level/XP, soft settings gear.
-- Extends juice surface — does not replace Join bar or CrateHud.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local AccountLevel = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Progress"):WaitForChild("AccountLevel"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))
local TweenUtil = require(script.Parent:WaitForChild("UI"):WaitForChild("TweenUtil"))
local SoundHooks = require(script.Parent:WaitForChild("UI"):WaitForChild("SoundHooks"))
local Tooltip = require(script.Parent:WaitForChild("UI"):WaitForChild("Tooltip"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))
local LobbyCamera = require(script.Parent:WaitForChild("LobbyCamera"))

local TopbarHud = {}

local remotesFolder = ReplicatedStorage:WaitForChild("AssemblerRemotes")
local WalletUpdated = remotesFolder:FindFirstChild("WalletUpdated")

local root: Frame
local commonLabel: TextLabel
local rareLabel: TextLabel
local levelLabel: TextLabel
local xpFill: Frame
local xpText: TextLabel
local settingsPanel: Frame
local settingsRest: UDim2
local visible = true
local openCrateCb: (() -> ())?

local function fmt(n: number): string
	n = math.floor(n + 0.5)
	if n >= 10000 then
		return ("%.1fk"):format(n / 1000)
	end
	return tostring(n)
end

function TopbarHud.apply(wallet, progress)
	if not root then
		return
	end
	local w = wallet or { common = 0, rare = 0 }
	local info = AccountLevel.fromXp((progress and progress.xp) or 0)
	commonLabel.Text = fmt(w.common or 0)
	rareLabel.Text = fmt(w.rare or 0)
	levelLabel.Text = tostring(info.level)
	xpText.Text = ("%d / %d"):format(info.xpIntoLevel, info.xpForNext)
	TweenUtil.barFill(xpFill, info.progress)
end

function TopbarHud.setVisible(on: boolean)
	visible = on
	if root then
		root.Visible = on
	end
	if not on and settingsPanel then
		settingsPanel.Visible = false
		ModalMouse.pop("topSettings")
	end
end

function TopbarHud.mount(parent: ScreenGui, opts: { openCrate: (() -> ())? }?)
	openCrateCb = opts and opts.openCrate

	root = Instance.new("Frame")
	root.Name = "Topbar"
	root.Size = UDim2.new(1, -24, 0, 48)
	root.Position = UDim2.new(0, 12, 0, 10)
	root.BackgroundColor3 = Theme.colors.bgTopbar
	root.BackgroundTransparency = Theme.transparency.topbar
	root.BorderSizePixel = 0
	root.ZIndex = 40
	root.Parent = parent
	Theme.corner(root, Theme.radii.md)
	Theme.stroke(root, Theme.colors.strokeBright, 1)
	Theme.accentStrip(root, Theme.colors.accent)

	Theme.label(root, "ASSEMBLER", UDim2.new(0, 140, 0, 22), UDim2.new(0, 14, 0, 13), 16, {
		font = Theme.fonts.display,
		color = Theme.colors.accent,
	}).ZIndex = 41

	local function coinChip(name: string, color: Color3, x: number): TextLabel
		local chip = Instance.new("Frame")
		chip.Name = name
		chip.Size = UDim2.new(0, 88, 0, 28)
		chip.Position = UDim2.new(0, x, 0.5, -14)
		chip.BackgroundColor3 = Theme.colors.bgInset
		chip.BorderSizePixel = 0
		chip.ZIndex = 41
		chip.Parent = root
		Theme.corner(chip, Theme.radii.sm)
		Theme.stroke(chip, color, 1)
		local dot = Instance.new("Frame")
		dot.Size = UDim2.new(0, 8, 0, 8)
		dot.Position = UDim2.new(0, 8, 0.5, -4)
		dot.BackgroundColor3 = color
		dot.BorderSizePixel = 0
		dot.ZIndex = 42
		dot.Parent = chip
		Theme.corner(dot, 4)
		local lab = Instance.new("TextLabel")
		lab.Size = UDim2.new(1, -24, 1, 0)
		lab.Position = UDim2.new(0, 20, 0, 0)
		lab.BackgroundTransparency = 1
		lab.Font = Theme.fonts.mono
		lab.TextSize = 13
		lab.TextColor3 = color
		lab.TextXAlignment = Enum.TextXAlignment.Left
		lab.TextYAlignment = Enum.TextYAlignment.Center
		lab.Text = "0"
		lab.ZIndex = 42
		lab.Parent = chip
		return lab
	end

	commonLabel = coinChip("CommonChip", Theme.colors.commonCoin, 160)
	rareLabel = coinChip("RareChip", Theme.colors.rareCoin, 256)
	Tooltip.attach(root:FindFirstChild("CommonChip") :: GuiObject, "Common scrap")
	Tooltip.attach(root:FindFirstChild("RareChip") :: GuiObject, "Rare tokens")

	local levelWrap = Instance.new("Frame")
	levelWrap.Name = "LevelWrap"
	levelWrap.Size = UDim2.new(0, 180, 0, 32)
	levelWrap.Position = UDim2.new(0.5, -90, 0.5, -16)
	levelWrap.BackgroundTransparency = 1
	levelWrap.ZIndex = 41
	levelWrap.Parent = root

	local badge = Instance.new("Frame")
	badge.Size = UDim2.new(0, 28, 0, 28)
	badge.Position = UDim2.new(0, 0, 0.5, -14)
	badge.BackgroundColor3 = Theme.colors.levelBadge
	badge.BorderSizePixel = 0
	badge.ZIndex = 42
	badge.Parent = levelWrap
	Theme.corner(badge, Theme.radii.sm)
	Theme.stroke(badge, Theme.colors.ok, 1)
	levelLabel = Instance.new("TextLabel")
	levelLabel.Size = UDim2.new(1, 0, 1, 0)
	levelLabel.BackgroundTransparency = 1
	levelLabel.Font = Theme.fonts.title
	levelLabel.TextSize = 14
	levelLabel.TextColor3 = Theme.colors.text
	levelLabel.Text = "1"
	levelLabel.ZIndex = 43
	levelLabel.Parent = badge

	local xpTrack = Instance.new("Frame")
	xpTrack.Size = UDim2.new(1, -36, 0, 10)
	xpTrack.Position = UDim2.new(0, 36, 0, 6)
	xpTrack.BackgroundColor3 = Theme.colors.xpTrack
	xpTrack.BorderSizePixel = 0
	xpTrack.ZIndex = 42
	xpTrack.Parent = levelWrap
	Theme.corner(xpTrack, Theme.radii.bar)
	xpFill = Instance.new("Frame")
	xpFill.Name = "Fill"
	xpFill.Size = UDim2.new(0, 0, 1, 0)
	xpFill.BackgroundColor3 = Theme.colors.xpFill
	xpFill.BorderSizePixel = 0
	xpFill.ZIndex = 43
	xpFill.Parent = xpTrack
	Theme.corner(xpFill, Theme.radii.bar)
	xpText = Instance.new("TextLabel")
	xpText.Size = UDim2.new(1, -36, 0, 12)
	xpText.Position = UDim2.new(0, 36, 0, 18)
	xpText.BackgroundTransparency = 1
	xpText.Font = Theme.fonts.mono
	xpText.TextSize = 10
	xpText.TextColor3 = Theme.colors.textMuted
	xpText.TextXAlignment = Enum.TextXAlignment.Left
	xpText.Text = "0 / 80"
	xpText.ZIndex = 42
	xpText.Parent = levelWrap

	local crateBtn = Button.create(root, "Crate", UDim2.new(0, 64, 0, 30), UDim2.new(1, -120, 0.5, -15), "primary", {
		textSize = 12,
		zIndex = 42,
	})
	Tooltip.attach(crateBtn, "Open pending crate")
	crateBtn.MouseButton1Click:Connect(function()
		SoundHooks.play("click")
		if openCrateCb then
			openCrateCb()
		end
	end)

	local gearBtn = Button.create(root, "⚙", UDim2.new(0, 34, 0, 34), UDim2.new(1, -44, 0.5, -17), "ghost", {
		textSize = 16,
		zIndex = 42,
	})
	Tooltip.attach(gearBtn, "Settings")
	gearBtn.MouseButton1Click:Connect(function()
		SoundHooks.play("click")
		if settingsPanel.Visible then
			settingsPanel.Visible = false
			ModalMouse.pop("topSettings")
			return
		end
		ModalMouse.push("topSettings")
		TweenUtil.openFrom(
			settingsPanel,
			UDim2.new(settingsRest.X.Scale, settingsRest.X.Offset, 0, -8),
			settingsRest,
			Theme.transparency.panel
		)
	end)

	settingsRest = UDim2.new(1, -280, 0, 66)
	settingsPanel = Theme.panel(parent, "TopSettings", UDim2.new(0, 260, 0, 140), settingsRest, Theme.colors.cyan)
	settingsPanel.Visible = false
	settingsPanel.ZIndex = 50
	Theme.label(settingsPanel, "SETTINGS", UDim2.new(1, -80, 0, 20), UDim2.new(0, 14, 0, 10), 15, {
		font = Theme.fonts.title,
		color = Theme.colors.cyan,
	})
	Theme.label(settingsPanel, "V or Cam for look. Menus free the mouse.", UDim2.new(1, -24, 0, 28), UDim2.new(0, 14, 0, 34), 12, {
		color = Theme.colors.textDim,
	})
	local camBtn = Button.create(settingsPanel, "Toggle look", UDim2.new(1, -28, 0, 30), UDim2.new(0, 14, 0, 70), "cyan")
	camBtn.MouseButton1Click:Connect(function()
		LobbyCamera.toggleLook()
		SoundHooks.play("click")
	end)
	local close = Button.create(settingsPanel, "Close", UDim2.new(0, 64, 0, 24), UDim2.new(1, -78, 0, 10), "ghost")
	close.MouseButton1Click:Connect(function()
		settingsPanel.Visible = false
		ModalMouse.pop("topSettings")
	end)

	if WalletUpdated and WalletUpdated:IsA("RemoteEvent") then
		WalletUpdated.OnClientEvent:Connect(function(payload)
			if payload then
				TopbarHud.apply(payload.wallet, payload.progress)
			end
		end)
	end

	TopbarHud.apply({ common = 0, rare = 0 }, { xp = 0 })
end

return TopbarHud

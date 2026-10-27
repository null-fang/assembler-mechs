-- Pick-3 crate modal (juice surface). First-session starter + fight drops.
-- Polish only — same GetCrate / PickCrate remotes. Do not fork a second modal.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))
local TweenUtil = require(script.Parent:WaitForChild("UI"):WaitForChild("TweenUtil"))
local Motions = require(script.Parent:WaitForChild("UI"):WaitForChild("Motions"))
local SoundHooks = require(script.Parent:WaitForChild("UI"):WaitForChild("SoundHooks"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))
local Tooltip = require(script.Parent:WaitForChild("UI"):WaitForChild("Tooltip"))

local CrateHud = {}

local remotesFolder = ReplicatedStorage:WaitForChild("AssemblerRemotes")
local GetCrate = remotesFolder:WaitForChild("GetCrate")
local PickCrate = remotesFolder:WaitForChild("PickCrate")

local root: Frame?
local titleLabel: TextLabel?
local subLabel: TextLabel?
local cardRow: Frame?
local statusLabel: TextLabel?
local rest = UDim2.new(0.5, -270, 0.35, -150)
local open = false
local busy = false
local onPicked: ((any) -> ())?

local function clearCards()
	if not cardRow then
		return
	end
	for _, child in cardRow:GetChildren() do
		if child:IsA("GuiObject") and not child:IsA("UIListLayout") then
			child:Destroy()
		end
	end
end

function CrateHud.mount(parentGui: ScreenGui, callbacks: { onPicked: ((any) -> ())? }?)
	onPicked = callbacks and callbacks.onPicked
	root = Theme.panel(parentGui, "CratePanel", UDim2.new(0, 540, 0, 320), rest, Theme.colors.accent)
	root.Visible = false
	root.ZIndex = 50

	titleLabel = Theme.label(root, "CRATE", UDim2.new(1, -100, 0, 24), UDim2.new(0, 16, 0, 12), 18, {
		font = Theme.fonts.display,
		color = Theme.colors.accent,
	})
	subLabel = Theme.label(root, "Pick one. Other two scrap.", UDim2.new(1, -28, 0, 20), UDim2.new(0, 16, 0, 40), 12, {
		color = Theme.colors.textDim,
	})

	cardRow = Instance.new("Frame")
	cardRow.Name = "Cards"
	cardRow.Size = UDim2.new(1, -24, 0, 180)
	cardRow.Position = UDim2.new(0, 12, 0, 72)
	cardRow.BackgroundTransparency = 1
	cardRow.Parent = root
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.Padding = UDim.new(0, 12)
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = cardRow

	statusLabel = Theme.label(root, "", UDim2.new(1, -24, 0, 18), UDim2.new(0, 12, 1, -36), 12, {
		color = Theme.colors.textMuted,
	})

	local close = Button.create(root, "Later", UDim2.new(0, 72, 0, 28), UDim2.new(1, -86, 0, 12), "ghost")
	close.MouseButton1Click:Connect(function()
		if busy then
			return
		end
		CrateHud.setOpen(false)
	end)
end

function CrateHud.setOpen(isOpen: boolean)
	if not root then
		return
	end
	if isOpen == open and isOpen then
		CrateHud.render()
		return
	end
	open = isOpen
	ModalMouse.set("crate", isOpen)
	if isOpen then
		SoundHooks.play("open")
		root.BackgroundTransparency = Theme.transparency.panel
		TweenUtil.openFrom(root, UDim2.new(0.5, -270, 0.35, -110), rest, Theme.transparency.panel)
		Motions.popIn(root, 0.9)
		CrateHud.render()
	else
		SoundHooks.play("close")
		busy = false
		TweenUtil.closeTo(root, UDim2.new(0.5, -270, 0.35, -100), rest)
	end
end

function CrateHud.isOpen(): boolean
	return open
end

function CrateHud.render()
	clearCards()
	if not statusLabel or not cardRow then
		return
	end
	local ok, data = pcall(function()
		return GetCrate:InvokeServer()
	end)
	if not ok or not data or not data.pending then
		statusLabel.Text = "No crate waiting."
		if titleLabel then
			titleLabel.Text = "CRATE"
		end
		if subLabel then
			subLabel.Text = "Pick one. Other two scrap."
		end
		Theme.label(cardRow, "Come back after a fight drop — or finish onboarding.", UDim2.new(1, 0, 0, 40), UDim2.new(0, 0, 0, 50), 13, {
			color = Theme.colors.textMuted,
		})
		return
	end
	local offer = data.pending
	local isStarter = offer.source == "starter"
	if titleLabel then
		titleLabel.Text = if isStarter then "BAY CRATE" else "FIGHT DROP"
	end
	if subLabel then
		subLabel.Text = if isStarter then "First pull — keep one part." else "Loot from the bay — keep one."
	end
	statusLabel.Text = if isStarter then "Starter crate · pick 1 of 3" else "Fight drop · pick 1 of 3"
	SoundHooks.play("crateReveal")

	local cards = {}
	for _, card in offer.options do
		local color = Theme.rarityColor(card.rarity)
		local frame = Instance.new("TextButton")
		frame.Name = "Card_" .. tostring(card.index)
		frame.Size = UDim2.new(0, 156, 0, 172)
		frame.BackgroundColor3 = Theme.colors.bgRaised
		frame.BorderSizePixel = 0
		frame.AutoButtonColor = false
		frame.Text = ""
		frame.LayoutOrder = card.index
		frame.Visible = false
		frame.Parent = cardRow
		Theme.corner(frame, Theme.radii.md)
		local stroke = Theme.glowStroke(frame, color, 2)

		local banner = Instance.new("Frame")
		banner.Size = UDim2.new(1, 0, 0, 24)
		banner.BackgroundColor3 = color
		banner.BackgroundTransparency = 0.2
		banner.BorderSizePixel = 0
		banner.Parent = frame
		local rarityLab = Instance.new("TextLabel")
		rarityLab.Size = UDim2.new(1, -8, 1, 0)
		rarityLab.Position = UDim2.new(0, 4, 0, 0)
		rarityLab.BackgroundTransparency = 1
		rarityLab.Font = Theme.fonts.button
		rarityLab.TextSize = 11
		rarityLab.TextColor3 = Theme.colors.textOnAccent
		rarityLab.Text = string.upper(card.rarity or "Common")
		rarityLab.Parent = banner

		local name = Instance.new("TextLabel")
		name.Size = UDim2.new(1, -12, 0, 44)
		name.Position = UDim2.new(0, 6, 0, 34)
		name.BackgroundTransparency = 1
		name.Font = Theme.fonts.button
		name.TextSize = 14
		name.TextColor3 = Theme.colors.text
		name.TextWrapped = true
		name.Text = card.name
		name.Parent = frame

		local meta = Instance.new("TextLabel")
		meta.Size = UDim2.new(1, -12, 0, 36)
		meta.Position = UDim2.new(0, 6, 0, 82)
		meta.BackgroundTransparency = 1
		meta.Font = Theme.fonts.body
		meta.TextSize = 11
		meta.TextColor3 = Theme.colors.textDim
		meta.TextWrapped = true
		meta.Text = ("%s · w%d"):format(card.slot or "Part", card.weight or 0)
		meta.Parent = frame

		local pick = Button.create(frame, "Keep", UDim2.new(1, -16, 0, 28), UDim2.new(0, 8, 1, -36), "primary")
		Tooltip.attach(pick, card.tooltip or card.name)
		Tooltip.attach(frame, card.tooltip or card.name)
		local index = card.index
		local function keep()
			if busy then
				return
			end
			busy = true
			SoundHooks.play("cratePick")
			statusLabel.Text = "Keeping " .. (card.name or "part") .. "…"
			local result = PickCrate:InvokeServer(index)
			busy = false
			if not result or not result.ok then
				statusLabel.Text = (result and result.error) or "Pick failed"
				return
			end
			statusLabel.Text = "Kept " .. (result.chosen and result.chosen.name or "part")
			CrateHud.setOpen(false)
			if onPicked then
				onPicked(result)
			end
		end
		pick.MouseButton1Click:Connect(keep)
		frame.MouseButton1Click:Connect(keep)
		frame.MouseEnter:Connect(function()
			TweenUtil.play(frame, Theme.tween.hover, { BackgroundColor3 = Theme.colors.bgHover })
			TweenUtil.play(stroke, Theme.tween.hover, { Thickness = 2.5 })
		end)
		frame.MouseLeave:Connect(function()
			TweenUtil.play(frame, Theme.tween.hover, { BackgroundColor3 = Theme.colors.bgRaised })
			TweenUtil.play(stroke, Theme.tween.hover, { Thickness = 2 })
		end)
		table.insert(cards, frame)
	end

	for i, frame in cards do
		task.delay(0.1 * (i - 1), function()
			if frame.Parent then
				Motions.popIn(frame, 0.55)
				local scale = frame:FindFirstChildOfClass("UIScale")
				if scale then
					scale.Scale = 0.45
					TweenService:Create(scale, Theme.tween.pop, { Scale = 1 }):Play()
				end
			end
		end)
	end
end

return CrateHud

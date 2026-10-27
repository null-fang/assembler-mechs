-- Pick-3 crate modal. First-session starter + fight drops.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))
local TweenUtil = require(script.Parent:WaitForChild("UI"):WaitForChild("TweenUtil"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))
local Tooltip = require(script.Parent:WaitForChild("UI"):WaitForChild("Tooltip"))

local CrateHud = {}

local remotesFolder = ReplicatedStorage:WaitForChild("AssemblerRemotes")
local GetCrate = remotesFolder:WaitForChild("GetCrate")
local PickCrate = remotesFolder:WaitForChild("PickCrate")

local root: Frame?
local cardRow: Frame?
local statusLabel: TextLabel?
local rest = UDim2.new(0.5, -250, 0.35, -120)
local open = false
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
	root = Theme.panel(parentGui, "CratePanel", UDim2.new(0, 500, 0, 280), rest, Theme.colors.accent)
	root.Visible = false
	root.ZIndex = 50

	Theme.label(root, "CRATE", UDim2.new(1, -100, 0, 24), UDim2.new(0, 16, 0, 12), 18, {
		font = Theme.fonts.display,
		color = Theme.colors.accent,
	})
	Theme.label(root, "Pick one. Other two scrap.", UDim2.new(1, -28, 0, 20), UDim2.new(0, 16, 0, 40), 12, {
		color = Theme.colors.textDim,
	})

	cardRow = Instance.new("Frame")
	cardRow.Name = "Cards"
	cardRow.Size = UDim2.new(1, -24, 0, 140)
	cardRow.Position = UDim2.new(0, 12, 0, 72)
	cardRow.BackgroundTransparency = 1
	cardRow.Parent = root
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.Padding = UDim.new(0, 10)
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.Parent = cardRow

	statusLabel = Theme.label(root, "", UDim2.new(1, -24, 0, 18), UDim2.new(0, 12, 1, -36), 12, {
		color = Theme.colors.textMuted,
	})

	local close = Button.create(root, "Later", UDim2.new(0, 72, 0, 28), UDim2.new(1, -86, 0, 12), "ghost")
	close.MouseButton1Click:Connect(function()
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
		root.BackgroundTransparency = Theme.transparency.panel
		TweenUtil.openFrom(root, UDim2.new(0.5, -250, 0.35, -90), rest, Theme.transparency.panel)
		CrateHud.render()
	else
		TweenUtil.closeTo(root, UDim2.new(0.5, -250, 0.35, -80), rest)
	end
end

function CrateHud.isOpen(): boolean
	return open
end

function CrateHud.render()
	clearCards()
	if not statusLabel then
		return
	end
	local ok, data = pcall(function()
		return GetCrate:InvokeServer()
	end)
	if not ok or not data or not data.pending then
		statusLabel.Text = "No crate waiting."
		Theme.label(cardRow, "Come back after a fight drop — or finish onboarding.", UDim2.new(1, 0, 0, 40), UDim2.new(0, 0, 0, 40), 13, {
			color = Theme.colors.textMuted,
		})
		return
	end
	local offer = data.pending
	statusLabel.Text = if offer.source == "starter" then "Starter crate" else "Fight drop"
	for _, card in offer.options do
		local frame = Instance.new("Frame")
		frame.Size = UDim2.new(0, 148, 0, 132)
		frame.BackgroundColor3 = Theme.colors.bgRaised
		frame.BorderSizePixel = 0
		frame.Parent = cardRow
		Theme.corner(frame, Theme.radii.sm)
		Theme.stroke(frame, Theme.rarityColor(card.rarity), 1.5)

		local name = Instance.new("TextLabel")
		name.Size = UDim2.new(1, -12, 0, 40)
		name.Position = UDim2.new(0, 6, 0, 10)
		name.BackgroundTransparency = 1
		name.Font = Theme.fonts.button
		name.TextSize = 14
		name.TextColor3 = Theme.colors.text
		name.TextWrapped = true
		name.Text = card.name
		name.Parent = frame

		local meta = Instance.new("TextLabel")
		meta.Size = UDim2.new(1, -12, 0, 36)
		meta.Position = UDim2.new(0, 6, 0, 52)
		meta.BackgroundTransparency = 1
		meta.Font = Theme.fonts.body
		meta.TextSize = 11
		meta.TextColor3 = Theme.colors.textDim
		meta.TextWrapped = true
		meta.Text = ("%s · %s · w%d"):format(card.rarity, card.slot, card.weight)
		meta.Parent = frame

		local pick = Button.create(frame, "Keep", UDim2.new(1, -16, 0, 28), UDim2.new(0, 8, 1, -36), "primary")
		Tooltip.attach(pick, card.tooltip or card.name)
		local index = card.index
		pick.MouseButton1Click:Connect(function()
			local result = PickCrate:InvokeServer(index)
			if not result or not result.ok then
				statusLabel.Text = (result and result.error) or "Pick failed"
				return
			end
			statusLabel.Text = "Kept " .. (result.chosen and result.chosen.name or "part")
			CrateHud.setOpen(false)
			if onPicked then
				onPicked(result)
			end
		end)
	end
end

return CrateHud

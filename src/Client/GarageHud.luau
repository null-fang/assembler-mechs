-- Garage: slot + bag panels with rarity color, tweens, short tooltips.
-- ModalMouse unlocks mouse while open.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))
local TweenUtil = require(script.Parent:WaitForChild("UI"):WaitForChild("TweenUtil"))
local Tooltip = require(script.Parent:WaitForChild("UI"):WaitForChild("Tooltip"))

local GarageHud = {}

local remotesFolder = ReplicatedStorage:WaitForChild("AssemblerRemotes")
local GetInventory = remotesFolder:WaitForChild("GetInventory")
local EquipPart = remotesFolder:WaitForChild("EquipPart")
local UnequipPart = remotesFolder:WaitForChild("UnequipPart")
local InventoryUpdated = remotesFolder:WaitForChild("InventoryUpdated")

local root
local slotList
local bagList
local statusLabel
local titleSub: TextLabel
local open = false
local snapshot
local selectedSlot: string? = nil
local restPos = UDim2.new(1, -548, 0, 24)
local openedListeners: { () -> () } = {}

local SLOT_ROWS = {
	{ field = "torso", label = "Torso" },
	{ field = "leftLeg", label = "Left leg" },
	{ field = "rightLeg", label = "Right leg" },
	{ field = "lowerLeft", label = "Lower L" },
	{ field = "lowerRight", label = "Lower R" },
	{ field = "shoulderLeft", label = "Shoulder L" },
	{ field = "shoulderRight", label = "Shoulder R" },
	{ field = "battery", label = "Battery" },
	{ field = "cpu", label = "CPU" },
	{ field = "drone", label = "Drone" },
	{ field = "chip:1", label = "Chip 1" },
	{ field = "chip:2", label = "Chip 2" },
	{ field = "Chip", label = "Chip (add)" },
}

local function clear(frame)
	for _, child in frame:GetChildren() do
		if child:IsA("GuiObject") and not child:IsA("UIListLayout") and not child:IsA("UIPadding") then
			child:Destroy()
		end
	end
end

local function equippedName(field: string): string
	if not snapshot then
		return "—"
	end
	local lo = snapshot.loadout
	if field == "torso" then
		return lo.torso or "—"
	elseif field == "leftLeg" or field == "rightLeg" then
		for _, owned in snapshot.owned do
			if owned.equipField == field then
				return owned.summary.name
			end
		end
		return "—"
	elseif field == "lowerLeft" then
		return lo.lowerLeft or "—"
	elseif field == "lowerRight" then
		return lo.lowerRight or "—"
	elseif field == "shoulderLeft" then
		return lo.shoulderLeft or "—"
	elseif field == "shoulderRight" then
		return lo.shoulderRight or "—"
	elseif field == "battery" then
		return lo.battery or "—"
	elseif field == "cpu" then
		return lo.cpu or "—"
	elseif field == "drone" then
		return lo.drone or "—"
	elseif string.sub(field, 1, 5) == "chip:" then
		local uid = snapshot.equipped and snapshot.equipped[field]
		if uid then
			for _, owned in snapshot.owned do
				if owned.uid == uid then
					return owned.summary.name
				end
			end
		end
		return "—"
	elseif field == "Chip" then
		return ("%d / %d"):format(lo.chips or 0, snapshot.maxChips or 2)
	end
	return "—"
end

local function partFitsSlot(summary, field: string): boolean
	local slot = summary.slot
	if field == "Chip" or string.sub(field, 1, 5) == "chip:" then
		return slot == "Chip"
	end
	if field == "lowerLeft" or field == "lowerRight" then
		return summary.mountClass == "Lower" or slot == "LowerLeft" or slot == "LowerRight"
	end
	if field == "shoulderLeft" or field == "shoulderRight" then
		return summary.mountClass == "Shoulder" or slot == "ShoulderLeft" or slot == "ShoulderRight"
	end
	local map = {
		torso = "Torso",
		leftLeg = "LeftLeg",
		rightLeg = "RightLeg",
		battery = "Battery",
		cpu = "CPU",
		drone = "Drone",
	}
	return slot == map[field]
end

local function setStatus(text)
	statusLabel.Text = text
end

local function refreshBag()
	clear(bagList)
	if not snapshot or not selectedSlot then
		Theme.label(bagList, "Pick a slot.", UDim2.new(1, -4, 0, 36), UDim2.new(0, 0, 0, 0), 12, {
			color = Theme.colors.textMuted,
		})
		return
	end
	local any = false
	for _, owned in snapshot.owned do
		if owned.equippedOn then
			continue
		end
		if not partFitsSlot(owned.summary, selectedSlot) then
			continue
		end
		any = true
		local s = owned.summary
		local row = Instance.new("Frame")
		row.Size = UDim2.new(1, -4, 0, 36)
		row.BackgroundTransparency = 1
		row.Parent = bagList

		local btn = Button.create(row, ("%s  ·  w%d"):format(s.name, s.weight), UDim2.new(1, 0, 1, 0), nil, "card", {
			textXAlignment = Enum.TextXAlignment.Left,
			textSize = 12,
		})
		btn.TextColor3 = Theme.rarityColor(s.rarity)

		local dot = Instance.new("Frame")
		dot.Size = UDim2.new(0, 4, 1, -10)
		dot.Position = UDim2.new(0, 3, 0, 5)
		dot.BackgroundColor3 = Theme.rarityColor(s.rarity)
		dot.BorderSizePixel = 0
		dot.Parent = btn
		Theme.corner(dot, 2)

		local uid = owned.uid
		local slot = selectedSlot
		Tooltip.attach(btn, s.tooltip or s.name)
		btn.MouseButton1Click:Connect(function()
			local result = EquipPart:InvokeServer(uid, slot)
			if not result.ok then
				setStatus(result.error or "Equip failed")
				return
			end
			snapshot = result.inventory
			setStatus("Equipped " .. s.name)
			GarageHud.render()
		end)
	end
	if not any then
		Theme.label(bagList, "No spare parts for this slot.", UDim2.new(1, -4, 0, 36), UDim2.new(0, 0, 0, 0), 12, {
			color = Theme.colors.textMuted,
		})
	end
end

local function refreshSlots()
	clear(slotList)
	if not snapshot then
		return
	end
	for _, rowDef in SLOT_ROWS do
		local name = equippedName(rowDef.field)
		local row = Instance.new("Frame")
		row.Size = UDim2.new(1, -4, 0, 32)
		row.BackgroundTransparency = 1
		row.Parent = slotList

		local hasX = rowDef.field ~= "Chip" and name ~= "—"
		local btn = Button.create(
			row,
			("%s — %s"):format(rowDef.label, name),
			UDim2.new(1, if hasX then -36 else 0, 1, 0),
			nil,
			"card",
			{ textXAlignment = Enum.TextXAlignment.Left, textSize = 12 }
		)
		if selectedSlot == rowDef.field then
			Button.setSelected(btn, true)
		end
		local field = rowDef.field
		btn.MouseButton1Click:Connect(function()
			selectedSlot = field
			GarageHud.render()
		end)
		if hasX then
			local x = Button.create(row, "×", UDim2.new(0, 30, 1, 0), UDim2.new(1, -30, 0, 0), "danger", { textSize = 14 })
			Tooltip.attach(x, "Unequip")
			x.MouseButton1Click:Connect(function()
				local result = UnequipPart:InvokeServer(field)
				if not result.ok then
					setStatus(result.error or "Unequip failed")
					return
				end
				snapshot = result.inventory
				setStatus("Removed from " .. rowDef.label)
				GarageHud.render()
			end)
		end
	end
end

function GarageHud.render()
	if not open then
		return
	end
	local lo = snapshot and snapshot.loadout
	if lo then
		local legal = if lo.legal then "ready" else "incomplete"
		titleSub.Text = ("Primary · %s · weight %d · %s"):format(lo.torso or "?", lo.weight or 0, legal)
	end
	refreshSlots()
	refreshBag()
end

function GarageHud.applySnapshot(snap)
	snapshot = snap
	GarageHud.render()
end

function GarageHud.onOpened(cb: () -> ())
	table.insert(openedListeners, cb)
end

function GarageHud.setOpen(isOpen: boolean)
	if isOpen == open and isOpen then
		snapshot = GetInventory:InvokeServer()
		GarageHud.render()
		return
	end
	open = isOpen
	ModalMouse.set("garage", isOpen)
	if isOpen then
		snapshot = GetInventory:InvokeServer()
		root.BackgroundTransparency = Theme.transparency.panel
		TweenUtil.openFrom(
			root,
			UDim2.new(1, restPos.X.Offset + 28, 0, restPos.Y.Offset),
			restPos,
			Theme.transparency.panel
		)
		GarageHud.render()
		for _, cb in openedListeners do
			cb()
		end
	else
		TweenUtil.closeTo(root, UDim2.new(1, restPos.X.Offset + 24, 0, restPos.Y.Offset), restPos, function()
			root.BackgroundTransparency = Theme.transparency.panel
		end)
	end
end

function GarageHud.toggle()
	GarageHud.setOpen(not open)
end

function GarageHud.isOpen(): boolean
	return open
end

function GarageHud.mount(parentGui: ScreenGui)
	root = Theme.panel(parentGui, "GaragePanel", UDim2.new(0, 530, 0, 400), restPos, Theme.colors.garage)
	root.Visible = false

	Theme.label(root, "GARAGE", UDim2.new(1, -100, 0, 24), UDim2.new(0, 16, 0, 12), 18, {
		font = Theme.fonts.display,
		color = Theme.colors.accent,
	})
	titleSub = Theme.label(root, "Primary loadout", UDim2.new(1, -100, 0, 18), UDim2.new(0, 16, 0, 38), 12, {
		color = Theme.colors.textDim,
	})
	statusLabel = Theme.label(root, "", UDim2.new(1, -24, 0, 18), UDim2.new(0, 16, 1, -28), 11, {
		color = Theme.colors.textMuted,
	})

	slotList = Instance.new("ScrollingFrame")
	slotList.Name = "Slots"
	slotList.Size = UDim2.new(0.48, -12, 1, -90)
	slotList.Position = UDim2.new(0, 12, 0, 64)
	slotList.BackgroundTransparency = 1
	slotList.ScrollBarThickness = 3
	slotList.ScrollBarImageColor3 = Theme.colors.cyanDeep
	slotList.BorderSizePixel = 0
	slotList.AutomaticCanvasSize = Enum.AutomaticSize.Y
	slotList.CanvasSize = UDim2.new(0, 0, 0, 0)
	slotList.Parent = root
	local leftList = Instance.new("UIListLayout")
	leftList.Padding = UDim.new(0, 6)
	leftList.Parent = slotList

	bagList = Instance.new("ScrollingFrame")
	bagList.Name = "Bag"
	bagList.Size = UDim2.new(0.48, -12, 1, -90)
	bagList.Position = UDim2.new(0.52, 0, 0, 64)
	bagList.BackgroundTransparency = 1
	bagList.ScrollBarThickness = 3
	bagList.ScrollBarImageColor3 = Theme.colors.cyanDeep
	bagList.BorderSizePixel = 0
	bagList.AutomaticCanvasSize = Enum.AutomaticSize.Y
	bagList.CanvasSize = UDim2.new(0, 0, 0, 0)
	bagList.Parent = root
	local rightList = Instance.new("UIListLayout")
	rightList.Padding = UDim.new(0, 6)
	rightList.Parent = bagList

	local close = Button.create(root, "Close", UDim2.new(0, 72, 0, 28), UDim2.new(1, -86, 0, 12), "ghost")
	close.MouseButton1Click:Connect(function()
		GarageHud.setOpen(false)
	end)

	InventoryUpdated.OnClientEvent:Connect(function(snap)
		snapshot = snap
		if open then
			GarageHud.render()
		end
	end)
end

return GarageHud

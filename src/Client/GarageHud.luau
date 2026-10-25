-- Garage: secondary panel for swapping owned parts. Modal unlocks mouse.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))

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
local open = false
local snapshot
local selectedSlot: string? = nil

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
		if child:IsA("GuiObject") and child.Name ~= "Title" then
			child:Destroy()
		end
	end
end

local function rarityColor(rarity: string): Color3
	if rarity == "Rare" then
		return Color3.fromRGB(210, 170, 70)
	elseif rarity == "Uncommon" then
		return Color3.fromRGB(140, 180, 120)
	end
	return Theme.colors.textDim
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
		Theme.label(bagList, "Pick a slot on the left.", UDim2.new(1, -8, 0, 40), UDim2.new(0, 4, 0, 4), 12, {
			color = Theme.colors.textDim,
		})
		return
	end
	local y = 4
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
		local line = ("%s  ·  %s  ·  w%d"):format(s.name, s.rarity, s.weight)
		local btn = Theme.button(bagList, line, UDim2.new(1, -8, 0, 30), UDim2.new(0, 4, 0, y), {
			bg = Theme.colors.bgRaised,
			textColor = rarityColor(s.rarity),
		})
		btn.TextXAlignment = Enum.TextXAlignment.Left
		local pad = Instance.new("UIPadding")
		pad.PaddingLeft = UDim.new(0, 8)
		pad.Parent = btn
		local uid = owned.uid
		local slot = selectedSlot
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
		btn.MouseEnter:Connect(function()
			setStatus(s.tooltip or s.name)
		end)
		y += 34
	end
	if not any then
		Theme.label(bagList, "No spare parts for this slot.", UDim2.new(1, -8, 0, 40), UDim2.new(0, 4, 0, 4), 12, {
			color = Theme.colors.textDim,
		})
	end
	bagList.CanvasSize = UDim2.new(0, 0, 0, y + 8)
end

local function refreshSlots()
	clear(slotList)
	if not snapshot then
		return
	end
	local y = 4
	for _, row in SLOT_ROWS do
		local name = equippedName(row.field)
		local label = ("%s — %s"):format(row.label, name)
		local btn = Theme.button(slotList, label, UDim2.new(1, -8, 0, 28), UDim2.new(0, 4, 0, y), {
			bg = if selectedSlot == row.field then Theme.colors.cyanDeep else Theme.colors.bgRaised,
		})
		btn.TextXAlignment = Enum.TextXAlignment.Left
		local pad = Instance.new("UIPadding")
		pad.PaddingLeft = UDim.new(0, 8)
		pad.Parent = btn
		local field = row.field
		btn.MouseButton1Click:Connect(function()
			selectedSlot = field
			GarageHud.render()
		end)
		if field ~= "Chip" and name ~= "—" then
			local x = Theme.button(slotList, "×", UDim2.new(0, 28, 0, 28), UDim2.new(1, -36, 0, y), {
				bg = Theme.colors.danger,
			})
			x.MouseButton1Click:Connect(function()
				local result = UnequipPart:InvokeServer(field)
				if not result.ok then
					setStatus(result.error or "Unequip failed")
					return
				end
				snapshot = result.inventory
				setStatus("Removed from " .. row.label)
				GarageHud.render()
			end)
		end
		y += 32
	end
	slotList.CanvasSize = UDim2.new(0, 0, 0, y + 8)
end

function GarageHud.render()
	if not open then
		return
	end
	local lo = snapshot and snapshot.loadout
	if lo then
		local legal = if lo.legal then "ready" else "incomplete"
		statusLabel.Text = ("Primary · %s · weight %d · %s"):format(lo.torso or "?", lo.weight or 0, legal)
	end
	refreshSlots()
	refreshBag()
end

function GarageHud.applySnapshot(snap)
	snapshot = snap
	GarageHud.render()
end

function GarageHud.setOpen(isOpen: boolean)
	open = isOpen
	root.Visible = isOpen
	ModalMouse.set("garage", isOpen)
	if isOpen then
		snapshot = GetInventory:InvokeServer()
		GarageHud.render()
	end
end

function GarageHud.toggle()
	GarageHud.setOpen(not open)
end

function GarageHud.isOpen(): boolean
	return open
end

function GarageHud.mount(parentGui: ScreenGui)
	root = Theme.panel(parentGui, "GaragePanel", UDim2.new(0, 520, 0, 380), UDim2.new(1, -540, 0, 24))
	root.Visible = false

	Theme.label(root, "Garage — Primary", UDim2.new(1, -100, 0, 24), UDim2.new(0, 14, 0, 10), 18, {
		font = Theme.fonts.title,
		color = Theme.colors.accent,
	})
	statusLabel = Theme.label(root, "", UDim2.new(1, -24, 0, 20), UDim2.new(0, 14, 0, 36), 12, {
		color = Theme.colors.textDim,
	})

	slotList = Instance.new("ScrollingFrame")
	slotList.Name = "Slots"
	slotList.Size = UDim2.new(0.48, -10, 1, -78)
	slotList.Position = UDim2.new(0, 8, 0, 62)
	slotList.BackgroundTransparency = 1
	slotList.ScrollBarThickness = 4
	slotList.BorderSizePixel = 0
	slotList.CanvasSize = UDim2.new(0, 0, 0, 0)
	slotList.Parent = root

	bagList = Instance.new("ScrollingFrame")
	bagList.Name = "Bag"
	bagList.Size = UDim2.new(0.48, -10, 1, -78)
	bagList.Position = UDim2.new(0.5, 2, 0, 62)
	bagList.BackgroundTransparency = 1
	bagList.ScrollBarThickness = 4
	bagList.BorderSizePixel = 0
	bagList.CanvasSize = UDim2.new(0, 0, 0, 0)
	bagList.Parent = root

	local close = Theme.button(root, "Close", UDim2.new(0, 72, 0, 26), UDim2.new(1, -86, 0, 10), {
		bg = Theme.colors.bgInset,
	})
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

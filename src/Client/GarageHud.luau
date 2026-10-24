-- Garage: secondary panel for swapping owned parts. World stays primary.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GarageHud = {}

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local remotesFolder = ReplicatedStorage:WaitForChild("AssemblerRemotes")
local GetInventory = remotesFolder:WaitForChild("GetInventory")
local EquipPart = remotesFolder:WaitForChild("EquipPart")
local UnequipPart = remotesFolder:WaitForChild("UnequipPart")
local InventoryUpdated = remotesFolder:WaitForChild("InventoryUpdated")

local screen
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

local function makeLabel(parent, text, size, pos, textSize)
	local l = Instance.new("TextLabel")
	l.Size = size
	l.Position = pos
	l.BackgroundTransparency = 1
	l.TextColor3 = Color3.fromRGB(220, 220, 220)
	l.Font = Enum.Font.Gotham
	l.TextSize = textSize or 13
	l.TextXAlignment = Enum.TextXAlignment.Left
	l.TextYAlignment = Enum.TextYAlignment.Top
	l.TextWrapped = true
	l.Text = text
	l.Parent = parent
	return l
end

local function makeButton(parent, text, size, pos)
	local b = Instance.new("TextButton")
	b.Size = size
	b.Position = pos
	b.BackgroundColor3 = Color3.fromRGB(42, 48, 58)
	b.BorderSizePixel = 0
	b.TextColor3 = Color3.fromRGB(230, 230, 230)
	b.Font = Enum.Font.GothamMedium
	b.TextSize = 13
	b.Text = text
	b.AutoButtonColor = true
	b.Parent = parent
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 4)
	corner.Parent = b
	return b
end

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
	return Color3.fromRGB(170, 175, 185)
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
		makeLabel(bagList, "Pick a slot on the left.", UDim2.new(1, -8, 0, 40), UDim2.new(0, 4, 0, 4), 12)
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
		local btn = makeButton(bagList, line, UDim2.new(1, -8, 0, 30), UDim2.new(0, 4, 0, y))
		btn.TextColor3 = rarityColor(s.rarity)
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
		makeLabel(bagList, "No spare parts for this slot.", UDim2.new(1, -8, 0, 40), UDim2.new(0, 4, 0, 4), 12)
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
		local btn = makeButton(slotList, label, UDim2.new(1, -8, 0, 28), UDim2.new(0, 4, 0, y))
		btn.TextXAlignment = Enum.TextXAlignment.Left
		local pad = Instance.new("UIPadding")
		pad.PaddingLeft = UDim.new(0, 8)
		pad.Parent = btn
		if selectedSlot == row.field then
			btn.BackgroundColor3 = Color3.fromRGB(70, 90, 120)
		end
		local field = row.field
		btn.MouseButton1Click:Connect(function()
			selectedSlot = field
			GarageHud.render()
		end)
		-- Unequip on right-ish: small × for non-chip-add
		if field ~= "Chip" and name ~= "—" then
			local x = makeButton(slotList, "×", UDim2.new(0, 28, 0, 28), UDim2.new(1, -36, 0, y))
			x.BackgroundColor3 = Color3.fromRGB(70, 40, 40)
			x.MouseButton1Click:Connect(function()
				local unequipField = field
				-- For chips we'd need chip:N; chip add row doesn't unequip.
				local result = UnequipPart:InvokeServer(unequipField)
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

function GarageHud.mount(parentGui: ScreenGui?)
	screen = parentGui
	if not screen then
		screen = Instance.new("ScreenGui")
		screen.Name = "AssemblerGarage"
		screen.ResetOnSpawn = false
		screen.Parent = playerGui
	end

	root = Instance.new("Frame")
	root.Name = "GaragePanel"
	root.Size = UDim2.new(0, 520, 0, 360)
	root.Position = UDim2.new(1, -536, 0, 16)
	root.BackgroundColor3 = Color3.fromRGB(16, 18, 22)
	root.BackgroundTransparency = 0.08
	root.BorderSizePixel = 0
	root.Visible = false
	root.Parent = screen
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 8)
	corner.Parent = root

	makeLabel(root, "Garage — Primary", UDim2.new(1, -20, 0, 24), UDim2.new(0, 12, 0, 8), 18).Font =
		Enum.Font.GothamBold
	statusLabel = makeLabel(root, "", UDim2.new(1, -20, 0, 20), UDim2.new(0, 12, 0, 34), 12)
	statusLabel.TextColor3 = Color3.fromRGB(170, 180, 190)

	local left = Instance.new("ScrollingFrame")
	left.Name = "Slots"
	left.Size = UDim2.new(0.48, -10, 1, -70)
	left.Position = UDim2.new(0, 8, 0, 58)
	left.BackgroundTransparency = 1
	left.ScrollBarThickness = 4
	left.BorderSizePixel = 0
	left.Parent = root
	slotList = left

	local right = Instance.new("ScrollingFrame")
	right.Name = "Bag"
	right.Size = UDim2.new(0.48, -10, 1, -70)
	right.Position = UDim2.new(0.5, 2, 0, 58)
	right.BackgroundTransparency = 1
	right.ScrollBarThickness = 4
	right.BorderSizePixel = 0
	right.Parent = root
	bagList = right

	local close = makeButton(root, "Close", UDim2.new(0, 72, 0, 26), UDim2.new(1, -84, 0, 8))
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

-- Garage: slot + bag panels with rarity color, tweens, short tooltips.
-- ModalMouse unlocks mouse while open.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))
local TweenUtil = require(script.Parent:WaitForChild("UI"):WaitForChild("TweenUtil"))
local Tooltip = require(script.Parent:WaitForChild("UI"):WaitForChild("Tooltip"))

local GarageHud = {}

local SoundHooks = require(script.Parent:WaitForChild("UI"):WaitForChild("SoundHooks"))
local Motions = require(script.Parent:WaitForChild("UI"):WaitForChild("Motions"))

local remotesFolder = ReplicatedStorage:WaitForChild("AssemblerRemotes")
local GetInventory = remotesFolder:WaitForChild("GetInventory")
local EquipPart = remotesFolder:WaitForChild("EquipPart")
local UnequipPart = remotesFolder:WaitForChild("UnequipPart")
local SellPart = remotesFolder:WaitForChild("SellPart")
local InventoryUpdated = remotesFolder:WaitForChild("InventoryUpdated")

local root
local slotList
local bagList
local comparePanel
local statusLabel
local titleSub: TextLabel
local open = false
local snapshot
local selectedSlot: string? = nil
local selectedOwned: any? = nil
local restPos = UDim2.new(1, -548, 0, 66)
local openedListeners: { () -> () } = {}
local confirmRoot: Frame?
local onWalletRefresh: (() -> ())?

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

local function equippedOwned(field: string): any?
	if not snapshot or field == "Chip" then
		return nil
	end
	local uid = snapshot.equipped and snapshot.equipped[field]
	if uid then
		for _, owned in snapshot.owned do
			if owned.uid == uid then
				return owned
			end
		end
	end
	for _, owned in snapshot.owned do
		if owned.equipField == field then
			return owned
		end
	end
	return nil
end

local function statLines(summary): { string }
	local lines = { ("Weight %d"):format(summary.weight or 0) }
	if summary.damage then
		table.insert(lines, ("%s %d"):format(summary.damageType or "Dmg", summary.damage))
	end
	if summary.integrity then
		table.insert(lines, ("INT %d"):format(summary.integrity))
	end
	if summary.sellWorth then
		table.insert(lines, ("Sell %d"):format(summary.sellWorth))
	end
	return lines
end

local function refreshCompare()
	if not comparePanel then
		return
	end
	clear(comparePanel)
	if not selectedOwned then
		Theme.label(comparePanel, "Tap a spare to compare vs equipped.", UDim2.new(1, -8, 0, 36), UDim2.new(0, 4, 0, 8), 12, {
			color = Theme.colors.textMuted,
		})
		return
	end
	local s = selectedOwned.summary
	Theme.label(comparePanel, s.name, UDim2.new(1, -8, 0, 18), UDim2.new(0, 4, 0, 4), 13, {
		font = Theme.fonts.button,
		color = Theme.rarityColor(s.rarity),
	})
	local eq = if selectedSlot then equippedOwned(selectedSlot) else nil
	local bagStats = statLines(s)
	local eqStats = if eq then statLines(eq.summary) else {}
	Theme.label(comparePanel, "Bag", UDim2.new(0.5, -6, 0, 14), UDim2.new(0, 4, 0, 26), 11, {
		color = Theme.colors.accent,
	})
	Theme.label(comparePanel, "On mech", UDim2.new(0.5, -6, 0, 14), UDim2.new(0.5, 0, 0, 26), 11, {
		color = Theme.colors.cyan,
	})
	local y = 42
	for i = 1, math.max(#bagStats, #eqStats) do
		local bagLine = bagStats[i]
		local eqLine = eqStats[i]
		local bagColor = Theme.colors.text
		-- Soft upgrade cue when bag weight is lower or sell worth higher.
		if bagLine and eqLine and string.find(bagLine, "Sell") and string.find(eqLine, "Sell") then
			local bagN = tonumber(string.match(bagLine, "%d+"))
			local eqN = tonumber(string.match(eqLine, "%d+"))
			if bagN and eqN and bagN > eqN then
				bagColor = Theme.colors.ok
			end
		end
		Theme.label(comparePanel, bagLine or "—", UDim2.new(0.5, -6, 0, 14), UDim2.new(0, 4, 0, y), 11, {
			color = bagColor,
		})
		Theme.label(comparePanel, eqLine or "—", UDim2.new(0.5, -6, 0, 14), UDim2.new(0.5, 0, 0, y), 11, {
			color = Theme.colors.textDim,
		})
		y += 14
	end
	Theme.label(comparePanel, "Upgrade stub · tiers later", UDim2.new(1, -8, 0, 14), UDim2.new(0, 4, 0, y + 4), 10, {
		color = Theme.colors.textMuted,
	})
end

local function hideConfirm()
	if confirmRoot then
		confirmRoot.Visible = false
		ModalMouse.pop("sellConfirm")
	end
end

local function askSell(owned)
	if not confirmRoot then
		return
	end
	ModalMouse.push("sellConfirm")
	confirmRoot.Visible = true
	Motions.popIn(confirmRoot, 0.92)
	local nameLab = confirmRoot:FindFirstChild("NameLab") :: TextLabel?
	local worthLab = confirmRoot:FindFirstChild("WorthLab") :: TextLabel?
	if nameLab then
		nameLab.Text = owned.summary.name
		nameLab.TextColor3 = Theme.rarityColor(owned.summary.rarity)
	end
	if worthLab then
		worthLab.Text = ("Sell for %d common?"):format(owned.summary.sellWorth or 0)
	end
	confirmRoot:SetAttribute("SellUid", owned.uid)
end

local function refreshBag()
	clear(bagList)
	selectedOwned = nil
	if not snapshot or not selectedSlot then
		Theme.label(bagList, "Pick a slot.", UDim2.new(1, -4, 0, 36), UDim2.new(0, 0, 0, 0), 12, {
			color = Theme.colors.textMuted,
		})
		refreshCompare()
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
		local color = Theme.rarityColor(s.rarity)
		local row = Instance.new("Frame")
		row.Size = UDim2.new(1, -4, 0, 40)
		row.BackgroundColor3 = Theme.colors.bgRaised
		row.BorderSizePixel = 0
		row.Parent = bagList
		Theme.corner(row, Theme.radii.sm)
		Theme.stroke(row, color, 1.5)

		local btn = Button.create(row, ("%s  ·  w%d"):format(s.name, s.weight), UDim2.new(1, -40, 1, 0), nil, "card", {
			textXAlignment = Enum.TextXAlignment.Left,
			textSize = 12,
		})
		btn.BackgroundTransparency = 1
		btn.TextColor3 = color

		local sell = Button.create(row, "$", UDim2.new(0, 32, 1, -6), UDim2.new(1, -34, 0, 3), "ghost", { textSize = 13 })
		Tooltip.attach(sell, ("Sell · %d"):format(s.sellWorth or 0))
		sell.MouseButton1Click:Connect(function()
			askSell(owned)
		end)

		local uid = owned.uid
		local slot = selectedSlot
		Tooltip.attach(btn, s.tooltip or s.name)
		btn.MouseButton1Click:Connect(function()
			selectedOwned = owned
			refreshCompare()
			SoundHooks.play("click")
			local result = EquipPart:InvokeServer(uid, slot)
			if not result.ok then
				setStatus(result.error or "Equip failed")
				return
			end
			SoundHooks.play("equip")
			snapshot = result.inventory
			setStatus("Equipped " .. s.name .. " · pedestal updated")
			GarageHud.render()
		end)
	end
	if not any then
		Theme.label(bagList, "No spare parts for this slot.", UDim2.new(1, -4, 0, 36), UDim2.new(0, 0, 0, 0), 12, {
			color = Theme.colors.textMuted,
		})
	end
	refreshCompare()
end

local function refreshSlots()
	clear(slotList)
	if not snapshot then
		return
	end
	for _, rowDef in SLOT_ROWS do
		local owned = equippedOwned(rowDef.field)
		local name = equippedName(rowDef.field)
		local row = Instance.new("Frame")
		row.Size = UDim2.new(1, -4, 0, 34)
		row.BackgroundColor3 = Theme.colors.bgRaised
		row.BorderSizePixel = 0
		row.Parent = slotList
		Theme.corner(row, Theme.radii.sm)
		local border = Theme.colors.stroke
		if owned then
			border = Theme.rarityColor(owned.summary.rarity)
		end
		if selectedSlot == rowDef.field then
			border = Theme.colors.cyan
		end
		Theme.stroke(row, border, if selectedSlot == rowDef.field then 1.5 else 1)

		local hasX = rowDef.field ~= "Chip" and name ~= "—"
		local btn = Button.create(
			row,
			("%s — %s"):format(rowDef.label, name),
			UDim2.new(1, if hasX then -36 else 0, 1, 0),
			nil,
			"card",
			{ textXAlignment = Enum.TextXAlignment.Left, textSize = 12 }
		)
		btn.BackgroundTransparency = 1
		local field = rowDef.field
		btn.MouseButton1Click:Connect(function()
			selectedSlot = field
			SoundHooks.play("click")
			GarageHud.render()
		end)
		if hasX then
			local x = Button.create(row, "×", UDim2.new(0, 30, 1, -4), UDim2.new(1, -32, 0, 2), "danger", { textSize = 14 })
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

function GarageHud.onWallet(cb: () -> ())
	onWalletRefresh = cb
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
		SoundHooks.play("open")
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
		SoundHooks.play("close")
		hideConfirm()
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
	root = Theme.panel(parentGui, "GaragePanel", UDim2.new(0, 530, 0, 460), restPos, Theme.colors.garage)
	root.Visible = false
	root.ZIndex = 30

	Theme.label(root, "GARAGE", UDim2.new(1, -100, 0, 24), UDim2.new(0, 16, 0, 12), 18, {
		font = Theme.fonts.display,
		color = Theme.colors.accent,
	})
	titleSub = Theme.label(root, "Primary · pedestal mirrors equip", UDim2.new(1, -100, 0, 18), UDim2.new(0, 16, 0, 38), 12, {
		color = Theme.colors.textDim,
	})
	statusLabel = Theme.label(root, "", UDim2.new(1, -180, 0, 18), UDim2.new(0, 16, 1, -28), 11, {
		color = Theme.colors.textMuted,
	})

	local sellAllHint = Button.create(root, "Sell tips", UDim2.new(0, 78, 0, 26), UDim2.new(1, -176, 1, -42), "ghost", {
		textSize = 11,
	})
	Tooltip.attach(sellAllHint, "Unequip first. $ sells one spare. Upgrade stub is browse-only.")
	sellAllHint.MouseButton1Click:Connect(function()
		setStatus("Sell: tap $ on a spare. Upgrade: coming with part tiers.")
		SoundHooks.play("click")
	end)

	local upgradeStub = Button.create(root, "Upgrade", UDim2.new(0, 78, 0, 26), UDim2.new(1, -90, 1, -42), "secondary", {
		textSize = 11,
	})
	Tooltip.attach(upgradeStub, "Part upgrade stub — tiers land with economy depth")
	upgradeStub.MouseButton1Click:Connect(function()
		if not selectedOwned then
			setStatus("Select a spare in the bag to preview upgrade.")
			SoundHooks.play("click")
			return
		end
		SoundHooks.play("upgrade")
		local s = selectedOwned.summary
		setStatus(("Upgrade stub · %s stays Lv%d — polish only"):format(s.name, s.level or 1))
	end)

	slotList = Instance.new("ScrollingFrame")
	slotList.Name = "Slots"
	slotList.Size = UDim2.new(0.48, -12, 0, 230)
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
	bagList.Size = UDim2.new(0.48, -12, 0, 230)
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

	comparePanel = Instance.new("Frame")
	comparePanel.Name = "Compare"
	comparePanel.Size = UDim2.new(1, -24, 0, 110)
	comparePanel.Position = UDim2.new(0, 12, 0, 304)
	comparePanel.BackgroundColor3 = Theme.colors.bgInset
	comparePanel.BackgroundTransparency = 0.1
	comparePanel.BorderSizePixel = 0
	comparePanel.Parent = root
	Theme.corner(comparePanel, Theme.radii.sm)
	Theme.stroke(comparePanel, Theme.colors.stroke, 1)

	local close = Button.create(root, "Close", UDim2.new(0, 72, 0, 28), UDim2.new(1, -86, 0, 12), "ghost")
	close.MouseButton1Click:Connect(function()
		GarageHud.setOpen(false)
	end)

	confirmRoot = Theme.panel(parentGui, "SellConfirm", UDim2.new(0, 300, 0, 150), UDim2.new(0.5, -150, 0.5, -75), Theme.colors.accent)
	confirmRoot.Visible = false
	confirmRoot.ZIndex = 90
	Theme.label(confirmRoot, "SELL PART", UDim2.new(1, -20, 0, 22), UDim2.new(0, 14, 0, 12), 16, {
		font = Theme.fonts.title,
		color = Theme.colors.accent,
	})
	local nameLab = Theme.label(confirmRoot, "", UDim2.new(1, -28, 0, 22), UDim2.new(0, 14, 0, 40), 15, {
		font = Theme.fonts.button,
	})
	nameLab.Name = "NameLab"
	local worthLab = Theme.label(confirmRoot, "", UDim2.new(1, -28, 0, 18), UDim2.new(0, 14, 0, 66), 13, {
		color = Theme.colors.textDim,
	})
	worthLab.Name = "WorthLab"
	local yes = Button.create(confirmRoot, "Sell", UDim2.new(0, 90, 0, 32), UDim2.new(0, 14, 1, -48), "primary")
	local no = Button.create(confirmRoot, "Keep", UDim2.new(0, 90, 0, 32), UDim2.new(0, 116, 1, -48), "ghost")
	yes.MouseButton1Click:Connect(function()
		local uid = confirmRoot:GetAttribute("SellUid")
		hideConfirm()
		if typeof(uid) ~= "string" then
			return
		end
		local result = SellPart:InvokeServer(uid)
		if not result or not result.ok then
			setStatus((result and result.error) or "Sell failed")
			return
		end
		SoundHooks.play("sell")
		snapshot = result.inventory
		setStatus(("Sold %s · +%d common"):format(result.partName or "part", result.commonGained or 0))
		GarageHud.render()
		if onWalletRefresh then
			onWalletRefresh()
		end
	end)
	no.MouseButton1Click:Connect(hideConfirm)

	InventoryUpdated.OnClientEvent:Connect(function(snap)
		snapshot = snap
		if open then
			GarageHud.render()
		end
	end)
end

return GarageHud

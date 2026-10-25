-- Branded join / lobby chrome: bottom action bar + Mechs / Settings panels.
-- Not a wall of locked mechs — Primary is ready; other bays show as locked slots.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))
local LobbyCamera = require(script.Parent:WaitForChild("LobbyCamera"))

local JoinHud = {}

local remotesFolder = ReplicatedStorage:WaitForChild("AssemblerRemotes")
local GetBootstrap = remotesFolder:WaitForChild("GetBootstrap")

local screen: ScreenGui
local bar: Frame
local walletLabel: TextLabel
local statusLabel: TextLabel
local cameraBtn: TextButton
local mechsPanel: Frame
local settingsPanel: Frame
local mechsList: Frame
local callbacks: {
	openCampaign: () -> (),
	openGarage: () -> (),
	isBusy: () -> boolean,
}?

local function refreshCameraButton()
	if not cameraBtn then
		return
	end
	if LobbyCamera.isLookEnabled() then
		cameraBtn.Text = "Cam · look"
		cameraBtn.BackgroundColor3 = Theme.colors.cyanDeep
	else
		cameraBtn.Text = "Cam · free"
		cameraBtn.BackgroundColor3 = Theme.colors.bgRaised
	end
end

local function hideSidePanels()
	mechsPanel.Visible = false
	settingsPanel.Visible = false
	ModalMouse.pop("mechs")
	ModalMouse.pop("settings")
end

local function renderMechs(boot)
	for _, child in mechsList:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	local inv = boot and boot.inventory
	local bays = (inv and inv.bays) or {
		{ id = "Primary", name = "Primary", unlocked = true },
		{ id = "Secondary", name = "Secondary", unlocked = false },
		{ id = "Tertiary", name = "Tertiary", unlocked = false },
	}
	local active = (inv and inv.activeBay) or "Primary"
	local loadout = boot and boot.loadout
	local y = 0
	for _, bay in bays do
		local row = Instance.new("Frame")
		row.Size = UDim2.new(1, -8, 0, 52)
		row.Position = UDim2.new(0, 4, 0, y)
		row.BackgroundColor3 = if bay.unlocked then Theme.colors.bgRaised else Theme.colors.locked
		row.BorderSizePixel = 0
		row.Parent = mechsList
		Theme.corner(row, Theme.radii.sm)
		if bay.id == active and bay.unlocked then
			Theme.stroke(row, Theme.colors.accent, 1.5)
		end

		local title = if bay.unlocked then bay.name else (bay.name .. " · locked")
		Theme.label(row, title, UDim2.new(1, -16, 0, 20), UDim2.new(0, 10, 0, 6), 14, {
			font = Theme.fonts.button,
			color = if bay.unlocked then Theme.colors.text else Theme.colors.textMuted,
		})
		local detail
		if bay.unlocked and bay.id == active and loadout then
			detail = ("Ready · %s"):format(loadout.torso or "starter")
		elseif bay.unlocked then
			detail = "Empty bay"
		else
			detail = "Unlock later (PvP lives)"
		end
		Theme.label(row, detail, UDim2.new(1, -16, 0, 18), UDim2.new(0, 10, 0, 28), 12, {
			color = Theme.colors.textDim,
		})
		y += 58
	end
end

function JoinHud.setStatus(text: string)
	if statusLabel then
		statusLabel.Text = text
	end
end

function JoinHud.setWallet(text: string)
	if walletLabel then
		walletLabel.Text = text
	end
end

function JoinHud.setVisible(on: boolean)
	if bar then
		bar.Visible = on
	end
	if not on then
		hideSidePanels()
	end
end

function JoinHud.closePanels()
	hideSidePanels()
end

function JoinHud.refresh()
	local ok, boot = pcall(function()
		return GetBootstrap:InvokeServer()
	end)
	if not ok or not boot then
		JoinHud.setWallet("Assembler")
		return
	end
	JoinHud.setWallet(("Common %d · XP %d · Cleared %d/%d"):format(
		boot.wallet.common,
		boot.progress.xp,
		boot.progress.highestCleared,
		boot.ladderCount
	))
	if mechsPanel.Visible then
		renderMechs(boot)
	end
	local lo = boot.loadout
	if not callbacks or not callbacks.isBusy() then
		JoinHud.setStatus(("Primary ready · %s — V look · Campaign / Garage"):format(lo.torso or "mech"))
	end
end

function JoinHud.mount(parent: ScreenGui, cbs: typeof(callbacks))
	screen = parent
	callbacks = cbs

	bar = Instance.new("Frame")
	bar.Name = "JoinBar"
	bar.Size = UDim2.new(0, 640, 0, 72)
	bar.Position = UDim2.new(0.5, -320, 1, -92)
	bar.BackgroundColor3 = Theme.colors.bgDeep
	bar.BackgroundTransparency = Theme.transparency.bar
	bar.BorderSizePixel = 0
	bar.Parent = screen
	Theme.corner(bar, Theme.radii.lg)
	Theme.stroke(bar, Theme.colors.strokeBright, 1)

	local brand = Theme.label(bar, "ASSEMBLER", UDim2.new(0, 120, 0, 22), UDim2.new(0, 16, 0, 8), 16, {
		font = Theme.fonts.title,
		color = Theme.colors.accent,
	})
	brand.Name = "Brand"

	walletLabel = Theme.label(bar, "", UDim2.new(0, 280, 0, 18), UDim2.new(0, 16, 0, 34), 12, {
		color = Theme.colors.textDim,
	})
	statusLabel = Theme.label(bar, "", UDim2.new(0, 300, 0, 16), UDim2.new(0, 16, 0, 52), 11, {
		color = Theme.colors.textMuted,
	})

	local btnW = 88
	local btnH = 36
	local gap = 8
	local actions = {
		{ id = "campaign", text = "Campaign", bg = Theme.colors.cyanDeep },
		{ id = "garage", text = "Garage", bg = Theme.colors.garage },
		{ id = "mechs", text = "Mechs", bg = Theme.colors.bgRaised },
		{ id = "settings", text = "Settings", bg = Theme.colors.bgRaised },
	}
	local totalW = #actions * btnW + (#actions - 1) * gap
	local startX = 640 - totalW - 16
	for i, a in actions do
		local x = startX + (i - 1) * (btnW + gap)
		local btn = Theme.button(bar, a.text, UDim2.new(0, btnW, 0, btnH), UDim2.new(0, x, 0, 18), {
			bg = a.bg,
			textSize = 13,
		})
		btn.Name = "Btn_" .. a.id
		btn.MouseButton1Click:Connect(function()
			if callbacks and callbacks.isBusy() then
				return
			end
			if a.id == "campaign" then
				hideSidePanels()
				callbacks.openCampaign()
			elseif a.id == "garage" then
				hideSidePanels()
				callbacks.openGarage()
			elseif a.id == "mechs" then
				local open = not mechsPanel.Visible
				settingsPanel.Visible = false
				ModalMouse.pop("settings")
				mechsPanel.Visible = open
				ModalMouse.set("mechs", open)
				if open then
					JoinHud.refresh()
					local ok, boot = pcall(function()
						return GetBootstrap:InvokeServer()
					end)
					if ok then
						renderMechs(boot)
					end
				end
			elseif a.id == "settings" then
				local open = not settingsPanel.Visible
				mechsPanel.Visible = false
				ModalMouse.pop("mechs")
				settingsPanel.Visible = open
				ModalMouse.set("settings", open)
			end
		end)
	end

	-- Mechs panel (compact slots, not a catalog wall)
	mechsPanel = Theme.panel(screen, "MechsPanel", UDim2.new(0, 300, 0, 220), UDim2.new(1, -316, 1, -330))
	mechsPanel.Visible = false
	Theme.label(mechsPanel, "Mech slots", UDim2.new(1, -20, 0, 22), UDim2.new(0, 12, 0, 10), 16, {
		font = Theme.fonts.title,
		color = Theme.colors.accent,
	})
	Theme.label(
		mechsPanel,
		"Starter is on Primary. Extra bays unlock later.",
		UDim2.new(1, -20, 0, 32),
		UDim2.new(0, 12, 0, 34),
		12,
		{ color = Theme.colors.textDim }
	)
	mechsList = Instance.new("Frame")
	mechsList.Size = UDim2.new(1, -16, 1, -84)
	mechsList.Position = UDim2.new(0, 8, 0, 72)
	mechsList.BackgroundTransparency = 1
	mechsList.Parent = mechsPanel
	local closeMechs = Theme.button(mechsPanel, "Close", UDim2.new(0, 64, 0, 26), UDim2.new(1, -76, 0, 8), {
		bg = Theme.colors.bgInset,
	})
	closeMechs.MouseButton1Click:Connect(function()
		mechsPanel.Visible = false
		ModalMouse.pop("mechs")
	end)

	-- Settings panel
	settingsPanel = Theme.panel(screen, "SettingsPanel", UDim2.new(0, 300, 0, 160), UDim2.new(1, -316, 1, -270))
	settingsPanel.Visible = false
	Theme.label(settingsPanel, "Settings", UDim2.new(1, -20, 0, 22), UDim2.new(0, 12, 0, 10), 16, {
		font = Theme.fonts.title,
		color = Theme.colors.accent,
	})
	Theme.label(
		settingsPanel,
		"Press V (or this button) for mouse look while walking. Cursor stays free for menus.",
		UDim2.new(1, -20, 0, 36),
		UDim2.new(0, 12, 0, 36),
		12,
		{ color = Theme.colors.textDim }
	)
	cameraBtn = Theme.button(settingsPanel, "Cam · free", UDim2.new(1, -24, 0, 34), UDim2.new(0, 12, 0, 82), {
		bg = Theme.colors.bgRaised,
	})
	cameraBtn.MouseButton1Click:Connect(function()
		LobbyCamera.toggleLook()
		refreshCameraButton()
	end)
	local closeSettings = Theme.button(settingsPanel, "Close", UDim2.new(0, 64, 0, 26), UDim2.new(1, -76, 0, 8), {
		bg = Theme.colors.bgInset,
	})
	closeSettings.MouseButton1Click:Connect(function()
		settingsPanel.Visible = false
		ModalMouse.pop("settings")
	end)

	LobbyCamera.onLookChanged(function()
		refreshCameraButton()
	end)
	refreshCameraButton()
	JoinHud.refresh()
end

return JoinHud

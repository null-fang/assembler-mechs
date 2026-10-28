-- Branded join / lobby chrome: bottom action bar + Mechs / Settings panels.
-- Not a wall of locked mechs — Primary is ready; other bays show as locked slots.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))
local LobbyCamera = require(script.Parent:WaitForChild("LobbyCamera"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))
local TweenUtil = require(script.Parent:WaitForChild("UI"):WaitForChild("TweenUtil"))
local Tooltip = require(script.Parent:WaitForChild("UI"):WaitForChild("Tooltip"))

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
local mechsRest: UDim2
local settingsRest: UDim2
local ThemedStarters = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Parts"):WaitForChild("ThemedStarters"))

local callbacks: {
	openCampaign: () -> (),
	openGarage: () -> (),
	openCrate: (() -> ())?,
	openPvP: (() -> ())?,
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
	if mechsPanel.Visible then
		mechsPanel.Visible = false
		mechsPanel.Position = mechsRest
	end
	if settingsPanel.Visible then
		settingsPanel.Visible = false
		settingsPanel.Position = settingsRest
	end
	ModalMouse.pop("mechs")
	ModalMouse.pop("settings")
end

local function openSide(panel: Frame, rest: UDim2, id: string)
	ModalMouse.push(id)
	panel.BackgroundTransparency = Theme.transparency.panel
	TweenUtil.openFrom(panel, UDim2.new(rest.X.Scale, rest.X.Offset + 24, rest.Y.Scale, rest.Y.Offset), rest, Theme.transparency.panel)
end

local ACCENT_COLORS = {
	scrap = Theme.colors.accentSoft,
	ember = Theme.colors.temperature,
	frost = Theme.colors.cyan,
	arc = Theme.colors.battery,
	toxin = Theme.colors.ok,
	void = Theme.colors.premiumCoin,
}

local function renderMechs(boot)
	for _, child in mechsList:GetChildren() do
		if child:IsA("GuiObject") and not child:IsA("UIListLayout") then
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
	for bi, bay in bays do
		local row = Instance.new("Frame")
		row.Size = UDim2.new(1, -4, 0, 48)
		row.BackgroundColor3 = if bay.unlocked then Theme.colors.bgRaised else Theme.colors.locked
		row.BorderSizePixel = 0
		row.LayoutOrder = bi
		row.Parent = mechsList
		Theme.corner(row, Theme.radii.sm)
		if bay.id == active and bay.unlocked then
			Theme.stroke(row, Theme.colors.accent, 1.5)
		else
			Theme.stroke(row, Theme.colors.stroke, 1)
		end

		local strip = Instance.new("Frame")
		strip.Size = UDim2.new(0, 3, 1, -8)
		strip.Position = UDim2.new(0, 4, 0, 4)
		strip.BackgroundColor3 = if bay.unlocked then Theme.colors.accent else Theme.colors.textMuted
		strip.BorderSizePixel = 0
		strip.Parent = row
		Theme.corner(strip, 2)

		local title = if bay.unlocked then bay.name else (bay.name .. " · locked")
		Theme.label(row, title, UDim2.new(1, -20, 0, 18), UDim2.new(0, 14, 0, 4), 13, {
			font = Theme.fonts.button,
			color = if bay.unlocked then Theme.colors.text else Theme.colors.textMuted,
		})
		local detail
		if bay.unlocked and bay.id == active and loadout then
			detail = ("Ready · %s"):format(loadout.torso or "starter")
		elseif bay.unlocked then
			detail = "Empty bay"
		else
			detail = "Unlock later"
		end
		Theme.label(row, detail, UDim2.new(1, -20, 0, 16), UDim2.new(0, 14, 0, 24), 11, {
			color = Theme.colors.textDim,
		})
	end

	-- Themed starters browse (apply locked until themes land).
	Theme.label(mechsList, "THEMED STARTERS", UDim2.new(1, -8, 0, 16), UDim2.new(0, 0, 0, 0), 11, {
		font = Theme.fonts.mono,
		color = Theme.colors.textMuted,
	}).LayoutOrder = 50
	local themes = (boot and boot.themes) or ThemedStarters.clientList()
	for i, theme in themes do
		local row = Instance.new("Frame")
		row.Size = UDim2.new(1, -4, 0, 52)
		row.BackgroundColor3 = Theme.colors.bgRaised
		row.BorderSizePixel = 0
		row.LayoutOrder = 50 + i
		row.Parent = mechsList
		Theme.corner(row, Theme.radii.sm)
		local accent = ACCENT_COLORS[theme.accent] or Theme.colors.strokeBright
		Theme.stroke(row, accent, if theme.status == "live" then 1.5 else 1)
		Theme.label(row, theme.name, UDim2.new(1, -70, 0, 16), UDim2.new(0, 10, 0, 4), 12, {
			font = Theme.fonts.button,
			color = Theme.colors.text,
		})
		Theme.label(row, theme.tagline, UDim2.new(1, -70, 0, 28), UDim2.new(0, 10, 0, 22), 10, {
			color = Theme.colors.textDim,
		})
		local badge = Theme.label(
			row,
			if theme.status == "live" then "LIVE" elseif theme.status == "preview" then "PREVIEW" else "SOON",
			UDim2.new(0, 56, 0, 16),
			UDim2.new(1, -62, 0, 6),
			10,
			{
				font = Theme.fonts.mono,
				color = accent,
				align = Enum.TextXAlignment.Right,
			}
		)
		Tooltip.attach(badge, theme.unlockNote or "")
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
	JoinHud.setWallet(("Common %d · Rare %d · Cleared %d/%d"):format(
		boot.wallet.common,
		boot.wallet.rare or 0,
		boot.progress.highestCleared,
		boot.ladderCount
	))
	if mechsPanel.Visible then
		renderMechs(boot)
	end
	local lo = boot.loadout
	if not callbacks or not callbacks.isBusy() then
		JoinHud.setStatus(("Primary ready · %s — Campaign / Garage / Crate"):format(lo.torso or "mech"))
	end
end

function JoinHud.mount(parent: ScreenGui, cbs: typeof(callbacks))
	screen = parent
	callbacks = cbs
	Tooltip.bind(screen)

	bar = Instance.new("Frame")
	bar.Name = "JoinBar"
	bar.Size = UDim2.new(0, 780, 0, 78)
	bar.Position = UDim2.new(0.5, -390, 1, -98)
	bar.BackgroundColor3 = Theme.colors.bgDeep
	bar.BackgroundTransparency = Theme.transparency.bar
	bar.BorderSizePixel = 0
	bar.Parent = screen
	Theme.corner(bar, Theme.radii.lg)
	Theme.stroke(bar, Theme.colors.strokeBright, 1)
	Theme.accentStrip(bar, Theme.colors.accent)

	local brand = Theme.label(bar, "ASSEMBLER", UDim2.new(0, 160, 0, 24), UDim2.new(0, 16, 0, 10), 18, {
		font = Theme.fonts.display,
		color = Theme.colors.accent,
	})
	brand.Name = "Brand"

	walletLabel = Theme.label(bar, "", UDim2.new(0, 300, 0, 18), UDim2.new(0, 16, 0, 36), 12, {
		font = Theme.fonts.mono,
		color = Theme.colors.accentSoft,
	})
	statusLabel = Theme.label(bar, "", UDim2.new(0, 320, 0, 16), UDim2.new(0, 16, 0, 54), 11, {
		color = Theme.colors.textMuted,
	})

	local actions = {
		{ id = "campaign", text = "Campaign", variant = "cyan" :: any, tip = "Fight ladder" },
		{ id = "garage", text = "Garage", variant = "garage" :: any, tip = "Swap parts" },
		{ id = "crate", text = "Crate", variant = "primary" :: any, tip = "Pick-3 pending crate" },
		{ id = "pvp", text = "PvP", variant = "danger" :: any, tip = "Queue stub / ghost spar" },
		{ id = "mechs", text = "Mechs", variant = "secondary" :: any, tip = "Bay + themed starters" },
		{ id = "settings", text = "Settings", variant = "secondary" :: any, tip = "Camera look" },
	}
	local btnW, btnH, gap = 84, 38, 6
	local totalW = #actions * btnW + (#actions - 1) * gap
	local startX = 780 - totalW - 18
	for i, a in actions do
		local x = startX + (i - 1) * (btnW + gap)
		local btn = Button.create(bar, a.text, UDim2.new(0, btnW, 0, btnH), UDim2.new(0, x, 0, 20), a.variant, {
			textSize = 12,
		})
		btn.Name = "Btn_" .. a.id
		Tooltip.attach(btn, a.tip)
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
			elseif a.id == "crate" then
				hideSidePanels()
				if callbacks.openCrate then
					callbacks.openCrate()
				end
			elseif a.id == "pvp" then
				hideSidePanels()
				if callbacks.openPvP then
					callbacks.openPvP()
				end
			elseif a.id == "mechs" then
				local open = not mechsPanel.Visible
				if settingsPanel.Visible then
					settingsPanel.Visible = false
					settingsPanel.Position = settingsRest
					ModalMouse.pop("settings")
				end
				if open then
					openSide(mechsPanel, mechsRest, "mechs")
					JoinHud.refresh()
					local ok, boot = pcall(function()
						return GetBootstrap:InvokeServer()
					end)
					if ok then
						renderMechs(boot)
					end
				else
					mechsPanel.Visible = false
					ModalMouse.pop("mechs")
				end
			elseif a.id == "settings" then
				local open = not settingsPanel.Visible
				if mechsPanel.Visible then
					mechsPanel.Visible = false
					mechsPanel.Position = mechsRest
					ModalMouse.pop("mechs")
				end
				if open then
					openSide(settingsPanel, settingsRest, "settings")
				else
					settingsPanel.Visible = false
					ModalMouse.pop("settings")
				end
			end
		end)
	end

	mechsRest = UDim2.new(1, -336, 1, -520)
	mechsPanel = Theme.panel(screen, "MechsPanel", UDim2.new(0, 320, 0, 420), mechsRest, Theme.colors.accent)
	mechsPanel.Visible = false
	Theme.label(mechsPanel, "MECH BAY", UDim2.new(1, -90, 0, 22), UDim2.new(0, 14, 0, 12), 16, {
		font = Theme.fonts.title,
		color = Theme.colors.accent,
	})
	Theme.label(
		mechsPanel,
		"Slots + themed starters. Preview until art themes land.",
		UDim2.new(1, -24, 0, 28),
		UDim2.new(0, 14, 0, 36),
		12,
		{ color = Theme.colors.textDim }
	)
	mechsList = Instance.new("ScrollingFrame")
	mechsList.Size = UDim2.new(1, -20, 1, -90)
	mechsList.Position = UDim2.new(0, 10, 0, 72)
	mechsList.BackgroundTransparency = 1
	mechsList.ScrollBarThickness = 3
	mechsList.ScrollBarImageColor3 = Theme.colors.cyanDeep
	mechsList.BorderSizePixel = 0
	mechsList.AutomaticCanvasSize = Enum.AutomaticSize.Y
	mechsList.CanvasSize = UDim2.new(0, 0, 0, 0)
	mechsList.Parent = mechsPanel
	local mechLayout = Instance.new("UIListLayout")
	mechLayout.Padding = UDim.new(0, 6)
	mechLayout.SortOrder = Enum.SortOrder.LayoutOrder
	mechLayout.Parent = mechsList
	local closeMechs = Button.create(mechsPanel, "Close", UDim2.new(0, 64, 0, 26), UDim2.new(1, -78, 0, 10), "ghost")
	closeMechs.MouseButton1Click:Connect(function()
		mechsPanel.Visible = false
		mechsPanel.Position = mechsRest
		ModalMouse.pop("mechs")
	end)

	settingsRest = UDim2.new(1, -316, 1, -280)
	settingsPanel = Theme.panel(screen, "SettingsPanel", UDim2.new(0, 300, 0, 170), settingsRest, Theme.colors.cyan)
	settingsPanel.Visible = false
	Theme.label(settingsPanel, "SETTINGS", UDim2.new(1, -90, 0, 22), UDim2.new(0, 14, 0, 12), 16, {
		font = Theme.fonts.title,
		color = Theme.colors.cyan,
	})
	Theme.label(
		settingsPanel,
		"V (or Cam) for mouse look while walking. Menus keep the cursor free.",
		UDim2.new(1, -24, 0, 40),
		UDim2.new(0, 14, 0, 38),
		12,
		{ color = Theme.colors.textDim }
	)
	cameraBtn = Button.create(settingsPanel, "Cam · free", UDim2.new(1, -28, 0, 34), UDim2.new(0, 14, 0, 88), "secondary")
	cameraBtn.MouseButton1Click:Connect(function()
		LobbyCamera.toggleLook()
		refreshCameraButton()
	end)
	local closeSettings = Button.create(settingsPanel, "Close", UDim2.new(0, 64, 0, 26), UDim2.new(1, -78, 0, 10), "ghost")
	closeSettings.MouseButton1Click:Connect(function()
		settingsPanel.Visible = false
		settingsPanel.Position = settingsRest
		ModalMouse.pop("settings")
	end)

	LobbyCamera.onLookChanged(function()
		refreshCameraButton()
	end)
	refreshCameraButton()
	JoinHud.refresh()
end

return JoinHud

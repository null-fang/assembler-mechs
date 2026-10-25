-- Unlock mouse whenever a modal menu is open; restore lobby camera lock on close.
-- Uses ScreenGui.Modal (drives GuiService.MenuIsOpen) + UserInputService.MouseBehavior.

local GuiService = game:GetService("GuiService")
local UserInputService = game:GetService("UserInputService")

local ModalMouse = {}

local screenGui: ScreenGui? = nil
local openIds: { [string]: boolean } = {}
local openCount = 0
local combatClickMode = false
local onChanged: ((menuOpen: boolean, combat: boolean) -> ())? = nil

local function anyOpen(): boolean
	return openCount > 0
end

local function apply()
	local menuOpen = anyOpen()
	if screenGui then
		-- Modal ScreenGui frees/shows cursor and sets GuiService.MenuIsOpen.
		screenGui.Modal = menuOpen
	end

	if menuOpen or combatClickMode then
		UserInputService.MouseBehavior = Enum.MouseBehavior.Default
		UserInputService.MouseIconEnabled = true
	end
	-- LobbyCamera listens via onChanged and re-applies LockCenter when appropriate.

	if onChanged then
		onChanged(menuOpen, combatClickMode)
	end

	-- Soft assert for Studio debugging
	if menuOpen and not GuiService.MenuIsOpen then
		-- Modal may lag one frame; force mouse state anyway.
		UserInputService.MouseBehavior = Enum.MouseBehavior.Default
		UserInputService.MouseIconEnabled = true
	end
end

function ModalMouse.bind(gui: ScreenGui)
	screenGui = gui
	apply()
end

function ModalMouse.onStateChanged(cb: (menuOpen: boolean, combat: boolean) -> ())
	onChanged = cb
end

function ModalMouse.push(id: string)
	if openIds[id] then
		return
	end
	openIds[id] = true
	openCount += 1
	apply()
end

function ModalMouse.pop(id: string)
	if not openIds[id] then
		return
	end
	openIds[id] = nil
	openCount -= 1
	if openCount < 0 then
		openCount = 0
	end
	apply()
end

function ModalMouse.set(id: string, isOpen: boolean)
	if isOpen then
		ModalMouse.push(id)
	else
		ModalMouse.pop(id)
	end
end

function ModalMouse.isMenuOpen(): boolean
	return anyOpen()
end

-- Combat HUD: mouse stays free for clicking moves (no Modal / no lock).
function ModalMouse.setCombatClickMode(enabled: boolean)
	combatClickMode = enabled
	apply()
end

function ModalMouse.isCombatClickMode(): boolean
	return combatClickMode
end

function ModalMouse.refresh()
	apply()
end

return ModalMouse

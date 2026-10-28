-- Thin PvP queue UI stub. Shares combat resolver via ghost spar — no full matchmaking.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local ModalMouse = require(script.Parent:WaitForChild("ModalMouse"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))
local TweenUtil = require(script.Parent:WaitForChild("UI"):WaitForChild("TweenUtil"))
local Motions = require(script.Parent:WaitForChild("UI"):WaitForChild("Motions"))
local SoundHooks = require(script.Parent:WaitForChild("UI"):WaitForChild("SoundHooks"))
local Tooltip = require(script.Parent:WaitForChild("UI"):WaitForChild("Tooltip"))

local PvpHud = {}

local remotesFolder = ReplicatedStorage:WaitForChild("AssemblerRemotes")
local QueuePvP = remotesFolder:WaitForChild("QueuePvP")
local LeaveQueue = remotesFolder:WaitForChild("LeaveQueue")
local GetQueueStatus = remotesFolder:WaitForChild("GetQueueStatus")
local StartGhostSpar = remotesFolder:WaitForChild("StartGhostSpar")
local QueueUpdated = remotesFolder:WaitForChild("QueueUpdated")
local OpenPvP = remotesFolder:WaitForChild("OpenPvP")

local root: Frame
local statusLabel: TextLabel
local restPos = UDim2.new(0, 24, 1, -420)
local open = false
local onSpar: ((any) -> ())?
local isBusy: (() -> boolean)?

local function setStatus(text: string)
	if statusLabel then
		statusLabel.Text = text
	end
end

local function applyStatus(status)
	if not status then
		setStatus("Queue idle.")
		return
	end
	if status.inQueue then
		setStatus(("In queue · #%d of %d — %s"):format(status.position or 1, status.queueSize or 1, status.waitingFor or "waiting"))
	else
		setStatus(("Idle · %d waiting"):format(status.queueSize or 0))
	end
end

function PvpHud.isOpen(): boolean
	return open
end

function PvpHud.setOpen(isOpen: boolean)
	if isOpen == open and isOpen then
		local st = GetQueueStatus:InvokeServer()
		applyStatus(st)
		return
	end
	open = isOpen
	ModalMouse.set("pvp", isOpen)
	if isOpen then
		SoundHooks.play("open")
		root.BackgroundTransparency = Theme.transparency.panel
		TweenUtil.openFrom(
			root,
			UDim2.new(0, restPos.X.Offset - 20, 1, restPos.Y.Offset),
			restPos,
			Theme.transparency.panel
		)
		Motions.popIn(root, 0.94)
		applyStatus(GetQueueStatus:InvokeServer())
	else
		SoundHooks.play("close")
		TweenUtil.closeTo(root, UDim2.new(0, restPos.X.Offset - 16, 1, restPos.Y.Offset), restPos)
	end
end

function PvpHud.mount(parent: ScreenGui, opts: { onSpar: ((any) -> ())?, isBusy: (() -> boolean)? }?)
	onSpar = opts and opts.onSpar
	isBusy = opts and opts.isBusy

	root = Theme.panel(parent, "PvpPanel", UDim2.new(0, 320, 0, 220), restPos, Theme.colors.danger)
	root.Visible = false
	root.ZIndex = 32

	Theme.label(root, "PvP QUEUE", UDim2.new(1, -90, 0, 22), UDim2.new(0, 14, 0, 12), 16, {
		font = Theme.fonts.display,
		color = Theme.colors.danger,
	})
	Theme.label(
		root,
		"Stub only — no full matchmaking. Ghost spar uses the shared combat resolver.",
		UDim2.new(1, -28, 0, 40),
		UDim2.new(0, 14, 0, 40),
		12,
		{ color = Theme.colors.textDim }
	)
	statusLabel = Theme.label(root, "Idle", UDim2.new(1, -28, 0, 36), UDim2.new(0, 14, 0, 88), 12, {
		font = Theme.fonts.mono,
		color = Theme.colors.accentSoft,
	})

	local join = Button.create(root, "Join queue", UDim2.new(0, 110, 0, 32), UDim2.new(0, 14, 1, -52), "primary")
	Tooltip.attach(join, "Enter thin queue")
	join.MouseButton1Click:Connect(function()
		if isBusy and isBusy() then
			return
		end
		local result = QueuePvP:InvokeServer()
		SoundHooks.play("queue")
		applyStatus(result and result.status)
		if result and result.note then
			setStatus(result.note)
		end
	end)

	local leave = Button.create(root, "Leave", UDim2.new(0, 72, 0, 32), UDim2.new(0, 132, 1, -52), "ghost")
	leave.MouseButton1Click:Connect(function()
		local result = LeaveQueue:InvokeServer()
		SoundHooks.play("dequeue")
		applyStatus(result and result.status)
	end)

	local spar = Button.create(root, "Ghost spar", UDim2.new(0, 100, 0, 32), UDim2.new(1, -114, 1, -52), "cyan")
	Tooltip.attach(spar, "Practice via shared Resolver (PvP mode)")
	spar.MouseButton1Click:Connect(function()
		if isBusy and isBusy() then
			return
		end
		local result = StartGhostSpar:InvokeServer()
		if not result or not result.ok then
			setStatus((result and result.error) or "Spar failed")
			return
		end
		SoundHooks.play("turn")
		PvpHud.setOpen(false)
		if onSpar then
			onSpar(result)
		end
	end)

	local close = Button.create(root, "×", UDim2.new(0, 32, 0, 28), UDim2.new(1, -42, 0, 10), "ghost")
	close.MouseButton1Click:Connect(function()
		PvpHud.setOpen(false)
	end)

	QueueUpdated.OnClientEvent:Connect(function(status)
		applyStatus(status)
	end)
	OpenPvP.OnClientEvent:Connect(function()
		if isBusy and isBusy() then
			return
		end
		PvpHud.setOpen(true)
	end)
end

return PvpHud

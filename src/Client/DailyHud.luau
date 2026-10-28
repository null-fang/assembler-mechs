-- Soft daily / login claim toast. Brief Roblox-pattern payout stub.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))
local Motions = require(script.Parent:WaitForChild("UI"):WaitForChild("Motions"))
local SoundHooks = require(script.Parent:WaitForChild("UI"):WaitForChild("SoundHooks"))
local Tooltip = require(script.Parent:WaitForChild("UI"):WaitForChild("Tooltip"))

local DailyHud = {}

local remotesFolder = ReplicatedStorage:WaitForChild("AssemblerRemotes")
local ClaimDaily = remotesFolder:WaitForChild("ClaimDaily")
local GetDaily = remotesFolder:WaitForChild("GetDaily")
local DailyClaimed = remotesFolder:WaitForChild("DailyClaimed")

local chip: TextButton?
local toast: Frame?
local toastLabel: TextLabel?
local onRefresh: (() -> ())?

local function showToast(text: string)
	if not toast or not toastLabel then
		return
	end
	toastLabel.Text = text
	toast.Visible = true
	Motions.popIn(toast, 0.94)
	task.delay(3.2, function()
		if toast then
			toast.Visible = false
		end
	end)
end

local function applyStatus(status)
	if not chip then
		return
	end
	if not status then
		chip.Text = "Daily"
		return
	end
	if status.claimedToday then
		chip.Text = ("Day %d ✓"):format(status.streak or 1)
		chip.BackgroundColor3 = Theme.colors.bgInset
	else
		local p = status.preview
		local amt = if p then p.common else 80
		chip.Text = ("+%d"):format(amt)
		chip.BackgroundColor3 = Theme.colors.bgRaised
	end
end

function DailyHud.refresh()
	local ok, status = pcall(function()
		return GetDaily:InvokeServer()
	end)
	if ok then
		applyStatus(status)
	end
end

function DailyHud.mount(parent: ScreenGui, opts: { onRefresh: (() -> ())? }?)
	onRefresh = opts and opts.onRefresh

	chip = Button.create(parent, "Daily", UDim2.new(0, 72, 0, 28), UDim2.new(1, -96, 0, 18), "primary", {
		textSize = 12,
	})
	chip.Name = "DailyChip"
	chip.ZIndex = 45
	Tooltip.attach(chip, "Soft daily — common + maybe a crate")

	chip.MouseButton1Click:Connect(function()
		local result = ClaimDaily:InvokeServer()
		if not result or not result.ok then
			showToast((result and result.error) or "Already claimed")
			applyStatus(result and result.status)
			SoundHooks.play("click")
			return
		end
		SoundHooks.play("daily")
		local r = result.reward
		local bits = { ("+%d common"):format(r.common or 0), ("streak %d"):format(r.streak or 1) }
		if r.crate then
			table.insert(bits, "crate ready")
		end
		showToast(table.concat(bits, " · "))
		applyStatus(result.status)
		if onRefresh then
			onRefresh()
		end
	end)

	toast = Instance.new("Frame")
	toast.Name = "DailyToast"
	toast.Size = UDim2.new(0, 280, 0, 44)
	toast.Position = UDim2.new(0.5, -140, 0, 66)
	toast.BackgroundColor3 = Theme.colors.bgPanel
	toast.BackgroundTransparency = 0.08
	toast.BorderSizePixel = 0
	toast.Visible = false
	toast.ZIndex = 55
	toast.Parent = parent
	Theme.corner(toast, Theme.radii.md)
	Theme.stroke(toast, Theme.colors.accent, 1.5)
	toastLabel = Theme.label(toast, "", UDim2.new(1, -16, 1, -8), UDim2.new(0, 8, 0, 4), 13, {
		font = Theme.fonts.button,
		color = Theme.colors.accent,
		align = Enum.TextXAlignment.Center,
	})
	toastLabel.ZIndex = 56

	DailyClaimed.OnClientEvent:Connect(function(payload)
		if payload then
			showToast(payload.label or "Daily claimed")
		end
		DailyHud.refresh()
	end)

	DailyHud.refresh()
end

return DailyHud

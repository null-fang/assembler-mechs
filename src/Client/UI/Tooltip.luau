-- Short human tooltips — one line.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))

local Tooltip = {}

local host: Frame? = nil
local label: TextLabel? = nil
local hideToken = 0
local layer: ScreenGui? = nil

function Tooltip.bind(screenGui: ScreenGui)
	layer = screenGui
	if host and host.Parent ~= screenGui then
		host.Parent = screenGui
	end
end

local function ensure()
	if host and host.Parent then
		return
	end
	assert(layer, "Tooltip.bind(screen) first")
	host = Instance.new("Frame")
	host.Name = "Tooltip"
	host.Size = UDim2.new(0, 200, 0, 30)
	host.BackgroundColor3 = Theme.colors.bgDeep
	host.BackgroundTransparency = 0.04
	host.BorderSizePixel = 0
	host.Visible = false
	host.ZIndex = 200
	host.Parent = layer
	Theme.corner(host, Theme.radii.sm)
	Theme.stroke(host, Theme.colors.strokeFocus, 1)

	label = Instance.new("TextLabel")
	label.Size = UDim2.new(1, -14, 1, 0)
	label.Position = UDim2.new(0, 7, 0, 0)
	label.BackgroundTransparency = 1
	label.Font = Theme.fonts.body
	label.TextSize = 12
	label.TextColor3 = Theme.colors.text
	label.TextXAlignment = Enum.TextXAlignment.Left
	label.TextYAlignment = Enum.TextYAlignment.Center
	label.ZIndex = 201
	label.Parent = host
end

function Tooltip.show(text: string, anchor: GuiObject?)
	if not text or text == "" then
		Tooltip.hide()
		return
	end
	ensure()
	assert(host and label)
	hideToken += 1
	local clipped = if #text > 72 then string.sub(text, 1, 69) .. "…" else text
	label.Text = clipped
	host.Size = UDim2.new(0, math.clamp(#clipped * 7 + 20, 110, 280), 0, 30)
	if anchor then
		local pos = anchor.AbsolutePosition
		local size = anchor.AbsoluteSize
		host.Position = UDim2.new(0, pos.X, 0, pos.Y + size.Y + 6)
	end
	host.Visible = true
end

function Tooltip.hide()
	hideToken += 1
	local token = hideToken
	task.delay(0.05, function()
		if token == hideToken and host then
			host.Visible = false
		end
	end)
end

function Tooltip.attach(target: GuiObject, textOrFn: string | () -> string)
	target.MouseEnter:Connect(function()
		local text = if typeof(textOrFn) == "function" then (textOrFn :: any)() else textOrFn
		Tooltip.show(text, target)
	end)
	target.MouseLeave:Connect(function()
		Tooltip.hide()
	end)
end

return Tooltip

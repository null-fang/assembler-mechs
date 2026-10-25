-- Themed buttons with hover / press (not raw gray AutoButtonColor).

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local TweenUtil = require(script.Parent:WaitForChild("TweenUtil"))

local Button = {}

export type Variant = "primary" | "secondary" | "ghost" | "danger" | "card" | "cyan" | "garage"

local function palette(variant: Variant)
	local c = Theme.colors
	if variant == "primary" then
		return { idle = c.accent, hover = c.accent:Lerp(Color3.new(1, 1, 1), 0.16), press = c.accentSoft, text = c.textOnAccent }
	elseif variant == "cyan" then
		return { idle = c.cyanDeep, hover = c.cyanDeep:Lerp(c.cyan, 0.35), press = c.cyanDeep:Lerp(Color3.new(0, 0, 0), 0.2), text = c.text }
	elseif variant == "garage" then
		return { idle = c.garage, hover = c.garage:Lerp(Color3.new(1, 1, 1), 0.14), press = c.garage:Lerp(Color3.new(0, 0, 0), 0.2), text = c.text }
	elseif variant == "danger" then
		return { idle = c.danger, hover = c.danger:Lerp(Color3.new(1, 1, 1), 0.14), press = c.danger:Lerp(Color3.new(0, 0, 0), 0.2), text = c.text }
	elseif variant == "ghost" then
		return { idle = c.bgInset, hover = c.bgHover, press = c.bgPress, text = c.textDim }
	elseif variant == "card" then
		return { idle = c.bgRaised, hover = c.bgHover, press = c.bgPress, text = c.text }
	end
	return { idle = c.bgRaised, hover = c.bgHover, press = c.bgPress, text = c.text }
end

function Button.create(
	parent: Instance,
	text: string,
	size: UDim2,
	pos: UDim2?,
	variant: Variant?,
	opts: { textXAlignment: Enum.TextXAlignment?, textSize: number?, zIndex: number? }?
): TextButton
	local v: Variant = variant or "secondary"
	local colors = palette(v)
	local c = Theme.colors

	local b = Instance.new("TextButton")
	b.Name = "Btn"
	b.Size = size
	b.Position = pos or UDim2.new(0, 0, 0, 0)
	b.BackgroundColor3 = colors.idle
	b.BorderSizePixel = 0
	b.AutoButtonColor = false
	b.Font = Theme.fonts.button
	b.TextSize = (opts and opts.textSize) or 13
	b.TextColor3 = colors.text
	b.Text = text
	b.TextXAlignment = (opts and opts.textXAlignment) or Enum.TextXAlignment.Center
	b.ZIndex = (opts and opts.zIndex) or 1
	b.Parent = parent
	Theme.corner(b, Theme.radii.sm)

	local stroke
	if v == "card" or v == "secondary" or v == "ghost" then
		stroke = Theme.stroke(b, c.stroke, 1)
	end

	if opts and opts.textXAlignment == Enum.TextXAlignment.Left then
		local pad = Instance.new("UIPadding")
		pad.PaddingLeft = UDim.new(0, 10)
		pad.PaddingRight = UDim.new(0, 8)
		pad.Parent = b
	end

	local hovering = false
	b.MouseEnter:Connect(function()
		hovering = true
		TweenUtil.play(b, Theme.tween.hover, { BackgroundColor3 = colors.hover })
		if stroke then
			TweenUtil.play(stroke, Theme.tween.hover, { Color = c.strokeFocus })
		end
	end)
	b.MouseLeave:Connect(function()
		hovering = false
		TweenUtil.play(b, Theme.tween.hover, { BackgroundColor3 = colors.idle })
		if stroke then
			TweenUtil.play(stroke, Theme.tween.hover, { Color = c.stroke })
		end
	end)
	b.MouseButton1Down:Connect(function()
		TweenUtil.play(b, Theme.tween.press, { BackgroundColor3 = colors.press })
	end)
	b.MouseButton1Up:Connect(function()
		TweenUtil.play(b, Theme.tween.press, {
			BackgroundColor3 = if hovering then colors.hover else colors.idle,
		})
	end)

	return b
end

function Button.setSelected(btn: TextButton, selected: boolean)
	local c = Theme.colors
	local stroke = btn:FindFirstChildOfClass("UIStroke")
	if selected then
		btn.BackgroundColor3 = c.cyanDeep
		if stroke then
			stroke.Color = c.cyan
			stroke.Thickness = 1.5
		end
	else
		btn.BackgroundColor3 = c.bgRaised
		if stroke then
			stroke.Color = c.stroke
			stroke.Thickness = 1
		end
	end
end

return Button

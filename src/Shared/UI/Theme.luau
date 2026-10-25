-- Assembler UI theme — shared by Join HUD, Campaign, Garage, Combat.
-- RSC-12 (UI redesign) should extend this module rather than hardcoding colors.

local Theme = {}

-- Steel bay + amber/cyan terminal accents (matches lobby props, not gray slop).
Theme.colors = {
	bgDeep = Color3.fromRGB(8, 12, 18),
	bgPanel = Color3.fromRGB(16, 22, 32),
	bgRaised = Color3.fromRGB(24, 34, 48),
	bgInset = Color3.fromRGB(12, 18, 26),
	stroke = Color3.fromRGB(48, 64, 82),
	strokeBright = Color3.fromRGB(72, 98, 128),
	text = Color3.fromRGB(232, 238, 246),
	textDim = Color3.fromRGB(148, 162, 180),
	textMuted = Color3.fromRGB(100, 114, 132),
	accent = Color3.fromRGB(232, 168, 56), -- amber
	accentSoft = Color3.fromRGB(196, 140, 48),
	cyan = Color3.fromRGB(56, 196, 204), -- campaign terminal
	cyanDeep = Color3.fromRGB(28, 110, 118),
	garage = Color3.fromRGB(72, 118, 168),
	danger = Color3.fromRGB(196, 72, 64),
	ok = Color3.fromRGB(88, 176, 112),
	locked = Color3.fromRGB(56, 62, 72),
}

Theme.fonts = {
	title = Enum.Font.GothamBold,
	body = Enum.Font.Gotham,
	button = Enum.Font.GothamMedium,
}

Theme.radii = {
	sm = 4,
	md = 8,
	lg = 12,
}

Theme.transparency = {
	panel = 0.08,
	bar = 0.05,
	overlay = 0.35,
}

function Theme.corner(parent: Instance, radius: number?)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, radius or Theme.radii.md)
	c.Parent = parent
	return c
end

function Theme.stroke(parent: Instance, color: Color3?, thickness: number?)
	local s = Instance.new("UIStroke")
	s.Color = color or Theme.colors.stroke
	s.Thickness = thickness or 1
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Parent = parent
	return s
end

function Theme.padding(parent: Instance, px: number)
	local p = Instance.new("UIPadding")
	p.PaddingTop = UDim.new(0, px)
	p.PaddingBottom = UDim.new(0, px)
	p.PaddingLeft = UDim.new(0, px)
	p.PaddingRight = UDim.new(0, px)
	p.Parent = parent
	return p
end

function Theme.label(
	parent: Instance,
	text: string,
	size: UDim2,
	pos: UDim2,
	textSize: number?,
	opts: { color: Color3?, font: Enum.Font?, align: Enum.TextXAlignment? }?
)
	local l = Instance.new("TextLabel")
	l.Size = size
	l.Position = pos
	l.BackgroundTransparency = 1
	l.Text = text
	l.TextColor3 = (opts and opts.color) or Theme.colors.text
	l.Font = (opts and opts.font) or Theme.fonts.body
	l.TextSize = textSize or 14
	l.TextXAlignment = (opts and opts.align) or Enum.TextXAlignment.Left
	l.TextYAlignment = Enum.TextYAlignment.Top
	l.TextWrapped = true
	l.Parent = parent
	return l
end

function Theme.button(
	parent: Instance,
	text: string,
	size: UDim2,
	pos: UDim2,
	opts: { bg: Color3?, textColor: Color3?, textSize: number? }?
)
	local b = Instance.new("TextButton")
	b.Size = size
	b.Position = pos
	b.BackgroundColor3 = (opts and opts.bg) or Theme.colors.bgRaised
	b.BorderSizePixel = 0
	b.Text = text
	b.TextColor3 = (opts and opts.textColor) or Theme.colors.text
	b.Font = Theme.fonts.button
	b.TextSize = (opts and opts.textSize) or 14
	b.AutoButtonColor = true
	b.Parent = parent
	Theme.corner(b, Theme.radii.sm)
	return b
end

function Theme.panel(parent: Instance, name: string, size: UDim2, pos: UDim2)
	local f = Instance.new("Frame")
	f.Name = name
	f.Size = size
	f.Position = pos
	f.BackgroundColor3 = Theme.colors.bgPanel
	f.BackgroundTransparency = Theme.transparency.panel
	f.BorderSizePixel = 0
	f.Parent = parent
	Theme.corner(f, Theme.radii.md)
	Theme.stroke(f, Theme.colors.stroke, 1)
	return f
end

return Theme

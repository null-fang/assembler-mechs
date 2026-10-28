-- Integrity / Temp / Battery bars with track + fill + mono values + danger glow.

local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local TweenUtil = require(script.Parent:WaitForChild("TweenUtil"))

local ResourceBar = {}

export type Kind = "integrity" | "temperature" | "battery"

export type BarHandles = {
	root: Frame,
	set: (current: number, max: number) -> (),
}

local KIND = {
	integrity = { tag = "INT", fill = "integrity", track = "integrityTrack" },
	temperature = { tag = "TEMP", fill = "temperature", track = "temperatureTrack" },
	battery = { tag = "BAT", fill = "battery", track = "batteryTrack" },
}

function ResourceBar.create(parent: Instance, kind: Kind, size: UDim2, position: UDim2): BarHandles
	local meta = KIND[kind]
	local c = Theme.colors

	local root = Instance.new("Frame")
	root.Name = "Bar_" .. kind
	root.Size = size
	root.Position = position
	root.BackgroundTransparency = 1
	root.Parent = parent

	local tag = Instance.new("TextLabel")
	tag.Size = UDim2.new(0, 40, 1, 0)
	tag.BackgroundTransparency = 1
	tag.Font = Theme.fonts.mono
	tag.TextSize = 10
	tag.TextColor3 = c.textDim
	tag.TextXAlignment = Enum.TextXAlignment.Left
	tag.TextYAlignment = Enum.TextYAlignment.Center
	tag.Text = meta.tag
	tag.Parent = root

	local track = Instance.new("Frame")
	track.Size = UDim2.new(1, -96, 0, 10)
	track.Position = UDim2.new(0, 42, 0.5, -5)
	track.BackgroundColor3 = c[meta.track]
	track.BorderSizePixel = 0
	track.Parent = root
	Theme.corner(track, Theme.radii.bar)
	local trackStroke = Theme.stroke(track, c.stroke, 1)

	local fill = Instance.new("Frame")
	fill.Name = "Fill"
	fill.Size = UDim2.new(1, 0, 1, 0)
	fill.BackgroundColor3 = c[meta.fill]
	fill.BorderSizePixel = 0
	fill.Parent = track
	Theme.corner(fill, Theme.radii.bar)

	local value = Instance.new("TextLabel")
	value.Size = UDim2.new(0, 50, 1, 0)
	value.Position = UDim2.new(1, -50, 0, 0)
	value.BackgroundTransparency = 1
	value.Font = Theme.fonts.mono
	value.TextSize = 11
	value.TextColor3 = c.text
	value.TextXAlignment = Enum.TextXAlignment.Right
	value.TextYAlignment = Enum.TextYAlignment.Center
	value.Text = "0/0"
	value.Parent = root

	local glowTween: Tween? = nil

	local function setDanger(on: boolean, glowColor: Color3)
		if glowTween then
			glowTween:Cancel()
			glowTween = nil
		end
		if on then
			trackStroke.Color = glowColor
			trackStroke.Thickness = 2
			glowTween = TweenService:Create(trackStroke, Theme.tween.glow, { Transparency = 0.55 })
			glowTween:Play()
		else
			trackStroke.Color = c.stroke
			trackStroke.Thickness = 1
			trackStroke.Transparency = 0
		end
	end

	local function set(current: number, max: number)
		local m = math.max(1, max)
		local ratio = math.clamp(current / m, 0, 1)
		TweenUtil.barFill(fill, ratio)
		value.Text = ("%d/%d"):format(math.floor(current + 0.5), math.floor(max + 0.5))
		if kind == "temperature" and ratio >= 0.8 then
			fill.BackgroundColor3 = c.danger
			setDanger(true, c.danger)
		elseif kind == "battery" and ratio <= 0.22 then
			fill.BackgroundColor3 = c.warning
			setDanger(true, c.warning)
		elseif kind == "integrity" and ratio <= 0.28 then
			fill.BackgroundColor3 = c.danger
			setDanger(true, c.danger)
		else
			fill.BackgroundColor3 = c[meta.fill]
			setDanger(false, c.stroke)
		end
	end

	return { root = root, set = set }
end

function ResourceBar.sideBlock(parent: Instance, displayName: string, size: UDim2, position: UDim2)
	local c = Theme.colors

	local root = Instance.new("Frame")
	root.Name = "SideBlock"
	root.Size = size
	root.Position = position
	root.BackgroundColor3 = c.bgInset
	root.BackgroundTransparency = 0.12
	root.BorderSizePixel = 0
	root.Parent = parent
	Theme.corner(root, Theme.radii.sm)
	Theme.stroke(root, c.stroke, 1)

	local nameLabel = Instance.new("TextLabel")
	nameLabel.Size = UDim2.new(1, -16, 0, 18)
	nameLabel.Position = UDim2.new(0, 8, 0, 6)
	nameLabel.BackgroundTransparency = 1
	nameLabel.Font = Theme.fonts.button
	nameLabel.TextSize = 13
	nameLabel.TextColor3 = c.text
	nameLabel.TextXAlignment = Enum.TextXAlignment.Left
	nameLabel.TextTruncate = Enum.TextTruncate.AtEnd
	nameLabel.Text = displayName
	nameLabel.Parent = root

	local integrity = ResourceBar.create(root, "integrity", UDim2.new(1, -12, 0, 16), UDim2.new(0, 6, 0, 28))
	local temperature = ResourceBar.create(root, "temperature", UDim2.new(1, -12, 0, 16), UDim2.new(0, 6, 0, 46))
	local battery = ResourceBar.create(root, "battery", UDim2.new(1, -12, 0, 16), UDim2.new(0, 6, 0, 64))

	local function setFromSide(side: any)
		nameLabel.Text = side.displayName or displayName
		integrity.set(side.integrity or 0, side.integrityMax or 1)
		temperature.set(side.temperature or 0, side.temperatureMax or 1)
		battery.set(side.battery or 0, side.batteryMax or 1)
	end

	return {
		root = root,
		nameLabel = nameLabel,
		setFromSide = setFromSide,
	}
end

return ResourceBar

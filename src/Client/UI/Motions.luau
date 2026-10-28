-- UI motions: UIScale pops, pulses, float-ups. Uses Theme.tween tokens.

local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))

local Motions = {}

local function ensureScale(gui: GuiObject): UIScale
	local existing = gui:FindFirstChildOfClass("UIScale")
	if existing then
		return existing
	end
	local s = Instance.new("UIScale")
	s.Scale = 1
	s.Parent = gui
	return s
end

function Motions.popIn(gui: GuiObject, fromScale: number?)
	gui.Visible = true
	local scale = ensureScale(gui)
	scale.Scale = fromScale or 0.86
	TweenService:Create(scale, Theme.tween.pop, { Scale = 1 }):Play()
end

function Motions.popOut(gui: GuiObject, onDone: (() -> ())?)
	local scale = ensureScale(gui)
	local tw = TweenService:Create(scale, Theme.tween.close, { Scale = 0.9 })
	tw:Play()
	tw.Completed:Connect(function()
		gui.Visible = false
		scale.Scale = 1
		if onDone then
			onDone()
		end
	end)
end

function Motions.pulse(gui: GuiObject, peak: number?)
	local scale = ensureScale(gui)
	local peakScale = peak or 1.06
	local up = TweenService:Create(scale, Theme.tween.pulse, { Scale = peakScale })
	up:Play()
	up.Completed:Connect(function()
		TweenService:Create(scale, Theme.tween.pulse, { Scale = 1 }):Play()
	end)
end

function Motions.shake(gui: GuiObject, amplitude: number?)
	local amp = amplitude or 6
	local origin = gui.Position
	local steps = {
		UDim2.new(origin.X.Scale, origin.X.Offset + amp, origin.Y.Scale, origin.Y.Offset),
		UDim2.new(origin.X.Scale, origin.X.Offset - amp, origin.Y.Scale, origin.Y.Offset),
		UDim2.new(origin.X.Scale, origin.X.Offset + amp * 0.5, origin.Y.Scale, origin.Y.Offset),
		origin,
	}
	task.spawn(function()
		for _, pos in steps do
			local tw = TweenService:Create(gui, TweenInfo.new(0.04, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
				Position = pos,
			})
			tw:Play()
			tw.Completed:Wait()
		end
	end)
end

function Motions.floatUp(
	gui: GuiObject,
	distance: number?,
	duration: number?,
	onDone: (() -> ())?
)
	local dist = distance or 48
	local info = TweenInfo.new(duration or 0.85, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	local start = gui.Position
	local tw = TweenService:Create(gui, info, {
		Position = UDim2.new(start.X.Scale, start.X.Offset, start.Y.Scale, start.Y.Offset - dist),
		TextTransparency = if gui:IsA("TextLabel") or gui:IsA("TextButton") then 1 else nil,
		BackgroundTransparency = if gui:IsA("Frame") then 1 else nil,
	})
	-- TextTransparency only valid on text objects
	if gui:IsA("TextLabel") or gui:IsA("TextButton") then
		tw = TweenService:Create(gui, info, {
			Position = UDim2.new(start.X.Scale, start.X.Offset, start.Y.Scale, start.Y.Offset - dist),
			TextTransparency = 1,
		})
	else
		tw = TweenService:Create(gui, info, {
			Position = UDim2.new(start.X.Scale, start.X.Offset, start.Y.Scale, start.Y.Offset - dist),
		})
	end
	tw:Play()
	tw.Completed:Connect(function()
		if onDone then
			onDone()
		end
		gui:Destroy()
	end)
end

function Motions.revealStagger(guis: { GuiObject }, delayStep: number?)
	local step = delayStep or 0.08
	for i, g in guis do
		g.Visible = false
		task.delay((i - 1) * step, function()
			if g.Parent then
				Motions.popIn(g, 0.7)
			end
		end)
	end
end

return Motions

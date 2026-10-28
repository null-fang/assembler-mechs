-- Open/close and hover tweens using Theme tokens.

local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))

local TweenUtil = {}

function TweenUtil.play(instance: Instance, info: TweenInfo, props: { [string]: any }): Tween
	local tw = TweenService:Create(instance, info, props)
	tw:Play()
	return tw
end

function TweenUtil.openFrom(frame: GuiObject, startPos: UDim2, endPos: UDim2, endTransparency: number?)
	frame.Visible = true
	frame.Position = startPos
	local startT = frame.BackgroundTransparency
	frame.BackgroundTransparency = math.min(1, startT + 0.4)
	TweenUtil.play(frame, Theme.tween.open, {
		Position = endPos,
		BackgroundTransparency = endTransparency or startT,
	})
end

function TweenUtil.closeTo(frame: GuiObject, endPos: UDim2, restorePos: UDim2?, onDone: (() -> ())?)
	local tw = TweenUtil.play(frame, Theme.tween.close, {
		Position = endPos,
		BackgroundTransparency = math.min(1, frame.BackgroundTransparency + 0.45),
	})
	tw.Completed:Connect(function()
		frame.Visible = false
		if restorePos then
			frame.Position = restorePos
		end
		if onDone then
			onDone()
		end
	end)
end

function TweenUtil.barFill(fill: GuiObject, scaleX: number)
	TweenUtil.play(fill, Theme.tween.bar, {
		Size = UDim2.new(math.clamp(scaleX, 0, 1), 0, 1, 0),
	})
end

return TweenUtil

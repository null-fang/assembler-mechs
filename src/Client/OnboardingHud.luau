-- Soft first-session prompts. Skippable. Short copy.

local Players = game:GetService("Players")
local Workspace = game:GetService("Workspace")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Theme = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("UI"):WaitForChild("Theme"))
local Steps = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Onboarding"):WaitForChild("Steps"))
local Button = require(script.Parent:WaitForChild("UI"):WaitForChild("Button"))

local OnboardingHud = {}

local remotesFolder = ReplicatedStorage:WaitForChild("AssemblerRemotes")
local CompleteOnboarding = remotesFolder:WaitForChild("CompleteOnboarding")

local player = Players.LocalPlayer
local root: Frame?
local titleL: TextLabel?
local bodyL: TextLabel?
local hintL: TextLabel?
local progress: any = nil
local callbacks: {
	openCampaign: () -> (),
	openGarage: () -> (),
	openCrate: () -> (),
}?
local beacon: Part?
local conn: RBXScriptConnection?
local rest = UDim2.new(0.5, -200, 0, 18)

local function destroyBeacon()
	if beacon then
		beacon:Destroy()
		beacon = nil
	end
end

local function findWorldTarget(stepId: string): BasePart?
	local lobby = Workspace:FindFirstChild("Lobby")
	if not lobby then
		return nil
	end
	if stepId == "campaign" then
		local t = lobby:FindFirstChild("CampaignTerminal", true)
		if t and t:IsA("BasePart") then
			return t
		end
	elseif stepId == "garage" then
		local t = lobby:FindFirstChild("GaragePedestal", true)
		if t and t:IsA("BasePart") then
			return t
		end
	elseif stepId == "crate" then
		local t = lobby:FindFirstChild("StarterCrate", true)
		if t and t:IsA("BasePart") then
			return t
		end
	end
	return nil
end

local function placeBeacon(stepId: string)
	destroyBeacon()
	local target = findWorldTarget(stepId)
	if not target then
		return
	end
	beacon = Instance.new("Part")
	beacon.Name = "OnboardingBeacon"
	beacon.Anchored = true
	beacon.CanCollide = false
	beacon.CanQuery = false
	beacon.CanTouch = false
	beacon.Material = Enum.Material.Neon
	beacon.Color = if stepId == "campaign" then Theme.colors.cyan else Theme.colors.accent
	beacon.Size = Vector3.new(1.2, 1.2, 1.2)
	beacon.Transparency = 0.25
	beacon.Parent = Workspace
	local base = target.Position + Vector3.new(0, target.Size.Y * 0.5 + 5, 0)
	if conn then
		conn:Disconnect()
	end
	local t0 = os.clock()
	conn = RunService.RenderStepped:Connect(function()
		if not beacon or not beacon.Parent then
			return
		end
		local bob = math.sin((os.clock() - t0) * 3) * 0.6
		beacon.CFrame = CFrame.new(base + Vector3.new(0, bob, 0)) * CFrame.Angles(0, os.clock() * 1.4, 0)
	end)
end

local function currentStep(): Steps.StepId?
	if not progress or progress.done or progress.skipped then
		return nil
	end
	return progress.next
end

function OnboardingHud.apply(snap)
	progress = snap
	OnboardingHud.refresh()
end

function OnboardingHud.refresh()
	if not root or not titleL or not bodyL or not hintL then
		return
	end
	local stepId = currentStep()
	if not stepId then
		root.Visible = false
		destroyBeacon()
		if conn then
			conn:Disconnect()
			conn = nil
		end
		return
	end
	local def = Steps.get(stepId)
	titleL.Text = def.title
	bodyL.Text = def.body
	hintL.Text = def.hint
	root.Visible = true
	placeBeacon(stepId)
end

function OnboardingHud.complete(stepId: string)
	local ok, snap = pcall(function()
		return CompleteOnboarding:InvokeServer(stepId)
	end)
	if ok and snap then
		progress = snap
		OnboardingHud.refresh()
	end
end

function OnboardingHud.notifyOpened(kind: string)
	-- kind: campaign | garage | crate
	local stepId = currentStep()
	if stepId == kind then
		OnboardingHud.complete(kind)
	elseif kind == "campaign" or kind == "garage" or kind == "crate" then
		-- Still mark if they open out of order.
		OnboardingHud.complete(kind)
	end
end

function OnboardingHud.mount(parentGui: ScreenGui, cbs: typeof(callbacks))
	callbacks = cbs
	root = Instance.new("Frame")
	root.Name = "OnboardingTip"
	root.Size = UDim2.new(0, 400, 0, 92)
	root.Position = rest
	root.BackgroundColor3 = Theme.colors.bgPanel
	root.BackgroundTransparency = Theme.transparency.panel
	root.BorderSizePixel = 0
	root.Visible = false
	root.ZIndex = 30
	root.Parent = parentGui
	Theme.corner(root, Theme.radii.md)
	Theme.stroke(root, Theme.colors.strokeFocus, 1)
	Theme.accentStrip(root, Theme.colors.cyan)

	titleL = Theme.label(root, "", UDim2.new(1, -90, 0, 20), UDim2.new(0, 14, 0, 10), 14, {
		font = Theme.fonts.display,
		color = Theme.colors.cyan,
	})
	bodyL = Theme.label(root, "", UDim2.new(1, -24, 0, 36), UDim2.new(0, 14, 0, 34), 13, {
		color = Theme.colors.text,
	})
	hintL = Theme.label(root, "", UDim2.new(1, -100, 0, 16), UDim2.new(0, 14, 1, -22), 11, {
		color = Theme.colors.textDim,
	})

	local skip = Button.create(root, "Skip", UDim2.new(0, 64, 0, 26), UDim2.new(1, -78, 0, 10), "ghost")
	skip.MouseButton1Click:Connect(function()
		OnboardingHud.complete("skip")
	end)

	player.CharacterAdded:Connect(function()
		task.delay(0.8, function()
			OnboardingHud.refresh()
		end)
	end)
end

return OnboardingHud

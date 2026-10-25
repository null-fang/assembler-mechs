-- Elevated side camera for arena fights. Stops lobby follow cam while active.

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local Workspace = game:GetService("Workspace")

local BattleCamera = {}

local player = Players.LocalPlayer
local savedType: Enum.CameraType? = nil
local conn: RBXScriptConnection? = nil
local targetPos: Vector3? = nil
local lookAt: Vector3? = nil
local active = false

local function computeFromArena(arenaId: string): (Vector3?, Vector3?)
	local arenas = Workspace:FindFirstChild("Arenas")
	if not arenas then
		return nil, nil
	end
	local arena = arenas:FindFirstChild(arenaId)
	if not arena then
		return nil, nil
	end
	local padA = arena:FindFirstChild("PadA", true)
	local padB = arena:FindFirstChild("PadB", true)
	local origin = arena:FindFirstChild("ArenaOrigin", true)
	if not (padA and padA:IsA("BasePart") and padB and padB:IsA("BasePart")) then
		return nil, nil
	end
	local mid = padA.Position:Lerp(padB.Position, 0.5) + Vector3.new(0, 8, 0)
	if origin and origin:IsA("BasePart") then
		mid = Vector3.new(origin.Position.X, mid.Y, origin.Position.Z)
	end
	local axis = padB.Position - padA.Position
	local flat = Vector3.new(axis.X, 0, axis.Z)
	if flat.Magnitude < 0.1 then
		flat = Vector3.new(1, 0, 0)
	else
		flat = flat.Unit
	end
	local side = flat:Cross(Vector3.yAxis)
	if side.Magnitude < 0.1 then
		side = Vector3.new(0, 0, 1)
	else
		side = side.Unit
	end
	local camPos = mid + side * 52 + Vector3.new(0, 26, 0)
	return camPos, mid
end

function BattleCamera.startForArena(arenaId: string)
	local camPos, focus = computeFromArena(arenaId)
	if not camPos or not focus then
		return
	end
	local cam = Workspace.CurrentCamera
	if not cam then
		return
	end
	active = true
	savedType = cam.CameraType
	cam.CameraType = Enum.CameraType.Scriptable
	targetPos = camPos
	lookAt = focus
	cam.CFrame = CFrame.lookAt(camPos, focus)
	-- Combat HUD needs a free cursor for action buttons.
	UserInputService.MouseBehavior = Enum.MouseBehavior.Default
	UserInputService.MouseIconEnabled = true
	if conn then
		conn:Disconnect()
	end
	conn = RunService.RenderStepped:Connect(function()
		local c = Workspace.CurrentCamera
		if not c or not targetPos or not lookAt then
			return
		end
		c.CFrame = c.CFrame:Lerp(CFrame.lookAt(targetPos, lookAt), 0.1)
		-- Keep mouse free even if something else tries to lock it mid-fight.
		if active then
			UserInputService.MouseBehavior = Enum.MouseBehavior.Default
			UserInputService.MouseIconEnabled = true
		end
	end)
end

function BattleCamera.stop()
	active = false
	if conn then
		conn:Disconnect()
		conn = nil
	end
	targetPos = nil
	lookAt = nil
	local cam = Workspace.CurrentCamera
	if cam then
		cam.CameraType = savedType or Enum.CameraType.Custom
		local character = player.Character
		local humanoid = character and character:FindFirstChildOfClass("Humanoid")
		if humanoid then
			cam.CameraSubject = humanoid
		end
	end
end

function BattleCamera.isActive(): boolean
	return active
end

return BattleCamera

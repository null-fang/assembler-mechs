-- Lobby third-person follow + mouse look. V (or Join HUD) toggles look lock.
-- Menus / combat click mode unlock the cursor via ModalMouse callbacks.

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local Workspace = game:GetService("Workspace")

local LobbyCamera = {}

local player = Players.LocalPlayer

local DISTANCE = 12
local HEIGHT = 3.2
local MIN_PITCH = math.rad(-35)
local MAX_PITCH = math.rad(55)
local SENS = 0.0042

local enabled = false -- overall lobby camera (off during BattleCamera)
-- Default free cursor so Join HUD is clickable on spawn; V enables look.
local lookEnabled = false
local menuBlocksLook = false
local yaw = 0
local pitch = math.rad(12)
local conn: RBXScriptConnection? = nil
local inputConn: RBXScriptConnection? = nil
local charConn: RBXScriptConnection? = nil
local statusCb: ((lookOn: boolean) -> ())? = nil

local function subjectPart(): BasePart?
	local char = player.Character
	if not char then
		return nil
	end
	local hum = char:FindFirstChildOfClass("Humanoid")
	local root = char:FindFirstChild("HumanoidRootPart")
	if hum and root and root:IsA("BasePart") and hum.Health > 0 then
		return root
	end
	return nil
end

local function wantMouseLock(): boolean
	return enabled and lookEnabled and not menuBlocksLook
end

local function applyMouseBehavior()
	if wantMouseLock() then
		UserInputService.MouseBehavior = Enum.MouseBehavior.LockCenter
		UserInputService.MouseIconEnabled = false
	else
		UserInputService.MouseBehavior = Enum.MouseBehavior.Default
		UserInputService.MouseIconEnabled = true
	end
end

local function syncYawFromCharacter()
	local root = subjectPart()
	if root then
		local look = root.CFrame.LookVector
		yaw = math.atan2(-look.X, -look.Z)
	end
end

local function updateCamera(dt: number)
	if not enabled then
		return
	end
	local root = subjectPart()
	local cam = Workspace.CurrentCamera
	if not root or not cam then
		return
	end

	if wantMouseLock() then
		local delta = UserInputService:GetMouseDelta()
		yaw -= delta.X * SENS
		pitch = math.clamp(pitch - delta.Y * SENS, MIN_PITCH, MAX_PITCH)

		-- Face walk direction with camera yaw so WASD matches look.
		local flat = CFrame.Angles(0, yaw, 0)
		root.CFrame = CFrame.new(root.Position) * flat
	else
		-- Free cursor: trail behind wherever the character is facing.
		local look = root.CFrame.LookVector
		local targetYaw = math.atan2(-look.X, -look.Z)
		local alpha = 1 - math.exp(-10 * dt)
		local diff = (targetYaw - yaw + math.pi) % (2 * math.pi) - math.pi
		yaw += diff * alpha
		-- RMB drag still orbits when cursor is free.
		if UserInputService:IsMouseButtonPressed(Enum.UserInputType.MouseButton2) then
			local delta = UserInputService:GetMouseDelta()
			yaw -= delta.X * SENS
			pitch = math.clamp(pitch - delta.Y * SENS, MIN_PITCH, MAX_PITCH)
		end
	end

	local rot = CFrame.Angles(0, yaw, 0) * CFrame.Angles(pitch, 0, 0)
	local focus = root.Position + Vector3.new(0, HEIGHT * 0.55, 0)
	local offset = rot:VectorToWorldSpace(Vector3.new(0, HEIGHT * 0.15, DISTANCE))
	local desired = CFrame.lookAt(focus + offset, focus)
	local alpha = 1 - math.exp(-14 * dt)
	cam.CFrame = cam.CFrame:Lerp(desired, alpha)
end

local function bindCharacter(char: Model)
	local hum = char:WaitForChild("Humanoid", 5)
	if hum and hum:IsA("Humanoid") then
		hum.AutoRotate = not wantMouseLock()
		hum.CameraOffset = Vector3.zero
	end
	syncYawFromCharacter()
end

local function setHumanoidAutoRotate()
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if hum then
		hum.AutoRotate = not wantMouseLock()
	end
end

function LobbyCamera.isLookEnabled(): boolean
	return lookEnabled
end

function LobbyCamera.setLookEnabled(on: boolean)
	lookEnabled = on
	setHumanoidAutoRotate()
	applyMouseBehavior()
	if statusCb then
		statusCb(lookEnabled)
	end
end

function LobbyCamera.toggleLook()
	LobbyCamera.setLookEnabled(not lookEnabled)
end

function LobbyCamera.onLookChanged(cb: (lookOn: boolean) -> ())
	statusCb = cb
end

function LobbyCamera.setMenuBlocking(blocks: boolean)
	menuBlocksLook = blocks
	setHumanoidAutoRotate()
	applyMouseBehavior()
end

function LobbyCamera.start()
	if enabled then
		return
	end
	enabled = true
	local cam = Workspace.CurrentCamera
	if cam then
		cam.CameraType = Enum.CameraType.Scriptable
	end
	player.CameraMode = Enum.CameraMode.Classic
	player.CameraMinZoomDistance = DISTANCE
	player.CameraMaxZoomDistance = DISTANCE

	syncYawFromCharacter()
	applyMouseBehavior()
	setHumanoidAutoRotate()

	if conn then
		conn:Disconnect()
	end
	conn = RunService.RenderStepped:Connect(function(dt)
		updateCamera(dt)
	end)

	if inputConn then
		inputConn:Disconnect()
	end
	inputConn = UserInputService.InputBegan:Connect(function(input, gameProcessed)
		if gameProcessed then
			return
		end
		if input.KeyCode == Enum.KeyCode.V then
			if menuBlocksLook then
				return
			end
			LobbyCamera.toggleLook()
		end
	end)

	if charConn then
		charConn:Disconnect()
	end
	charConn = player.CharacterAdded:Connect(function(char)
		task.defer(function()
			if enabled then
				local c = Workspace.CurrentCamera
				if c then
					c.CameraType = Enum.CameraType.Scriptable
				end
				bindCharacter(char)
				applyMouseBehavior()
			end
		end)
	end)

	if player.Character then
		bindCharacter(player.Character)
	end
end

function LobbyCamera.stop()
	if not enabled then
		return
	end
	enabled = false
	if conn then
		conn:Disconnect()
		conn = nil
	end
	if inputConn then
		inputConn:Disconnect()
		inputConn = nil
	end
	-- Leave charConn so restart can rebind; disconnect on hard stop below.
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if hum then
		hum.AutoRotate = true
	end
	local cam = Workspace.CurrentCamera
	if cam then
		cam.CameraType = Enum.CameraType.Custom
		if hum then
			cam.CameraSubject = hum
		end
	end
	UserInputService.MouseBehavior = Enum.MouseBehavior.Default
	UserInputService.MouseIconEnabled = true
end

function LobbyCamera.destroy()
	LobbyCamera.stop()
	if charConn then
		charConn:Disconnect()
		charConn = nil
	end
end

return LobbyCamera

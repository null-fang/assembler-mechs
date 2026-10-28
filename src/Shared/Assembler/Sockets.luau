-- Attach sockets relative to torso center (local space, studs).
-- SuperMechs-inspired combat stance: crouched biped, weapons ready — not a T-pose.

export type SocketName =
	"Torso"
	| "LeftHip"
	| "RightHip"
	| "LowerLeft"
	| "LowerRight"
	| "ShoulderLeft"
	| "ShoulderRight"
	| "Battery"
	| "CPU"
	| "Drone"

export type SocketDef = {
	name: SocketName,
	-- Offset from torso origin (center of torso block).
	offset: Vector3,
	-- Default block size when part has no visual.size.
	defaultSize: Vector3,
	-- Local rotation (degrees) applied after offset.
	rotationDeg: Vector3?,
}

local Sockets = {}

-- Chibi torso sits a bit lower; short thick legs reach the pad.
Sockets.TORSO_HEIGHT = 3.85

Sockets.defs = {
	Torso = {
		name = "Torso",
		offset = Vector3.new(0, 0, 0),
		-- Slight forward lean baked via rotation so the whole stack reads aggressive.
		defaultSize = Vector3.new(3.6, 2.8, 2.4),
		rotationDeg = Vector3.new(8, 0, 0),
	},
	-- Hips tucked under the belly; pitch = knee-forward combat crouch (kit Root = hip pivot).
	LeftHip = {
		name = "LeftHip",
		offset = Vector3.new(-1.05, -1.85, 0.15),
		defaultSize = Vector3.new(1.35, 2.2, 1.45),
		rotationDeg = Vector3.new(18, 6, 10),
	},
	RightHip = {
		name = "RightHip",
		offset = Vector3.new(1.05, -1.85, 0.15),
		defaultSize = Vector3.new(1.35, 2.2, 1.45),
		rotationDeg = Vector3.new(18, -6, -10),
	},
	-- Lower weapons = forearm guns/blades: forward + slightly down, elbows in — not wing T-pose.
	LowerLeft = {
		name = "LowerLeft",
		offset = Vector3.new(-2.15, -0.35, 0.95),
		defaultSize = Vector3.new(1.0, 0.85, 2.4),
		rotationDeg = Vector3.new(12, 28, -22),
	},
	LowerRight = {
		name = "LowerRight",
		offset = Vector3.new(2.15, -0.35, 0.95),
		defaultSize = Vector3.new(1.0, 0.85, 2.4),
		rotationDeg = Vector3.new(12, -28, 22),
	},
	-- Shoulder pods/cannons sit high and aim forward over the cockpit.
	ShoulderLeft = {
		name = "ShoulderLeft",
		offset = Vector3.new(-1.75, 1.55, -0.35),
		defaultSize = Vector3.new(1.55, 1.15, 2.4),
		rotationDeg = Vector3.new(-18, 18, 6),
	},
	ShoulderRight = {
		name = "ShoulderRight",
		offset = Vector3.new(1.75, 1.55, -0.35),
		defaultSize = Vector3.new(1.55, 1.15, 2.4),
		rotationDeg = Vector3.new(-18, -18, -6),
	},
	Battery = {
		name = "Battery",
		offset = Vector3.new(0, 0.15, -1.45),
		defaultSize = Vector3.new(1.5, 0.95, 0.65),
	},
	CPU = {
		name = "CPU",
		offset = Vector3.new(0, 1.15, 0.35),
		defaultSize = Vector3.new(0.7, 0.35, 0.7),
	},
	Drone = {
		name = "Drone",
		offset = Vector3.new(0.35, 2.15, -1.05),
		defaultSize = Vector3.new(1.0, 0.55, 1.1),
	},
} :: { [string]: SocketDef }

function Sockets.get(name: SocketName): SocketDef
	return Sockets.defs[name]
end

return Sockets

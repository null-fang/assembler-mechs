-- Attach sockets relative to torso center (local space, studs).
-- Readable biped silhouette at combat distance.

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

-- Torso origin sits ~4.5 studs above ground so feet touch pads.
Sockets.TORSO_HEIGHT = 4.5

Sockets.defs = {
	Torso = {
		name = "Torso",
		offset = Vector3.new(0, 0, 0),
		defaultSize = Vector3.new(4.0, 3.0, 2.5),
	},
	LeftHip = {
		name = "LeftHip",
		offset = Vector3.new(-1.15, -2.6, 0),
		defaultSize = Vector3.new(1.3, 2.6, 1.5),
	},
	RightHip = {
		name = "RightHip",
		offset = Vector3.new(1.15, -2.6, 0),
		defaultSize = Vector3.new(1.3, 2.6, 1.5),
	},
	LowerLeft = {
		name = "LowerLeft",
		offset = Vector3.new(-2.7, -0.2, 0.3),
		defaultSize = Vector3.new(1.1, 0.9, 2.3),
		rotationDeg = Vector3.new(0, 12, -8),
	},
	LowerRight = {
		name = "LowerRight",
		offset = Vector3.new(2.7, -0.2, 0.3),
		defaultSize = Vector3.new(1.1, 0.9, 2.3),
		rotationDeg = Vector3.new(0, -12, 8),
	},
	ShoulderLeft = {
		name = "ShoulderLeft",
		offset = Vector3.new(-2.1, 1.55, -0.1),
		defaultSize = Vector3.new(1.5, 1.0, 2.6),
		rotationDeg = Vector3.new(-6, 8, 0),
	},
	ShoulderRight = {
		name = "ShoulderRight",
		offset = Vector3.new(2.1, 1.55, -0.1),
		defaultSize = Vector3.new(1.5, 1.0, 2.6),
		rotationDeg = Vector3.new(-6, -8, 0),
	},
	Battery = {
		name = "Battery",
		offset = Vector3.new(0, 0.2, -1.55),
		defaultSize = Vector3.new(1.6, 1.0, 0.7),
	},
	CPU = {
		name = "CPU",
		offset = Vector3.new(0, 1.35, 0.2),
		defaultSize = Vector3.new(0.7, 0.35, 0.7),
	},
	Drone = {
		name = "Drone",
		offset = Vector3.new(0.4, 2.4, -1.2),
		defaultSize = Vector3.new(1.0, 0.6, 1.2),
	},
} :: { [string]: SocketDef }

function Sockets.get(name: SocketName): SocketDef
	return Sockets.defs[name]
end

return Sockets

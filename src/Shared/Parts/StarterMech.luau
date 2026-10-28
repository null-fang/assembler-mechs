-- Default starter loadout — complete basic mech on Primary.

local Catalog = require(script.Parent.Catalog)
local SoftSlots = require(script.Parent.Slots)

local StarterMech = {}

type SoftLoadout = SoftSlots.EquippedLoadout

-- Part ids granted into inventory on first touch (owned + equipped on Primary).
StarterMech.GRANT_IDS = {
	"rusty_cage",
	"workboot_l",
	"workboot_r",
	"snap_arm",
	"rivet_gun",
	"brick_shoulder",
	"thick_skin",
	"heat_sink_chip",
	"desk_brick",
	"scrap_cpu",
	"floor_bit",
	-- Spares the player can swap in garage (not auto-equipped).
	"ember_fist",
	"wire_wrap",
} :: { string }

function StarterMech.buildLoadout(): SoftLoadout
	return {
		torso = Catalog.require("rusty_cage"),
		leftLeg = Catalog.require("workboot_l"),
		rightLeg = Catalog.require("workboot_r"),
		lowerLeft = Catalog.asWeapon("snap_arm", "LowerLeft"),
		lowerRight = Catalog.asWeapon("rivet_gun", "LowerRight"),
		shoulderLeft = nil,
		shoulderRight = Catalog.asWeapon("brick_shoulder", "ShoulderRight"),
		chips = {
			Catalog.require("thick_skin"),
			Catalog.require("heat_sink_chip"),
		},
		battery = Catalog.require("desk_brick"),
		cpu = Catalog.require("scrap_cpu"),
		drone = Catalog.require("floor_bit"),
	}
end

function StarterMech.isLegal(loadout: SoftSlots.EquippedLoadout): boolean
	if not loadout.torso then
		return false
	end
	if not loadout.leftLeg or not loadout.rightLeg then
		return false
	end
	if not SoftSlots.legsCompatible(loadout.leftLeg, loadout.rightLeg) then
		return false
	end
	local hasWeapon = loadout.lowerLeft
		or loadout.lowerRight
		or loadout.shoulderLeft
		or loadout.shoulderRight
	return hasWeapon ~= nil
end

return StarterMech

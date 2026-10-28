-- Embedded industrial texture payloads (RGBA8 base64 @ 128).
local M = {
	SIZE = 128,
	metal_plate = require(script.metal_plate),
	scratched_steel = require(script.scratched_steel),
	hazard_stripe = require(script.hazard_stripe),
	matte_rubber = require(script.matte_rubber),
	carbon_dark = require(script.carbon_dark),
	emissive_strip = require(script.emissive_strip),
}
return M

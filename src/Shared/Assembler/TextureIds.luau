-- Shared TextureIds contract (keep in sync with tools/texture_ids.json).
-- Fill rbxassetid after Studio/Open Cloud upload; empty → TextureApply uses embedded pixels.

export type TextureDef = {
	key: string,
	rbxassetid: string,
	role: string,
	studsPerTile: number,
	transparency: number,
	minRarity: string?,
	file: string,
}

local TextureIds = {}

TextureIds.version = 1

TextureIds.keys = {
	"metal_plate",
	"scratched_steel",
	"hazard_stripe",
	"matte_rubber",
	"carbon_dark",
	"emissive_strip",
}

-- rbxassetid strings without "rbxassetid://" prefix. Empty = use embed bake.
TextureIds.textures = {
	metal_plate = {
		key = "metal_plate",
		rbxassetid = "",
		role = "hull",
		studsPerTile = 2.5,
		transparency = 0.35,
		file = "assets/textures/metal_plate.png",
	},
	scratched_steel = {
		key = "scratched_steel",
		rbxassetid = "",
		role = "steel",
		studsPerTile = 2.0,
		transparency = 0.4,
		file = "assets/textures/scratched_steel.png",
	},
	hazard_stripe = {
		key = "hazard_stripe",
		rbxassetid = "",
		role = "hazard",
		studsPerTile = 1.5,
		transparency = 0.25,
		file = "assets/textures/hazard_stripe.png",
	},
	matte_rubber = {
		key = "matte_rubber",
		rbxassetid = "",
		role = "rubber",
		studsPerTile = 3.0,
		transparency = 0.45,
		file = "assets/textures/matte_rubber.png",
	},
	carbon_dark = {
		key = "carbon_dark",
		rbxassetid = "",
		role = "carbon",
		studsPerTile = 1.75,
		transparency = 0.3,
		file = "assets/textures/carbon_dark.png",
	},
	emissive_strip = {
		key = "emissive_strip",
		rbxassetid = "",
		role = "emissive",
		studsPerTile = 2.0,
		transparency = 0.15,
		minRarity = "Epic",
		file = "assets/textures/emissive_strip.png",
	},
} :: { [string]: TextureDef }

TextureIds.materialHints = {
	Metal = "metal_plate",
	CorrodedMetal = "scratched_steel",
	DiamondPlate = "metal_plate",
	Neon = "emissive_strip",
	SmoothPlastic = "matte_rubber",
	Plastic = "matte_rubber",
	Fabric = "matte_rubber",
	Foil = "carbon_dark",
	Glass = "carbon_dark",
	ForceField = "emissive_strip",
}

TextureIds.nameHints = {
	Accent = "hazard_stripe",
	Glow = "emissive_strip",
	Trim = "hazard_stripe",
	Pad = "matte_rubber",
	Grip = "matte_rubber",
	Rubber = "matte_rubber",
	Chip = "carbon_dark",
	Carbon = "carbon_dark",
	Cpu = "carbon_dark",
	Core = "metal_plate",
}

function TextureIds.contentUri(def: TextureDef): string?
	if def.rbxassetid == nil or def.rbxassetid == "" then
		return nil
	end
	local id = def.rbxassetid
	if string.sub(id, 1, 13) == "rbxassetid://" then
		return id
	end
	return "rbxassetid://" .. id
end

function TextureIds.resolveRole(partName: string, materialName: string): string
	for prefix, key in TextureIds.nameHints do
		if string.sub(partName, 1, #prefix) == prefix or string.find(partName, prefix, 1, true) then
			return key
		end
	end
	local fromMat = TextureIds.materialHints[materialName]
	if fromMat then
		return fromMat
	end
	return "metal_plate"
end

return TextureIds

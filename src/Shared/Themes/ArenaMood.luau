-- Per-arena Lighting / Atmosphere presets keyed by ThemeIds.ARENA_THEMES.
-- Applied when teleporting into a fight; Lobby restores bay daylight.

local Lighting = game:GetService("Lighting")

local ThemeIds = require(script.Parent.ThemeIds)

local ArenaMood = {}

export type MoodPreset = {
	Ambient: Color3,
	OutdoorAmbient: Color3,
	Brightness: number,
	ClockTime: number,
	FogColor: Color3,
	FogStart: number,
	FogEnd: number,
	Atmosphere: {
		Density: number,
		Offset: number,
		Color: Color3,
		Decay: Color3,
		Glare: number,
		Haze: number,
	},
	ColorCorrection: {
		Brightness: number,
		Contrast: number,
		Saturation: number,
		TintColor: Color3,
	},
	BloomIntensity: number?,
}

local function c(r: number, g: number, b: number): Color3
	return Color3.fromRGB(r, g, b)
end

ArenaMood.Lobby = {
	Ambient = c(56, 61, 76),
	OutdoorAmbient = c(71, 76, 92),
	Brightness = 2.0,
	ClockTime = 16.25,
	FogColor = c(140, 148, 166),
	FogStart = 280,
	FogEnd = 1400,
	Atmosphere = {
		Density = 0.275,
		Offset = 0.12,
		Color = c(184, 194, 214),
		Decay = c(128, 140, 158),
		Glare = 0.12,
		Haze = 1.15,
	},
	ColorCorrection = {
		Brightness = 0.02,
		Contrast = 0.08,
		Saturation = 0.1,
		TintColor = Color3.new(1, 0.98, 0.95),
	},
	BloomIntensity = 0.32,
} :: MoodPreset

-- Scrap / Yardbone — warm amber dusk
ArenaMood.ScrapPit = {
	Ambient = c(72, 48, 32),
	OutdoorAmbient = c(90, 60, 40),
	Brightness = 1.85,
	ClockTime = 17.4,
	FogColor = c(170, 110, 70),
	FogStart = 120,
	FogEnd = 900,
	Atmosphere = {
		Density = 0.32,
		Offset = 0.08,
		Color = c(210, 140, 80),
		Decay = c(140, 80, 40),
		Glare = 0.18,
		Haze = 1.6,
	},
	ColorCorrection = {
		Brightness = 0.03,
		Contrast = 0.1,
		Saturation = 0.14,
		TintColor = Color3.new(1.05, 0.95, 0.88),
	},
	BloomIntensity = 0.36,
} :: MoodPreset

-- Arctic / Rimevault — cold blue morning
ArenaMood.DryDock = {
	Ambient = c(48, 70, 92),
	OutdoorAmbient = c(70, 100, 130),
	Brightness = 2.1,
	ClockTime = 10.2,
	FogColor = c(160, 200, 230),
	FogStart = 100,
	FogEnd = 950,
	Atmosphere = {
		Density = 0.3,
		Offset = 0.18,
		Color = c(180, 220, 245),
		Decay = c(90, 140, 180),
		Glare = 0.22,
		Haze = 1.4,
	},
	ColorCorrection = {
		Brightness = 0.04,
		Contrast = 0.06,
		Saturation = 0.05,
		TintColor = Color3.new(0.92, 0.97, 1.05),
	},
	BloomIntensity = 0.34,
} :: MoodPreset

-- Neon / Voltframe — deep night
ArenaMood.NightYard = {
	Ambient = c(28, 24, 48),
	OutdoorAmbient = c(36, 32, 70),
	Brightness = 1.35,
	ClockTime = 22.5,
	FogColor = c(50, 40, 90),
	FogStart = 80,
	FogEnd = 850,
	Atmosphere = {
		Density = 0.34,
		Offset = 0.1,
		Color = c(70, 50, 120),
		Decay = c(30, 20, 60),
		Glare = 0.08,
		Haze = 1.8,
	},
	ColorCorrection = {
		Brightness = -0.02,
		Contrast = 0.14,
		Saturation = 0.18,
		TintColor = Color3.new(0.95, 0.9, 1.08),
	},
	BloomIntensity = 0.48,
} :: MoodPreset

-- Desert / Duneplate — hot noon
ArenaMood.SandQuarry = {
	Ambient = c(90, 70, 40),
	OutdoorAmbient = c(120, 95, 55),
	Brightness = 2.35,
	ClockTime = 13.1,
	FogColor = c(210, 175, 110),
	FogStart = 110,
	FogEnd = 1000,
	Atmosphere = {
		Density = 0.28,
		Offset = 0.06,
		Color = c(230, 190, 120),
		Decay = c(180, 120, 60),
		Glare = 0.28,
		Haze = 1.5,
	},
	ColorCorrection = {
		Brightness = 0.05,
		Contrast = 0.09,
		Saturation = 0.12,
		TintColor = Color3.new(1.06, 0.98, 0.88),
	},
	BloomIntensity = 0.3,
} :: MoodPreset

local byTheme: { [string]: MoodPreset } = {
	Lobby = ArenaMood.Lobby,
	ScrapPit = ArenaMood.ScrapPit,
	DryDock = ArenaMood.DryDock,
	NightYard = ArenaMood.NightYard,
	SandQuarry = ArenaMood.SandQuarry,
}

local function ensureAtmosphere(): Atmosphere
	local existing = Lighting:FindFirstChildOfClass("Atmosphere")
	if existing then
		return existing
	end
	local a = Instance.new("Atmosphere")
	a.Parent = Lighting
	return a
end

local function ensureColorCorrection(): ColorCorrectionEffect
	local existing = Lighting:FindFirstChildOfClass("ColorCorrectionEffect")
	if existing then
		return existing
	end
	local cc = Instance.new("ColorCorrectionEffect")
	cc.Name = "ColorCorrection"
	cc.Parent = Lighting
	return cc
end

local function ensureBloom(): BloomEffect
	local existing = Lighting:FindFirstChildOfClass("BloomEffect")
	if existing then
		return existing
	end
	local bloom = Instance.new("BloomEffect")
	bloom.Name = "Bloom"
	bloom.Parent = Lighting
	return bloom
end

function ArenaMood.presetFor(themeId: string?): MoodPreset
	if themeId and byTheme[themeId] then
		return byTheme[themeId]
	end
	return ArenaMood.Lobby
end

function ArenaMood.apply(themeId: string?)
	local preset = ArenaMood.presetFor(themeId)
	Lighting.Ambient = preset.Ambient
	Lighting.OutdoorAmbient = preset.OutdoorAmbient
	Lighting.Brightness = preset.Brightness
	Lighting.ClockTime = preset.ClockTime
	Lighting.FogColor = preset.FogColor
	Lighting.FogStart = preset.FogStart
	Lighting.FogEnd = preset.FogEnd

	local atmos = ensureAtmosphere()
	local a = preset.Atmosphere
	atmos.Density = a.Density
	atmos.Offset = a.Offset
	atmos.Color = a.Color
	atmos.Decay = a.Decay
	atmos.Glare = a.Glare
	atmos.Haze = a.Haze

	local cc = ensureColorCorrection()
	cc.Enabled = true
	local corr = preset.ColorCorrection
	cc.Brightness = corr.Brightness
	cc.Contrast = corr.Contrast
	cc.Saturation = corr.Saturation
	cc.TintColor = corr.TintColor

	local bloom = ensureBloom()
	bloom.Enabled = true
	if preset.BloomIntensity then
		bloom.Intensity = preset.BloomIntensity
	end
end

function ArenaMood.applyForArena(arena: Instance?)
	if not arena then
		ArenaMood.apply("Lobby")
		return
	end
	local themeId = arena:GetAttribute(ThemeIds.ATTR_ARENA_THEME)
	if typeof(themeId) ~= "string" or themeId == "" then
		themeId = ThemeIds.arenaThemeFor(arena.Name)
	end
	ArenaMood.apply(themeId :: string)
end

function ArenaMood.applyLobby()
	ArenaMood.apply("Lobby")
end

return ArenaMood

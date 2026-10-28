-- Tag Rojo maps + assembled mechs; register collision groups (modern Streaming/Physics hooks).

local CollectionService = game:GetService("CollectionService")
local PhysicsService = game:GetService("PhysicsService")

local Tags = require(game.ReplicatedStorage.Shared.World.Tags)
local ThemeIds = require(game.ReplicatedStorage.Shared.Themes.ThemeIds)

local WorldBootstrap = {}

local GROUP_MECH = "AssemblerMech"
local taggedWorld = false
local physicsReady = false

local function tag(instance: Instance, tag: string)
	if not CollectionService:HasTag(instance, tag) then
		CollectionService:AddTag(instance, tag)
	end
end

function WorldBootstrap.ensurePhysics()
	if physicsReady then
		return
	end
	physicsReady = true
	pcall(function()
		PhysicsService:RegisterCollisionGroup(GROUP_MECH)
		-- Anchored preview mechs stay query-light; keep them from shoving characters if collide flips on.
		PhysicsService:CollisionGroupSetCollidable(GROUP_MECH, "Default", false)
		PhysicsService:CollisionGroupSetCollidable(GROUP_MECH, GROUP_MECH, false)
	end)
end

function WorldBootstrap.tagWorld(lobby: Instance?, arenasFolder: Instance?)
	WorldBootstrap.ensurePhysics()
	if taggedWorld then
		-- Re-tag is cheap if maps hot-reload under Rojo.
	end
	taggedWorld = true

	if lobby then
		tag(lobby, Tags.Lobby)
		local terminal = lobby:FindFirstChild("CampaignTerminal", true)
		if terminal then
			tag(terminal, Tags.CampaignTerminal)
		end
		local pedestal = lobby:FindFirstChild("GaragePedestal", true)
		if pedestal then
			tag(pedestal, Tags.GaragePedestal)
		end
		local crate = lobby:FindFirstChild("StarterCrate", true)
		if crate then
			tag(crate, Tags.StarterCrate)
		end
	end

	if arenasFolder then
		for _, arena in arenasFolder:GetChildren() do
			if arena:IsA("Model") then
				tag(arena, Tags.Arena)
				tag(arena, Tags.ArenaTheme)
				arena:SetAttribute("ArenaId", arena.Name)
				-- Prefer baked Rojo ThemeId; fall back to ThemeIds.arenaDefault.
				if arena:GetAttribute(ThemeIds.ATTR_ARENA_THEME) == nil then
					arena:SetAttribute(ThemeIds.ATTR_ARENA_THEME, ThemeIds.arenaThemeFor(arena.Name))
				end
				if arena:GetAttribute(ThemeIds.ATTR_MECH_LINE) == nil then
					arena:SetAttribute(ThemeIds.ATTR_MECH_LINE, ThemeIds.mechLineForArena(arena.Name))
				end
				local padA = arena:FindFirstChild("PadA", true)
				local padB = arena:FindFirstChild("PadB", true)
				local origin = arena:FindFirstChild("ArenaOrigin", true)
				if padA then
					tag(padA, Tags.PadA)
				end
				if padB then
					tag(padB, Tags.PadB)
				end
				if origin then
					tag(origin, Tags.ArenaOrigin)
				end
			end
		end
	end
end

function WorldBootstrap.tagMech(model: Model, isPreview: boolean?, themeLine: string?)
	WorldBootstrap.ensurePhysics()
	tag(model, Tags.Mech)
	tag(model, Tags.MechLine)
	if isPreview then
		tag(model, Tags.GaragePreview)
	end
	if themeLine then
		model:SetAttribute(ThemeIds.ATTR_MECH_LINE, themeLine)
	end
	pcall(function()
		model.ModelStreamingMode = Enum.ModelStreamingMode.Atomic
	end)
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") then
			pcall(function()
				d.CollisionGroup = GROUP_MECH
			end)
		end
	end
end

function WorldBootstrap.getTagged(tag: string): { Instance }
	return CollectionService:GetTagged(tag)
end

return WorldBootstrap

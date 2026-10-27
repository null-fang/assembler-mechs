-- Apply industrial texture pack onto authored kits.
-- Prefers rbxassetid from TextureIds; otherwise bakes embedded TexturePixels via EditableImage.

local AssetService = game:GetService("AssetService")
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local TextureIds = require(script.Parent.TextureIds)

local TextureApply = {}

local embedCache: { [string]: any } = {}
local warnedEmbed = false
local FACES = {
	Enum.NormalId.Front,
	Enum.NormalId.Back,
	Enum.NormalId.Left,
	Enum.NormalId.Right,
	Enum.NormalId.Top,
	Enum.NormalId.Bottom,
}

local RARITY_RANK = {
	Common = 0,
	Uncommon = 1,
	Rare = 2,
	Epic = 3,
	Legendary = 4,
	Mythic = 5,
	Blessed = 6,
	Relic = 6,
}

local function pixelsModule()
	local ok, mod = pcall(function()
		return require(script.Parent.TexturePixels)
	end)
	if ok then
		return mod
	end
	return nil
end

local function getTemplate(key: string): Texture?
	local assets = ReplicatedStorage:FindFirstChild("AssemblerAssets")
	if not assets then
		return nil
	end
	local folder = assets:FindFirstChild("Textures")
	if not folder then
		return nil
	end
	local t = folder:FindFirstChild(key)
	if t and t:IsA("Texture") then
		return t
	end
	return nil
end

local function bakeEmbed(key: string): any?
	if embedCache[key] ~= nil then
		return embedCache[key]
	end
	local pixels = pixelsModule()
	if not pixels or pixels[key] == nil then
		embedCache[key] = false
		return nil
	end
	local size = pixels.SIZE or 128
	local editable = nil
	local okImg = false
	okImg, editable = pcall(function()
		return (AssetService :: any):CreateEditableImage({ Size = Vector2.new(size, size) })
	end)
	if not okImg or editable == nil then
		okImg, editable = pcall(function()
			return (AssetService :: any):CreateEditableImageAsync(Vector2.new(size, size))
		end)
	end
	if not okImg or editable == nil then
		if not warnedEmbed then
			warnedEmbed = true
			warn("[Assembler] EditableImage bake unavailable; fill TextureIds rbxassetid after upload")
		end
		embedCache[key] = false
		return nil
	end
	local okDecode, raw = pcall(function()
		return HttpService:Base64Decode(pixels[key])
	end)
	if not okDecode or typeof(raw) ~= "string" then
		embedCache[key] = false
		return nil
	end
	local buf = buffer.fromstring(raw)
	local okWrite = pcall(function()
		editable:WritePixelsBuffer(Vector2.zero, Vector2.new(size, size), buf)
	end)
	if not okWrite then
		embedCache[key] = false
		return nil
	end
	embedCache[key] = editable
	return editable
end

local function clearOldTextures(part: BasePart)
	for _, ch in part:GetChildren() do
		if ch:IsA("Texture") and ch:GetAttribute("AssemblerTexture") == true then
			ch:Destroy()
		end
	end
end

local function stampTexture(part: BasePart, key: string, def: TextureIds.TextureDef, face: Enum.NormalId)
	local template = getTemplate(key)
	local tex: Texture
	if template then
		tex = template:Clone()
	else
		tex = Instance.new("Texture")
		tex.Name = key
	end
	tex.Face = face
	tex.StudsPerTileU = def.studsPerTile
	tex.StudsPerTileV = def.studsPerTile
	tex.Transparency = def.transparency
	tex:SetAttribute("AssemblerTexture", true)
	tex:SetAttribute("TextureRole", key)
	part:SetAttribute("AssemblerTextured", true)
	part:SetAttribute("TextureRole", key)

	local uri = TextureIds.contentUri(def)
	if uri then
		tex.Texture = uri
	else
		local editable = bakeEmbed(key)
		if editable then
			local okContent = pcall(function()
				(tex :: any).TextureContent = Content.fromObject(editable)
			end)
			if not okContent then
				-- Keep material-only look; template still documents the slot.
				tex.Transparency = 1
			end
		else
			tex.Transparency = 1
		end
	end
	tex.Parent = part
end

function TextureApply.roleFor(part: BasePart): string
	local attr = part:GetAttribute("TextureRole")
	if typeof(attr) == "string" and attr ~= "" and TextureIds.textures[attr] then
		return attr
	end
	return TextureIds.resolveRole(part.Name, part.Material.Name)
end

function TextureApply.applyPart(part: BasePart, rarity: string?)
	if part.Name == "Root" or part.Transparency >= 0.99 then
		return
	end
	local key = TextureApply.roleFor(part)
	local def = TextureIds.textures[key]
	if not def then
		return
	end
	if def.minRarity then
		local need = RARITY_RANK[def.minRarity] or 0
		local have = RARITY_RANK[rarity or "Common"] or 0
		if have < need and key == "emissive_strip" then
			-- Epic+ only for emissive; remap Neon accents below Epic to hazard
			key = "hazard_stripe"
			def = TextureIds.textures[key]
			if not def then
				return
			end
		end
	end
	clearOldTextures(part)
	-- Front + Top cover most kit silhouettes without 6x overdraw
	stampTexture(part, key, def, Enum.NormalId.Front)
	stampTexture(part, key, def, Enum.NormalId.Top)
	if key == "hazard_stripe" or key == "emissive_strip" then
		stampTexture(part, key, def, Enum.NormalId.Right)
	end
end

function TextureApply.applyModel(model: Model, rarity: string?)
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") then
			TextureApply.applyPart(d, rarity)
		end
	end
end

function TextureApply.preloadEmbeds()
	for _, key in TextureIds.keys do
		local def = TextureIds.textures[key]
		if def and (def.rbxassetid == nil or def.rbxassetid == "") then
			bakeEmbed(key)
		end
	end
end

-- silence unused FACES (kept for future full-wrap mode)
local _ = FACES

return TextureApply

-- Warm AssemblerAssets.Parts so garage pedestal / pads don't pop in late.
-- Uses ContentProvider:PreloadAsync (modern asset warm path).

local ContentProvider = game:GetService("ContentProvider")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local KitPreload = {}

local done = false

function KitPreload.run()
	if done then
		return
	end
	done = true

	local assets = ReplicatedStorage:FindFirstChild("AssemblerAssets")
	if not assets then
		return
	end
	local parts = assets:FindFirstChild("Parts")
	if not parts then
		return
	end

	-- Priority: starter loadout ids first, then a bounded batch of the rest.
	local priority = {
		"rusty_cage",
		"workboot_l",
		"workboot_r",
		"snap_arm",
		"rivet_gun",
		"brick_shoulder",
		"desk_brick",
		"scrap_cpu",
		"floor_bit",
		"thick_skin",
		"heat_sink_chip",
	}

	local queue: { Instance } = {}
	local seen: { [Instance]: boolean } = {}

	local function enqueue(inst: Instance?)
		if inst and not seen[inst] then
			seen[inst] = true
			table.insert(queue, inst)
		end
	end

	for _, id in priority do
		enqueue(parts:FindFirstChild(id))
	end

	local budget = 48
	for _, child in parts:GetChildren() do
		if #queue >= budget then
			break
		end
		enqueue(child)
	end

	if #queue == 0 then
		return
	end

	task.spawn(function()
		pcall(function()
			ContentProvider:PreloadAsync(queue)
		end)
		print(("[Assembler] Preloaded %d part kits"):format(#queue))
	end)
end

return KitPreload

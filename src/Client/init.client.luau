-- Assembler client — world-first HUD: campaign overlay + secondary garage.

local CombatHud = require(script:WaitForChild("CombatHud"))
local GarageHud = require(script:WaitForChild("GarageHud"))

CombatHud.mount(GarageHud)

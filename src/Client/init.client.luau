-- Assembler client — join HUD, lobby camera, campaign/garage modals, battle HUD.

local CombatHud = require(script:WaitForChild("CombatHud"))
local GarageHud = require(script:WaitForChild("GarageHud"))

CombatHud.mount(GarageHud)

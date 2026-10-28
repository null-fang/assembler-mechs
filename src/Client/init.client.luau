-- Assembler client — join HUD, lobby camera, campaign/garage modals, battle HUD.

local KitPreload = require(script:WaitForChild("KitPreload"))
local SessionBridge = require(script:WaitForChild("SessionBridge"))
local CombatHud = require(script:WaitForChild("CombatHud"))
local GarageHud = require(script:WaitForChild("GarageHud"))

KitPreload.run()
SessionBridge.start()
CombatHud.mount(GarageHud)

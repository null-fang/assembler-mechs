-- Assembler server entry (scaffold).
-- Campaign ladder + PvP matchmaking stubs load here; full combat later.

local Ladder = require(script.Campaign.Ladder)
local Matchmaking = require(script.PvP.Matchmaking)

local firstSlice = Ladder.buildFirstSlice()
print(("[Assembler] Campaign ladder ready: %d NPC fights (no bosses)"):format(#firstSlice))
print("[Assembler] PvP matchmaking stub loaded (not in first shippable slice)")

-- Keep refs so require graph stays live for Rojo sync / future wiring.
local _ = Matchmaking

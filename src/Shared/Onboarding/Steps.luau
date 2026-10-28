-- First-session soft prompts. Short, skippable, one job each.

export type StepId = "campaign" | "garage" | "crate"

export type StepDef = {
	id: StepId,
	title: string,
	body: string,
	hint: string, -- world / HUD nudge
}

local Steps = {}

Steps.ORDER = { "campaign", "garage", "crate" } :: { StepId }

Steps.DEFS = {
	campaign = {
		id = "campaign",
		title = "Campaign",
		body = "Walk to the cyan terminal. Open it.",
		hint = "Campaign terminal →",
	},
	garage = {
		id = "garage",
		title = "Garage",
		body = "Open the garage once. Peek your parts.",
		hint = "Garage pedestal →",
	},
	crate = {
		id = "crate",
		title = "Crate",
		body = "Open your starter crate. Keep one part.",
		hint = "Bay crate →",
	},
} :: { [StepId]: StepDef }

function Steps.get(id: StepId): StepDef
	return Steps.DEFS[id]
end

return Steps

-- Per-player first-session flags. In-memory for scaffold.

local Steps = require(game.ReplicatedStorage.Shared.Onboarding.Steps)

local OnboardingService = {}

export type Progress = {
	campaign: boolean,
	garage: boolean,
	crate: boolean,
	skipped: boolean,
}

local byUser: { [number]: Progress } = {}

local function fresh(): Progress
	return {
		campaign = false,
		garage = false,
		crate = false,
		skipped = false,
	}
end

function OnboardingService.get(userId: number): Progress
	local p = byUser[userId]
	if not p then
		p = fresh()
		byUser[userId] = p
	end
	return p
end

function OnboardingService.isDone(userId: number): boolean
	local p = OnboardingService.get(userId)
	if p.skipped then
		return true
	end
	return p.campaign and p.garage and p.crate
end

function OnboardingService.nextStep(userId: number): Steps.StepId?
	local p = OnboardingService.get(userId)
	if p.skipped then
		return nil
	end
	for _, id in Steps.ORDER do
		if not p[id] then
			return id
		end
	end
	return nil
end

function OnboardingService.complete(userId: number, stepId: string): Progress
	local p = OnboardingService.get(userId)
	if stepId == "skip" then
		p.skipped = true
		return p
	end
	if stepId == "campaign" or stepId == "garage" or stepId == "crate" then
		p[stepId] = true
	end
	return p
end

function OnboardingService.clientSnapshot(userId: number)
	local p = OnboardingService.get(userId)
	return {
		campaign = p.campaign,
		garage = p.garage,
		crate = p.crate,
		skipped = p.skipped,
		done = OnboardingService.isDone(userId),
		next = OnboardingService.nextStep(userId),
	}
end

return OnboardingService

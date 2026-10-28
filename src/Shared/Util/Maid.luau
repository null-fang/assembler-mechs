-- Tiny connection/instance maid (Trove-style). Prefer over leaked :Connect in long-lived scripts.

local Maid = {}
Maid.__index = Maid

export type Maid = typeof(setmetatable(
	{} :: {
		_tasks: { any },
	},
	Maid
))

function Maid.new(): Maid
	return setmetatable({
		_tasks = {},
	}, Maid)
end

function Maid:Give(task: any): any
	table.insert(self._tasks, task)
	return task
end

function Maid:Connect(signal: RBXScriptSignal, fn: (...any) -> ()): RBXScriptConnection
	local conn = signal:Connect(fn)
	self:Give(conn)
	return conn
end

function Maid:DoCleaning()
	local tasks = self._tasks
	self._tasks = {}
	for i = #tasks, 1, -1 do
		local t = tasks[i]
		local ty = typeof(t)
		if ty == "RBXScriptConnection" then
			(t :: RBXScriptConnection):Disconnect()
		elseif ty == "Instance" then
			(t :: Instance):Destroy()
		elseif ty == "function" then
			(t :: () -> ())()
		elseif ty == "table" and type((t :: any).Destroy) == "function" then
			(t :: any):Destroy()
		end
	end
end

function Maid:Destroy()
	self:DoCleaning()
end

return Maid

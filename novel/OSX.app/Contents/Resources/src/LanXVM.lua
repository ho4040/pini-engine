function print_r (t, name, indent)
	local tableList = {}
	function table_r (t, name, indent, full)
		local id = not full and name
				or type(name)~="number" and tostring(name) or '['..name..']'
		local tag = indent .. id .. ' = '
		local out = {}	-- result
		if type(t) == "table" then
			if tableList[t] ~= nil then table.insert(out, tag .. '{} -- ' .. tableList[t] .. ' (self reference)')
			else
				tableList[t]= full and (full .. '.' .. id) or id
				if next(t) then -- Table not empty
					table.insert(out, tag .. '{')
					for key,value in pairs(t) do 
						table.insert(out,table_r(value,key,indent .. '|	',tableList[t]))
					end 
					table.insert(out,indent .. '}')
				else table.insert(out,tag .. '{}') end
			end
		else 
			local val = type(t)~="number" and type(t)~="boolean" and '"'..tostring(t)..'"' or tostring(t)
			table.insert(out, tag .. val)
		end
		return table.concat(out, '\n')
	end
	return table_r(t,name or 'Value',indent or '')
end

local LanXVM = {}
LanXVM.commands = {
	t_function=function(vm,arg)
		local f = vm.customfunc[arg["name"]]
		if f then
			vm:call(arg["name"])
			vm:doNext()
		else
			f = vm.luafunc[arg["name"]]
			if f then
				f(vm,arg)
			else
				--print("CAN NOT FIND FUNCTION == ("..arg["name"]..")")
				vm:doNext()
			end
		end
	end,
	t_registcommand = function(vm,arg)
		vm:registCommand(arg["name"],arg["func"])
		vm:doNext()
	end,
	t_registfunc = function(vm,arg)
		vm:registFunc(arg["name"],arg["func"], arg["custom"])
		vm:doNext()
	end,
	t_operate = function(vm,arg)
		local o = arg["op"]
		local L = arg["L"]["v"]
		local R = arg["R"]["v"]
		if arg["L"]["type"] == "id" then L=vm.variable[arg["L"]["v"]] end
		if arg["R"]["type"] == "id" then R=vm.variable[arg["R"]["v"]] end

		if L == nil then L =0 end
		if R == nil then R =0 end

		    if o == "+" then vm.variable[arg["A"]] = L + R 
		elseif o == "*" then vm.variable[arg["A"]] = L * R 
		elseif o == "/" then if R == 0 then R=1 end vm.variable[arg["A"]] = L / R 
		elseif o == "-" then vm.variable[arg["A"]] = L - R end
		
		vm:doNext()
	end,
	t_bookmark=function(vm,arg)
		vm:doNext()
	end,
	t_goto = function(vm,arg)
		if vm.unuse_goto then
			vm:doNext()
			return 
		end

		local name = arg["v"]
		print( name )
		vm:GotoBookmark(name)
		vm:doNext()
	end,
	t_assign=function(vm,arg)
		if arg["value"]["type"] == "id" then
			vm.variable[arg["id"]] = vm.variable[arg["value"]["v"]]
		elseif arg["value"]["type"] == "function" then
			self.registFunc(arg["id"],arg["value"]["v"],true)
		else
			vm.variable[arg["id"]] = arg["value"]["v"]
		end
		vm:doNext()
	end
}

function LanXVM:init()
	if self.require then 
		for k,v in pairs(self.require) do
			package.loaded[k] = nil
		end
		for k,v in pairs(self.module) do
			package.loaded[k] = nil
		end
	end
	
	self.variable = {}
	self.stack = {}
	self.bookmark = {}
	self.callstack = nil
	self.luafunc = {}
	self.customfunc = {}
	self.require = {}
	self.module = {}
	self.running = false
	self.next = false
	self.defaultStack = "global"
	self:call(self.defaultStack)
	self:defaultFunction()
end

function LanXVM:defaultFunction()
	self:registFunc("스크립트",function(vm,arg)
		local t = vm.variable["스크립트.파일명"] or nil
		local beforeStack = vm.defaultStack;
		vm.defaultStack = t
		
		local path = t:gsub(".scene","")
		if self.require[path] == nil then
			self.require[path] = require(path)
		end
		self.require[path](vm)

		vm.defaultStack = beforeStack
		vm:call(t)

		vm:doNext()
	end)
	self:registFunc("루아",function(vm,arg)
		local t = vm.variable["루아.모듈명"] or nil
		local path = "module/"..t
		if self.module[path] == nil then
			self.module[path] = require(path)
		end
		self.module[path](vm)
	end)
end

function LanXVM:clearFunction(name)
	self.stack[name] = {}
end

function LanXVM:registCommand(i,f)
	self.commands[i] = f
end

function LanXVM:registFunc(i,f,a)
	if a then
		self.customfunc[i] = true
		f(self)
	else
		self.luafunc[i] = f
	end
end

function LanXVM:pushCmd(cmd,arg,stackName)
	if stackName == nil then stackName = self.defaultStack end
	if self.stack[stackName] == nil then
		self.stack[stackName] = {}
	end

	if self.commands[cmd] == self.commands.t_bookmark then
		self.bookmark[arg["v"]] = {
			stackName,
			#self.stack[stackName]
		}
	end

	table.insert(self.stack[stackName],{self.commands[cmd],arg})
end

function LanXVM:GotoBookmark(bm)
	local b = self.bookmark[bm]
	if b then
		if self.callstack.name ~= b[1] then
			self:call(b[1])
		end
		self.callstack.curLine = b[2]
	end
end

function LanXVM:CallStackDepth(stack)
	local c=1
	local s=nil
	if stack.stack then 
		b,s = self:CallStackDepth(stack.stack)
		c=c+b
	else
		s=stack
	end
	return c,s
end

function LanXVM:call(stackName)
	self.callstack = {
		curLine = 0,
		name = stackName,
		stack = self.callstack
	}
	c,s = self:CallStackDepth(self.callstack)
	if c > 100 then
		self.callstack = s
		print("callstack overflow!")
	end
end

function LanXVM:_return()
	if self.callstack.stack == nil then
		return false
	end
	self.callstack = self.callstack.stack
	self.callstack.curLine = self.callstack.curLine
	return true
end

function LanXVM:runCommand()
	if self.stack[self.callstack.name] == nil then
		return 
	end
	self.running = true
	while true do
		self.callstack.curLine = self.callstack.curLine+1
		if #self.stack[self.callstack.name] < self.callstack.curLine then
			if self:_return() == false then -- global stack end
				if self.eventCallback then 
					self.eventCallback("FIN")
				end
				return 
			end
			self:runCommand()
			return 
		end

		self.next = false

		--print("name:"..self.callstack.name.." ("..self.callstack.curLine.."/"..#self.stack[self.callstack.name]..")")
		local v = self.stack[self.callstack.name][self.callstack.curLine]
		v[1](self,v[2])
		if self.next == false then
			break
		end
	end
	self.running = false
end

function LanXVM:doNext()
	if self.running then
		self.next = true
	else
		self:runCommand()
	end
end

function LanXVM:registEvent(func)
	self.eventCallback = func
end

function LanXVM:showValues()
	print(print_r(self.variable))
end

function LanXVM:showCommands()
	print(print_r(self.commands))
end

function LanXVM:showCurrentStack()
	print("==============================")
	print("StackName : "..self.callstack.name)
	print("==============================")
	print(print_r(self.stack[self.callstack.name]))
end

function LanXVM:showCallStack()
	print(print_r(self.callstack))
end
return LanXVM
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

LXVM = {
	loops = {};
}

local stringmeta = getmetatable("")
stringmeta.__add = function(op1,op2) return op1..op2 end
stringmeta.__div = function(op1,op2) return op1 end
stringmeta.__mul = function(op1,op2) return op1 end
stringmeta.__sub = function(op1,op2) return op1 end

function LXVM:init()
	_LNXF = {} -- functions
	_LNXB = {} -- bookmarks
	_LNXVT = {{}, {}} -- varable triggers

	if _LNXG then
		local nextLNXGP = {}

		for k,v in pairs(_LNXGP) do
			if string.sub(k,1,1) == "$" then
				nextLNXGP[k] = v
			end
		end

		_LNXGP = nextLNXGP -- proxy for variables; keep save-variables
		_LNXG = {} -- keep null table
	else
		_LNXGP = {} -- proxy for variables
		_LNXG = {} -- variables
	end

	local mt = {
		__index = function (t,k)
			return _LNXGP[k] or _LNXGP["___"..k]
		end,

		__newindex = function (t,k,v)
			if _LNXVT[2][k] ~= nil then
				if _LNXGP[k] ~= v then
					for i=1,#_LNXVT[2][k] do
						_LNXVT[2][k][i][2]()
					end
				end
			end
			
			_LNXGP[k] = v
		end
	}

	-- hard coded function
	_LNXB['스크립트']={}
	_LNXF['스크립트'] = function() return {
	{
		t=5,
		pre =
		{
			function(vm,idx,rets,fcall)
				local fname = vm:ARGU("스크립트","파일명","")
				local run = vm:ARGU("스크립트", "실행", "예") == "예"

				LXVM:OpenLNX(fname)

				if fcall then
					if fcall[6] then
						fname = fcall[6]
						run = true
						LXVM:OpenLNX(fname)
					else
						fname = nil
						run = false
					end
				end

				if run then
					return _VM_LOOP_(fname,_LNXF[fname],idx,nil,nil,nil,rets,fcall)
				end
			end
		},
		f=function(vm,idx) end},
	} end
	setmetatable(_LNXG, mt)
end

function LXVM:_return()
	self.currentLoop[6] = true
end

function LXVM:ARGU(fname,arg,default)
	return _LNXG[fname.."."..arg] or _LNXG["___"..fname.."."..arg] or default
end

ONLY_PREVIEW_NO_MACRO_ERR = ""
if not OnPreview then
	ONLY_PREVIEW_NO_MACRO_ERR = [[
		print ("매크로가 존재하지 않습니다..."..fname)
	]]
end

ONLY_PREVIEW_CODE = ""
if OnPreview then
	ONLY_PREVIEW_CODE = [[
	if stckInfo[5] then
		if string.sub(stckInfo[5],1,1) ~= "%" then
			stckInfo[5] = nil
		end
	end
	stckInfo[8] = nil
]]
end

function LXVM:PRE_LOOP(stckInfo,pres,forceCall,f)
	local rets = {}

	local pi = 1

	if forceCall then
		pi = forceCall[3]
		rets = forceCall[5]
		stckInfo[9][5] = rets

		forceCall = forceCall[1]
	end

	if pres then
		while pi <= #pres do
			stckInfo[9][3] = pi
			rets[pi] = pres[pi](LXVM,stckInfo,rets,forceCall)
			stckInfo[9][5][pi] = rets[pi]
			pi = pi + 1
		end
	end

	stckInfo[9][2] = stckInfo[9][2] + 1
	stckInfo[9][3] = 1

	try{
		function()
			f(rets)
		end,
		catch {
		function(error)
			print(error)
		end
		}
	}	
end

tabb = ""
_VM_LOOP_ =
loadstring([[return
function (fname,fns,stckInfo,new_arg,del_arg,start_i,rets,scall)
	if fns == nil then
		]]..ONLY_PREVIEW_NO_MACRO_ERR..[[
		return 0
	end
	local LXVM = LXVM
	local nscall = nil
	if (not scall) and new_arg then
		rets = rets or {}
		new_arg(rets)
	end

	-- print ("_VM_LOOP_ begin. fname="..fname)
	-- print ("_loopidx="..tostring(LXVM:currentLoopIdx()))

	--tabb = tabb.."\t"

	fns = fns()
	local fns_max = #fns
	local i=1
	if start_i then
		i = start_i
	elseif scall then
		i = scall[2]
	end

	stckInfo[9] = {
		stckInfo[9], -- before stack [1]
		i, -- i [2]
		1, -- pi [3]
		false, -- ispause [4]
		{}, -- rets [5]
		fname, -- scriptName [6]
	}

	if scall and scall[1] == nil then
		stckInfo[2] = false
	end

	while true do
		]]+ONLY_PREVIEW_CODE+[[
		-- vm force return
		-- print ("fname="..fname..", i="..tostring(i)..", stck="..tostring(LXVM:currentLoopIdx()))

		if stckInfo[6] == true then
			-- print ("vm force return; fname="..fname)
			stckInfo[6] = false
			break
		end

		-- vm pause
		if stckInfo[2] == false then
			stckInfo[9][4] = true
			-- print ("vm pause; fname="..fname)
			coroutine.yield()
			-- print ("vm resume; fname="..fname)
			stckInfo[9][4] = false
		end

		-- bookmark
		local bmk = stckInfo[5]
		if bmk then 
			stckInfo[5] = nil
			local t = _LNXB[fname][bmk]
			if t then
				i = t
				stckInfo[9][2] = i 
			else
				for k,b in pairs(_LNXB)do
					local bb = b[bmk]
					if bb then
						local pi = bb

						local forceCall = nscall

						if forceCall then
							pi = nil

							forceCall = forceCall[1]
						end	

						stckInfo[9][2] = i - 1
						_VM_LOOP_(k,_LNXF[k],stckInfo,nil,nil,pi,rets,forceCall)
						stckInfo[9][2] = i + 1
						break
					end
				end
			end
		end

		-- hyper goto
		if stckInfo[8] then
			-- print ("vm hypergoto exit; fname="..fname)
			break
		end

		-- cmd
		local v = fns[i]
		if v == nil then
			-- print ("vm no more commands; fname="..fname)
			break
		end

		local t = v["t"]
		--print(tabb..fname.." : "..i.."("..t..")")
		if t == 1 or t == 5 then
			LXVM:PRE_LOOP(stckInfo,v["pre"], scall, function(rets)
				v["f"](LXVM,stckInfo,rets)
			end)

		elseif t == 12 or t == 13 then
			v["f"](LXVM,stckInfo)
		
		elseif t == 2 then --ifgoto
			LXVM:PRE_LOOP(stckInfo,v["pre"], scall, function(rets)
				local ifgoto_ = v["test"](LXVM,stckInfo,rets)
				if ifgoto_ == false then
					stckInfo[5] = v["else"]
				end
			end)

		elseif t == 4 then -- goto
			stckInfo[5] = v["n"]

		elseif t == 7 then -- return
			LXVM:PRE_LOOP(stckInfo,v["pre"], scall, function(rets)
				LXVM:returnValue(v["f"](LXVM,stckInfo,rets))
			end)

			-- print ("vm normal return; fname="..fname)
			break
		
		elseif t == 11 then -- hyper-goto
			stckInfo[8] = v["n"]
		end
		i = i+1

		nscall = scall
		scall = nil
		stckInfo[9][2] = i 
	end
	if del_arg then
		del_arg()
	end

	--tabb = string.sub(tabb,0,-2)
	
	local ret = LXVM.currentLoop[7]
	LXVM.currentLoop[7] = 0
	stckInfo[9] = stckInfo[9][1]

	-- print ("_VM_LOOP_ end. fname="..fname)

	return ret,stckInfo
end
]])()

function LXVM:currentLoopIdx()
	for k,v in ipairs(self.loops) do
		if v == self.currentLoop then
			return k
		end
	end
end

function LXVM:removeLoop(infotable)
	for k,v in ipairs(self.loops) do
		if v == infotable then
			self.loops[k][10] = false

			if k == #self.loops then
				local i = k
				while i >= 1 and (not self.loops[i][10]) do
					self.loops[i] = nil
					i = i - 1
				end
			end
		end
	end
end

function LXVM:resumeAndGoBookmark(idx,bmk)
	if (not self.loops[idx][10]) then
		-- print ("______resume, dead resume founded. skip it.")
		return
	end

	self.currentLoop = self.loops[idx]
	self:GotoBookmark(bmk)
end

function LXVM:GotoBookmark(bmk)
	self.currentLoop[5] = bmk
	if self.currentLoop[2] == false then
		self:resume(self:currentLoopIdx())
	end
end

function LXVM:OpenLNX(file)
	-- print ("OpenLNX() called. file="..file)
	local fname = FILES["module/"..file]
	if fname == nil then
		fname = FILES["scene/"..file]
		if fname == nil then
			fname = file
		end
	end
	if fname ~= file then
		fname = string.sub(fname,0,-5)
	end
	try{
		function()
			require(fname)(file)
		end,
		catch {
		function(error)
			print(error)
		end
		}
	}
end

function LXVM:resume(idx)
	if (not self.loops[idx]) then
		return
	elseif (not self.loops[idx][10]) then
		return
	end

	self.currentLoop = self.loops[idx]
	self.currentLoop[2] = true
	
	local r1,r2,r3 = coroutine.resume(self.currentLoop[1])
	if r3 then
		local hyper = r3[8]
		LXVM:removeLoop(r3)
		if hyper and type(hyper) == "string" then
			LXVM:GotoBookmarkNewCall(hyper)
		end
	end
	if r1 == false then
		print (r2)
	end
end

function LXVM:stop()
	self.currentLoop[2] = false
	return self:currentLoopIdx();
end

function LXVM:sleep(time)
	if time <= 0 then
		time = 0.001
	end
	
	self.currentLoop[2] = false
	self.currentLoop[3] = time
end

function LXVM:update(dt)
	for k,v in ipairs(self.loops) do 
		if v[2] == false and v[3] > 0 then 
			v[3] = v[3] - dt
			if v[3]<=0 then
				v[3] = 0
				LXVM:resume(k)
			end
		end
	end
end

function LXVM:returnValue(ret)
	self.currentLoop[7] = ret
end

function LXVM:returnValueOnThread(ret,idx)
	self.loops[idx][7] = ret
end

function LXVM:GotoBookmarkNewCall(bmk)
	local start_i = 1
	local stackName = self.currentLoop[4]
	if bmk then
		local t = nil
		if _LNXB[stackName] then
			t = _LNXB[stackName][bmk]
		end
		if t then
			start_i = t 
		else
			for k,b in pairs(_LNXB)do
				local bb = b[bmk]
				if bb then
					stackName = k
					start_i = bb
					break
				end
			end
		end
	end

	LXVM:call(stackName,start_i)
end

function LXVM:call(stckName, start_i, fcall)
	if _LNXF == nil or _LNXF[stckName] == nil then
		self:OpenLNX(stckName)
		if _LNXF == nil or _LNXF[stckName] == nil then
			return 
		end
	end

	start_i = start_i or 1

	self.currentLoop = {
		coroutine.create(_VM_LOOP_), -- 코루틴 객체 [1]
		true, -- stop인지 아닌지 [2]
		0, -- sleep 시간 [3]
		stckName, -- 스택 이름 [4]
		nil, -- gotobookmark [5]
		false, -- force return flag [6]
		0, -- return value [7]
		nil, -- hyper goto [8]
		{["begin"]=stckName}, -- virtual stack [9]
		true, -- isAlive [10]
	}
	table.insert(self.loops,self.currentLoop)
	local r1,r2,r3 = coroutine.resume(
		self.currentLoop[1],
		stckName,
		_LNXF[stckName],
		self.loops[#self.loops],
		nil, -- new_arg
		nil, -- del_arg
		start_i,
		nil, -- rets
		fcall -- fcall
	)
	if r3 then
		local hyper = r3[8]
		LXVM:removeLoop(r3)
		if hyper and type(hyper) == "string" then
			LXVM:GotoBookmarkNewCall(hyper)
		end
	end
	if r1 == false then
		print (r2)
	end
end

function LXVM:VarFlush()
end

function LXVM:VarSave()
end

function LXVM:registVariableTrigger(id,varName,func)
	LXVM:unregistVariableTrigger(id)

	_LNXVT[1][id] = varName
	_LNXVT[2][varName] = _LNXVT[2][varName] or {}

	table.insert(_LNXVT[2][varName],{
		id, -- [1]
		func
	})
end

function LXVM:unregistVariableTrigger(id)
	_LNXVT[1] = _LNXVT[1] or {}
	_LNXVT[2] = _LNXVT[2] or {}

	if _LNXVT[1][id] ~= nil then
		varName = _LNXVT[1][id]
		_LNXVT[1][id] = nil

		for i=1,#_LNXVT[2][varName] do
			if _LNXVT[2][varName][i][1] == id then
				table.remove(_LNXVT[2][varName], i)
				break
			end
		end
	end
end

function LXVM:getState()
	local ret = {}
	local stckTransTable = {}
	ret["vg"] = {} -- 변수
	ret["loops"] = {} -- 루프들
	ret["fns"] = {} -- 매크로
	ret["bm"] = {} -- 북마크
	ret["vtg"] = {} -- 변수 트리거

	-- 저장변수는 저장하지 않습니다
	for k,v in pairs(_LNXGP) do
		if string.sub(k,1,1) ~= "$" then
			ret["vg"][k] = v
		end
	end

	for k,v in pairs(_LNXF) do
		ret["fns"][k] = string.dump(v)
	end

	for k,v in pairs(_LNXB) do
		ret["bm"][k] = v
	end

	for k,v in pairs(_LNXVT[2]) do
		for i,f in ipairs(v) do
			ret["vtg"][f[1]] = {f[1], k, string.dump(f[2])}
		end
	end

	for i,v in ipairs(self.loops) do
		if v[10] then
			table.insert(ret["loops"], {v[9], v[2]})
			table.insert(stckTransTable, #ret["loops"])
		else
			table.insert(stckTransTable, -1)
		end
	end

	return ret, stckTransTable
end

function LXVM:setState(state, targetStck1, targetStck2)

	local retTarget1 = -1
	local retTarget2 = -1

	-- print ""
	-- print ("(Before original loop shutout)")
	for k,v in pairs(self.loops) do
		v[8] = {}
		self:resume(k)
	end
	-- print ("(After original loop shutout)")
	-- print ""

	for k,v in pairs(state["vg"]) do
		if string.sub(k,1,1) ~= "$" then
			_LNXG[k] = v
		end
	end

	for k,v in pairs(state["fns"]) do
		_LNXF[k] = loadstring(v)
	end

	for k,v in pairs(state["bm"]) do
		_LNXB[k] = v
	end

	for k,v in pairs(state["vtg"]) do
		self:registVariableTrigger(v[1], v[2], loadstring(v[3]))
	end

	for i,v in ipairs(state["loops"]) do
		-- print ("____________LOOPSPLIT____________")
		local target = v[1]

		local forceCallStack = nil

		local z = target
		local begin = nil

		while z ~= nil do
			forceCallStack = {
				forceCallStack,
				z[2],
				z[3],
				z[4],
				z[5],
				z[6]
			}

			if z["begin"] ~= nil then
				begin = z["begin"]
			end

			z = z[1]
		end

		if forceCallStack[2] == nil then
			forceCallStack = forceCallStack[1]
		end
		
		self:call(begin, forceCallStack[2], forceCallStack)

		if v[2] then
			self:resume(self:currentLoopIdx())
		end

		if i == targetStck1 then
			retTarget1 = self:currentLoopIdx()
		end
		if i == targetStck2 then
			retTarget2 = self:currentLoopIdx()
		end
	end
	-- print ("____________LOOPSPLIT____________")

	return retTarget1, retTarget2
end

function LXVM:Awake()
	print "LanXVM:Awake() called"
	if LXVM.isAwakeUp == nil then
		LXVM.isAwakeUp = true
		if OnPreview then
		else
			local flushTime = 0;
			_G.__VM_TIMER__ = function(dt)
				LXVM:update(dt)
				flushTime = flushTime + dt;
				if flushTime > 1 then
					LXVM.VarFlush()
					flushTime = 0;
				end
			end
			SCHEDULER = cc.Director:getInstance():getScheduler()
			SCHEDULER:scheduleScriptFunc(_G.__VM_TIMER__, 0, false)
		end
	end
end

return LXVM
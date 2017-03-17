require "Cocos2d"
require "Cocos2dConstants"

cclog = function(...)
	print(string.format(...))
end

-- for CCLuaEngine traceback
function __G__TRACKBACK__(msg)
	cclog("----------------------------------------")
	cclog("LUA ERROR: " .. tostring(msg) .. "\n")
	cclog(debug.traceback())
	cclog("----------------------------------------")
	return msg
end

function InitCocos2d(width,height)

	local director = cc.Director:getInstance()
	local glview = director:getOpenGLView()
	if nil == glview then
		glview = cc.GLView:createWithRect("VisualNovel", cc.rect(0,0,width,height))
		director:setOpenGLView(glview)
	end
	
	glview:setDesignResolutionSize(width,height, cc.ResolutionPolicy.NO_BORDER)
	director:setDisplayStats(true)
	director:setAnimationInterval(1.0 / 60)
end

local function main()
	collectgarbage("collect")
	collectgarbage("setpause", 100)
	collectgarbage("setstepmul", 5000)

	cc.FileUtils:getInstance():addSearchPath("src")
	cc.FileUtils:getInstance():addSearchPath("res")
	cc.FileUtils:getInstance():addSearchPath(cc.FileUtils:getInstance():getWritablePath())

    local JSON = require("JSON")

	local ROOT_PATH = cc.FileUtils:getInstance():getWritablePath()

	local proj = require("ProjectInfo")
	InitCocos2d(proj.width,proj.height)
	
	function LanX_start()
		XVM = require("LanXVM")
		XVM:init()
		require("EmulateVM")(XVM)

		require("__Main__")(XVM)

		XVM:runCommand()
	end


	co = coroutine.create(
	function ()
		print("init sockets")
		local socket = require("socket")
		function newset()
			local reverse = {}
			local set = {}
			return setmetatable(set, {__index = {
				insert = function(set, value)
					if not reverse[value] then
						table.insert(set, value)
						reverse[value] = #set
					end
				end,
				remove = function(set, value)
					local index = reverse[value]
					if index then
						reverse[value] = nil
						local top = table.remove(set)
						if top ~= value then
							reverse[top] = index
							set[index] = top
						end
					end
				end,
				find = function(set,value)
					local index = reverse[value]
					return index
				end
			}})
		end

		set = newset()

		local server = assert(socket.bind("*", 45674))
		local ip, port = server:getsockname()
		local clients = {}

		local function recv(socket,size)
			data, error = socket:receive(size)
			if error then
				print("RECV ERROR : "..error)
			end
			return data
		end
		set:insert(server)
		while 1 do
			print("Waiting...")
			local readable, _, error = socket.select(set, nil,0.5)
			for _, input in ipairs(readable) do
				if input == server then 
					local new = input:accept()
					if new then
						new:settimeout(3)
						set:insert(new)

						clients[set:find(new)] = 0
					else
					end
				else
					local line, error;
					local idx = set:find(input)

					print(">>",idx,clients[idx])
					if clients[idx] == 0 then
						header = recv(input,4)
						size = recv(input,11)
						
						size = tonumber(size)
						clients[idx] = {header,size,0}
					else 
						order = clients[idx][1]
						if order == "tran" then
							fileName = recv(input,255)
							fileData = recv(input,clients[idx][2]-255)


							print (ROOT_PATH..fileName)
							local out = io.open(ROOT_PATH..fileName, "wb")
							local t = {}
							out:write(fileData)
							out:close()

							clients[idx] = 0

						elseif order == "flst" then
							payload = recv(input,clients[idx][2])

							local fileList = JSON:decode(payload)
							for k,v in pairs(fileList)do
								print(k.."//"..v)
							end
							
							clients[idx] = 0
						end
					end

					if error then
						print("Removing client from set\n")
						clients[idx] = 0
						input:close()
						set:remove(input)
					else
						--[[
						print("recved '", #line)
						
						local out = io.open(idx.."_"..#line..".txt", "wb")
						local t = {}
						out:write(line)
						out:close()

						print("Broadcasting line '", line, "'\n")
						writable, error = socket.skip(1, socket.select(nil, set, 1))
						if not error then
							for __, output in ipairs(writable) do
								if output ~= input then
									print(">>>>"..line)
									output:send(line .. "\n")
								end
							end
						else print("No client ready to receive!!!\n") end
						]]
					end
				end
			end
			coroutine.yield()
		end
	end)

	local function networkUpdate()
		coroutine.resume(co)
	end
	
	local scheduler = cc.Director:getInstance():getScheduler()
	schedulerEntry = scheduler:scheduleScriptFunc(networkUpdate, 0, false)

end

local status, msg = xpcall(main, __G__TRACKBACK__)
if not status then
	error(msg)
end
--{nodes = {{frames = {{{0,1.0},{1,2.0},{2,3.0},{3,4.0},{4,10.0}},{{0,10.9},{1,13.0},{2,2.8}},{{0,20.8},{1,24.0},{2,2.6}},{{0,30.7},{1,35.0},{2,2.4}},{{0,40.6},{1,46.0},{2,2.2}},{{0,50.5},{1,57.0},{2,2.0}},{{0,60.4},{1,68.0},{2,1.8}},{{0,70.3},{1,79.0},{2,1.6}},{{0,80.2},{1,90.0},{2,1.4}},{{0,90.1},{1,101.0},{2,1.2}},{{0,100.0},{1,112.0},{2,1.0}},{{0,92.0},{1,123.0}},{{0,84.0},{1,134.0}},{{0,76.0},{1,145.0}},{{0,68.0},{1,156.0}},{{0,60.0},{1,167.0}},{{0,52.0},{1,178.0}},{{0,44.0},{1,189.0}},{{0,36.0},{1,200.0}},{{0,28.0},{1,211.0}}},type = "atl_node",idx = 1.0}},t = 10,name = "내애니메이션"}
require("PiniAPI")

local AnimMgr = {
}

if OnPreview then
else
	local Utils = require("plua.utils")
	function FAL_REGIST(json)
		return Utils.FAL_registAnimation(json)
	end
	function FAL_GETFRAME(idx,node,frame,nodename,hash)
		return Utils.FAL_getFrame(idx,node,frame,nodename,hash)
	end
	function FAL_GETVALUE(frame,key)
		return Utils.FAL_getNumberVal(frame,key)
	end
	function FAL_GETSTRVALUE(frame,key)
		return Utils.FAL_getStringVal(frame,key)
	end
	function FAL_ISVALUE(frame,key)
		return Utils.FAL_isValue(frame,key)
	end
	function FAL_DELETEFRAME(frame)
		return Utils.FAL_deleteFrame(frame)
	end
	function FAL_MAXFRAME(idx,node)
		return Utils.FAL_getMaxFrame(idx,node)
	end
	function FAL_ISEXISTS(idx)
		return Utils.FAL_isExists(idx)
	end
	function FAL_NUMNODE(idx)
		return Utils.FAL_numNode(idx)
	end
	function FAL_REGISTSTRINGVALUE(node,idx,value)
		return Utils.FAL_registStringValue(node,idx,value)
	end
	function FAL_REGISTNUMBERVALUE(node,idx,value)
		return Utils.FAL_registNumberValue(node,idx,value)
	end
	function FAL_DELETENODEVALUE(node)
		return Utils.FAL_deleteNodeValue(node)
	end
	function FAL_CLEARFRAME()
		return Utils.FAL_clearFrame()
	end
end

--[[
"위치X",  0
"위치Y",  1
"크기X",  2 
"크기Y",  3
"회전",   4
"색상R",  5
"색상G",  6 
"색상B",  7
"색상A",  8
"매크로", 9
"루아",   10
"이미지", 11
]]

function AnimMgr:init(xvm)
	self.XVM = xvm
end

function AnimMgr:clear()
	--self.anims={} 
end

function AnimMgr:registAnimation(animation)
	FAL_REGIST(animation["json"])
end

function AnimMgr:interpolation(t,o1,o2)
	return ( 1 - t )*o1 + t*o2,2
end

AnimMgr.animUpdate = function(t)
	if AnimMgr == nil then 
		AnimMgr = _G.AnimMgr
	end

	local per = 1
	local delta = t.userdata.delta
	local curFrame = t.userdata.curFrame
	local loopCnt = t.userdata.loopCnt
	local dt = t.userdata.dt
	local i = t.userdata.i
	local max = t.userdata.max
	local node = pini:FindNode(t.userdata.nodeId)
	local default = t.userdata.default
	local name = t.userdata.name
	local args = t.userdata.args
	local isSkipCurrentFrame = false

	if node == nil then
		FAL_DELETENODEVALUE(t.userdata.nodeId)
		t:stop()
		return 
	end

	delta = delta + t.dt
	if dt ~= 0 then
		per = delta / dt
		if per > 1 then per = 1 end
	end

	AnimMgr:adjustFrame(name,i,curFrame,per,node,default,args,false)

	if delta >= dt then
		AnimMgr:adjustFrame(name,i,curFrame,1,node,default,args,true)
		delta = delta - dt
		curFrame = curFrame+1
		if curFrame >= max then
			if loopCnt then
				loopCnt = loopCnt - 1
				if loopCnt <= 0 then
					FAL_DELETENODEVALUE(t.userdata.nodeId)
					t:stop()

					if t.userdata.callback then
						t.userdata.callback()
					end

					return
				else
					isSkipCurrentFrame = true
				end
			else
				isSkipCurrentFrame = true
			end
			curFrame = 0
			delta = 0
			AnimMgr:adjustFrame(name,i,max,1,node,default,args,true)
		end
	end

	t.userdata.delta = delta
	t.userdata.curFrame = curFrame
	t.userdata.loopCnt = loopCnt

	if isSkipCurrentFrame then
		t.userdata.delta = t.userdata.delta + dt
		AnimMgr.animUpdate(t)
	end
end


function AnimMgr:run(name,i,start,_end,dt,loopCnt,node,args,callback)
	-- name : idx
	-- i : key
	if node then
		x,y = node:position()
		local default = {
			x = x,
			y = y
		}

		local max
		if _end == nil then
			max = FAL_MAXFRAME(name,i)
		else
			max = _end
		end
		if OnPreview then
			local frames = FAL_MARKEDFRAMES(name,i);
			AnimMgr:adjustFrame(name,i,start,1,node,default,args,false)
			for k,v in python.enumerate(frames) do
				if v > start then
					AnimMgr:adjustFrame(name,i,v,1,node,default,args,false)
				end
			end
			FAL_DELETENODEVALUE(node.id)
		else
			local userdata = {
				curFrame=start,
				delta=0,
				dt=dt,
				i=i,
				max=max,
				nodeId=node.id,
				default=default,
				loopCnt=loopCnt,
				name = name,
				args = args,
				callback = callback
			}

			local timer = pini:FindTimer(node.id.."_ATL_TIMER")
			if timer then
				timer:stop();
			end

			AnimMgr.animUpdate({dt=0,userdata=userdata})
			pini.Timer(node.id.."_ATL_TIMER",0,AnimMgr.animUpdate,true,nil,userdata):run()
			node:registOnExit("PINI_ANIM_MGR",function(n)
				local timer = pini:FindTimer(n.id.."_ATL_TIMER")
				if timer then
					FAL_DELETENODEVALUE(n.id)
					timer:stop()
				end
			end)
		end
	end
end

function AnimMgr:adjustFrame(idx,key,fn,persent,node,default,args,justInterval)
	-- idx = animation name
	-- key = node number 
	if node.isDestroyed then
		return 
	end

	local propMax = 11
	if justInterval == true then
		propMax = propMax-3
	end

	local fd1 = FAL_GETFRAME(idx,key,fn-1,node.id,args)
	local fd2 = FAL_GETFRAME(idx,key,fn,node.id,args)
	for i=0,propMax,1 do
		if FAL_ISVALUE(fd2,i) then 
			local value = nil
			local values = nil
			local valuel = nil
			if i < 9 then
				local value2, value2s, value2l = FAL_GETVALUE(fd2,i)
				if OnPreview then
					value2, value2s, value2l = value2[0], value2[1], value2[2]
				end
				local value1, value1s, value1l = value2, value2s, value1l
				if FAL_ISVALUE(fd1,i) then 
					value1, value1s, value1l = FAL_GETVALUE(fd1,i)
					if OnPreview then
						value1, value1s, value1l = value1[0], value1[1], value1[2]
					end
				end

				value = self:interpolation(persent,value1,value2)
				values = self:interpolation(persent,value1s,value2s)
				valuel = self:interpolation(persent,value1l,value2l)
			else
				if persent >= 1 then
					value = FAL_GETSTRVALUE(fd2,i)
				end
			end
			if value then
				if i == 0 then
					node:setPositionX(default.x * valuel + value + values)
				
				elseif i == 1 then
					node:setPositionY(default.y * valuel + value + values)

				elseif i == 2 then
					node:setScaleX(value)
				
				elseif i == 3 then
					node:setScaleY(value)

				elseif i == 4 then
					node:setRotate(value)

				elseif i == 5 then
					local c = node:getColor()
					node:setColor(value,c[2],c[3])

				elseif i == 6 then
					local c = node:getColor()
					node:setColor(c[1],value,c[3])

				elseif i == 7 then
					local c = node:getColor()
					node:setColor(c[1],c[2],value)

				elseif i == 8 then
					node:setOpacity(value)

				elseif i == 9 then
					--macro
					if persent >= 1 then
						_LNXG["FAL.노드이름"] = node.id

						if not OnPreview and value ~= "" then
							self.XVM:call(value)
						end
					end
				elseif i == 10 then
					--lua
					if persent >= 1 then
						_G[value]()
					end
				elseif i == 11 then
					--image
					if persent >= 1 then
						if node.type == "Sprite" then
							node:setSprite(value)
						end
					end
				end
			end
		end
	end

end

function AnimMgr:maxFrame(idx,key)
	return FAL_MAXFRAME(idx,key)
end

function AnimMgr:isAnim(idx)
	return FAL_ISEXISTS(idx)
end

function AnimMgr:numNode(idx)
	return FAL_NUMNODE(idx)
end

function AnimMgr:forceFinalNodeAndStop(node)
	local t = pini:FindTimer(node.id.."_ATL_TIMER")
	if t then
		local curFrame = t.userdata.curFrame
		local i = t.userdata.i
		local max = t.userdata.max
		local default = t.userdata.default
		local name = t.userdata.name
		local args = t.userdata.args

		t:stop()

		while curFrame <= max do
			AnimMgr:adjustFrame(name,i,curFrame,1,node,default,args,false)
			curFrame = curFrame + 1
		end

		if t.userdata.callback then
			t.userdata.callback()
		end

		node:unregistOnExit("PINI_ANIM_MGR")
	end
end

function AnimMgr:stop(node)
	local t = pini:FindTimer(node.id.."_ATL_TIMER")
	if t then
		t:stop()
		node:unregistOnExit("PINI_ANIM_MGR")
	end
end

function AnimMgr:registArgument(node,idx,value)
	if type(value) == "number" then
		return FAL_REGISTNUMBERVALUE(node,idx,value)
	else
		return FAL_REGISTSTRINGVALUE(node,idx,value)
	end
end
return AnimMgr
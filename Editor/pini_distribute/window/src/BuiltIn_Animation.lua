fs_animation={}
fs_ease={}

fs_ease["사인인"] = function(a) return pini.Anim.EaseSineIn(a) end
fs_ease["사인아웃"] = function(a) return pini.Anim.EaseSineOut(a) end
fs_ease["사인인아웃"] = function(a) return pini.Anim.EaseSineInOut(a) end
fs_ease["바운스인"] = function(a) return pini.Anim.EaseBounceIn(a) end
fs_ease["바운스아웃"] = function(a) return pini.Anim.EaseBounceOut(a) end
fs_ease["바운스인아웃"] = function(a) return pini.Anim.EaseBounceInOut(a) end
fs_ease["백인"] = function(a) return pini.Anim.EaseBackIn(a) end
fs_ease["백아웃"] = function(a) return pini.Anim.EaseBackOut(a) end
fs_ease["백인아웃"] = function(a) return pini.Anim.EaseBackInOut(a) end
fs_ease["엘라스틱인"] = function(a) return pini.Anim.EaseElasticIn(a) end
fs_ease["엘라스틱아웃"] = function(a) return pini.Anim.EaseElasticOut(a) end
fs_ease["엘라스틱인아웃"] = function(a) return pini.Anim.EaseElasticInOut(a) end

local function posStrToPt(pos)
    local winSize = {width=WIN_WIDTH,height=WIN_HEIGHT}--cc.Director:getInstance():getVisibleSize()
	local pos = pos:explode(",")
	--if OnPreview then
		return tonumber(pos[1] or 0),tonumber(pos[2] or 0)
	--else
	--	return tonumber(pos[1] or 0),winSize.height-tonumber(pos[2] or 0)
	--end
end

fs_animation["이동"] = {
	"위치=\"0,0\" 시간=\"1\" 가속=\"\" ",
	function(vm,node)
		local pos = vm:ARGU("애니메이션","위치","0,0")
		local sec = vm:ARGU("애니메이션","시간",1)
		local ease = vm:ARGU("애니메이션","가속","")
		local rep = vm:ARGU("애니메이션","지속","아니오")
		local legacy = vm:ARGU("애니메이션","레거시","아니오")

		legacy = legacy == "예"
		local parent = nil
		if not legacy then
			parent = node.parent
		end

		local x,y = posStrToPt(pos)
		local action = pini.Anim.MoveTo(sec,x,y,parent)

		if fs_ease[ease] then
			action = fs_ease[ease](action)
		end

		action:run(node)
	end
}

fs_animation["회전"] = {
	"각도=\"90\" 시간=\"1\" 가속=\"\" ",
	function(vm,node)
		local rot = vm:ARGU("애니메이션","각도",0)
		local sec = vm:ARGU("애니메이션","시간",1)
		local ease = vm:ARGU("애니메이션","가속","")
		local rep = vm:ARGU("애니메이션","지속","아니오")

		local action = pini.Anim.RotateTo(sec,rot)

		if fs_ease[ease] then
			action = fs_ease[ease](action)
		end
		if rep == "예" then
			--action = cc.Repeat:create(action,999)
		end
		action:run(node)
	end
}

fs_animation["크기"] = {
	"크기=\"100,100\" 시간=\"1\" 가속=\"\" ",
	function(vm,node)
		local size = vm:ARGU("애니메이션","크기","100,100")
		local sec = vm:ARGU("애니메이션","시간",1)
		local ease = vm:ARGU("애니메이션","가속","")
		local rep = vm:ARGU("애니메이션","지속","아니오")
		
		local size = size:explode(",")
		local action = pini.Anim.ScaleTo(sec,tonumber(size[1]),tonumber(size[2]))

		if fs_ease[ease] then
			action = fs_ease[ease](action)
		end
		if rep == "예" then
			--action = cc.RepeatForever:create(action)
		end
		action:run(node)
	end
}

fs_animation["점프"] = {
	"위치=\"100,0\" 횟수=\"1\" 높이=\"50\" 시간=\"1\" 가속=\"\"",
	function(vm,node)
		local pos = vm:ARGU("애니메이션","위치","0,0")
		local count = vm:ARGU("애니메이션","횟수",0)
		local height = vm:ARGU("애니메이션","높이",0)
		local sec = vm:ARGU("애니메이션","시간",1)
		local ease = vm:ARGU("애니메이션","가속","")
		
		local x,y = posStrToPt(pos)
		local action = pini.Anim.JumpTo(sec,x,y,height,count)

		if fs_ease[ease] then
			action = fs_ease[ease](action)
		end
		if rep == "예" then
			--action = cc.RepeatForever:create(action)
		end
		action:run(node)
	end
}

fs_animation["투명"] = {
	"투명도=\"1\" 시간=\"1\" 가속=\"\"",
	function(vm,node)
		local fade1 = vm:ARGU("애니메이션","투명",nil)
		local fade2 = vm:ARGU("애니메이션","투명도",nil)
		local sec = vm:ARGU("애니메이션","시간",1)
		local ease = vm:ARGU("애니메이션","가속","")

		local fade = ((tonumber(fade1) or tonumber(fade2)) or 1)

		local action = pini.Anim.FadeTo(sec,fade)

		if fs_ease[ease] then
			action = fs_ease[ease](action)
		end
		if rep == "예" then
			--action = cc.RepeatForever:create(action)
		end
		action:run(node)
	end
}

fs_animation["블링크"] = {
	"횟수=\"5\" 시간=\"1\" 가속=\"\"",
	function(vm,node)
		local count = vm:ARGU("애니메이션","횟수",1)
		local sec = vm:ARGU("애니메이션","시간",1)
		local ease = vm:ARGU("애니메이션","가속","")

		local action = pini.Anim.Blink(sec,count)

		if fs_ease[ease] then
			action = fs_ease[ease](action)
		end
		if rep == "예" then
			--action = cc.RepeatForever:create(action)
		end
		action:run(node)
	end
}

fs_animation["색상"] = {
	"색상=\"255,255,255\" 시간=\"1\" 가속=\"\"",
	function(vm,node)
		local color = vm:ARGU("애니메이션","색상","255,255,255")
		local sec = vm:ARGU("애니메이션","시간",1)
		local ease = vm:ARGU("애니메이션","가속","")

		color = color:explode(",")
		local action = pini.Anim.TintTo(sec,tonumber(color[1] or 255),
											tonumber(color[2] or 255),
											tonumber(color[3] or 255))

		if fs_ease[ease] then
			action = fs_ease[ease](action)
		end
		if rep == "예" then
			--action = cc.RepeatForever:create(action)
		end
		action:run(node)
	end
}

fs_animation["상하흔들기"] = {
	"폭=\"50\" 횟수=\"1\" 시간=\"1\" 가속=\"\"",
	function(vm,node)
		local width = vm:ARGU("애니메이션","폭",1)
		local count = vm:ARGU("애니메이션","횟수",1)
		local sec = vm:ARGU("애니메이션","시간",1)
		local ease = vm:ARGU("애니메이션","가속","")

		local action = nil
		for i=1,count,1 do 
			local a = pini.Anim.Sequence(
				pini.Anim.MoveBy(sec/(4*count),0,width/2),
				pini.Anim.MoveBy(sec/(4*count),0,-width/2),
				pini.Anim.MoveBy(sec/(4*count),0,-width/2),
				pini.Anim.MoveBy(sec/(4*count),0,width/2)
			)
			if action then
				action = pini.Anim.Sequence(action,a)
			else
				action = a
			end
		end

		if fs_ease[ease] then
			action = fs_ease[ease](action)
		end
		if rep == "예" then
			--action = cc.RepeatForever:create(action)
		end
		action:run(node)
	end
}

fs_animation["좌우흔들기"] = {
	"폭=\"50\" 횟수=\"1\" 시간=\"1\" 가속=\"\"",
	function(vm,node)
		local width = vm:ARGU("애니메이션","폭",1)
		local count = vm:ARGU("애니메이션","횟수",1)
		local sec = vm:ARGU("애니메이션","시간",1)
		local ease = vm:ARGU("애니메이션","가속","")

		local action = nil
		for i=1,count,1 do 
			local a = pini.Anim.Sequence(
				pini.Anim.MoveBy(sec/(4*count),width/2,0),
				pini.Anim.MoveBy(sec/(4*count),-width/2,0),
				pini.Anim.MoveBy(sec/(4*count),-width/2,0),
				pini.Anim.MoveBy(sec/(4*count),width/2,0)
			)
			if action then
				action = pini.Anim.Sequence(action,a)
			else
				action = a
			end
		end

		if fs_ease[ease] then
			action = fs_ease[ease](action)
		end
		if rep == "예" then
			--action = cc.RepeatForever:create(action)
		end
		action:run(node)
	end
}

fs_animation["떨림"] = {
	"폭=\"4\" 시간=\"1\" 가속=\"\"",
	function(vm,node)
		local width = vm:ARGU("애니메이션","폭",1)
		local sec = vm:ARGU("애니메이션","시간",1)
		local ease = vm:ARGU("애니메이션","가속","")

		local actions = {}
		local x,y = node:position()

		if node.isRunnVibe then
			return
		end
		node.isRunnVibe = true

		pini.Timer(pini:GetUUID(),0,function(t)
			t.userdata.delta = t.userdata.delta + t.dt
			local node = pini:FindNode(t.userdata.nodeId)
			if node then
				if node:ActiveActions() > 0 then
					return ;
				end
				if node.onAnim == true then
					local dx = math.random()*t.userdata.width - t.userdata.width/2
					local dy = math.random()*t.userdata.width - t.userdata.width/2
					node:setPosition(dx+t.userdata.x,dy+t.userdata.y)
					if t.userdata.delta > t.userdata.sec then
						t:stop()
						node:setPosition(t.userdata.x,t.userdata.y)
						node.isRunnVibe = nil
					end
				else
					t:stop()
					node:setPosition(t.userdata.x,t.userdata.y)
					node.isRunnVibe = nil
				end
			end
		end,true,nil,{
			x=x,
			y=y,
			nodeId=node.id,
			width=width,
			delta=0,
			sec=tonumber(sec) or 1
		}):run()
	end
}

fs_animation["걷기"] = {
	"폭=\"40\" 횟수=\"5\" 확대=\"1.3,1.3\" 시간=\"1\" 가속=\"\"",
	function(vm,node)
		local width = vm:ARGU("애니메이션","폭",1)
		local count = vm:ARGU("애니메이션","횟수",1)
		local sec = vm:ARGU("애니메이션","시간",1)
		local ease = vm:ARGU("애니메이션","가속","")
		local scale = vm:ARGU("애니메이션","확대","")

		local action = nil
		for i=1,count,1 do 
			local a = pini.Anim.Sequence(
				pini.Anim.MoveBy(sec/(2*count),0,width/2),
				pini.Anim.MoveBy(sec/(2*count),0,-width/2)
			)
			if action then
				action = pini.Anim.Sequence(action,a)
			else
				action = a
			end
		end

		scale = scale:explode(",")

		action = pini.Anim.Spawn(
			pini.Anim.ScaleBy(sec,tonumber(scale[1]) or 1.0,tonumber(scale[2])or 1.0),
			action
		)

		if fs_ease[ease] then
			action = fs_ease[ease](action)
		end
		if rep == "예" then
			--action = cc.RepeatForever:create(action)
		end
		action:run(node)
	end
}

fs_animation["스프라이트"] = {
	"스프라이트=\"이미지이름\" 시작=\"0\" 끝=\"5\" 프레임시간=\"0.1\" 반복=\"0\"",
	function(vm,node)
		local name = vm:ARGU("애니메이션","스프라이트","")
		local start = vm:ARGU("애니메이션","시작",1)
		local _end = vm:ARGU("애니메이션","끝",1)
		local sec = vm:ARGU("애니메이션","프레임시간",0.1)
		local loop = vm:ARGU("애니메이션","반복","0")

		if name:len() == 0 then
			return 
		end

		start = tonumber(start)
		_end = tonumber(_end)
		loop = tonumber(loop)
		sec = tonumber(sec)

		local beforeTexName = node:getTextureName()

		local length = math.abs(start-_end) + 1
		local isReverse = start > _end

		if loop == 0 then
			length = nil
		end

		pini.Timer(pini:GetUUID(),sec,function(t)
			local idx   = t.userdata.idx
			local name  = t.userdata.name
			local start = t.userdata.start
			local _end  = t.userdata._end
			local isReverse = t.userdata.isReverse
			local node  = pini:FindNode(t.userdata.nodeId)
			if node and node.onAnim == true and node:getTextureName() == t.userdata.beforeTexName then
				node:setSprite(name .. tostring(idx) .. ".png")

				if isReverse then
					idx = idx - 1 
					if idx < _end then
						idx = start
					end
				else
					idx = idx + 1 
					if idx > _end then
						idx = start
					end
				end

				t.userdata.idx = idx
				t.userdata.beforeTexName = node:getTextureName()
			else
				t:stop()
			end
		end,true,length,{
			beforeTexName = beforeTexName,
			idx = start,
			name = name,
			isReverse = isReverse,
			start = start,
			_end = _end,
			nodeId = node.id,
		}):run()
	end
}

--[[
@애니메이션 아이디 : 
	#1 이동 10 10
	#2 크기 10 10 
	#0 멈춤 1
	#0 멈춤 1
	#
]]
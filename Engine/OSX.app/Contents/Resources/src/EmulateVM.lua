require("utils")

local function Emulate(luavm)
    local winSize = cc.Director:getInstance():getVisibleSize()
	local scene = nil
	local fs_position={
		왼쪽상단=function(i)
			i:setAnchorPoint(cc.p(0,1));
			i:setPosition(0,winSize.height)
		end,
		오른쪽상단=function(i)
			i:setAnchorPoint(cc.p(1,1));
			i:setPosition(winSize.width,winSize.height)
		end,
		화면중앙=function(i)
			i:setAnchorPoint(cc.p(0.5,0.5));
			i:setPosition(winSize.width/2,winSize.height/2)
		end,
		왼쪽하단=function(i)
			i:setAnchorPoint(cc.p(0,0));
			i:setPosition(0,0)
		end,
		오른쪽하단=function(i)
			i:setAnchorPoint(cc.p(1,0));
			i:setPosition(winSize.width,0)
		end
	}
	local fs_size = {
		 원본크기=function(i)
		 end,
		 두배=function(i)
		 	i:setScale(2)
		 end,
		 화면맞춤=function(i)
		 	i:setScale(1)
		 	size = i:getContentSize()
		 	i:setScaleX( winSize.width / size.width )
		 	i:setScaleY( winSize.height / size.height )
		 end
	}
	local fs_imageEffect = {
		업페이드=function(img,sec)
			img:setPositionY(img:getPositionY()-10)
			img:setOpacity(0)
			local action = cc.Spawn:create(
				cc.MoveBy:create(sec,cc.p(0,10)),
				cc.FadeIn:create(sec)
			)
			img:runAction(action)
		end,
		다운페이드=function(img,sec)
			img:setPositionY(img:getPositionY()+10)
			img:setOpacity(0)
			local action = cc.Spawn:create(
				cc.MoveBy:create(sec,cc.p(0,-10)),
				cc.FadeIn:create(sec)
			)
			img:runAction(action)
		end,
		줌인페이드=function(img,sec)
			s = img:getScale()
			img:setScale(s-0.1)
			img:setOpacity(0)
			local action = cc.Spawn:create(
				cc.ScaleTo:create(sec,s),
				cc.FadeIn:create(sec)
			)
			img:runAction(action)
		end,
		줌아웃페이드=function(img,sec)
			s = img:getScale()
			img:setScale(s+0.1)
			img:setOpacity(0)
			local action = cc.Spawn:create(
				cc.ScaleTo:create(sec,s),
				cc.FadeIn:create(sec)
			)
			img:runAction(action)
		end
	}
	local fs_imageDeleteEffect = {
		업페이드=function(img,sec)
			local action = cc.Spawn:create(
				cc.MoveBy:create(sec,cc.p(0,10)),
				cc.FadeTo:create(sec,0)
			)
            img:runAction(cc.Sequence:create(action,cc.RemoveSelf:create(true)))
		end,
		다운페이드=function(img,sec)
			local action = cc.Spawn:create(
				cc.MoveBy:create(sec,cc.p(0,-10)),
				cc.FadeTo:create(sec,0)
			)
			img:runAction(cc.Sequence:create(action,cc.RemoveSelf:create(true)))
		end,
		줌인페이드=function(img,sec)
			local s = img:getScale()
			local action = cc.Spawn:create(
				cc.ScaleTo:create(sec,s-0.1),
				cc.FadeTo:create(sec,0)
			)
			img:runAction(cc.Sequence:create(action,cc.RemoveSelf:create(true)))
		end,
		줌아웃페이드=function(img,sec)
			local s = img:getScale()
			local action = cc.Spawn:create(
				cc.ScaleTo:create(sec,s+0.1),
				cc.FadeTo:create(sec,0)
			)
			img:runAction(cc.Sequence:create(action,cc.RemoveSelf:create(true)))
		end
	}

	local images = {}
	local Dialog = {}
	function Dialog:initialize()
		self.back = cc.LayerColor:create(cc.c4b(255,255,255,122),
										 winSize.width-20,winSize.height-20)
		self.back:retain()
		self.back:setPosition(10,10)

		local touches = nil
		local focuses = nil
		local function focusOff(blocks)
			for k,v in ipairs(blocks)do 
				v:stopAllActions()
				v:setOpacity(40)
			end
			focuses = nil
		end
		local function focusOn(blocks)
			for k,v in ipairs(blocks)do 
				local sequence = cc.Sequence:create(
					cc.FadeTo:create(0.25,120),
					cc.FadeTo:create(0.25,60))
				v:runAction( cc.RepeatForever:create(sequence) )
			end
			focuses = blocks
		end
		local function onTouchBegan(touch, event)
			if self.back:isVisible() == false then
				return false
			end
			if #self.linker > 0 then
				local location = touch:getLocation()
				for k,list in ipairs(self.linker) do
					for k,v in ipairs(list) do
						local tloc = v:convertToNodeSpace(location);
						local b = v:getBoundingBox();
						if tloc.x > 0 and tloc.y > 0 and tloc.x < b.width and tloc.y < b.height then
							if touches and touches ~= list then
								focusOff(touches)
							end
							touches = list
							return true
						end
					end
				end
				if touches then
					focusOff(touches)
					touches = nil
				end
			end
			return true
		end
		local function onTouchEnded(touch, event)
			if self.cursor >= #self.letters then
				if #self.linker == 0 then
					self:fin()
					self.vm:doNext()
				elseif touches then
					local location = touch:getLocation()
					for k,v in ipairs(touches) do
						local tloc = v:convertToNodeSpace(location);
						local b = v:getBoundingBox();
						if tloc.x > 0 and tloc.y > 0 and tloc.x < b.width and tloc.y < b.height then
							if focuses == touches then
								touches = nil
								self:fin()
								self.vm:GotoBookmark(v.link)
								self.vm:doNext()
							else
								focusOn(touches)
							end
							return true
						end
					end

				end
			else
				self.cursor = #self.letters
				for k,v in ipairs(self.letters) do
					v:setVisible(true)
				end
			end
		end

		local listener = cc.EventListenerTouchOneByOne:create()
		listener:registerScriptHandler(onTouchBegan,cc.Handler.EVENT_TOUCH_BEGAN )
		listener:registerScriptHandler(onTouchEnded,cc.Handler.EVENT_TOUCH_ENDED )
		local eventDispatcher = self.back:getEventDispatcher()
		eventDispatcher:addEventListenerWithSceneGraphPriority(listener, self.back)

		self.letters = {}
		self.runEntry = nil
		self.cursor = 0
		self.nowX = 0
		self.nowY = 0
		self.linker = {}
	end
	function Dialog:setConfig(op)
		local width = op["width"] or self.back:getContentSize().width
		local height = op["height"] or self.back:getContentSize().height
		self.back:setContentSize(cc.size(width,height))
	end
	function Dialog:build(args)
		if self.name then
			layer = cc.LayerColor:create(cc.c4b(255,255,255,122),200,50)
			self.back:addChild(layer)

			layer:setPositionY(10 + self.back:getContentSize().height )
			local label = cc.Label:createWithTTF(self.name,"default.ttf",30)
			layer:addChild(label)
			label:setColor(cc.c3b(0,0,0))
			label:setPosition(100,25)

		end

		default_color = cc.c3b(255,255,255)
		default_size = 30

		x,y,maxY,color,size,link,lineGap,wordGap = 
		self.nowX,self.nowY,default_size,default_color,default_size,nil,5,0

		for k,v in ipairs(args) do
			print_str = nil
			if v["type"] == "string" then
				if v["v"] == "\n" then
					x,y,maxY = 0,y-maxY-lineGap,default_size
				elseif v["v"]:len() > 0 then
					print_str = v["v"]
				end
			else
				_v = v["v"]
				_a = _v["args"]

				if _v["name"] == "색상" then
					color = cc.c3b(tonumber(_a[1]),tonumber(_a[2]),tonumber(_a[3]))
				elseif _v["name"] == "/색상" then
					color = default_color

				elseif _v["name"] == "크기" then
					size = tonumber(_a[1])
				elseif _v["name"] == "/크기" then
					size = default_size

				elseif _v["name"] == "공백" then
					x = x+tonumber(_a[1])

				elseif _v["name"]:startsWith("=") then
					local _id = _v["name"]:sub(2,#_v["name"])
					print_str = tostring(self.vm.variable[_id])
					
				elseif _v["name"] == "연결" then
					if #_a > 0 then 
						link = _a[1]:sub(2,#_a[1]-1)
					else 
						link = "??"
					end
				elseif _v["name"] == "/연결" then
					link = nil
				end
			end
			if print_str then 
				x,y,mY,blocks = self:makeBlock(x,y,print_str,color,size,link,wordGap)
				if maxY < mY then maxY = mY end 
				if #blocks > 0 then
					table.insert(self.linker,blocks)
				end
			end
		end
	end
	function Dialog:makeBlock(startX,startY,str,color,size,link,wordGap)
		_c=cc.c4b(60,60,60,40)

		local blocks = {}
		if link then
			c = cc.LayerColor:create(_c,0,0)
			c.link = link
			c:setPositionX(startX)
			self.back:addChild(c)
			table.insert(blocks,c)
		end

		t,p = {},""
		str:gsub(".",function(c)
			table.insert(t,c)
		end)
		
		x,y,maxY,width = startX,startY,0,0
		for k,v in ipairs(t) do
			local char = ""
			if string.byte(v) < 127 then
				char = v
			else
				p = p .. v
				if p:len() == 3 then
					char = p
					p=""
				end
			end
			if char:len() > 0 then
				local label = cc.Label:createWithTTF(char,"default.ttf",size)
				table.insert(self.letters,label)

				if x + label:getContentSize().width > self.back:getContentSize().width then
					y,x,maxY,width = y-maxY,0,0,0
					if link then 
						c = cc.LayerColor:create(_c,0,0)
						c.link = link
						c:setPositionX(0)
						self.back:addChild(c)
						table.insert(blocks,c)
					end
				end
				
				self.back:addChild(label,1)
				label:setPosition(x,y)
				label:setColor(color)
				label:setVisible(false)
				label:setAnchorPoint(cc.p(0,1))
				x = x + label:getContentSize().width + wordGap
				width = width + label:getContentSize().width + wordGap
				if maxY < label:getContentSize().height then
					maxY = label:getContentSize().height
					if link then blocks[#blocks]:setPositionY(y-maxY) end
				end
				if link then blocks[#blocks]:setContentSize(cc.size(width,maxY)) end

				table.insert(self.letters,label)
			end
		end
		return x,y,maxY,blocks
	end
	function Dialog:run()
		if self.cursor < #self.letters then
			self.cursor = self.cursor+1
			self.letters[self.cursor]:setVisible(true)
		end
	end
	function Dialog:start()
		local scheduler = cc.Director:getInstance():getScheduler()
		self.runEntry = scheduler:scheduleScriptFunc(function() self:run() end, 0.00,false)
	end
	function Dialog:fin()
		local scheduler = cc.Director:getInstance():getScheduler()
		scheduler:unscheduleScriptEntry(self.runEntry)
		self.runEntry = nil
		self.back:removeFromParent()
	end
	function Dialog:setName(name)
		self.name = name
	end
	function Dialog:runText(vm,scene,args)
		if self.back:getParent() then
			self.back:removeFromParent()
		end
		self.vm = vm
		self.cursor = 0
		self.nowX = 0
		self.nowY = self.back:getContentSize().height
		self.letters = {}
		self.linker = {}
		scene.layer:addChild(self.back,100)
		self.back:removeAllChildren();

		self:build(args)
		self:start()
	end
	function Dialog:appendText()
	end

	Dialog:initialize()
	--Dialog:setConfig({height=300})

	luavm:registFunc("이미지",function(vm,arg)
		local id = vm.variable["이미지.아이디"] or ""
		local path = vm.variable["이미지.파일명"] or ""
		local pos = vm.variable["이미지.위치"] or "0,0"
		local effect = vm.variable["이미지.효과"] or ""
		local effectSec = vm.variable["이미지.효과시간"] or 0.25
		local size = vm.variable["이미지.크기"] or "0,0"
		if path:len() > 0 then
			local img = cc.Sprite:create("image/"..path)
			scene.layer:addChild(img)
			
			if fs_position[pos] then
				fs_position[pos](img)
			else
				p = pos:explode(",")
				img:setAnchorPoint(cc.p(0,1));
				img:setPosition(tonumber(p[1]),winSize.height-tonumber(p[2]))
			end

			if fs_size[size] then
				fs_size[size](img)
			else
				p = pos:explode(",")
				img:setScale(1)
				size = img:getContentSize()

				img:setScaleX(tonumber(p[1])/size.width)
				img:setScaleY(tonumber(p[2])/size.height)
			end

			if id:len() > 0 then
				if images[id] then
					images[id]:removeFromParent()
				end
				images[id] = img
			end
			if effect:len() > 0 then
				if fs_imageEffect[effect] then
					fs_imageEffect[effect](img,effectSec)
				end
			end
		end
		vm:doNext()
	end)

	luavm:registFunc("이미지삭제",function(vm,arg)
		local id = vm.variable["이미지삭제.아이디"] or ""
		local effect = vm.variable["이미지삭제.효과"] or ""
		local effectSec = vm.variable["이미지삭제.효과시간"] or 0.25

		if id:len() > 0 then
			if effect:len() > 0 then
				if fs_imageDeleteEffect[effect] then
					fs_imageDeleteEffect[effect](images[id],effectSec)
				end
			else
				images[id]:removeFromParent()
			end
			images[id] = nil
		end
		vm:doNext()
	end)

	luavm:registFunc("독백",function(vm,arg)
		Dialog:setConfig({height=winSize.height-20})
		Dialog:runText(vm,scene,arg["targ"])
	end)

	luavm:registFunc("대화",function(vm,arg)
		local name = vm.variable["대화.이름"] or ""

		if name:len() > 0 then
			Dialog:setName(name)
		else
			Dialog:setName(nil)
		end
		Dialog:setConfig({height=200})
		Dialog:runText(vm,scene,arg["targ"])
	end)

	luavm:registFunc("화면전환",function(vm,arg)
	    scene = cc.Scene:create()
	    layer = cc.Node:create()

	    scene:addChild(layer)
	    scene.layer = layer
		if cc.Director:getInstance():getRunningScene() then
			cc.Director:getInstance():replaceScene(scene)
		else
			cc.Director:getInstance():runWithScene(scene)
		end
		vm:doNext()
	end)
	luavm:pushCmd("t_function",{targ = {},name = "화면전환"})
end

return Emulate
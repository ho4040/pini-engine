require("trycatch")

local PiniLib
local fileUtil = nil
local ROOT_PATH = nil
local SCALE_FACTOR = nil
local SCHEDULER = nil
local Utils = nil
if OnPreview then
else
	Utils = require("plua.utils")
	fileUtil = cc.FileUtils:getInstance()
	ROOT_PATH = fileUtil:getWritablePath()
	SCHEDULER = cc.Director:getInstance():getScheduler()
	--require("cocos.cocosdenshion.AudioEngine")
	SCALE_FACTOR = function ()
		return cc.Director:getInstance():getContentScaleFactor()
	end

	fileUtil.fileExistCache = {}
	fileUtil.fileExist = function(self,path)
		if path == nil then
			return false
		end
		if self.fileExistCache[path] == nil then
			self.fileExistCache[path] = self:isFileExist(path)
		end
		return self.fileExistCache[path]
	end
end

function ripairs(t)
  local function ripairs_it(t,i)
	i=i-1
	local v=t[i]
	if v==nil then return v end
	return i,v
  end
  return ripairs_it, t, #t+1
end

function class(base, init)
	local c = {}	 -- a new class instance
	if not init and type(base) == 'function' then
		init = base
		base = nil
	elseif type(base) == 'table' then
		for i,v in pairs(base) do
			c[i] = v
		end
		c._base = base
	end
	c.__index = c

	local mt = {}
	mt.__call = function(class_tbl, ...)
		local obj = {}
		setmetatable(obj,c)
		if init then
			init(obj,...)
		elseif class_tbl.init then
			if class_tbl.init(obj,...) == false then
				return nil
			end
		else 
			if base and base.init then
				if base.init(obj, ...) == false then
					return nil
				end
			end
		end
		return obj
	end
	c.init = init
	c.is_a = function(self, klass)
		local m = getmetatable(self)
		while m do 
			if m == klass then return true end
			m = m._base
		end
		return false
	end
	setmetatable(c, mt)
	return c
end

---------------------------------------------
-- PINI API 
---------------------------------------------
function StrEnumToPos(node,str)
	-- "화면중앙", "왼쪽상단", "120,240" 등을 좌표로 변경합니다.
	local x,y = unpack(str:explode(","))
	if fs_position[x] then
		local sx,sy,psx,psy
		local ps = node:parentSize()
		local acx,acy = node:anchor()
		local size = node:contentSize()
		sx,sy = node:scale()
		psx,psy = node:parentsNodeScale()

		sx = size.width  * psx * sx 
		sy = size.height * psy * sy 
		x = fs_position[x](ps,sx,sy)
		
		y = x[2] + sy*(0.5-acy)
		x = x[1] - sx*(0.5-acx)
	else
		x = tonumber(x) or 0
		y = tonumber(y) or 0
	end
	return x,y
end

function StrEnumToScale(node,str)
	-- "원본크기", "두배", "2,2" 등을 배율로 변경합니다.
	local x,y = unpack(str:explode(","))
	if fs_size[x] then
		local sx,sy,psx,psy
		local ps = node:parentSize()
		local s = node:contentSize()
		x,y = unpack(fs_size[x](ps,s.width,s.height))
	else
		x = tonumber(x) or 1
		y = tonumber(y) or 1
	end
	return x,y
end

---------------------------------------------------------------
--위치 선정
---------------------------------------------------------------
fs_position={}
fs_size = {}
---------------------------------------------------------------
fs_position["왼쪽상단"]=function(w,sx,sy)
	return {sx*0.5,sy*0.5}
end
fs_position["오른쪽상단"]=function(w,sx,sy)
	return {w.width-sx*0.5,sy*0.5}
end
fs_position["화면중앙"]=function(w,sx,sy)
	return {w.width*0.5,w.height*0.5}
end
fs_position["왼쪽하단"]=function(w,sx,sy)
	return {sx*0.5,w.height-sy*0.5}
end
fs_position["오른쪽하단"]=function(w,sx,sy)
	return {w.width-sx*0.5,w.height-sy*0.5}
end

---------------------------------------------------------------
--사이즈 선정
---------------------------------------------------------------

fs_size["원본크기"]=function(w,sx,sy)
	return {1,1}
end
fs_size["두배"]=function(w,sx,sy)
	return {2,2}
end
fs_size["화면맞춤"]=function(w,sx,sy)
	return {w.width/sx,w.height/sy}
end

---------------------------------------------------------------
--이미지 등장 효과 관리
---------------------------------------------------------------
fs_imageEffect = {}
fs_imageDeleteEffect = {}
---------------------------------------------------------------
fs_imageEffect["페이드"]=function(node,sec)
	local op = node.opacity
	node:setOpacity(0)
	local action = pini.Anim.EaseIn(pini.Anim.FadeTo(sec,op),0.5)
	action:run(node)
end
fs_imageEffect["업페이드"]=function(node,sec)
	local op = node.opacity
	local x,y
	x,y = node:position()
	node:setPosition(x,y+10)
	node:setOpacity(0)
	local action = pini.Anim.Spawn(
		pini.Anim.MoveBy(sec,0,-10),
		pini.Anim.FadeTo(sec,op)
	)
	action:run(node)
end
fs_imageEffect["다운페이드"]=function(node,sec)
	local op = node.opacity
	local x,y
	x,y = node:position()
	node:setPosition(x,y-10)
	node:setOpacity(0)
	local action = pini.Anim.Spawn(
		pini.Anim.MoveBy(sec,0,10),
		pini.Anim.FadeTo(sec,op)
	)
	action:run(node)
end
fs_imageEffect["줌인페이드"]=function(node,sec)
	local op = node.opacity
	local x,y
	x,y = node:scale()
	node:setScale(x-0.1,y-0.1)
	node:setOpacity(0)
	local action = pini.Anim.Spawn(
		pini.Anim.ScaleTo(sec,x,y),
		pini.Anim.FadeTo(sec,op)
	)
	action:run(node)
end
fs_imageEffect["줌아웃페이드"]=function(node,sec)
	local op = node.opacity
	local x,y
	x,y = node:scale()
	node:setScale(x+0.1,y+0.1)
	node:setOpacity(0)
	local action = pini.Anim.Spawn(
		pini.Anim.ScaleTo(sec,x,y),
		pini.Anim.FadeTo(sec,op)
	)
	action:run(node)
end

---------------------------------------------------------------
--이미지 퇴장 효과 관리
---------------------------------------------------------------
fs_imageDeleteEffect["페이드"]=function(node,sec)
	local action = pini.Anim.EaseOut(pini.Anim.FadeTo(sec,0),0.5)
	action:run(node)
end
fs_imageDeleteEffect["업페이드"]=function(node,sec)
	local action = pini.Anim.Spawn(
		pini.Anim.MoveBy(sec,0,-10),
		pini.Anim.FadeTo(sec,0)
	)
	action:run(node)
end
fs_imageDeleteEffect["다운페이드"]=function(node,sec)
	local action = pini.Anim.Spawn(
		pini.Anim.MoveBy(sec,0,10),
		pini.Anim.FadeTo(sec,0)
	)
	action:run(node)
end
fs_imageDeleteEffect["줌인페이드"]=function(node,sec)
	local x,y
	x,y = node:scale()
	local action = pini.Anim.Spawn(
		pini.Anim.ScaleTo(sec,x-0.1,y-0.1),
		pini.Anim.FadeTo(sec,0)
	)
	action:run(node)
end
fs_imageDeleteEffect["줌아웃페이드"]=function(node,sec)
	local x,y
	x,y = node:scale()
	local action = pini.Anim.Spawn(
		pini.Anim.ScaleTo(sec,x+0.1,y+0.1),
		pini.Anim.FadeTo(sec,0)
	)
	action:run(node)
end

---------------------------------------------
-- Animation
---------------------------------------------
local MoveBy = class()
function MoveBy:init(sec,x,y)
	self.x = x
	if OnPreview then
		self.y = y
	else
		self.y = -y
		self._y = y
	end
	self.sec = sec
	return true
end
function MoveBy:cocosObj()
	return cc.MoveBy:create(self.sec,cc.p(self.x,self.y))
end
function MoveBy:changeValue(node)
	local x,y = node:position()
	node._x = self.x+x
	node._y = self._y+y
end
function MoveBy:run(node)
	local x,y = node:position()
	if OnPreview then
		node:setPosition(self.x+x,self.y+y)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local MoveTo = class()
function MoveTo:init(sec,x,y,parent)
	self.x = x
	self._y = y

	if OnPreview then
		self.y = y
	else
		x = x/SCALE_FACTOR()
		y = y/SCALE_FACTOR()

		local height = WIN_HEIGHT
		local dx = 0
		local dy = 0
		if parent then
			local ax,ay,width

			if parent.type ~= "Scene" then
				width  = parent:contentSize().width
				height = parent:contentSize().height
				ax,ay  = parent:anchor()
			else
				width = WIN_WIDTH
				ax,ay = 0,1
			end

			dx = width*ax
			dy = height*(1-ay)
		end

		self.x = x+dx
		self.y = height-y-dy
	end
	self.sec = sec
	return true
end
function MoveTo:cocosObj()
	return cc.MoveTo:create(self.sec,cc.p(self.x,self.y))
end
function MoveTo:changeValue(node)
	node._x = self.x
	node._y = self._y
end
function MoveTo:run(node)
	if OnPreview then
		node:setPosition(self.x,self.y)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local RotateTo = class()
function RotateTo:init(sec,rot)
	self.sec = sec
	self.rot = rot
	return true
end
function RotateTo:cocosObj()
	return cc.RotateTo:create(self.sec,self.rot)
end
function RotateTo:changeValue(node)
	node.rotate = self.rot
end
function RotateTo:run(node)
	if OnPreview then
		node:setRotate(self.rot)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local FadeTo = class()
function FadeTo:init(sec,op)
	self.opacity = op
	self.sec = sec
	return true
end
function FadeTo:cocosObj()
	return cc.FadeTo:create(self.sec,self.opacity)
end
function FadeTo:changeValue(node)
	node.opacity = self.opacity
end
function FadeTo:run(node)
	if OnPreview then
		node:setOpacity(self.opacity)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local ScaleTo= class()
function ScaleTo:init(sec,x,y)
	self.x = x
	self.y = y
	self.sec = sec
	return true
end
function ScaleTo:cocosObj()
	return cc.ScaleTo:create(self.sec,self.x,self.y)
end
function ScaleTo:changeValue(node)
	node.scaleX = self.x
	node.scaleY = self.y
end
function ScaleTo:run(node)
	if OnPreview then
		node:setScale(self.x,self.y)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local ScaleBy=class()
function ScaleBy:init(sec,x,y)
	self.x = x
	self.y = y
	self.sec = sec
	return true
end
function ScaleBy:cocosObj()
	return cc.ScaleBy:create(self.sec,self.x,self.y)
end
function ScaleBy:changeValue(node)
	local x,y = node:scale()
	node.scaleX = x*self.x
	node.scaleY = y*self.y
end
function ScaleBy:run(node)
	if OnPreview then
		local x,y = node:scale()
		node:setScale(x*self.x,y*self.y)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local Spawn=class()
function Spawn:init(...)
	self.list = {...}
	return true
end
function Spawn:cocosObj()
	local _list = {}
	for k,v in ipairs(self.list) do
		table.insert(_list,v:cocosObj())
	end
	return cc.Spawn:create(unpack(_list))
end
function Spawn:changeValue(node)
	for k,v in ipairs(self.list) do
		v:changeValue(node)
	end
end
function Spawn:run(node)
	if OnPreview then
		for i,v in ipairs(self.list) do
			v:run(node)
		end
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local Sequence=class()
function Sequence:init(...)
	self.list = {...}
	return true
end
function Sequence:cocosObj()
	local _list = {}
	for k,v in ipairs(self.list) do
		table.insert(_list,v:cocosObj())
	end
	return cc.Sequence:create(unpack(_list))
end
function Sequence:changeValue(node)
	for k,v in ipairs(self.list) do
		v:changeValue(node)
	end
end
function Sequence:run(node)
	if OnPreview then
		for i,v in ipairs(self.list) do
			v:run(node)
		end
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local TintTo=class()
function TintTo:init(sec,r,g,b)
	self.r = r
	self.g = g
	self.b = b
	self.sec = sec
	return true
end
function TintTo:cocosObj()
	return cc.TintTo:create(self.sec,self.r,self.g,self.b)
end
function TintTo:changeValue(node)
	node.color = {self.r,self.g,self.b}
end
function TintTo:run(node)
	if OnPreview then
		node:setColor(self.r,self.g,self.b)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local DelayTime=class()
function DelayTime:init(sec)
	self.sec = sec
	return true
end
function DelayTime:cocosObj()
	return cc.DelayTime:create(self.sec)
end
function DelayTime:changeValue(node)
end
function DelayTime:run(node)
	if OnPreview then
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local JumpTo=class()
function JumpTo:init(sec,x,y,height,count)
	self.x = x
	if OnPreview then
		self.y = y
	else
		self.y = WIN_HEIGHT-y
		self._y = y
	end
	self.h = height
	self.c = count
	self.sec = sec
	return true
end
function JumpTo:cocosObj()
	return cc.JumpTo:create(self.sec,cc.p(self.x,self.y),self.h,self.c)
end
function JumpTo:changeValue(node)
	node._x = self.x
	node._y = self._y
end
function JumpTo:run(node)
	if OnPreview then
		node:setPosition(self.x,self.y)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local Blink=class()
function Blink:init(sec,count)
	self.sec = sec
	self.c = count
	return true
end
function Blink:cocosObj()
	return cc.Blink:create(self.sec,self.c)
end
function Blink:changeValue(node)
end
function Blink:run(node)
	if OnPreview then
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local Forever=class()
function Forever:init(action)
	self.action = action
	return true
end
function Forever:cocosObj()
	return cc.RepeatForever:create(self.action:cocosObj())
end
function Forever:changeValue(node)
end
function Forever:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseSineIn=class()
function EaseSineIn:init(action)
	self.action = action
	return true
end
function EaseSineIn:cocosObj()
	return cc.EaseSineIn:create(self.action:cocosObj())
end
function EaseSineIn:changeValue(node)
	self.action:changeValue(node)
end
function EaseSineIn:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseSineOut=class()
function EaseSineOut:init(action)
	self.action = action
	return true
end
function EaseSineOut:cocosObj()
	return cc.EaseSineOut:create(self.action:cocosObj())
end
function EaseSineOut:changeValue(node)
	self.action:changeValue(node)
end
function EaseSineOut:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseSineInOut=class()
function EaseSineInOut:init(action)
	self.action = action
	return true
end
function EaseSineInOut:cocosObj()
	return cc.EaseSineInOut:create(self.action:cocosObj())
end
function EaseSineInOut:changeValue(node)
	self.action:changeValue(node)
end
function EaseSineInOut:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseBounceIn=class()
function EaseBounceIn:init(action)
	self.action = action
	return true
end
function EaseBounceIn:cocosObj()
	return cc.EaseBounceIn:create(self.action:cocosObj())
end
function EaseBounceIn:changeValue(node)
	self.action:changeValue(node)
end
function EaseBounceIn:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseBounceOut=class()
function EaseBounceOut:init(action)
	self.action = action
	return true
end
function EaseBounceOut:cocosObj()
	return cc.EaseBounceOut:create(self.action:cocosObj())
end
function EaseBounceOut:changeValue(node)
	self.action:changeValue(node)
end
function EaseBounceOut:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseBounceInOut=class()
function EaseBounceInOut:init(action)
	self.action = action
	return true
end
function EaseBounceInOut:cocosObj()
	return cc.EaseBounceInOut:create(self.action:cocosObj())
end
function EaseBounceInOut:changeValue(node)
	self.action:changeValue(node)
end
function EaseBounceInOut:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseBackIn=class()
function EaseBackIn:init(action)
	self.action = action
	return true
end
function EaseBackIn:cocosObj()
	return cc.EaseBackIn:create(self.action:cocosObj())
end
function EaseBackIn:changeValue(node)
	self.action:changeValue(node)
end
function EaseBackIn:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseBackOut=class()
function EaseBackOut:init(action)
	self.action = action
	return true
end
function EaseBackOut:cocosObj()
	return cc.EaseBackOut:create(self.action:cocosObj())
end
function EaseBackOut:changeValue(node)
	self.action:changeValue(node)
end
function EaseBackOut:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseBackInOut=class()
function EaseBackInOut:init(action)
	self.action = action
	return true
end
function EaseBackInOut:cocosObj()
	return cc.EaseBackInOut:create(self.action:cocosObj())
end
function EaseBackInOut:changeValue(node)
	self.action:changeValue(node)
end
function EaseBackInOut:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseElasticIn=class()
function EaseElasticIn:init(action)
	self.action = action
	return true
end
function EaseElasticIn:cocosObj()
	return cc.EaseElasticIn:create(self.action:cocosObj())
end
function EaseElasticIn:changeValue(node)
	self.action:changeValue(node)
end
function EaseElasticIn:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseElasticOut=class()
function EaseElasticOut:init(action)
	self.action = action
	return true
end
function EaseElasticOut:cocosObj()
	return cc.EaseElasticOut:create(self.action:cocosObj())
end
function EaseElasticOut:changeValue(node)
	self.action:changeValue(node)
end
function EaseElasticOut:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseElasticInOut=class()
function EaseElasticInOut:init(action)
	self.action = action
	return true
end
function EaseElasticInOut:cocosObj()
	return cc.EaseElasticInOut:create(self.action:cocosObj())
end
function EaseElasticInOut:changeValue(node)
	self.action:changeValue(node)
end
function EaseElasticInOut:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseIn=class()
function EaseIn:init(action,factor)
	self.action = action
	self.factor = factor
	return true
end
function EaseIn:cocosObj()
	return cc.EaseIn:create(self.action:cocosObj(),self.factor)
end
function EaseIn:changeValue(node)
	self.action:changeValue(node)
end
function EaseIn:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseOut=class()
function EaseOut:init(action,factor)
	self.action = action
	self.factor = factor
	return true
end
function EaseOut:cocosObj()
	return cc.EaseOut:create(self.action:cocosObj(),self.factor)
end
function EaseOut:changeValue(node)
	self.action:changeValue(node)
end
function EaseOut:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local EaseInOut=class()
function EaseInOut:init(action,factor)
	self.action = action
	self.factor = factor
	return true
end
function EaseInOut:cocosObj()
	return cc.EaseInOut:create(self.action:cocosObj(),self.factor)
end
function EaseInOut:changeValue(node)
	self.action:changeValue(node)
end
function EaseInOut:run(node)
	if OnPreview then
		self.action:run(node)
	else
		self:changeValue(node)
		node:runAction(self:cocosObj())
	end
end
---------------------------------------------
local anim = {}
anim["MoveBy"] = MoveBy
anim["MoveTo"] = MoveTo
anim["FadeTo"] = FadeTo
anim["ScaleTo"] = ScaleTo
anim["ScaleBy"] = ScaleBy
anim["TintTo"] = TintTo
anim["Spawn"] = Spawn
anim["Sequence"] = Sequence
anim["RotateTo"] = RotateTo
anim["JumpTo"] = JumpTo
anim["Blink"] = Blink
anim["Forever"] = Forever
anim["DelayTime"] = DelayTime

anim["EaseSineIn"] = EaseSineIn
anim["EaseSineOut"] = EaseSineOut
anim["EaseSineInOut"] = EaseSineInOut
anim["EaseBounceIn"] = EaseBounceIn
anim["EaseBounceOut"] = EaseBounceOut
anim["EaseBounceInOut"] = EaseBounceInOut
anim["EaseBackIn"] = EaseBackIn
anim["EaseBackOut"] = EaseBackOut
anim["EaseBackInOut"] = EaseBackInOut
anim["EaseElasticIn"] = EaseElasticIn
anim["EaseElasticOut"] = EaseElasticOut
anim["EaseElasticInOut"] = EaseElasticInOut
anim["EaseIn"] = EaseIn
anim["EaseOut"] = EaseOut
anim["EaseInOut"] = EaseInOut

----------------------------------------------
-- Shader
----------------------------------------------
local Shader = class()
function Shader:init(id,vsh,fsh)
	self.id = id
	self.vsh = vsh
	self.fsh = fsh
	self.bindNode = nil
	self.isDestroyed = false
	self.uniform = {}
	pini:RegistShader(self)
	if OnPreview then
	else
		self.program = cc.GLProgram:create(vsh,fsh)
		self.program:bindAttribLocation(cc.ATTRIBUTE_NAME_POSITION, cc.VERTEX_ATTRIB_POSITION) 
		self.program:bindAttribLocation(cc.ATTRIBUTE_NAME_TEX_COORD, cc.VERTEX_ATTRIB_TEX_COORD)
		self.program:link()
		self.program:updateUniforms()

		self.glprogramstate = cc.GLProgramState:getOrCreateWithGLProgram( self.program );
	end
	return true
end

function Shader:bind(node)
	self.bindNode = node
	node.shaderID = self.id
	if OnPreview then
	else
		if node.type == "RenderTexture" then
			node.node:getSprite():setGLProgram( self.program )
			node.node:getSprite():setGLProgramState( self.glprogramstate );
		else
			node.node:setGLProgram( self.program )
			node.node:setGLProgramState( self.glprogramstate );
		end
	end
end

function Shader:setUniformFloat(name,value)
	if self.isDestroyed then return end
	self.uniform[name]=value
	if OnPreview then
	else
		if self.bindNode == nil or self.bindNode.isDestroyed == false then
			self.glprogramstate:setUniformFloat(name,tonumber(value))
		end
	end
end

function Shader:setUniformTexture(name,spr)
	if self.isDestroyed then return end
	if OnPreview then
	else
		if self.bindNode == nil or self.bindNode.isDestroyed == false then
			self.glprogramstate:setUniformTexture(name, spr:getTextureName());
		end
	end
end

function Shader:fin()
	pini:UnregistShader(self)
	self.isDestroyed = true
end

---------------------------------------------
-- Node 
---------------------------------------------
local Node = class()
--if OnPreview then
local OnPreviewDrawOrder=0		
--end
function Node:init(id)
	self.id = id
	self.type = "Node"
	self:initialize()
	if OnPreview then
	else
		self.node = cc.Node:create()
		self.node.obj = self
		self.node:setCascadeColorEnabled(true)
	end
	self:initEventHandler()
	return true
end

function Node:registOnExit(id,func)
	table.insert(self.exitEvent,{id,func})
end

function Node:unregistOnExit(id,justOne)
	local rems = {}

	for k,v in ipairs(self.exitEvent) do
		if v[1] == id then
			table.insert(rems,k)
			if justOne == true then
				break
			end
		end
	end

	for i=0,#rems,1 do 
		local k = rems[#rems-i]
		if k then
			table.remove(self.exitEvent,k)
		end
	end
end

function Node:initEventHandler()
	self.exitEvent = {}
	if OnPreview then
	else
		local function onNodeEvent(tag)
			if self.isExited == nil then
				if tag == "exit" or tag == "cleanup" then
					self.isDestroyed = true
					for k,v in ipairs(self.exitEvent) do
						v[2](self)
					end
					pini:DetachDisplay(self,true,true)
					self.isExited = true
				end
			end
		end
		self.node:registerScriptHandler(onNodeEvent)
	end
end

function Node:serialize(t)
	t = t or self
	local serial = {}
	for k,v in pairs(t) do
		if type(v) ~= "function" and type(v) ~= "userdata" then
			if type(v) == "table" then
				serial[k] = self:serialize(v)
			else
				serial[k] = v
			end
		end
	end
	return serial
end
function Node:OverrideDefault(v)
	-- initialize from data v
	-- 이 함수는 상속받지 않습니다. 공통적인 초기화 처리는 여기서 합니다.
	self:setPosition(v._x,v._y)
	self:setRotate(v.rotate)
	self:setScale(v.scaleX,v.scaleY)
	self:setOpacity(v.opacity)
	self:setAnchorPoint(v.anchorX,v.anchorY)
	self:setIncludeScreenShot(v.includeScreenShot)
	self:setZ(v.zOrder)
	self:setContentSize(v.width,v.height)
	self:setBlendMode(v.blendMode)
	self.drawOrder = v.drawOrder
	self.touchPriority = v.touchPriority
	self.touchRegisted = v.touchRegisted
	self.onAnim = v.onAnim
	self.onTouchAnim = v.onTouchAnim
	self.callstack = v.callstack
end
function Node:gen(v)
	-- initialize from data v
	-- 이 함수는 반드시 상속받아야 합니다. 상속받은 클래스만의 처리는 여기서 합니다.
	local n = Node(v.id)
	n:OverrideDefault(v)
	return n
end
function Node:initialize()
	-- default initialize
	-- 이 함수는 상속받지 않습니다. 공통적인 초기화 처리입니다.
	self.visible = true
	self.x = 0
	self.y = 0
	self._x = 0
	self._y = 0
	self.blendMode = "기본" 
	self.scaleX = 1
	self.scaleY = 1
	self.rotate = 0
	self.anchorX = 0.5
	self.anchorY = 0.5
	self.zOrder = 0
	self.color = {255,255,255}
	self.opacity = 255
	self.touchPriority = 0
	self.includeScreenShot = true
	self._children = {}
	self.isDestroyed = false
	self.isPreserve = false
	self.onAnim = false
	self.onTouchAnim = nil
	--if OnPreview then
	self.drawOrder = OnPreviewDrawOrder
	OnPreviewDrawOrder = OnPreviewDrawOrder+1
	--end
end

function Node:release()
	if OnPreview then

	else
		self.node:release()
	end
end

function Node:runAction(obj)
	if OnPreview then

	else
		self.node:runAction(obj)
		self.onAnim = true
	end
end

function Node:changeId(newId)
	display = pini._regist_.Display

	display[self.id] = nil
	display[newId] = self
	self.id = newId
end

function Node:retain()
	if OnPreview then

	else
		self.node:retain()
	end
end

function Node:setBlendMode(blendMode)
	self.blendMode = blendMode
	if OnPreview then
	else
		if self.type == "Sprite" then
			if blendMode == "기본" then
				Utils.updateBlend(self.node)
			elseif blendMode == "더하기" then 
				self.node:setBlendFunc(GL_ONE, GL_ONE)
			elseif blendMode == "빼기" then 
				self.node:setBlendFunc(GL_ZERO, GL_ONE_MINUS_SRC_COLOR)
			elseif blendMode == "배타" then 
				self.node:setBlendFunc(GL_ONE_MINUS_DST_COLOR, GL_ONE_MINUS_SRC_COLOR)
			elseif blendMode == "곱하기" then 
				self.node:setBlendFunc(GL_ZERO, GL_SRC_COLOR)
			elseif blendMode == "반전" then 
				self.node:setBlendFunc(GL_ONE_MINUS_DST_COLOR, GL_ZERO)
			elseif blendMode == "스크린" then 
				self.node:setBlendFunc(GL_ONE_MINUS_DST_COLOR, GL_ONE)
			elseif blendMode == "선광원" then 
				self.node:setBlendFunc(GL_ONE, GL_SRC_COLOR)
			end
		end
	end
end


function Node:setIncludeScreenShot(b)
	self.includeScreenShot = b
end

function Node:setZ(z)
	self.zOrder = z
	if OnPreview then
	else
		self.node:setLocalZOrder(z)
	end
end

function Node:setFlip(x,y)
	if OnPreview then
		if x then
			self.scaleX = self.scaleX * -1
		end 
		if y then
			self.scaleY = self.scaleY * -1
		end 
	else
		--self.node:setFlippedX(x)
		--self.node:setFlippedY(y)
		local sx = self.node:getScaleX()
		local sy = self.node:getScaleY()

		if x then
			sx = sx * -1
		end 
		if y then
			sy = sy * -1
		end 

		self.node:setScale(sx,sy)
	end
end

function Node:setVisible(v)
	self.visible = v
	if OnPreview then
	else
		self.node:setVisible(v)
	end
end

function Node:isVisible()
	if OnPreview then
		return self.visible
	else
		return self.node:isVisible()
	end
end

function Node:setPreserve(v)
	self.isPreserve = v
	if OnPreview then
	else
	end	
end

function Node:removeSelf(cleanup)
	if OnPreview then
		if self.parent then
			k,v = self.parent:findChild(self.id)
			if k then
				table.remove(self.parent._children,k)
				self.parent = nil

				if cleanup ~= false then
					self.node = nil
				end
			end
		end
	else
		try{
			function()
				self.node:removeFromParent()
			end,
			catch{function(error)
				print(" error self.node:removeFromParent ")
			end}
		}
		self.parent = nil
		if cleanup ~= false then
			self.node = nil
		end
	end
end

function Node:children()
	if OnPreview then
		return self._children
	else
		local ret = {}
		local children = {}
		try{
			function()
				children = self.node:getChildren()
			end,
			catch{function(error)end}
		}
		for k,v in ipairs(children)do
			table.insert(ret,v.obj)
		end
		return ret
	end
end

function Node:setContentSize(x,y)
	if x ==nil or y==nil then 
		return
	end
	if OnPreview then
		if self.type == "ColorLayer" then
			self.width  = x
			self.height = y
		end
	else
		self.width  = x
		self.height = y
		self.node:setContentSize(cc.size(x,y))
	end
end

function Node:findChild(idx)
	if OnPreview then
		for k,v in ipairs(self._children) do
			if v.id == idx then
				return k,v
			end
		end
	else
	end
end

function Node:addChild(node)
	node.parent = self
	if OnPreview then
		table.insert(self._children,node)
	else
		self.node:addChild(node.node)
	end

	node:setPosition(node._x,node._y)
	node:setScale(node.scaleX,node.scaleY)
end

function Node:removeChild(node)
	if OnPreview then

	else
		self.node:removeChild(node.node)
		node.node = nil
	end
end

function Node:removeAllChildren()
	if OnPreview then

	else
		self.node:removeAllChildren(true)
	end
end

function Node:position()
	--if OnPreview then
	return tonumber(self._x) or 0,tonumber(self._y) or 0
	--else
	--	return self.node:getPositionX() , self.node:getPositionY()
	--end
end

function Node:setAnchorPoint(x,y)
	self.anchorX = tonumber(x)
	self.anchorY = tonumber(y)
	if OnPreview then
	else
		self.node:setAnchorPoint(cc.p(x,y))
	end
end

function Node:anchor()
	if OnPreview then
		return tonumber(self.anchorX) or 0.5,tonumber(self.anchorY) or 0.5
	else
		local p = self.node:getAnchorPoint()
		return p.x,p.y
	end
end

function Node:setPositionX(x)
	--[[
	self._x = x
	if OnPreview then
		self.x = x
	else
		self.node:setPositionX(tonumber(x))
	end
	]]
	self:setPosition(x,self._y)
end

function Node:setPositionY(y)
	self:setPosition(self._x,y)
--[[
	self._y = y
	if OnPreview then
		self.y = y
	else
		local height = WIN_HEIGHT
		if self.parent then
			height = self.parent:contentSize().height
		end
		self.node:setPositionY(height-tonumber(y))
	end
]]
end

function Node:setPosition(x,y)
	self._x = x
	self._y = y

	if OnPreview then
		self.x = x
		self.y = y
	else
		x = x/SCALE_FACTOR()
		y = y/SCALE_FACTOR()

		local height = WIN_HEIGHT
		local dx = 0
		local dy = 0
		if self.parent then
			local ax,ay,width

			if self.parent.type ~= "Scene" then
				width  = self.parent:contentSize().width
				height = self.parent:contentSize().height
				ax,ay  = self.parent:anchor()
			else
				width = WIN_WIDTH
				ax,ay = 0,1
			end

			dx = width*ax
			dy = height*(1-ay)
		end
		self.node:setPosition(tonumber(x)+dx,height-tonumber(y)-dy)
	end
end

function Node:setScaleX(x)
	self.scaleX = x
	if OnPreview then
	else
		self.node:setScaleX(tonumber(x))
	end
end

function Node:setScaleY(y)
	self.scaleY = y
	if OnPreview then
	else
		self.node:setScaleY(tonumber(y))
	end
end

function Node:setScale(x,y)
	if y == nil and tonumber(x) == nil then 
	end
	self.scaleX = x
	self.scaleY = y
	if OnPreview then
	else
		x = x/SCALE_FACTOR()
		y = y/SCALE_FACTOR()
		self.node:setScale(tonumber(x),tonumber(y))
	end
end

function Node:parentSize()
	local psx,psy
	local ps = {width=WIN_WIDTH,height=WIN_HEIGHT}
	if self.parent then
		ps = self.parent:contentSize()
		psx,psy = self:parentsNodeScale(self.parent)
		ps.width  = ps.width * psx
		ps.height = ps.height * psy
	end
	return ps
end

function Node:scale()
	if OnPreview then
		return tonumber(self.scaleX) or 1,tonumber(self.scaleY) or 1
	else
		return self.node:getScaleX(),self.node:getScaleY()
	end
end

function Node:contentSize()
	if OnPreview then
		if self.type == "Sprite" then
			local s = PiniLuaHelper:imageSize(self.path);
			return {width=s[0],height=s[1]}
		elseif self.type=="ColorLayer" then
			return {width=self.width,height=self.height}
		elseif self.type=="Label" then
			local s = PiniLuaHelper:fontSize(self.text,self.size,self.font)
			return {width=s[0],height=s[1]}
		elseif self.type=="VideoPlayer" then
			return {width=1,height=1}
		elseif self.type=="TextInput" then
			local s = PiniLuaHelper:fontSize(self.value,self.size,self.font)
			return {width=s[0],height=s[1]}
		else
			return {width=0,height=0}
		end
	else
		if self.type=="VideoPlayer" then
			return {width=self.node:getWidth(),height=self.node:getHeight()}
		else
			local size = self.node:getContentSize();
			if self.type=="Label" then
				if self.text ~= " " then
					size.width = size.width-2
				else
					size.width = size.width + self.size / 3
				end 
			end
			return size;
		end
	end
end

function Node:parentsNodeScale(node)
	if OnPreview then
		return 1,1
	end

	if node == nil then
		node = self
	end

	local scaleX,scaleY
	scaleX,scaleY = node:scale()
	if node.parent then
		local sx,sy
		sx,sy = self:parentsNodeScale(node.parent)
		scaleX = scaleX * sx
		scaleY = scaleY * sy
	end
	return scaleX,scaleY
end

function Node:setColor(r,g,b)
	self.color = {r,g,b}
	if OnPreview then
	else
		if self.type == "Label" then
			self.node:setTextColor(cc.c3b(r,g,b))
		else
			self.node:setColor(cc.c3b(r,g,b))
		end
	end
end

function Node:getColor()
	if OnPreview then
		return self.color
	else
		local c =  self.node:getColor()
		return {c.r,c.g,c.b}
	end
end

function Node:setOpacity(a)
	self.opacity = a
	if OnPreview then
	else
		try{function()
			self.node:setOpacity(a)
		end,catch{function(error)print(error)end}}
	end
end

function Node:setRotate(angle)
	self.rotate = tonumber(angle)
	if OnPreview then
	else
		self.node:setRotation(angle)
	end
end

function Node:getRotate()
	if OnPreview then
		return self.rotate
	else
		return self.node:getRotation()
	end
end

function Node:ActiveActions()
	if OnPreview then
		return 0
	else
		return self.node:getNumberOfRunningActions()
	end
end

function Node:StopAction()
	self.onAnim = false
	if OnPreview then
	else
		self.node:stopAllActions()
	end
end

function Node:setFlippedY(b)
	if OnPreview then
	else
		self.node:setFlippedY(b)
	end
end

---------------------------------------------
-- Clipping Node
---------------------------------------------
local ClippingNode = class(Node)
function ClippingNode:init(id)
	self.id = id
	self.type = "ClippingNode"
	self:initialize()
	if OnPreview then
	else
		self.node = cc.ClippingNode:create()
		self.node.obj = self
	end
	self:initEventHandler()
	return true

end
function ClippingNode:gen(v)
	local n = ClippingNode(v.id)
	n:OverrideDefault(v)

	if v.clipXpos and v.clipYpos and v.clipWidth and v.clipHeight then
		n:setClippingSize(v.clipXpos, v.clipYpos, v.clipWidth, v.clipHeight)
	end

	return n
end

function ClippingNode:setClippingSize(x,y,w,h)
	x = x or 0
	y = y or 0
	if w ==nil or h==nil then 
		return
	end
	if OnPreview then
	else
		if self.drawNode then
			self.drawNode = nil
		end

		self.clipXpos = x
		self.clipYpos = y
		self.clipWidth  = w
		self.clipHeight = h

		local rect = {cc.p(x -w*0.5,y -h*0.5), cc.p(x + w*0.5,y -h*0.5), cc.p(x + w*0.5, y + h*0.5), cc.p(x -w*0.5, y + h*0.5)}

		self.drawNode = cc.DrawNode:create()
		self.drawNode:drawPolygon(rect, 4, cc.c4f(1,1,1,1), 0, cc.c4f(1,0,0,1))
		self.node:setStencil(self.drawNode)
	end
end
---------------------------------------------
-- Sprite 
---------------------------------------------
local Sprite = class(Node)
function Sprite:init(id,path,overoll,immediately)
	self.id = id
	self.type = "Sprite"
	self.path = path
	self.overoll = overoll
	self:initialize()
	if OnPreview then
	else
		if type(path) == "string" then
			local fname = FILES["image/"..path]
			if fileUtil:fileExist(ROOT_PATH+path) then
				fname = ROOT_PATH+path
			elseif fileUtil:fileExist(path) and fileUtil:fileExist("res.prz") == false then
				fname = path
			end
			if fname == nil then
				return false
			end
			if immediately then
				if fileUtil:fileExist(fname) then
					self.node = cc.Sprite:create(fname)
				else
					self.node = pini:getSpriteFromZips(path)
				end
			else
				if fname then
					self.node = Utils.CreateSpriteAsync(fname,"res.prz",pini.password)
				end
				local imgInfo = IMAGES["image/"..path] or IMAGES[path]
				if imgInfo then
					self:setContentSize(imgInfo["w"],imgInfo["h"])
				end
			end
		else
			self.node = cc.Sprite:createWithTexture(path)
		end
		if self.node == nil then
			return false
		end
		self.node.obj = self
		self.node:setCascadeColorEnabled(true)
	end
	self:setPosition(0,0)
	self:initEventHandler()
	return true
end
function Sprite:gen(v)
	local n = Sprite(v.id,v.path,v.overoll,true)
	n:OverrideDefault(v)

	n:setColor(v.color[1],v.color[2],v.color[3])
	n.connect = v.connect
	
	return n
end
function Sprite:setSprite(path)
	if self.isExited then return end
	if OnPreview then
		self.path = path
	else
		local cache = cc.Director:getInstance():getTextureCache()
		local texture = nil
		if fileUtil:fileExist(FILES["image/"..path]) then
			texture = cache:addImage(FILES["image/"..path])
		elseif fileUtil:fileExist(path) then
			texture = cache:addImage(path)
		end
		if texture == nil then
			try{
				function()
					local sprite = pini:getSpriteFromZips(path)
					if sprite then
						texture = sprite:getTexture()
					end
				end,
				catch{function(error)end}
			}
		end
		if texture then
			self.node:setTexture(texture)
			self.node:setTextureRect(texture:getContentSize())
		end
	end
end

function Sprite:getTextureName()
	if self.isExited then return 0 end
	if OnPreview then
	else
		return self.node:getTexture():getName()
	end
end
---------------------------------------------
-- Slider 
---------------------------------------------
local Slider = class(Node)
function Slider:init(id,img1,img2,img3)
	self.id = id
	self.type = "Slider"
	self.img1 = img1
	self.img2 = img2
	self.img3 = img3
	self.value = 0
	self:initialize()
	if OnPreview then

	else
		local _img1 = FILES["image/"..img1] or img1
		local _img2 = FILES["image/"..img2] or img2
		local _img3 = FILES["image/"..img3] or img3

		if fileUtil:fileExist(_img1) and 
			fileUtil:fileExist(_img2) and 
			fileUtil:fileExist(_img3) then
			self.node = cc.ControlSlider:create(_img1,_img2,_img3)
		end

		if self.node == nil then
			local i1 = pini:getSpriteFromZips(img1)
			local i2 = pini:getSpriteFromZips(img2)
			local i3 = pini:getSpriteFromZips(img3)
			self.node = cc.ControlSlider:create(i1,i2,i3)
		end

		if self.node == nil then
			return false
		end
		self.node:setMinimumValue(0.0)
		self.node:setMaximumValue(100.0)
	end
	self:initEventHandler()
	return true
end
function Slider:gen(v)
	local n = Slider(v.id,v.img1,v.img2,v.img3)
	n:OverrideDefault(v)
	return n
end

function Slider:getValue()
	if OnPreview then
		return self.value
	else
		return self.node:getValue()
	end
end

function Slider:setValue(v)
	self.value = v
	if OnPreview then
	else
		self.node:setValue(v)
	end
end

function Slider:setEnabled(v)
	if OnPreview then
	else
		self.node:setEnabled(v)
	end
end

---------------------------------------------
-- Scene 
---------------------------------------------
local Scene=class()
function Scene:init()
	self.type = "Scene"
	self.keyboards = {}
	self.touchGestures = {}
	if OnPreview then
	else
		self.scene = cc.Scene:create()
		self.layer = cc.Layer:create()

		local function onKeyReleased(keyCode, event)
			local node = event:getCurrentTarget()

			if keyCode == 14 then
				-- 이벤트 처리에서 직접 예외를 거는 것은 좋은 처리가 아니나
				-- 일정상, 직접 Ctrl 스킵 처리 로직을 추가합니다.

				pini:StopTimer("PINI_CtrlSkip")
			end

			for k,v in pairs(self.keyboards) do
				if v and v["stop"]==nil then 
					v["func"](0,keyCode,v["arg"])
				end
			end
		end

		local function onKeyPressed(keyCode, event)
			local node = event:getCurrentTarget()

			if keyCode == 14 then
				-- 이벤트 처리에서 직접 예외를 거는 것은 좋은 처리가 아니나
				-- 일정상, 직접 Ctrl 스킵 처리 로직을 추가합니다.

				if pini.SkipAllowStatus then
					pini.Timer("PINI_CtrlSkip",0,function(t)
						dialogTouch = pini:FindNode("PINI_Dialog_touch")
						if dialogTouch then
							dialogTouch.onTouchUp(nil,dialogTouch)
						end
						clickTouch = pini:FindNode("ClickWait")
						if clickTouch then
							clickTouch.onTouchUp(nil,clickTouch)
						end
					end,true,nil,nil):run()
				end
			end

			for k,v in pairs(self.keyboards) do
				if v and v["stop"]==nil then 
					v["func"](1,keyCode,v["arg"])
				end
			end
		end

		local function onMouseClick(e)
			if e:getMouseButton() == 0 then
				return false
			end

			local x = e:getCursorX()
			local y = e:getCursorY()

			try{
				function()
					for k,v in pairs(pini.TouchManager.callbacks.touchBeganCallbacks) do
						v(x, y, e:getMouseButton())
					end
				end,
				catch{function(error)
					print(error)
				end}
			}

			for k,v in pairs(self.keyboards) do
				if v and v["stop"]==nil then 
					v["func"](1,e:getMouseButton()+1000,v["arg"],x,y)
				end
			end

			return true
		end

		local function onMouseRelease(e)
			local x = e:getCursorX()
			local y = e:getCursorY()

			try{
				function()
					for k,v in pairs(pini.TouchManager.callbacks.touchEndedCallbacks) do
						v(x, y, e:getMouseButton())
					end
				end,
				catch{function(error)
					print(error)
				end}
			}

			for k,v in pairs(self.keyboards) do
				if v and v["stop"]==nil then 
					v["func"](0,e:getMouseButton()+1000,v["arg"],x,y)
				end
			end

			return true
		end

		local function onMouseScroll(e)
			local x = e:getScrollX()
			local y = e:getScrollY()

			-- 이벤트 처리에서 직접 예외를 거는 것은 좋은 처리가 아니나
			-- 일정상, 직접 백로그 스크롤 처리 로직을 추가합니다..

			try{
				function()
					for k,v in pairs(pini.TouchManager.callbacks.touchMovedCallbacks) do
						v(0, 0, y)
					end
				end,
				catch{function(error)
					print(error)
				end}
			}

			result = pini.Backlog:runScrollEvent(y * 30)

			if not result then
				for k,v in pairs(self.keyboards) do
					if v and v["stop"]==nil then 
						v["func"](1,1005,v["arg"],x,y)
					end
				end
			end
			return true
		end

		local function onMouseMove(e)
			local x = e:getCursorX()
			local y = e:getCursorY()

			try{
				function()
					for k,v in pairs(pini.TouchManager.callbacks.touchMovedCallbacks) do
						v(x, y, 0)
					end
				end,
				catch{function(error)
					print(error)
				end}
			}

			for k,v in pairs(pini._regist_.Display) do
				if v and v.overoll and v.overoll:len() > 0 then
					local tloc = v.node:convertToNodeSpace(cc.p(x,y));
					local b = v:contentSize()
					if tloc.x > 0 and tloc.y > 0 and tloc.x < b.width and tloc.y < b.height then
						v:setSprite(v.overoll)
					else
						v:setSprite(v.path)
					end
				end
			end
		end

		local eventDispatcher = self.layer:getEventDispatcher()

		local listener = cc.EventListenerKeyboard:create()
		listener:registerScriptHandler(onKeyPressed, cc.Handler.EVENT_KEYBOARD_PRESSED )
		listener:registerScriptHandler(onKeyReleased, cc.Handler.EVENT_KEYBOARD_RELEASED )
		eventDispatcher:addEventListenerWithSceneGraphPriority(listener, self.layer)

		local listener = cc.EventListenerMouse:create()
		listener:registerScriptHandler(onMouseClick, cc.Handler.EVENT_MOUSE_DOWN )
		listener:registerScriptHandler(onMouseRelease, cc.Handler.EVENT_MOUSE_UP )
		listener:registerScriptHandler(onMouseScroll, cc.Handler.EVENT_MOUSE_SCROLL )
		listener:registerScriptHandler(onMouseMove, cc.Handler.EVENT_MOUSE_MOVE )
		eventDispatcher:addEventListenerWithSceneGraphPriority(listener, self.layer)

		self.scene:addChild(self.layer)
		if cc.Director:getInstance():getRunningScene() then
			cc.Director:getInstance():replaceScene(self.scene)
		else
			cc.Director:getInstance():runWithScene(self.scene)
		end

		local function onNodeEvent(tag)
			if tag == "exit" then
				pini:ClearDisplay()
			end
		end
		self.scene:registerScriptHandler(onNodeEvent)
	end
	pini:SetScene(self)
	return true
end
function Scene:registKeyboard(id,func,arg,stop)
	self.keyboards[id] = {
		func=func,
		arg=arg,
		stop=stop
	}
end
function Scene:unregistKeyboard(id)
	self.keyboards[id] = nil
end
function Scene:pauseAllKeyboard(id)
	for k,v in pairs(self.keyboards) do
		v["stop"] = id
	end
end
function Scene:playAllKeyboard(id)
	for k,v in pairs(self.keyboards) do
		if id == v["stop"] then
			v["stop"] = nil
		end
	end
end
function Scene:registTouchGesture(id,func,stop)
	self.touchGestures[id] = {
		func=func,
		stop=stop
	}
end
function Scene:unregistTouchGesture(id)
	self.touchGestures[id] = nil
end
function Scene:pauseAllTouchGesture(id)
	for k,v in pairs(self.touchGestures) do
		v["stop"] = id
	end
end
function Scene:playAllTouchGesture(id)
	for k,v in pairs(self.touchGestures) do
		if id == v["stop"] then
			v["stop"] = nil
		end
	end
end
function Scene:addChild(node)
	if OnPreview then
	else
		self.layer:addChild(node.node)
		node.parent = self
	end
end
function Scene:contentSize()
	return {width=WIN_WIDTH,height=WIN_HEIGHT}
end
function Scene:scale()
	return 1,1
end
function Scene:removeChild(node)
	if OnPreview then

	else
		self.layer:removeChild(node.node)
		node.node = nil
	end
end
function Scene:clear()
	if OnPreview then

	else
		try{
			function()
				self.layer:removeAllChildren(true)
			end,
			catch{function(error) print(error) end}
		}
	end
end
function Scene:visit()
	if OnPreview then

	else
		self.layer:visit()
	end
end

---------------------------------------------
-- ColorRect 
---------------------------------------------
local ColorLayer=class(Node)
function ColorLayer:init(id,r,g,b,a,w,h)
	-- 단순 단색 사각형을 표기하는 객체입니디ㅏ.
	self.id = id
	self.type = "ColorLayer"
	
	self:initialize()
	self.width  = w
	self.height = h
	self.color  = {r,g,b}
	self.opacity = a
	self.anchorX = 0.0
	self.anchorY = 1.0

	if OnPreview then
	else
		self.node = cc.LayerColor:create(cc.c4b(r,g,b,a),w,h)
		self.node:setAnchorPoint(cc.p(0,0))
		self.node.obj = self
	end
	self:initEventHandler()
	return true
end

function ColorLayer:gen(v)
	local n = ColorLayer(v.id,v.color[1],v.color[2],v.color[3],v.opacity,v.width,v.height)
	n:OverrideDefault(v)
	n.connect = v.connect
	return n
end
---------------------------------------------
-- label 
---------------------------------------------
local Label = class(Node)
function Label:init(id,str,fnt,size,contentSize)
	self.id = id
	self.type = "Label"
	
	contentSize = contentSize or {0,0}

	self:initialize()
	self.text = str
	self.font = fnt
	self.size = size
	
	if OnPreview then
	else
		local lp = pini.ManagedNodePool["label"]

		self.node = nil
		local a = self.text
		local b = self.font
		local c = tostring(self.size)
		if lp[a] and lp[a][b] and lp[a][b][c] and #lp[a][b][c] > 0 then
			self.node = lp[a][b][c][1]
			Utils.AUTORELEASE(self.node)
			table.remove(lp[a][b][c],1)
		else
			if fileUtil:fileExist(fnt..".fnt") then
				fnt = fnt..".fnt"
			elseif FILES["font/"..fnt] then
				fnt = FILES["font/"..fnt]
			elseif FILES["font/"..fnt..".ttf"] then
				fnt = FILES["font/"..fnt..".ttf"]
			elseif fileUtil:fileExist(fnt) == false then
				fnt = "NanumBarunGothic.ttf"
			end
			self.node = cc.Label:createWithTTF(str, fnt, size, cc.size(contentSize[1],contentSize[2]))
		end
		self.node.obj = self
	end
	self:initEventHandler()
	return true
end
function Label:gen(v)
	local n = Label(v.id,v.text,v.font,v.size)
	n:OverrideDefault(v)
	n:setColor(v.color[1],v.color[2],v.color[3])

	if v.stroke then
		n:setStroke(v.stroke[1],v.stroke[2],v.stroke[3],v.stroke[4],v.stroke[5])
	end

	if v.shadow then
		n:setShadow(v.shadow[1],v.shadow[2],v.shadow[3],v.shadow[4],v.shadow[5],v.shadow[6],v.shadow[7])
	end

	if v.glow then
		n:setGlow(v.glow[1],v.glow[2],v.glow[3],v.glow[4])
	end

	return n
end

function Label:registManagedNode()
	if OnPreview then
	else
		local targetNode = self.node
		targetNode:retain()
		local function onNodeEvent(tag)
			if self.isExited == nil then
				if tag == "exit" then
					local a = self.text
					local b = self.font
					local c = tostring(self.size)
					local lp = pini.ManagedNodePool["label"]
					lp[a] = lp[a] or {}
					lp[a][b] = lp[a][b] or {}
					lp[a][b][c] = lp[a][b][c] or {}

					if #lp[a][b][c] <= 5 then
						table.insert(lp[a][b][c],targetNode)
					end
				end
			end
		end
		targetNode:registerScriptHandler(onNodeEvent)
	end
end

function Label:string(v)
	if OnPreview then
		return self.text
	else
		return self.node:getString()
	end
end

function Label:setString(v)
	if OnPreview then
		self.text = v
	else
		self.node:setString(v)
	end
end

function Label:setStroke(r,g,b,a,w)
	if OnPreview then
	else
		self.stroke = {r,g,b,a,w}
		self.node:enableOutline(cc.c4b(r,g,b,a),w)
	end
end

function Label:setShadow(r,g,b,a,x,y,w)
	if OnPreview then
	else
		self.shadow = {r,g,b,a,x,y,w}
		self.node:enableShadow(cc.c4b(r,g,b,a),cc.size(x,y),w)
	end
end

function Label:setGlow(r,g,b,a)
	if OnPreview then
	else
		self.glow = {r,g,b,a}
		self.node:enableGlow(cc.c4b(r,g,b,a))
	end
end

-----------------------------------------------
----- VideoPlayer
-----------------------------------------------
local VideoPlayer = class(Node)
function VideoPlayer:init(id,path)
	self.type = "VideoPlayer"
	self.path = path
	self.id = id
	self:initialize()
	if OnPreview then
	else
		self.node = npini.VideoPlayer:create(FILES[path])
	end
	self:initEventHandler()
	return true
end
function VideoPlayer:gen(v)
	local n = VideoPlayer(v.id,v.path)
	n:OverrideDefault(v)
	n:setColor(v.color[1],v.color[2],v.color[3])
	n:play()
	return n
end
function VideoPlayer:play()
	if OnPreview then
	else
		self.node:play()
	end
end

function VideoPlayer:stop()
	if OnPreview then
	else
		self.node:stop()
	end
end

function VideoPlayer:setCallback(func)
	if OnPreview then
	else
		self.node:setCallback(func)
	end
end
---------------------------------------------
--TextInput
---------------------------------------------
function ttfTest(fnt)
	local list = {fnt..".ttf",fnt}

	if FILES["font/"..fnt..".TTF"] then
		table.insert(list,FILES["font/"..fnt..".TTF"])
	end
	if FILES["font/"..fnt..".ttf"] then
		table.insert(list,FILES["font/"..fnt..".ttf"])
	end
	if FILES["font/"..fnt] then
		table.insert(list,FILES["font/"..fnt])
	end

	for k,v in ipairs(list) do
		if v then
			local founded = false
			try{
				function()
					if cc.Label:createWithTTF("str", v,10) then
						founded = true
					end
				end,
				catch{function(error)
					print "error on ttfTest()"
				end}
			}

			if founded then
				return v
			end
		end
	end
	return "Arial"
end
local TextInput = class(Label)
function TextInput:init(id,holder,value,fnt,size,isGUI)
	self.id = id
	
	self:initialize()
	self.value = value
	self.holder = holder
	self.font = fnt
	self.size = size
	
	self.type = "TextInput"
	if OnPreview then
	else
		self.node = npini.TextInput:create(self.holder, ttfTest(fnt), size)
		self.node.obj = self

		if value:len() > 0 then
			self:setString(value)
		end
	end
	self:initEventHandler()
	self.onTouchUp = function(location,v)
		v:setEnableIME(true)
	end
	self.onTouchMiss = function(location,v)
		v:setEnableIME(false)
	end

	if isGUI then
		self:setZ(9999999)
		self.touchPriority = GUI_PRIORITY
	end

	pini.TouchManager:registNode(self)
	return true
end
function TextInput:gen(v)
	local n = TextInput(v.id,v.holder,v.value,v.font,v.size)
	n:OverrideDefault(v)
	n:setColor(v.color[1],v.color[2],v.color[3])
	return n
end

function TextInput:setEnableIME(v)
	if OnPreview then
	else
		self.node:setEnableIME(v)
	end
end

function TextInput:string(v)
	if OnPreview then
		return self.value
	else
		return self.node:getString()
	end
end

function TextInput:setString(v)
	if OnPreview then
		self.value = v
	else
		self.node:setString(v)
	end
end

function TextInput:setMaxLength(v)
	if OnPreview then
	else
		self.node:setMaxLength(v)
	end
end

function TextInput:setPasswordMode(v)
	if OnPreview then
	else
		self.node:setPasswordMode(v)
	end
end

-----------------------------------------------
----- RenderTexture
-----------------------------------------------
local RenderTexture = class(Node)
function RenderTexture:init(id,w,h,renderList)
	self.type = "RenderTexture"
	self.id = id
	self.renderList = renderList
	self:initialize()
	self.width = w
	self.height = h
	if OnPreview then
	else
		self.node  = cc.RenderTexture:create(w, h, cc.TEXTURE2_D_PIXEL_FORMAT_RGB_A8888)
		self.timer = pini.Timer(pini:GetUUID(),0,self.update,nil,nil,{uid=id})
		self.timer:run()
	end
	self:setPosition(w*0.5,h*0.5)
	self:initEventHandler()
	self:registOnExit("PINI_RENDERTEXTURE_EXIT",self.onExit)
	return true
end
function RenderTexture:gen(v)
	local n = RenderTexture(v.id,v.width,v.height,v.renderList)
	n:OverrideDefault(v)
	n:setPosition(v.width,0)
	return n
end
function RenderTexture:onExit()
	self.timer:stop()
	for k,v in ipairs(self.renderList) do
		local v = pini:FindNode(v)
		if v and v.isDestroyed == false then
			v:setVisible(true)
		end
	end
end
function RenderTexture:update()
	local rt = pini:FindNode( self.userdata.uid )
	if rt then
		rt:render(0,0,0,0)
	else
		self:stop()
	end
end

function RenderTexture:isRenderNode(node)
	if self.renderList == true then
		return true
	end
	for k,v in ipairs(self.renderList) do
		local v = pini:FindNode(v)
		if v and v.isDestroyed == false then
			if v == node then
				return true
			end
		end
	end
	return false
end

function RenderTexture:render(r,g,b,a)
	if OnPreview then
	else
		local noneVisible = {}
		for k,v in pairs(pini._regist_.Display) do
			if not self:isRenderNode(v) and v:isVisible() then
				v:setVisible(false)
				table.insert(noneVisible,v)
			end
		end

		for k,v in ipairs(self.renderList) do
			local v = pini:FindNode(v)
			if v and v.isDestroyed == false then
				v:setVisible(true)
			end
		end

		self.node:clear(r,g,b,a)
		self.node:begin()

		pini:scene():visit()

		self.node:endToLua()
		Utils.forceRender()

		for k,v in ipairs(noneVisible) do
			v:setVisible(true)
		end
		for k,v in ipairs(self.renderList) do
			local v = pini:FindNode(v)
			if v and v.isDestroyed == false then
				v:setVisible(false)
			end
		end

	end
end

---------------------------------------------
-- Global Timer 
---------------------------------------------
local GlobalTimer = class()
function GlobalTimer:init()
	-- Timer 를 돌리기 위한 단일 고정타이머입니다.
	self.entry = nil
	self:run()
	return true
end

function GlobalTimer:run()
	if OnPreview then
	else
		self.entry = SCHEDULER:scheduleScriptFunc(function(dt)
			local timers = pini._regist_.Timers
		
			for k,t in pairs(timers) do
				if t.playing == false then
					return 
				end
				t.lastTime = t.lastTime - dt
				t.realdt = t.realdt + dt

				t.dt = dt
				if t.lastTime < 0.0 then
					t.lastTime = t.lastTime + t.time
					local realdt = t.realdt
					t.realdt = 0
					try{
						function()
							t.func(t,realdt)
						end,
						catch{function(error)
							print(error)
						end}
					}
					if t.count then
						t.count = t.count - 1
						if t.count == 0 then
							t:stop()
						end
					end
					if t.rep == false then
						t:stop()
					end
				end
			end
		end, 0, false)
	end
end

---------------------------------------------
-- Timer 
---------------------------------------------
local Timer = class()
function Timer:init(id,time,func,re,count,userdata)
	self.id = id
	self.time = tonumber(time)
	self.func = func
	self.rep = re
	self.count = count
	self.playing = false
	self.userdata = userdata or {}
	return true
end
function Timer:run()
	self.id = self.id or pini:GetUUID()
	self.playing = true
	if OnPreview then
		self.dt = 0
		self.func(self)
	else
		self.lastTime = self.time
		self.realdt = 0
	end
	if self.id then
		pini:RegistTimer(self)
	end
end
function Timer:stop()
	self.playing = false
	pini:UnregistTimer(self)
end

--##########################################################################
-- 터치 매니저
--##########################################################################
local TouchManager = nil
if OnPreview then
	TouchManager = {
		SetScene = function(scene)
		end,
		clearNode = function()
		end,
		removeNode = function(node)
		end,
		registNode = function(node)
		end,
		onTouchBegan = function (touch, event)
		end,
		onTouchMoved = function (touch, event)
		end,
		onTouchEnded = function (touch, event)
		end
	}
else
	TouchManager = {
		nodes = {},
		count = 0,
		touchNode = nil,
		lastClicked = {},
		touchGesture = {
			touches = {},
			currentTouchCount = 0,
			activeTouchCount = 0,
			touchStartAvgX = 0,
			touchStartAvgY = 0,
			touchEndAvgX = 0,
			touchEndAvgY = 0,
			touchStartClock = 0,
			touchStartDistance = -1,
			touchEndDistance = -1,
		},
		callbacks = {
			touchBeganCallbacks = {},
			touchMovedCallbacks = {},
			touchEndedCallbacks = {},
			multiTouchBeganCallbacks = {},
			multiTouchMovedCallbacks = {},
			multiTouchEndedCallbacks = {},
			multiTouchCanceledCallbacks = {},
		},
		SetScene = function(self,scene)
			scene = scene.scene
			
			self:clearNode()
			local eventDispatcher = scene:getEventDispatcher()
			
			local listener = cc.EventListenerTouchOneByOne:create()
			listener:registerScriptHandler(self.onTouchBegan,cc.Handler.EVENT_TOUCH_BEGAN )
			listener:registerScriptHandler(self.onTouchMoved,cc.Handler.EVENT_TOUCH_MOVED )
			listener:registerScriptHandler(self.onTouchEnded,cc.Handler.EVENT_TOUCH_ENDED )
			eventDispatcher:addEventListenerWithSceneGraphPriority(listener, scene)
	
			local listener = cc.EventListenerTouchAllAtOnce:create()
			listener:registerScriptHandler(self.onMultiTouchBegan,cc.Handler.EVENT_TOUCHES_BEGAN)
			listener:registerScriptHandler(self.onMultiTouchMoved,cc.Handler.EVENT_TOUCHES_MOVED)
			listener:registerScriptHandler(self.onMultiTouchEnded,cc.Handler.EVENT_TOUCHES_ENDED)
			listener:registerScriptHandler(self.onMultiTouchCanceled,cc.Handler.EVENT_TOUCHES_CANCELLED)
			eventDispatcher:addEventListenerWithSceneGraphPriority(listener, scene)

		end,
		clearNode = function(self)
			self.nodes = {}
		end,
		removeNode = function(self,node)
			for k,v in ipairs(self.nodes) do
				if v == node then
					v.touchRegisted = nil
					table.remove(self.nodes,k)
					if self.touchNode == v then
						self.touchNode = nil
					end
					break
				end
			end
		end,
		registNode = function(self,node)
			local function onNodeExitEvent()
				self:removeNode(node)
			end
			node:registOnExit("PINI_TOUCHMANAGER_EXIT",onNodeExitEvent)
			node.touchIdx = self.count
			self.count = self.count+1
			table.insert(self.nodes,node)
			table.sort(self.nodes,function(a,b)
				if a.perfectPriority or b.perfectPriority then
					return a.touchIdx > b.touchIdx
				elseif a.touchPriority == b.touchPriority then
					return a.touchIdx > b.touchIdx
				else
					return a.touchPriority > b.touchPriority
				end
			end)
			node.touchRegisted = true
		end,

		touchesCenter = function(touches)
			local x = 0
			local y = 0
			local count = 0
			for k,v in pairs(touches) do
				local loc = v:getLocation()
				x = x + loc.x
				y = y + loc.y
				count = count + 1
			end
			if count == 0 then
				return 0,0
			end
			x = x / count
			y = y / count
			return x,y
		end,

		touchDistanceSquare = function(touches)
			if table.Count(touches) ~= 2 then
				return -1
			end

			local x0 = nil
			local y0 = nil
			local x1 = nil
			local y1 = nil

			for k,v in pairs(touches) do
				if x0 then
					x1 = v:getLocation().x
					y1 = v:getLocation().y
				else
					x0 = v:getLocation().x
					y0 = v:getLocation().y
				end
			end

			local dx = x0 - x1
			local dy = y0 - y1

			return dx * dx + dy * dy
		end,

		onMultiTouchBegan = function(touches, event)
			local self = TouchManager
			local tg = self.touchGesture
			local count = table.getn(touches)
			tg.currentTouchCount = tg.currentTouchCount + count
			local counts = tg.currentTouchCount

			try{
				function()
					for k,v in pairs(self.callbacks.multiTouchBeganCallbacks) do
						v(touches)
					end
				end,
				catch{function(error)
					print(error)
				end}
			}


			for i,v in ipairs(touches) do
				tg.touches[v:getId()] = v
			end

			if tg.activeTouchCount < counts then
				tg.activeTouchCount = counts
				tg.touchStartAvgX,tg.touchStartAvgY = self.touchesCenter(tg.touches)
				tg.touchStartClock = os.clock()
				tg.touchStartDistance = self.touchDistanceSquare(tg.touches)
			end
		end,
		onMultiTouchMoved = function(touches, event)
			local self = TouchManager
			local count = table.getn(touches)

			try{
				function()
					for k,v in pairs(self.callbacks.multiTouchMovedCallbacks) do
						v(touches)
					end
				end,
				catch{function(error)
					print(error)
				end}
			}
		end,
		onMultiTouchEnded = function(touches, event)
			local self = TouchManager
			local tg = self.touchGesture
			local count = table.getn(touches)
			tg.currentTouchCount = tg.currentTouchCount - count
			local counts = tg.currentTouchCount

			try{
				function()
					for k,v in pairs(self.callbacks.multiTouchEndedCallbacks) do
						v(touches)
					end
				end,
				catch{function(error)
					print(error)
				end}
			}

			if counts == tg.activeTouchCount - 1 then
				tg.touchEndAvgX,tg.touchEndAvgY = self.touchesCenter(tg.touches)

				tg.touchEndDistance= self.touchDistanceSquare(tg.touches)
			end

			for i,v in ipairs(touches) do
				tg.touches[v:getId()] = nil
			end

			if counts == 0 then
				local sx, sy = tg.touchStartAvgX,tg.touchStartAvgY
				local ex, ey = tg.touchEndAvgX,tg.touchEndAvgY
				local dx, dy = ex-sx, ey-sy
				local dt = os.clock() - tg.touchStartClock
				local atc = tg.activeTouchCount
				local dd = math.sqrt(tg.touchEndDistance) - math.sqrt(tg.touchStartDistance)

				local onePointTouchAction = function(touch, event)
					local v = self.touchNode

					if v then
						local location = touch:getLocation()
						local tloc = v.node:convertToNodeSpace(location);
						local b = v:contentSize()
						if tloc.x > 0 and tloc.y > 0 and tloc.x < b.width and tloc.y < b.height then
							if v.onTouchUp then
								local func = v.onTouchUp
								pini.Timer(pini:GetUUID(),0,function()
									if func then
										func(location,v)
									end
								end,false):run()
							end
						end
						if v.node then
							local anim = pini.Anim.ScaleTo(0.2,v.sx,v.sy)
							anim:run(v)
						end

						for k,v2 in ipairs(self.nodes) do
							if v ~= v2 and v2.onTouchMiss then
								local func = v2.onTouchMiss
								v2:StopAction()
								AnimMgr:stop(v2)
								pini.Timer(pini:GetUUID(),0,function()
									if v2.isExited == nil then
										func(location,v2)
									end
								end,false):run()
							end
						end

						self.touchNode = nil
					end
				end

				local noticeTouchGesture = function(touchCount,touchType)
					if pini:scene().touchGestures ~= nil then
						for k,v in pairs(pini:scene().touchGestures) do
							if v and v["stop"]==nil then 
								v["func"](touchCount,touchType)
							end
						end
					end
				end

				local noMoveActions = function()
					if dt > 1.0 then
						noticeTouchGesture(atc,"롱터치")
					else
						if atc == 1 then
							onePointTouchAction(touches[1],event)
						else
							noticeTouchGesture(atc,"터치")
						end
					end					
				end

				if math.abs(dd) > 100 then
					if dd < 0 then
						noticeTouchGesture(atc,"축소")
					else
						noticeTouchGesture(atc,"확대")
					end
				elseif math.abs(dx) > math.abs(dy) then
					if math.abs(dx) < 30 then
						noMoveActions()
					else
						if dx < 0 then
							noticeTouchGesture(atc,"왼쪽")
						else
							noticeTouchGesture(atc,"오른쪽")
						end
					end
				else
					if math.abs(dy) < 30 then
						noMoveActions()
					else
						if dy < 0 then
							noticeTouchGesture(atc,"아래쪽")
						else
							noticeTouchGesture(atc,"위쪽")
						end
					end
				end

				tg.activeTouchCount = 0
				tg.touchStartAvgX = 0
				tg.touchStartAvgY = 0
				tg.touchEndAvgX = 0
				tg.touchEndAvgX = 0
			end
		end,
		onMultiTouchCanceled = function(touches, event)
			local self = TouchManager
			local tg = self.touchGesture
			local count = table.getn(touches)
			tg.currentTouchCount = tg.currentTouchCount - count
			local counts = tg.currentTouchCount

			try{
				function()
					for k,v in pairs(self.callbacks.multiTouchCanceledCallbacks) do
						v(touches)
					end
				end,
				catch{function(error)
					print(error)
				end}
			}

			tg.touches = {}
			if counts == 0 then
				tg.activeTouchCount = 0
				tg.touchStartAvgX = 0
				tg.touchStartAvgY = 0
				tg.touchEndAvgX = 0
				tg.touchEndAvgX = 0
			end
		end,

		onTouchBegan = function(touch, event)
			local self = TouchManager
			local nodes = self.nodes

			local location = touch:getLocation()

			x=location.x
			y=location.y

			try{
				function()
					for k,v in pairs(self.callbacks.touchBeganCallbacks) do
						v(x, y, 0)
					end
				end,
				catch{function(error)
					print(error)
				end}
			}

			self.lastClicked["x"] = x
			self.lastClicked["y"] = y
			self.lastClicked["dx"] = 0
			self.lastClicked["dy"] = 0

			pini:StopTimer("PINI_ScrollMomentum")

			if pini:scene().keyboards ~= nil then
				for k,v in pairs(pini:scene().keyboards) do
					if v and v["stop"]==nil then 
						v["func"](1,1000,v["arg"],x,y)
					end
				end
			end

			for k,v in ipairs(nodes) do
				local tloc = v.node:convertToNodeSpace(location)
				local b = v:contentSize()
				if tloc.x > 0 and tloc.y > 0 and tloc.x < b.width and tloc.y < b.height then
					self.touchNode = v

					if v.sx == nil then
						v.sx , v.sy = v:scale()
					end

					if v.onTouchDown then
						local func = v.onTouchDown
						pini.Timer(pini:GetUUID(),0,function()
							func(location,v)
						end,false,nil):run()
					end

					if v.onTouchAnim then
						if type(v.onTouchAnim) == "string" then
							if AnimMgr:isAnim(v.onTouchAnim) then
								AnimMgr:run(v.onTouchAnim,1,0,nil,0.01,nil,v)
							end
						else
							v.onTouchAnim:run(v)
						end
					else
						local anim = pini.Anim.ScaleTo(0.2,v.sx+(10/b.width),v.sy+(10/b.height))
						anim:run(v)
					end

					return true
				end
			end
			return true
		end,
		onTouchMoved = function (touch, event)
			local self = TouchManager

			local location = touch:getLocation()

			local x = location.x
			local y = location.y

			try{
				function()
					for k,v in pairs(self.callbacks.touchMovedCallbacks) do
						v(x, y)
					end
				end,
				catch{function(error)
					print(error)
				end}
			}

			local dx = x - self.lastClicked["x"]
			local dy = y - self.lastClicked["y"]

			if pini.Backlog.isShowing then
				pini.Backlog:runScrollEvent(dy)
			end

			self.lastClicked["x"] = x
			self.lastClicked["y"] = y
			self.lastClicked["dx"] = dx
			self.lastClicked["dy"] = dy

			local v = self.touchNode

			if v then
				local location = touch:getLocation()
				local tloc = v.node:convertToNodeSpace(location);
				local b = v:contentSize()
				if tloc.x > 0 and tloc.y > 0 and tloc.x < b.width and tloc.y < b.height then
				elseif v.node then
					local anim = pini.Anim.ScaleTo(0.2,v.sx,v.sy)
					anim:run(v)

					self.touchNode = nil
				end
			end
		end,
		onTouchEnded = function (touch, event)
			local self = TouchManager

			local location = touch:getLocation()

			x=location.x
			y=location.y

			try{
				function()
					for k,v in pairs(self.callbacks.touchEndedCallbacks) do
						v(x, y, 0)
					end
				end,
				catch{function(error)
					print(error)
				end}
			}

			if pini:scene().keyboards ~= nil then
				for k,v in pairs(pini:scene().keyboards) do
					if v and v["stop"]==nil then 
						v["func"](0,1000,v["arg"],x,y)
					end
				end
			end

			if pini.Backlog.isShowing and self.lastClicked["dy"] ~= 0 then
				pini.Timer("PINI_ScrollMomentum",0,function(t)
					if not pini.Backlog.isShowing then
						pini:StopTimer("PINI_ScrollMomentum")
					end
					t.userdata.dy = t.userdata.dy * 0.9
					if t.userdata.dy > -1 and t.userdata.dy < 1 then
						pini:StopTimer("PINI_ScrollMomentum")
					end

					pini.Backlog:runScrollEvent(t.userdata.dy)
				end,true,nil,{dy=self.lastClicked["dy"]}):run()
			end
		end,
		addTouchBeganCallback = function (id, callback)
			TouchManager.callbacks.touchBeganCallbacks[id] = callback
		end,
		removeTouchBeganCallback = function (id)
			TouchManager.callbacks.touchBeganCallbacks[id] = nil
		end,
		addTouchMovedCallback = function (id, callback)
			TouchManager.callbacks.touchMovedCallbacks[id] = callback
		end,
		removeTouchMovedCallback = function (id)
			TouchManager.callbacks.touchMovedCallbacks[id] = nil
		end,
		addTouchEndedCallback = function (id, callback)
			TouchManager.callbacks.touchEndedCallbacks[id] = callback
		end,
		removeTouchEndedCallback = function (id)
			TouchManager.callbacks.touchEndedCallbacks[id] = nil
		end,
		addMultiTouchBeganCallback = function (id, callback)
			TouchManager.callbacks.multiTouchBeganCallbacks[id] = callback
		end,
		removeMultiTouchBeganCallback = function (id)
			TouchManager.callbacks.multiTouchBeganCallbacks[id] = nil
		end,
		addMultiTouchMovedCallback = function (id, callback)
			TouchManager.callbacks.multiTouchMovedCallbacks[id] = callback
		end,
		removeMultiTouchMovedCallback = function (id)
			TouchManager.callbacks.multiTouchMovedCallbacks[id] = nil
		end,
		addMultiTouchEndedCallback = function (id, callback)
			TouchManager.callbacks.multiTouchEndedCallbacks[id] = callback
		end,
		removeMultiTouchEndedCallback = function (id)
			TouchManager.callbacks.multiTouchEndedCallbacks[id] = nil
		end,
		addMultiTouchCanceledCallback = function (id, callback)
			TouchManager.callbacks.multiTouchCanceledCallbacks[id] = callback
		end,
		removeMultiTouchCanceledCallback = function (id)
			TouchManager.callbacks.multiTouchCanceledCallbacks[id] = nil
		end,
	}
end

-----------------------------------------------
----- Backlog
-----------------------------------------------
local Backlog=class()
function Backlog:init()
	self.configs = {
		fontName = "NanumBarunGothic",
		lineMargin = 10,
		fontSize = 20,
		fontColor = {255,255,255},
		logLimit = 10,
		namePos = 150
	}
	self.logdatas = {}
	self.pending = {}

	self.labelContainer = {}

	self.isShowing = false
	self.yPos = 0
	self.limitYPos = 0

	self.currentName = ""
	self.nextName = ""

	return true
end

function Backlog:config()
	return self.configs
end

function Backlog:setConfig(newConfigs)
	self.configs = newConfigs

	while #self.logdatas > self.configs.logLimit do
		if #self.logdatas == 0 then
			break
		end

		table.remove(self.logdatas, 1)
	end
end

function Backlog:setName(name)
	self.currentName = self.nextName
	self.nextName = name
end

function Backlog:addPendingString(str)
	table.insert(self.pending, str)
end

function Backlog:commitString()
	local temp = ""
	for z,x in ipairs(self.pending) do
		temp = temp..x
	end

	if temp ~= "" then
		table.insert(self.logdatas, {self.currentName, temp})
		self.pending = {}

		if #self.logdatas > self.configs.logLimit then
			table.remove(self.logdatas, 1)
		end
	end
end

function Backlog:show(xPos, yPos, contentWidth)
	local font = self.configs.fontName or "NanumBarunGothic"

	self.yPos = 0
	local y = yPos
	local prevHeight = 0
	
	for k,v in ripairs(self.logdatas) do
		local label = pini.Label(pini:GetUUID(),v[2],font,self.configs.fontSize,{contentWidth,0})
		table.insert(self.labelContainer, label)
		pini:AttachDisplay(label)
		label:setColor(self.configs.fontColor[1] or 255,self.configs.fontColor[2] or 255,self.configs.fontColor[3] or 255)
		label:setZ(10000000)

		local currentHeight = label:contentSize().height
		y = y - currentHeight - (self.configs.lineMargin or 10)
		prevHeight = currentHeight
		label:setPosition(xPos,y)
		label:setAnchorPoint(0,1)

		if v[1] and v[1] ~= "" then
			local nameLabel = pini.Label(pini:GetUUID(),"\n"..v[1],font,self.configs.fontSize)
			table.insert(self.labelContainer, nameLabel)
			pini:AttachDisplay(nameLabel)
			nameLabel:setColor(self.configs.fontColor[1] or 255,self.configs.fontColor[2] or 255,self.configs.fontColor[3] or 255)
			nameLabel:setZ(10000000)
			nameLabel:setPosition(xPos - (self.configs.namePos or 150),y)
			nameLabel:setAnchorPoint(0,1)
		end
	end

	self.limitYPos = y - 200
	self.motherNode = motherNode

	self.isShowing = true
end

function Backlog:hide()
	if self.isShowing then
		for k,v in ipairs(self.labelContainer) do
			pini:DetachDisplay(v,true)
		end

		self.isShowing = false
		self.labelContainer = {}
	end
end

function Backlog:runScrollEvent(scrollY)

	if self.isShowing then
		self.yPos = self.yPos + scrollY

		if self.yPos > 0 then
			self.yPos = 0
			return false
		end

		if self.yPos < self.limitYPos then
			self.yPos = self.yPos - scrollY
			return true
		end

		for k,v in ipairs(self.labelContainer) do
			local posx, posy = v:position()
			v:setPosition(posx, posy - scrollY)
		end

		return true
	end

	return false
end

function Backlog:clear()
	self.logdatas = {}
	self.pending = {}
end

-----------------------------------------------
----- Dialog
-----------------------------------------------
local Dialog=class()
function Dialog:init()
	self.name = nil
	self.connects = {}
	self.background = nil
	self.nameWindow = nil
	self.cursor = nil
	self.configs = {}
	self.words = {}
	self.allwords = {}
	self.showingWords = {}
	self.showingDelFlag = false
	self.default = {}
	self.configIdx = "대화"
	self.needUpdate = true
	self.lastX = 0
	self.lastY = 0
	self.wait = false
	self.lastMaxY = 0
	self.enableInputWait = true
	self.timerWait = 0
	self.running = false
	self.isConnectBlockBuilted = false
	
	self.animWords = {}
	self.nextBuildWords = {}

	return true
end
function Dialog:config(idx)
	return self.configs[idx] 
end
function Dialog:SetConfig(idx,data)
	self.configs[idx] = data
end
function Dialog:UseConfig(idx)
	if idx == nil then
		self.name = nil 
	end
	if self.configIdx ~= idx then
		self.needUpdate = true
		self.default = {}
		self:Reset()
	end
	self.configIdx = idx
end
function Dialog:ClearShowingCache()
	self.showingWords = {}
	self.showingDelFlag = false
end
function Dialog:Clear()
	if self.background then
		pini:DetachDisplay(self.background,true)
		self.background = nil
	end
	if self.nameWindow then
		pini:DetachDisplay(self.nameWindow,true)
	end
	self.nameWindow = nil
	self.cursor = nil
	self.isConnectBlockBuilted = false
	self.connects = {}
	self.words = {}
	self.allwords = {}
end
function Dialog:Reset()
	self.resetFlag = false
	self.lastX = 0
	self.lastY = 0
	self.lastMaxY = 0
	self.needUpdate = true
	self.wait = false;

	self.animWords = {}
	self.nextBuildWords = {}

	self:stop()
	self:Clear()
end
function Dialog:Preview()
	if OnPreview then
		for k,v in ipairs(self.words) do
			if v[1] == 1 then
				if self.resetFlag then
					self:Reset()
				end
				self:insertPendingString(v[2])
			else
				self:ApplyMarkup(v[2])
			end
		end
	end
end
function Dialog:Add(arg)
	if OnPreview then
		table.insert(self.words,{1,arg})
	else
		if self.showingDelFlag then
			pini.Backlog:commitString()
			self.showingWords = {}
			self.showingDelFlag = false
		end
		table.insert(self.showingWords,{1,arg})

		self:insertPendingString(arg)
		self:run()
	end
end
function Dialog:AddMarkup(arg)
	if OnPreview then
		if arg["name"] == "=" then
			args = self:EqualMarkup(tostring(arg["args"][1]) or "")
			self:Add(args)
		else
			table.insert(self.words,{2,arg})
		end
		
	else
		if arg["name"] == "=" then
		else
			table.insert(self.showingWords,{2,arg})
			self:run()
		end

		self:ApplyMarkup(arg)
	end
end
function Dialog:EqualMarkup(arg)
	local strs = {}
	local args = {}
	local var = _LNXG[arg]
	var = tostring(var) or ""
	var:gsub(".",function(c)
		table.insert(strs,c)
	end)
	local p = ""
	for k,v in ipairs(strs) do
		local char = nil
		if string.byte(v) < 127 then
			char = v
		else
			p = p .. v
			if p:len() == 3 then
				char = p
				p=""
			end
		end
		if char then
			table.insert(args,char)
		end
	end	

	return args
end
function Dialog:ApplyMarkup(arg)
	local name = arg["name"]
	if name == "클린" then
		if OnPreview then
			self.resetFlag = true
		else
			self:Reset()
			self.showingDelFlag = true
		end

	elseif name == "클릭" then
		if OnPreview then
		else
			self.wait = true
			self.callstack = pini.XVM:stop()
			return 
		end

	elseif name == "대사창나타남" then
		if OnPreview then
		else
			self:_make(function(isUpdated)
				local config = self.configs[self.configIdx]
				local appearAnimation = config["appearAnim"]
				local effect = config["effect"]
				local animationTime = config["effectSec"]
				local isRunOk = false

				if appearAnimation:len() > 0 and AnimMgr:isAnim(appearAnimation) then
					animationTime = AnimMgr:maxFrame(appearAnimation,0) * 0.017
					AnimMgr:run(appearAnimation,0,0,nil,0.017,1,self.background,"")
					AnimMgr:run(appearAnimation,0,0,nil,0.017,1,self.nameWindow,"")
					isRunOk = true
				elseif effect:len() > 0 then
					if fs_imageEffect[effect] then
						fs_imageEffect[effect](self.background,animationTime)
						fs_imageEffect[effect](self.nameWindow,animationTime)
						isRunOk = true
					end
				end
			end)
			return 
		end

	elseif name == "대사창사라짐" then
		if OnPreview then
		else
			if self.background then
				local config = self.configs[self.configIdx]
				local disappearAnimation = config["disappearAnim"]
				local effect = config["effect"]
				local animationTime = config["effectSec"]

				self.showingDelFlag = true

				if disappearAnimation:len() > 0 and AnimMgr:isAnim(disappearAnimation) then
					self.frameStopCallstack = pini.XVM:stop()
					self.background:removeAllChildren()

					animationTime = AnimMgr:maxFrame(disappearAnimation,0) * 0.017
					AnimMgr:run(disappearAnimation,0,0,nil,0.017,1,self.background,"")
					AnimMgr:run(disappearAnimation,0,0,nil,0.017,1,self.nameWindow,"")

					self.cursorUpdateDisable = true
					pini.Timer(nil,animationTime,function(t)
						pini.Dialog.cursorUpdateDisable = nil
						pini.Dialog:Reset()
						pini.XVM:resume(pini.Dialog.frameStopCallstack)
					end,false,nil,{}):run()
				elseif effect:len() > 0 and fs_imageDeleteEffect[effect] then 
					self.frameStopCallstack = pini.XVM:stop()
					self.background:removeAllChildren()

					fs_imageDeleteEffect[effect](self.background,animationTime)

					self.cursorUpdateDisable = true
					pini.Timer(nil,animationTime,function(t)
						pini.Dialog.cursorUpdateDisable = nil
						pini.Dialog:Reset()
						pini.XVM:resume(pini.Dialog.frameStopCallstack)
					end,false,nil,{}):run()
				else
					self.frameStopCallstack = pini.XVM:stop()
					self.background:removeAllChildren()

					animationTime = 0.01
					self.cursorUpdateDisable = true
					pini.Timer(nil,animationTime,function(t)
						pini.Dialog.cursorUpdateDisable = nil
						pini.Dialog:Reset()
						pini.XVM:resume(pini.Dialog.frameStopCallstack)
					end,false,nil,{}):run()
				end
			end
		end
	elseif name == "닫기" then
		if OnPreview then
			if self.background then
				self.background:setVisible(false)
			end
			if self.nameWindow then
				self.nameWindow:setVisible(false)
			end
		else
			table.insert(self.nextBuildWords,{2,(tonumber(arg["args"][1]) or 0)})
		end

	elseif name == "켜기" then
		if OnPreview then
			if self.background then
				self.background:setVisible(true)
			end
			if self.nameWindow then
				self.nameWindow:setVisible(true)
			end
		else
			table.insert(self.nextBuildWords,{3,(tonumber(arg["args"][1]) or 0)})
		end

	elseif name == "색상" then
		table.insert(self.nextBuildWords,{4,function ()
			self.default.R = tonumber(arg["args"][1]) or 255
			self.default.G = tonumber(arg["args"][2]) or 255
			self.default.B = tonumber(arg["args"][3]) or 255
		end})

	elseif name == "크기" then
		table.insert(self.nextBuildWords,{4,function ()
			self.default.size = tonumber(arg["args"][1]) or 40
		end})

	elseif name == "대기" then
		if OnPreview then
		else
			pini.XVM:sleep(tonumber(arg["args"][1] or 0))
		end
		
		local timer = pini:FindTimer("PINI_Dialog_Update")
		if timer then
			table.insert(self.nextBuildWords,{0,(tonumber(arg["args"][1]) or 0)})
			return 
		end

	elseif name == "시간" then
		local timer = pini:FindTimer("PINI_Dialog_Update")
		if timer then
			table.insert(self.nextBuildWords,{1,tonumber(arg["args"][1]) or 0.05})
			return 
		end

	elseif name == "공백" then
		table.insert(self.nextBuildWords,{4,function ()
			self.lastX = self.lastX+tonumber(arg["args"][1]) or 0
		end})

	elseif name == "자간" then
		table.insert(self.nextBuildWords,{4,function ()
			self.default.wordGap = tonumber(arg["args"][1]) or 0
		end})

	elseif name == "행간" then
		table.insert(self.nextBuildWords,{4,function ()
			self.default.lineGap = (tonumber(arg["args"][1]) or 0)+5
		end})

	elseif name == "폰트" then
		table.insert(self.nextBuildWords,{4,function ()
			self.default.font = tostring(arg["args"][1]) or "NanumBarunGothic"
		end})

	elseif name == "연결" then
		table.insert(self.nextBuildWords,{4,function ()
			self.isConnectBlockBuilted = false
			self.default.connect = tostring(arg["args"][1])
		end})

	elseif name == "=" then
		args = self:EqualMarkup(tostring(arg["args"][1]) or "")
		self:Add(args)

	elseif name == "비활성" then
		for k,v in ipairs(self.allwords) do 
			if v.isDisabled == nil then
				local action = pini.Anim.Spawn(
							pini.Anim.MoveBy(0.5,0,-2),
							pini.Anim.FadeTo(0.5,100)
						)
				action:run(v)
				v.isDisabled = true
			end
		end

	--닫기!
	elseif name == "/" then
		for k,v in ipairs(arg["args"]) do
			if v == "색상" then
				table.insert(self.nextBuildWords,{4,function ()
					self.default.R = nil
					self.default.G = nil
					self.default.B = nil
				end})
			elseif v == "크기" then
				table.insert(self.nextBuildWords,{4,function ()
					self.default.size = nil
				end})
			elseif v == "폰트" then
				table.insert(self.nextBuildWords,{4,function ()
					self.default.font = nil
				end})
			elseif v == "연결" then
				table.insert(self.nextBuildWords,{4,function ()
					self.default.connect = nil
				end})
			end
		end
	end
end

function Dialog:createNameWindow()
	local config = self.configs[self.configIdx]
	--create name window
	if self.name then
		local nameWindow = config["name"] or {}
		x,y = nameWindow["x"] or 0 ,nameWindow["y"] or 0 
		if nameWindow["path"] then
			self.nameWindow = pini.Sprite("PINI_dialog_name",nameWindow["path"])
			self.nameWindow:setAnchorPoint(0,0);
		else
			self.nameWindow = pini.ColorLayer("PINI_dialog_name",60,60,60,122,nameWindow["width"] or 300,nameWindow["height"] or 50)
		end
		local backColor = nameWindow["background_color"] or {255,255,255,255}
		self.nameWindow:setColor(backColor[1] or 255,backColor[2] or 255,backColor[3] or 255)
		self.nameWindow:setOpacity(backColor[4] or 255)
		self.nameWindow:setPosition(x,y)
		self.nameWindow:setZ(50000);
		pini:AttachDisplay(self.nameWindow)
	end
end

function Dialog:createCursor()
	local config = self.configs[self.configIdx]
	--create cursor
	local cursorConf = config["cursor"] or {}
	if cursorConf["sprite"] and cursorConf["sprite"]:len() > 0 then
		self.cursor = pini.Sprite("PINI_dialog_cursor",cursorConf["sprite"])
	else
		self.cursor = pini.ColorLayer("PINI_dialog_cursor",0,0,0,0,cursorConf["width"] or 20,cursorConf["height"] or 10)
	end

	local color = cursorConf["color"] or {255,255,255,255}
	self.cursor:setColor(color[1] or 255,color[2] or 255,color[3] or 255)
	self.cursor:setOpacity(color[4] or 255)
	self:SetCursorVisible(false)
	self.cursor:setZ(50000)
	pini:AttachDisplay(self.cursor,self.background.id)
end

function Dialog:updateName()
	local config = self.configs[self.configIdx]

	if self.nameDirty then
		pini.Backlog:setName(self.name)

		if self.nameWindow then
			self.nameWindow:removeAllChildren()
		end
		if self.name then
			local nameConf = config["name"] or {}
			local font = nameConf["font"] or config["font"] or "NanumBarunGothic"

			local ax,ay = self.nameWindow:anchor()
			local originX = -self.nameWindow:contentSize().width * ax
			local originY = -self.nameWindow:contentSize().height* (1-ay)
			
			local label = pini.Label(pini:GetUUID(),self.name,font,nameConf["text_size"] or 30)
			pini:AttachDisplay(label,self.nameWindow.id)
			label:setColor(nameConf["text_color"][1] or 255,nameConf["text_color"][2] or 255,nameConf["text_color"][3] or 255)
			label:setPosition(StrEnumToPos(label,nameConf["text_align"] or "화면중앙"))
			local x,y = label:position()
			label:setPosition(x+originX,y+originY)

			local outline = nameConf["text_outline"]
			local shadow = nameConf["text_shadow"]
			local glow = nameConf["text_outglow"]
			if outline then
				local o = outline
				label:setStroke(o[1] or 0,o[2] or 0,o[3] or 0,o[4] or 0,o[5] or 0)
			end
			if shadow then
				local s = shadow
				label:setShadow(s[1] or 0,s[2] or 0,s[3] or 0,s[4] or 0,s[5] or 0,-(s[6] or 0),s[7] or 0)
			end
			if glow then
				local g = glow
				label:setGlow(g[1] or 0,g[2] or 0,g[3] or 0,g[4] or 0)
			end
		end
	end	
end
function Dialog:_make(callback)
	local config = self.configs[self.configIdx]
	if self.background == nil then
		self.needUpdate = true
	end

	if self.needUpdate then
		self:Clear()
		local x,y

		-- create dialog window
		x,y = config["x"] or 0 ,config["y"] or 0 
		if config["path"] then
			self.background = pini.Sprite("PINI_dialog_background",config["path"])
			self.background:setAnchorPoint(0,0);
		else
			self.background = pini.ColorLayer("PINI_dialog_background",0,0,0,0,config["width"] or 300,config["height"] or 300)
		end

		local backColor = config["background_color"] or {255,255,255,255}
		self.background:setColor(backColor[1] or 255,backColor[2] or 255,backColor[3] or 255)
		self.background:setOpacity(backColor[4] or 255)
		self.background:setPosition(x,y)
		self.background:setZ(9000);
		pini:AttachDisplay(self.background)
		self:createNameWindow()
		self:createCursor()
	end

	self:updateName()
	if callback then
		callback(self.needUpdate)
	end
	self.needUpdate = false
end

function Dialog:createConnectBlock(bmrk)
	local config = self.configs[self.configIdx]
	config = config["linkBlock"] or {}

	local c = config["color"] or {255,255,255,60}
	local ls = config["linkSound"]
	local back=nil
	if tostring(config["unselect"] or ""):len() > 0 then
		back = pini.Sprite(pini:GetUUID(),config["unselect"])
	else
		back = pini.ColorLayer(pini:GetUUID(),c[1] or 255,c[2] or 255,c[3] or 255,c[4] or 100,0,0)
	end
	back:setOpacity(c[4] or 60)
	back:setPositionX(self.lastX)
	back.bmrk = bmrk
	back.selectSprite = config["select"]
	back.unselectSprite = config["unselect"]

	pini:AttachDisplay(back,self.background.id)

	back.check = 0
	back.touchPriority = 50001
	back.onTouchUp = function(loc,v)
		if ls then
			pini:PlaySound("PINI_Dialog_LinkSound",ls,false,1)
		end

		if v.check == 1 then
			pini.Dialog:Reset()
			pini.Dialog.showingDelFlag = true
			pini.XVM:resumeAndGoBookmark(pini.Dialog.callstack,v.bmrk)
		end
		v.check = 1
		if v.selectSprite then
			v:setSprite(v.selectSprite)
		end
	end
	back.onTouchMiss = function(location,v)
		v.check = 0
		if v.unselectSprite then
			v:setSprite(v.unselectSprite)
		end
	end

	pini.TouchManager:registNode(back)

	local linkOp = c[4] or 60
	back.onTouchAnim  = pini.Anim.Forever(
							pini.Anim.Sequence(
								pini.Anim.FadeTo(0.5,linkOp*0.1),
								pini.Anim.FadeTo(0.5,linkOp)
							)
						)


	table.insert(self.connects,back)
	return back
end

function Dialog:connectBlockModify(block,y,w,maxY)
	local config = self.configs[self.configIdx]
	local bconfig = config["linkBlock"] or {}
	local marginX = config["marginX"] or 0
	local my = y

	if block.type=="Sprite" then
		local size = block:contentSize()
		local sx = w/size.width
		if bconfig["fitWidth"] then
			sx = (config["width"] or 0)/size.width
			block:setPositionX(marginX)
		end
		block:setPositionY(my)
		block:setScale(sx,maxY/size.height)
		block:setAnchorPoint(0,0)
	else
		local sx = w
		if bconfig["fitWidth"] then
			sx = (config["width"] or 0)
			block:setPositionX(marginX)
		end
		block:setPositionY(my)
		block:setContentSize(sx,maxY)
	end
end

function Dialog:stop()
	if self.running then
		pini:StopTimer("PINI_Dialog_Update")
		pini:DetachDisplay(pini:FindNode("PINI_Dialog_touch")) 
		pini:scene():unregistKeyboard("PINI_Dialog_keyInput")
	end
	self.running = false
end

function Dialog:insertPendingString(words)
	self:_make()

	for k,v in ipairs(words) do
		table.insert(self.nextBuildWords, v)
	end
end

function Dialog:CreateOneWord()
	local t = pini:FindTimer("PINI_Dialog_Update")

	if #self.nextBuildWords > 0 then
		local config = self.configs[self.configIdx]
		local font = config["font"] or "NanumBarunGothic"
		local default_color = config["text_color"] or {255,255,255}
		local default_size = config["size"] or 40
		
		local ax,ay = self.background:anchor();

		local additionalX = 0--self.background:contentSize().width * ax
		local additionalY = self.background:contentSize().height*(1-ay)

		local lastedX = self.lastX + additionalX-(config["marginX"] or 0)
		local lastedY = self.lastY + additionalY
		if (self.lastX ==0 and self.lastY == 0) then
			lastedX = 0
			lastedY = (config["marginY"] or 0) - (config["lineGap"] or 0)
		end

		local originX = (config["marginX"] or 0)-additionalX--lastedX-additionalX
		local originY = lastedY-additionalY
		local x = originX+lastedX
		local y = originY

		local maxY = self.lastMaxY or default_size
		
		local outline = config["text_outline"];
		local shadow = config["text_shadow"];
		local glow = config["text_outglow"];

		--GET COLOR
		local R = default_color[1]
		local G = default_color[2]
		local B = default_color[3]
		if self.default.R ~= nil then R=self.default.R end
		if self.default.G ~= nil then G=self.default.G end
		if self.default.B ~= nil then B=self.default.B end

		--GET SIZE
		local size = self.default.size or default_size

		--GET FONT
		font = self.default.font or font

		local link = self.default.connect
		local lineGap = self.default.lineGap or 5
		local wordGap = self.default.wordGap or 0
		local marginX = config["marginX"] or 0
		local globalLineGap = config["lineGap"] or 0

		local textAnim  = config["text_anim"]
		if textAnim and textAnim:len() <= 0 then
			textAnim = nil
		end

		local ch = self.nextBuildWords[1]
		table.remove(self.nextBuildWords,1)

		if type(ch) ~= "table" then
			pini.Backlog:addPendingString(ch)

			if link then
				if self.lastCreatedblcks == nil then
					if not self.isConnectBlockBuilted then
						self.lastCreatedblcks = self:createConnectBlock(link)
						self.isConnectBlockBuilted = true
					end
				end
			else
				self.lastCreatedblcks = nil
			end

			if ch == "\n" then
				x = originX
				y = y+maxY+lineGap+globalLineGap
				maxY  = default_size
				self.lastCreatedblckWidth = 0

				if self:isAllLettersShow() then
					self:SetCursorVisible(true)
				end
			elseif ch == "" then
				-- skip and try one more

				if self:isAllLettersShow() then
					self:SetCursorVisible(true)
				else
					self:CreateOneWord()
				end

				return
			else
				if y == (config["marginY"] or 0) - (config["lineGap"] or 0) - additionalY then
					y = (config["marginY"] or 0) - additionalY + lineGap
				end

				local label = pini.Label(pini:GetUUID(),ch,font,size)
				--label:registManagedNode()

				table.insert(self.allwords,label)
				pini:AttachDisplay(label,self.background.id)

				local cs = label:contentSize()
				label:setPosition(x+cs.width*0.5,y+cs.height*0.5)
				label:setColor(R,G,B)
				x = x + cs.width + wordGap
			
				if x + marginX - originX > config["width"] then
					x = originX
					y = y+maxY+globalLineGap

					label:setPosition(x+cs.width*0.5,y+cs.height*0.5)
					x = x + cs.width + wordGap

					maxY = 0
					self.lastCreatedblckWidth = 0
				end	

				if outline then
					local o = outline
					label:setStroke(o[1] or 0,o[2] or 0,o[3] or 0,o[4] or 0,o[5] or 0)
				end
				if shadow then
					local s = shadow
					label:setShadow(s[1] or 0,s[2] or 0,s[3] or 0,s[4] or 0,s[5] or 0,-(s[6] or 0),s[7] or 0)
				end
				if glow then
					local g = glow
					label:setGlow(g[1] or 0,g[2] or 0,g[3] or 0,g[4] or 0)
				end
				if textAnim and (not self.continuousBuild) then
					AnimMgr:run(textAnim,0,0,nil,0.01,1,label,"",function()
						if #self.animWords > 0 then
							table.remove(self.animWords,1)
						end
					end)
					table.insert(self.animWords, label)
				end

				if maxY < cs.height then
					maxY = cs.height
				end
				self.lastMaxY = maxY
				self.lastCreatedblckWidth = self.lastCreatedblckWidth or 0
				self.lastCreatedblckWidth = self.lastCreatedblckWidth + cs.width + wordGap
			end
			if link and self.lastCreatedblcks then
				self:connectBlockModify(self.lastCreatedblcks,y+maxY,self.lastCreatedblckWidth,maxY)
			end
			self.lastX = x
			self.lastY = y
			self:SetCursorVisible(false)
		end

		local textSound = config["sound"] or ""

		if type(ch) == "table" then
			if ch[1] == 0 then
				t.userdata.deltaTime = t.userdata.deltaTime - ch[2]
				t.userdata.doNext = true;

			elseif ch[1] == 1 then
				t.userdata.textRate = ch[2]
				t.userdata.doNext = true;

			elseif ch[1] == 2 then
				if self.background then
					self.background:setVisible(false)
				end
				if self.nameWindow then
					self.nameWindow:setVisible(false)
				end
			elseif ch[1] == 3 then
				if self.background then
					self.background:setVisible(true)
				end
				if self.nameWindow then
					self.nameWindow:setVisible(true)
				end
			elseif ch[1] == 4 then
				ch[2]()
			end

			if self:isAllLettersShow() then
				self:SetCursorVisible(true)
			end
		else 
			if textSound then
				pini:PlaySound("PINI_Dialog_TextSound",textSound,false,1)
			end
		end
	end
end

function Dialog:run()
	if self.running == false then
		--data
		local config = self.configs[self.configIdx]
		local textRate = config["text_rate"] or 0.01

		--functions
		local touches = pini.Node("PINI_Dialog_touch")
		touches:setContentSize(99999,99999)
		touches.onTouchUp = function(location,v)
			local v = pini.Dialog
			if v.wait then
				if v:isAllLettersShow() then
					v.wait = false
					if #v.connects == 0 then
						local t = v.callstack
						v.callstack = nil
						pini.XVM:resume(t)
					end
				else
					v:showAllLetters()
					v:SetCursorVisible(true)
				end
			end
		end
		touches.touchPriority = 50000

		if self.enableInputWait then
			pini:AttachDisplay(touches)

			local KeyName = config["keyName"] or 59
			pini:scene():registKeyboard("PINI_Dialog_keyInput",
				function (press,k)
					if press == false then
						if k == KeyName then 
							touches.onTouchUp()
						end
					end
				end)
		end

		pini.TouchManager:registNode(touches)

		pini.Timer("PINI_Dialog_Update",0,function(t)
			t.userdata.deltaTime = t.userdata.deltaTime + t.dt
			while true do
				if t.userdata.deltaTime < t.userdata.textRate then
					break
				end

				t.userdata.deltaTime = t.userdata.deltaTime - t.userdata.textRate
				pini.Dialog:CreateOneWord()

				if #self.nextBuildWords <= 0 then
					t.userdata.deltaTime = 0
					break
				end
			end
			if pini.Dialog:isAllLettersShow() then
				if t.userdata.waitsec > 0 then
					t.userdata.endtime = t.userdata.endtime + t.dt
					if t.userdata.endtime > t.userdata.waitsec then
						if #pini.Dialog.connects == 0 then
							pini.Dialog:stop()
							pini.XVM:resume(pini.Dialog.callstack)
						end
					end
				end
				pini.Dialog:SetCursorVisible(true)
			end
		end,true,nil,{
			deltaTime = 0,
			endtime = 0,
			waitsec = self.timerWait,
			textRate = textRate,
		}):run()
	end
	self.running = true;
end

function Dialog:WaitConfig(key,sec)
	self.enableInputWait = key
	self.timerWait = sec
end
function Dialog:SetCursorVisible(v)
	if self.cursorUpdateDisable then
		return
	end
	if self.cursor then
		local config = self.configs[self.configIdx]
		if v and self.cursor:isVisible() == false then
			local cursorConf = config["cursor"] or {}
			if cursorConf["anim"] then
				if not OnPreview and AnimMgr:isAnim(cursorConf["anim"]) then
					AnimMgr:run(cursorConf["anim"],0,0,nil,0.01,nil,self.cursor,"")
				else
					local action = pini.Anim.Forever(pini.Anim.Sequence(pini.Anim.FadeTo(0.5,100),pini.Anim.FadeTo(0.5,255)))
					action:run(self.cursor)
				end
			end
		end

		local txt = nil
		for i=0,#self.allwords,1 do
			txt = self.allwords[#self.allwords - i]
			if txt and txt[1] == nil then
				if #(txt:string()) > 0 then
					break
				end
			end
		end
		if txt then
			local s   = txt:contentSize()
			local x,y = txt:position()
			self:SetCursorPosition(x+s.width*0.5,y+s.height*0.5)
		end

		self.cursor:setVisible(v)
	end
end

function Dialog:SetCursorPosition(x,y)
	if self.cursor then
		if self.cursor.type == "Sprite" then
			local s = self.cursor:contentSize()
			self.cursor:setPosition(x + s.width*0.5,y - s.height*0.5)
		else
			self.cursor:setPosition(x,y)
		end
	end
end
function Dialog:isAllLettersShow()
	return #self.nextBuildWords == 0 and #self.animWords == 0
end

function Dialog:showAllLetters()
	if OnPreview then
		if self.background == nil or self.background.visible then
			while #self.nextBuildWords > 0 do
				self:CreateOneWord()
			end
		end
	else
		while #self.animWords > 0 do
			AnimMgr:forceFinalNodeAndStop(self.animWords[1])
		end

		if self.background == nil or self.background.visible then
			while #self.nextBuildWords > 0 do
				self:CreateOneWord()
			end
		end
	end
end
function Dialog:setName(name)
	if self.name ~= name then
		self.nameDirty = true
	end
	self.name = name
end

-----------------------------------------------
-----PINI MAINS
-----------------------------------------------

pini={
	_regist_={
		Sounds = {},
		BGM = nil,
		Display = {},
		SystemNode = {},
		Timers = {},
		Shaders= {},
		LatestScene=nil
	}
}

pini["Node"] = Node
pini["ClippingNode"] = ClippingNode
pini["Sprite"] = Sprite
pini["Scene"] = Scene
pini["GlobalTimer"] = GlobalTimer()
pini["Timer"] = Timer
pini["Label"] = Label
pini["Slider"] = Slider
pini["ColorLayer"] = ColorLayer
pini["TouchManager"] = TouchManager
pini["Dialog"] = Dialog()
pini["DialogType"] = Dialog
pini["Anim"] = anim
pini["Shader"] = Shader
pini["VideoPlayer"] = VideoPlayer
pini["TextInput"] = TextInput
pini["RenderTexture"] = RenderTexture
pini["Backlog"] = Backlog()
pini["BacklogType"] = Backlog
pini.FindZip = {}
pini.ManagedNodePool = {
	["label"]={}
}
pini.password = ""

function pini:clearNodePool()
	for k,v in pairs(pini.ManagedNodePool) do
		for j,node in ipairs(v) do
			Utils.AUTORELEASE(node)
		end
		pini.ManagedNodePool[k]={}
	end
end

function pini:getSpriteFromZips(path)
	for k,v in ipairs(pini.FindZip) do
		local node = nil
		if FILES["image/"..path] then
			node = Utils.loadSpriteFromZip(v,FILES["image/"..path],pini.password)
		else
			node = Utils.loadSpriteFromZip(v,"image/"..path,pini.password)
		end
		if node then
			return node
		end
	end
	return nil
end

function pini:copyFileFromZips(path)
	for k,v in ipairs(pini.FindZip) do
		local relative = Utils.extractZipTempFile(v,path,pini.password)
		if relative then
			return relative
		end
	end
end

function pini:SetScene(scene)
	self._regist_.LatestScene = scene
	TouchManager:SetScene(scene)
end

function pini:GetUUID()
	local time = tostring(os.time())
	local uuid = "AUTO_"..time
	local count = 0;
	while true do
		if self._regist_.Display[uuid] == nil and 
		   self._regist_.Timers[uuid] == nil  and 
		   self._regist_.Sounds[uuid] == nil  and 
		   self._regist_.Shaders[uuid] == nil then
			return uuid
		end
		uuid = "AUTO_"..time..count
		count = count+1
	end
end

function pini:ClearShader()
	local shaders = self._regist_.Shaders
	for k,v in pairs(shaders) do 
		v:fin()
	end
	self._regist_.Shaders = {}
end

function pini:UnregistShader(shader)
	local shaders = self._regist_.Shaders
	local name = shader
	if type(shader) == "table" then
		name = shader.id
	end
	shaders[name] = nil
end

function pini:FindShader(shader)
	local shaders = self._regist_.Shaders
	local name = shader
	if type(shader) == "table" then
		name = shader.id
	end
	return shaders[name]
end

function pini:RegistShader(shader)
	local shaders = self._regist_.Shaders
	if shaders[shader.id] then
		shaders[shader.id]:fin()
	end
	shaders[shader.id] = shader
end

function pini:AttachDisplay(node,parent)
	if node == nil then
		return
	end
	local displays = self._regist_.Display
	
	if node.id:len() > 0 then
		if displays[node.id] then
			local node = displays[node.id]
			self:DetachDisplay(node)
		end
		displays[node.id] = node
	end

	if parent and type(parent)=="string" and parent:len() > 0 and node.id ~= parent and displays[parent] then
		displays[parent]:addChild(node)
		return displays[parent]
	else
		self:scene():addChild(node)
	end
	return false
end
function pini:DetachDisplay(node,cleanup,checker)
	if node == nil then
		return 
	end

	if OnPreview then
	else
		if node.detached then
			return 
		end
		node.detached = true
	end

	local displays = self._regist_.Display;
	if cleanup ~= false then
		local children = {}
		for k,v in ipairs(node:children()) do
			table.insert(children,v)
		end
		for k,v in ipairs(children) do 
			pini:DetachDisplay(v,cleanup)
		end
		displays[node.id] = nil
	end
	if checker == nil then
		node:removeSelf(cleanup)
	end
end
function pini:Clear()
	self:ClearSound()
	self:ClearTimer()
	self:ClearDisplay()
	self:ClearScene()
	self:ClearShader()
end
function pini:ClearScene()
	if self._regist_.LatestScene then
		self._regist_.LatestScene:clear()
		--self._regist_.LatestScene:removeSelf()
		self._regist_.LatestScene = nil
	end
end
function pini:ClearSound()
	for k in pairs(self._regist_.Sounds) do
		self:StopSound(k)
	end
end
function pini:ClearTimer()
	for k in pairs(self._regist_.Timers) do
		self:StopTimer(k)
	end
end
function pini:ClearDisplay()
	OnPreviewDrawOrder = 0
	self.Backlog:hide()
	self.Dialog:Reset()
	self.Dialog:ClearShowingCache()
	for k in pairs (self._regist_.Display) do
		self._regist_.Display[k] = nil
	end
end
function pini:ClearNonPreserveDisplay()
	OnPreviewDrawOrder = 0
	self.Backlog:hide()
	self.Dialog:Reset()
	for k in pairs (self._regist_.Display) do
		local d = self._regist_.Display[k]

		if not d.isPreserve then
			self:DetachDisplay(d)
		end
	end
end
function pini:RegistTimer(timer)
	local timers = self._regist_.Timers
	if timers[timer.id] then
		timers[timer.id]:stop()
	end
	timers[timer.id] = timer
end
function pini:UnregistTimer(timer)
	local timers = self._regist_.Timers
	if timers[timer.id] then
		timers[timer.id] = nil
	end
end
function pini:FindTimer(idx)
	local timers = self._regist_.Timers
	return timers[idx]
end
function pini:StopTimer(idx)
	local timers = self._regist_.Timers
	if timers[idx] then
		timers[idx]:stop()
	end
end
function pini:SoundVolume( vol , idx )
	local sid -- = self._regist_.BGM[4]
	if idx then
		if self._regist_.Sounds[idx] then
			sid = self._regist_.Sounds[idx][1]
		else
			sid = idx
		end
	else 
		if self._regist_.BGM then
			self._regist_.BGM[3] = vol
			sid = self._regist_.BGM[4]
		else
			return 
		end
	end
	if OnPreview then
	else
		if vol > 1 then
			vol = 1
		end
		if vol < 0 then
			vol = 0
		end
		ccexp.AudioEngine:setVolume(sid, tonumber(vol))
	end
end

function pini:PlaySound(idx,path,loop,vol)
	if path:len() > 0 then
		local sid
		if OnPreview then
		else
			local relative = FILES["sound/"..path]
			if not fileUtil:fileExist(relative) then
				relative = pini:copyFileFromZips(relative)
			end
			if relative == nil then
				return 
			end

			sid = ccexp.AudioEngine:play2d(relative, loop, vol)
			if sid == -1 then
				sid = ccexp.AudioEngine:play2d(ROOT_PATH..relative, loop, vol)
			end
		end
		if not idx or idx:len() <= 0  then
			idx = self:GetUUID()
		end
		self._regist_.Sounds[idx] = {sid,path,idx,loop,vol}

	end
end
function pini:StopSound(idx)
	local sid = self._regist_.Sounds[idx]
	if OnPreview then
	else
		if sid then
			ccexp.AudioEngine:stop(sid[1])
			self._regist_.Sounds[idx] = nil
		else
			ccexp.AudioEngine:stop(idx)
		end
	end
end
function pini:PlayBGM(path,brep,vol)
	if path:len() > 0 then
		if OnPreview then
		else
			self:StopBGM()

			local relative = FILES["sound/"..path]
			if not fileUtil:fileExist(relative) then
				relative = pini:copyFileFromZips(relative)
			end
			if relative == nil then
				return 
			end
			
			-- cc.SimpleAudioEngine:getInstance():playMusic(relative, true)
			sid = ccexp.AudioEngine:play2d(relative, brep, vol)
			self._regist_.BGM = {path,brep,vol,sid}
		end
	end
end
function pini:StopBGM()
	if OnPreview then
	else
		if self._regist_.BGM then
			ccexp.AudioEngine:stop(self._regist_.BGM[4])
		end
		self._regist_.BGM = nil
	end
end
function pini:scene()
	return self._regist_.LatestScene
end
function pini:FindNode(idx)
	return self._regist_.Display[idx]
end
function pini:FindTimer(idx)
	return self._regist_.Timers[idx]
end
function pini:takeScreenShot(callback,savefile)
	if OnPreview then
		callback(nil)
	else
		local visibleList = {}
		for k,v in pairs(self._regist_.Display) do
			if not v.includeScreenShot and v:isVisible() then
				table.insert(visibleList,v)
				v:setVisible(false)
			end
		end

		local target = cc.RenderTexture:create(
								WIN_WIDTH, 
								WIN_HEIGHT, 
								cc.TEXTURE2_D_PIXEL_FORMAT_RGB_A8888)
		target:clear(0,0,0,255)
		target:begin()
		self:scene():visit()
		target:endToLua()

		Utils.forceRender()

		local sprite = pini.Sprite("ScreenShot",target:getSprite():getTexture())
		sprite:setPosition(WIN_WIDTH*0.5, WIN_HEIGHT*0.5)
		sprite:setFlippedY(true);
		sprite:retain()

		if savefile then
			target:saveToFile(savefile,1)
		end

		Utils.forceRender()

		for k,v in pairs(visibleList) do
			v:setVisible(true)
		end
			
		cc.TextureCache:getInstance():removeTextureForKey(savefile)

		callback(sprite)
	end
end

try{
	function()
		pini.password = require("pp")():sub(1,11)
		-- pini.password = ""
		if fileUtil:fileExist("res.prz") then
			Utils.COPYPRZ()
			table.insert(pini.FindZip,"res.prz")
		end
	end,
	catch{function(error)end}
}
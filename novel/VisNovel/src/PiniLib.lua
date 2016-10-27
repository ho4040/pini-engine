require "utils"
require "trycatch"
require "PiniAPI"
require "cocos.cocos2d.json"
require "BuiltIn_Animation"

math.randomseed(os.time())

ENGINE_LOG = nil
XLSX_CLEAR = nil
REFRESH_BUILD_PATH = nil

local luaj = nil
local Utils = nil
local PiniLib = nil
local fileUtil = nil
local xlsxCache = {}
local ROOT_PATH = nil
local PackageName = nil
local CurrentPlatform = nil

local VM_BLOCK_FOR_ANDROID=nil

PROP_PUSH = function()end
PROP_POP  = function()end

if OnPreview then
	_G._LOG_ = {}
	ROOT_PATH = PiniLuaHelper:buildPath()
	ENGINE_LOG = function(text) table.insert(_G._LOG_,text) end
	XLSX_CLEAR = function() xlsxCache={} end
	REFRESH_BUILD_PATH = function() ROOT_PATH = PiniLuaHelper:buildPath() end
	CurrentPlatform = "Preview"
else
	OnPreview = false
	Utils = require("plua.utils")
	-- PROP_PUSH = Utils.PROP_PUSH
	-- PROP_POP  = Utils.PROP_POP
	fileUtil = cc.FileUtils:getInstance()
	ROOT_PATH = fileUtil:getWritablePath()
	CurrentPlatform = cc.Application:getInstance():getTargetPlatform()
	if (cc.PLATFORM_OS_ANDROID == CurrentPlatform) then
		luaj = require "cocos.cocos2d.luaj"
	end
end

local JavaClassName = "org/cocos2dx/lua/AppActivity"
function DeviceNativeCall(func,args,sig)
	local ok,ret  = luaj.callStaticMethod(JavaClassName,func,args,sig)
	if not ok then
		print("luaj error:", ret)
	else
		print("The ret is:", ret)
	end
	return ret
end

function AppPackageName()
	return DeviceNativeCall("AppPackageName",{},"()Ljava/lang/String;")
end

function OBBDirPath()
	return DeviceNativeCall("OBBDirPath",{},"()Ljava/lang/String;")
end

function PINI_IAP_CALLBACK(jsondata)
	print(jsondata)
	-- DeviceNativeCall("Android_Toast",{ jsondata , 10})
	
	local _data = jsondata:sub(2,#jsondata-1)
	local ds = _data:explode(",")
	local result = false

	for k,v in ipairs(ds) do
		ks = v:explode(":")
		if ks[1] == '"result"' then
			if ks[2]:startsWith("true") then
				result = true
			end
			break
		end
	end

	if result then
		pini.XVM:returnValueOnThread( 1, VM_BLOCK_FOR_ANDROID )
		_LNXG["결제정보.데이터"] = jsondata
	else
		pini.XVM:returnValueOnThread( 0, VM_BLOCK_FOR_ANDROID )
	end

	pini.Timer(pini:GetUUID(),1,function()
		local blockId = VM_BLOCK_FOR_ANDROID
		VM_BLOCK_FOR_ANDROID = nil
		pini.XVM:resume(blockId)
	end,false):run()
end

function PINI_IAP_CHECK_CALLBACK(jsondata)
	local j = json.decode(jsondata)
	pini.XVM:returnValueOnThread( j["result"], VM_BLOCK_FOR_ANDROID )

	pini.Timer(pini:GetUUID(),1,function()
		local blockId = VM_BLOCK_FOR_ANDROID
		VM_BLOCK_FOR_ANDROID = nil
		pini.XVM:resume(blockId)
	end,false):run()
end

function PINI_IAP_CONSUME_CALLBACK(jsondata)
	local j = json.decode(jsondata)

	_LNXG["jtext"] = j["jtext"]
	_LNXG["jsize"] = j["jsize"]

	pini.XVM:returnValueOnThread( j["result"], VM_BLOCK_FOR_ANDROID )

	pini.Timer(pini:GetUUID(),1,function()
		local blockId = VM_BLOCK_FOR_ANDROID
		VM_BLOCK_FOR_ANDROID = nil
		pini.XVM:resume(blockId)
	end,false):run()
end

function PINI_OBB_DOWNLOAD_RESULT(result)
	--DeviceNativeCall("Android_Toast",{ ">>>>>>>>"..tostring(result).."/"..tostring(VM_BLOCK_FOR_ANDROID) , 1})

	pini.XVM:returnValue(tonumber(result))
	pini.Timer(pini:GetUUID(),1,function()
		--DeviceNativeCall("Android_Toast",{ ">>>>>>>>GOGO", 1})
		local blockId = VM_BLOCK_FOR_ANDROID
		VM_BLOCK_FOR_ANDROID = nil
		pini.XVM:resume(blockId)
	end,false):run()
end

function LNX_VUNGLE_CALLBACK(length)
	if pini.XVM.vungleCallback then
		_LNXG["벙글광고표기.길이"] = length

		local funcName = pini.XVM.vungleCallback
		pini.XVM.vungleCallback = nil

		pini.Timer(pini:GetUUID(),0,function()
			pini.XVM:call(funcName)
		end,false):run()
	end
end

try{
	function() require(FILES["module/Animation"]) end,
	catch {function(error)end}
}
CLICK_WAIT_PRIORITY = 55000
GUI_PRIORITY = 60000

--##########################################################################
-- LanXVM 라이브러리 기능
--##########################################################################
function LNX_NODE(vm,stck)
	local id = vm:ARGU("노드","아이디","")
	local pos = vm:ARGU("노드","위치","화면중앙")
	local size = vm:ARGU("노드","크기","원본크기")
	local parent  = vm:ARGU("노드","부모","")
	local x = vm:ARGU("노드","x",nil)
	local y = vm:ARGU("노드","y",nil)
	local isPreserve = vm:ARGU("노드","항상표시","아니오")
	local angle = vm:ARGU("노드","회전",0)

	x = tonumber(x)
	y = tonumber(y)
	angle = tonumber(angle)

	local acp = _LNXG["설정.이미지중심"] or "0.5,0.5"
	acp = acp:explode(",")

	isPreserve = isPreserve=="예"

	local node = nil
	node = pini.Node(id)

	if node == nil then
		return 
	end

	pini:AttachDisplay(node,parent)

	node:setAnchorPoint(acp[1] or 0.5,1-(acp[2] or 0.5))
	node:setScale(StrEnumToScale(node,size))
	if x or y then
		node:setPosition(x or 0,y or 0)
	else
		node:setPosition(StrEnumToPos(node,pos))
	end

	node:setPreserve(isPreserve)
	node:setRotate(angle)
end

function LNX_IMAGE(vm,stck)
	local id = vm:ARGU("이미지","아이디","")
	local path = vm:ARGU("이미지","파일명","")
	local pos = vm:ARGU("이미지","위치","화면중앙")
	local effect = vm:ARGU("이미지","효과","")
	local effectSec = vm:ARGU("이미지","효과시간",0.25)
	local size = vm:ARGU("이미지","크기","원본크기")
	local connect = vm:ARGU("이미지","북마크이동","")
	local parent  = vm:ARGU("이미지","부모","")
	local overoll = vm:ARGU("이미지","오버롤","")
	local color = vm:ARGU("이미지","색상","255,255,255")
	local opacity = vm:ARGU("이미지","투명도","255")
	local screenshot = vm:ARGU("이미지","스크린샷노출","예")
	local GUI = vm:ARGU("이미지","GUI","아니오")
	local x = vm:ARGU("이미지","x",nil)
	local y = vm:ARGU("이미지","y",nil)
	local flip = vm:ARGU("이미지","반전","")
	local isPreserve = vm:ARGU("이미지","항상표시","아니오")
	local blendMode = vm:ARGU("이미지","색상모드","기본")
	local keep = vm:ARGU("이미지","유지","아니오") == "예"
	local angle = vm:ARGU("이미지","회전",0)
	local enableAnti = vm:ARGU("이미지","안티","예")

	x = tonumber(x)
	y = tonumber(y)
	angle = tonumber(angle)

	local acp = _LNXG["설정.이미지중심"] or "0.5,0.5"
	acp = acp:explode(",")

	GUI = GUI=="예"
	screenshot = screenshot=="예"
	isPreserve = isPreserve=="예"
	enableAnti = enableAnti=="예"

	local flipX = false
	local flipY = false
	if flip == "좌우" then
		flipX = true
	elseif flip == "상하" then
		flipY = true
	elseif flip == "상하좌우" then
		flipX = true
		flipY = true
	end

	if path:len() > 0 then
		local node = nil
		if keep then
			node = pini:FindNode(id)
			if node == nil or node.type ~= "Sprite" then
				node = pini.Sprite(id,path,overoll)
				pini:AttachDisplay(node,parent)
			else
				AnimMgr:stop(node)
				node:StopAction();
				node:setSprite(path)
				node:setVisible(true)
			end
		else
			node = pini.Sprite(id,path,overoll)
			if node == nil then
			-- 	Utils.MessageBox("이미지를 로딩할 수 없습니다. \n이미지 이름 : "..path,PROJ_TITLE)
			-- 	if IS_RELEASE == nil then
			-- 		Utils.MessageBox("엔진에 이미지가 정상적으로 포함되어 있다면 '클린 테스트'를 진행해주시기 바랍니다.",PROJ_TITLE)
			-- 	end
				return 
			end

			pini:AttachDisplay(node,parent)
		end

		node:setBlendMode(blendMode)
		node:setAnchorPoint(acp[1] or 0.5,1-(acp[2] or 0.5))
		node:setScale(StrEnumToScale(node,size))
		if x or y then
			node:setPosition(x or 0,y or 0)
		else
			node:setPosition(StrEnumToPos(node,pos))
		end

		local c = color:explode(",")
		if GUI then
			node:setZ(9999999)
			node.touchPriority = GUI_PRIORITY
		end
		node:setIncludeScreenShot(screenshot)
		node:setColor(tonumber(c[1] or 255),tonumber(c[2] or 255),tonumber(c[3] or 255))
		node:setOpacity(tonumber(opacity or 255))
		node:setFlip(flipX,flipY)
		node:setPreserve(isPreserve)
		node:setRotate(angle)

		if not OnPreview then
			if enableAnti then
				node.node:getTexture():setAntiAliasTexParameters()
			else
				node.node:getTexture():setAliasTexParameters()
			end
		end

		if type(connect)=="string" and connect:len() > 0 then
			node.connect = connect
			node.onTouchUp = function(location,self)
				node = pini:FindNode(self.id)
				if node == nil or node.type ~= "Sprite" then
				else
					pini.XVM:GotoBookmarkNewCall(self.connect)
				end
			end
			pini.TouchManager:registNode(node)
		end

		if effect:len() > 0 then
			if fs_imageEffect[effect] then
				fs_imageEffect[effect](node,effectSec)
			end
		end
	end
end

function LNX_TEXT(vm,stck)
	local id = vm:ARGU("텍스트","아이디","")
	local text1 = vm:ARGU("텍스트","텍스트","")
	local text2 = vm:ARGU("텍스트","내용","")
	local pos = vm:ARGU("텍스트","위치","화면중앙")
	local effect = vm:ARGU("텍스트","효과","")
	local effectSec = vm:ARGU("텍스트","효과시간",0)
	local font = vm:ARGU("텍스트","글꼴","NanumBarunGothic.ttf")
	local size = vm:ARGU("텍스트","크기",20)
	local color = vm:ARGU("텍스트","색상","255,255,255")
	local opacity = vm:ARGU("텍스트","투명도","255")
	local parent = vm:ARGU("텍스트","부모","")
	local screenshot = vm:ARGU("텍스트","스크린샷노출","예")
	local GUI = vm:ARGU("텍스트","GUI","아니오")
	local align = vm:ARGU("텍스트","정렬","중앙")
	local x = vm:ARGU("텍스트","x","")
	local y = vm:ARGU("텍스트","y","")
	local flip = vm:ARGU("텍스트","반전","")
	local isPreserve = vm:ARGU("텍스트","항상표시","아니오")
	local outline = vm:ARGU("텍스트","외곽선",nil)--"r,g,b,a,w"
	local shadow  = vm:ARGU("텍스트","그림자",nil)--"r,g,b,a,x,y,w"
	local glow = vm:ARGU("텍스트","글로우",nil) -- "r,g,b,a"
	--local blendMode = vm:ARGU("텍스트","색상모드","기본")

	--텍스트인자를 "내용"으로 바꾸려고하니 기존에 "텍스트"로 작업했던 사람들을 위한 하위호환
	text1 = tostring(text1)
	text2 = tostring(text2)
	local text = text1
	if text2 and text2:len() > 0 then
		text = text2
	end

	x = tonumber(x)
	y = tonumber(y)
	
	GUI = GUI=="예"
	screenshot = screenshot=="예"
	isPreserve = isPreserve=="예"

	local flipX = false
	local flipY = false
	if flip == "좌우" then
		flipX = true
	elseif flip == "상하" then
		flipY = true
	elseif flip == "상하좌우" then
		flipX = true
		flipY = true
	end

	text = tostring(text)
	if text:len() > 0 then
		local node = pini.Label(id,text,font,size)
		local c = color:explode(",")
		node:setColor(tonumber(c[1] or 255),tonumber(c[2] or 255),tonumber(c[3] or 255))
		node:setOpacity(tonumber(opacity or 255))
		node:setFlip(flipX,flipY)

		if x or y then
			node:setPosition(x or 0,y or 0)
		else
			node:setPosition(StrEnumToPos(node,pos))
		end
		

		if align == "왼쪽" then
			node:setAnchorPoint(0,0.5)
		elseif align == "중앙" then
			node:setAnchorPoint(0.5,0.5)
		elseif align == "오른쪽" then
			node:setAnchorPoint(1,0.5)
		end
		
		if GUI then
			node:setZ(9999999)
			node.touchPriority = GUI_PRIORITY
		end
		if outline then
			local o = outline:explode(",")
			node:setStroke(o[1] or 0,o[2] or 0,o[3] or 0,o[4] or 0,o[5] or 0)
		end
		if shadow then
			local s = shadow:explode(",")
			node:setShadow(s[1] or 0,s[2] or 0,s[3] or 0,s[4] or 0,s[5] or 0,-(s[6] or 0),s[7] or 0)
		end
		if glow then
			local g = glow:explode(",")
			node:setGlow(g[1] or 0,g[2] or 0,g[3] or 0,g[4] or 0)
		end
		node:setIncludeScreenShot(screenshot)
		node:setPreserve(isPreserve)
		pini:AttachDisplay(node,parent)

		if effect:len() > 0 then
			if fs_imageEffect[effect] then
				fs_imageEffect[effect](node,effectSec)
			end
		end
	end
end

function LNX_TEXTINPUT(vm,stck)
	local id = vm:ARGU("입력필드","아이디","")
	local pos = vm:ARGU("입력필드","위치","화면중앙")
	local parent = vm:ARGU("입력필드","부모","")
	local x = vm:ARGU("입력필드","x","")
	local y = vm:ARGU("입력필드","y","")
	local str = vm:ARGU("입력필드","내용","")
	local max = vm:ARGU("입력필드","길이제한","0")
	local holder = vm:ARGU("입력필드","라벨","무엇을 입력할까요?")
	local font = vm:ARGU("입력필드","글꼴","NanumBarunGothic.ttf")
	local size = vm:ARGU("입력필드","크기",20)
	local password = vm:ARGU("입력필드","패스워드","아니오")
	local color = vm:ARGU("입력필드","색상","255,255,255")
	local GUI = vm:ARGU("입력필드","GUI","아니오")
	GUI = GUI=="예"

	x = tonumber(x)
	y = tonumber(y)
	max = tonumber(max) or 0

	password = password == "예"

	if max == 0 then
		max = nil
	end

	local node = pini.TextInput(id,holder,str,font,size,GUI)
	if x or y then
		node:setPosition(x or 0,y or 0)
	else
		node:setPosition(StrEnumToPos(node,pos))
	end

	if max then
		node:setMaxLength(max)
	end

	if password then
		node:setPasswordMode(password)
	end

	color = color:explode(",")
	node:setColor(color[1] or 0,color[2] or 0,color[3] or 0)

	pini:AttachDisplay(node,parent)
end

function LNX_TOINT(vm,stck)
	local value = vm:ARGU("수변환","값","")

	vm:returnValue(tonumber(value) or 0)
end

function LNX_SLIDERVALUE(vm,stck)
	local id = vm:ARGU("슬라이더값","아이디","")
	
	local node = pini:FindNode(id)
	if node and node.type=="Slider" then
		vm:returnValue(node:getValue())
	else
		vm:returnValue(0)
	end

end

function LNX_SLIDER(vm,stck)
	local id = vm:ARGU("슬라이더","아이디","")
	local pos = vm:ARGU("슬라이더","위치","화면중앙")
	local val = vm:ARGU("슬라이더","값",0)
	local read = vm:ARGU("슬라이더","읽기전용","아니오") == "예"
	local x = vm:ARGU("슬라이더","x",nil)
	local y = vm:ARGU("슬라이더","y",nil)
	local img1 = vm:ARGU("슬라이더","빈칸이미지",nil)
	local img2 = vm:ARGU("슬라이더","채움이미지",nil)
	local img3 = vm:ARGU("슬라이더","앵커이미지",nil)
	local parent = vm:ARGU("슬라이더","부모","")
	local screenshot = vm:ARGU("슬라이더","스크린샷노출","예")
	local GUI = vm:ARGU("슬라이더","GUI","아니오")

	x = tonumber(x)
	y = tonumber(y)
	val = tonumber(val) or 0

	id = tostring(id) or ""
	if img1 == nil then img1 = "피니/UI/sliderTrack2.png" end
	if img2 == nil then img2 = "피니/UI/sliderProgress2.png" end
	if img3 == nil then img3 = "피니/UI/sliderThumb.png" end

	if id:len() > 0  then
		local node = pini.Slider(id,img1,img2,img3)
		if node == nil then
			Utils.MessageBox("슬라이더를 로딩할 수 없습니다. \n이미지 이름 : "..img1.."\n이미지 이름 : "..img2.."\n이미지 이름 : "..img3,PROJ_TITLE)
			if IS_RELEASE == nil then
				Utils.MessageBox("엔진에 이미지가 정상적으로 포함되어 있다면 '클린 테스트'를 진행해주시기 바랍니다.",PROJ_TITLE)
			end
			return 
		end
		node:setValue(val)
		pini:AttachDisplay(node,parent)

		if read then
			node:setEnabled(false)
		end

		if x or y then
			node:setPosition(x or 0,y or 0)
		else
			node:setPosition(StrEnumToPos(node,pos))
		end
		node:setIncludeScreenShot(screenshot)

		if GUI then
			node:setZ(9999999)
			node.touchPriority = GUI_PRIORITY
		end
	end
end

function LNX_GOTOBOOKMARK(vm,stck)
	local label = vm:ARGU("북마크이동","북마크","")
	if OnPreview then
	else
		vm:_return()
		vm:GotoBookmark(label)
	end
end

function LNX_CLEANUP_MEMORY(vm,stck)
	if OnPreview then

	else
		local cache = cc.Director:getInstance():getTextureCache()
		if #pini.password == 0 then
			cache:removeUnusedTextures()
		end
		xlsxCache = {}

		collectgarbage("collect")
	end
end

function LNX_DELDEFAULTARGU(vm,stck)
	local macro = vm:ARGU("기본값해제","매크로명","")
	local argu = vm:ARGU("기본값해제","인자명","")
	
	_LNXG["___"..macro.."."..argu] = nil
end

function LNX_SETDEFAULTARGU(vm,stck)
	local macro = vm:ARGU("기본값","매크로명","")
	local argu = vm:ARGU("기본값","인자명","")
	local value = vm:ARGU("기본값","값","")
	
	_LNXG["___"..macro.."."..argu] = value
end

function LNX_GET_ENVIRONMENT(vm,stck)
	local envType = vm:ARGU("현재환경","종류","")
	local targetPlatform = nil

	if cc then
		targetPlatform = cc.Application:getInstance():getTargetPlatform()
	end

	if envType == "리모트" then
		vm:returnValue(OnPreview and 0 or 1)
	elseif envType == "프리뷰" then
		vm:returnValue(OnPreview and 1 or 0)
	elseif envType == "익스포트" then
		vm:returnValue(IS_RELEASE and 1 or 0)
	elseif envType == "모바일" then
		if targetPlatform then
			if targetPlatform == kTargetWindows or targetPlatform == kTargetMacOS then
				vm:returnValue(0)
			else
				vm:returnValue(1)
			end
		else
			vm:returnValue(0)
		end
	elseif envType == "운영체제" then
		local target = "알수없음"
		if OnPreview then
			target = "윈도우즈"
		elseif targetPlatform == kTargetWindows then
			target = "윈도우즈"
		elseif targetPlatform == kTargetMacOS then
			target = "맥OS"
		elseif targetPlatform == kTargetAndroid then
			target = "안드로이드"
		elseif targetPlatform == kTargetIphone or targetPlatform == kTargetIpad then
			target = "iOS"
		end
		vm:returnValue(target)
	end
end

function LNX_GET_NODEINFO(vm,stck)
	local nodeId = vm:ARGU("노드정보","아이디","")
	local _type = vm:ARGU("노드정보","타입","")

	local node = pini:FindNode(nodeId)

	if node then
		local x, y = node:position()
		local rot = node:getRotate()
		
		if _type == "X좌표" then
			vm:returnValue(x)
		elseif _type == "Y좌표" then
			vm:returnValue(y)
		elseif _type == "회전값" then
			vm:returnValue(rot)
		end
	end
end

function LNX_TOUCHGESTURE(vm,stck)
	local id = vm:ARGU("터치제스처","아이디","")
	local func = vm:ARGU("터치제스처", "매크로명", "")

	pini:scene():registTouchGesture(id,loadstring([[
	return function(touchCount,touchType)
		local f = "]]..func..[["
		_LNXG["터치제스처.터치갯수"] = touchCount
		_LNXG["터치제스처.터치타입"] = touchType
		pini.XVM:call(f)
	end]])())
end

function LNX_REMOVETOUCHGESTURE(vm,stck)
	local id = vm:ARGU("터치제스처해제","아이디","")
	pini:scene():unregistTouchGesture(id)
end

function LNX_TOUCHAREA(vm,stck)
	local id = vm:ARGU("터치영역","아이디","")
	local pos = vm:ARGU("터치영역","위치","")
	local size = vm:ARGU("터치영역","크기","")
	local connect = vm:ARGU("터치영역","북마크이동","")
	local x = vm:ARGU("터치영역","x","")
	local y = vm:ARGU("터치영역","y","")
	local GUI = vm:ARGU("터치영역","GUI","아니오")

	GUI = GUI=="예"

	x = tonumber(x)
	y = tonumber(y)

	local op = 0
	if OnPreview then
		op = 40
	end

	local s = size:explode(",")
	local node = pini.ColorLayer(id,225,30,30,op,s[1] or 0,s[2] or 0)
	if x or y then
		node:setPosition(x or 0,y or 0)
	else
		local px,py = unpack(pos:explode(","))
		node:setPosition(tonumber(px) or 0,tonumber(py) or 0)
	end
	node.connect = connect
	node.onTouchUp = function(location,self)
		pini.XVM:GotoBookmarkNewCall(self.connect)
	end

	if GUI then
		node:setZ(9999999)
		node.touchPriority = GUI_PRIORITY
	end

	pini.TouchManager:registNode(node)

	pini:AttachDisplay(node)
end


function LNX_REGIST_VARIABLE_TRIGGER(vm,stck)
	local id = vm:ARGU("변수트리거","아이디","")
	local variableName = vm:ARGU("변수트리거","변수이름")
	local func = vm:ARGU("변수트리거","매크로")

	vm:registVariableTrigger(id,variableName,loadstring([[
	return function()
		local f = "]]..func..[["
		local vn = "]]..variableName..[["

		pini.Timer(pini:GetUUID(),0,function()
			_LNXG["변수트리거.변수이름"] = vn
			pini.XVM:call(f)
		end,false):run()
	end]])())
end

function LNX_UNREGIST_VARIABLE_TRIGGER(vm,stck)
	local id = vm:ARGU("변수트리거해제","아이디","")

	vm:unregistVariableTrigger(id)
end

function LNX_TEXTINPUT_GET(vm,stck)
	local id = vm:ARGU("입력필드가져오기","아이디","")
	local node = pini:FindNode(id)
	if node then 
		if node.type == "TextInput" then
			vm:returnValue( node:string() )
		end
	end
end

function LNX_ADS(vm,stck)
	local isBanner = vm:ARGU("광고","배너","아니오")
	
	isBanner = isBanner == "예"

	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			if isBanner then
				DeviceNativeCall("ADS_Banner",{ })
			else
				DeviceNativeCall("ADS_Fullscreen",{ })
			end
		end
	end
end

function LNX_VUNGLE_INIT(vm, arg)
	local appId = vm:ARGU("벙글광고초기화","앱아이디","")

	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			DeviceNativeCall("VungleInit", { appId }) 
		end
	end
end

function LNX_VUNGLE_SHOW(vm, arg)
	local func = vm:ARGU("벙글광고표기", "매크로", "")

	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			vm.vungleCallback = func
			DeviceNativeCall("VunglePlay", { })
		else
			_LNXG["벙글광고표기.길이"] = 15.01 -- 고ㅈ값을 리턴합니다.
			pini.XVM:call(func)
		end
	end
end

function LNX_IAP_SETTING(vm, arg)
	local publickey = vm:ARGU("결제모듈셋팅","공개키","")
	
	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			DeviceNativeCall("IAB_Settings",{ publickey })
		end
	end
end

function LNX_IAP_REQUEST(vm,stck)
	local id = vm:ARGU("결제요청","아이템","")

	vm:returnValue( 0 )
	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			if VM_BLOCK_FOR_ANDROID == nil then
				VM_BLOCK_FOR_ANDROID = vm:stop()
				DeviceNativeCall("IAB_Buy",{ id })
			else
				print ("LNX_IAP_REQUEST() ignored. because android blocking is progressing")
			end
		else
		end
	end
end

function LNX_IAP_CONSUME(vm,stck)
	local id = vm:ARGU("결제소비","아이템","")

	vm:returnValue( 0 )
	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			if VM_BLOCK_FOR_ANDROID == nil then
				VM_BLOCK_FOR_ANDROID = vm:stop()
				DeviceNativeCall("IAB_Consume",{ id })
			else
				print ("LNX_IAP_REQUEST() ignored. because android blocking is progressing")
			end
		else
		end
	end
end

function LNX_IAP_CHECK(vm, arg)
	local id = vm:ARGU("결제확인","아이템","")
	
	vm:returnValue( 0 )
	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			if VM_BLOCK_FOR_ANDROID == nil then
				VM_BLOCK_FOR_ANDROID = vm:stop()
				DeviceNativeCall("IAB_Check",{ id })
			else
				print ("LNX_IAP_REQUEST() ignored. because android blocking is progressing")
			end
		else
		end
	end
end

function LNX_LOCAL_PUSH(vm,stck)
	local title = vm:ARGU("로컬푸시","타이틀","")
	local text  = vm:ARGU("로컬푸시","텍스트","")
	local vibrate = vm:ARGU("로컬푸시","진동",0)
	local day   = vm:ARGU("로컬푸시","일",0)
	local hour  = vm:ARGU("로컬푸시","시",0)
	local min   = vm:ARGU("로컬푸시","분",0)
	local sec   = vm:ARGU("로컬푸시","초",10)
	
	vibrate = tonumber(vibrate) or 0
	day  = tonumber(day) or 0 
	hour = tonumber(hour) or 0 
	min  = tonumber(min) or 0 
	sec  = tonumber(sec) or 10 

	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			DeviceNativeCall("Device_LocalPush",{ title, text, vibrate, day, hour, min, sec })
		end
	end
end

function LNX_GET_XLSX_DATA(vm,stck)
	local path  = vm:ARGU("엑셀","파일명")
	local sheet = vm:ARGU("엑셀","시트","")
	local row   = vm:ARGU("엑셀","행","0")
	local col   = vm:ARGU("엑셀","열","0")

	path = tostring(path) or ""
	row = tostring(row) or ""
	col = tostring(col) or ""

	vm:returnValue("")
	if path:len() > 0 then
		fPath = FILES["etc/"..path]
		if fPath then
			local path = ROOT_PATH..fPath
			if xlsxCache[path] == nil then
				local f = io.open(path, "rb")
				if f then
					xlsxCache[path] = json.decode(f:read("*all"))
				else
					xlsxCache[path] = json.decode(fileUtil:getStringFromFile(fPath))
				end
			end

			sheet = tostring(sheet) or ""
			data = xlsxCache[path]
			if data then
				if sheet:len() == 0 then
					sheet = data["primary"]
				end

				if data[sheet] and data[sheet][row] and data[sheet][row][col] then 
					vm:returnValue(data[sheet][row][col])
				end
			end
		end
	end
end

function LNX_FLOOR(vm,stck)
	local num  = vm:ARGU("소수점버림","수",0)
	vm:returnValue(math.floor(num))
end

function LNX_ROUND(vm,stck)
	local num  = vm:ARGU("반올림","수",0)
	vm:returnValue(math.floor(num+0.5))
end

function LNX_VIBRATE(vm,stck)
	local sec   = vm:ARGU("진동","시간",10)
	
	sec = tonumber(sec) or 10 

	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			--DeviceNativeCall("Device_Vibrator",{ sec })
		end
	end
end

function LNX_VALUE_TYPE_CHECK(vm,stck)
	local id = vm:ARGU("타입체크","변수명","")

	if _LNXG[id] then 
		if _LNXG[id] == nil then
			vm:returnValue( "없음" )
		elseif type(_LNXG[id]) == "string" then
			vm:returnValue( "문자열" )
		elseif type(_LNXG[id]) == "number" then
			vm:returnValue( "숫자" )
		else
			vm:returnValue( "그외" )
		end
	end
end

function LNX_LOG(vm,stck)
	local text = vm:ARGU("로그","텍스트","")
	if OnPreview then
		-- ENGINE_LOG(text)
	else
		print(text)
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			DeviceNativeCall("Android_Toast",{ tostring(text) , 1})
		end
	end
end

function LNX_DELETENODE(vm,stck)
	local id = vm:ARGU("삭제","아이디","")
	local effect = vm:ARGU("삭제","효과","")
	local effectSec = vm:ARGU("삭제","효과시간",0.25)
	if id:len() > 0 then
		local node = pini:FindNode(id)
		if node then
			if effect:len() > 0 then
				if fs_imageDeleteEffect[effect] then
					node:changeId(pini:GetUUID())
					fs_imageDeleteEffect[effect](node,effectSec)

					pini.Timer(nil,effectSec,function(t)
						local node = pini:FindNode(t.userdata.id)
						if node then
							pini:DetachDisplay(node)
						end
					end,false,nil,{id=node.id}):run()

					local function recursiveEff(node)
						local children = node:children()
						if children then
							for k,v in ipairs(children) do
								recursiveEff(v)
								fs_imageDeleteEffect["페이드"](v,effectSec)
							end
						end
					end

					recursiveEff(node)
				end
			else
				pini:DetachDisplay(node)
			end
		end
	end
end

function LNX_MODAL_NODE(vm,stck)
	local id = vm:ARGU("이전터치막기","아이디","")
	local touches = pini.Node(id)
	touches:setContentSize(99999,99999)
	touches.onTouchUp = function(location) end
	touches:registOnExit("touch_modal",function(v)
		pini:scene():playAllTouchGesture(v.id)
	end)
	touches.perfectPriority = true
	pini.TouchManager:registNode(touches)
	pini:AttachDisplay(touches)
	pini:scene():pauseAllTouchGesture(id)
end

function LNX_MODAL_KEY(vm,stck)
	local id = vm:ARGU("이전키입력막기","아이디","")
	local modalkey = pini.Node(id)
	modalkey:registOnExit("key_modal",function(v)
		pini:scene():playAllKeyboard(v.id)
	end)
	pini:AttachDisplay(modalkey)
	pini:scene():pauseAllKeyboard(id)
end

function build_plaintText_To_extendArgu(_sarg,contents)
	local sarg = {}
	if #contents > 0 then
		for k,v in ipairs(contents:explode("\n")) do
			local strs = {}
			v:gsub(".",function(c) table.insert(strs,c) end)

			local word = ""
			local cntUTF = 0
			table.insert(sarg,{t=1,v="\n"})
			for k,v in ipairs(strs) do
				if mode then
					word = word..v
					if v == ">" then
						mode = false

						word = word:sub(2,word:len()-1)
						local words = word:explode(" ")
						local name = words[1]
						table.remove(words,1)
						local args = words
						table.insert(sarg,{t=0,v={name=name,args=args}})

						word=""
					end
				else
					if v == "<" and strs[k-1] ~= "<" and strs[k+1] ~= "<" then
						table.insert(sarg,{t=1,v=word})
						word = "<"
						mode = true
					else
						if string.byte(v) <= 127 then 
							table.insert(sarg,{t=1,v=v})
						else
							word = word..v
							cntUTF = cntUTF+1
							if cntUTF == 3 then
								table.insert(sarg,{t=1,v=word})
								cntUTF = 0
								word = ""
							end
						end
					end
				end
			end
			if word:len() > 0 then
				table.insert(sarg,{t=1,v=word})
			end
		end
	end

	for k,v in ipairs(_sarg) do
		table.insert(sarg,v)
	end
	return sarg
end

function LNX_MONOLOG(vm,stck)
	local forceOn = vm:ARGU("독백","유지","아니오") == "예"
	local window = vm:ARGU("독백","대사창","독백")
	local contents = vm:ARGU("독백","내용","")
	local sec = vm:ARGU("독백","대기시간",0)
	local inputwait = vm:ARGU("독백","입력대기","예") == "예"
	
	sec = tonumber(sec) or 0
	if sec == 0 then
		sec = pini.AutoreadSpeed or 0
	end

	pini.Dialog:setName(nil)
	pini.Dialog:UseConfig(window)

	if forceOn == false then
		pini.Dialog:Reset()
	end
	pini.Dialog:WaitConfig(inputwait,sec)

	local isAdd = false

	local sarg = build_plaintText_To_extendArgu({},contents)
	local args_tmp = {}
	for k,v in ipairs(sarg) do 
		if v["t"] == 1 then
			table.insert(args_tmp,v["v"])
		else
			if #args_tmp > 0 then
				pini.Dialog:Add(args_tmp)
				args_tmp={}
				isAdd = true
			end
			--pini.Dialog:AddMarkup(v)
		end
	end
	if #args_tmp > 0 then
		pini.Dialog:Add(args_tmp)
		isAdd = true
	end

	if OnPreview then
	else
		if isAdd then
			pini.Dialog:AddMarkup({name="클릭",args={}})
		else 
		end
	end
end

function LNX_DIALOG(vm,stck)
	local name = vm:ARGU("대화","이름","")
	local forceOn = vm:ARGU("대화","유지","아니오") == "예"
	local contents = vm:ARGU("대화","내용","")
	local window = vm:ARGU("대화","대사창","대화")
	local sec = vm:ARGU("대화","대기시간",0)
	local inputwait = vm:ARGU("대화","입력대기","예") == "예"

	sec = tonumber(sec) or 0
	if sec == 0 then
		sec = pini.AutoreadSpeed or 0
	end

	name = tostring(name)
	if name:len() > 0 then
		pini.Dialog:setName(name)
	else
		pini.Dialog:setName(nil)
	end

	if forceOn == false then
		pini.Dialog:Reset()
	end

	pini.Dialog:UseConfig(window)
	pini.Dialog:WaitConfig(inputwait,sec)

	local isAdd = false

	local sarg = build_plaintText_To_extendArgu({},contents)
	local args_tmp = {}
	for k,v in ipairs(sarg) do 
		if v["t"] == 1 then
			table.insert(args_tmp,v["v"])
		else
			if #args_tmp > 0 then
				pini.Dialog:Add(args_tmp)
				args_tmp={}
				isAdd = true
			end
			--pini.Dialog:AddMarkup(v)
		end
	end
	if #args_tmp > 0 then
		pini.Dialog:Add(args_tmp)
		isAdd = true
	end

	if OnPreview then
	else
		if isAdd then
			pini.Dialog:AddMarkup({name="클릭",args={}})
		else 
		end
	end
end

function LNX_REMOVEDIALOG(vm,stck)
	pini.Dialog:Reset()
end

function LNX_HTTP_REQUEST(vm,stck)
	if OnPreview then
		vm:returnValue(0)
		return 
	end

	--값 = [인터넷연결 주소="" 타입="GET,POST" 인자수="3" 키1="" 값1="" 키2="" 값2="" 키3="" 값3=""]
	local request_url  = vm:ARGU("인터넷연결","주소")
	local request_type = vm:ARGU("인터넷연결","타입")
	local request_num  = vm:ARGU("인터넷연결","인자수")

	local xhr = cc.XMLHttpRequest:new()
	xhr.responseType = cc.XMLHTTPREQUEST_RESPONSE_STRING
	xhr:open(request_type, request_url)

	local arg = "";
	for i=1,request_num,1 do
		if i > 1 then
			arg = arg.."&"
		end

		local _id = vm:ARGU("인터넷연결","키"..i)
		local _val= vm:ARGU("인터넷연결","값"..i)
		if _id and _val then
			arg = arg.._id..'='..urlencode(_val)
		end
	end

	local callstack = pini.XVM:stop()

	local function onReadyStateChange()
		if xhr.readyState == 4 and (xhr.status >= 200 and xhr.status < 207) then
			local response = xhr.response
			vm:returnValue(response)
		else
			print("xhr.readyState is:", xhr.readyState, "xhr.status is: ",xhr.status)
		end
		pini.XVM:resume(callstack)
	end

	xhr:registerScriptHandler(onReadyStateChange)
	xhr:send(arg)
end

function LNX_BROWSER_OPEN(vm,stck)
	if OnPreview then
		return
	end

	local text = vm:ARGU("브라우저","주소","")
	text = tostring(text) or ""

	cc.Application:getInstance():openURL(text);
end

function LNX_STRING_SUB(vm,stck)
	local text   = vm:ARGU("문자열일부","문자열","")
	local start  = vm:ARGU("문자열일부","시작",0)
	local length = vm:ARGU("문자열일부","길이",5)

	start  = tonumber(start) or 0
	length = (tonumber(length) - 1) or 0

	text = tostring(text) or ""

	vm:returnValue( text:sub(start,start+length) )
end

function LNX_ANIMATION(vm,stck)
	local id = vm:ARGU("애니메이션","아이디","")
	local t = vm:ARGU("애니메이션","타입","")
	
	if id == "" then
		if fs_animation[t] then
			local stack
			if not OnPreview then
				stack = vm:stop()
			end

			for i,v in pairs(pini._regist_.Display) do
				if i:startsWith("PINI") == false then
					fs_animation[t][2](vm,v)
					v.onAnim = true
				end
			end

			if not OnPreview then
				vm:resume(stack)
			end
		end
	else
		local node = pini:FindNode(id)
		if node and fs_animation[t] then
			fs_animation[t][2](vm,node)
			node.onAnim = true
		end
	end
end

function LNX_ANIMATIONSTOP(vm,stck)
	local id = vm:ARGU("애니메이션중지","아이디","")
	
	local node = pini:FindNode(id)
	if node then
		node:StopAction();
		AnimMgr:stop(node)
	end
end

function LNX_STOP(vm,stck)
	if OnPreview then
	else
		vm:_return()
		vm:stop()
	end
end

function LNX_WAIT(vm,stck)
	if OnPreview then
	else
		local time = tonumber(vm:ARGU("대기","시간",0)) 

		vm:sleep(time)
	end
end

function LNX_ANDROIDSETPUBLICKKEY(vm,stck)
	local pkey = vm:ARGU("안드로이드공개키설정","키","")
	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			DeviceNativeCall("Extension_SetPublicKey",{pkey})
		end
	end
end

function LNX_ANDROIDEXTENSION_CHECK(vm,stck)
	local isMain   = vm:ARGU("확장파일검사","타입","메인") == "메인"
	local version  = vm:ARGU("확장파일검사","버전","1")
	local fileSize = vm:ARGU("확장파일검사","파일크기","0")
	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then

			local _type = "main"
			if isMain == false then
				_type = "fetch"
			end

			local ret = DeviceNativeCall("ExtensionFile_IsFileExists",{_type,version,tostring(fileSize)},"(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Z")
			if ret then 
				vm:returnValue( 1 )
			else
				vm:returnValue( 0 )
			end
		end
	end
end

function LNX_ANDROIDEXTENSION_DOWNLOAD(vm,stck)
	vm:returnValue(1)
	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			if VM_BLOCK_FOR_ANDROID == nil then
				VM_BLOCK_FOR_ANDROID = vm:stop()
				--DeviceNativeCall("Android_Toast",{tostring(VM_BLOCK_FOR_ANDROID),1})
				DeviceNativeCall("ExtensionFile_Download",{})
			else
				print ("LNX_IAP_REQUEST() ignored. because android blocking is progressing")
			end
		end
	end
end

function LNX_ANDROIDEXTENSION_MOUNT(vm,stck)
	local isMain = vm:ARGU("확장파일마운트","타입","메인") == "메인"
	local version = vm:ARGU("확장파일마운트","버전","1")
	if OnPreview then
	else
		if cc.PLATFORM_OS_ANDROID == CurrentPlatform then
			local _type = "main"
			if isMain == false then
				_type = "fetch"
			end
			local package = AppPackageName();
			local obbpath = OBBDirPath();

			print("LNX_ANDROIDEXTENSION_MOUNT >> ",obbpath.."/".._type.."."..version.."."..package..".obb")
			table.insert(pini.FindZip,obbpath.."/".._type.."."..version.."."..package..".obb")
			--table.insert(pini.FindZip,obbpath.."/extension.prz")
		end
	end
end

function LNX_CLICKWAIT(vm,stck)
	local sec = vm:ARGU("클릭대기","대기시간",0)

	sec = tonumber(sec) or 0
	if sec == 0 then
		sec = pini.AutoreadSpeed or 0
	end

	if OnPreview ~= true then
		callstack = vm:stop()
		local node = pini.Node("ClickWait")
		node:setContentSize(99999,99999)
		node.touchPriority = CLICK_WAIT_PRIORITY
		node.callstack = callstack
		node.onTouchUp = function(pos,v)
			pini:DetachDisplay(v)
			pini.XVM:resume(v.callstack)
		end

		pini.TouchManager:registNode(node)
		pini:AttachDisplay(node)

		if sec > 0 then
			pini.Timer("PINI_ClickWait_Update",0,function(t)
				t.userdata.endtime = t.userdata.endtime + t.dt
				if t.userdata.endtime > t.userdata.waitsec then
					pini.XVM:resume(t.userdata.callstack)
				end
			end,true,nil,{
				endtime = 0,
				waitsec = sec,
				callstack = callstack
			}):run()
		end
	else
	end
end

function LNX_SCREENFILTER(vm,stck)
	local id  = vm:ARGU("필터","아이디","")
	local _type = vm:ARGU("필터","타입","좌우")
	local sec = vm:ARGU("필터","시간",0)
	--local dir = vm:ARGU("필터","방향",0)
	--local pwr = vm:ARGU("필터","강도",14.0)

	id = tostring(id) or ""
	_type = tostring(_type) or ""
	sec = tonumber(sec) or 0

	if id:len() > 0 and _type:len() > 0 then
		if OnPreview then
			local node = pini:FindNode(id)
			if node then
				node:setColor(30,30,255)
				node:setOpacity(200)
			else
				local node = pini.ColorLayer(id,30,30,255,60,WIN_WIDTH,WIN_HEIGHT)
				node:setPosition(0,WIN_HEIGHT)
				pini:AttachDisplay(node) 
			end
		else
			local node = pini:FindNode(id)
			if node == nil then
				local currentNodeList = {}
				for k,v in pairs(pini._regist_.Display) do
					if k:startsWith("PINI") == false then
						if v:isVisible() then
							table.insert(currentNodeList,v.id)
						end
					end
				end

				node = pini.RenderTexture( id, WIN_WIDTH, WIN_HEIGHT, currentNodeList )
				pini:AttachDisplay(node)
			end

			local shader = nil
			if _type == "블러" then
				local dir = vm:ARGU("필터","방향",0)
				local pwr = vm:ARGU("필터","강도",14.0)
				pwr = (tonumber(pwr) or 14.0)/1000.0
				
				if dir == "상하" then
					shader = pini.Shader(pini:GetUUID(),"filter/gaussianblur_v.vsh", "filter/gaussianblur.fsh")
				else
					shader = pini.Shader(pini:GetUUID(),"filter/gaussianblur_h.vsh", "filter/gaussianblur.fsh")
				end
				shader:setUniformFloat("power",pwr)
			elseif _type == "흑백" then
				shader = pini.Shader(pini:GetUUID(),"filter/grayscale.vsh", "filter/grayscale.fsh")
			elseif _type == "세피아" then
				shader = pini.Shader(pini:GetUUID(),"filter/sepia.vsh", "filter/sepia.fsh")
			elseif _type == "모자이크" then
				shader = pini.Shader(pini:GetUUID(),"filter/mosaic.vsh", "filter/mosaic.fsh")
				shader:setUniformFloat("pixel",0.01);
			elseif _type == "펜선" then
				shader = pini.Shader(pini:GetUUID(),"filter/line.vsh", "filter/line.fsh")
			elseif _type == "LED" then
				local num = vm:ARGU("필터","갯수",100)
				num = tonumber(num) or 100

				shader = pini.Shader(pini:GetUUID(),"filter/led.vsh", "filter/led.fsh")
				shader:setUniformFloat("pixelsNum",num)
			elseif _type == "빛샘" then
				shader = pini.Shader(pini:GetUUID(),"filter/volumetric.vsh", "filter/volumetric.fsh")
			elseif _type == "반전" then
				shader = pini.Shader(pini:GetUUID(),"filter/reverse.vsh", "filter/reverse.fsh")
			elseif _type == "빛번짐" then
				local pwr = vm:ARGU("필터","강도",7.0)
				shader = pini.Shader(pini:GetUUID(),"filter/bloom.vsh", "filter/bloom.fsh")
				shader:setUniformFloat("power",pwr)
			elseif _type == "노이즈" then
				local num = vm:ARGU("필터","갯수",400.0)
				shader = pini.Shader(pini:GetUUID(),"filter/noise.vsh", "filter/noise.fsh")
				shader:setUniformFloat("nums",num)
			elseif _type == "실루엣" then
				local color = vm:ARGU("필터","색상","0,0,0")
				color = color:explode(",")
				shader = pini.Shader(pini:GetUUID(),"filter/silhouette.vsh", "filter/silhouette.fsh")
				shader:setUniformFloat("_r",tonumber(color[1]) or 0)
				shader:setUniformFloat("_g",tonumber(color[2]) or 0)
				shader:setUniformFloat("_b",tonumber(color[3]) or 0)
			end

			if shader then
				shader:bind(node)
				if sec == 0 then
					shader:setUniformFloat("threshold",1)
				else
					pini.Timer(pini:GetUUID(),0,function(t)
						t.userdata.delta = t.userdata.delta + t.dt
						t.userdata.threshold = t.userdata.delta / t.userdata.max
						local shader = pini:FindShader(t.userdata.sid)
						if t.userdata.threshold > 1 then
							t:stop()
						end
						shader:setUniformFloat("threshold",t.userdata.threshold)
					end,true,nil,{sid=shader.id,threshold=0,delta=0,max=sec}):run()
				end
			end
		end
	end
end

function LNX_REMOVESCREENFILTER(vm,stck)
	local id  = vm:ARGU("필터삭제","아이디","")
	local sec = vm:ARGU("필터삭제","시간",0)
	
	sec = tonumber(sec) or 0

	local node = pini:FindNode(id)
	if node then
		if OnPreview then
			if node.type == "ColorLayer" then
				pini:DetachDisplay(node)
			else
				node:setColor(255,255,255)
				node:setOpacity(255)
			end
		elseif node.shaderID then
			local shader = pini:FindShader(node.shaderID)
			if shader then
				if sec == 0 then
					if node.type == "RenderTexture" then
						pini:DetachDisplay(node)
					else
						local shader = pini.Shader(pini:GetUUID(),"filter/normal.vsh", "filter/normal.fsh")
						shader:bind(node)
					end
				else
					pini.Timer(pini:GetUUID(),0,function(t)
						t.userdata.delta = t.userdata.delta - t.dt
						t.userdata.threshold = t.userdata.delta / t.userdata.max

						if t.userdata.threshold < 0 then
							t:stop()
							local node = pini:FindNode(t.userdata.nid)
							if node then
								if node.type == "RenderTexture" then
									pini:DetachDisplay(node)
								else
									local shader = pini.Shader(pini:GetUUID(),"filter/normal.vsh", "filter/normal.fsh")
									shader:bind(node)
								end
								return 
							end
						end

						local shader = pini:FindShader(t.userdata.sid)
						shader:setUniformFloat("threshold",t.userdata.threshold)
					end,true,nil,{nid=id,sid=shader.id,threshold=0,delta=sec,max=sec}):run()
				end
			end
		end
	end
end

function LNX_PLAYSOUND(vm,stck)
	local id = vm:ARGU("효과음","아이디","")
	local path = vm:ARGU("효과음","파일명","")
	local loop = vm:ARGU("효과음","반복","아니오")
	local vol = vm:ARGU("효과음","볼륨","1")
	local sec = vm:ARGU("효과음","시간","0")

	if id and id:len() <= 0 then
		Utils.MessageBox("효과음의 아이디가 지정되지 않았습니다. \n파일명 : "..path,PROJ_TITLE)
		return
	end

	vol = tonumber(vol) or 0
	sec = tonumber(sec) or 0

	try{
		function()
			pini:StopSound(id)
		end,
		catch {function(error)end}
	}

	pini:PlaySound(id,path,loop=="예",vol)

	if sec > 0 then
		local step = (vol or 1) / (sec*20)
		pini:SoundVolume( 0 , id )
		pini.Timer(pini:GetUUID(),0.05,function(t)
			pini:SoundVolume( t.userdata.v , t.userdata.id )
			t.userdata.v = t.userdata.v + t.userdata.step
		end,true,sec*20+1,{v=0,step=step,id=id}):run()
	end
end

local bgm_volume = "1"

function LNX_PLAYBGM(vm,stck)
	local path = vm:ARGU("배경음","파일명","")
	local brep = vm:ARGU("배경음","반복","예")
	local vol = vm:ARGU("배경음","볼륨",nil)
	local sec = vm:ARGU("배경음","시간","0")

	vol = tonumber(vol or bgm_volume)

	pini:PlayBGM(path,brep=="예",vol)

	sec = tonumber(sec) or 0

	if sec > 0 then
		local step = (tonumber(vol) or 1) / (sec*20)
		pini:SoundVolume( 0 )
		pini.Timer(pini:GetUUID(),0.05,function(t)
			pini:SoundVolume( t.userdata.v )
			t.userdata.v = t.userdata.v + t.userdata.step
		end,true,sec*20+1,{v=0,step=step}):run()
	end
end

function LNX_CHANGE_BGM_VOLUME(vm,stck)
	local vol = vm:ARGU("배경음볼륨","볼륨","1")
	local bgm_volume = tonumber(vol) or 1

	pini:SoundVolume(bgm_volume)
end

function LNX_STOPBGM(vm,stck)
	local sec = vm:ARGU("배경음끄기","시간","0")
	if pini._regist_.BGM then
		sec = tonumber(sec) or 0
		if sec > 0 then
			local sid = pini._regist_.BGM[4]
			local vol = pini._regist_.BGM[3]
			local step = vol / (sec*20)
			pini._regist_.BGM = nil

			pini:SoundVolume( vol , sid)
			pini.Timer(pini:GetUUID(),0.05,function(t)
				pini:SoundVolume( t.userdata.v , t.userdata.sid )
				t.userdata.v = t.userdata.v - t.userdata.step
				if t.userdata.v <= 0 then
					pini:StopSound( t.userdata.sid )
				end
			end,true,sec*20+1,{v=vol,step=step,sid=sid}):run()
		else
			pini:StopBGM()
		end
	end
end

function LNX_STOPSOUND(vm,stck)
	local id = vm:ARGU("효과음끄기","아이디","")
	local sec = vm:ARGU("효과음끄기","시간","0")

	if pini._regist_.Sounds[id] then
		sec = tonumber(sec) or 0
		if sec > 0 then
			local step = 1 / (sec*20)
			
			pini:SoundVolume( 1 , id )
			pini.Timer(pini:GetUUID(),0.05,function(t)
				pini:SoundVolume( t.userdata.v , t.userdata.id )
				t.userdata.v = t.userdata.v - t.userdata.step
				if t.userdata.v <= 0 then
					pini:StopSound( t.userdata.id )
				end
			end,true,sec*20+1,{v=1,id=id,step=step}):run()
		else
			pini:StopSound(id)
		end
	end
end

function LNX_APP_EXIT(vm,stck)
	if OnPreview then
	else
		if vm.VarFlush then
			vm.VarFlush()
		end

		local director = cc.Director:getInstance()
		director:endToLua()
	end
end

function LNX_TIMER(vm,stck)
	local id = vm:ARGU("타이머","아이디","")
	local func = vm:ARGU("타이머","매크로")
	local sec = vm:ARGU("타이머","시간","1")
	local loopCnt = vm:ARGU("타이머","횟수","0")

	loopCnt = tonumber(loopCnt)
	if loopCnt == 0 then loopCnt = nil end

	pini.Timer(id,sec,function(t,dt)
		_LNXG["타이머.시간차"] = dt
		pini.XVM:call(t.userdata.call)
	end,true,loopCnt,{call=func}):run()
end

function LNX_TIMER_EXIT(vm,stck)
	local id = vm:ARGU("타이머종료","아이디","")
	pini:StopTimer(id)
end

function LNX_SCREENCLEAN(vm,stck)
	pini.Dialog:Clear()
	pini:ClearNonPreserveDisplay()

	pini.Timer(pini:GetUUID(),0,function()
		
	end,false):run()
end

function LNX_GETSET_VARIABLE(vm,stck)
	local id  = vm:ARGU("변수","아이디","")
	local val = vm:ARGU("변수","값")

	if val then
		if val ~= _LNXG[id] then
			-- 값이 바뀔 경우에 한하여 변수트리거를 작동합니다.

			-- for k,v in pairs(vm.variableTriggers) do
			-- 	if v and id == v["variableName"] then
			-- 		v["func"]()
			-- 	end
			-- end
		end

		_LNXG[id] = val;

		local L_Saved = id:sub(1,1) == "$"

		if L_Saved then
			vm:VarSave(id, _LNXG[id])
		end
	end
	vm:returnValue( _LNXG[id] or 0 )
end

function LNX_JSON_PARSE(vm,stck)
	local jdata  = vm:ARGU("제이슨파싱","원문","")
	local key    = vm:ARGU("제이슨파싱","키","")

	local data = json.decode(jdata) or {}
	local d = data
	if type(data) == "table" then
		keys = key:explode("/")
		for k,v in ipairs(keys) do
			d = d[v]
			if d == nil then
				d = 0
				break
			end
		end
		if type(d) == "table" then
			d = "{배열}"
		end
	end
	vm:returnValue(d)
end

function LNX_IMAGE_LOAD(vm,stck)
	local path = vm:ARGU("이미지로딩","파일명","")
	pini.Sprite(pini:GetUUID(),path,nil,true)
end

function LNX_MOVIE_PLAYER(vm,stck)
	local id = vm:ARGU("비디오","아이디","")
	local path = vm:ARGU("비디오","파일명","")
	local video = pini.VideoPlayer(id,path)

	video:setScale(StrEnumToScale(video,"화면맞춤"))
	video:setPosition(StrEnumToPos(video,"화면중앙"))

	pini:AttachDisplay(video)

	video:play()
end

function LNX_CUSTOMANIMATION(vm,stck)
	local name = vm:ARGU("사용자애니메이션","이름","")
	local dt = vm:ARGU("사용자애니메이션","프레임시간","0.1")
	local start = vm:ARGU("사용자애니메이션","시작","0")
	local _end   = vm:ARGU("사용자애니메이션","끝",nil)
	local loopCnt 	 = vm:ARGU("사용자애니메이션","반복","1")

	start = tonumber(start)
	_end = tonumber(_end)
	loopCnt = tonumber(loopCnt)
	dt = tonumber(dt)

	if loopCnt == 0 then
		loopCnt = nil
	end

	if AnimMgr:isAnim(name) then
		local argValues = {}
		local macro = "사용자애니메이션."
		for k,v in pairs(_LNXGP) do
			if k:startsWith(macro) then
				if k:startsWith(macro.."노드") == false then
					local _k = k:sub(macro:len()+1,macro:len()+k:len());
					argValues[_k] = v
				end
			end
		end

		local num = AnimMgr:numNode(name)
		for i=1,num,1 do
			local nodeName = vm:ARGU("사용자애니메이션","노드"..i,"")
			local node = pini:FindNode(nodeName)

			local args = "";
			for k,v in pairs(argValues) do
				AnimMgr:registArgument(nodeName,k,v)
				--print(k.." : "..v.." / "..type(v))
				args = args..k.."="..v.."&"
			end

			AnimMgr:run(name,i-1,start,_end,dt,loopCnt,node,args)
		end
	end
end

function LNX_TRANSITION(vm,stck)
	local id = vm:ARGU("전환","아이디","")
	local sec = vm:ARGU("전환","시간","")
	local scale = vm:ARGU("전환","인자이미지","")
	local path = vm:ARGU("전환","이미지","")
	local size = vm:ARGU("전환","크기","화면맞춤")

	-- 화면 전환 효과는 inGame에서만 작동됨
	if OnPreview then
		pini:ClearNonPreserveDisplay()

		local img = pini.Sprite(id,path)
		img:setScale(StrEnumToScale(img,size))
		img:setPosition(StrEnumToPos(img,"화면중앙"))
		
		pini:AttachDisplay(img)
	else
		local stackId = vm:stop()
		pini:takeScreenShot(function(sprite)
			pini.Dialog:Clear()
			pini:ClearNonPreserveDisplay()

			-- newSprite = pini.Sprite(id,path,nil,true)
			sprite.id = id --pini:GetUUID()
			sprite.path = path

			local img1 = pini.Sprite("transition1",scale,nil,true)
			local img2 = pini.Sprite("transition2",path,nil,true)

			local ss = img2:contentSize()
			local dx,dy = ss.width / WIN_WIDTH ,ss.height / WIN_HEIGHT
			local sx,sy = StrEnumToScale(sprite,size)

			sprite:setPosition(WIN_WIDTH/2,WIN_HEIGHT/2)
			sprite:setAnchorPoint(0.5,0.5)

			sprite:setScale(1,1)
			--pini:AttachDisplay(newSprite)
			pini:AttachDisplay(sprite)
			sprite:release()
			
			local shader = pini.Shader(pini:GetUUID(),"transition.vsh", "transition.fsh")
			shader:bind(sprite)

			shader:setUniformTexture("u_fadetex", img1)
			shader:setUniformTexture("u_disttex", img2)

			img2:setScale(StrEnumToScale(img2,size))
			img2:setPosition(StrEnumToPos(img2,"화면중앙"))

			-- newSprite:setScale(img2.scaleX,img2.scaleY)
			-- newSprite:setPosition(img2._x,img2._y)
			sprite.scaleX = img2.scaleX
			sprite.scaleY = img2.scaleY
			sprite._x = img2._x
			sprite._y = img2._y

			pini.Timer(pini:GetUUID(),0,function(t)
				if stackId then
					vm:resume(stackId)
					stackId = nil
				end
				t.userdata.delta = t.userdata.delta + t.dt
				t.userdata.threshold = t.userdata.delta / t.userdata.max
				local shader = pini:FindShader(t.userdata.sid)
				shader:setUniformFloat("threshold",t.userdata.threshold)
				if t.userdata.threshold > 1 then
					t:stop()
					shader:fin()
					-- local toRemove = pini:FindNode(t.userdata.ssId)
					-- pini:DetachDisplay(toRemove)
				end
			end,true,nil,{sid=shader.id,threshold=0,delta=0,max=sec,ssId=sprite.id}):run()
		end)
	end
end

function LNX_REGIST_KEYBOARD(vm,stck)
	local id   = vm:ARGU("키입력","아이디","")
	local func = vm:ARGU("키입력","매크로")

	pini:scene():registKeyboard(id,loadstring([[
	return function(press,keyCode,arg,x,y)
		local f = "]]..func..[["
		_LNXG["키입력.값"] = keyCode
		_LNXG["키입력.누름"] = press
		_LNXG["키입력.x"] = x
		_LNXG["키입력.y"] = y
		pini.XVM:call(f)
	end]])())
end

function LNX_SAVEVARFLUSH(vm,stck)
	if vm.VarFlush then
		vm.VarFlush()
	end
end

function LNX_UNREGIST_KEYBOARD(vm,stck)
	local id = vm:ARGU("키입력해제","아이디","")
	pini:scene():unregistKeyboard(id)
end

function LNX_RANDOM(vm,stck)
	local min = vm:ARGU("랜덤","시작",0)
	local max  = vm:ARGU("랜덤","끝",100)

	min = tonumber(min)
	max = tonumber(max)
	if min > max then
		min,max = max,min
	end

	math.random(min,max)

	local ret = 0
	if min-max == 0 then
		ret = min
	else
		ret = math.random(min,max)
	end
	
	_LNXG["랜덤값"] = ret
	vm:returnValue(ret)
end

function LNX_VM_CHECKSAVE(vm,stck)
	local number = vm:ARGU("저장체크","번호","")
	if OnPreview then
	else
		try{
			function()
				local savename = tostring(number)
				local savepath = ROOT_PATH.."save/"..savename.."/"
				if fileUtil:isDirectoryExist(savepath) then
					_LNXG["저장체크.결과"] = 1

					local _in = io.open(savepath.."info", "rb")
					if _in then
						local info = json.decode(_in:read("*all"))
						_in:close()

						_LNXG["저장체크.제목"]   = info.name
						_LNXG["저장체크.타임"]   = info.time
						_LNXG["저장체크.데이트"] = info.date
						print (info.name,info.time,info.date)
					else
						_LNXG["저장체크.결과"] = 0
					end
				else
					_LNXG["저장체크.결과"] = 0
				end
			end,
			catch {function(error)
				_LNXG["저장체크.결과"] = 0
			end}
		}
		vm:returnValue(_LNXG["저장체크.결과"])
	end
end

function LNX_VM_LOAD(vm,stck)
	local number = vm:ARGU("불러오기","번호","")

	if OnPreview then
	else
		print("****************LNX_VM_LOAD****************")
		-- all clear!
		pini.Timer(nil,1,function()
			vm:init()
			pini:Clear()
			PiniLib(vm)
			pini.Timer(nil,0.5,function()
				------------------------------------
				-- lxvm_state file : vm state file
				-- loops file : vm looping stack file
				-- p file : pini object list file
				-- info file : info file
				-- k0~n file : keyboard event function bytecode file
				-- fns0~n file : vm lua function bytecode
				-- vtg0~n file : variable trigger function bytecode
				-- t0~n file : timer event function bytecode
				-- tu0~n file : node touch up function bytecode
				-- td0~n file : node touch down function bytecode
				-- tg0~n file : touch gesture function bytecode

				print ""
				print "(Load called clear point)"
				print ""

				local loadname = tostring(number)
				local loadpath = ROOT_PATH.."save/"..loadname.."/"
				if not fileUtil:isDirectoryExist(loadpath) then
					return
				end

				local _in = io.open(loadpath.."lxvm_state", "rb")
				local lxvm_state = json.decode(_in:read())
				_in:close()

				local _in = io.open(loadpath.."loops", "rb")
				local r = json.decode(_in:read())
				_in.close()

				lxvm_state["loops"] = r

				lxvm_state["vtg"] = {}
				local next_fns = {}

				for k,v in ipairs(lxvm_state["fns"]) do
					local _in = io.open(loadpath.."fns"..(k-1), "rb")
					local r = _in:read("*all")
					_in:close()

					next_fns[v] = r
				end

				lxvm_state["fns"] = next_fns

				for k,v in ipairs(lxvm_state["vtg"]) do
					local _in = io.open(loadpath.."vtg"..(k-1), "rb")
					local r = _in:read("*all")
					_in:close()

					lxvm_state["vtg"][v[1]] = {v[1], v[2], r}
				end

				------------------------------------------------------------
				------------------------------------------------------------
				pini.Backlog:clear()
				local _in = io.open(loadpath.."dialog", "rb")
				local r = json.decode(_in:read("*all"))
				_in:close()

				pini.Dialog.configs = r.config
				pini.Dialog:setName(r.name)
				pini.Dialog:UseConfig(r.window)
				local isRun = false
				
				for k,v in pairs(r.showingWords) do
					isRun = true
					if v[1] == 1 then
						pini.Dialog:Add(v[2])
					else
						pini.Dialog:AddMarkup(v[2])
					end
				end

				local dialogCallstack = r.callstack
				local dialogFrameStopCallstack = r.frameStopCallstack

				if isRun then
					pini.Dialog:run()
				end

				-------------------------------------------------------------
				-------------------------------------------------------------
				_in = io.open(loadpath.."p", "rb")
				ret = json.decode(_in:read())
				_in:close()

				local bgm = ret["bgm"] or nil
				local node = ret["node"] or {}
				local sound = ret["sound"] or {}
				local timer = ret["timer"] or {}
				local keyboard = ret["keyboard"] or {}
				local shaders = ret["shader"] or {}
				local gestures = ret["gestures"] or {}

				pini.SkipAllowStatus = ret["backlogEnabled"]
			    pini.Backlog:setConfig(ret["backLogConfig"] or {})

				pini:StopBGM()
				if bgm then
					pini:PlayBGM(bgm[1],bgm[2],bgm[3])
				end
				for k,v in ipairs(sound) do
					pini:PlaySound(v[3],v[2],v[4],v[5])
				end

				local loaded_node = {}
				for k,v in ipairs(node) do 
					local n = pini[v.type]:gen(v)
					table.insert(loaded_node,{n,v.parent,n.drawOrder,v.touchRegisted})
					if v.touchRegisted then
						local _in = io.open(loadpath.."tu"..(k-1), "rb")
						if _in then
							n.onTouchUp = loadstring(_in:read("*all"))
							_in:close()
						else
						end
						_in = io.open(loadpath.."td"..(k-1), "rb")
						if _in then
							n.onTouchDown = loadstring(_in:read("*all"))
							_in:close()
						end
						_in = io.open(loadpath.."tm"..(k-1), "rb")
						if _in then
							n.onTouchMiss = loadstring(_in:read("*all"))
							_in:close()
						end
					end

					local event = v.exitEvent
					v.exitEvent = {}
					for h,v in ipairs(event) do 
						if v["3"] == true then
							_in = io.open(loadpath.."exit"..(k-1).."."..(h-1), "rb")
							if _in then
								n:registOnExit(v["1"],loadstring(_in:read("*all")))
								_in:close()
							end
						end
					end
				end

				table.sort(loaded_node,function(a,b) return a[3]<b[3] end)
				
				for k,v in ipairs(loaded_node) do 
					local n = v[1]
					local parent = v[2]
					if parent.type == "Scene" then
						pini:AttachDisplay(n)
					else
						pini:AttachDisplay(n,parent.id)
					end
					if v[4] then
						pini.TouchManager:registNode(n)
					end
				end

				for k,v in ipairs(timer) do 
					local _in = io.open(loadpath.."t"..(k-1), "rb")
					local r = _in:read("*all")
					_in:close()
					local func = loadstring(r)
					local t = pini.Timer(v.id,v.time,func,v.loop,v.count,v.userdata)
					if v.playing then
						t:run()
					end
				end

				for k,v in ipairs(keyboard) do 
					local _in = io.open(loadpath.."k"..(k-1), "rb")
					local r = _in:read("*all")
					_in:close()

					pini:scene():registKeyboard(v["id"],loadstring(r),v["arg"],v["stop"])
				end

				for k,v in ipairs(gestures) do
					local _in = io.open(loadpath.."tg"..(k-1), "rb")
					local r = _in:read("*all")
					_in:close()

					pini:scene():registTouchGesture(v["id"],loadstring(r),v["stop"])
				end

				for k,v in ipairs(shaders) do
					print(v.id,v.vsh,v.fsh)
					local shader = pini.Shader(v.id,v.vsh,v.fsh)
					if v.bind then
						shader:bind(pini:FindNode(v.bind))
					end
					for n,u in pairs(v.uniform)do
						shader:setUniformFloat(n,u)
					end
				end
				-------------------------------------------------------------
				-------------------------------------------------------------

				dialogCallstack, dialogFrameStopCallstack = vm:setState(lxvm_state, dialogCallstack, dialogFrameStopCallstack)
				pini.Dialog.callstack = dialogCallstack
				pini.Dialog.frameStopCallstack = dialogFrameStopCallstack

				pini:clearNodePool()

			end,false):run()
		end,false):run()

		vm:stop()
	end
end

function LNX_SAVE(vm,stck)
	local number = vm:ARGU("저장","번호","")
	local name = vm:ARGU("저장","저장제목","")

	if OnPreview then
	else
		if not fileUtil:isDirectoryExist(ROOT_PATH.."save") then
			fileUtil:createDirectory(ROOT_PATH.."save")
		end

		local savename = tostring(number)
		local savepath = ROOT_PATH.."save/"..savename.."/"
		if not fileUtil:isDirectoryExist(savepath) then
			fileUtil:createDirectory(savepath)
		end

		pini:takeScreenShot(function(sprite)

			local state
			local stckTransTable
			state, stckTransTable = vm:getState()
			print (state["loops"])

			local info = {}
			info["name"] = name
			info["date"] = os.date("%Y-%m-%d %X",os.time())
			info["time"] = os.time()

			local lxvm_states = {}
			local out = io.open(savepath.."loops", "wb")
			out:write(json.encode(state["loops"]))
			out:close()

			lxvm_states["vg"] = state["vg"]
			lxvm_states["bm"] = state["bm"]

			local i=0
			lxvm_states["fns"] = {}
			for k,v in pairs(state["fns"]) do
				table.insert(lxvm_states["fns"], k)

				local out = io.open(savepath.."fns"..i, "wb")
				out:write(v)
				out:close()
				i = i+1
			end

			local i=0
			lxvm_states["vtg"] = {}
			for k,v in pairs(state["vtg"]) do
				table.insert(lxvm_states["vtg"], {v[1], v[2]})

				local out = io.open(savepath.."vtg"..i, "wb")
				out:write(v[3])
				out:close()
				i = i+1
			end

			local out = io.open(savepath.."lxvm_state", "wb")
			out:write(json.encode(lxvm_states))
			out:close()

			out = io.open(savepath.."info", "wb")
			out:write(json.encode(info))
			out:close()

			local dialog = {}
			dialog["name"] = pini.Dialog.name
			dialog["keep"] = pini.Dialog.keepFlag
			dialog["window"] = pini.Dialog.configIdx
			dialog["config"] = pini.Dialog.configs
			dialog["showingWords"] = pini.Dialog.showingWords
			if pini.Dialog.showingDelFlag then
				dialog["showingWords"] = {}
			end
			dialog["callstack"] = stckTransTable[pini.Dialog.callstack]
			dialog["frameStopCallstack"] = stckTransTable[pini.Dialog.frameStopCallstack]

			out = io.open(savepath.."dialog", "wb")
			out:write(json.encode(dialog))
			out:close()
			-----------------------------------------------
			-----------------------------------------------
			local scene = pini:scene()
			local keyboards = scene.keyboards
			scene.keyboards = {}
			local gestures = scene.touchGestures
			scene.touchGestures = {}

			i=0
			local pin = {}
			pin["node"] = {}
			for k,v in pairs(pini._regist_.Display) do
				if v.id:startsWith("PINI") or (v.parent and v.parent.type ~= "Scene" and v.parent.id:startsWith("PINI")) then
				else 
					table.insert(pin["node"],v)
					if v.touchRegisted then
						if v.onTouchUp then
							local out = io.open(savepath.."tu"..i, "wb")
							out:write(string.dump(v.onTouchUp))
							out:close()
						end
						if v.onTouchDown then
							local out = io.open(savepath.."td"..i, "wb")
							out:write(string.dump(v.onTouchDown))
							out:close()
						end
						if v.onTouchMiss then
							local out = io.open(savepath.."tm"..i, "wb")
							out:write(string.dump(v.onTouchMiss))
							out:close()
						end
					end
					local h=0
					for k,v in ipairs(v.exitEvent) do 
						if v[1]:startsWith("PINI") == false then
							local out = io.open(savepath.."exit"..i.."."..h, "wb")
							out:write(string.dump(v[2]))
							out:close()

							v[3] = true
							h = h+1
						else
							v[3] = false
						end
					end
					i=i+1
				end
			end

			i=0
			pin["shader"]={}
			for k,v in pairs(pini._regist_.Shaders) do
				if v.isDestroyed == false then
					local data = {
						vsh = v.vsh,
						fsh = v.fsh,
						id = v.id,
						uniform = v.uniform
					}
					if v.bindNode and v.bindNode.isDestroyed == false then
						data["bind"] = v.bindNode.id
					end
					table.insert(pin["shader"],data)
				end
			end

			i=0
			pin["timer"]={}
			for k,v in pairs(pini._regist_.Timers) do
				if v.id:startsWith("PINI") == false then
					table.insert(pin["timer"],{
						id=v.id , 
						time=v.time , 
						loop=v.rep, 
						playing=v.playing, 
						count=v.count, 
						userdata=v.userdata
					})

					local out = io.open(savepath.."t"..i, "wb")
					out:write(string.dump(v.func))
					out:close()
					i = i+1
				end
			end

			i=0
			pin["keyboard"]={}
			for k,v in pairs(keyboards) do
				if k:startsWith("PINI") then
				else
					table.insert(pin["keyboard"],{id=k,arg=v["arg"],stop=v["stop"]})

					local out = io.open(savepath.."k"..i, "wb")
					out:write(string.dump(v["func"]))
					out:close()
					i = i+1
				end
			end

			i=0
			pin["gestures"]={}
			for k,v in pairs(gestures) do
				table.insert(pin["gestures"],{id=k,stop=v["stop"]})

				local out = io.open(savepath.."tg"..i, "wb")
				out:write(string.dump(v["func"]))
				out:close()
				i = i+1
			end

			pin["sound"] = {}
			for k,v in pairs(pini._regist_.Sounds) do
				local soundState = ccexp.AudioEngine:getState(v[1])
				if soundState ~= -1 then
					table.insert(pin["sound"],v)
				end
			end
			pin["bgm"] = pini._regist_.BGM

			pin["backlogEnabled"] = pini.SkipAllowStatus
			pin["backLogConfig"] = pini.Backlog:config()

			out = io.open(savepath.."p", "wb")
			out:write(json.encode(pin))
			out:close()

			scene.keyboards = keyboards
			scene.touchGestures = gestures
		end,"save/"..savename.."/screenshot.png")
	end
end

function LNX_SAVE_DELETE(vm,stck)
	local number = vm:ARGU("저장삭제","번호","")

	if OnPreview then
	else
		if not fileUtil:isDirectoryExist(ROOT_PATH.."save") then
			fileUtil:createDirectory(ROOT_PATH.."save")
		end

		local savename = tostring(number)
		local savepath = ROOT_PATH.."save/"..savename.."/"
		if fileUtil:isDirectoryExist(savepath) then
			fileUtil:removeDirectory(savepath)
		end
	end

end

function LNX_DATEINFO(vm,stck)
	local _type = vm:ARGU("시간정보","타입","")

	local ret = 0
	if _type == "현재초" then
		ret = os.time()
	elseif _type == "년월일" then
		ret = os.date("%Y-%m-%d",os.time())
	elseif _type == "년월일시분초" then
		ret = os.date("%Y-%m-%d %X",os.time())
	end

	vm:returnValue(ret)
end

-- function LNX_RUN_SCRIPT(vm,stck)
-- 	local fname = vm:ARGU("스크립트","파일명","")
-- 	local run = vm:ARGU("스크립트","실행","예") == "예"

-- 	LXVM:OpenLNX(fname)
-- 	if run then
-- 		_VM_LOOP_(fname,_LNXF[fname],stck,nil,nil)
-- 	end
-- end

function LNX_SCREENSHOT(vm,stck)
	local filename = vm:ARGU("스크린샷","파일명","")
	pini:takeScreenShot(function(sprite)
		vm:returnValue(filename)
	end,filename)
end

function LNX_FULLSCREENSWITCH(vm,stck)
	local isFullScreen = vm:ARGU("전체화면전환","전체화면","")

	isFullScreen = isFullScreen == "예"

	if OnPreview then
	else
		vm:SettingSave("fullscreen",isFullScreen)
	end
end

function LNX_SKIP_DIALOG(vm,stck)
	-- 대사넘김

	dialogTouch = pini:FindNode("PINI_Dialog_touch")
	if dialogTouch then
		dialogTouch.onTouchUp(nil,dialogTouch)
	end
	clickTouch = pini:FindNode("ClickWait")
	if clickTouch then
		clickTouch.onTouchUp(nil,clickTouch)
	end
end

function LNX_SWITCH_SKIP_ALLOW(vm,stck)
	local isAllow = vm:ARGU("빨리감기","허용","예")

	isAllow = isAllow == "예"

	pini.SkipAllowStatus = isAllow

	if not isAllow then
		pini:StopTimer("PINI_CtrlSkip")
	end
end

function LNX_START_FASTSKIP(vm,stck)
	-- 빨리감기시작

	pini.Timer("PINI_FastSkip",0,function(t)
		t.userdata.dt = t.userdata.dt+t.dt
		if t.userdata.dt > 0.075 then
			local dialogTouch = pini:FindNode("PINI_Dialog_touch")
			if dialogTouch then
				dialogTouch.onTouchUp(nil,dialogTouch)
			end
			local clickTouch = pini:FindNode("ClickWait")
			if clickTouch then
				clickTouch.onTouchUp(nil,clickTouch)
			end
			--if clickTouch== nil and dialogTouch == nil then
				t.userdata.dt = 0
			--end
		end
	end,true,nil,{dt=0}):run()
end

function LNX_STOP_FASTSKIP(vm,stck)
	-- 빨리감기중단

	pini:StopTimer("PINI_FastSkip")
end

function LNX_BACKLOG(vm,stck)
	local xPos          = vm:ARGU("백로그","x","200")
	local yPos          = vm:ARGU("백로그","y","600")
	local contentWidth  = vm:ARGU("백로그","너비","400")

	xPos = tonumber(xPos) or 200
	yPos = tonumber(yPos) or 600
	contentWidth = tonumber(contentWidth) or 400

	pini.Backlog:show(xPos, yPos, contentWidth)
end

function LNX_BACKLOG_SETTING(vm,stck)
	local lineMargin    = vm:ARGU("백로그설정","줄간격")
	local fontSize      = vm:ARGU("백로그설정","폰트크기")
	local fontFace      = vm:ARGU("백로그설정","폰트")
	local fontColor     = vm:ARGU("백로그설정","폰트색상")
	local logLimit      = vm:ARGU("백로그설정","로그갯수")
	local namePos       = vm:ARGU("백로그설정","이름위치")

	local configs = pini.Backlog:config() or {}

	if lineMargin then
		configs["lineMargin"] = tonumber(lineMargin) or configs["lineMargin"]
	end
	if fontSize then
		configs["fontSize"] = tonumber(fontSize) or configs["fontSize"]
	end
	if fontFace then
		configs["fontName"] = tostring(fontFace) or configs["fontName"]
	end
	if fontColor then
		local s = fontColor:explode(",")
		configs["fontColor"] = {
			tonumber(s[1] or configs["fontColor"][1]),
			tonumber(s[2] or configs["fontColor"][2]),
			tonumber(s[3] or configs["fontColor"][3])
		}
	end
	if logLimit then
		configs["logLimit"] = tonumber(logLimit) or configs["logLimit"]
	end
	if namePos then
		configs["namePos"] = tonumber(namePos) or configs["namePos"]
	end

	pini.Backlog:setConfig(configs)
end

function LNX_BACKLOG_HIDE(vm,stck)
	-- 백로그숨김

	pini.Backlog:hide()
end

function LNX_BACKLOG_CLEAR(vm,stck)
	-- 백로그초기화, 지금까지 누적해온 

	pini.Backlog:clear()
end

function LNX_START_AUTOREAD(vm,stck)
	-- 자동읽기시작
	local sec = vm:ARGU("자동읽기시작","대기시간",1.0)

	sec = tonumber(sec) or 1.0

	if sec < 0.1 then
		sec = 0.1
	end

	pini.AutoreadSpeed = sec

	clickWaitNode = pini:FindNode("ClickWait")
	if clickWaitNode then
		clickWaitNode.onTouchUp(nil, clickWaitNode)
	end

	pini.Dialog:WaitConfig(true,sec)
	dialogTouch = pini:FindNode("PINI_Dialog_touch")
	if dialogTouch then
		dialogTouch.onTouchUp(nil,dialogTouch)
		dialogTimer = pini:FindTimer("PINI_Dialog_Update")

		if dialogTimer then
			dialogTimer.userdata.waitsec = sec
		end
	end
end

function LNX_STOP_AUTOREAD(vm,stck)
	-- 자동읽기중단

	pini:StopTimer("PINI_ClickWait_Update")

	pini.Dialog:WaitConfig(true,0)
	dialogTouch = pini:FindNode("PINI_Dialog_touch")
	if dialogTouch then
		dialogTimer = pini:FindTimer("PINI_Dialog_Update")

		if dialogTimer then
			dialogTimer.userdata.waitsec = 0
		end
	end

	pini.AutoreadSpeed = nil
end

function LNX_HIDE_DIALOG(vm,stck)
	-- 대사창끄기

	if pini.Dialog.background then
		pini.Dialog.background:setVisible(false)
	end
	if pini.Dialog.nameWindow then
		pini.Dialog.nameWindow:setVisible(false)
	end
end

function LNX_SHOW_DIALOG(vm,stck)
	-- 대사창켜기
	if pini.Dialog.background then
		pini.Dialog.background:setVisible(true)
	end
	if pini.Dialog.nameWindow then
		pini.Dialog.nameWindow:setVisible(true)
	end
end

function LNX_DIALOG_CONFIG(vm,stck)
	local id 		  = vm:ARGU("대사창수정","아이디") 

	local margin	  = vm:ARGU("대사창수정","여백")
	local size 		  = vm:ARGU("대사창수정","영역") 
	local pos 		  = vm:ARGU("대사창수정","위치") 
	local lineGap     = vm:ARGU("대사창수정","행간")
	local effect      = vm:ARGU("대사창수정","효과")
	local effectSec   = vm:ARGU("대사창수정","효과시간")
	local appearAnimation    = vm:ARGU("대사창수정","나타남애니메이션")
	local disappearAnimation = vm:ARGU("대사창수정","사라짐애니메이션")
	local color 	  = vm:ARGU("대사창수정","색상") 
	local image 	  = vm:ARGU("대사창수정","이미지")
	local fnt 		  = vm:ARGU("대사창수정","폰트") 
	local fntcolor	= vm:ARGU("대사창수정","폰트색상")
	local fntsize	 = vm:ARGU("대사창수정","폰트크기")
	local sound	   = vm:ARGU("대사창수정","효과음")
	local textOutline = vm:ARGU("대사창수정","폰트외곽선") --"r,g,b,a,w"
	local textShadow  = vm:ARGU("대사창수정","폰트그림자") --"r,g,b,a,x,y,w"
	local textGlow    = vm:ARGU("대사창수정","폰트글로우") -- "r,g,b,a"

	local keyName = vm:ARGU("대사창수정","키입력")
	
	local cursorImg   = vm:ARGU("대사창수정","커서이미지")
	local cursorSize  = vm:ARGU("대사창수정","커서크기")
	local cursorColor = vm:ARGU("대사창수정","커서색상")
	local cursorAnim  = vm:ARGU("대사창수정","커서애니메이션")

	local namepos 		= vm:ARGU("대사창수정","이름창위치")
	local namesize 		= vm:ARGU("대사창수정","이름창영역")
	local namecolor 	= vm:ARGU("대사창수정","이름창색상")
	local nameimage 	= vm:ARGU("대사창수정","이름창이미지")
	local namefntsize 	= vm:ARGU("대사창수정","이름창폰트크기")
	local namefntcolor 	= vm:ARGU("대사창수정","이름창폰트색상")
	local namefnt 		= vm:ARGU("대사창수정","이름창폰트")
	local nameOutline = vm:ARGU("대사창수정","이름창폰트외곽선") --"r,g,b,a,w"
	local nameShadow  = vm:ARGU("대사창수정","이름창폰트그림자") --"r,g,b,a,x,y,w"
	local nameGlow    = vm:ARGU("대사창수정","이름창폰트글로우") -- "r,g,b,a"

	local linkImg 		= vm:ARGU("대사창수정","연결이미지")
	local linkColor		= vm:ARGU("대사창수정","연결색상")
	local linkWidthFit	= vm:ARGU("대사창수정","연결넓이맞춤")
	local linkSelectImg = vm:ARGU("대사창수정","연결선택시이미지")
	local linkSound     = vm:ARGU("대사창수정","연결선택효과음")

	local textRate	  = vm:ARGU("대사창수정","시간")
	local textAnimation = vm:ARGU("대사창수정","애니메이션")

	if id then
		local config = pini.Dialog:config(id) or {
													x=10,
													y=WIN_HEIGHT-10,
													width=WIN_WIDTH-20,
													height=250,
													background_color={60,60,60,122},
													text_color={255,255,255,255},
													text_rate = 0.08,
													text_outline = nil,
													text_outglow = nil,
													text_shadow  = nil,
													text_anim="",
													effect="",
													effectSec=0.25,
													appearAnim = "",
													disappearAnim = "",
													lineGap=0,
													keyName=59,
													cursor={
														width=20,
														height=10,
														color={255,255,255,255},
														sprite=nil,
														anim=""
													},
													name={
														x=10,
														y=WIN_HEIGHT-270,
														background_color={60,60,60,122},
														text_color={255,255,255,255},
														text_size=30,
														text_align="화면중앙",
														text_outline = nil,
														text_outglow = nil,
														text_shadow  = nil,
													}
												  }
		if pos then
			local s = pos:explode(",")
			config["x"] = tonumber(s[1] or config["x"])
			config["y"] = tonumber(s[2] or config["y"])
		end
		if size then
			local s = size:explode(",")
			config["width"] = tonumber(s[1] or config["width"])
			config["height"]= tonumber(s[2] or config["height"])
		end
		if sound then
			config["sound"] = sound or ""
		end
		if keyName then
			config["keyName"] = tonumber(keyName) or 59
		end
		if lineGap then
			config["lineGap"] = tonumber(lineGap) or 0
		end
		if effect then
			config["effect"] = tostring(effect) or ""
		end
		if effectSec then
			config["effectSec"] = tonumber(effectSec) or 0.25
		end
		if appearAnimation then
			config["appearAnim"] = tostring(appearAnimation) or ""
		end
		if disappearAnimation then
			config["disappearAnim"] = tostring(disappearAnimation) or ""
		end
		if color then
			local s = color:explode(",")
			config["background_color"] = {
				tonumber(s[1] or config["background_color"][1]),
				tonumber(s[2] or config["background_color"][2]),
				tonumber(s[3] or config["background_color"][3]),
				tonumber(s[4] or config["background_color"][4])
			}
		end
		if fntcolor then
			local s = fntcolor:explode(",")
			config["text_color"] = {
				tonumber(s[1] or config["text_color"][1]),
				tonumber(s[2] or config["text_color"][2]),
				tonumber(s[3] or config["text_color"][3]),
				tonumber(s[4] or config["text_color"][4])
			}
		end
		if textRate then
			if tonumber(textRate) then
				config["text_rate"] = tonumber(textRate)
			end
		end
		if textAnimation then
			config["text_anim"] = textAnimation
		end
		if margin then
			local s = margin:explode(",")
			config["marginX"] = tonumber(s[1] or config["marginX"])
			config["marginY"] = tonumber(s[2] or config["marginY"])
		end
		config["font"] = fnt or config["font"]
		config["path"] = image or config["path"]
		config["size"] = tonumber(fntsize or config["size"])

		if textOutline then
			local s = textOutline:explode(",")
			config["text_outline"] = {
				tonumber(s[1] or 0),
				tonumber(s[2] or 0),
				tonumber(s[3] or 0),
				tonumber(s[4] or 0),
				tonumber(s[5] or 0),
			}
		end

		if textGlow then
			local s = textGlow:explode(",")
			config["text_outglow"] = {
				tonumber(s[1] or 0),
				tonumber(s[2] or 0),
				tonumber(s[3] or 0),
				tonumber(s[4] or 0),
			}
		end

		if textShadow then
			local s = textShadow:explode(",")
			config["text_shadow"] = {
				tonumber(s[1] or 0),
				tonumber(s[2] or 0),
				tonumber(s[3] or 0),
				tonumber(s[4] or 0),
				tonumber(s[5] or 0),
				tonumber(s[6] or 0),
			}
		end

		--------------------------------------------
		-- name window!
		--------------------------------------------
		config["name"] = config["name"] or {}
		local nconfig = config["name"]
		if namepos then
			local s = namepos:explode(",")
			nconfig["x"] = tonumber(s[1] or nconfig["x"])
			nconfig["y"] = tonumber(s[2] or nconfig["y"])
		end
		if namesize then
			local s = namesize:explode(",")
			nconfig["width"] = tonumber(s[1] or nconfig["width"])
			nconfig["height"]= tonumber(s[2] or nconfig["height"])
		end
		if namecolor then
			local s = namecolor:explode(",")
			nconfig["background_color"] = {
				tonumber(s[1] or nconfig["background_color"][1]),
				tonumber(s[2] or nconfig["background_color"][2]),
				tonumber(s[3] or nconfig["background_color"][3]),
				tonumber(s[4] or nconfig["background_color"][4])
			}
		end
		if namefntcolor then
			local s = namefntcolor:explode(",")
			nconfig["text_color"] = {
				tonumber(s[1] or nconfig["text_color"][1]),
				tonumber(s[2] or nconfig["text_color"][2]),
				tonumber(s[3] or nconfig["text_color"][3]),
				tonumber(s[4] or nconfig["text_color"][4])
			}
		end
		if nameOutline then
			local s = nameOutline:explode(",")
			nconfig["text_outline"] = {
				tonumber(s[1] or 0),
				tonumber(s[2] or 0),
				tonumber(s[3] or 0),
				tonumber(s[4] or 0),
				tonumber(s[5] or 0),
			}
		end

		if nameGlow then
			local s = nameGlow:explode(",")
			nconfig["text_outglow"] = {
				tonumber(s[1] or 0),
				tonumber(s[2] or 0),
				tonumber(s[3] or 0),
				tonumber(s[4] or 0),
			}
		end

		if nameShadow then
			local s = nameShadow:explode(",")
			nconfig["text_shadow"] = {
				tonumber(s[1] or 0),
				tonumber(s[2] or 0),
				tonumber(s[3] or 0),
				tonumber(s[4] or 0),
				tonumber(s[5] or 0),
				tonumber(s[6] or 0),
			}
		end

		nconfig["font"] = namefnt or nconfig["font"]
		nconfig["path"] = nameimage or nconfig["path"]
		nconfig["text_size"] = tonumber(namefntsize or nconfig["text_size"])

		--------------------------------------------
		--link block
		--------------------------------------------
		config["linkBlock"] = config["linkBlock"] or {}
		bconfig = config["linkBlock"]
		if linkColor then
			local s = linkColor:explode(",")
			bconfig["color"] = {
				tonumber(s[1] or bconfig["color"][1]),
				tonumber(s[2] or bconfig["color"][2]),
				tonumber(s[3] or bconfig["color"][3]),
				tonumber(s[4] or bconfig["color"][4])
			}
		end
		if linkWidthFit then
			bconfig["fitWidth"] = linkWidthFit == "예" 
		end
		bconfig["select"] = linkSelectImg or bconfig["select"]
		bconfig["unselect"] = linkImg or bconfig["unselect"]
		bconfig["linkSound"] = linkSound or bconfig["linkSound"]

		--------------------------------------------
		--cursor
		--------------------------------------------
		config["cursor"] = config["cursor"] or {}
		cconfig = config["cursor"]
		
		cconfig["sprite"] = cursorImg or cconfig["sprite"]
		cconfig["anim"] = cursorAnim or cconfig["anim"]

		if cursorColor then
			local s = cursorColor:explode(",")
			cconfig["color"] = {
				tonumber(s[1] or cconfig["color"][1]),
				tonumber(s[2] or cconfig["color"][2]),
				tonumber(s[3] or cconfig["color"][3]),
				tonumber(s[4] or cconfig["color"][4])
			}
		end
		if cursorSize then
			local s = cursorSize:explode(",")
			cconfig["width"] = tonumber(s[1] or cconfig["width"])
			cconfig["height"]= tonumber(s[2] or cconfig["height"])
		end
		
		pini.Dialog:SetConfig(id,config);
	end
end

PiniLib = function()
	pini.XVM = LXVM

	-- if OnPreview then
	-- 	LanXVM.unuse_goto = true;
	-- end
	pini.Dialog:SetConfig("독백",{
		x=10,
		y=WIN_HEIGHT-10,
		width=WIN_WIDTH-20,
		height=WIN_HEIGHT-20,
		background_color={60,60,60,122},
		text_color={255,255,255,255},
		text_outline = nil,
		text_outglow = nil,
		text_shadow  = nil,
		text_rate=0.02,
		effect="",
		effectSec=0.25,
		appearAnim="",
		disappearAnim="",
		lineGap=0,
		keyName=59,
		cursor={
			width=20,
			height=10,
			color={255,255,255,255},
			sprite=nil,
			anim=""
		}
		--[[,
		linkBlock={
			color={255,255,255,255},
			select="select.png",
			unselect="unselect.png",
			fitWidth=true,
			anim=pini.Anim.Sequence(pini.Anim.FadeTo(0.5,100),pini.Anim.FadeTo(0.5,255))
		}]]
	})
	pini.Dialog:SetConfig("대화",{
		x=10,
		y=WIN_HEIGHT-10,
		width=WIN_WIDTH-20,
		height=250,
		background_color={60,60,60,122},
		text_color={255,255,255,255},
		text_outline = nil,
		text_outglow = nil,
		text_shadow  = nil,
--		path="textArea.png",
		text_rate=0.02,
		effect="",
		effectSec=0.25,
		appearAnim="",
		disappearAnim="",
		lineGap=0,
		text_anim="",
		keyName=59,
		cursor={
			width=20,
			height=10,
			color={255,255,255,255},
			sprite=nil,
			anim=""
		},
		name={
			x=10,
			y=WIN_HEIGHT-270,
			background_color={60,60,60,122},
			text_color={255,255,255,255},
			text_size=30,
			text_align="화면중앙",
			text_outline = nil,
			text_outglow = nil,
			text_shadow  = nil,
		}--[[,
		linkBlock={
			color={255,255,255,60},
			select="select.png",
			unselect="unselect.png",
			fitWidth=false,
			anim=pini.Anim.Sequence(pini.Anim.FadeTo(0.5,100),pini.Anim.FadeTo(0.5,255))
		}]]
	})
	pini.Dialog:UseConfig("대화")
	--LNX_SCENE_TRANSITION(LanXVM)
	pini.Scene()
end
return PiniLib
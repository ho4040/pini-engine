require("utils")
local Simulate = {}
function Simulate:init(luavm,w,h)
	self.images = {}
	self.dialog = nil
	self.monolog = nil
	
    local winSize = {width=w,height=h}
    local fs_position={}
	fs_position["왼쪽상단"]=function(i) return 0 end
	fs_position["오른쪽상단"]=function(i) return 1 end
	fs_position["화면중앙"]=function(i) return 2 end
	fs_position["왼쪽하단"]=function(i) return 3 end
	fs_position["오른쪽하단"]=function(i) return 4 end

    local fs_size={}
	fs_size["원본크기"]=function(i) return 0 end
	fs_size["두배"]   =function(i) return 1 end
	fs_size["화면맞춤"]=function(i) return 2 end
	
	function imageRemove(key)
		for k,v in ipairs(self.images) do
			if v["id"] == key then
				table.remove(self.images,k)
				return 
			end
		end
	end

	luavm:registFunc("이미지",function(vm,arg)
		self.dialog = nil

		local id = vm.variable["이미지.아이디"] or ""
		local path = vm.variable["이미지.파일명"] or ""
		local pos = vm.variable["이미지.위치"] or "0,0"
		local effect = vm.variable["이미지.효과"] or ""
		local effectSec = vm.variable["이미지.효과시간"] or 0
		local size = vm.variable["이미지.크기"] or "0,0"

		if path:len() > 0 then
			if fs_position[pos] then
				pos = fs_position[pos]()
			else
				pos = pos:explode(",")
			end

			if fs_size[size] then
				size = fs_size[size]()
			else
				size = size:explode(",")
			end
			
			imageRemove(id)
			table.insert(self.images,{
				id=id,
				path=path,
				pos=pos,
				size=size
			})
		end
		vm:doNext()
	end)

	luavm:registFunc("이미지삭제",function(vm,arg)
		self.dialog = nil
		self.monolog = nil
		local id = vm.variable["이미지삭제.아이디"] or ""
		if id:len() > 0 then
			imageRemove(id)
		end
		vm:doNext()
	end)

	luavm:registFunc("대화",function(vm,arg)
		self.monolog = nil
		self.dialog = arg
		self.dialog["player"] = vm.variable["대화.이름"] or ""
		vm:doNext()
	end)

	luavm:registFunc("독백",function(vm,arg)
		self.dialog = nil
		self.monolog = arg
		vm:doNext()
	end)

	luavm:registFunc("화면전환",function(vm,arg)
		self.dialog = nil
		self.monolog = nil
		vm:doNext()
	end)
	
	luavm:registFunc("북마크",function(vm,arg)
		self.dialog = nil
		self.monolog = nil
		vm:doNext()
	end)

	luavm:registFunc("이동",function(vm,arg)
		self.dialog = nil
		self.monolog = nil
		vm:doNext()
	end)

	luavm:pushCmd("t_function",{targ = {},name = "화면전환"})
	luavm.unuse_goto = true
end

return Simulate
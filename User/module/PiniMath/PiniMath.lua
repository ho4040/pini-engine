--최초 1회만 불리는 코드는 여기다 적어주세요.

function LNX_MATH_RAD(vm,stck)
	local value = vm:ARGU("라디안","수",0)
	vm:returnValue(math.rad(value))
end

function LNX_MATH_DEG(vm,stck)
	local value = vm:ARGU("각도","수",0)
	vm:returnValue(math.deg(value))
end

function LNX_MATH_SIN(vm,stck)
	local value = vm:ARGU("사인","수",0)
	value = math.rad(value)
	vm:returnValue(math.sin(value))
end

function LNX_MATH_COS(vm,stck)
	local value = vm:ARGU("코사인","수",0)
	value = math.rad(value)
	vm:returnValue(math.cos(value))
end

function LNX_MATH_ASIN(vm,stck)
	local value = vm:ARGU("아크사인","수",0)
	vm:returnValue(math.deg(math.asin(value)))
end

function LNX_MATH_ACOS(vm,stck)
	local value = vm:ARGU("아크코사인","수",0)
	vm:returnValue(math.deg(math.acos(value)))
end

function LNX_MATH_TAN(vm,stck)
	local value = vm:ARGU("탄젠트","수",0)
	value = math.rad(value)
	vm:returnValue(math.tan(value))
end

function LNX_MATH_ATAN(vm,stck)
	local value1 = vm:ARGU("아크탄젠트","수1",0)
	local value2 = vm:ARGU("아크탄젠트","수2",nil)

	if value2 then
		vm:returnValue(math.deg(math.atan2(value1,value2)))
	else
		vm:returnValue(math.deg(math.atan(value1)))
	end
end

function LNX_MATH_ABS(vm,stck)
	local value = vm:ARGU("절대값","수",0)
	vm:returnValue(math.abs(value))
end

function LNX_MATH_LOG(vm,stck)
	local value = vm:ARGU("자연로그","수",0)
	vm:returnValue(math.log(value))
end

function LNX_MATH_LOG10(vm,stck)
	local value = vm:ARGU("상용로그","수",0)
	vm:returnValue(math.log10(value))
end

function LNX_MATH_EXP(vm,stck)
	local value = vm:ARGU("초월함수","수",0)
	vm:returnValue(math.exp(value))
end

function LNX_MATH_POW(vm,stck)
	local base = vm:ARGU("제곱승","밑",0)
	local power = vm:ARGU("제곱승","승수",0)
	vm:returnValue(math.pow(base,power))
end

function LNX_MATH_MAX(vm,stck)
	local value1 = vm:ARGU("최대값","수1",0)
	local value2 = vm:ARGU("최대값","수2",0)

	vm:returnValue(math.max(value1,value2))
end

function LNX_MATH_MIN(vm,stck)
	local value1 = vm:ARGU("최소값","수1",0)
	local value2 = vm:ARGU("최소값","수2",0)

	vm:returnValue(math.min(value1,value2))
end

function LNX_MATH_SQRT(vm,stck)
	local value = vm:ARGU("제곱근","수",0)

	vm:returnValue(math.sqrt(value))
end

function LNX_MATH_PI(vm,stck)
	-- [원주율] 매크로는 인자가 없습니다.

	vm:returnValue(math.pi)
end

function LNX_MATH_E(vm,stck)
	-- [자연상수] 매크로는 인자가 없습니다.

	vm:returnValue(math.exp(1))
end

local function m(XVM)
	-- 함수 정의용 루아 파일이므로,
	-- 아무 것도 하지 않습니다.
end
return m

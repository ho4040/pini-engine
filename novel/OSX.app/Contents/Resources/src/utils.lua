local explode = function (p,d)
	local t, ll = {},0
	if(#p == 1) then return {p} end
	while true do
		l=string.find(p,d,ll,true)
		if l~=nil then
			table.insert(t, string.sub(p,ll,l-1))
			ll=l+1
		else
			table.insert(t, string.sub(p,ll))
			break
		end
	end
	return t
end
local implode = function (list , delimiter)
	local len = #list
	if len == 0 then
		return ""
	end
	local string = list[1]
	for i = 2, len do
		string = string .. delimiter .. list[i]
	end
	return string
end
local startsWith = function(self, piece)
  return string.sub(self, 1, string.len(piece)) == piece
end
 
rawset(_G.string, "startsWith", startsWith)
rawset(_G.string, "explode", explode)
rawset(_G.table, "implode", implode)
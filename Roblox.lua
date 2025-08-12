local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local DataStoreService = game:GetService("DataStoreService")
local BanStore = DataStoreService:GetDataStore("PlayerBans")

Players.PlayerAdded:Connect(function(player)
	local userId = player.UserId
	local banData
	local success, err = pcall(function()
		banData = BanStore:GetAsync(tostring(userId))
	end)

	if success and banData then
		local banTime = banData.timestamp
		local duration = banData.duration
		local reason = banData.reason
		local now = os.time()

		if now < banTime + (duration * 86400) then
			player:Kick("You have been banned: " .. reason)
		else
			BanStore:RemoveAsync(tostring(userId))
		end
	elseif not success then
		warn("[BanSystem] Error while checking ban:", err)
	end
end)

function fetchCommands()
	local success, response = pcall(function()
		return HttpService:GetAsync("url/get_commands")
	end)

	if success then
		local commands = HttpService:JSONDecode(response)

		for _, cmd in ipairs(commands) do
			local command = cmd.command
			local userId = tonumber(cmd.userid)

			if command == "ban" and userId then
				local reason = cmd.reason or "No reason provided"
				local days = tonumber(cmd.day) or 7

				local success, err = pcall(function()
					BanStore:SetAsync(tostring(userId), {
						timestamp = os.time(),
						duration = days,
						reason = reason
					})
				end)

				if success then
					local plr = Players:GetPlayerByUserId(userId)
					if plr then
						plr:Kick("You have been banned: " .. reason)
					end
					print("[BanSystem] Banned UserId:", userId)
				else
					warn("[BanSystem] Error while banning:", err)
				end

			elseif command == "unban" and userId then
				local success, err = pcall(function()
					BanStore:RemoveAsync(tostring(userId))
				end)

				if success then
					print("[BanSystem] Unbanned UserId:", userId)
				else
					warn("[BanSystem] Error while unbanning:", err)
				end

			elseif command == "kick" and userId then
				local plr = Players:GetPlayerByUserId(userId)
				if plr then
					plr:Kick("You have been kicked: " .. (cmd.reason or "No reason provided"))
					print("[BanSystem] Kicked UserId:", userId)
				else
					print("[BanSystem] Player not online:", userId)
				end

			elseif command == "announce" and cmd.message then
				local announceEvent = ReplicatedStorage:FindFirstChild("AnnouncementEvent")
				if announceEvent then
					announceEvent:FireAllClients(cmd.message)
				end

			elseif command == "check" then
			end
		end

		pcall(function()
			HttpService:PostAsync("url/clear_commands", "")
		end)
	else
		warn("[BanSystem] Failed to fetch commands:", response)
	end
end

function updatePlayerCount()
	local count = #Players:GetPlayers()
	local json = HttpService:JSONEncode({ count = count })
	pcall(function()
		HttpService:PostAsync(
			"url/update_players",
			json,
			Enum.HttpContentType.ApplicationJson
		)
	end)
end

while true do
	fetchCommands()
	updatePlayerCount()
	wait(10)
end

-- MADE BY DAI VIET --

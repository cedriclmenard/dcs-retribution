-------------------------------------------------------------------------------------------------------------------------------------------------------------
-- configuration file for Mbot's Call Artillery Script
--
-- This configuration is tailored for a mission generated by DCS Retribution
-- see https://github.com/dcs-retribution/dcs-retribution
-------------------------------------------------------------------------------------------------------------------------------------------------------------

-- artymbot plugin - configuration
if dcsRetribution then
    -- retrieve specific options values
    if dcsRetribution.plugins then
        if dcsRetribution.plugins.artymbot then
            env.info("DCSRetribution|Mbot's Call Artillery Script plugin - Setting Up")
			for _, data in pairs(dcsRetribution.artilleryGroups.groundArtillery) do
				AddFS(data.groupName)
			end
			if dcsRetribution.plugins.artymbot.shipArtilleryEnable then
				for _, data in pairs(dcsRetribution.artilleryGroups.shipArtillery) do
					AddFS(data.groupName)
				end
			end
			for _, data in pairs(dcsRetribution.forwardObserverUnits) do
				AddFO(data.unitName)
			end
        end
    end
end

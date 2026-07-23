WITH meta_combined AS (
	SELECT ts."state",
		CASE WHEN extract(YEAR FROM DATE_TRUNC('hour', from_unixtime(ts."timestamp" / 1000000000)) + INTERVAL '1' HOUR) = 2019 THEN DATE_TRUNC('hour', from_unixtime(ts."timestamp" / 1000000000)) - INTERVAL '1' YEAR + INTERVAL '1' HOUR
		ELSE DATE_TRUNC('hour', from_unixtime(ts."timestamp" / 1000000000)) + INTERVAL '1' HOUR END as timestamp_hour,
		meta."in.geometry_building_type_recs" as building_type,
		ts."out.electricity.cooling.energy_consumption" as cooling,
		ts."out.electricity.heating.energy_consumption" + ts."out.electricity.heating_hp_bkup.energy_consumption" as heating,
		ts."out.electricity.hot_water.energy_consumption" as water_heating,
		ts."out.electricity.range_oven.energy_consumption" as cooking,
		ts."out.electricity.lighting_interior.energy_consumption" + ts."out.electricity.lighting_exterior.energy_consumption" + ts."out.electricity.lighting_garage.energy_consumption" as lighting,
		ts."out.electricity.refrigerator.energy_consumption" + ts."out.electricity.freezer.energy_consumption" as refrigeration,
		ts."out.electricity.ceiling_fan.energy_consumption" as ceiling_fan,
		ts."out.electricity.heating_fans_pumps.energy_consumption" + ts."out.electricity.cooling_fans_pumps.energy_consumption" +  ts."out.electricity.well_pump.energy_consumption" + ts."out.electricity.heating_hp_bkup_fa.energy_consumption" + ts."out.electricity.mech_vent.energy_consumption" as fans_and_pumps,
		ts."out.electricity.plug_loads.energy_consumption" as computers,
		ts."out.electricity.plug_loads.energy_consumption" as tvs,
		ts."out.electricity.clothes_washer.energy_consumption" as clothes_washing,
		ts."out.electricity.clothes_dryer.energy_consumption" as drying,
		ts."out.electricity.dishwasher.energy_consumption" as dishwasher,
		ts."out.electricity.pool_heater.energy_consumption" as pool_heaters,
		ts."out.electricity.pool_pump.energy_consumption" as pool_pumps,
		ts."out.electricity.permanent_spa_heat.energy_consumption" + ts."out.electricity.permanent_spa_pump.energy_consumption" as portable_electric_spas,
		ts."out.electricity.plug_loads.energy_consumption" as other,
		meta.weight,
		meta."in.sqft" as sqft
		FROM "resstock_amy2018_release_2024.2_by_state" as ts
		LEFT JOIN "resstock_amy2018_release_2024.2_metadata" as meta
		ON ts.bldg_id = meta.bldg_id
		WHERE meta.upgrade = 0 AND ts.upgrade = '0'
		    AND ts."state" NOT IN ('AK', 'HI')
)
SELECT
	timestamp_hour,
	"state" as state,
	"building_type" as building_type,
	sum(cooling*weight) as cooling,
	sum(heating*weight) as heating,
	sum(water_heating*weight) as water_heating,
	sum(cooking*weight) as cooking,
	sum(drying*weight) as drying,
	sum(lighting*weight) as lighting,
	sum(refrigeration*weight) as refrigeration,
	sum(ceiling_fan*weight) as ceiling_fan,
	sum(fans_and_pumps*weight) as fans_and_pumps,
	sum(computers*weight) as computers,
	sum(tvs*weight) as tvs,
	sum(clothes_washing*weight) as clothes_washing,
	sum(dishwasher*weight) as dishwasher,
	sum(pool_heaters*weight) as pool_heaters,
	sum(pool_pumps*weight) as pool_pumps,
	sum(portable_electric_spas*weight) as portable_electric_spas,
	sum(other*weight) as other,
	sum(cooling*weight/sqft) as cooling_sqft,
	sum(heating*weight/sqft) as heating_sqft,
	sum(water_heating*weight/sqft) as water_heating_sqft,
	sum(cooking*weight/sqft) as cooking_sqft,
	sum(drying*weight/sqft) as drying_sqft,
	sum(lighting*weight/sqft) as lighting_sqft,
	sum(refrigeration*weight/sqft) as refrigeration_sqft,
	sum(ceiling_fan*weight/sqft) as ceiling_fan_sqft,
	sum(fans_and_pumps*weight/sqft) as fans_and_pumps_sqft,
	sum(computers*weight/sqft) as computers_sqft,
	sum(tvs*weight/sqft) as tvs_sqft,
	sum(clothes_washing*weight/sqft) as clothes_washing_sqft,
	sum(dishwasher*weight/sqft) as dishwasher_sqft,
	sum(pool_heaters*weight/sqft) as pool_heaters_sqft,
	sum(pool_pumps*weight/sqft) as pool_pumps_sqft,
	sum(portable_electric_spas*weight/sqft) as portable_electric_spas_sqft,
	sum(other*weight/sqft) as other_sqft
FROM meta_combined
GROUP BY "state", "building_type", timestamp_hour
ORDER BY "state", "building_type", timestamp_hour;
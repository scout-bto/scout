WITH meta_combined AS (
	SELECT ts."state",meta."in.county",
		CASE WHEN extract(YEAR FROM {ts_trunc} + INTERVAL '1' HOUR) = 2019 THEN {ts_trunc} - INTERVAL '1' YEAR + INTERVAL '1' HOUR
		ELSE {ts_trunc} + INTERVAL '1' HOUR END as timestamp_hour,
		meta."in.geometry_building_type_recs" as building_type,
		ts."out.electricity.cooling.energy_consumption{kwh}" as cooling,
		ts."out.electricity.heating.energy_consumption{kwh}" + ts."out.electricity.heating_hp_bkup.energy_consumption{kwh}" as heating,
		ts."out.electricity.hot_water.energy_consumption{kwh}" as water_heating,
		ts."out.electricity.range_oven.energy_consumption{kwh}" as cooking,
		ts."out.electricity.lighting_interior.energy_consumption{kwh}" + ts."out.electricity.lighting_exterior.energy_consumption{kwh}" + ts."out.electricity.lighting_garage.energy_consumption{kwh}" as lighting,
		ts."out.electricity.refrigerator.energy_consumption{kwh}" + ts."out.electricity.freezer.energy_consumption{kwh}" as refrigeration,
		ts."out.electricity.ceiling_fan.energy_consumption{kwh}" as ceiling_fan,
		ts."out.electricity.heating_fans_pumps.energy_consumption{kwh}" + ts."out.electricity.cooling_fans_pumps.energy_consumption{kwh}" +  ts."out.electricity.well_pump.energy_consumption{kwh}" + ts."out.electricity.heating_hp_bkup_fa.energy_consumption{kwh}" + ts."out.electricity.mech_vent.energy_consumption{kwh}" as fans_and_pumps,
		-- ResStock doesn't break plug_loads down further, so computers/tvs/
		-- other are all the same underlying value duplicated under 3 names
		-- ("cooking" above is a distinct, real column — range_oven — not
		-- part of this duplication). update_tsv.py's downstream logic only
		-- ever uses "other" (renamed "plug loads"); anything that sums
		-- across these columns must pick a single representative one or it
		-- will multiply-count this load (see compute_peak_days.py's
		-- RESIDENTIAL_ENERGY_COLS).
		ts."out.electricity.plug_loads.energy_consumption{kwh}" as computers,
		ts."out.electricity.plug_loads.energy_consumption{kwh}" as tvs,
		ts."out.electricity.clothes_washer.energy_consumption{kwh}" as clothes_washing,
		ts."out.electricity.clothes_dryer.energy_consumption{kwh}" as drying,
		ts."out.electricity.dishwasher.energy_consumption{kwh}" as dishwasher,
		ts."out.electricity.pool_heater.energy_consumption{kwh}" as pool_heaters,
		ts."out.electricity.pool_pump.energy_consumption{kwh}" as pool_pumps,
		ts."out.electricity.permanent_spa_heat.energy_consumption{kwh}" + ts."out.electricity.permanent_spa_pump.energy_consumption{kwh}" as portable_electric_spas,
		ts."out.electricity.plug_loads.energy_consumption{kwh}" as other,
		meta.weight,
		meta."{sqft_col}" as sqft
		FROM "{by_state_table}" as ts
		LEFT JOIN "{meta_table}" as meta
		ON ts.bldg_id = meta.bldg_id
		WHERE meta.upgrade = 0 AND ts.upgrade = '0'
		    AND meta."in.geometry_building_type_recs" IN (
		        'Mobile Home', 'Multi-Family with 5+ Units', 'Single-Family Detached')
	),
geomap_combined AS (
	SELECT mc.*,
		gm.emm2020_county as emm
	FROM meta_combined as mc
	LEFT JOIN geo_map as gm
	-- Lower-48 in.county values are comma-free NHGIS GISJOIN codes (e.g.
	-- "G0800010"); AK/HI in.county values are instead "ST, County Name"
	-- strings (e.g. "AK, Yukon-Koyukuk Census Area"). geo_map.csv can't
	-- store that comma as-is (the geo_map Athena table uses the naive
	-- Hive CSV SerDe with no quote-escaping), so AK/HI rows are keyed by
	-- the comma-stripped county string instead; stripping commas here is
	-- a no-op for the GISJOIN-keyed Lower-48 rows.
	ON REPLACE(mc."in.county", ',', '') = gm."stock.county"
)
SELECT
	timestamp_hour,
	"emm" as emm,
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
FROM geomap_combined
GROUP BY "emm", "building_type", timestamp_hour
ORDER BY "emm", "building_type", timestamp_hour;
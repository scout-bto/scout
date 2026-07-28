WITH meta_combined AS (
	SELECT ts."state", meta."in.nhgis_county_gisjoin",
		CASE WHEN extract(YEAR FROM {ts_trunc} + INTERVAL '1' HOUR) = 2019 THEN {ts_trunc} - INTERVAL '1' YEAR + INTERVAL '1' HOUR
		ELSE {ts_trunc} + INTERVAL '1' HOUR END as timestamp_hour,
		meta."in.comstock_building_type" as building_type,
		ts."out.electricity.cooling.energy_consumption" as cooling,
		ts."out.electricity.heating.energy_consumption" + ts."out.electricity.heat_recovery.energy_consumption" + ts."out.electricity.heat_rejection.energy_consumption" as heating,
		ts."out.electricity.pumps.energy_consumption" as pumps,
		ts."out.electricity.fans.energy_consumption" as ventilation,
		ts."out.electricity.water_systems.energy_consumption" as water_heating,
		ts."out.electricity.interior_lighting.energy_consumption" + ts."out.electricity.exterior_lighting.energy_consumption" as lighting,
		ts."out.electricity.refrigeration.energy_consumption" as refrigeration,
		ts."out.electricity.interior_equipment.energy_consumption" as cooking,
		ts."out.electricity.interior_equipment.energy_consumption" as "pcs",
		ts."out.electricity.interior_equipment.energy_consumption" as nonpc_office_equipment,
		ts."out.electricity.interior_equipment.energy_consumption" as other_mels,
		meta.weight,
		meta."in.sqft..ft2" as sqft
		FROM "{by_state_table}" as ts
		LEFT JOIN "{meta_table}" as meta
		ON ts.bldg_id = meta.bldg_id
		WHERE (meta.upgrade = 0 AND ts.upgrade = '0')
		    AND meta."in.comstock_building_type" IN (
		        'MediumOffice', 'LargeOffice', 'LargeHotel', 'RetailStandalone', 'Warehouse')
),

geomap_combined AS (
	SELECT mc.*,
		gm.emm2020_county as emm
	FROM meta_combined as mc
	LEFT JOIN geo_map as gm
	ON mc."in.nhgis_county_gisjoin" = gm."stock.county"
)

SELECT
	timestamp_hour,
	"emm" as emm,
	"building_type" as building_type,
	sum(cooling*weight) as cooling,
	sum(heating*weight) as heating,
	sum(pumps*weight) as pumps,
	sum(ventilation*weight) as ventilation,
	sum(water_heating*weight) as water_heating,
	sum(lighting*weight) as lighting,
	sum(refrigeration*weight) as refrigeration,
	sum(cooking*weight) as cooking,
	sum(pcs*weight) as pcs,
	sum(nonpc_office_equipment*weight) as nonpc_office_equipment,
	sum(other_mels*weight) as other_mels,
	sum(cooling*weight/sqft) as cooling_sqft,
	sum(heating*weight/sqft) as heating_sqft,
	sum(pumps*weight/sqft) as pumps_sqft,
	sum(ventilation*weight/sqft) as ventilation_sqft,
	sum(water_heating*weight/sqft) as water_heating_sqft,
	sum(lighting*weight/sqft) as lighting_sqft,
	sum(refrigeration*weight/sqft) as refrigeration_sqft,
	sum(cooking*weight/sqft) as cooking_sqft,
	sum(pcs*weight/sqft) as pcs_sqft,
	sum(nonpc_office_equipment*weight/sqft) as nonpc_office_equipment_sqft,
	sum(other_mels*weight/sqft) as other_mels_sqft
FROM geomap_combined
GROUP BY "emm", "building_type", timestamp_hour
ORDER BY "emm", "building_type", timestamp_hour;
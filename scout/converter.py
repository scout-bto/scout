#!/usr/bin/env python3

"""Module for updating the conversion factors and prices JSON databases.

This module can be used to update the following two files:

1) Electricity site-source conversion factors and CO2 intensities and prices for electricity,
natural gas, and "other" fuel stored in a JSON database. The module uses the EIA API to pull
the required data and automate this process without first downloading AEO data tables.

2) CO2 intensities and retail electricity price projections for the EIA's 25 2020 EMM regions or
states stored in a JSON database. For states, gas price projections are included as well. The module
uses the EIA API to pull the required regional EMM data and automate this process without first
downloading AEO data tables.

The module gives users the option to specify an EIA AEO year and an EIA AEO scenario for which to
output updated site-source conversion factors or updated EMM region CO2 intensity and retail price
projections.

This module leaves intact any data in the JSON from years prior to the first year of available data
for a particular AEO requested. For example, if AEO 2018 is requested, the first year of available
data is 2016, so data already present in the conversions JSON file for years prior to 2016 would
remain unchanged by this function.

The intended workflow for running this module with other routines is as follows:

1) Run ./scout/state_baseline_data_updater.py to update the current snapshots of state-level
emissions and energy prices from EIA's survey data (via the API). The result will be written to the
file ./scout/supporting_data/convert_data/EIA_State_Emissions_Prices_Baselines_*.csv, where *
indicates the year of the data.

2) Run ./scout/converter.py separately to update each of the files beginning with "emm_region_"
or "site_source in ./scout/supporting_data/convert_data, which will update all of the annual average
emissions intensity, energy price, and site-source conversion values to reflect AEO projections
pulled from the EIA API. Users are prompted to choose AEO cases separately for fossil fuels and
electricity to support bounding sensitivity cases on prices (more below). Electricity
and gas prices are both broken out in the "state_" files, while only electricity prices are broken
out in the "emm_region_" files. Electricity emissions intensities are also broken out in both of
those files. Also note that updating the "emm_region_" files will automatically update the files
beginning "state_" as well. When prompted, select the latest AEO year available and use the
following mapping between AEO case and the scenarios indicated in the file names being updated:
lowZTC -> files with "-100by2035" and "-95by2050"; ref2023 -> all other files. Users may also enter
pairs of scenarios that differ for electricity vs. fossil fuels and represent high gas/low electric
price and low gas/high electric price futures, e.g., 'lowZTC' (low zero-carbon technology cost) for
electricity and 'lowogs' (low oil and gas supply) for fossil (low electric/high gas rates), and
'highZTC' for electricity and 'highogs' for fossil (high electric/low gas rates).

3) Run ./scout/cambium_updater.py separately to update each of the files beginning with
"emm_region_" or "state" and including the scenarios "-MidCase" "95by2050" and "-100by2035" from
reflecting AEO trends in the EMM- or state-level annual emissions intensity values to reflecting
trends from the relevant Cambium scenario. This routine will also update hourly emissions and
price scaling factors that are used in Scout for time-sensitive valuation of these variables.
Cambium data are downloaded from https://scenarioviewer.nrel.gov/ to a folder that this routine
reads in from, see prompts in routine for instructions about how to structure that folder, and use
the latest available Cambium year when prompted.

"""

import requests
import os
import sys
import numpy as np
import json
import argparse
import pandas as pd
from backoff import on_exception, expo
from collections import OrderedDict
from pathlib import Path
from scout.config import FilePaths as fp


class UsefulVars(object):
    """Class of variables that are handy to have widely available.

    Attributes:
        emm_state_map (str): Weights for mapping from EMM regions to states.
        state_baseline_files (list): List of state-level baseline data files.
        state_conv_file (str): Path to location for writing state-level
            conversions JSON file output.
        metadata (str): Path to AEO data year range metadata file.
    """

    def __init__(self):
        self.emm_state_map = fp.CONVERT_DATA / "geo_map" / (
            "EMM_State_ColSums.txt")
        # Set path to state-level baseline data
        self.state_baseline_files = list(Path(fp.CONVERT_DATA).glob(
            'EIA_State_Emissions_Prices_Baselines_*.csv'))
        self.metadata = fp.METADATA_PATH


class ValidQueries(object):
    """Define valid query options for AEO data requested via the EIA data API

    Attributes:
        file_type (list): A list of file types to update with this
            module, where "national" corresponds to the site-source
            conversions files, and "regional" corresponds to the EMM
            and state price and emissions projections files
        years (list): A list of valid AEO report years for which this
            module has been evaluated to work.
        emm_years (list): A list of valid AEO report years for which
            this module has been evaluated to work for EMM-resolved data
            updates
        cases (dict): A list of AEO cases relevant to Scout for each AEO
            publication year, specified with the strings used by the API.
        regions_dict (dict): A dict of valid AEO regions, with keys
            denoting region abbreviations to use when querying the
            API and values denoting region abbreviations to use for
            writing the updated JSON file.
    """

    def __init__(self):
        self.file_type = ['national', 'regional']
        self.years = ['2018', '2019', '2020', '2021', '2022', '2023', '2025']
        self.emm_years = ['2020', '2021', '2022', '2023', '2025']
        self.cases = {
            '2018': ['ref2018', 'co2fee25'],
            '2019': ['ref2019'],
            '2020': ['ref2020', 'co2fee25', 'lowogs', 'lorencst'],
            '2021': ['ref2021', 'lowogs', 'lorencst'],
            '2022': ['ref2022', 'lowogs', 'lorencst'],
            '2023': ['ref2023', 'lowogs', 'lowZTC', 'highogs', 'highZTC',
                     'lowmaclowZTC', 'highmachighZTC'],
            '2025': ['ref2025', 'lowogs', 'lowZTC', 'highogs', 'highZTC']}
        self.regions_dict = OrderedDict({'WECCB': 'BASN',
                                         'WECCCAN': 'CANO',
                                         'WECCCAS': 'CASO',
                                         'FLRC': 'FRCC',
                                         'NPCCNE': 'ISNE',
                                         'MCC': 'MISC',
                                         'MCE': 'MISE',
                                         'MCS': 'MISS',
                                         'MCW': 'MISW',
                                         'WENWPP': 'NWPP',
                                         'NENYCLI': 'NYCW',
                                         'NPCCUPNY': 'NYUP',
                                         'PJMCE': 'PJMC',
                                         'PJMD': 'PJMD',
                                         'PJME': 'PJME',
                                         'PJMW': 'PJMW',
                                         'WECCRKS': 'RMRG',
                                         'SWPPC': 'SPPC',
                                         'SWPPNO': 'SPPN',
                                         'SWPPSO': 'SPPS',
                                         'SERCE': 'SRCA',
                                         'SERCCNT': 'SRCE',
                                         'SERCSOES': 'SRSE',
                                         'WECCSW': 'SRSG',
                                         'TRE': 'TRE'})


class EIAQueries(object):
    """Reference strings for obtaining required data from EIA AEO

    Attributes:
        data_series (list): API key strings to obtain the desired data
            from the EIA AEO for the scenario and AEO release year
            specified by the user.
        data_names (list): A list of strings to use as keys for the
            data pulled from the AEO and added to a dict.
        data_table_ids (list): A list of the expected data tableId
            values corresponding to the tables for the requested data
            series from the EIA API.
        data_series_gasprice (list): API key strings to obtain the desired
            gas price projections EIA AEO for the scenario and
            AEO release year specified by the user.
        data_names_gasprice (list): A list of strings to use as keys for
            the gas price data pulled from the AEO and added to a dict.
        data_table_ids_gasprice (list): A list of the expected data tableId
            values corresponding to the tables for the requested gas price data
            series from the EIA API.
        data_series_emm (list): API key strings to obtain the desired
            data by EMM region from the EIA AEO for the scenario and
            AEO release year specified by the user.
        data_names_emm (list): A list of strings to use as keys for
            the EMM data pulled from the AEO and added to a dict.
        data_table_ids_emm (list): A list of the expected data tableId
            values corresponding to the tables for the requested EMM data
            series from the EIA API.
        nonstandard_query_reqd (list): A list of API series IDs whose
            API paths do not follow the same format as other data.
        query (list): Complete API path (URL) constructed for the
            AEO scenario and release year specified by the user.
        query_gasprice (list): Complete API path (URL) constructed for gas
            price data in the AEO scenario and release year specified by the user.
        query_emm (list): Complete API path (URL) constructed for
            each EMM region for the AEO scenario and release year
            specified by the user.
    """
    def __init__(self, yr, scen):
        self.data_series = [
            'cnsm_NA_elep_NA_hyd_cnv_NA_qbtu',
            'cnsm_NA_elep_NA_geothm_NA_NA_qbtu',
            'cnsm_NA_elep_NA_slr_therm_NA_qbtu',
            'cnsm_NA_elep_NA_slr_phtvl_NA_qbtu',
            'cnsm_NA_elep_NA_wnd_NA_NA_qbtu',
            'cnsm_enu_alls_NA_elc_delv_NA_qbtu',
            'cnsm_enu_alls_NA_erl_delv_NA_qbtu',
            'cnsm_enu_resd_NA_elc_NA_NA_qbtu',
            'cnsm_enu_resd_NA_erl_NA_NA_qbtu',
            'cnsm_enu_comm_NA_erl_NA_NA_qbtu',
            'cnsm_enu_comm_NA_elc_NA_NA_qbtu',
            'emi_co2_resd_NA_elc_NA_NA_millmetnco2',
            'emi_co2_comm_NA_elc_NA_NA_millmetnco2',
            'prce_real_resd_NA_elc_NA_NA_y13dlrpmmbtu',
            'prce_real_comm_NA_elc_NA_NA_y13dlrpmmbtu',
            'cnsm_enu_resd_NA_ng_NA_NA_qbtu',
            'cnsm_enu_comm_NA_ng_NA_NA_qbtu',
            'emi_co2_resd_NA_ng_NA_NA_millmetnco2',
            'emi_co2_comm_NA_ng_NA_NA_millmetnco2',
            'prce_real_resd_NA_ng_NA_NA_y13dlrpmmbtu',
            'prce_real_comm_NA_ng_NA_NA_y13dlrpmmbtu',
            'cnsm_enu_resd_NA_lfl_NA_NA_qbtu',
            'emi_co2_resd_NA_pet_NA_NA_millmetnco2',
            'cnsm_enu_comm_NA_lfl_NA_NA_qbtu',
            'emi_co2_comm_NA_pet_NA_NA_millmetnco2',
            'cnsm_enu_comm_NA_cl_NA_NA_qbtu',
            'emi_co2_comm_NA_cl_NA_NA_millmetnco2',
            'prce_real_resd_NA_prop_NA_NA_y13dlrpmmbtu',
            'prce_real_resd_NA_dfo_NA_NA_y13dlrpmmbtu',
            'cnsm_enu_resd_NA_prop_NA_NA_qbtu',
            'cnsm_enu_resd_NA_dfo_NA_NA_qbtu',
            'prce_real_comm_NA_prop_NA_NA_y13dlrpmmbtu',
            'prce_real_comm_NA_dfo_NA_NA_y13dlrpmmbtu',
            'prce_real_comm_NA_rfl_NA_NA_y13dlrpmmbtu',
            'cnsm_enu_comm_NA_prop_NA_NA_qbtu',
            'cnsm_enu_comm_NA_dfo_NA_NA_qbtu',
            'cnsm_enu_comm_NA_rfo_NA_NA_qbtu']
        self.data_series_gasprice = [
            'prce_real_resd_NA_ng_NA_NA_y13dlrpmmbtu',
            'prce_real_comm_NA_ng_NA_NA_y13dlrpmmbtu']

        self.data_names = [
            'elec_renew_hydro',
            'elec_renew_geothermal',
            'elec_renew_solar_thermal',
            'elec_renew_solar_pv',
            'elec_renew_wind',
            'elec_tot_energy_site',
            'elec_tot_energy_loss',
            'elec_res_energy_site',
            'elec_res_energy_loss',
            'elec_com_energy_site',
            'elec_com_energy_loss',
            'elec_res_co2',
            'elec_com_co2',
            'elec_res_price',
            'elec_com_price',
            'ng_res_energy',
            'ng_com_energy',
            'ng_res_co2',
            'ng_com_co2',
            'ng_res_price',
            'ng_com_price',
            'petro_res_energy',
            'petro_res_co2',
            'petro_com_energy',
            'petro_com_co2',
            'coal_com_energy',
            'coal_com_co2',
            'lpg_res_price',
            'distl_res_price',
            'lpg_res_energy',
            'distl_res_energy',
            'lpg_com_price',
            'distl_com_price',
            'rsid_com_price',
            'lpg_com_energy',
            'distl_com_energy',
            'rsid_com_energy']
        self.data_names_gasprice = [
            'ng_res_price',
            'ng_com_price']

        # Note: convert table number to string for API query
        self.data_table_ids = [
            str(x) for x in [
                # Table 17. Renewable Energy Consumption by Sector and Source
                24, 24, 24, 24, 24,
                # Table 2. Energy Consumption by Sector and Source
                2, 2, 2, 2, 2, 2,
                # Table 18. Energy-Related Carbon Dioxide Emissions by Sector and
                # Source
                17, 17,
                # Table 3. Energy Prices by Sector and Source
                3, 3,
                2, 2,
                17, 17,
                3, 3,
                2, 17, 2, 17, 2, 17,
                3, 3, 2, 2,
                3, 3, 3, 2, 2, 2]]
        self.data_table_ids_gasprice = ["3"] * len(self.data_series_gasprice)

        self.data_series_emm = []
        self.data_names_emm = []

        for reg in list(ValidQueries().regions_dict.keys()):
            self.data_series_emm.extend([
                'emi_co2_elep_NA_NA_NA_' + reg.lower() + '_millton',
                'cnsm_NA_elep_NA_elc_NA_' + reg.lower() + '_blnkwh',
                'prce_NA_resd_NA_elc_NA_' + reg.lower() + '_y13cntpkwh',
                'prce_NA_comm_NA_elc_NA_' + reg.lower() + '_y13cntpkwh'])
            self.data_names_emm.extend([
                'elec_co2_total_' + reg,
                'elec_sales_total_' + reg,
                'elec_enduse_price_res_' + reg,
                'elec_enduse_price_com_' + reg])

        self.data_table_ids_emm = ["62"] * len(self.data_series_emm)
        # Table 54. Electric Power Projections by Electricity Market Module
        # Region

        self.query = []
        self.query_gasprice = []
        self.query_emm = []

        self.nonstandard_query_reqd = self.data_series[0:5]

        for series_id in self.data_series:
            if series_id in self.nonstandard_query_reqd:
                qstr = (
                    'https://api.eia.gov/v2/aeo/' + yr +
                    '/data/?frequency=annual&data[0]=value&facets[scenario][]='
                    + scen + '&facets[seriesId][]=' + series_id +
                    '&facets[seriesId][]=' + series_id +
                    '&sort[0][column]=period&sort[0][direction]=desc&offset=0'
                    + '&length=5000')
            else:
                qstr = (
                    'https://api.eia.gov/v2/aeo/' + yr +
                    '/data/?frequency=annual&data[0]=value&facets[scenario][]='
                    + scen + '&facets[seriesId][]=' + series_id +
                    '&sort[0][column]=period&sort[0][direction]=desc&offset=0'
                    + '&length=5000')
            self.query.append(qstr)

        for series_id in self.data_series_gasprice:
            self.query_gasprice.append(
                    'https://api.eia.gov/v2/aeo/' + yr +
                    '/data/?frequency=annual&data[0]=value&facets[scenario][]='
                    + scen + '&facets[seriesId][]=' + series_id +
                    '&sort[0][column]=period&sort[0][direction]=desc&offset=0'
                    + '&length=5000')

        for series_id in self.data_series_emm:
            self.query_emm.append(
                'https://api.eia.gov/v2/aeo/' + yr +
                '/data/?frequency=annual&data[0]=value&facets[scenario][]='
                + scen + '&facets[seriesId][]=' + series_id +
                '&sort[0][column]=period&sort[0][direction]=desc&offset=0'
                + '&length=5000')


# https://stackoverflow.com/questions/22786068/
# how-to-avoid-http-error-429-too-many-requests-python
@on_exception(expo, Exception, max_tries=5)
def api_query(api_key, query_str, expect_table_id):
    """Execute an EIA API query and extract the data returned

    Execute a query of the EIA API and extract the data from the
    structure returned by the API.

    Args:
        api_key (str): EIA API key.
        query_str (str): EIA API URL for a specific data series,
            excluding the user-specific API key.
        expect_table_id (int): The tableId in the EIA API from which
            the current query data are expected to be drawn.

    Returns:
        A nested list of data with inner lists structured as
        [year, data value] where the years are YYYY strings.
    """
    response = requests.get(query_str + '&api_key=' + api_key)

    try:
        data = response.json()['response']['data']
        # Extract only the required data in the API response; ensure that
        # all numbers are formatted as floats (in some cases, they are retrieved as strings)
        data = [[str(x['period']), float(x['value'])] for x in data if
                x['tableId'] == expect_table_id]
    except KeyError:
        if response.status_code == 429:  # API rate limit exceeded
            raise Exception('Rate limit reached')
        else:
            # Any other response, e.g., malformed header or no data returned
            print('\nAttempted query invalid: ' + query_str)
    # print(query_str + '&api_key=' + api_key)
    return data


def data_processor(data):
    """Restructure the data obtained from the API into numpy arrays

    Args:
        data (list): A list of data, with each value a list where
            the first value is the year as a string and the second
            value is the number for that year for the data requested.

    Returns:
        Two numpy arrays, one containing the data and one containing
        the years corresponding to those data. Both arrays are sorted
        according to ascending year order.
    """
    years, data = zip(*data)
    years = np.array(years)
    data = np.array(data)[years.argsort()]  # Re-sort in ascending year order
    years = years[years.argsort()]  # Re-sort to be in ascending year order

    # Get year of earliest AEO data
    aeo_min = aeo_min_extract()

    # If/else loop to handle issue of conversion file not matching
    # aeo_min from metadata.json. In this case, years for each region
    # in conversion file are extended to match aeo_min, using replicated
    # values from minimum year in conversion file.

    if str(aeo_min) not in years:

        # convert aeo_min and year data to datetime64
        aeo_min = np.datetime64(str(aeo_min))
        years = [np.datetime64(year) for year in years]

        # Get difference between earliest data year and aeo_min year
        # from metadata.json
        diff = (min(years) - aeo_min).astype(int)

        # add prior years to array for length of diff
        new_years = np.array([aeo_min + np.timedelta64(i, 'Y') for i in
                              range(diff)])
        years = np.insert(years, 0, new_years, axis=0)

        # add repeated data to array to match number of prior years added
        data_insert = [data[0]] * diff
        data = np.insert(data, 0, data_insert, axis=0)

        # convert years back to array of strings
        years = np.array([np.datetime_as_string(year, unit='Y') for year in
                          years])

        # Re-sort in ascending year order
        data = np.array(data)[years.argsort()]
        years = years[years.argsort()]

    return data, years


def data_getter(api_key, series_names, api_urls, series_table):
    """Get data from EIA using their data API and store in dict

    Call the required functions to obtain data from EIA using their
    data API, restructure the data into numpy arrays, and store in
    a dict according to the specified series names for later recall.

    Args:
        api_key (str): EIA API key.
        series_names (list): List of strings for the desired keys
            to use for the data in the dict.
        api_urls (list): List of paths (URLs) to obtain the desired
            data from the EIA API.
        series_table (list): The data tableId values corresponding to
            the expected tables for the series_names.

    Returns:
        Dict with keys specified in series_names for which the
        values correspond to the numpy arrays of data obtained from
        the EIA API for the data from api_urls.
    """
    mstr_data_dict = {}

    for idx, series in enumerate(api_urls):
        # Obtain data from EIA API; if the data returned is a dict,
        # there was an error with the series_id provided and that
        # output should be ignored entirely; the resulting error
        # from the missing key in the master dict will be handled
        # in the updater function
        raw_data = api_query(api_key, series, series_table[idx])
        if isinstance(raw_data, (list,)):
            # Restructure the data obtained from the API
            data, years = data_processor(raw_data)
            # Record the data as a value in a dict with the key
            # corresponding to the specified series name
            mstr_data_dict[series_names[idx]] = data

    return mstr_data_dict, years


def updater(conv, api_key, aeo_yr, scen_elec, scen_gas, web):
    """Perform calculations using EIA data to update conversion factors JSON

    Using data from the AEO year and specified NEMS modeling scenario,
    calculate revised site-source conversion factors, CO2 emissions
    rates, and energy prices.

    In the case of the "other" fuel types, energy prices are based on
    an energy use by fuel type-weighted average.

    For each of the calculations performed, in case of data missing from
    the record dict 'z' not obtained from the API due to invalid series
    IDs, run each calculation and update in a try/except block to catch
    KeyErrors for missing data and address them by not updating the
    original data and printing a warning to the console for the user.

    Args:
        conv (dict): Data structure from conversion JSON data file.
        api_key (str): EIA API key from system environment variable.
        aeo_yr (str): The desired year of the Annual Energy Outlook
            to query for data.
        scen_elec (str): The desired AEO "case" or scenario to query for electricity.
        scen_gas (str): The desired AEO "case" or scenario to query for fossil fuels.
        web (bool): If true, the data output should include "other
            fuel" instead of separate "distillate" and "propane" fields.

    Returns:
        Updated conversion factors dict to be exported to the conversions JSON.
    """

    # Get data via EIA API. Account for cases where user has specified two separate
    # scenarios to use in representing fossil vs. electric projections.
    dq_foss, dq_elec = [EIAQueries(aeo_yr, x) for x in [scen_elec, scen_gas]]

    z_foss, yrs_foss = \
        data_getter(api_key, dq_foss.data_names, dq_foss.query, dq_foss.data_table_ids)
    z_elec, yrs_elec = \
        data_getter(api_key, dq_elec.data_names, dq_elec.query, dq_elec.data_table_ids)

    # Calculate adjustment factor to use the captured energy method
    # to account for electric source energy from renewable generation;
    # this approach is derived from the DOE report "Accounting
    # Methodology for Source Energy of Non-Combustible Renewable
    # Electricity Generation"
    if conv['site-source calculation method'] == 'captured energy':
        renew_factor = ((z_elec['elec_renew_hydro'] + z_elec['elec_renew_geothermal'] +
                         z_elec['elec_renew_wind'] + z_elec['elec_renew_solar_thermal'] +
                         z_elec['elec_renew_solar_pv']) /
                        (z_elec['elec_tot_energy_site'] +
                            z_elec['elec_tot_energy_loss']))
        capnrg = 1 - renew_factor + renew_factor*3412/9510
        # Since proceeding without this conversion factor would yield
        # results that are not as expected, the possible KeyError exception
        # due to missing data is intentionally not caught
    else:
        # Use the existing calculations for the fossil fuel equivalence method
        capnrg = np.ones(np.shape(z_elec['elec_renew_hydro']))

    # Electricity site-source conversion factors
    try:
        ss_conv = ((z_elec['elec_tot_energy_site'] + z_elec['elec_tot_energy_loss']) /
                   z_elec['elec_tot_energy_site'])
        for idx, year in enumerate(yrs_elec):
            conv['electricity']['site to source conversion']['data'][year] = (
                round(ss_conv[idx]*capnrg[idx], 6))
    except KeyError:
        print('\nDue to failed data retrieval from the API, electricity '
              'site-source conversion factors were not updated.')

    # Update electricity CO2 intensities
    # Residential electricity CO2 intensities [Mt CO2/quads]
    try:
        co2_res_ints = (z_elec['elec_res_co2'] /
                        (z_elec['elec_res_energy_site'] +
                         z_elec['elec_res_energy_loss']))
        for idx, year in enumerate(yrs_elec):
            conv['electricity']['CO2 intensity']['data']['residential'][
                 year] = (round(co2_res_ints[idx]/capnrg[idx], 6))
    except KeyError:
        print('\nDue to failed data retrieval from the API, residential '
              'electricity CO2 emissions intensities were not updated.')

    # Commercial electricity CO2 intensities [Mt CO2/quads]
    try:
        co2_com_ints = (z_elec['elec_com_co2'] /
                        (z_elec['elec_com_energy_site'] +
                         z_elec['elec_com_energy_loss']))
        for idx, year in enumerate(yrs_elec):
            conv['electricity']['CO2 intensity']['data']['commercial'][
                 year] = (round(co2_com_ints[idx]/capnrg[idx], 6))
    except KeyError:
        print('\nDue to failed data retrieval from the API, commercial '
              'electricity CO2 emissions intensities were not updated.')

    # Residential natural gas CO2 intensities [Mt CO2/quads]
    try:
        co2_res_ng_ints = z_foss['ng_res_co2']/z_foss['ng_res_energy']
        for idx, year in enumerate(yrs_foss):
            conv['natural gas']['CO2 intensity']['data']['residential'][
                 year] = (round(co2_res_ng_ints[idx], 6))
    except KeyError:
        print('\nDue to failed data retrieval from the API, residential '
              'natural gas CO2 emissions intensities were not updated.')

    # Commercial natural gas CO2 intensities [Mt CO2/quads]
    try:
        co2_com_ng_ints = z_foss['ng_com_co2']/z_foss['ng_com_energy']
        for idx, year in enumerate(yrs_foss):
            conv['natural gas']['CO2 intensity']['data']['commercial'][
                 year] = (round(co2_com_ng_ints[idx], 6))
    except KeyError:
        print('\nDue to failed data retrieval from the API, commercial '
              'natural gas CO2 emissions intensities were not updated.')

    # Residential propane CO2 intensities [Mt CO2/quads]
    try:
        for idx, year in enumerate(yrs_foss):
            conv['propane']['CO2 intensity']['data']['residential'][year] = (
                62.88)  # hard coded CO2 intensity of propane
    except KeyError:
        if not web:
            print('\nDue to failed data retrieval from the API, residential '
                  'propane CO2 emissions intensities were not updated.')

    # Commercial propane CO2 intensities [Mt CO2/quads]
    try:
        for idx, year in enumerate(yrs_foss):
            conv['propane']['CO2 intensity']['data']['commercial'][year] = (
                62.88)  # hard coded CO2 intensity of propane
    except KeyError:
        if not web:
            print('\nDue to failed data retrieval from the API, commercial '
                  'propane CO2 emissions intensities were not updated.')

    # Residential distillate CO2 intensities [Mt CO2/quads]
    try:
        for idx, year in enumerate(yrs_foss):
            conv['distillate']['CO2 intensity']['data']['residential'][
                year] = (74.14)  # hard coded CO2 intensity of distillate
    except KeyError:
        if not web:
            print('\nDue to failed data retrieval from the API, residential '
                  'distillate CO2 emissions intensities were not updated.')

    # Commercial distillate CO2 intensities [Mt CO2/quads]
    try:
        for idx, year in enumerate(yrs_foss):
            conv['distillate']['CO2 intensity']['data']['commercial'][
                 year] = (74.14)  # hard coded CO2 intensity of distillate
    except KeyError:
        if not web:
            print('\nDue to failed data retrieval from the API, commercial '
                  'distillate CO2 emissions intensities were not updated.')

    # Residential other fuel CO2 intensities [Mt CO2/quads]
    try:
        co2_res_ot_ints = z_foss['petro_res_co2']/z_foss['petro_res_energy']
        for idx, year in enumerate(yrs_foss):
            conv['other']['CO2 intensity']['data']['residential'][year] = (
                round(co2_res_ot_ints[idx], 6))
    except KeyError:
        if web:
            print('\nDue to failed data retrieval from the API, residential '
                  '"other fuel" CO2 emissions intensities were not updated.')

    # Commercial other fuel CO2 intensities [Mt CO2/quads]
    try:
        co2_com_ot_ints = ((z_foss['petro_com_co2'] + z_foss['coal_com_co2']) /
                           (z_foss['petro_com_energy'] + z_foss['coal_com_energy']))
        for idx, year in enumerate(yrs_foss):
            conv['other']['CO2 intensity']['data']['commercial'][year] = (
                round(co2_com_ot_ints[idx], 6))
    except KeyError:
        if web:
            print('\nDue to failed data retrieval from the API, commercial '
                  '"other fuel" CO2 emissions intensities were not updated.')

    # Residential electricity prices [$/MMBtu source]
    try:
        for idx, year in enumerate(yrs_elec):
            conv['electricity']['price']['data']['residential'][year] = (
                round(z_elec['elec_res_price'][idx]/(ss_conv[idx]*capnrg[idx]), 6))
    except KeyError:
        print('\nDue to failed data retrieval from the API, residential '
              'electricity prices were not updated.')

    # Commercial electricity prices [$/MMBtu source]
    try:
        for idx, year in enumerate(yrs_elec):
            conv['electricity']['price']['data']['commercial'][year] = (
                round(z_elec['elec_com_price'][idx]/(ss_conv[idx]*capnrg[idx]), 6))
    except KeyError:
        print('\nDue to failed data retrieval from the API, commercial '
              'electricity prices were not updated.')

    # Residential natural gas prices [$/MMBtu source]
    try:
        for idx, year in enumerate(yrs_foss):
            conv['natural gas']['price']['data']['residential'][year] = (
                round(z_foss['ng_res_price'][idx], 6))
    except KeyError:
        print('\nDue to failed data retrieval from the API, residential '
              'natural gas prices were not updated.')

    # Commercial natural gas prices [$/MMBtu source]
    try:
        for idx, year in enumerate(yrs_foss):
            conv['natural gas']['price']['data']['commercial'][year] = (
                round(z_foss['ng_com_price'][idx], 6))
    except KeyError:
        print('\nDue to failed data retrieval from the API, commercial '
              'natural gas prices were not updated.')

    # Residential propane prices [$/MMBtu source]
    try:
        for idx, year in enumerate(yrs_foss):
            conv['propane']['price']['data']['residential'][year] = (
                round(z_foss['lpg_res_price'][idx], 6))
    except KeyError:
        if not web:
            print('\nDue to failed data retrieval from the API, residential '
                  'propane prices were not updated.')

    # Commercial propane prices [$/MMBtu source]
    try:
        for idx, year in enumerate(yrs_foss):
            conv['propane']['price']['data']['commercial'][year] = (
                round(z_foss['lpg_com_price'][idx], 6))
    except KeyError:
        if not web:
            print('\nDue to failed data retrieval from the API, commercial '
                  'propane prices were not updated.')

    # Residential distillate prices [$/MMBtu source]
    try:
        for idx, year in enumerate(yrs_foss):
            conv['distillate']['price']['data']['residential'][year] = (
                round(z_foss['distl_res_price'][idx], 6))
    except KeyError:
        if not web:
            print('\nDue to failed data retrieval from the API, residential '
                  'distillate prices were not updated.')

    # Commercial distillate prices [$/MMBtu source]
    try:
        for idx, year in enumerate(yrs_foss):
            conv['distillate']['price']['data']['commercial'][year] = (
                round(z_foss['distl_com_price'][idx], 6))
    except KeyError:
        if not web:
            print('\nDue to failed data retrieval from the API, commercial '
                  'distillate prices were not updated.')

    # Residential other fuel price as energy use-weighted average
    # of propane and distillate (fuel oil) prices [$/MMBtu source]
    try:
        res_other_price = (z_foss['lpg_res_price']*z_foss['lpg_res_energy']/(
                            z_foss['lpg_res_energy'] + z_foss['distl_res_energy']) +
                           z_foss['distl_res_price']*z_foss['distl_res_energy']/(
                            z_foss['lpg_res_energy'] + z_foss['distl_res_energy']))
        for idx, year in enumerate(yrs_foss):
            conv['other']['price']['data']['residential'][year] = (
                round(res_other_price[idx], 6))
    except KeyError:
        if web:
            print('\nDue to failed data retrieval from the API, residential '
                  '"other fuel" prices were not updated.')

    # Commercial other fuel price as energy use-weighted average of
    # propane, distillate (fuel oil), and residual (fuel oil) prices
    # [$/MMBtu source]
    try:
        denom = z_foss['lpg_com_energy']+z_foss['distl_com_energy']+z_foss['rsid_com_energy']
        com_other_price = (z_foss['lpg_com_price']*z_foss['lpg_com_energy']/denom +
                           z_foss['distl_com_price']*z_foss['distl_com_energy']/denom +
                           z_foss['rsid_com_price']*z_foss['rsid_com_energy']/denom)
        for idx, year in enumerate(yrs_foss):
            conv['other']['price']['data']['commercial'][year] = (
                round(com_other_price[idx], 6))
    except KeyError:
        if web:
            print('\nDue to failed data retrieval from the API, commercial '
                  '"other fuel" prices were not updated.')

    return conv


def updater_gastrend(conv, api_key, aeo_yr, scen_gas):
    """Pull AEO natural gas price projections for residential and commercial.

    Using data from the AEO year and specified NEMS modeling scenario, pull gas price forecasts
    in $/MMBtu.

    In case of data missing from the record dict 'z' not obtained from the API due to invalid
    series IDs, run each calculation and update in a try/except block to catch KeyErrors for
    missing data and address them by not updating the original data and printing a warning to the
    console for the user.

    Args:
        conv (dict): Data structure for gas price information.
        api_key (str): EIA API key from system environment variable.
        aeo_yr (str): The desired year of the Annual Energy Outlook to query for data.
        scen_gas (str): The desired AEO "case" or scenario to query.

    Returns:
        Residential and commercial gas price forecast at the national level.
    """

    dq = EIAQueries(aeo_yr, scen_gas)
    z, yrs = data_getter(
        api_key, dq.data_names_gasprice, dq.query_gasprice, dq.data_table_ids_gasprice)

    # Residential natural gas prices [$/MMBtu source]
    try:
        for idx, year in enumerate(yrs):
            conv['residential'][year] = (round(z['ng_res_price'][idx], 6))
    except KeyError:
        print('\nDue to failed data retrieval from the API, residential '
              'natural gas prices were not updated.')
    # Commercial natural gas prices [$/MMBtu source]
    try:
        for idx, year in enumerate(yrs):
            conv['commercial'][year] = (round(z['ng_com_price'][idx], 6))
    except KeyError:
        print('\nDue to failed data retrieval from the API, commercial '
              'natural gas prices were not updated.')

    return conv


def updater_emm(conv, api_key, aeo_yr, scen_elec):
    """Perform calculations using EIA data to update EMM conversion factors
    JSON.

    Using data from the AEO year and specified NEMS modeling scenario,
    calculate CO2 emissions intensities and energy prices for EIA EMM regions.
    For each of the calculations performed, in case of data missing from
    the record dict 'z' not obtained from the API due to invalid series
    IDs, run each calculation and update in a try/except block to catch
    KeyErrors for missing data and address them by not updating the
    original data and printing a warning to the console for the user.

    Args:
        conv (dict): Data structure from conversion JSON data file.
        api_key (str): EIA API key from system environment variable.
        aeo_yr (str): The desired year of the Annual Energy Outlook
            to query for data.
        scen_elec (str): The desired AEO "case" or scenario to query.

    Returns:
        Updated EMM conversion factors dict to be exported to the
        conversions JSON.
    """

    dq = EIAQueries(aeo_yr, scen_elec)
    z, yrs = data_getter(api_key, dq.data_names_emm, dq.query_emm,
                         dq.data_table_ids_emm)
    # Set the year of AEO cost data (assume convention of using year before AEO year persists)
    aeo_cost_yr = int(aeo_yr) - 1

    # Emissions conversion factor from short tons to metric tons
    conv_factor = 0.90718474

    for key, value in ValidQueries().regions_dict.items():

        # Electricity CO2 intensities [Mt CO2/MWh]
        try:
            co2_ints = ((z['elec_co2_total_' + key].astype('float') * conv_factor) /
                        # account for T&D losses by multiplying sales by 5%
                        (z['elec_sales_total_' + key].astype('float') * 1.05))
            for idx, year in enumerate(yrs):
                conv['CO2 intensity of electricity'][
                    'data'][value][year] = (
                    round(co2_ints[idx], 6))
            # Ensure years are ordered chronologically
            conv['CO2 intensity of electricity']['data'][value] = (
                OrderedDict(sorted(conv['CO2 intensity of electricity'][
                    'data'][value].items())))
        except KeyError:
            print('\nDue to failed data retrieval from the API, '
                  'electricity CO2 emissions intensities were '
                  'not updated.')

        # Residential electricity prices [$/kWh site]
        try:
            for idx, year in enumerate(yrs):
                conv['End-use electricity price']['data']['residential'][
                    value][year] = (round((z['elec_enduse_price_res_' + key][
                        idx].astype('float') / 100), 6))
            # Ensure years are ordered chronologically
            conv['End-use electricity price']['data']['residential'][value] = (
                OrderedDict(sorted(conv['End-use electricity price']['data'][
                    'residential'][value].items())))

        except KeyError:
            print('\nDue to failed data retrieval from the API, residential '
                  'electricity prices were not updated.')

        # Commercial electricity prices [$/kWh site]
        try:
            for idx, year in enumerate(yrs):
                conv['End-use electricity price']['data']['commercial'][value][
                    year] = (round((z['elec_enduse_price_com_' + key][
                                idx].astype('float') / 100), 6))
            # Ensure years are ordered chronologically
            conv['End-use electricity price']['data']['commercial'][value] = (
                OrderedDict(sorted(conv['End-use electricity price']['data'][
                    'commercial'][value].items())))

        except KeyError:
            print('\nDue to failed data retrieval from the API, commercial '
                  'electricity prices were not updated.')
        # Reset cost units
        conv['End-use electricity price']['units'] = (str(aeo_cost_yr) + "$/kWh site")

    return conv


def updater_state(conv_emm, aeo_min, conv_gas):
    """Perform calculations using EIA data to generate state conversion
    factors JSON.

    Using state-level emissions and prices baseline data from EIA and
    EMM-level projections in these metrics through 2050, as well as
    EMM-level to state-level mapping factors, generate projections in
    conversion factors for all contiguous US states.

    Args:
        conv_emm (dict): Data structure from conversion JSON data file
            populated with EMM region-structured conversion values.
        aeo_min (str): Minimum (earliest) AEO data output year.
        conv_gas (dict): National residential and commercial gas price forecasts
            (used to project forward current state-level gas prices).

    Returns:
        State-level conversion factors dict to be exported to JSON.
    """

    # Convert EIA present-day gas prices from $/MCF to $/MMBtu (used in Scout forecast)
    mcf_mmbtu = (1 / 1.038)

    # Check if any state_baseline_data is available;
    # if no data file exists, prompt user to run
    # state_baseline_data_updater.py to create one
    # if multiple exist, ask user to specify year of data file
    if not UsefulVars().state_baseline_files:
        print('\nNo state baseline data available. Please run '
              'state_baseline_data_updater.py to create one.')
        sys.exit(1)
    elif len(UsefulVars().state_baseline_files) > 1:
        print("Multiple state baseline data files found:")
        for i, file in enumerate(UsefulVars().state_baseline_files, start=1):
            print(f"{i}: {file}")
        while True:
            try:
                file_index = int(input("Enter the number of the file to "
                                       "use: "))
                if 1 <= file_index <= len(UsefulVars().state_baseline_files):
                    state_baseline_data = UsefulVars().state_baseline_files[
                        file_index - 1]
                    break
                else:
                    print("Invalid input. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    else:
        state_baseline_data = UsefulVars().state_baseline_files[0]

    # Load and clean state baselines data from CSV
    # Drop AK and HI and rename columns
    state_baselines = pd.read_csv(state_baseline_data).set_index('State')
    # Find the year of current snapshot data and ensure it is later than the AEO minimum year (AEO
    # year range is used to project state-level emissions and costs)
    anchor_yr = state_baselines["Year"].iloc[0]
    if anchor_yr < int(aeo_min):
        anchor_yr = aeo_min
    else:
        anchor_yr = str(anchor_yr)

    # Load and clean EMM to State mapping file
    emm_state_map = pd.read_csv(UsefulVars().emm_state_map,
                                delimiter="\t").dropna(
        axis=0).set_index('EMM').drop(
        ['AK', 'HI'], axis=1).sort_index()

    # Create dataframe of EMM emissions ratios from base year through 2050
    # Get EMM emissions factors from EMM conversion file
    emm_co2 = pd.DataFrame.from_dict(
        conv_emm['CO2 intensity of electricity']['data'], orient='index')
    # Divide each year in dataframe by base year
    emm_co2_ratios = emm_co2.iloc[:, 1:].div(emm_co2[aeo_min], axis=0)
    # Re-insert base year into new dataframe
    emm_co2_ratios.insert(0, aeo_min, '')
    emm_co2_ratios[aeo_min] = 1.0

    # Create dataframe of EMM price ratios for base year through 2050
    # Get prices from EMM conversion file
    emm_price_res = pd.DataFrame.from_dict(
        conv_emm['End-use electricity price']['data']['residential'],
        orient='index')
    emm_price_com = pd.DataFrame.from_dict(
        conv_emm['End-use electricity price']['data']['commercial'],
        orient='index')
    # Divide each year in dataframe by base year
    emm_price_res_ratios = emm_price_res.iloc[:, 1:].div(
        emm_price_res[aeo_min], axis=0)
    emm_price_com_ratios = emm_price_com.iloc[:, 1:].div(
        emm_price_com[aeo_min], axis=0)
    # Re-insert base year into new dataframe
    emm_price_res_ratios.insert(0, aeo_min, '')
    emm_price_res_ratios[aeo_min] = 1.0
    emm_price_com_ratios.insert(0, aeo_min, '')
    emm_price_com_ratios[aeo_min] = 1.0

    # Generate state factors using baseline state data and
    # projections based on EMM trends (base year ratios),
    # weighted using EMM to State mapping factors

    # Emissions
    state_co2 = {state:
                 {yr: np.average(emm_co2_ratios.loc[:, yr],
                                 weights=emm_state_map.loc[:, state]) for
                  yr in emm_co2_ratios.columns} for
                 state in emm_state_map.columns}
    state_co2_proj = {state:
                      {yr: state_co2[state][yr] *
                       state_baselines.loc[state,
                       'Emissions Rate (Mt/TWh)'] for
                       yr in emm_co2_ratios.columns} for
                      state in state_co2.keys()}

    # Prices - residential electric and gas
    state_elec_price_res = {state:
                            {yr: np.average(emm_price_res_ratios.loc[:, yr],
                                            weights=emm_state_map.loc[:, state]) for
                             yr in emm_price_res_ratios.columns} for
                            state in emm_state_map.columns}
    state_elec_price_res_proj = {state:
                                 {yr: state_elec_price_res[state][yr] *
                                  state_baselines.loc[state,
                                  'Residential Electricity Price ($/kWh)'] for
                                  yr in emm_price_res_ratios.columns} for
                                 state in state_elec_price_res.keys()}
    # Ensure that gas price trends do not apply to years before/leading up to anchor year
    state_gas_price_res = {yr: (conv_gas["residential"][yr] / conv_gas["residential"][anchor_yr])
                           if int(yr) > int(anchor_yr) else 1 for yr
                           in conv_gas["residential"].keys()}
    state_gas_price_res_proj = {state:
                                {yr: state_gas_price_res[yr] * state_baselines.loc[state,
                                 'Residential Gas Price ($/MCF)'] * mcf_mmbtu for
                                 yr in state_gas_price_res.keys()} for
                                state in state_baselines.index}

    # Prices - commercial electric and gas
    state_elec_price_com = {state:
                            {yr: np.average(emm_price_com_ratios.loc[:, yr],
                                            weights=emm_state_map.loc[:, state]) for
                             yr in emm_price_com_ratios.columns} for
                            state in emm_state_map.columns}
    state_elec_price_com_proj = {state:
                                 {yr: state_elec_price_com[state][yr] *
                                  state_baselines.loc[state,
                                  'Commercial Electricity Price ($/kWh)'] for
                                  yr in emm_price_com_ratios.columns} for
                                 state in state_elec_price_com.keys()}
    # Ensure that gas price trends do not apply to years before/leading up to anchor year
    state_gas_price_com = {yr: (conv_gas["commercial"][yr] / conv_gas["commercial"][anchor_yr])
                           if int(yr) > int(anchor_yr) else 1 for yr
                           in conv_gas["commercial"].keys()}
    state_gas_price_com_proj = {state:
                                {yr: state_gas_price_com[yr] * state_baselines.loc[state,
                                 'Commercial Gas Price ($/MCF)'] * mcf_mmbtu for
                                 yr in state_gas_price_com.keys()} for
                                state in state_baselines.index}

    # Update data fields to store state factors
    conv_emm['CO2 intensity of electricity']['data'] = state_co2_proj
    conv_emm['CO2 intensity of electricity']['source'] = (
        'Base year (' + anchor_yr + ') data from EIA State Electricity Data website, '
        'projected to 2050 using sales-weighted average AEO trends in '
        'CO2 intensity for EMM regions that comprise a given state.')
    conv_emm['End-use electricity price']['data']['residential'] = \
        state_elec_price_res_proj
    conv_emm['End-use electricity price']['data']['commercial'] = \
        state_elec_price_com_proj
    conv_emm['End-use electricity price']['units'] = (str(anchor_yr) + "$/kWh site")
    conv_emm['End-use electricity price']['source'] = (
        'Base (' + anchor_yr + ') data from EIA State Electricity Data website, '
        'projected to 2050 using sales-weighted average AEO trends in '
        'residential and commercial electricity prices for EMM regions '
        'that comprise a given state.')
    conv_emm['End-use gas price'] = {
        "data": {
            "residential": state_gas_price_res_proj,
            "commercial": state_gas_price_com_proj},
        "source": (
            'Base year (' + anchor_yr + ') data from EIA Natural Gas Annual, '
            'projected to 2050 using national AEO trends in '
            'residential and commercial gas prices.'),
        "units": (anchor_yr + "$/MMBtu site")}

    return conv_emm


def aeo_min_extract():
    """Get minimum AEO data year based on AEO metadata file

    Returns:
        Year string with the format YYYY corresponding to the earliest
        year of reported AEO data based on the metadata file.
    """
    # Load metadata including AEO year range
    with open(UsefulVars().metadata, 'r') as aeo_yrs:
        try:
            aeo_yrs = json.load(aeo_yrs)
        except ValueError as e:
            raise ValueError(
                "Error reading in '" +
                UsefulVars().metadata + "': " + str(e)) from None
    # Get minimum AEO modeling year
    aeo_min = aeo_yrs["min year"]

    return aeo_min


def main():
    """Main function calls to generate updated conversion files"""

    # Get API key from available environment variables
    if 'EIA_API_KEY' in os.environ:
        api_key = os.environ['EIA_API_KEY']
    else:
        print('\nExpected environment variable EIA_API_KEY not set.\n'
              'Obtain an API key from EIA at https://www.eia.gov/opendata/\n'
              'On a Mac, add the API key to your environment using the '
              'following command in Terminal (and then open a new window).'
              'For bash:'
              "$ echo 'export EIA_API_KEY=your api key' >> ~/.bash_profile\n"
              'For zsh:'
              "$ echo 'export EIA_API_KEY=your api key' >> ~/.zshrc\n")
        sys.exit(1)

    # Add arguments for the name of the file to be updated and the AEO
    # year and scenario to use for the update
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', required=True,
                        help="Name of file to be updated, without the path.")
    parser.add_argument('-y',
                        help="Desired AEO publication year")
    parser.add_argument('-s_e',
                        help="Desired AEO electricity scenario in given year")
    parser.add_argument('-s_g',
                        help="Desired AEO fossil scenario in given year")
    opts = parser.parse_args()

    # Determine what file type is being updated based on the file name;
    # only allow users to specify the emm_region_* and site_source_co2_*
    # files, with the state emissions factors updated automatically
    if opts.f.startswith('emm'):
        geography = 'regional'
    elif opts.f.startswith('site_source'):
        geography = 'national'
    else:
        print('The file name provided does not correspond to an expected '
              'conversion file.')

    # Set state conversion file to use on the basis of the emm file name
    state_conv_file = opts.f.replace("emm_region_emissions", "state_emissions")

    # If not provided as a command-line argument, ask the user to
    # specify the desired report year, informing the user about
    # the valid year options
    if opts.y is not None:
        year = opts.y
    else:  # Year not provided as command line argument
        while opts.y is None:
            year = input('Please specify the desired AEO year. '
                         'Valid entries are: ' +
                         ', '.join(ValidQueries().years) + '.\n')
            if year not in ValidQueries().years:
                print('Invalid year entered.')
            else:
                break

    # If not provided as a command-line argument, ask the user to specify the desired AEO case or
    # scenario, allowing for different scenarios to be used for electricity vs. fossil fuels,
    # and informing the user about the valid scenario options
    # Electricity
    if opts.s_e is not None:
        scenario_elec = opts.s_e
    else:  # Scenario not provided as command line argument
        while opts.s_e is None:
            scenario_elec = input('Please specify the desired AEO electricity scenario. '
                                  'Valid entries are: ' +
                                  ', '.join(ValidQueries().cases[year]) + '.\n')
            if scenario_elec not in ValidQueries().cases[year]:
                print('Invalid scenario entered.')
            else:
                break
    # Fossil fuels
    if opts.s_g is not None:
        scenario_gas = opts.s_g
    else:  # Scenario not provided as command line argument
        while opts.s_g is None:
            scenario_gas = input('Please specify the desired AEO fossil fuel scenario. '
                                 'Valid entries are: ' +
                                 ', '.join(ValidQueries().cases[year]) + '.\n')
            if scenario_gas not in ValidQueries().cases[year]:
                print('Invalid scenario entered.')
            else:
                break

    # Get year of earliest AEO data
    aeo_min = aeo_min_extract()

    # Import file contents for the EMM file
    conv = json.load(open(fp.CONVERT_DATA / opts.f, 'r'))
    # Import file contents for the state file
    conv_state = json.load(open(fp.CONVERT_DATA / state_conv_file, 'r'))

    # Update routine specific to whether user is updating site-to-source
    # file or regional emission/price projections file
    if geography == 'national':
        # Set calculation method
        method_text = conv['site-source calculation method']

        print('\nATTENTION: SITE-SOURCE CONVERSIONS FOR ELECTRICITY '
              'WILL BE CALCULATED USING THE ' + method_text.upper() +
              ' METHOD.')

        if opts.f.endswith('web.json'):
            make_web_version = True
        else:
            make_web_version = False

        # Change conversion factors dict imported from JSON to OrderedDict
        # so that the AEO year and scenario specified by the user can be
        # added with the indicated keys to the beginning of the file
        conv = OrderedDict(conv)
        conv['updated_to_aeo_year'] = year
        # List scenarios user has specified for electricity vs. fossil fuels
        conv['updated_to_aeo_case'] = {"fossil fuels": scenario_gas, "electricity": scenario_elec}
        conv.move_to_end('updated_to_aeo_case', last=False)
        conv.move_to_end('updated_to_aeo_year', last=False)

        # Update site-source and CO2 emissions conversions
        conv = updater(conv, api_key, year, scenario_elec, scenario_gas, make_web_version)

        # Exclude years that are not covered in AEO metadata year range
        fuels = ['CO2 price', 'electricity', 'natural gas', 'propane',
                 'distillate']
        metrics = ['CO2 intensity', 'site to source conversion', 'price']
        bldgs = ['residential', 'commercial']
        for fuel in fuels:
            for metric in metrics:
                for bldg in bldgs:
                    for year_remove in list(conv['CO2 price']['data'].keys()):
                        if int(year_remove) < aeo_min:
                            conv['CO2 price']['data'].pop(year_remove)
                    for year_remove in list(conv[fuels[1]][
                                            'site to source conversion'][
                                            'data'].keys()):
                        if int(year_remove) < aeo_min:
                            conv[fuels[1]]['site to source conversion'][
                                           'data'].pop(year_remove)
                    try:
                        for year_remove in list(conv[fuel][
                                         metric]['data'][bldg].keys()):
                            if int(year_remove) < aeo_min:
                                conv[fuel][metric]['data'][
                                                    bldg].pop(year_remove)
                    except KeyError:
                        pass

        # Output modified site-source and CO2 emissions conversion data
        with open(fp.CONVERT_DATA / opts.f, 'w') as js_out:
            json.dump(conv, js_out, indent=2)

        # Warn user that source fields need to be updated manually
        print('\nWARNING: THE SOCIAL COST OF CARBON AND ALL "source" AND '
              '"units" FIELDS IN THE CONVERSIONS JSON ARE NOT UPDATED '
              'BY THIS FUNCTION. PLEASE UPDATE THOSE FIELDS MANUALLY.\n')

    else:
        # If the year is not in emm_years, stop execution because the
        # EMM data will not have the expected 25 EMM regions
        if year not in ValidQueries().emm_years:
            raise ValueError('Year specified does not match valid EMM years')

        # Exclude years that are not covered in AEO metadata year range
        metrics = ['CO2 intensity of electricity', 'End-use electricity price']
        bldgs = ['residential', 'commercial']
        for bldg in bldgs:
            for reg in list(conv[metrics[0]]['data'].keys()):
                try:
                    for year_remove in list(conv[metrics[0]]['data'][
                                    reg].keys()):
                        if int(year_remove) < aeo_min:
                            conv[metrics[0]]['data'][reg].pop(year_remove)
                except KeyError:
                    for year_remove in list(conv[metrics[1]]['data'][
                                     bldg][reg].keys()):
                        if int(year_remove) < aeo_min:
                            conv[metrics[1]]['data'][
                                                  bldg][reg].pop(year_remove)

        # Change conversion factors dict imported from JSON to OrderedDict
        # so that the AEO year and scenario specified by the user can be
        # added with the indicated keys to the beginning of the file
        conv = OrderedDict(conv)
        conv['updated_to_aeo_year'] = year
        # List scenarios user has specified for electricity vs. fossil fuels
        conv['updated_to_aeo_case'] = {"fossil fuels": scenario_gas, "electricity": scenario_elec}
        conv.move_to_end('updated_to_aeo_case', last=False)
        conv.move_to_end('updated_to_aeo_year', last=False)

        print('\nUpdating EMM region CO2 emissions and prices '
              'conversion factors.')

        # Update EMM region emissions and electricity price factors
        conv_emm = updater_emm(conv, api_key, year, scenario_elec)

        # Pull national gas price projections for use in trending current state-level prices
        # subsequently through 2050
        conv_gas = {"residential": {}, "commercial": {}}
        conv_gas = updater_gastrend(conv_gas, api_key, year, scenario_gas)

        # Output updated EMM emissions/price projections data
        with open(fp.CONVERT_DATA / opts.f, 'w') as js_out:
            json.dump(conv_emm, js_out, indent=5)

        # Update state emissions data
        print('\nUpdating state CO2 emissions and prices.')
        # Fully replace state emissions and electricity prices
        conv_state = updater_state(conv_emm, str(aeo_min), conv_gas)

        # Output updated state emissions/price projections data
        with open(fp.CONVERT_DATA / state_conv_file, 'w') as js_out:
            json.dump(conv_state, js_out, indent=2)


if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""Module for updating supporting emissions and prices files with Cambium data.

This module can be used to update annual and hourly electricity CO2 intensities for varying
electricity system scenarios using data from the NREL Cambium database, available at:
https://scenarioviewer.nrel.gov/. Cambium documentation for 2023 is available at:
https://www.nrel.gov/docs/fy24osti/88507.pdf.

This module will update the following metrics for a given Cambium grid
scenario:

    1) Annual average electricity CO2 emissions rates of generation induced by end-use load at the
    U.S. national scale, or for the EIA's 25 2020 EMM regions, or for U.S. states.

    2) Scaling fractions representing:
        a) The shape of hourly average electricity CO2 emissions rates of generation induced by a
        region's end-use load at the EIA's 25 2020 EMM region scale.
        b) The shape of hourly marginal end-use electricity costs, inclusive of energy, capacity,
        operating reserve, and policy costs.

    In both cases, the fractions are calculated as the ratio of the hourly value to the annual
    average in each EMM region in each year.

The module gives users the option to specify a Cambium scenario for which to output updated data.
For the annual emissions rates, it gives the option to specify whether to update these data at the
U.S. national or EMM region geographical resolution.

This module leaves intact any data in the input JSON files that have been updated with the
converter.py module, which is used to query the EIA AEO API to update annual emissions and
site-source factors, as well as retail electricity prices, using AEO data.

The intended workflow for running this module with other routines is as follows:

1) Run ./scout/state_baseline_data_updater.py to update the current snapshots of state-level
emissions and energy prices from EIA's survey data (via the API). The result will be written to the
file ./scout/supporting_data/convert_data/EIA_State_Emissions_Prices_Baselines_*.csv, where *
indicates the year of the data.

2) Run ./scout/converter.py separately to update each of the files beginning with "emm_region_"
or "site_source in ./scout/supporting_data/convert_data, which will update all of the annual average
emissions intensity, energy price, and site-source conversion values to reflect AEO projections
pulled from the EIA API. For energy prices, electricity and gas prices are both broken out in the
"state_" files, while only electricity prices are broken out in the "emm_region_" files. Electricity
emissions intensities are also broken out in both of those files. Also note that updating the
"emm_region_" files will automatically update the files beginning "state_" as well. When prompted,
select the latest AEO year available and use the following mapping between AEO case and the
scenarios indicated in the file names being updated: lowmaclowZTC -> files with "-100by2035" and
"-95by2050"; ref2023 -> all other files. Users may also enter pairs of scenarios, separated by a
comma, that represent high gas/low electric price and low gas/high electric price futures, as
follows: 'lowogs, lowmaclowZTC', 'highogs, highmachighZTC'.

3) Run ./scout/cambium_updater.py separately to update each of the files beginning with
"emm_region_" or "state" and including the scenarios "-MidCase" "95by2050" and "-100by2035" from
reflecting AEO trends in the EMM- or state-level annual emissions intensity values to reflecting
trends from the relevant Cambium scenario. This routine will also update hourly emissions and
price scaling factors that are used in Scout for time-sensitive valuation of these variables.
Cambium data are downloaded from https://scenarioviewer.nrel.gov/ to a folder that this routine
reads in from, see prompts in routine for instructions about how to structure that folder, and use
the latest available Cambium year when prompted.

"""

import pandas as pd
import json
import gzip
import re
from pathlib import Path
from scout.config import FilePaths as fp


class UsefulInputFiles(object):
    """Class of input file paths to be used by this routine.

    Attributes:
        ba_emm_map (Path): File containing mapping of EMM regions to Cambium BA
        ss_ref (Path): Site-source, emissions, and price data, national
            for AEO Reference Case.
        emm_ref (Path): Emissions and price data, by EMM region,
            for AEO Reference Case.
        state_ref (Path): Emissions and price data, by State,
            for AEO Reference Case.
        ss_midcase (Path): Site-source, emissions, and price data, national
            for MidCase Cambium scenario.
        ss_95by2050 (Path): Site-source, emissions, and price data, national
            for Decarb95by2050 Cambium scenario.
        ss_100by2035 (Path): Site-source, emissions, and price data, national
            for Decarb100by2035 Cambium scenario.
        emm_midcase (Path): Emissions and price data, by EMM region,
            for MidCase Cambium scenario.
        emm_95by2050 (Path): Emissions and price data, by EMM region,
            for Decarb95by2050 Cambium scenario.
        emm_100by2035 (Path): Emissions and price data, by EMM region,
            for Decarb100by2035 Cambium scenario.
        state_midcase (Path): Emissions and price data, by State,
            for MidCase Cambium scenario.
        state_95by2050 (Path): Emissions and price data, by State,
            for Decarb95by2050 Cambium scenario.
        state_100by2035 (Path): Emissions and price data, by State,
            for Decarb100by2035 Cambium scenario.
        tsv_cost_emm_midcase (Path): Time sensitive electricity price data by
            EMM Region for MidCase Cambium scenario.
        tsv_carbon_emm_midcase (Path): Time sensitive average CO2 emissions by
            EMM Region data for MidCase Cambium scenario.
        tsv_cost_emm_95by2050 (Path): Time sensitive electricity price data by
            EMM Region for Decarb95by2050 Cambium scenario.
        tsv_carbon_emm_95by2050 (Path): Time sensitive average CO2 emissions
            data by EMM Region for Decarb95by2050 Cambium scenario.
        tsv_cost_emm_100by2035 (Path): Time sensitive electricity price data by
            EMM Region for Decarb100by2035 Cambium scenario.
        tsv_carbon_emm_100by2035 (Path): Time sensitive average CO2 emissions
            data by EMM Region for Decarb100by2035 Cambium scenario.
        tsv_cost_state_midcase (Path): Time sensitive electricity price data by
            State for MidCase Cambium scenario.
        tsv_carbon_state_midcase (Path): Time sensitive average CO2 emissions
            data by State for MidCase Cambium scenario.
        tsv_cost_state_95by2050 (Path): Time sensitive electricity price data
            by State for Decarb95by2050 Cambium scenario.
        tsv_carbon_state_95by2050 (Path): Time sensitive average CO2 emissions
            data by State for Decarb95by2050 Cambium scenario.
        tsv_cost_state_100by2035 (Path): Time sensitive electricity price data
            by State for Decarb100by2035 Cambium scenario.
        tsv_carbon_state_100by2035 (Path): Time sensitive average CO2 emissions
            data by State for Decarb100by2035 Cambium scenario.
        state_ref (Path): Emissions and price data, by State,
            for AEO Reference Case.
        ss_midcase (Path): Site-source, emissions, and price data, national
            for MidCase Cambium scenario.
        ss_95by2050 (Path): Site-source, emissions, and price data, national
            for Decarb95by2050 Cambium scenario.
        ss_100by2035 (Path): Site-source, emissions, and price data, national
            for Decarb100by2035 Cambium scenario.
        emm_midcase (Path): Emissions and price data, by EMM region,
            for MidCase Cambium scenario.
        emm_95by2050 (Path): Emissions and price data, by EMM region,
            for Decarb95by2050 Cambium scenario.
        emm_100by2035 (Path): Emissions and price data, by EMM region,
            for Decarb100by2035 Cambium scenario.
        state_midcase (Path): Emissions and price data, by State,
            for MidCase Cambium scenario.
        state_95by2050 (Path): Emissions and price data, by State,
            for Decarb95by2050 Cambium scenario.
        state_100by2035 (Path): Emissions and price data, by State,
            for Decarb100by2035 Cambium scenario.
        tsv_cost_emm_midcase (Path): Time sensitive electricity price data by
            EMM Region for MidCase Cambium scenario.
        tsv_carbon_emm_midcase (Path): Time sensitive average CO2 emissions by
            EMM Region data for MidCase Cambium scenario.
        tsv_cost_emm_95by2050 (Path): Time sensitive electricity price data by
            EMM Region for Decarb95by2050 Cambium scenario.
        tsv_carbon_emm_95by2050 (Path): Time sensitive average CO2 emissions
            data by EMM Region for Decarb95by2050 Cambium scenario.
        tsv_cost_emm_100by2035 (Path): Time sensitive electricity price data by
            EMM Region for Decarb100by2035 Cambium scenario.
        tsv_carbon_emm_100by2035 (Path): Time sensitive average CO2 emissions
            data by EMM Region for Decarb100by2035 Cambium scenario.
        tsv_cost_state_midcase (Path): Time sensitive electricity price data by
            State for MidCase Cambium scenario.
        tsv_carbon_state_midcase (Path): Time sensitive average CO2 emissions
            data by State for MidCase Cambium scenario.
        tsv_cost_state_95by2050 (Path): Time sensitive electricity price data
            by State for Decarb95by2050 Cambium scenario.
        tsv_carbon_state_95by2050 (Path): Time sensitive average CO2 emissions
            data by State for Decarb95by2050 Cambium scenario.
        tsv_cost_state_100by2035 (Path): Time sensitive electricity price data
            by State for Decarb100by2035 Cambium scenario.
        tsv_carbon_state_100by2035 (Path): Time sensitive average CO2 emissions
            data by State for Decarb100by2035 Cambium scenario.
        file_paths (dict): Dictionary of file paths to be updated.
    """

    def __init__(self):
        # Set the path to the file that maps Cambium BA regions to EMM regions
        self.ba_emm_map = fp.CONVERT_DATA / "geo_map" / "scout_reeds_emm_mapping_071325.csv"
        # Set the path to the national site-source conversions file
        # for the AEO Reference Case
        self.ss_ref = fp.CONVERT_DATA / "site_source_co2_conversions.json"
        self.emm_ref = fp.CONVERT_DATA / "emm_region_emissions_prices.json"
        self.state_ref = fp.CONVERT_DATA / "state_emissions_prices.json"
        # Set the path to the national site-source conversions file
        # for all Cambium scenarios
        self.ss_midcase = fp.CONVERT_DATA / "site_source_co2_conversions-MidCase.json"
        self.ss_95by2050 = fp.CONVERT_DATA / "site_source_co2_conversions-95by2050.json"
        self.ss_100by2035 = fp.CONVERT_DATA / "site_source_co2_conversions-100by2035.json"
        # Set the path to the EMM region CO2 emissions intensities
        # and price data for all Cambium scenarios
        self.emm_midcase = fp.CONVERT_DATA / "emm_region_emissions_prices-MidCase.json"
        self.emm_95by2050 = fp.CONVERT_DATA / "emm_region_emissions_prices-95by2050.json"
        self.emm_100by2035 = fp.CONVERT_DATA / "emm_region_emissions_prices-100by2035.json"
        # Set the path to the State CO2 emissions intensities
        # and price data for all Cambium scenarios
        self.state_midcase = fp.CONVERT_DATA / "state_emissions_prices-MidCase.json"
        self.state_95by2050 = fp.CONVERT_DATA / "state_emissions_prices-95by2050.json"
        self.state_100by2035 = fp.CONVERT_DATA / "state_emissions_prices-100by2035.json"
        # Set the path to the hourly EMM Region emissions/price scaling factors
        # for all Cambium scenarios
        self.tsv_cost_emm_midcase = fp.TSV_DATA / "tsv_cost-emm-MidCase.gz"
        self.tsv_carbon_emm_midcase = fp.TSV_DATA / "tsv_carbon-emm-MidCase.gz"
        self.tsv_cost_emm_95by2050 = fp.TSV_DATA / "tsv_cost-emm-95by2050.gz"
        self.tsv_carbon_emm_95by2050 = fp.TSV_DATA / "tsv_carbon-emm-95by2050.gz"
        self.tsv_cost_emm_100by2035 = fp.TSV_DATA / "tsv_cost-emm-100by2035.gz"
        self.tsv_carbon_emm_100by2035 = fp.TSV_DATA / "tsv_carbon-emm-100by2035.gz"
        # Set the path to the hourly State emissions/price scaling factors
        # for all Cambium scenarios
        self.tsv_cost_state_midcase = fp.TSV_DATA / "tsv_cost-state-MidCase.gz"
        self.tsv_carbon_state_midcase = fp.TSV_DATA / "tsv_carbon-state-MidCase.gz"
        self.tsv_cost_state_95by2050 = fp.TSV_DATA / "tsv_cost-state-95by2050.gz"
        self.tsv_carbon_state_95by2050 = fp.TSV_DATA / "tsv_carbon-state-95by2050.gz"
        self.tsv_cost_state_100by2035 = fp.TSV_DATA / "tsv_cost-state-100by2035.gz"
        self.tsv_carbon_state_100by2035 = fp.TSV_DATA / "tsv_carbon-state-100by2035.gz"
        # Create a dictionary of the paths to the data files to be
        # updated
        self.file_paths = {
            'ss': {
                'Ref': self.ss_ref,
                'MidCase': self.ss_midcase,
                'Decarb95by2050': self.ss_95by2050,
                'Decarb100by2035': self.ss_100by2035
            },
            'emm': {
                'Ref': self.emm_ref,
                'MidCase': self.emm_midcase,
                'Decarb95by2050': self.emm_95by2050,
                'Decarb100by2035': self.emm_100by2035
            },
            'state': {
                'Ref': self.state_ref,
                'MidCase': self.state_midcase,
                'Decarb95by2050': self.state_95by2050,
                'Decarb100by2035': self.state_100by2035
            },
            'tsv': {
                'emm': {
                    'cost': {
                        'MidCase': self.tsv_cost_emm_midcase,
                        'Decarb95by2050': self.tsv_cost_emm_95by2050,
                        'Decarb100by2035': self.tsv_cost_emm_100by2035
                    },
                    'carbon': {
                        'MidCase': self.tsv_carbon_emm_midcase,
                        'Decarb95by2050': self.tsv_carbon_emm_95by2050,
                        'Decarb100by2035': self.tsv_carbon_emm_100by2035
                    }
                },
                'state': {
                    'cost': {
                        'MidCase': self.tsv_cost_state_midcase,
                        'Decarb95by2050': self.tsv_cost_state_95by2050,
                        'Decarb100by2035': self.tsv_cost_state_100by2035
                    },
                    'carbon': {
                        'MidCase': self.tsv_carbon_state_midcase,
                        'Decarb95by2050': self.tsv_carbon_state_95by2050,
                        'Decarb100by2035': self.tsv_carbon_state_100by2035
                    }
                }
            }
        }


class ValidQueries(object):
    """Define valid query options for Cambium data.

    Attributes:
        years (list): A list of valid Cambium data years for which this
            module has been evaluated to work.
        scenarios (list): A list of valid Cambium scenarios,
            which are available for updating annual (national or EMM region)
            or hourly emissions and price data.
    """

    def __init__(self, scenario=None):
        self.scenarios = ['MidCase', 'Decarb95by2050',
                          'Decarb100by2035']
        # Cambium 2024 data are only available for MidCase
        if scenario == "MidCase":
            self.years = ['2022', '2023', '2024']
        else:
            self.years = ['2022', '2023']


def import_ba_emm_mapping():
    """Import Cambium data and concatenate files into single data frame.

    Returns:
        Mapping csv file that is used to map Cambium BA regions to 2020 EIA EMM
        regions.
    """
    # Scout <> ReEDS <> EMM2020
    mapping = pd.read_csv(UsefulInputFiles().ba_emm_map)
    # set ba column to str
    mapping['cambium_24_ba'] = 'p' + mapping['cambium_24_ba'].astype(str)
    # select relevant columns
    mapping = mapping.drop_duplicates(
        subset=['cambium_24_ba'])[[
            'cambium_24_ba', 'EMM_2020', 'state_abbrev']].reset_index(
        drop=True)
    # change name of BASIN to BASN
    mapping['EMM_2020'] = mapping.apply(
        lambda x: 'BASN' if x['EMM_2020'] == 'BASIN' else x['EMM_2020'],
        axis=1)
    return mapping


def cambium_data_import(cambium_base_dir, year, scenario):
    """Import Cambium data and concatenate files into single data frame.

    Args:
        scenario (str): Cambium scenario ['MidCase', 'Decarb95by2050',
                                          'Decarb100by2035'].
        year (str): Cambium data year.

    Returns:
        Data frame of all Cambium data for specified scenario,
        year (every 2 years through 2050),
        and region (Cambium Balancing Authority)
    """
    # create list of files
    files = list(Path(cambium_base_dir, year, scenario).glob("*20*.csv"))
    # create df from multiple CSVs in working directory and assign new 'ba'
    # column to appropriate file name; parse dates with datetime
    ba_df = pd.concat(
        map(lambda file: pd.read_csv(
            str(file.resolve()), parse_dates=['timestamp', 'timestamp_local'],
            header=5).assign(
                # extract "pXX" from file name and assign to ba
                ba=re.search(r'p\d+', str(file)).group()), files))
    return ba_df


def annual_factors_updater(df, ss, geography):
    """Update annual CO2 emissions intensities in either national or
       EMM region supporting data files using Cambium data for a given
       scenario.

    Args:
        df (data frame): Data frame of Cambium data mapped to EMM regions
            or states for a given scenario.
        ss (str): Cambium scenario.
        geography (str): Geographic resolution for data aggregation.

    Returns:
        Updated annual conversion factors dict to be exported to the
        conversions JSON.
    """
    # Create conversion factors to convert CO2 rates from kgCO2/MWh to Mt/quad
    kg_to_mt = 1/(1e9)
    mwh_to_quad = 1/(3.4121414798969e-9)
    mwh_to_twh = 1e6
    # Create data frame from which to compute annual CO2 emissions intensities
    # to update supporting data file for a given Cambium scenario.
    # Create new datetime columns
    df['year'] = df.timestamp.dt.year
    # Create new CO2 emissions intensity columns in units of Mt/quad and Mt/TWh
    df['co2_avg_enduse_mt_quad'] = df['aer_load_co2_c'] * kg_to_mt * \
        mwh_to_quad
    df['co2_avg_enduse_mt_twh'] = df['aer_load_co2_c'] * kg_to_mt * \
        mwh_to_twh
    # Group by year and compute annual average co2 intensity using
    # aer_load_co2_c metric
    df_nat = df.groupby(
        ['year'])[['co2_avg_enduse_mt_quad']].mean().reset_index()
    # Set index as year and convert to datetime
    df_nat.set_index('year', inplace=True)
    df_nat.index = pd.to_datetime(df_nat.index, format='%Y')
    # If updating national data, resample to annual and interpolate to get
    # annual factors starting with the most recent year in the Cambium data
    if geography == "National":
        # Create a data frame from loaded supporting data file
        ss_df = pd.DataFrame.from_dict(
            ss['electricity']['site to source conversion']['data'],
            'index')[0].values
        # Resample yearly with linear interpolation and set year as string
        df_resamp = df_nat.resample(
                            'YE').mean().interpolate(
                                method='linear').assign(
                                    year=lambda x: x.index.year.astype(
                                        str)).reset_index(drop=True)
        # Truncate the ss_df array to the length of df_resamp
        index = len(ss_df) - len(df_resamp['co2_avg_enduse_mt_quad'])
        ss_df_trunc = ss_df[index:]
        # Append s2s as a column to df_resamp
        df_resamp['s2s_factor'] = ss_df_trunc
        # Use s2s factor to convert CO2 intensity to site
        df_resamp['co2_avg_enduse_mt_quad'] = \
            df_resamp['co2_avg_enduse_mt_quad'].div(df_resamp['s2s_factor'])
        # Create dictionary of year:value pairs for the national CO2 emissions
        # intensities
        co2_dict = dict(zip(df_resamp['year'],
                            df_resamp['co2_avg_enduse_mt_quad']))
        # Update the national CO2 emissions intensities in the s2s file
        ss['electricity']['CO2 intensity']['data']['residential'].update(
            co2_dict)
        ss['electricity']['CO2 intensity']['data']['commercial'].update(
            co2_dict)
    elif geography == "EMM":
        # Group data frame by EMM region and year and calculate average CO2
        # emissions intensity
        df_reg = df.groupby(
            ['EMM_2020', 'year'])[['co2_avg_enduse_mt_twh']].mean(
            ).reset_index()
        # Set index as year and convert to datetime
        df_reg.set_index(pd.to_datetime(df_reg['year'], format='%Y'),
                         inplace=True)
        # Group by EMM region and resample annually with linear interpolation
        df_resamp = df_reg.groupby(
            'EMM_2020').resample(
            'YE').mean().interpolate(
            method='linear').reset_index(
            level=0).assign(
                year=lambda x: x.index.year.astype(str)).reset_index(
                    drop=True)
        # Create dictionary of year:value pairs for each EMM region
        co2_dict = {emm: {year: value for year, value in zip(group['year'],
                          group['co2_avg_enduse_mt_twh'])}
                    for emm, group in df_resamp.groupby('EMM_2020')}
        # Save final dictionary for output
        {ss['CO2 intensity of electricity']['data'][key].update(val)
         for key, val in co2_dict.items()}
    elif geography == "State":
        # Group data frame by state and year and calculate average CO2
        # emissions intensity
        df_reg = df.groupby(
            ['state_abbrev', 'year'])[['co2_avg_enduse_mt_twh']].mean(
            ).reset_index()
        # Set index as year and convert to datetime
        df_reg.set_index(pd.to_datetime(df_reg['year'], format='%Y'),
                         inplace=True)
        # Group by state and resample annually with linear interpolation
        df_resamp = df_reg.groupby(
            'state_abbrev').resample(
            'YE').mean().interpolate(
            method='linear').reset_index(
            level=0).assign(
                year=lambda x: x.index.year.astype(str)).reset_index(
                    drop=True)
        # Create dictionary of year:value pairs for each EMM region
        co2_dict = {state: {year: value for year, value in zip(group['year'],
                            group['co2_avg_enduse_mt_twh'])}
                    for state, group in df_resamp.groupby('state_abbrev')}
        # Save final dictionary for output
        {ss['CO2 intensity of electricity']['data'][key].update(val)
         for key, val in co2_dict.items()}
    else:
        print('Invalid geography entered.')

    return ss


def generate_hourly_factors(df, geography):
    """Generate hourly CO2 emissions and electricity price scaling
       factors to update supporting data TSV files based on Cambium
       data for a given scenario.

    Args:
        df (data frame): Data frame of Cambium data mapped to EMM regions
            or states for a given scenario.
        geography (str): Geographic resolution for data aggregation.

    Returns:
        Data frame of hourly CO2 emissions and price scaling factors.
    """
    # Create new datetime columns
    df['month'], df['year'], df['day'], df['hour'] = df.timestamp.dt.month, \
        df.timestamp.dt.year, df.timestamp.dt.day, df.timestamp.dt.hour
    # Create list of CO2 and price metrics to use in generating scaling
    # fractions
    metrics = ['aer_load_co2_c', 'total_cost_enduse']
    if geography == "EMM":
        # Calculate EMM region & national annual averages for CO2
        # emissions/price metrics
        reg_ann_avg = df.groupby(
            ['EMM_2020', 'year'])[metrics].mean().reset_index()
        ann_avg = df.groupby(['year'])[metrics].mean().reset_index()
        # Join EMM region & national annual averages to calculate scaling
        # fractions
        scaling = pd.merge(reg_ann_avg, ann_avg, on='year', how='left',
                           suffixes=('_reg_ann_avg', '_ann_avg'))
        # Fix BASIN typo to enable clean join
        scaling['EMM_2020'] = scaling.apply(
            lambda x: 'BASN' if x['EMM_2020'] == 'BASIN' else x['EMM_2020'],
            axis=1)
        # Join scaling fractions to original Cambium data
        df_scaled = pd.merge(df, scaling, on=['EMM_2020', 'year'], how='left')
    elif geography == "State":
        # Calculate state & national annual averages for CO2 emissions/price
        # metrics
        reg_ann_avg = df.groupby(
            ['state_abbrev', 'year'])[metrics].mean().reset_index()
        ann_avg = df.groupby(['year'])[metrics].mean().reset_index()
        # Join EMM region & national annual averages to calculate scaling
        # fractions
        scaling = pd.merge(reg_ann_avg, ann_avg, on='year', how='left',
                           suffixes=('_reg_ann_avg', '_ann_avg'))
        # Join scaling fractions to original Cambium data
        df_scaled = pd.merge(df, scaling, on=['state_abbrev', 'year'],
                             how='left')
    else:
        print('Invalid geography entered.')
    # Create new columns, where hourly values are multiplied by a scaling
    # factor that represents the ratio between the within-region annual
    # average and the national annual average in each year
    df_scaled['electricity price shapes'] = (
        df_scaled['total_cost_enduse'] /
        df_scaled['total_cost_enduse_reg_ann_avg'])
    df_scaled['average carbon emissions rates'] = (
        df_scaled['aer_load_co2_c'] /
        df_scaled['aer_load_co2_c_reg_ann_avg']).fillna(0)
    # Convert year column to string
    df_scaled['year'] = df_scaled['year'].astype(str)
    #
    metrics_names = ['electricity price shapes',
                     'average carbon emissions rates']
    if geography == "EMM":
        # Create data frame with 8760s for each scaled metric by EMM region
        df_reg = df_scaled.groupby(
            ['year', 'month', 'day', 'hour',
             'EMM_2020'])[metrics_names].mean().reset_index()
    elif geography == "State":
        # Create data frame with 8760s for each scaled metric by state
        df_reg = df_scaled.groupby(
            ['year', 'month', 'day', 'hour',
             'state_abbrev'])[metrics_names].mean().reset_index()
    else:
        print('Invalid geography entered.')
    return df_reg


def hourly_factors_updater(df, scenario, year, metric, geography):
    """
    Update existing hourly cost/carbon tsv files with scaling fractions
    from Cambium data for a given scenario.

    Args:
        scenario (str): Cambium scenario ['MidCase', 'Decarb95by2050',
                                          'Decarb100by2035']
        df_reg (data frame): Data frame of hourly emissions and price scaling
            factors from Cambium data for a given scenario, with EMM or state
            resolution.
        geography (str): Geographic resolution for data aggregation.
    Returns:
        Updated hourly conversion factors dict to be exported to the
        conversions JSON.
    """

    if geography == "EMM":
        # Create vars to iterate over
        regions = df['EMM_2020'].unique()
    elif geography == "State":
        # Create vars to iterate over
        regions = df['state_abbrev'].unique()
    else:
        print('Invalid geography entered.')
    # Create vars to iterate over
    data_years = df['year'].unique()
    # Create dictionaries to store results
    dict_regions = dict.fromkeys(regions)
    dict_results = dict.fromkeys(data_years)
    # Create documentation header for json files
    dict_to_write = {}
    metrics_notes = {'cost':
                     'Values represent hourly total cost '
                     'values (sum of energy, capacity, '
                     'operating reserve, and policy costs). '
                     'Values are first averaged across all '
                     'Cambium BA areas that comprise a given '
                     'region and then are normalized by '
                     'the annual average total cost for that '
                     'region.',
                     'carbon':
                     'Values represent the hourly average '
                     'CO2 emissions rate of the generation '
                     'that is allocated to a region’s '
                     'end-use load. This metric includes '
                     'the effects of imported and exported '
                     'power. Values are first averaged across '
                     'all Cambium BA areas that comprise a '
                     'given region and then are normalized '
                     'by the annual average CO2 rate for that region.'}
    # For loop to pull scaling factors for each year and EMM region
    if geography == "EMM":
        for y in data_years:
            for r in regions:
                if metric == 'cost':
                    dict_regions[r] = df[(df['year'] == y) &
                                         (df['EMM_2020'] == r)][
                                         'electricity price shapes'].to_list()
                elif metric == 'carbon':
                    dict_regions[r] = df[
                        (df['year'] == y) &
                        (df['EMM_2020'] == r)][
                        'average carbon emissions rates'].to_list()
                else:
                    print('Invalid metric entered.')
            dict_results[y] = dict_regions
            dict_regions = dict.fromkeys(regions)
    elif geography == "State":
        for y in data_years:
            for r in regions:
                if metric == 'cost':
                    dict_regions[r] = df[(df['year'] == y) &
                                         (df['state_abbrev'] == r)][
                                         'electricity price shapes'].to_list()
                elif metric == 'carbon':
                    dict_regions[r] = df[
                        (df['year'] == y) &
                        (df['state_abbrev'] == r)][
                        'average carbon emissions rates'].to_list()
                else:
                    print('Invalid metric entered.')
            dict_results[y] = dict_regions
            dict_regions = dict.fromkeys(regions)
    dict_to_write['Source Data'] = {'Title': 'Cambium data for Standard '
                                    'Scenarios',
                                    'Year': year,
                                    'Updated to Scenario': scenario,
                                    'author': 'Gagnon, Pieter; Cowiestoll, '
                                    'Brady; Schwarz, Marty',
                                    'organization': 'National Renewable '
                                    'Energy Laboratory',
                                    'link': 'https://cambium.nrel.gov/',
                                    'notes': metrics_notes[metric]}
    if metric == 'cost':
        dict_to_write['electricity price shapes'] = dict_results
    elif metric == 'carbon':
        dict_to_write['average carbon emissions rates'] = dict_results
    else:
        print('Invalid metric entered.')
    return dict_to_write


def main():
    """Main function calls to generate updated supporting files"""

    # Ask the user to specify the file path to downloaded Cambium data
    while True:
        cambium_file_path = input('\nPlease provide the file path to '
                                  'downloaded Cambium data. \n\n'
                                  'Data directory should be structured as: \n'
                                  './Cambium_data/year/scenario/csv_file \n\n '
                                  'where ./Cambium_data is the file path '
                                  'provided and year/scenario are subfolders '
                                  'containing Cambium data files. \n\n'
                                  'This module will subsequently ask you to '
                                  'specify the year and scenario for which '
                                  'to update supporting data files.\n')
        if cambium_file_path == '':
            print('Invalid file path entered.')
        else:
            break
    # Ask the user to specify the desired temporal resolution
    # for which to update and generate factors from Cambium data.
    while True:
        full_update = input('Would you like to update all supporting '
                            'data files for a given Cambium scenario '
                            'and data year? '
                            'Valid entries are: ' +
                            ', '.join(['Yes', 'No']) + '.\n')
        if full_update not in ['Yes', 'No']:
            print('Invalid entry.')
        else:
            break
    if full_update == 'Yes':
        # Ask the user to specify the desired Cambium scenario,
        # informing the user about the valid scenario options
        while True:
            scenario = input('Please specify the desired Cambium scenario. \n'
                             'Valid entries are: ' +
                             ', '.join(ValidQueries().scenarios) + '.\n')
            if scenario not in ValidQueries().scenarios:
                print('Invalid scenario entered.')
            else:
                break
        # Ask the user to specify the desired Cambium data year.
        while True:
            year = input('Please specify the desired Cambium data year. \n'
                         'Valid entries are: ' +
                         ', '.join(ValidQueries(scenario).years) + '.\n')
            if year not in ValidQueries(scenario).years:
                print('Invalid year entered.')
            else:
                break
        # Load Ref Case National supporting data file
        with open(UsefulInputFiles().file_paths['ss']['Ref'], "r") as js:
            ss_nat = json.load(js)
        # Import mapping file to map Cambium BA regions to EMM regions
        ba_emm_map = import_ba_emm_mapping()
        # Notify user that Cambium data are importing
        print('Importing Cambium scenario data...')
        # Import Cambium data for the specified year and scenario
        cambium_df = cambium_data_import(cambium_file_path, year, scenario)
        # Join mapping file to cambium data
        df = pd.merge(cambium_df, ba_emm_map, left_on='ba',
                      right_on='cambium_24_ba', how='left')
        # Notify user that national supporting factors are updating
        print('Updating national annual emissions intensities data...')
        # Update national annual CO2 emissions intensities for annual data for
        # a given Cambium scenario
        ss_updated = annual_factors_updater(df, ss_nat, 'National')
        # Update year and Cambium case keys in dictionary to reflect
        # data updates
        ss_updated['updated_to_cambium_case'] = scenario
        ss_updated['updated_to_cambium_year'] = year
        # Update emissions source notes
        ss_updated["electricity"]["CO2 intensity"]["source"] = \
            "AEO 2025 data through 2024 w/ Cambium projections"
        # Notify user that national supporting factors are writing to file
        print('Writing national annual emissions intensities data to file...')
        # Write national annual CO2 emissions intensities for annual data for
        # a given Cambium scenario to file
        with open(UsefulInputFiles().file_paths['ss'][scenario], 'w') as json_file:
            json.dump(ss_updated, json_file, sort_keys=False, indent=2)
        # Notify user that EMM region supporting factors are updating
        print('Updating EMM region annual emissions intensities data...')
        # Load existing Ref Case EMM region supporting data file
        with open(UsefulInputFiles().file_paths['emm']['Ref'], "r") as js:
            ss_emm = json.load(js)
        # Update EMM region annual CO2 emissions intensities for annual data
        # for a given Cambium scenario
        ss_emm_updated = annual_factors_updater(df, ss_emm, 'EMM')
        # Update year and Cambium case keys in dictionary to reflect
        # data updates
        ss_emm_updated['updated_to_cambium_case'] = scenario
        ss_emm_updated['updated_to_cambium_year'] = year
        # Update emissions source notes
        ss_emm_updated["CO2 intensity of electricity"]["source"] = \
            "AEO 2025 data through 2024 w/ Cambium projections"
        # Notify user that EMM region supporting factors are writing to file
        print('Writing EMM region annual emissions intensities data to file..')
        # Write EMM region annual CO2 emissions intensities for annual data for
        # a given Cambium scenario to file
        with open(UsefulInputFiles().file_paths['emm'][scenario], 'w') as json_file:
            json.dump(ss_emm_updated, json_file, sort_keys=False, indent=2)
        # Notify user that state supporting factors are updating
        print('Updating state annual emissions intensities data...')
        # Load existing Ref Case State supporting data file
        with open(UsefulInputFiles().file_paths['state']['Ref'], "r") as js:
            ss_state = json.load(js)
        # Update State CO2 emissions intensities for annual data
        # for a given Cambium scenario
        ss_state_updated = annual_factors_updater(df, ss_state, 'State')
        # Update year and Cambium case keys in dictionary to reflect
        # data updates
        ss_state_updated['updated_to_cambium_case'] = scenario
        ss_state_updated['updated_to_cambium_year'] = year
        # Update emissions source notes
        ss_state_updated["CO2 intensity of electricity"]["source"] = \
            "AEO 2025 data through 2024 w/ Cambium projections"
        # Notify user that State supporting factors are writing to file
        print('Writing state annual emissions intensities data to file..')
        # Write State annual CO2 emissions intensities for annual data for
        # a given Cambium scenario to file
        with open(UsefulInputFiles().file_paths['state'][scenario], 'w') as json_file:
            json.dump(ss_state_updated, json_file, sort_keys=False, indent=2)
        # Notify user that EMM hourly supporting factors are updating
        print('Updating EMM region hourly emissions and price factors...')
        # Update EMM region hourly CO2 emissions and price scaling factors
        df_hour_emm = generate_hourly_factors(df, 'EMM')
        hourly_cost_json_emm = hourly_factors_updater(df_hour_emm, scenario, year,
                                                      metric='cost',
                                                      geography='EMM')
        hourly_carbon_json_emm = hourly_factors_updater(df_hour_emm, scenario, year,
                                                        metric='carbon',
                                                        geography='EMM')
        # Notify user that hourly supporting factors are writing to file
        print('Writing EMM price scaling factors to file...')
        # # Write hourly price scaling factors to file
        with gzip.open(
            UsefulInputFiles().file_paths['tsv']['emm']['cost'][scenario],
                'wt') as fp:
            json.dump(hourly_cost_json_emm, fp, sort_keys=True, indent=4)
        print('Writing EMM CO2 emissions scaling factors to file...')
        # Write hourly CO2 emissions scaling factors to file
        with gzip.open(
            UsefulInputFiles().file_paths['tsv']['emm']['carbon'][scenario],
                'wt') as fp:
            json.dump(hourly_carbon_json_emm, fp, sort_keys=True, indent=4)
        # Notify user that State hourly supporting factors are updating
        print('Updating state hourly emissions and price factors...')
        # Update state hourly CO2 emissions and price scaling factors
        df_hour_state = generate_hourly_factors(df, 'State')
        hourly_cost_json_state = hourly_factors_updater(df_hour_state, scenario, year,
                                                        metric='cost',
                                                        geography='State')
        hourly_carbon_json_state = hourly_factors_updater(df_hour_state, scenario, year,
                                                          metric='carbon',
                                                          geography='State')
        # Notify user that hourly supporting factors are writing to file
        print('Writing state price scaling factors to file...')
        # Write State hourly price scaling factors to file
        with gzip.open(
            UsefulInputFiles().file_paths['tsv']['state']['cost'][scenario],
                'wt') as fp:
            json.dump(hourly_cost_json_state, fp, sort_keys=True, indent=4)
        print('Writing state CO2 emissions scaling factors to file...')
        # Write State hourly CO2 emissions scaling factors to file
        with gzip.open(
            UsefulInputFiles().file_paths['tsv']['state']['carbon'][scenario],
                'wt') as fp:
            json.dump(hourly_carbon_json_state, fp, sort_keys=True, indent=4)
        print('Update complete.')
    elif full_update == "No":
        while True:
            temporal_res = input('You have selected to update specific '
                                 'supporting files. Please specify which '
                                 'temporal resolution of supporting data '
                                 'to update. '
                                 'Valid entries are: ' +
                                 ', '.join(['Annual', 'Hourly']) + '.\n')
            if temporal_res not in ['Annual', 'Hourly']:
                print('Invalid temporal resolution entered.')
            else:
                break
        if temporal_res == 'Annual':
            # Ask the user to specify the desired update to make, whether
            # to the site_to_source conversions json or EMM region
            # emissions/price projections json or State emissions/price
            # projections.
            while True:
                geography = input('Please specify the desired file type to update. '
                                  'Valid entries are: ' +
                                  ', '.join(['National', 'EMM', 'State']) + '.\n')
                if geography not in ['National', 'EMM', 'State']:
                    print('Invalid file type entered.')
                else:
                    break
        else:
            # Ask the user to specify the desired update to make, whether
            # to the EMM region hourly emissions/price projections json or
            # State emissions/price projections.
            while True:
                geography = input('Please specify the desired file type to update. '
                                  'Valid entries are: ' +
                                  ', '.join(['EMM', 'State']) + '.\n')
                if geography not in ['EMM', 'State']:
                    print('Invalid file type entered.')
                else:
                    break
        # Ask the user to specify the desired Cambium scenario,
        # informing the user about the valid scenario options
        while True:
            scenario = input('Please specify the desired Cambium scenario. '
                             'Valid entries are: ' +
                             ', '.join(ValidQueries().scenarios) + '.\n')
            if scenario not in ValidQueries().scenarios:
                print('Invalid scenario entered.')
            else:
                break
        # Ask the user to specify the desired Cambium data year.
        while True:
            year = input('Please specify the desired Cambium data year. '
                         'Valid entries are: ' +
                         ', '.join(ValidQueries(scenario).years) + '.\n')
            if year not in ValidQueries(scenario).years:
                print('Invalid year entered.')
            else:
                break
        # Update annual CO2 emissions intensities for annual data for a given
        # Cambium scenario
        if temporal_res == "Annual":
            # Load existing national supporting data file for specified
            # scenario
            with open(UsefulInputFiles().file_paths['ss']['Ref'], "r") as js:
                ss_nat = json.load(js)
            # Import mapping file to map Cambium BA regions to EMM regions
            ba_emm_map = import_ba_emm_mapping()
            # Notify user that Cambium data are importing
            print('Importing Cambium scenario data...')
            # Import Cambium data for the specified year and scenario
            cambium_df = cambium_data_import(cambium_file_path, year, scenario)
            # Join mapping file to cambium data
            df = pd.merge(cambium_df, ba_emm_map, left_on='ba',
                          right_on='cambium_24_ba', how='left')
            if geography == "National":
                # Update national annual CO2 emissions intensities for annual
                # data for a given Cambium scenario
                ss_updated = annual_factors_updater(df, ss_nat,
                                                    'National')
                # Update year and Cambium case keys in dictionary to reflect
                # data updates
                ss_updated['updated_to_cambium_case'] = scenario
                ss_updated['updated_to_cambium_year'] = year
                # Notify user that national supporting factors are writing to
                # file
                print(
                    'Writing national annual emissions intensities to file...')
                # Write national annual CO2 emissions intensities for annual
                # data for a given Cambium scenario to file
                with open(UsefulInputFiles().file_paths['ss'][scenario], 'w') as json_file:
                    json.dump(ss_updated, json_file, sort_keys=False, indent=2)
                # Notify user that update is complete.
                print('Update complete.')
            elif geography == "EMM":
                # Notify user that EMM region supporting factors are updating
                print(
                    'Updating EMM region annual emissions intensities data...')
                # Load Ref case EMM region supporting data file for specified
                # scenario
                with open(UsefulInputFiles().file_paths['emm']['Ref'], "r") as js:
                    ss_reg = json.load(js)
                # Update EMM region annual CO2 emissions intensities for annual
                # data for a given Cambium scenario
                ss_updated = annual_factors_updater(df, ss_reg,
                                                    'EMM')
                # Update year and Cambium case keys in dictionary to reflect
                # data updates
                ss_updated['updated_to_cambium_case'] = scenario
                ss_updated['updated_to_cambium_year'] = year
                # Notify user that EMM region factors are writing to file
                print(
                    'Writing EMM region annual emissions intensities to \
                    file...')
                # Write EMM region annual CO2 emissions intensities for annual
                # data for a given Cambium scenario to file
                with open(UsefulInputFiles().file_paths['emm'][scenario], 'w') as json_file:
                    json.dump(ss_updated, json_file, sort_keys=False, indent=2)
                # Notify user that update is complete.
                print('Update complete.')
            elif geography == "State":
                # Notify user that State supporting factors are updating
                print(
                    'Updating state annual emissions intensities data...')
                # Load Reference case State supporting data file for specified
                # scenario
                with open(UsefulInputFiles().file_paths['state']['Ref'], "r") as js:
                    ss_reg = json.load(js)
                # Update State annual CO2 emissions intensities for annual
                # data for a given Cambium scenario
                ss_updated = annual_factors_updater(df, ss_reg,
                                                    'State')
                # Update year and Cambium case keys in dictionary to reflect
                # data updates
                ss_updated['updated_to_cambium_case'] = scenario
                ss_updated['updated_to_cambium_year'] = year
                # Notify user that EMM region factors are writing to file
                print(
                    'Writing state annual emissions intensities to \
                    file...')
                # Write EMM region annual CO2 emissions intensities for annual
                # data for a given Cambium scenario to file
                with open(UsefulInputFiles().file_paths['emm'][scenario], 'w') as json_file:
                    json.dump(ss_updated, json_file, sort_keys=False, indent=2)
                # Notify user that update is complete.
                print('Update complete.')
        else:
            if geography == "EMM":
                # Import mapping file to map Cambium BA regions to EMM regions
                ba_emm_map = import_ba_emm_mapping()
                # Notify user that Cambium data are importing
                print('Importing Cambium scenario data...')
                # Import Cambium data for the specified year and scenario
                cambium_df = cambium_data_import(cambium_file_path, year,
                                                 scenario)
                # Join mapping file to cambium data
                df = pd.merge(cambium_df, ba_emm_map, left_on='ba',
                              right_on='cambium_24_ba', how='left')
                # Notify user that hourly supporting factors are updating
                print('Updating EMM region hourly emissions and price \
                      factors...')
                # Update hourly CO2 emissions and price scaling factors
                df_hour = generate_hourly_factors(df, geography='EMM')
                hourly_cost_json = hourly_factors_updater(df_hour, scenario, year,
                                                          metric='cost',
                                                          geography='EMM')
                hourly_carbon_json = hourly_factors_updater(df_hour, scenario, year,
                                                            metric='carbon',
                                                            geography='EMM')
                # Notify user that hourly supporting factors are writing to
                # file
                print('Writing EMM region price scaling factors to file...')
                # Write hourly price scaling factors to file
                with gzip.open(
                    UsefulInputFiles().file_paths['tsv']['emm']['cost'][scenario],
                        'wt') as fp:
                    json.dump(hourly_cost_json, fp, sort_keys=True, indent=4)
                print('Writing EMM region CO2 emissions scaling factors \
                      to file...')
                # Write hourly CO2 emissions scaling factors to file
                with gzip.open(
                    UsefulInputFiles().file_paths['tsv']['emm']['carbon'][scenario],
                        'wt') as fp:
                    json.dump(hourly_carbon_json, fp, sort_keys=True, indent=4)
                print('Update complete.')
            elif geography == "State":
                # Import mapping file to map Cambium BA regions to States
                ba_emm_map = import_ba_emm_mapping()
                # Notify user that Cambium data are importing
                print('Importing Cambium scenario data...')
                # Import Cambium data for the specified year and scenario
                cambium_df = cambium_data_import(cambium_file_path, year,
                                                 scenario)
                # Join mapping file to cambium data
                df = pd.merge(cambium_df, ba_emm_map, left_on='ba',
                              right_on='cambium_24_ba', how='left')
                # Notify user that hourly supporting factors are updating
                print('Updating hourly emissions and price scaling factors...')
                # Update hourly CO2 emissions and price scaling factors
                df_hour = generate_hourly_factors(df, 'State')
                hourly_cost_json = hourly_factors_updater(df_hour, scenario, year,
                                                          metric='cost',
                                                          geography='State')
                hourly_carbon_json = hourly_factors_updater(df_hour, scenario, year,
                                                            metric='carbon',
                                                            geography='State')
                # Notify user that hourly supporting factors are writing to
                # file
                print('Writing state price scaling factors to file...')
                # Write hourly price scaling factors to file
                with gzip.open(
                    UsefulInputFiles().file_paths['tsv']['state']['cost'][scenario],
                        'wt') as fp:
                    json.dump(hourly_cost_json, fp, sort_keys=True, indent=4)
                print('Writing state CO2 emissions scaling factors to file...')
                # Write hourly CO2 emissions scaling factors to file
                with gzip.open(
                    UsefulInputFiles().file_paths['tsv']['state']['carbon'][scenario],
                        'wt') as fp:
                    json.dump(hourly_carbon_json, fp, sort_keys=True, indent=4)
                print('Update complete.')
    else:
        print('Invalid entry.')


if __name__ == '__main__':
    import time
    start_time = time.time()
    main()
    hours, rem = divmod(time.time() - start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print("--- Runtime: %s (HH:MM:SS.mm) ---" %
          "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

#!/usr/bin/env python3

import json
from collections import OrderedDict
import gzip
from scout.config import FilePaths as fp


class UsefulInputFiles(object):
    """Class of input file paths to be used by this routine.

    Attributes:
        msegs_in (string): Database of baseline microsegment stock/energy.
        msegs_in_emm (string): Same as 'msegs_in' but broken out by EMM region
            instead of AIA climate region.
        msegs_in_state (string): Same as 'msegs_in' but broken out by state
            instead of AIA climate region.
        htcl_totals (string): File name for an output of this module -
            heating and cooling primary energy totals by climate zone,
            building type, and structure type calculated using the
            fossil fuel equivalent method for the site-source
            conversion factors for electricity (the Scout and
            AEO default).
        htcl_totals_decarb (string): File name for an output of this module -
            heating and cooling primary energy totals by climate zone,
            building type, and structure type calculated using the
            fossil fuel equivalent method for the site-source
            conversion factors for electricity (the Scout and
            AEO default), assuming a high degree of grid decarbonization.
        htcl_totals_ce (str): File name for an output of this module -
            heating and cooling primary energy totals by climate zone,
            building type, and structure type calculated using the
            captured energy method, which accounts for the reduced
            losses in source energy derived from renewable generation;
            this approach is derived from the DOE report "Accounting
            Methodology for Source Energy of Non-Combustible Renewable
            Electricity Generation".
        htcl_totals_site (str): File name for an output of this module -
            heating and cooling primary energy totals by climate zone,
            building type, and structure type calculated using site energy,
            thus requiring no conversion from site-source energy.
        htcl_totals_emm (string): Same as 'htcl_totals' but broken out by EMM
            region instead of AIA climate region.
        htcl_totals_emm_decarb (string): Same as 'htcl_totals_decarb' but
            broken out by EMM region instead of AIA climate region.
        htcl_totals_ce_emm (str): Same as 'htcl_totals_ce' but broken out by
            EMM region instead of AIA climate region.
        htcl_totals_site_emm (str): Same as 'htcl_totals_site' but broken out
            by EMM region instead of AIA climate region.
        htcl_totals_state (string): Same as 'htcl_totals' but broken out by
            state instead of AIA climate region.
        htcl_totals_ce_state (str): Same as 'htcl_totals_ce' but broken out by
            state instead of AIA climate region.
        htcl_totals_site_state (str): Same as 'htcl_totals_site' but broken out
            by state instead of AIA climate region.
        ss_fp (str): Site-source conversions file path for fossil fuel
            equivalent version.
        ss_fp_decarb (str): Site-source conversions file path for fossil fuel
            equivalent version under high grid decarbonization.
        ss_fp_ce (str): Site-source conversions file path for captured
            energy version.
        metadata (dict): Baseline metadata including min/max for year range.
    """

    def __init__(self):
        self.msegs_in = fp.STOCK_ENERGY / "mseg_res_com_cz.json"
        self.msegs_in_emm = fp.STOCK_ENERGY / "mseg_res_com_emm.gz"
        self.msegs_in_state = fp.STOCK_ENERGY / "mseg_res_com_state.gz"
        self.htcl_totals = fp.STOCK_ENERGY / "htcl_totals.json"
        self.htcl_totals_decarb = fp.STOCK_ENERGY / "htcl_totals_decarb.json"
        self.htcl_totals_ce = fp.STOCK_ENERGY / "htcl_totals-ce.json"
        self.htcl_totals_site = fp.STOCK_ENERGY / "htcl_totals-site.json"
        self.htcl_totals_emm = fp.STOCK_ENERGY / "htcl_totals_emm.json"
        self.htcl_totals_emm_decarb = fp.STOCK_ENERGY / "htcl_totals_emm_decarb.json"
        self.htcl_totals_ce_emm = fp.STOCK_ENERGY / "htcl_totals-ce_emm.json"
        self.htcl_totals_site_emm = fp.STOCK_ENERGY / "htcl_totals-site_emm.json"
        self.htcl_totals_state = fp.STOCK_ENERGY / "htcl_totals_state.json"
        self.htcl_totals_ce_state = fp.STOCK_ENERGY / "htcl_totals-ce_state.json"
        self.htcl_totals_site_state = fp.STOCK_ENERGY / "htcl_totals-site_state.json"
        self.ss_fp = fp.CONVERT_DATA / "site_source_co2_conversions.json"
        self.ss_fp_decarb = fp.CONVERT_DATA / "site_source_co2_conversions-100by2035.json"
        self.ss_fp_ce = fp.CONVERT_DATA / "site_source_co2_conversions-ce.json"
        self.metadata = fp.METADATA_PATH


class UsefulVars(object):
    """Class of variables that are used globally across functions.

    Attributes:
        aeo_years (list): Modeling time horizon.
        ss_conv (dict): Site-source conversion factors by fuel type
            calculated using the fossil fuel equivalent method.
        ss_conv_ce (dict or bool): Site-source conversion factors by
            fuel type calculated using the captured energy method.
        ss_conv_str (str): String to use in the output heating and
            cooling energy files to define the conversion method.
    """

    def __init__(self, handyfiles):
        # Load metadata including AEO year range
        with open(handyfiles.metadata, 'r') as aeo_yrs:
            try:
                aeo_yrs = json.load(aeo_yrs)
            except ValueError as e:
                raise ValueError(
                    "Error reading in '" +
                    handyfiles.metadata + "': " + str(e)) from None
        # Set minimum AEO modeling year to AEO base year
        aeo_min = aeo_yrs["aeo_base_year"]
        # Set maximum AEO modeling year
        aeo_max = aeo_yrs["max year"]
        # Derive time horizon from min/max years
        self.aeo_years = [
            str(i) for i in range(aeo_min, aeo_max + 1)]

        # Read in JSON with site to source conversion, fuel CO2 intensity,
        # and energy/carbon costs data
        with open(handyfiles.ss_fp, 'r') as ss:
            cost_ss_carb = json.load(ss)
        # Set site to source conversions
        self.ss_conv = {
            "electricity": cost_ss_carb[
                "electricity"]["site to source conversion"]["data"],
            "natural gas": {yr: 1 for yr in self.aeo_years},
            "distillate": {yr: 1 for yr in self.aeo_years},
            "other fuel": {yr: 1 for yr in self.aeo_years}}

        # Read in JSON with site to source conversion, fuel CO2 intensity,
        # and energy/carbon costs data under high grid decarbonization case
        with open(handyfiles.ss_fp_decarb, 'r') as ss:
            cost_ss_carb_decarb = json.load(ss)
        # Set site to source conversions under high grid decarbonization case
        self.ss_conv_decarb = {
            "electricity": cost_ss_carb_decarb[
                "electricity"]["site to source conversion"]["data"],
            "natural gas": {yr: 1 for yr in self.aeo_years},
            "distillate": {yr: 1 for yr in self.aeo_years},
            "other fuel": {yr: 1 for yr in self.aeo_years}}

        # Set site to source conversions to one for a site energy output
        # (no conversion is required)
        self.ss_conv_site = {
            "electricity": {yr: 1 for yr in self.aeo_years},
            "natural gas": {yr: 1 for yr in self.aeo_years},
            "distillate": {yr: 1 for yr in self.aeo_years},
            "other fuel": {yr: 1 for yr in self.aeo_years}}

        # Try to get site-source conversion factors for the captured
        # energy method if the file is present
        try:
            with open(handyfiles.ss_fp_ce, 'r') as ss:
                ss_dict = json.load(ss)
            self.ss_conv_ce = {
                "electricity": ss_dict[
                    "electricity"]["site to source conversion"]["data"],
                "natural gas": {yr: 1 for yr in self.aeo_years},
                "distillate": {yr: 1 for yr in self.aeo_years},
                "other fuel": {yr: 1 for yr in self.aeo_years}}
        except FileNotFoundError:
            self.ss_conv_ce = False

        # Define site-source calculation method key string for module outputs
        self.ss_conv_str = "site-source calculation method"


def sum_htcl_branches(nested_dict, adj_frac, sum_val):
    """Sum all leaf node values under a given nested dict level.

    Args:
        nested_dict (dict): The nested dict with values to sum.
        adj_frac (dict): Adjustment fraction to apply to values.
        sum_val (dict): Summed values.

    Returns:
        Summed total values, each adjusted by the input fraction.
    """
    for (k, i) in sorted(nested_dict.items()):
        # Restrict summation of all values under the 'stock' key
        if k == "stock":
            continue
        elif isinstance(i, dict):
            sum_htcl_branches(i, adj_frac, sum_val)
        elif k in sum_val.keys():
            sum_val[k] = sum_val[k] + nested_dict[k] * adj_frac[k]

    return sum_val


def set_new_exist_frac(msegs, aeo_years, bldg):
    """ Determine cumulative new vs. existing structures by year.

    Attributes:
        msegs (dict): Data on new and existing homes (residential) and new and
            existing square feet (commercial), broken down by building type.
        aeo_years (list): Modeling time horizon.
        bldg (string): Building type energy data is currently being retrieved
            for.

    Returns:
        Fractions of the total building stock that are existing or newly
        constructed since the first year in the modeling time horizon.
    """

    # Initialize dict of supporting data for new/existing structure calcs.
    new_constr = {
        "annual new": {}, "annual total": {}}
    # Initialize dict to store new vs. existing structure fractions
    new_exist_frac = {"new": {}, "existing": {}}

    # Determine annual and total new construction for each year (by new
    # homes for the residential sector, by square feet for commercial)
    if bldg in ["single family home", "mobile home",
                "multi family home"]:
        new_constr["annual new"] = {yr: msegs["new homes"][yr] for
                                    yr in aeo_years}
        new_constr["annual total"] = {yr: msegs["total homes"][yr] for
                                      yr in aeo_years}
    else:
        new_constr["annual new"] = {yr: msegs["new square footage"][yr] for
                                    yr in aeo_years}
        new_constr["annual total"] = {yr: msegs["total square footage"][yr] for
                                      yr in aeo_years}

    # Find the cumulative fraction of new buildings constructed in all
    # years since the beginning of the modeling time horizon

    # Set cumulative new homes or square footage totals
    for yr in aeo_years:
        if yr == aeo_years[0]:
            new_exist_frac["new"][yr] = new_constr["annual new"][yr]
        else:
            new_exist_frac["new"][yr] = new_constr["annual new"][yr] + \
                new_exist_frac["new"][str(int(yr) - 1)]
    # Divide cumulative new home or square footage totals by total
    # new homes or square footage to arrive at cumulative new fraction
    new_exist_frac["new"] = {
        key: val / new_constr["annual total"][key] if
        (val / new_constr["annual total"][key]) <= 1 else 1 for key, val in
        new_exist_frac["new"].items()}
    # Cumulative existing fraction equals 1 - cumulative new fraction
    new_exist_frac["existing"] = {key: (1 - val) for key, val in
                                  new_exist_frac["new"].items()}

    return new_exist_frac


def sum_htcl_energy(msegs, aeo_years, ss_conv):
    """ Sum heating/cooling energy by climate, building, and structure.

    Attributes:
        msegs (dict): Baseline energy data to sum.
        aeo_years (list): Modeling time horizon.
        ss_conv (dict): Site-source energy conversions by fuel type.

    Note:
        Energy values are summed across a particular climate zone,
        building type, and structure type combination. All energy values must
        be converted to source energy and apportioned to the given structure
        type, in order to be consistent with the ECM competition data these
        data are later combined with in the analysis engine.

    Returns:
        Total energy by year associated with a given climate zone,
        building type, and structure type combination.
    """

    # Initialize dict for storing summed heating/cooling energy totals
    htcl_totals = {}

    # Loop through all climate zone, building type, and structure type
    # combinations and sum the energy values associated with each. Skip
    # "_cdiv_disagg_info", a metadata key (not a region) that
    # final_mseg_converter.py adds to the EMM/state files reporting how
    # their Cdiv->EMM/state disaggregation was prepared.
    for cz in [c for c in msegs.keys() if c != "_cdiv_disagg_info"]:
        htcl_totals[cz] = {}
        # Skip the "unspecified" building type, which is non-standard
        for bldg in [b for b in msegs[cz].keys() if b != 'unspecified']:
            htcl_totals[cz][bldg] = {}
            # Find new vs. existing structure type fraction for bldg. type
            new_exist_frac = set_new_exist_frac(
                msegs[cz][bldg], aeo_years, bldg)
            for vint in new_exist_frac.keys():
                htcl_totals[cz][bldg][vint] = {}
                # Fuel type
                for fuel in [x for x in msegs[cz][bldg].keys() if
                             x not in ["total homes", "new homes",
                                       "total square footage",
                                       "new square footage",
                                       "total square footage"]]:
                    htcl_totals[cz][bldg][vint][fuel] = {}
                    for eu in [x for x in [
                        "heating", "secondary heating", "cooling"] if
                            x in msegs[cz][bldg][fuel].keys()]:
                        htcl_totals[cz][bldg][vint][fuel][eu] = {
                                yr: 0 for yr in aeo_years}
                        # Find energy value to add to total
                        sum_val = sum_htcl_branches(
                            msegs[cz][bldg][fuel][eu]["demand"],
                            adj_frac={yr: new_exist_frac[vint][yr] *
                                      ss_conv[fuel][yr] for yr in aeo_years},
                            sum_val={yr: 0 for yr in aeo_years})
                        # Update total energy for given climate,
                        # building and structure type combination
                        htcl_totals[cz][bldg][vint][fuel][eu] = {
                            yr: htcl_totals[cz][bldg][vint][fuel][eu][yr] +
                            sum_val[yr] for yr in aeo_years}

    return htcl_totals


def main():
    """ Import JSON energy data and sum by climate, building, and structure."""

    # Instantiate useful input files object
    handyfiles = UsefulInputFiles()
    # Instantiate useful variables
    handyvars = UsefulVars(handyfiles)

    # Generate data for both the default AIA climate region baseline data
    # breakout and EMM region and state baseline data breakout
    for f in ["AIA", "EMM", "State"]:
        # Determine input/output file names based on whether default AIA
        # climates, EMM regions, or states are used to breakout baseline data
        if f == "AIA":
            mseg_fi = handyfiles.msegs_in
            fo = handyfiles.htcl_totals
            fo_decarb = handyfiles.htcl_totals_decarb
            fo_site = handyfiles.htcl_totals_site
            fo_capt = handyfiles.htcl_totals_ce

        elif f == "EMM":
            mseg_fi = handyfiles.msegs_in_emm
            fo = handyfiles.htcl_totals_emm
            fo_decarb = handyfiles.htcl_totals_emm_decarb
            fo_site = handyfiles.htcl_totals_site_emm
            fo_capt = handyfiles.htcl_totals_ce_emm

        else:
            mseg_fi = handyfiles.msegs_in_state
            fo = handyfiles.htcl_totals_state
            fo_decarb = None
            fo_site = handyfiles.htcl_totals_site_state
            fo_capt = handyfiles.htcl_totals_ce_state

        # Import baseline microsegment stock and energy data; special
        # handling needed for state and EMM data, which are in zip format
        if f in ["State", "EMM"]:
            bjszip = mseg_fi
            with gzip.GzipFile(bjszip, 'r') as zip_ref:
                msegs = json.loads(zip_ref.read().decode('utf-8'))
        else:
            with open(mseg_fi, 'r') as msi:
                try:
                    msegs = json.load(msi)
                except ValueError as e:
                    raise ValueError(
                        f"Error reading in '{handyfiles.msegs_in}': {str(e)}") from None

        # Find total heating and cooling *source* energy use for each region,
        # building type, and structure type combination (fossil fuel site-
        # source conversion method)
        htcl_totals = sum_htcl_energy(
            msegs, handyvars.aeo_years, handyvars.ss_conv)

        # Add site-source conversion type to file
        htcl_totals = OrderedDict(htcl_totals)
        htcl_totals[handyvars.ss_conv_str] = "fossil fuel equivalence"
        htcl_totals.move_to_end(handyvars.ss_conv_str, last=False)

        # Write out summed heating/cooling fossil equivalent energy data
        output_file = fo
        with open(output_file, 'w') as jso:
            json.dump(htcl_totals, jso, indent=2)

        # Update high grid decarbonization case results if applicable
        if fo_decarb is not None:
            # Find total heating and cooling *source* energy use for each
            # region, building type, and structure type combination (fossil
            # fuel site-source conversion method) under high grid
            # decarbonization case
            htcl_totals_decarb = sum_htcl_energy(
                msegs, handyvars.aeo_years, handyvars.ss_conv_decarb)

            # Add site-source conversion type to file under high grid
            # decarbonization case
            htcl_totals_decarb = OrderedDict(htcl_totals_decarb)
            htcl_totals_decarb[handyvars.ss_conv_str] = \
                "fossil fuel equivalence"
            htcl_totals_decarb.move_to_end(handyvars.ss_conv_str, last=False)

            # Write out summed heating/cooling fossil equivalent energy data
            # under high grid decarbonization case
            output_file_decarb = fo_decarb
            with open(output_file_decarb, 'w') as jso:
                json.dump(htcl_totals_decarb, jso, indent=2)

        # Find total heating and cooling *site* energy use for each region,
        # building type, and structure type combination
        htcl_totals_site = sum_htcl_energy(
            msegs, handyvars.aeo_years, handyvars.ss_conv_site)

        # Add site-source conversion type to file
        htcl_totals_site = OrderedDict(htcl_totals_site)
        htcl_totals_site[handyvars.ss_conv_str] = \
            "site energy (no site-source conversion)"
        htcl_totals_site.move_to_end(handyvars.ss_conv_str, last=False)

        # Write out summed heating/cooling site energy data
        output_file = fo_site
        with open(output_file, 'w') as jso:
            json.dump(htcl_totals_site, jso, indent=2)

        # If the captured energy file is found, also generate the
        # heating and cooling *source* energy totals file based on the captured
        # energy method for calculating site-source conversion factors
        if handyvars.ss_conv_ce:
            htcl_totals_ce = sum_htcl_energy(
                msegs, handyvars.aeo_years, handyvars.ss_conv_ce)

            # Add site-source conversion type to file
            htcl_totals_ce = OrderedDict(htcl_totals_ce)
            htcl_totals_ce[handyvars.ss_conv_str] = "captured energy"
            htcl_totals_ce.move_to_end(handyvars.ss_conv_str, last=False)

            # Write out heating/cooling combined captured energy data
            output_file = fo_capt
            with open(output_file, 'w') as jso:
                json.dump(htcl_totals_ce, jso, indent=2)


if __name__ == '__main__':
    main()

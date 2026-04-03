#!/usr/bin/env python3

"""Extracted test data for Market Updates tests."""

ok_hpmeas_rates_breakouts = [{
    'stock': {
        'baseline': {
            'TRE': {'Residential (Existing)': {
                'Heating (Equip.)': {
                    'Electric': {'2009': 0, '2010': 0},
                    'Non-Electric': {'2009': 1.35, '2010': 2.766667}},
                'Cooling (Equip.)': {
                    'Electric': {'2009': 0, '2010': 0},
                    'Non-Electric': {}}}}},
        'efficient': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 1.35, '2010': 2.766667},
                        'Non-Electric': {'2009': 0, '2010': 0}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 0, '2010': 0},
                        'Non-Electric': {}}}}}
    },
    'energy': {
        'baseline': {
            'TRE': {'Residential (Existing)': {
                'Heating (Equip.)': {
                    'Electric': {'2009': 0, '2010': 0},
                    'Non-Electric': {'2009': 1.35, '2010': 2.766667}},
                'Cooling (Equip.)': {
                    'Electric': {'2009': 0.675, '2010': 1.383333},
                    'Non-Electric': {}}}}},
        'efficient': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 0.45, '2010': 0.9222222},
                        'Non-Electric': {'2009': 0, '2010': 0}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 0.225, '2010': 0.4611111},
                        'Non-Electric': {}}}}},
        'savings': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': -0.45,
                                     '2010': -0.9222222},
                        'Non-Electric': {'2009': 1.35,
                                         '2010': 2.766667}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 0.45, '2010': 0.9222222},
                        'Non-Electric': {}}}}}},
    'carbon': {
        'baseline': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 0, '2010': 0},
                        'Non-Electric': {
                            '2009': 77.05925, '2010': 153.4582}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 8.8155e-08,
                                     '2010': 1.658617e-07},
                        'Non-Electric': {}}}}},
        'efficient': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 5.877e-08,
                                     '2010': 1.105744e-07},
                        'Non-Electric': {'2009': 0, '2010': 0}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 2.9385e-08,
                                     '2010': 5.528722e-08},
                        'Non-Electric': {}}}}},
        'savings': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': -5.877e-08,
                                     '2010': -1.105744e-07},
                        'Non-Electric': {'2009': 77.05925,
                                         '2010': 153.4582}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 5.877e-08,
                                     '2010': 1.105744e-07},
                        'Non-Electric': {}}}}}},
    'energy cost': {
        'baseline': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 0, '2010': 0},
                        'Non-Electric': {'2009': 15.38028,
                                         '2010': 30.12291}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 20.1311,
                                     '2010': 37.30094},
                        'Non-Electric': {}}}}},
        'efficient': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 13.42074,
                                     '2010': 24.8673},
                        'Non-Electric': {'2009': 0, '2010': 0}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 6.710368,
                                     '2010': 12.43365},
                        'Non-Electric': {}}}}},
        'savings': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': -13.42074,
                                     '2010': -24.8673},
                        'Non-Electric': {'2009': 15.38028,
                                         '2010': 30.12291}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 13.42074,
                                     '2010': 24.8673},
                        'Non-Electric': {}}}}}}}, {
    'stock': {
        'baseline': {
            'TRE': {'Residential (Existing)': {
                'Heating (Equip.)': {
                    'Electric': {'2009': 0, '2010': 0},
                    'Non-Electric': {'2009': 90, '2010': 85}},
                'Cooling (Equip.)': {
                    'Electric': {'2009': 0, '2010': 0},
                    'Non-Electric': {}}}}},
        'efficient': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 6.9, '2010': 13.42},
                        'Non-Electric': {'2009': 0,
                                         '2010': 0}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 0, '2010': 0},
                        'Non-Electric': {}}}}}},
    'energy': {
        'baseline': {
            'TRE': {'Residential (Existing)': {
                'Heating (Equip.)': {
                    'Electric': {'2009': 0, '2010': 0},
                    'Non-Electric': {'2009': 90, '2010': 85}},
                'Cooling (Equip.)': {
                    'Electric': {'2009': 45, '2010': 42.5},
                    'Non-Electric': {}}}}},
        'efficient': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 2.3, '2010': 4.472222},
                        'Non-Electric': {'2009': 83.1,
                                         '2010': 71.58333}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 42.7, '2010': 38.02778},
                        'Non-Electric': {}}}}},
        'savings': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': -2.3, '2010': -4.472222},
                        'Non-Electric': {'2009': 6.9,
                                         '2010': 13.41667}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 2.3, '2010': 4.472222},
                        'Non-Electric': {}}}}}},
    'carbon': {
        'baseline': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 0, '2010': 0},
                        'Non-Electric': {
                            '2009': 5137.283, '2010': 4714.678}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 5.877e-06,
                                     '2010': 5.09575e-06},
                        'Non-Electric': {}}}}},
        'efficient': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 3.0038e-07,
                                     '2010': 5.362194e-07},
                        'Non-Electric': {'2009': 4743.425,
                                         '2010': 3970.499}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 5.57662e-06,
                                     '2010': 4.559531e-06},
                        'Non-Electric': {}}}}},
        'savings': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': -3.0038e-07,
                                     '2010': -5.362194e-07},
                        'Non-Electric': {'2009': 393.8584,
                                         '2010': 744.1796}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 3.0038e-07,
                                     '2010': 5.362194e-07},
                        'Non-Electric': {}}}}}},
    'energy cost': {
        'baseline': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 0, '2010': 0},
                        'Non-Electric': {'2009': 1025.352,
                                         '2010': 925.463}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 1342.074,
                                     '2010': 1145.993},
                        'Non-Electric': {}}}}},
        'efficient': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': 68.59487,
                                     '2010': 120.5914},
                        'Non-Electric': {'2009': 946.7417,
                                         '2010': 779.385}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 1273.479,
                                     '2010': 1025.401},
                        'Non-Electric': {}}}}},
        'savings': {
            'TRE': {
                'Residential (Existing)': {
                    'Heating (Equip.)': {
                        'Electric': {'2009': -68.59487,
                                     '2010': -120.5914},
                        'Non-Electric': {'2009': 78.61032,
                                         '2010': 146.078}},
                    'Cooling (Equip.)': {
                        'Electric': {'2009': 68.59487,
                                     '2010': 120.5914},
                        'Non-Electric': {}}}}}}}]
# Note: accounts for 50% market scaling fraction in the cooling segments when
# adding cooling costs to heating costs

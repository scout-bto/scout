# Download Required Input Files
Download following required input files from EIA data and put it in the scout/inputs folder.
For example, the AEO2025 data can be found in the Scout Teams channel under Documents/General/EIA Data/AEO2025
- RDM_DBOUT.TXT
- RDM_DGENOUT.txt
- rsmlgt.txt
- rsmess.xlsx
- ktekx.xlsx
- kprem.txt
- CDM_SDOUT.txt
- CDM_DGENOUT.txt


# Pre-Processing Checks
## For rsmlgt.txt:
- Review notes at top of rsmlgt sheet for general changes
- Verify columns match expected names in `r_lt_names` in mseg_techdata.py
- Count header rows before column headings start; set `lt_skip_header` accordingly
- Count footer rows after last data; set `lt_skip_footer` accordingly  
- Test import by adding `print(eia_lt)` around line 1040 in mseg_techdata.py

## For ktek.csv:
- Edit lifetime column to contain integer values


# Processing Workflow
## Preliminary Steps
- Run tests to confirm they're passing
`python -m unittest discover -s tests -p "*_test.py"`
- Check entry lines against actual files
- Generate required data input files in the scout/inputs folder
`python scout/eia_file.py`

## Step 1: Generate Metadata
`python scout/mseg_meta.py`
Outputs metadata.json in the scout/inputs folder

## Step 2: Generate Stock/Energy Input Files
Process residential data
`python scout/mseg.py -y 2025`
Outputs mseg_res_cdiv.json in the scout/inputs folder

Process commercial data
`python scout/com_mseg.py`
Outputs mseg_res_com_cdiv.json in the scout/inputs folder

Run commercial tests
`python tests/com_mseg_test.py`

Generate final aggregated files
`python scout/final_mseg_converter.py`
Select options 1,1 when prompted
Ignore: UserWarning: Key 'solar_water_heater_north' not found in add_dict – skipping
warnings.warn(f"Key '{k}' not found in add_dict – skipping"), there is an issue about this. 
Outputs mseg_res_com_cz.json
Also run with options 1,2,2,1 and 1,3,2,1

`python scout/final_mseg_converter.py`
Select appropriate options when prompted

Run converter tests
`python tests/final_mseg_converter_test.py`

## Step 3: Commit final output files
Move these final output files to the scout/scout/supporting_data/supporting_data/stock_energy_tech_data folder, commit and push to github:
- mseg_res_com_cz.json
- mseg_res_com_emm.gz
- mseg_res_com_state.gz

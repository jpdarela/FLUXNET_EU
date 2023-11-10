# README

- Convert data format from FLUXNET2015(csv) to CF(not always) NETCDF4 files
- Convert units to match LPJ-GUESS inputs
- One file per site & variable (One timeseries per file) for reference data
-- Reference data has different time periods for each site
-- Observations with quality flags lower than 0.75 were excluded from reference data
- All sites for one variable per file for driving (climatic) data.
-- Driving variables are for the period 1989-12-31 to 2019-12-31 (ERA downscaled data)
-- I created some Precipitation (pr) and VPD(vpd) datasets with some modifications in the timeseries.

Monthly Reference data (NEE, GPP, Reco and ET) are stored [here](./ref/)

Daily driver variables (tas, wind, rsds, pr, ps, hurs and VPD) are stored [here](./driver/)

## Use

FLUXNET data was downloaded from the [FLUXNET 2015 repository](https://fluxnet.org/login/?redirect_to=/data/download-data/) (Registration required) The dataset used can be found here: <https://www.icos-cp.eu/data-products/2G60-ZHAK>

Currently we have the folowing [sites](./driver/FLUXNET2015.grd)

Thus, everything is set to convert those sites. Just need to download and unzip it

With that, run the main script:

``$ python fluxnet2netcdf.py``

This will generate the files in the parent directory.

# README

 - Convert data format from FLUXNET2015(csv) to CF(not always) NETCDF4 files
 - Convert units to match LPJ-GUESS inputs
 - One file per site & variable (One timeseries per file) for reference data
    - Reference data has different time periods for each site
    - Observations with quality flags lower than 0.75 were excluded from reference data
 - All sites for one variable per file for driving (climatic) data.
    - Driving variables are for the period 1989-12-31 to 2014-12-31 (ERA downscaled data)
    - I created some Precipitation (pr) and VPD(vpd) datasets with some modifications in the timeseries.

 # Usage

Download and unzip the folders with data from the [fluxnet 2015 repository](https://fluxnet.org/login/?redirect_to=/data/download-data/) (Registration required) in the parent directory. Unzip it to a folder named as the zip file without the .zip extension inside the parent folder.

I hardcoded site metadata (Site name and geographic coordinates) along with the relative path to the files of interest in the unziped FLUXNET2015 folders in [this file](./nc_write.py). If you want to add more sites you need to download and unzip the new data and add the required info into the dictionaries SITES_COORDINATES and SITE_OBS in that file.

Currently we have the metadata for the folowing sites:

1. BE-Bra
1. BE-Vie
1. CH-Dav
1. CH-Lae
1. CZ-BK1
1. DE-Hai
1. DE-Lkb
1. DE-Lnf
1. DE-Obe
1. DE-RuR
1. DE-Tha
1. DK-Sor
1. FI-Hyy
1. FI-Let
1. FI-Sod
1. FR-Fon
1. FR-Pue
1. IT-Col
1. IT-Cpz
1. IT-Lav
1. IT-Ren
1. NL-Loo
1. RU-Fyo


Thus, everything is set to convert those sites. Just need to download and unzip it

With that, run the main script:

``$ python fluxnet2netcdf.py``

This will generate the files in the parent directory.
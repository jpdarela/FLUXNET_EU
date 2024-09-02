from pathlib import Path

import pandas as pd
import numpy as np
from datetime import datetime

IGBP_LAND_COVER = ["CVM", "DBF", "DNF", "EBF", "ENF", "MF", "SAV"]

# CONFIGURATION
# Set to True here if FLUXNET2015 data should be used. If set to False, the configuration is to work with FLUXNET2020 data.
HANDLE_FLUXNET2015_DATA = False
fluxnet_data = Path('./FLUXNET2020/')
sitelist_file = "./SitesList.csv"
# END CONFIGURATION


igbp_column_name = 'IGBPCode'
lat_column_name = 'Latitude'
lon_column_name = 'Longitude'
site_column_name = 'SiteCode'
last_day = '20191231'
get_side_code = lambda folder: folder.name.split("_")[1]

if HANDLE_FLUXNET2015_DATA:
    igbp_column_name = 'IGBP'
    lat_column_name = 'LOCATION_LAT'
    lon_column_name = 'LOCATION_LONG'
    site_column_name = 'SITE_ID'
    last_day = '20141231'
    get_side_code = lambda folder: folder.name

last_day_of_observations = datetime.strptime(last_day, "%Y%m%d")
first_day_of_observations = datetime(1989, 1, 1)
number_of_days_in_observations = (last_day_of_observations - first_day_of_observations).days + 1


# Coordinates of all FLUXNET sites
all_sites = pd.read_csv(sitelist_file, index_col=site_column_name).loc(1)[[lat_column_name, lon_column_name, igbp_column_name]]

# Our sites
site_codes = []
site_files = sorted([datadir.resolve() for datadir in fluxnet_data.glob("*/") if datadir.is_dir()])
fl = {}
for folder in site_files:
    site_code = get_side_code(folder)
    print(site_code)
    if all_sites[igbp_column_name][site_code] in IGBP_LAND_COVER:
        lat = np.array(round(all_sites[lat_column_name][site_code], 2), 'f4')
        lon = np.array(round(all_sites[lon_column_name][site_code], 2), 'f4')
        site_codes.append(site_code)
        fl[site_code.split("-")[-1]] = [lat, lon, site_code, folder]


def site_coord_dict(fl):
    driver_dict = {}
    ref_dict= {}
    tstart = {}
    idx = []
    driver_data_str = "*_FLUXNET2015_ERAI_DD_1989-*"
    ref_data_str = "*_FLUXNET2015_FULLSET_DD_*"
    for k, v in fl.items():
        ref_dict[k] = v[-1].glob(ref_data_str).__next__()
        driver_dict[k] = [v[0], v[1], v[2], v[3].glob(driver_data_str).__next__()]
        tstamps = pd.read_csv(ref_dict[k], index_col="TIMESTAMP", parse_dates=True).index
        start = f"{tstamps[0]}"[:10]
        end = f"{tstamps[-1]}"[:10]
        tstart[k] = [start, end]
        idx.append(k)

    pd.DataFrame(tstart).T.to_csv("trange.csv", header=False)
    return driver_dict, ref_dict

# do not adapt, variables are imported from other files.
SITES_COORDINATES, OBS_SITES = site_coord_dict(fl)
arr_da_lenght = number_of_days_in_observations
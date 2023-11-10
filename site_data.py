from pathlib import Path

import pandas as pd
import numpy as np

IGBP_LAND_COVER = ["CVM", "DBF", "DNF", "EBF", "ENF", "MF"]

fluxnet_data = Path("./FLUXNET2020/")
arr_da_lenght = 11322
last_day = "20191231"

# Coordinates of all FLUXNET sites
all_sites = pd.read_csv("./SitesList.csv", index_col="SiteCode").loc(1)[["Latitude","Longitude", "IGBPCode"]]

# Our sites
site_codes = []
site_files = sorted([i.resolve() for i in fluxnet_data.glob("*/")])
fl = {}
for folder in site_files:
    site_code = folder.name.split("_")[1]
    if all_sites.IGBPCode[site_code] in IGBP_LAND_COVER:
        lat = np.array(round(all_sites.Latitude[site_code], 2), 'f4')
        lon = np.array(round(all_sites.Longitude[site_code], 2), 'f4')
        site_codes.append(site_code)
        fl[site_code.split("-")[-1]] = [lat, lon, site_code, folder]


def site_coord_dict(fl):
    driver_dict = {}
    ref_dict= {}
    tstart = {}
    idx = []
    driver_data_str = "*_FLUXNET2015_ERAI_DD_1989-*"
    ref_data_str = "*_FLUXNET2015_FULLSET_MM_*"
    for k, v in fl.items():
        ref_dict[k] = v[-1].glob(ref_data_str).__next__()
        driver_dict[k] = [v[0], v[1], v[2], v[3].glob(driver_data_str).__next__()]
        tstamps = pd.read_csv(ref_dict[k], index_col="TIMESTAMP", parse_dates=True).index
        start = f"{tstamps[0]}01"
        end = f"{tstamps[-1]}31"
        tstart[k] = [start, end]
        idx.append(k)

    pd.DataFrame(tstart).T.to_csv("trange.csv", header=False)
    return driver_dict, ref_dict

SITES_COORDINATES, OBS_SITES = site_coord_dict(fl)
# -*- coding: utf-8 -*-
from pathlib import Path
from sys import platform
import os
import time as time_mod

from netCDF4 import Dataset

import cftime
import numpy as np
import pandas as pd

from conversions import convert_pr, convert_ps, convert_ta, convert_vpd, VPD2RH
from site_data import SITES_COORDINATES, OBS_SITES, arr_da_lenght, last_day

FLUXNET_REF = """References
1 - Pastorello, G., Trotta, C., Canfora, E. et al. The FLUXNET2015 dataset and the ONEFlux processing pipeline
for eddy covariance data. Sci Data 7, 225 (2020). https://doi.org/10.1038/s41597-020-0534-3.
2 - https://www.icos-cp.eu/data-products/2G60-ZHAK - ICOS Ecosystem Station data product DOI: https://doi.org/10.18160/2G60-ZHAK
"""


# # Variables METAdata (Fprcing)
FLUXNET_FULLSET_VARS = {'tas':  ["TA_ERA", "Air temperature, gapfilled using MDS method", "K", 'air_temperature'], # FLUXNET celsius
                        'rsds': ["SW_IN_ERA", "Shortwave radiation, incoming, gapfilled using MDS", 'W m-2',
                                 "surface_downwelling_shortwave_flux_in_air"],
                        'vpd':  ['VPD_ERA', "Vapor Pressure Deficit gapfilled using MDS method", "kPa", "vpd"], # FLUXNET hPa
                        'ps': ["PA_ERA","Atmospheric Pressure","Pa", "surface_air_pressure"], # FLUXNET kPa
                        'pr': ["P_ERA","Precipitation","kg m-2 s-1", "precipitation_flux"], # FLUXNET mm/day
                        'wind': ["WS_ERA","Wind Speed","m s-1", "wind_speed"], # Aparently the same
                        'PPFD': ["PPFD_IN","Photosynthetic photon flux density, incoming","µmol m-2 s-1", "PPFD"],
                        'co2': ["CO2_F_MDS","CO2 mole fraction, gapfilled with MDS", "µmol mol-1", "CONVERT TO TEXT\n<year> <value>\n"],
                        'hurs': ["RH_F","Relative humidity, range 0-100", "%", 'relative_humidity']}

# Reference data
# Monthly
# OBS_VARS = {"nee"  : ("NEE_VUT_REF", "kg m-2 month-1", "Net Ecosystem Exchange", "NEE_VUT_REF_QC"), #fluxnet
#             "gpp"  : ("GPP_NT_VUT_REF", "kg m-2 month-1", "Gross Primary Productivity", ""),
#             "reco" : ("RECO_NT_VUT_REF", "kg m-2 month-1", "Ecosystem Respiration", ""),
#             "mle"  : ("LE_F_MDS", "W m-2", "Latent Heat Flux", "LE_F_MDS_QC"), # COnvert to AET
#             "tas"  : ("TA_F_MDS", "celcius", "air temperature", "TA_F_MDS_QC"),
#             "et"  : ("AET", "kg m-2 month-1", "Actual Evapotranspiration")} # Not in the dataset ()}


OBS_VARS = {"nee"  : ("NEE_VUT_REF", "kg m-2 day-1", "Net Ecosystem Exchange", "NEE_VUT_REF_QC"), #fluxnet
            "gpp"  : ("GPP_NT_VUT_REF", "kg m-2 day-1", "Gross Primary Productivity", ""),
            "reco" : ("RECO_NT_VUT_REF", "kg m-2 day-1", "Ecosystem Respiration", ""),
            "mle"  : ("LE_F_MDS", "W m-2", "Latent Heat Flux", "LE_F_MDS_QC"), # COnvert to AET
            "tas"  : ("TA_F_MDS", "celcius", "air temperature", "TA_F_MDS_QC"),
            "et"  : ("AET", "kg m-2 day-1", "Actual Evapotranspiration")} # Not in the dataset ()}

def get_conv_func(var):

    if var == 'pr':
        return convert_pr
    elif var == 'ps':
        return convert_ps
    elif var == 'tas':
        return convert_ta
    elif var == 'vpd':
        return convert_vpd
    else:
        return lambda x : x

def get_timestamps(site, mon=True):
    if mon:
        data = pd.read_csv(OBS_SITES[site])["TIMESTAMP"].__array__()
        return f"{data[0]}01", f"{data[-1]}31"
    else:
        data = pd.read_csv(OBS_SITES[site])["TIMESTAMP"].__array__()[:arr_da_lenght]
        return f"{data[0]}", f"{data[-1]}"


def get_data(fpath, var=None):
    f = get_conv_func(var)
    return f(pd.read_csv(fpath)[FLUXNET_FULLSET_VARS[var][0]].__array__()[:arr_da_lenght])

def get_qc(site):
    fpath = OBS_SITES[site]
    return pd.read_csv(fpath)[OBS_VARS["nee"][-1]].__array__() > 0.75

def get_ref_data(site, var=None):
    # cv_factor = 0.0304368 # gm -2 d-1 => kg m-2 month-1
    cv_factor = 0.001 # kg m-2 d-1 => kg m-2 day-1
    assert var in ['nee','gpp','reco', "tas"]

    ref_data = pd.read_csv(OBS_SITES[site])[OBS_VARS[var][0]].__array__()[:arr_da_lenght]
    msk = ref_data == -9999
    if var == 'tas':
        return ref_data
    else:
        # need to convert C fluxes to make comparable
        cv = ref_data * cv_factor
        cv[msk] = -9999.0
        return cv

def calc_LHV(temp):
    """Harrison, L. P. 1963. Fundamentals concepts and definitions relating to humidity.
       In Wexler, A (Editor) Humidity and moisture Vol 3, Reinhold Publishing Co., N.Y.
       https://www.fao.org/3/x0490e/x0490e0k.htm#annex%203.%20background%20on%20physical%20parameters%20used%20in%20evapotranspiration%20computatio"""

    f = np.vectorize(lambda P: 2.501 - (2.361 * 10e-3) * P)
    return f(temp)

def get_aet(site):
    """
       https://www.fao.org/3/x0490e/x0490e00.htm
       https://earthscience.stackexchange.com/questions/20733/fluxnet15-how-to-convert-latent-heat-flux-to-actual-evapotranspiration
    """
    mle = pd.read_csv(OBS_SITES[site])[OBS_VARS["mle"][0]].__array__()[:arr_da_lenght] # W m-2
    qc_le = pd.read_csv(OBS_SITES[site])[OBS_VARS["mle"][-1]].__array__()[:arr_da_lenght] > 0.75
    qc_ta = pd.read_csv(OBS_SITES[site])[OBS_VARS["tas"][-1]].__array__()[:arr_da_lenght] > 0.75
    mask = np.logical_not(np.logical_and(qc_le, qc_ta))
    tas = get_ref_data(site, "tas")
    mle *= 1e-6 # convert to MJ m-2 s-1
    # cv_factor = 2.62974e6 ##from kg m-2 s-1 to kg m-2 month-1
    cv_factor = 86400.0 ##from kg m-2 s-1 to kg m-2 day-1

    aet = (mle / calc_LHV(tas)) * cv_factor ## convert
    aet[mask] = -9999.0
    return aet

def create_arrs(var, mod_var=None):
    lat = []
    lon = []
    fdata = []
    names = []
    counter = 0
    for k, v in SITES_COORDINATES.items():
        # print(k, v)
        if k == 'SITE':
            continue
        counter += 1
        fpath = v[3]
        lat.append(v[0])
        lon.append(v[1])
        names.append(v[2])
        fdata.append(fpath)
    dt = get_data(fpath, var)


    out_data = np.zeros(shape=(counter, dt.size))

    for x in range(counter):
        out_data[x, :] = get_data(fdata[x], var)


    if mod_var is not None:
            out_data = mod_var(out_data)

    return out_data, np.array(lat), np.array(lon), np.array(names, dtype="<U7")

def create_gridlist(fname):
    endline = "\r\n"
    if platform == "win32":
        endline = "\n"
    print(platform)
    with open(f"{Path('driver')}/{fname}.grd", 'w', encoding="utf-8") as fh:
        for k, v in SITES_COORDINATES.items():
            lat = v[0]
            lon = v[1]
            fname = v[2]
            fh.write(f"{lon:.2f}\t{lat:.2f}\t{fname}{endline}")

def timeseries(fname = None,
              arr=None,
              var=None,
              unit=None,
              names = None,
              descr=None,
              time=None,
              la=None,
              lo=None,
              site_data=True,
              set="FULLSET",
              reference=None):

    """write fluxnet 2015 selected sites to nc"""

    if fname is not None:
        dset = Dataset(os.path.join(Path('./'), fname + ".nc"),mode="w", format="NETCDF4")
    else:
        assert var is not None, "Need to set fname or var"
        dset = Dataset(os.path.join(Path('./'), FLUXNET_FULLSET_VARS[var][0] + '.nc'), mode="w", format="NETCDF4")

    if site_data:
        # Create temporal dimension
        time_dim = time['data']
        time_unit = time['units']
        calendar = time['calendar']

        lats = la
        lons = lo

        # Create netCDF dimensions
        dset.createDimension("station",size=arr.shape[0])
        dset.createDimension("time",size=arr.shape[1])

        # Data description
        dset.description = f"FLUXNET 2015 DATA - {set} {FLUXNET_FULLSET_VARS[var][0]}"
        dset.source = f'Forcing data for DVM - {descr}'
        dset.history= f'Created: {time_mod.ctime(time_mod.time())}'
        if reference is not None:
            dset.reference = reference
        dset.featureType = "timeSeries"

        # Create netCDF variables
        S = dset.createVariable("station", 'i4', ("station",), fill_value=999999)
        X  = dset.createVariable("lon", 'f4', ("station",))
        Y =  dset.createVariable("lat", 'f4', ("station",))
        SN = dset.createVariable("station_name", '<U6', ("station", ),fill_value= '------')
        T  = dset.createVariable("time", 'i4', ("time",), fill_value=999999)

        D  = dset.createVariable(var, 'f4', ("station", "time"), fill_value=-9999.0)

        S[...] = np.arange(arr.shape[0])
        T[...] = time_dim.__array__()
        T.units    = time_unit
        T.calendar = calendar
        T.standard_name = "time"
        T.axis = 'T'

        X[...] = lons
        X.units    = "degrees_east"
        X.long_name = 'station_longitude'
        X.standard_name = 'longitude'
        X.axis='X'

        Y[...] = lats
        Y.units    = "degrees_north"
        Y.long_name = 'station_latitude'
        Y.standard_name = 'latitude'
        Y.axis = 'Y'

        if names is None:
            assert False, "need station/site names"
        else:
            nm = names
        SN[...] = nm
        SN.long_name = "station name"
        SN.cf_role = "timeseries_id"


        D[...] = np.copy(arr[:,:], order="C")
        D.units = unit
        # D.fluxnet_name = FLUXNET_FULLSET_VARS[var][0]
        D.standard_name = FLUXNET_FULLSET_VARS[var][3]
        D.coordinates = u"lon lat"

        dset.close()

def cf_timeseries(fname = None,
                      arr=None,
                      var=None,
                      site=None,
                      unit=None,
                      descr=None,
                      time=None,
                      la=None,
                      lo=None,
                      set="FULLSET",
                      reference=None):

    """Create a CF compliant nc4 file for site(s) data TODO document
    Single Timeseries CF conventions (page 163)"""


    if fname is not None:
        dset = Dataset(os.path.join(Path('./'), fname + ".nc"),mode="w", format="NETCDF4")
    else:
        assert var is not None, "Need to set fname or var"
        dset = Dataset(os.path.join(Path('./'), OBS_VARS[var][0] + '.nc'), mode="w", format="NETCDF4")

    # Create temporal dimension
    time_dim = time['data']
    time_unit = time['units']
    calendar = time['calendar']

    lats = la
    lons = lo

    # Create netCDF dimensions
    dset.createDimension("time",size=arr.size)

    # Data description
    dset.description = f"FLUXNET 2015 DATA - {set} {OBS_VARS[var][2]} {OBS_VARS[var][0]}"
    dset.source = f'Forcing data for DVM - {descr}'
    dset.history= f'Created: {time_mod.ctime(time_mod.time())} - Single Timeseries CF conventions 1.10 Appendix H.2.3'
    dset.Conventions = "CF-1.10"
    if reference is not None:
        dset.reference = reference
    dset.featureType = "timeSeries"

    # Create netCDF variables
    X  = dset.createVariable("lon", 'f4')
    Y =  dset.createVariable("lat", 'f4')
    SN = dset.createVariable("station_name", '<U6')
    T  = dset.createVariable("time", 'i4', ("time",))

    D  = dset.createVariable(var, 'f8', ("time",), fill_value=-9999)

    T[...] = time_dim.__array__()
    T.units    = time_unit
    T.calendar = calendar
    T.standard_name = "time"
    T.axis = 'T'

    X[...] = lons
    X.units    = "degrees_east"
    X.long_name = 'station_longitude'
    X.standard_name = 'longitude'

    Y[...] = lats
    Y.units    = "degrees_north"
    Y.long_name = 'station_latitude'
    Y.standard_name = 'latitude'

    SN[...] = SITES_COORDINATES[site][2]
    SN.long_name = "station name"
    SN.cf_role = "timeseries_id"


    D[...] = np.copy(arr[:], order="C")
    D.units = unit
    D.standard_name = var
    D.coordinates = u"time lat lon station_name"
    # D.coordinates = 'lon lat'

    dset.close()

def write_site_nc(VAR, mod=None):

    """write FLUXNET2015 FULLSET Variable to a netCDF4 file """
    start = "19890101"
    end = last_day
    idx = pd.date_range(start, end, freq='D')

    time_data = np.arange(idx.size, dtype='i4')

    day_init, hour_init = idx[0].isoformat().split("T")

    time_units = "days since %s %s" % (str(day_init), str(hour_init))

    calendar = 'proleptic_gregorian'

    descr = FLUXNET_FULLSET_VARS[VAR][1]
    units = FLUXNET_FULLSET_VARS[VAR][2]

    time_dict = {'data': time_data,
                'units': time_units,
                'calendar': calendar}

    success = False
    try:
        arr, lat, lon, names = create_arrs(VAR)
        success = True
    except:
        if VAR == 'hurs':
            try:
                vpd, lat, lon, names = create_arrs('vpd')
                # TODO error
                tair = create_arrs('tas')[0] - 273.15
                arr = VPD2RH(tair, (vpd * (-1)))
                success = True
                # assert False, "dont do hurs - error"
            except:
                success = False
        pass

    if success:
        la = lat
        lo = lon

        fname00 = f"{Path('driver')}/{VAR}_FLUXNET2015"

        if mod is not None:
            ID, arr = mod(arr, VAR)
            fname00 = f"{Path('driver')}/{VAR}_{ID}_FLUXNET2015"

        timeseries(fname=fname00, arr=arr, var=VAR, unit=units, names=names,
                       descr=descr, time=time_dict, la=la, lo=lo,
                       reference=FLUXNET_REF)

    else:
        print(f"VAR NOT FOUND: {FLUXNET_FULLSET_VARS[VAR][0]}")

def write_ref_data(VAR, site):

    """write FLUXNET2015 FULLSET REFERENCE Variable to a netCDF4 file """

    assert VAR in ['nee', 'gpp', 'reco', "et"]

    start, end = get_timestamps(site, mon=False)
    freq="D" # MS
    idx = pd.date_range(start, end, freq=freq)

    # time_data = np.arange(idx.size, dtype='i4')

    day_init, hour_init = idx[0].isoformat().split("T")

    time_units = "days since %s %s" % (str(day_init), str(hour_init))

    calendar = 'proleptic_gregorian'

    time_data = cftime.date2num(idx.to_pydatetime(), units=time_units, calendar=calendar)

    descr = OBS_VARS[VAR][2]
    units = OBS_VARS[VAR][1]

    time_dict = {'data': time_data,
                'units': time_units,
                'calendar': calendar}

    if VAR == "et":
        arr = get_aet(site)
    else:
        arr = get_ref_data(site, VAR)

    if VAR in ["nee", "gpp", "reco"]:
        mask =  np.logical_not(get_qc(site))
        arr[mask] = -9999.0

    la = SITES_COORDINATES[site][0]
    lo = SITES_COORDINATES[site][1]

    fname00 = f"{Path('ref')}/{VAR}_{site}_FLUXNET2015"

    cf_timeseries(fname=fname00, arr=arr, var=VAR, site=site,unit=units,
                    descr=descr, time=time_dict, la=la, lo=lo,
                    reference=FLUXNET_REF)

if __name__ == "__main__":
    pass
    # for v in ['tas', 'vpd', 'hurs', 'ps', 'pr', 'wind', 'rsds']:
    #     write_site_nc(v)
    # for i, site in enumerate(SITES_COORDINATES.keys()):
    #     for v in ['tas', 'vpd', 'hurs', 'ps', 'pr', 'wind', 'rsds']:
    #         write_site_nc(v)
    #     for v in ['nee', 'gpp', 'reco', "et"]:
    #         write_ref_data(v, site)

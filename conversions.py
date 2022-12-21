from copy import deepcopy
import numpy as np
import cftime
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import cftime as cf
from copy import deepcopy
from numba import vectorize, float64, float32

# GLOBAL
Pa2kPa = 1e-3
idx = pd.date_range("19890101", "20141231", freq="D")
calendar = 'standard'
units = "days since 1989-01-01T00:00:00"
exp_st = cftime.date2num(cftime.DatetimeProlepticGregorian(2001, 1, 1),
                            units=units, calendar=calendar)

exp_drought_y1 = cftime.date2num(cftime.DatetimeProlepticGregorian(2003, 1, 1),
                            units=units, calendar=calendar)
exp_drought_y2 = cftime.date2num(cftime.DatetimeProlepticGregorian(2005, 1, 1),
                            units=units, calendar=calendar)

#vectorized functions
#Converts precipitation from mm/day (FLUXNET) to kg m-2 s-1 (SI) :: assume 1 mm as 1 kg m-2
convert_pr = np.vectorize(lambda P: P * 1.5741e-5)

#TODO good option to increase speed: 99% increase in comparison with convert_vpd approach
@vectorize([float32(float32),
            float64(float64)])
def convert_vpd_vec(P):
    return (P * 0.1) * (-1)

# VPD from hPa (FLUXNET) to -kPa (GUESS)
convert_vpd = np.vectorize(lambda P: (P * 0.1) * (-1))

# PS from kPa (FLUXNET) to Pa (GUESS)
convert_ps = np.vectorize(lambda P: P * 1e3)

convert_ta = np.vectorize(lambda P: P + 273.15)

# modifiers
def mod_mJJAs(pr:np.array=None, var:str="pr")->np.array:
    
    tmp = deepcopy(pr)
    
    if var == "pr":        
        for index, day in enumerate(idx):
            if index >= exp_st:
                if day.month in [6, 7, 8]:
                    x = 0.7
                    tmp[:, index] -= tmp[:, index] * x
                elif day.month in [5, 9]:
                    x = 0.7
                    tmp[:, index] -= tmp[:, index] * x
                
        return "dry-summer2001-", tmp
    
    elif var == "vpd":       
        for index, day in enumerate(idx):
            if index >= exp_st:
                if day.month in [6, 7, 8]:
                    dec = np.abs(tmp[:, index]) * 0.5  
                    tmp[:, index] -= dec
                elif day.month in [5, 9]:
                    dec = np.abs(tmp[:, index]) * 0.5  
                    tmp[:, index] -= dec
                
        return "dry-summer2001-", tmp
    
    else:
        assert False, f"operation not allowed for var {var}"


def mod_make_drought(pr:np.array=None, var:str="pr")->np.array:
    tmp = deepcopy(pr) #np.zeros(shape=idx.size, dtype='f4') + 20    
    # reduce pr x %
    if var == "pr":
        for index, day in enumerate(idx):
            if (index >= exp_drought_y1) and (index <= exp_drought_y2):
                if day.month in [12, 1, 2]:
                    x = 0.95
                    tmp[:, index] -= tmp[:, index] * x
                elif day.month in [11, 3]:
                    x = 0.9
                    tmp[:, index] -= tmp[:, index] * x
                elif day.month in [6, 7, 8]:
                    x = 0.9
                    tmp[:, index] -= tmp[:, index] * x
                elif day.month in [5, 9]:
                    x = 0.95
                    tmp[:, index] -= tmp[:, index] * x
        return "2003-5_drought", tmp

    elif var == "vpd":
        for index, day in enumerate(idx):
            if (index >= exp_drought_y1) and (index <= exp_drought_y2):
                if day.month in [12, 1, 2]:
                    dec = np.abs(tmp[:, index]) * 0.5
                    tmp[:, index] -= dec
                elif day.month in [11, 3]:
                    dec = np.abs(tmp[:, index]) * 0.5
                    tmp[:, index] -= dec
                elif day.month in [6, 7, 8]:
                    dec = np.abs(tmp[:, index]) * 0.5
                    tmp[:, index] -= dec
                elif day.month in [5, 9]:
                    dec = np.abs(tmp[:, index]) * 0.5
                    tmp[:, index] -= dec
        return "2003-5_drought", tmp   


def mod_tas(ts:np.array=None)->np.array:
    tmp = deepcopy(ts) #np.zeros(shape=idx.size, dtype='f4') + 20    
    # inbrease ts x dcgC
    x = 4
    for index, day in enumerate(idx):
        if index >= exp_st:
            if day.month in [6, 7, 8]:
                tmp[:,index] += x
            elif day.month in [5, 9]:
                x = 2
                tmp[:,index] += x            
    return "SSP3-7.0_NearTerm-", tmp

# utilities
def Vsat_slope(Tair:np.array,method=3) -> np.array:
# Translated to python from the bigleaf R package

#' Saturation Vapor Pressure (Esat) and Slope of the Esat Curve
#'
#' @references Sonntag D. 1990: Important new values of the physical constants of 1986, vapor
#'             pressure formulations based on the ITS-90 and psychrometric formulae.
#'             Zeitschrift fuer Meteorologie 70, 340-344.
#'
#'             World Meteorological Organization 2008: Guide to Meteorological Instruments
#'             and Methods of Observation (WMO-No.8). World Meteorological Organization,
#'             Geneva. 7th Edition.
#'
#'             Alduchov, O. A. & Eskridge, R. E., 1996: Improved Magnus form approximation of
#'             saturation vapor pressure. Journal of Applied Meteorology, 35, 601-609
#'
#'             Allen, R.G., Pereira, L.S., Raes, D., Smith, M., 1998: Crop evapotranspiration -
#'             Guidelines for computing crop water requirements - FAO irrigation and drainage
#'             paper 56, FAO, Rome.

    """ Tair °C """

    methods = ("Sonntag_1990","Alduchov_1996","Allen_1998")
    assert method <= 3 or method >= 1, "Methods:\n1 - Sonntag_1990\n2 - Alduchov_1996\n3 - Allen_1998"
    formula = methods[method - 1]
    print(f"Calculating RH from (TAIR, VPD) with Esat slope using the formula: {formula}")

    if formula == "Sonntag_1990":
        a = 611.2
        b = 17.62
        c = 243.12
    elif (formula == "Alduchov_1996"):
        a = 610.94
        b = 17.625
        c = 243.04
    elif (formula == "Allen_1998"):
        a = 610.8
        b = 17.27
        c = 237.3

  # saturation vapor pressure
    Esat = a * np.exp((b * Tair) / (c + Tair))
    Esat = Esat * Pa2kPa

  # slope of the saturation vapor pressure curve
    Delta = a * (np.exp((b * Tair)/(c + Tair)) * (b/(c + Tair) - (b * Tair)/(c + Tair)**2))
    Delta = Delta * Pa2kPa

    return Esat,Delta


def VPD2RH(Tair:np.array, VPD:np.array) -> np.array:
    """Estimate hurs from Tair (°C) and VPD (kPa)"""
    # Translated to python from the bigleaf R package
    esat =  Vsat_slope(Tair)[0]
    return 1.0 - (VPD / esat)


def mcwd_calc(et, pr, TIME_AXIS):

    T = TIME_AXIS.shape[0]
    MCWD_DAY = np.zeros(shape=T,)

    time = 0
    while time < T:
        check = cf.num2date(
            TIME_AXIS[time], units=units, calendar=calendar)
        if time == 0:
            mcwd = MCWD_DAY[time]
        else:
            mcwd = MCWD_DAY[time - 1]

        et1 = et[time] * 12.0
        pr1 = pr[time] * 3.15569e7

        temp = mcwd - (et1) + (pr1)
        mcwd = temp

        if temp > 0:
            mcwd = 0
        if check.month == 5 and check.day == 1:
            MCWD_DAY[time] = 0.0
        else:
            MCWD_DAY[time] = mcwd
        print(f"\rTSTEP{time}", end='', flush=True)
        time += 1
    print("\n")
    return MCWD_DAY


def mcwd_fluxnet2015(site):
    def get_series(var, site):
        station_name = f"FLX-{site}"
        data = Dataset(f"./{var}_dry-summer2001-_FLUXNET2015.nc")
        idx = np.where(data["station_name"][...] == station_name)[0][-1]
        tmp = data[var][idx, :] 
        return tmp, data
    #Get aet 
    ds = Dataset(f"aet_{site}_FLUXNET2015.nc")
    aet = ds["aet"][...].mean()
    
    pr, ncvar = get_series("pr", site)
    
    # TODO
    mcwd = mcwd_calc(np.repeat(aet, pr.size), pr, ncvar["time"][...])
    ds.close()
    ncvar.close()
       
    srs = pd.Series(mcwd, index=idx)
    fig, ax = plt.subplots(1,1)
    srs.rolling(365).mean().plot(ax=ax)
    plt.savefig(fname=f"mcwd_{site}.png", dpi=300)
    plt.clf()
    plt.close(fig)


if __name__ == "__main__":
    
    def test0():
        a = np.linspace(2,3,20000)
        convert_vpd_vec(a)
    def test1():
        a = np.linspace(2,3,20000)
        convert_vpd(a)
    def testmcwd():
        import matplotlib.pyplot as plt
        a = np.random.randint(0,10,730)
        b = np.random.randint(0,15,730)
        t = np.arange(730)
        
        mcwd = mcwd_calc(b,a,t)
        with plt.figure(1):
            plt.plot(mcwd)
            plt.savefig("testmcwd.png")
        # plt.close(fig)
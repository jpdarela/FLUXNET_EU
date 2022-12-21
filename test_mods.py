# test_mods.py
import matplotlib.pyplot as plt
import pandas as pd
from netCDF4 import Dataset

with open("./FLUXNET2015_gridlist.txt") as gridfile:
    GRIDLIST = []
    for line in gridfile.readlines():
        GRIDLIST.append(line.strip().split("\t"))

idx = pd.date_range("19890101", "20141231", freq="D")

SITES = [data[2] for data in GRIDLIST]

# PR
pr = Dataset("pr_FLUXNET2015.nc")
ts = Dataset("tas_FLUXNET2015.nc")

for grd, SITE in enumerate(SITES):

    season = "_drought_experiment_" # DJF JJA
    x = "pr_2003-5_drought_FLUXNET2015.nc"

    # pr_dec = Dataset(f"pr_SSP3-7.0_NearTerm-{season}_FLUXNET2015.nc")
    pr_dec = Dataset(x)

    s1 = []
    s2 = []
    for j in range(12):
        s1.append(pd.Series(pr.variables['pr'][j, :]))
        s2.append(pd.Series(pr_dec.variables['pr'][j, :]))

    plt.figure(figsize=(14,5))
    plt.title("2003-5 drought")

    # for x in range(12):
    #     s1[x].rolling(365).mean().plot(color='b', alpha=0.5) 
    #     s2[x].rolling(365).mean().plot(color='r', alpha=0.5)

    sr1 = s1[grd].rolling(90).mean()
    # .plot(color='b', alpha=0.4) 
    sr2 = s2[grd].rolling(90).mean()
    # ..plot(color='r', alpha=0.4)

    plt.plot(idx, sr1, color='k', alpha=0.4)
    plt.plot(idx, sr2, color='r', alpha=0.4)
    plt.legend(["pr", "pr_mod"])
    plt.gcf().autofmt_xdate()
    plt.ylabel("mm s-1")
    plt.xlabel(SITE)

    plt.savefig(f"test_pr_{SITE}_DRT2003.png", dpi=300)
    plt.clf()
    plt.close()
    # pr.close()
    pr_dec.close()

    # PR1

    pr_dec = Dataset("pr_dry-summer2001-_FLUXNET2015.nc")

    s1 = []
    s2 = []
    for j in range(12):
        s1.append(pd.Series(pr.variables['pr'][j, :]))
        s2.append(pd.Series(pr_dec.variables['pr'][j, :]))

    plt.figure(figsize=(14,5))
    plt.title("JJA drier")

    # for x in range(12):
    #     s1[x].rolling(365).mean().plot(color='b', alpha=0.5) 
    #     s2[x].rolling(365).mean().plot(color='r', alpha=0.5)

    sr1 = s1[grd].rolling(90).mean()
    sr2 = s2[grd].rolling(90).mean()

    plt.plot(idx, sr1, color='k', alpha=0.4)
    plt.plot(idx, sr2, color='r', alpha=0.4)
    plt.legend(["pr", "pr_mod"])
    plt.gcf().autofmt_xdate()
    plt.ylabel("mm s-1")
    plt.xlabel(SITE)

    plt.savefig(f"test_pr_{SITE}_2001-onwrds.png", dpi=300)
    plt.clf()
    plt.close()
    pr_dec.close()


    # # VPD
    vpd = Dataset("vpd_FLUXNET2015.nc")

    season = "JJA"
    vpd_dec = Dataset(f"vpd_dry-summer2001-_FLUXNET2015.nc")

    s1 = []
    s2 = []
    for j in range(12):
        s1.append(pd.Series(vpd.variables['vpd'][j, :]))
        s2.append(pd.Series(vpd_dec.variables['vpd'][j, :]))

    plt.figure(figsize=(14,5))
    plt.title("Dry growing season")

    # for x in range(12):
    #     s1[x].rolling(365).mean().plot(color='b', alpha=0.5) 
    #     s2[x].rolling(365).mean().plot(color='r', alpha=0.5)

    sr1 = s1[grd].rolling(90).mean()
    # .plot(color='b', alpha=0.4) 
    sr2 = s2[grd].rolling(90).mean()
    # ..plot(color='r', alpha=0.4)

    plt.plot(idx, sr1, color='k', alpha=0.4)
    plt.plot(idx, sr2, color='crimson', alpha=0.4)
    plt.legend(["vpd", "vpd mod"])
    plt.gcf().autofmt_xdate()
    plt.ylabel("-kPa")
    plt.xlabel(SITE)

    plt.savefig(f"test_vpd_{SITE}_{season}.png", dpi=300)
    plt.clf()
    plt.close()
    vpd_dec.close()


    season = "drt"
    vpd_dec = Dataset(f"vpd_2003-5_drought_FLUXNET2015.nc")

    s1 = []
    s2 = []
    for j in range(12):
        s1.append(pd.Series(vpd.variables['vpd'][j, :]))
        s2.append(pd.Series(vpd_dec.variables['vpd'][j, :]))

    plt.figure(figsize=(14,5))
    plt.title("2003-5 drought")

    sr1 = s1[grd].rolling(90).mean()
    # .plot(color='b', alpha=0.4) 
    sr2 = s2[grd].rolling(90).mean()
    # ..plot(color='r', alpha=0.4)

    plt.plot(idx, sr1, color='k', alpha=0.4)
    plt.plot(idx, sr2, color='r', alpha=0.4)
    plt.legend(["vpd", "vpd mod"])
    plt.gcf().autofmt_xdate()
    plt.ylabel("-kPa")
    plt.xlabel(SITE)

    plt.savefig(f"test_vpd_{SITE}_{season}.png", dpi=300)
    plt.clf()
    plt.close()
    vpd_dec.close()

pr.close()
ts.close()
vpd.close()
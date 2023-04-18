import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.offsetbox import AnchoredText
from nc_write import SITES_COORDINATES

site_names = []

def get_points():
    global site_names

    out = np.zeros(shape=(12,2))
    s = 0
    for k, v in SITES_COORDINATES.items():
        if k == "SITE":
            continue
        site_names.append(v[2])
        out[s, 0] = v[1]
        out[s, 1] = v[0]
        s += 1
    print(site_names)
    return out.T


def main():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([-1, 36, 36, 60], crs=ccrs.PlateCarree())

    # Create a feature for States/Admin 1 regions at 1:50m from Natural Earth
    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_0_countries',
        scale='50m',
        facecolor='none')


    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(states_provinces, edgecolor='gray')

    # Add a text annotation for the license information to the
    # the bottom right corner.
    text = AnchoredText("FLUXNET2015 sites", loc=4, prop={'size': 8}, frameon=True)
    ax.add_artist(text)
    xs, ys = get_points()
    ax.plot(xs, ys, marker="x", color='red', markersize=5, linestyle='')
    fs = 7
    for i, name in enumerate(site_names):
        if name == "DE-Lnf":
            ax.text(xs[i], ys[i], name, color="k", fontsize=fs, ha='right', va='bottom', transform=ccrs.PlateCarree())
        elif name == "DE-Obe":
            ax.text(xs[i], ys[i], name, color="k", fontsize=fs, ha='left', va='top', transform=ccrs.PlateCarree())
        elif name == "CZ-BK1":
            ax.text(xs[i], ys[i], name, color="k", fontsize=fs, ha='left', va='top', transform=ccrs.PlateCarree())
        elif name == "DE-Hai":
            ax.text(xs[i], ys[i], name, color="k", fontsize=fs, ha='left', va='bottom', transform=ccrs.PlateCarree())
        elif name == "DE-Tha":
            ax.text(xs[i], ys[i], name, color="k", fontsize=fs, ha='right', va='top', transform=ccrs.PlateCarree())
        elif name == "CH-Lae":
            ax.text(xs[i], ys[i], name, color="k", fontsize=fs, ha='right', va='top', transform=ccrs.PlateCarree())
        elif name == "CH-Dav":
            ax.text(xs[i], ys[i], name, color="k", fontsize=fs, ha='right', va='top', transform=ccrs.PlateCarree())
        elif name == "IT-Ren":
            ax.text(xs[i], ys[i], name, color="k", fontsize=fs, ha='left', va='top', transform=ccrs.PlateCarree())
        elif name == "DK-Sor":
            ax.text(xs[i], ys[i] + 2, name, color="k", fontsize=fs, ha='left', va='top', transform=ccrs.PlateCarree())
        else:
            ax.text(xs[i], ys[i], name, color="k", fontsize=fs, ha='right', va='bottom', transform=ccrs.PlateCarree())


    plt.savefig("map.png", dpi=400)


if __name__ == '__main__':
    main()

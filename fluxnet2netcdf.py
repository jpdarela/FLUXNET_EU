from os import makedirs
import concurrent.futures
from nc_write import write_ref_data, write_site_nc, create_gridlist, SITES_COORDINATES
from conversions import mod_mJJAs, mod_make_drought

makedirs("./driver", exist_ok=True)
makedirs("./ref", exist_ok=True)

# Forcing data
VAR = 'tas', 'vpd', 'hurs', 'ps', 'pr', 'wind', 'rsds'

# Reference variables
REF = 'gpp', 'reco', 'nee', 'et'

# FLUXNET 2015 Site names
SITES =  []
for k, v in SITES_COORDINATES.items():
    site_name = v[2]
    if site_name == "name": continue
    SITES.append(site_name.split("-")[-1])

def process_variable(variable):
    write_site_nc(variable)

def process_site(variable, site):
    write_ref_data(variable, site)

def main():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_variable, variable) for variable in VAR]
    # for variable in VAR:
    #     write_site_nc(variable)

    create_gridlist("FLUXNET2015")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for variable in REF:
            for site in SITES:
                futures.append(executor.submit(process_site, variable, site))
    # for variable in REF:
    #     for site in SITES:
    #         write_ref_data(variable, site)

    # create modified PREC
    write_site_nc('pr', mod=mod_mJJAs)
    write_site_nc('pr', mod=mod_make_drought)

    write_site_nc('vpd', mod=mod_mJJAs)
    write_site_nc('vpd', mod=mod_make_drought)

if __name__ == "__main__":
    main()

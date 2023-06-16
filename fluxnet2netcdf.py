from nc_write import write_ref_data, write_site_nc, create_gridlist
from conversions import mod_mJJAs, mod_make_drought

# Forcing data
VAR = 'tas', 'vpd', 'hurs', 'ps', 'pr', 'wind', 'rsds'

# Reference variables
REF = 'gpp', 'reco', 'nee', 'aet'

# FLUXNET 2015 Sites
SITES =  ['Dav', 'Tha', 'Hai', 'Lnf',
          'Obe', 'Lae', 'BK1', 'Lkb',
          'Sor', 'Col', 'Ren', 'Fyo',
          'Bra', 'Vie', 'Hyy', 'Let',
          'Sod', 'Fon', 'Pue', 'Cpz',
          'Lav', 'Loo']

def main():
    for variable in VAR:

        write_site_nc(variable)

    create_gridlist("FLUXNET2015_gridlist")

    for variable in REF:
        for site in SITES:
            write_ref_data(variable, site)

    # create modified PREC
    write_site_nc('pr', mod=mod_mJJAs)
    write_site_nc('pr', mod=mod_make_drought)

    write_site_nc('vpd', mod=mod_mJJAs)
    write_site_nc('vpd', mod=mod_make_drought)

if __name__ == "__main__":
    main()

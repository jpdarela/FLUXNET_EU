from pathlib import Path
import os

# Cycle over the folders in the FLUXNETYYYY and remove all csv files that are not used

# Get a list of all the folders in the FLUXNET2020 directory
folder_path = Path('./FLUXNET2020')
folders = [f for f in folder_path.iterdir() if f.is_dir()]

to_exclude = ["*AUXMETEO*", "*AUXNEE*", "*FLUXNET2015_ERAI_HH*",
              "*FLUXNET2015_ERAI_MM*", "*FLUXNET2015_ERAI_WW*",
              "*FLUXNET2015_ERAI_YY*", "*FLUXNET2015_FULLSET_HH*",
              "*FLUXNET2015_FULLSET_WW*", "*FLUXNET2015_FULLSET_YY*"]

for folder in folders:
    print(folder)
    for string in to_exclude:
        for file in folder.glob(string):
            os.remove(file)




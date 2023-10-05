from utils.nwb_helper import  create_nwb
import os , yaml, argparse
from pynwb import NWBHDF5IO

############### Iterate through every File and Create NWB #####################
###############################################################################

inventory   = '/braintree/home/aliya277/inventory/'
all_files = os.listdir(inventory)
i = 33
print(f'Number of all files: {len(all_files)}')
for folder in all_files[33:]:
    print(f'Creating nwb for folder {folder}')
    path = os.path.join(inventory, folder)
    SessionName = folder
    # try:
    with open(os.path.join(path,"config_nwb.yaml") , "r") as f:
        config = yaml.load(f, Loader = yaml.FullLoader)

    nwbfile = create_nwb(config, path)

    if os.path.isfile(os.path.join(path, f"{SessionName}.nwb")):
        os.remove(os.path.join(path, f"{SessionName}.nwb"))

    print('Saving NWB File..')
    io = NWBHDF5IO(os.path.join(path, f"{SessionName}.nwb"), "w") 
    io.write(nwbfile)
    io.close()
    print(f"File {i} saved.")
    i += 1
    # except: print(f'This file did not work: {SessionName}')
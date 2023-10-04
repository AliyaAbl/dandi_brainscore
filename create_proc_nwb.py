from utils.nwb_helper import  create_nwb
import os , yaml, argparse
from pynwb import NWBHDF5IO

parser = argparse.ArgumentParser(description='Run spike detection.')
parser.add_argument('num', metavar='N', type=int, help='channel number or slurm job array id')
args = parser.parse_args()
num_file = args.num

inventory   = '/braintree/home/aliya277/inventory/'

all_files = os.listdir(inventory)
folder      = all_files[num_file]

path = os.path.join(inventory, folder)
SessionName = folder
try:
    with open(os.path.join(path,"config_nwb.yaml") , "r") as f:
        config = yaml.load(f, Loader = yaml.FullLoader)

    nwbfile = create_nwb(config, path)

    if os.path.isfile(os.path.join(path, f"{SessionName}.nwb")):
            os.remove(os.path.join(path, f"{SessionName}.nwb"))

    print('Saving NWB File..')
    io = NWBHDF5IO(os.path.join(path, f"{SessionName}.nwb"), "w") 
    io.write(nwbfile)
    io.close()
    print("File saved.")
    
except: print(f'This file did not work: {SessionName}')
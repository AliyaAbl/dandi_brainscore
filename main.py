print('Entering main.py')
import os, yaml
from tqdm import tqdm 
from pynwb import NWBHDF5IO
import h5py
import argparse
import fnmatch

from utils.nwb_helper import  create_nwb

parser = argparse.ArgumentParser(description='Run spike detection.')
parser.add_argument('num', metavar='N', type=int, help='channel number or slurm job array id')
args = parser.parse_args()


inventory   = '/braintree/home/aliya277/dandi_brainscore/inventory'
start_time  = 0
stop_time   = 300
timebin     = 10

import gc
for obj in gc.get_objects():   # Browse through ALL objects
    if isinstance(obj, h5py.File):   # Just HDF5 files
        try:
            obj.close()
        except: pass

def find_directories_without_extension(root_dir, extension):
    directory_paths = []
    for foldername, subfolders, filenames in os.walk(root_dir):
        depth = foldername[len(root_dir):].count(os.sep)
        if depth == 1 :
            # Check if any file in the directory has the specified extension
            if not any(filename.endswith(extension) for filename in filenames):
                directory_paths.append(os.path.join(root_dir, foldername))
    return directory_paths


num_file = args.num
all_files = find_directories_without_extension(inventory, '.nwb') #os.listdir(inventory)


print('Running Main Script for File.', num_file)

folder = all_files[num_file]

path = os.path.join(inventory, folder)
SessionName = folder
config_path = '/braintree/home/aliya277/dandi_brainscore/dandi_brainscore'
with open(os.path.join(config_path,"config_nwb.yaml") , "r") as f:
        config = yaml.load(f, Loader = yaml.FullLoader)

print("Creating NWB.")
nwbfile = create_nwb(config,path)
print('NWB file created.')

if 'h5Files' in os.listdir(path):
    print("Adding PSTH.")
    filename = os.listdir(os.path.join(path, 'h5Files'))[0]
    file = h5py.File(os.path.join(path, 'h5Files', filename),'r+') 
    data = file['psth'][:]
    file.close()


    nwbfile.add_scratch(
        data,
        name="psth",
        description="psth, uncorrected [channels x stimuli x reps x timebins]",
        )
    print('PSTH added.')


else: pass
    # psth    = get_psth_from_nwb(nwbfile, path, start_time, stop_time, timebin)
    # data    = psth['psth']

try: io.close()
except:pass

print("Saving File.")
io = NWBHDF5IO(os.path.join(path, f"{SessionName}.nwb"), "w") 
io.write(nwbfile)
io.close()
print("File saved.")

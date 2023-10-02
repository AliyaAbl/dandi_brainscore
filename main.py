import os, yaml
from tqdm import tqdm 
from pynwb import NWBHDF5IO
import h5py

from utils.nwb_helper import  create_nwb, get_psth_from_nwb

inventory   = '/braintree/home/aliya277/dandi_brainscore/inventory'
start_time  = 0
stop_time   = 300
timebin     = 10
counter     = 0

import gc
for obj in gc.get_objects():   # Browse through ALL objects
    if isinstance(obj, h5py.File):   # Just HDF5 files
        try:
            obj.close()
        except: pass

print('Running Main Script.')

for folder, num_file in (zip(os.listdir(inventory), range(len(os.listdir(inventory))))):
    print(f"Folder: {num_file}/{len(os.listdir(inventory))}")

    path = os.path.join(inventory, folder)
    SessionName = folder
    config_path = '/om/user/aliya277/dandi_brainscore'
    with open(os.path.join(config_path,"config_nwb.yaml") , "r") as f:
            config = yaml.load(f, Loader = yaml.FullLoader)

    print("Creating NWB.")
    nwbfile = create_nwb(config,path)
    print('NWB file created.')

    if 'h5Files' in os.listdir(path):
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


    else: counter +=1
        # psth    = get_psth_from_nwb(nwbfile, path, start_time, stop_time, timebin)
        # data    = psth['psth']

    try: io.close()
    except:pass

    io = NWBHDF5IO(os.path.join(path, f"{SessionName}.nwb"), "w") 
    io.write(nwbfile)
    io.close()
    print("File saved.")

print(f'{counter} SpikeTimes do not have an h5 file.')
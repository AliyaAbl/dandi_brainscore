import numpy as np
import os
import pandas as pd


############### Validate All Files Using pwnyb, nwbinspectors #################
###############################################################################

from pynwb import validate
from nwbinspector import inspect_nwbfile
from dandi.validate import validate as dandival


df = pd.read_excel( '/braintree/home/aliya277/dandi_brainscore/pico_inventory.xlsx'  )
SubjectName = 'pico'
storage_dir = '/braintree/home/aliya277/inventory'
array_meta_path  = '/braintree/data2/active/users/sgouldin/array-metadata'
 
all_nwb_paths = []

for index, DataFrame in df.iterrows():
        
    if DataFrame['Has SpikeTime'] == 1:

        date = f"20{DataFrame['date']}"
        if len(str(DataFrame['time'])) != 6: time = f"0{DataFrame['time']}"
        else: time = str(DataFrame['time'])
        
        if DataFrame['ImageSet'] == 'normalizers':
            directory = f'norm_FOSS.sub_pico.{date}_{time}.proc'
        elif DataFrame['ImageSet'] == 'normalizers-HVM':
            directory = f'norm_HVM.sub_pico.{date}_{time}.proc'
        else: 
            directory = f"exp_{DataFrame['ImageSet']}.sub_pico.{date}_{time}.proc"
            
        imagesetdir = os.path.join(storage_dir, ".".join(directory.split(".")[0:1]))
        subjectdir  = os.path.join(storage_dir, imagesetdir, ".".join(directory.split(".")[0:2]))

        all_nwb_paths.append(os.path.join(subjectdir,directory, f"{directory}.nwb"))


num_files = len(all_nwb_paths)

for i in range(63,num_files):
    j = i
    if i + 1 < num_files: i += 1
    else: i = num_files
    print(f"Checking Files for {j}:{i}")
    pynwb_validation = validate(paths = all_nwb_paths[j:i])
    print(pynwb_validation)

i = 0
for path in all_nwb_paths:
    results = list(inspect_nwbfile(nwbfile_path=path))
    print(i, results)
    i +=1
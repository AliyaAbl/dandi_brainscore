
from dateutil.tz import tzlocal
from datetime import datetime, date
from uuid import uuid4
import yaml
import os
import json
import numpy as np
from collections import OrderedDict
from ruamel.yaml import YAML


"""
Config File Sarah RSVP. Please change anything that does not fit for your experiment.
"""

json_file_path          = os.path.join(os.getcwd(), '021023_pico_mapping_noCIT_adapter_version.json')
weight                  = '0.02 kg'
numimages               = 'x'
imageset                = 'x'
session_id              = 'x'
nrep                    = 'x'
stimon                  = 'x'
stimoff                 = 'x'
related_publications    = ['']
adapter_serial          = 'x'


def create_yaml(path):
    f                   = open(json_file_path)
    data                = json.load(f)
    bank_assignment     = np.unique(np.array(list(data['bank'].values())))              # unique for each group
    num_arrays          = len(bank_assignment)
    adapter_versions    = np.unique(np.array(list(data['adapter_version'].values())))   # unique for each group
    subregions          = np.unique(np.array(list(data['subregion'].values())))         # unique for each group
    region              = np.unique(np.array(list(data['region'].values())))            # same for all
    hemispheres         = np.unique(np.array(list(data['hemisphere'].values())))        # same for all
    serialnumbers       = np.unique(np.array(list(data['arr'].values())))               # same for all
    positions           = np.zeros((len(list(data['adapter_version'].values())), 3))    # row, col, number
    positions[:,0]      = np.array(list(data['row'].values()))
    positions[:,1]      = np.array(list(data['col'].values()))
    positions[:,2]      = np.array(list(data['elec'].values()))

    if len(adapter_versions)!= num_arrays: adapter_versions = np.repeat(adapter_versions, (num_arrays/len(adapter_versions)))
    if len(subregions)      != num_arrays: subregions       = np.repeat(subregions, (num_arrays/len(subregions)))
    if len(hemispheres)     != num_arrays: hemispheres      = np.repeat(hemispheres, (num_arrays/len(hemispheres)))
    if len(region)          != num_arrays: region           = np.repeat(region, (num_arrays/len(region)))
    if len(serialnumbers)   != num_arrays: serialnumbers    = np.repeat(serialnumbers, (num_arrays/len(serialnumbers)))


    config_dict = dict()

    config_dict['subject'] = {
                'subject_id':   'pico',
                'date_of_birth': datetime(2019, 12, 4, tzinfo = tzlocal()), #year, month, day
                'sex':          'male',
                'species':      'Macaca mulatta',
                'weight':       weight
                }
    
    config_dict["session_info"] = {
                'session_id': '{}'.format(session_id),
                'session_description': 'Number of Repetitions: {}'.format(nrep),
                }
    
    config_dict['paths'] = {
                    'intandata': '/braintree/data2/active/users/sgouldin/projects/oasis900/monkeys/pico/intanraw/pico_oasis900_230509_114338',
                    }
    
    config_dict['general'] ={
                'experiment_info': {
                    'experiment_description': 'Task: Rapid serial visual presentation (RSVP). Trial: Try 8 images - {} ms on, {} ms grey buch check mworks file for specifics. Reward: juice reward after every trial. Imageset: {} Images of {}'.format(stimon, stimoff, numimages, imageset),
                    'keywords': ['Vistual Stimuli', 'Object Recognition', 'Inferior temporal cortex (IT)', 'Ventral visual pathway'],
                    'related_publications': related_publications,
                    'protocol': 'Rapid serial visual presentation (RSVP)', 
                    'surgery' : '3x Utah Array Implant + Headpost',
                    },
                'lab_info': {
                    'university':  'Massachusetts Institute of Technology',
                    'institution': 'McGovern Institute for Brain Research',
                    'lab': 'DiCarlo',
                    'experimenter': 'Goulding, Sarah',
                    }
                }

    config_dict['hardware'] = {
                    'electrode_name': 'Electrode',
                    'electrode_description': 'Utah CerePort Array with a single electrode array',
                    'electrode_manuf': '2020 Blackrock Microsystems, LLC',
                    'system_name': 'RecordingSystem',
                    'system_description': 'RHD Recording System',
                    'system_manuf': '2010-2023 Intan Technologies', 
                    'adapter_name': 'Utah Array Pedestal Connector',
                    'adapter_description': 'Connects Utah Pedestal to Intan RHD Recording System',
                    'adapter_manuf': 'Ripple Neuro', 
                    'photodiode_name': 'DET36A2 Biased Si Detector',
                    'photodiode_description': 'Photodiode for detecting image presentation times. Comes with DET2A Power Adapter',
                    'photodiode_manuf': 'Thorlabs Inc.', 
                    'monitor_name': 'LG UltraGear',
                    'monitor_description': 'LG 32GP850-B 32 UltraGear QHD (2560 x 1440) Nano IPS Gaming Monitor w/ 1ms (GtG) Response Time & 165Hz Refresh Rate.\
                        Manually color calibrated and set to 120 HZ refresh rate.',
                    'monitor_manuf': 'LG', 
                    }
    
    config_dict['software'] ={
                    'mwclient_version': 'Version 0.11 (2022.02.15)',
                    'mwserver_version': 'Version 0.11 (2022.02.15)',
                    'OS': 'macOS Monterery on MAC Pro (Late 2013)',
                    'intan_version': 'Version 3.1.0'
                    }
   
                
    config_dict['metadata'] = {
                    'nwb_version' : '2.6.0',
                    'file_create_date': datetime.now(tzlocal()),
                    'identifier': str(uuid4()), 
                    'session_start_time':datetime.now(tzlocal())
                    }
                
    config_dict['array_info'] = {'intan_electrode_labeling_[row,col,id]':json.dumps(positions.tolist())}

    for arr, i in zip(bank_assignment, range(num_arrays)) :
            config_dict['array_info']['array_{}'.format(arr)] = {
                        'position': [0.0,0.0,0.0],
                        'serialnumber':     str(serialnumbers[i]),
                        'adapterversion':   str(adapter_versions[i]),
                        'hemisphere':       str(hemispheres[i]),
                        'region':           str(region[i]),
                        'subregion':        str(subregions[i]),
                        }  

    yaml = YAML()
    with open(os.path.join(path,"config_nwb.yaml"), 'w') as yamlfile:
        data = yaml.dump((config_dict), yamlfile)
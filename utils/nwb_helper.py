from datetime import datetime
from uuid import uuid4
from dateutil.tz import tzlocal
import numpy as np
import scipy.io
import os, yaml, glob, json
import pandas as pd
from nwbwidgets import nwb2widget
import pynwb
from pynwb import NWBHDF5IO, NWBFile, TimeSeries
from pynwb.behavior import Position, SpatialSeries
from pynwb.epoch import TimeIntervals
from pynwb.file import Subject
from pynwb.misc import Units        
from pynwb.ecephys import SpikeEventSeries
import shutil
import logging
from tqdm import tqdm
import pytz


def read_names(filename):
    assignment  = filename.split('.')[0].split('-')[1]
    number      = filename.split('.')[0].split('-')[2]
    return np.asarray([assignment, number])

def create_nwb(config, path):

    SessionDate = path.split('/')[-1].split('.')[-2].split('_')[0]
    SessionTime = path.split('/')[-1].split('.')[-2].split('_')[1]
    SubjectName = path.split('/')[-1].split('.')[1].split('_')[1]
    date_format = "%Y%m%d %H%M%S"

    if config['subject']['subject_id'].lower() != SubjectName.lower():
        raise ValueError("Subject Name incorrect.")
    
    session_start_time_ = datetime.strptime(SessionDate+' '+SessionTime, date_format)
    # Define the timezone you want to use (e.g., 'US/Eastern' for Boston)
    desired_timezone = pytz.timezone('US/Eastern')
    session_start_time = desired_timezone.localize(session_start_time_)


    ################ CREATE NWB FILE WITH METADATA ################################
    ###############################################################################
    nwbfile = NWBFile(
        session_description     = config['session_info']['session_description'],
        identifier              = config['metadata']['identifier'],
        session_start_time      = session_start_time,
        file_create_date        = config['metadata']['file_create_date'],
        experimenter            = config['general']['lab_info']['experimenter'],
        experiment_description  = config['general']['experiment_info']['experiment_description'],
        session_id              = config['session_info']['session_id'],
        lab                     = config['general']['lab_info']['lab'],                     
        institution             = config['general']['lab_info']['institution'],                                    
        keywords                = config['general']['experiment_info']['keywords'],
        protocol                = config['general']['experiment_info']['protocol'],
        related_publications    = config['general']['experiment_info']['related_publications'],
        surgery                 = config['general']['experiment_info']['surgery']
    )

    ################ CREATE SUBJECT ################################################
    ################################################################################
    nwbfile.subject = Subject(
        subject_id  = config['subject']['subject_id'],
        date_of_birth= config['subject']['date_of_birth'],
        species     = config['subject']['species'],
        sex         = config['subject']['sex'],
    )

    ################ CREATE HARDWARE LINKS #########################################
    ################################################################################
    nwbfile.create_device(
        name        = config['hardware']['system_name'], 
        description = config['hardware']['system_description'], 
        manufacturer= config['hardware']['system_manuf']
    )

    nwbfile.create_device(
        name        = config['hardware']['adapter_manuf'], 
        description = config['hardware']['adapter_description'], 
        manufacturer= config['hardware']['adapter_manuf']
    )

    nwbfile.create_device(
        name        = config['hardware']['monitor_name'], 
        description = config['hardware']['monitor_description'], 
        manufacturer= config['hardware']['monitor_manuf']
    )

    nwbfile.create_device(
        name        = config['hardware']['photodiode_name'], 
        description = config['hardware']['photodiode_description'], 
        manufacturer= config['hardware']['photodiode_manuf']
    )
    
    nwbfile.create_device(
        name        = 'Software Used', 
        description = str(['Mworks Client: '+config['software']['mwclient_version'],\
                        'Mworks Server: '+config['software']['mwserver_version'],\
                        'OS: '+config['software']['OS'],\
                        'Intan :'+config['software']['intan_version']])
    )

    ################ CREATE ELECTRODE LINKS ########################################
    ################################################################################
    electrodes = nwbfile.create_device(
        name        = config['hardware']['electrode_name'], 
        description = config['hardware']['electrode_description'], 
        manufacturer= config['hardware']['electrode_manuf']
    )

    all_files = sorted(os.listdir(os.path.join(path, 'SpikeTimes')))
    
    name_accumulator = []
    for file in all_files:
        name_accumulator.append(read_names(file))
    names = np.vstack(name_accumulator)

    nwbfile.add_electrode_column(name="label", description="label of electrode")
    groups, count_groups = np.unique(names[:,0], return_counts =True)
    ids                  = names[:,1]
    counter              = 0
    # create ElectrodeGroups A, B, C, ..
    for group, count_group in zip(groups, count_groups):
        electrode_group = nwbfile.create_electrode_group(
            name        = "group_{}".format(group),
            description = "Serialnumber: {}. Adapter Version: {}".format(config['array_info']['array_{}'.format(group)]['serialnumber'],\
                            config['array_info']['array_{}'.format(group)]['adapterversion']),
            device      = electrodes,
            location    = 'hemisphere, region, subregion: '+str([config['array_info']['array_{}'.format(group)]['hemisphere'],\
                                config['array_info']['array_{}'.format(group)]['region'],
                                config['array_info']['array_{}'.format(group)]['subregion']]),
            position    = config['array_info']['array_{}'.format(group)]['position']
        )

        # create Electrodes 001, 002, ..., 032 in ElectrodeGroups per channel
        for ichannel in range(count_group):
            nwbfile.add_electrode(
                group       = electrode_group,
                label       = ids[counter],
                location    = 'row, col, elec'+str(json.loads(config['array_info']['intan_electrode_labeling_[row,col,id]'])[counter])
            )
            counter += 1     

    ################ ADD SPIKE TIMES ###############################################
    ################################################################################

    nwbfile.add_unit_column(name="unit", description="millisecond") 
    for filename, i in zip(sorted(os.listdir(os.path.join(path, 'SpikeTimes'))), range(len(os.listdir(os.path.join(path, 'SpikeTimes'))))):
        [assignment, number] = read_names(filename)
        file_path = os.path.join(path, 'SpikeTimes', filename)
        data = scipy.io.loadmat(file_path, squeeze_me=True,
                        variable_names='spike_time_ms')['spike_time_ms']
        nwbfile.add_unit(
            spike_times = data, 
            electrodes  = [i],
            electrode_group = nwbfile.electrode_groups[f'group_{assignment}'], 
            unit = 'ms'
        )

    ################ ADD TRIAL TIMES ###############################################
    ################################################################################
    last_spike = data[-1]
    with open(os.path.join(path, 'NWBInfo.txt')) as f:
        lines = f.readlines()
        line1 = lines[0].split(',')[0]
        StimOnnOff = [float(line1.split('/')[0]),float(line1.split('/')[1])] 

    on_start  = 0
    on_dur    = StimOnnOff[1]
    off_dur   = StimOnnOff[1]

    
    nwbfile.add_trial_column(name="unit", description="millisecond")
    while on_start < last_spike:

        nwbfile.add_trial(
            start_time= float(on_start),
            stop_time = float(on_start+on_dur),
            unit = 'ms')
    
        on_start += on_dur+off_dur

    return nwbfile

def get_psth_from_nwb(nwbfile, path, start_time, stop_time, timebin, n_stimuli=None):

    # Find the MWORKS File
    with open(os.path.join(path, 'NWBInfo.txt')) as f:
        lines = f.readlines()
        line2 = lines[0].split(',')[1]
        ind = line2.split('/').index('intanproc')
        mwk_file = glob.glob(os.path.join('/', *line2.split('/')[0:ind], 'mworksproc', \
                '_'.join(map(str, line2.split('/')[ind+1].split('_')[0:3]))+'*_mwk.csv'))   
        
    assert len(mwk_file) == 1
    mwk_file = mwk_file[0]
    assert os.path.isfile(mwk_file)==True

    ################ MODIFIED FROM THE SPIKE-TOOLS-CHONG CODE ######################
    ################################################################################
    
    mwk_data = pd.read_csv(mwk_file)
    mwk_data = mwk_data[mwk_data.fixation_correct == 1]
    if 'photodiode_on_us' in mwk_data.keys():
        samp_on_ms = np.asarray(mwk_data['photodiode_on_us']) / 1000.
        logging.info('Using photodiode signal for sample on time')
    else:
        samp_on_ms = np.asarray(mwk_data['samp_on_us']) / 1000.
        logging.info('Using MWorks digital signal for sample on time')
    
    # Load spikeTime file for current channel
    spikeTimes = nwbfile.units[:].spike_times
    # Re-order the psth to image x reps
    max_number_of_reps = max(np.bincount(mwk_data['stimulus_presented']))  # Max reps obtained for any image
    if max_number_of_reps == 0:
        exit()
    mwk_data['stimulus_presented'] = mwk_data['stimulus_presented'].astype(int)  # To avoid indexing errors
    
    if n_stimuli is None:
            image_numbers = np.unique(mwk_data['stimulus_presented'])  # TODO: if not all images are shown (for eg, exp cut short), you'll have to manually type in total # images
    else:
        image_numbers = np.arange(1,n_stimuli+1) # all of my image starts with #1

    timebase = np.arange(start_time, stop_time, timebin)
    PSTH = np.full((len(image_numbers), max_number_of_reps, len(timebase),spikeTimes.shape[0]), np.nan)

    for num in range(spikeTimes.shape[0]):
        spikeTime = np.asanyarray(spikeTimes[num])
        osamp = 10
        psth_bin = np.zeros((len(samp_on_ms), osamp*(stop_time-start_time)))
        psth_matrix = np.full((len(samp_on_ms), len(timebase)), np.nan)

        for i in range(len(samp_on_ms)):

            sidx = np.floor(osamp*(spikeTime[(spikeTime>=(samp_on_ms[i]+start_time))*(spikeTime<(samp_on_ms[i]+stop_time))]-(samp_on_ms[i]+start_time))).astype(int)
            psth_bin[i, sidx] = 1
            psth_matrix[i] = np.sum(np.reshape(psth_bin[i], [len(timebase), osamp*timebin]), axis=1)
        
        
        psth = np.full((len(image_numbers), max_number_of_reps, len(timebase)), np.nan)  # Re-ordered PSTH

        for i, image_num in enumerate(image_numbers):
            index_in_table = np.where(mwk_data.stimulus_presented == image_num)[0]
            selected_cells = psth_matrix[index_in_table, :]
            psth[i, :selected_cells.shape[0], :] = selected_cells

        logging.info(psth.shape)
        # Save psth data
        PSTH[:,:,:,num] = psth
        
    meta = {'start_time_ms': start_time, 'stop_time_ms': stop_time, 'tb_ms': timebin}
    cmbined_psth = {'psth': PSTH, 'meta': meta}

    return cmbined_psth
   
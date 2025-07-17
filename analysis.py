from TempAnalyzer import *
import matplotlib.pyplot as plt  
    
dataset_cool_dds = {
    'base_name' : 'cool_dds',
    'x_label' : 'Cool DDS Frequency',
    'unit' : '',
    'iterator' : [10, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11]
}

dataset_time_ramp_aom = {
    'base_name' : 'time_ramp_aom',
    'x_label' : 'Ramp Time',
    'unit' : 'ms',
    'iterator' : [0.4, 0.6, 1, 2, 3, 4, 5, 10, 15, 20]
}

dataset_rep_delta = {
    'base_name' : 'rep_delta',
    'x_label' : 'Rep. Red Detuning',
    'unit' : '',
    'iterator' : [5, 10, 15, 20, 25, 30]
}

dataset_aom_amp = {
    'base_name' : 'aom_amp',
    'x_label' : 'AOM Amplitude',
    'unit' : '',
    'iterator' : [50, 100, 200, 300, 400, 500, 600, 700]
}

dataset_list = [dataset_cool_dds, dataset_time_ramp_aom, dataset_rep_delta, dataset_aom_amp]

for dataset in dataset_list:
    Analysis_and_Plotting(dataset)

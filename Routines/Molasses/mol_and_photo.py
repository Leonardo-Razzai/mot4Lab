from astropy.io import fits
import matplotlib.pyplot as plt
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
gp_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(gp_dir)

import Params
from Params import RT_PARAMS
from Modules.MOTAcqLib import *
from Modules.TempAnalyzer import *

mot_base_name = 'molasses_and_tof'

# TOF_VALS = [5., 10., 15., 20., 25., 30.]

# for TOF in TOF_VALS:
#     RT_PARAMS['<TOF>'] = TOF

#     print(f'\nTof = {TOF:.1f} ms')
#     for i in range(1, 4):
#         fits_fname = F'T_meas_tof={TOF:.0f}ms_{i:02d}'
#         print(f'Acquiring {fits_fname}')
#         setup_camera(gain=Params.CAM_GAIN, exp_time=Params.CAM_EXP_TIME)
#         write_and_acquire_mot(mot_base_name, fits_fname, params=RT_PARAMS)

for i in range(1, 4):
    fits_fname = F'odt_off_{i:02d}'
    print(f'Acquiring {fits_fname}')
    setup_camera(gain=Params.CAM_GAIN, exp_time=Params.CAM_EXP_TIME)
    write_and_acquire_mot(mot_base_name, fits_fname, params=RT_PARAMS)

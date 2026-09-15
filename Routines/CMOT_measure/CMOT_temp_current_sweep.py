import time
import os
import sys
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(grandparent_dir)


from Modules.MOTAcqLib import *
from Modules.TempAnalyzer import *

MOT_BASE_NAME = 'CMOT_temp'
FITS_BASE_NAME = MOT_BASE_NAME

RT_PARAMS = {
    '<TOF>': 30,
    '<CMOT>': 8,    
}

cam_gain = 34 # dB
CAM_EXP_TIME = 1000 # us

tof_values = range(3, 31, 3)
current_values = [8, 12, 16, 20]


print("\n" + "-"*30)
print('MOLASSES AND IMAGE ACQUISITION')

for current in current_values:
    RT_PARAMS['<CMOT>'] = current
    cam_gain=cam_gain + 1

    for t in tof_values:
        RT_PARAMS['<TOF>'] = t

        fits_fname = FITS_BASE_NAME + f'_CMOT={current}_tof={t:02d}'
        print(' --- Start exp -- ' + fits_fname)

        setup_camera(gain=cam_gain, exp_time=CAM_EXP_TIME, n=2)

        write_and_acquire_mot(MOT_BASE_NAME, fits_fname, params=RT_PARAMS, n=2)

        time.sleep(2)
        
	
	

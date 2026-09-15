import numpy as np
import subprocess
import time
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(grandparent_dir)

from Modules.MOTAcqLib import *
from Modules.TempAnalyzer import *

# Setup 
CAM_GAIN = 10 # dB
CAM_EXP_TIME = 1000 # us


MOT_BASE_NAME = 'change_By'
FITS_BASE_NAME = MOT_BASE_NAME

RT_PARAMS= {
    '<shimY>' : -1200.0 ,
}

shimy_values = range(-1000, 1000, 100)

print("\n"+ "-"*30)
print ('MOLASSES SHIM CALIBRATION')

for shimy in shimy_values:
			RT_PARAMS['<shimY>'] = shimy

			fits_fname = FITS_BASE_NAME + f'_shim_y={shimy}'
            #print('----Start exp ---' + fits_fname)
            
			setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME,n=2)
			print('Setup camera ok')

			write_and_acquire_mot(MOT_BASE_NAME, fits_fname, params=RT_PARAMS,n=2)

			time.sleep(2)

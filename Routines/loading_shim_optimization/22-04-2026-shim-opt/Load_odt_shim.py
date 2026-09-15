import time
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(current_dir))
grand_grandparent_dir  = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
grand_grand_grandparent_dir  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
sys.path.append(grandparent_dir)
sys.path.append(grand_grandparent_dir)
sys.path.append(grand_grand_grandparent_dir)

from Modules.MOTAcqLib import *
from Modules.TempAnalyzer import *


MOT_BASE_NAME = 'Load_odt'
FITS_BASE_NAME = MOT_BASE_NAME
REPETITIONS = 5

RT_PARAMS= {
    '<shimX>': -260 ,
    '<shimY>': -310 ,
    '<shimZ>': -120 ,
    '<ODTamp>' : 0 ,
}

SHIM_BASE_VAL = {
    '<shimX>': -260 ,
    '<shimY>': -310 ,
    '<shimZ>': -120 
}

current_values = reversed(list(range(-500, 0, 50)))

CAM_GAIN = 6 #dB
CAM_EXP_TIME = 1000 #us


print("\n"+ "-"*30)

shim_keys = ['<shimX>']

for shim_key in shim_keys:
    for curr in current_values:
        shim_current = curr
        RT_PARAMS[shim_key] = shim_current
        for i in range(1, REPETITIONS + 1):
            fits_fname = FITS_BASE_NAME + (f'_{shim_key}={shim_current:03d}_{i:02d}')
            fits_fname = fits_fname.replace("<", "").replace(">", "")

            RT_PARAMS['<ODTamp>'] = 0
            fits_fname = 'odt_off_'+ fits_fname
            setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME, n=1, manta=False)
            print(' --- Start bkg -- '+fits_fname)
            write_and_acquire_mot(MOT_BASE_NAME, fits_fname, params=RT_PARAMS, n=1, manta=True)
            time.sleep(5)

            fits_fname = FITS_BASE_NAME + (f'_{shim_key}={shim_current:03d}_{i:02d}')
            fits_fname = fits_fname.replace("<", "").replace(">", "")
            RT_PARAMS['<ODTamp>'] = 400
            setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME, n=1, manta=False)
            print(' --- Start exp -- '+fits_fname)
            write_and_acquire_mot(MOT_BASE_NAME, fits_fname, params=RT_PARAMS, n=1, manta=True)
            time.sleep(5)
    
    RT_PARAMS[shim_key] = SHIM_BASE_VAL[shim_key]


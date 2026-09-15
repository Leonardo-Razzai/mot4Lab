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


MOT_BASE_NAME = 'Load_odt_MOT_time'
FITS_BASE_NAME = MOT_BASE_NAME
REPETITIONS = 5

RT_PARAMS= {
    '<tmot>':    5,
    '<ODTamp>' : 0,
}


CAM_GAIN = 6 #dB
CAM_EXP_TIME = 1000 #us


print("\n"+ "-"*30)

t_mot_values = range(100, 7000, 200)

for t_mot in t_mot_values:
    RT_PARAMS['<tmot>'] = t_mot
    print(f't_mot= {t_mot}')
    
    for i in range(1, REPETITIONS + 1):
    	fits_fname = FITS_BASE_NAME + (f'_{t_mot}_{i:02d}')
    	
    	RT_PARAMS['<ODTamp>'] = 0
    	fits_fname = 'odt_off_'+ fits_fname
    	setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME, n=1, manta=False)
    	print(' --- Start bkg -- '+fits_fname)
    	write_and_acquire_mot(MOT_BASE_NAME, fits_fname, params=RT_PARAMS, n=1, manta=True)
    	time.sleep(3)
    	
    	fits_fname = FITS_BASE_NAME + (f'_{t_mot}_{i:02d}')
    	RT_PARAMS['<ODTamp>'] = 400
    	setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME, n=1, manta=False)
    	print(' --- Start exp -- '+fits_fname)
    	write_and_acquire_mot(MOT_BASE_NAME, fits_fname, params=RT_PARAMS, n=1, manta=True)
    	time.sleep(3)


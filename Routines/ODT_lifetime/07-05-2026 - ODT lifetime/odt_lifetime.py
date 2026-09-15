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


MOT_BASE_NAME = 'odt_lifetime'
FITS_BASE_NAME = MOT_BASE_NAME + 't_odt'
REPETITIONS = 5

RT_PARAMS= {
    '<todt>':    3,
    '<ODTamp>' : 0,
}


CAM_GAIN = 6 #dB
CAM_EXP_TIME = 1000 #us


print("\n"+ "-"*30)

t_odt_values = range(24, 35, 3)

for t_odt in t_odt_values:
	t_odt=t_odt-0.1
	RT_PARAMS['<todt>'] = t_odt
	print(f't_odt= {t_odt}')
	
	for i in range(1, REPETITIONS + 1):
		fits_fname = FITS_BASE_NAME + (f'={t_odt}_{i:02d}')

		# bkg acquisition
		RT_PARAMS['<ODTamp>'] = 0
		fits_fname = 'odt_off_'+ fits_fname
		setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME, n=1, manta=True)
		print(' --- Start bkg -- '+fits_fname)
		write_and_acquire_mot(MOT_BASE_NAME, fits_fname, params=RT_PARAMS, n=1, manta=True)
		time.sleep(3)
		
		# ODT On acquisition
		fits_fname = FITS_BASE_NAME + (f'={t_odt}_{i:02d}')
		RT_PARAMS['<ODTamp>'] = 420
		setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME, n=1, manta=True)
		print(' --- Start exp -- '+fits_fname)
		write_and_acquire_mot(MOT_BASE_NAME, fits_fname, params=RT_PARAMS, n=1, manta=True)
		time.sleep(3)


import time
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(grandparent_dir)

import Params 
from Params import *
from Modules.MOTAcqLib import *
from Modules.TempAnalyzer import *

mot_base_name = 'Shim_delay'
delays = range(50, 5000, 200)

imgs_on = []
print('\n----------------------------------------------------------')
print('MOLASSES + ODT AND IMAGE ACQUISITION')
j = 0
for t in delays:
    RT_PARAMS['<TDELAY>'] = t  
    for i in range(1, 4):
        fits_fname = f'Shim_delay={t:04d}_odt400_{i:02d}'
        setup_camera(gain=Params.CAM_GAIN, exp_time=Params.CAM_EXP_TIME)
        print('\n Setting up camera')
        write_and_acquire_mot(mot_base_name, fits_fname, params=RT_PARAMS)
        print('--- Start exp')
        time.sleep(2)
      
        fits_fname = f'Shim_delay={t:04d}_odt000_{i:02d}'
        setup_camera(gain=Params.CAM_GAIN, exp_time=Params.CAM_EXP_TIME)
        write_and_acquire_mot(mot_base_name, fits_fname, params=RT_PARAMS)
        time.sleep(2)

SHOW = True
if SHOW:
    img = Image(os.path.join(IMG_FOLDER, fits_fname) + '.fits.gz')
    img.select_roi(0, 450, 100, 600)
    img.show_img()

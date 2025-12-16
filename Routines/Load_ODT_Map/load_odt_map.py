from astropy.io import fits
import matplotlib.pyplot as plt
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(grandparent_dir)

import Params 
from Params import *
from Modules.MOTAcqLib import * # Removed the dots (...)
from Modules.TempAnalyzer import * # Removed the dots (...)

fits_fname = f'Ix={RT_PARAMS['<SHIM_X>']:.0f}_Iz={RT_PARAMS['<SHIM_Z>']:.0f}'
mot_base_name = 'load_odt_map'

for label, value in RT_PARAMS.items():
    print(label, value)


# setup_camera(gain=Params.CAM_GAIN, exp_time=Params.CAM_EXP_TIME)
mot_fname = write_mot_file(mot_base_name, RT_PARAMS)
# acquire_img(mot_fname=mot_fname, fits_fname=fits_fname, t_probe=Params.T_PROBE)

# SHOW = False
# if SHOW:
#     img = Image(os.path.join(IMG_FOLDER, fits_fname) + '.fits.gz')
#     img.select_roi(0, 450, 100, 600)
#     img.show_img()
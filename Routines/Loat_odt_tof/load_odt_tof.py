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

mot_base_name = 'load_odt_map'
shim_x_vals = np.arange(-1100., -450., 50.)
shim_z_vals = np.arange(-500., 50., 50.)

for shim_x in shim_x_vals:
    for shim_z in shim_z_vals:

        RT_PARAMS['<SHIM_X>'] = float(shim_x)
        RT_PARAMS['<SHIM_Z>'] = float(shim_z)
        print(f'SHIM_X = {shim_x:.1f} mA, SHIM_Z = {shim_z:.1f} mA')

        for i in range(1, 4):
            fits_fname = f'Ix={shim_x:.0f}mA_Iz={shim_z:.0f}mA_{i:02d}'
            setup_camera(gain=Params.CAM_GAIN, exp_time=Params.CAM_EXP_TIME)
            write_and_acquire_mot(mot_base_name, fits_fname, params=RT_PARAMS)
            time.sleep(2)

SHOW = False
if SHOW:
    img = Image(os.path.join(IMG_FOLDER, fits_fname) + '.fits.gz')
    img.select_roi(0, 450, 100, 600)
    img.show_img()
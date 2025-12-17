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
shim_x_vals = np.arange(-1100., -500., 100.)
shim_z_vals = np.arange(-500., 0., 100.)

for shim_x in shim_x_vals:
    for shim_z in shim_z_vals:

        RT_PARAMS['<SHIM_X>'] = float(shim_x)
        RT_PARAMS['<SHIM_Z>'] = float(shim_z)
        print(f'SHIM_X = {shim_x:.1f} mA, SHIM_Z = {shim_z:.1f}')

        for i in range(1, 4):
            fits_fname = f'odt_on_Ix={shim_x:.0f}mA_Iz={shim_z:.0f}mA_{i:02d}'
            setup_camera(gain=Params.CAM_GAIN, exp_time=Params.CAM_EXP_TIME)
            mot_fname = write_mot_file(mot_base_name, RT_PARAMS)
            time.sleep(0.5)
            acquire_img(mot_fname=mot_fname, fits_fname=fits_fname, t_probe=Params.T_PROBE)

SHOW = False
if SHOW:
    img = Image(os.path.join(IMG_FOLDER, fits_fname) + '.fits.gz')
    img.select_roi(0, 450, 100, 600)
    img.show_img()
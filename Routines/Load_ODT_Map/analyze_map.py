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

imgs_on = []
print('\n ---------------------------- Taking averages: --------------------------------')
for shim_x in shim_x_vals:
    shim_x_imgs = []
    for shim_z in shim_z_vals:
        print(f'ODT ON: SHIM_X = {shim_x:.1f} mA, SHIM_Z = {shim_z:.1f} --> DONE')

        avg_im = 0.0
        for i in range(1, 4):
            # fits_fname = f'odt_on_Ix={shim_x:.0f}mA_Iz={shim_z:.0f}mA_{i:02d}.fits.gz'
            # img = Image(os.path.join(IMG_FOLDER, fits_fname) + '.fits.gz')
            # img.select_roi(0, 450, 100, 600)
            # avg_im += img
            pass

        avg_im /= i
        shim_x_imgs.append(avg_im)
    
    imgs_on.append(shim_x_imgs)

print(f'ODT OFF --> DONE')
img_off = 0.0
for i in range(1, 4):
    # fits_fname = f'odt_off_{i:02d}.fits.gz'
    # img = Image(os.path.join(IMG_FOLDER, fits_fname) + '.fits.gz')
    # img.select_roi(0, 450, 100, 600)
    # img_off += img
    pass

img_off / i

print('\n --------------------- Subtracting background due to MOT: -----------------------')
no_bkg_imgs = []
peaks = []
for (i, shim_x) in enumerate(shim_x_vals):
    shim_x_imgs = []
    peaks_x = []
    for (j, shim_z) in enumerate(shim_z_vals):
        print(f'SHIM_X = {shim_x:.1f} mA, SHIM_Z = {shim_z:.1f}. Element ({i}, {j}) of Map')

        no_bkg_img = imgs_on[i][j] - img_off
        shim_x_imgs.append(no_bkg_img)
        peaks_x.append(np.max(no_bkg_img))

    no_bkg_imgs.append(shim_x_imgs)
    peaks.append(peaks_x)
    
no_bkg_imgs = np.array(no_bkg_imgs)
peaks = np.array(peaks)

print(no_bkg_imgs.shape)
print(peaks.shape)
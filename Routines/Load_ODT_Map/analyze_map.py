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
shim_x_vals = np.arange(-950., -450., 50.)
shim_z_vals = np.arange(-500., 50., 50.)

min_y, max_y, min_x, max_x = (0, 450, 250, 450)

int_on = []
print('\n ---------------------------- Taking averages: --------------------------------')
for shim_x in shim_x_vals:
    shim_x_int = []
    for shim_z in shim_z_vals:
        print(f'ODT ON: SHIM_X = {shim_x:.1f} mA, SHIM_Z = {shim_z:.1f} --> DONE')

        avg_int = 0.0
        for i in range(1, 4):
            fits_fname = f'Ix={shim_x:.0f}mA_Iz={shim_z:.0f}mA_{i:02d}.fits.gz'
            img = Image(os.path.join(IMG_FOLDER, fits_fname))
            img.select_roi(min_y, max_y, min_x, max_x)
            avg_int += img.row_sum
            pass

        avg_int /= i
        shim_x_int.append(avg_int)
    
    int_on.append(shim_x_int)

print(f'ODT OFF --> DONE')
int_off = 0.0
for i in range(1, 4):
    fits_fname = f'odt_off_{i:02d}.fits.gz'
    img = Image(os.path.join(IMG_FOLDER, fits_fname))
    img.select_roi(min_y, max_y, min_x, max_x)
    int_off += img.row_sum
    pass

int_off /= i

print('\n --------------------- Subtracting background due to MOT: -----------------------')
peaks = []
for (i, shim_x) in enumerate(shim_x_vals):
    peaks_x = []
    for (j, shim_z) in enumerate(shim_z_vals):
        print(f'SHIM_X = {shim_x:.1f} mA, SHIM_Z = {shim_z:.1f}. Element ({i}, {j}) of Map')

        no_bkg_int = int_on[i][j] - int_off
        peaks_x.append(np.max(no_bkg_int))

    peaks.append(peaks_x)
    
peaks = np.array(peaks)

from matplotlib import cm

SHIM_X, SHIM_Z = np.meshgrid(shim_x_vals, shim_z_vals)

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(SHIM_X, SHIM_Z, peaks.T,
                       cmap=cm.viridis,
                       linewidth=0,
                       antialiased=False)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.savefig('3d-map_IxIz.png')
plt.show()
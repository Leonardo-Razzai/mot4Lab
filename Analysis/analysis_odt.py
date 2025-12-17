import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Modules.TempAnalyzer import *

int_tot_x_on = 0.
for i in range(1, 4):
    img =Image(f'../raw_data/2025-12-17/img/Ix=-800mA_Iz=0mA_{i:02d}.fits.gz')
    img.select_roi(0, 450, 150, 500)
    int_tot_x_on += img.row_sum

int_tot_x_on /= 3

plt.plot(int_tot_x_on)
plt.show()

int_tot_x_off = 0.
for i in range(1, 4):
    img =Image(f'../raw_data/2025-12-17/img/odt_off_{i:02d}.fits.gz')
    img.select_roi(0, 450, 150, 500)
    int_tot_x_off += img.row_sum

int_tot_x_off /= 3

plt.plot(int_tot_x_off)
plt.show()

plt.plot(int_tot_x_on - int_tot_x_off)
plt.show()
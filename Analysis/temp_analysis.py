import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Modules.TempAnalyzer import *

date = '2025-12-05'
data_folder = '../raw_data/'+ f'{date}/img/'

def f_base_name(t):
    return f'T_meas_test_tof={t:.1f}ms.fits.gz'

t1 = 2. # ms
t2 = 20. # ms

img1 = Image(data_folder + f_base_name(t1))
img2 = Image(data_folder + f_base_name(t2))

img1.select_roi(0, 300, 0, 500)
img2.select_roi(0, 300, 0, 500)

img1.fit_gaussian(plot=True)
img2.fit_gaussian(plot=True)

T, dT = Get_temperature(img1, img2, t1, t2)

print(f'Temperature : ({T:.1f} +- {dT:.1f}) uK')
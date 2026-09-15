import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Modules.TempAnalyzer import *

date = '2026-09-15'
data_folder = '../raw_data/'+ f'{date}/img/'

def f_base_name(t):
    return f'optimal_loading_tof={t:.1f}ms.fits.gz'

t1 = 5. # ms
t2 = 30. # ms

img1 = Image(data_folder + f_base_name(t1))
img2 = Image(data_folder + f_base_name(t2))

img1.select_roi(0, 1100, 500, 1500)
img2.select_roi(0, 1100, 500, 1500)

img1.fit_gaussian(plot=True)
img2.fit_gaussian(plot=True)

T, dT = Get_temperature(img1, img2, t1, t2)

print(f'Temperature : ({T:.1f} +- {dT:.1f}) uK')
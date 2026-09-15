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
from Optimal_params import RT_PARAMS

from datetime import date
Date = date.today()
data_folder = f'../../raw_data/{Date}/img/'

MOT_BASE_NAME = 'optimal_loading'
FITS_BASE_NAME = MOT_BASE_NAME + '_tof'

# cam params
CAM_GAIN = 0 #dB
CAM_EXP_TIME = 1000 #us

# time of flight with odt off, before photo
t1 = 20. # ms
t2 = 30. # ms
t_odt_values = [t1, t2] # ms

# --------------------- ACQUISITION ------------------

def acquisition():

	print('\n' + '-'*12 + 'ACQUISITION' + '-'*12 + '\n')

	for t_odt in t_odt_values:
		RT_PARAMS['<todt>'] = t_odt
		print(f't_odt= {t_odt}')
			
		fits_fname = FITS_BASE_NAME + (f'={t_odt:.1f}ms')
		setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME, n=1, manta=True)
		print(' --- Start exp -- '+fits_fname)
		write_and_acquire_mot(MOT_BASE_NAME, fits_fname, params=RT_PARAMS, n=1, manta=True)
		time.sleep(3)

# --------------------- ANALYSIS ------------------

def f_base_name(t):
	return f'optimal_loading_tof={t:.1f}ms'

def analysis(show_im=False):
	
	print('\n' + '-'*12 + ' ANALYSIS ' + '-'*12)

	img1 = Image(data_folder + f_base_name(t1) + '.fits.gz')
	img2 = Image(data_folder + f_base_name(t2) + '.fits.gz')

	img1.select_roi(600, 1400, 600, 1200)
	img2.select_roi(600, 1400, 600, 1200)

	if show_im:
		img1.show_img()
		img2.show_img()

	img1.select_roi(0, 1100, 600, 1200)
	img2.select_roi(0, 1100, 600, 1200)

	img1.fit_gaussian(axis='x')
	img2.fit_gaussian(axis='x')

	img1.fit_gaussian(axis='y')
	img2.fit_gaussian(axis='y')

	print('-'*35 + '\n')

	T, dT = Get_temperature_avg(img1, img2, t1, t2)
	N, dN = img1.Get_Number_Of_Atoms_avg()

	pm = u'\u00B1'
	print('\n' + '-'*12 + ' RESULTS ' + '-'*12)
	print(f"Num. of Atoms : ({N/1e8:.1f} {pm} {dN/1e8:.1f}) x 10^8")
	print(f"Temperature : ({T:.1f} {pm} {dT:.1f}) uK")
	print('-'*35 + '\n')

ACQ = True
ANALYS = True
if __name__ == '__main__':
	if ACQ:
		acquisition()
	if ANALYS:
		analysis()
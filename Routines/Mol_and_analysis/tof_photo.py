import time
from astropy.io import fits
import matplotlib.pyplot as plt
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
gp_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(gp_dir)

import Params
from Params import RT_PARAMS
from Modules.MOTAcqLib import *
from Modules.TempAnalyzer import *

tof_vals = [2.0, 20.0]

data_folder = f'../../raw_data/{str(Date)}/img/'
img_base_name = 'molasses'

def f_base_name(t):
    return f'{img_base_name}_tof={t:.1f}ms'

mot_base_name = 'molasses_and_tof' # template file name

def show_imgs():
	for tof_val in tof_vals:
		with fits.open(f"{data_folder}{f_base_name(tof_val)}.fits.gz") as hdul:
			img = hdul[0].data
			plt.imshow(img)
			plt.title(f'Tof={tof_val:.1f} ms, MaxVal = {np.max(img)}')
			plt.show()
			hdul.close()
 
if __name__ == '__main__':
	
	print('\n----------------------------------------------------------')
	print('MOLASSES AND IMAGE ACQUISITION')
	
	print('Setup Camera')
	wait_time_to_meas = 1
	setup_camera(gain=Params.CAM_GAIN, exp_time=Params.CAM_EXP_TIME)

	print('Start Sequence')
	time.sleep(0.5)
	write_and_acquire_bkg(params=RT_PARAMS)

	for tof_val in tof_vals:
		RT_PARAMS['<TOF>'] = tof_val
		write_and_acquire_mot(mot_base_name, f_base_name(tof_val), params=RT_PARAMS)

	print('Sequence completed')

	from Modules.TempAnalyzer import *

	print('\n\n------------------------------------------------------')
	print('IMAGE PROCESSING:')
	img1 = Image(data_folder + f_base_name(tof_vals[0]) + '.fits.gz')
	img2 = Image(data_folder + f_base_name(tof_vals[-1]) + '.fits.gz')
	print('')

	img1.select_roi(0, 300, 200, 500)
	img2.select_roi(0, 300, 200, 500)

	img1.fit_gaussian(plot=False)
	img2.fit_gaussian(plot=False)

	T, dT = Get_temperature(img1, img2, tof_vals[0], tof_vals[-1])
	N1, dN1 = img1.Get_Number_Of_Atoms()
	N2, dN2 = img2.Get_Number_Of_Atoms()
	N = (N1+N2)/2
	dN = np.abs(N1-N2)/2

	print(f'\nTemperature : ({T:.2f} +- {dT:.2f}) uK')
	print(f'Num. of Atoms : ({N/1e8:.2f} +- {dN1/1e8:.2f}) * 10^8 \n\n')
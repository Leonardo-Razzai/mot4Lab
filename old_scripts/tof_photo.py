import time
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from MOTAcqLib import *

tof_vals = [2.0, 20.0]

CAM_GAIN = 5 # dB
CAM_EXP_TIME = 5000 # us
PROBE_TIME = 300 # us

img_base_name = 'T_meas_test'

mot_base_name = 'molasses_and_tof' # template file name

def show_imgs():
	for tof_val in tof_vals:
		with fits.open(f"./raw_data/{str(Date)}/img/{img_base_name}_tof={tof_val:.1f}ms.fits.gz") as hdul:
			img = hdul[0].data
			plt.imshow(img)
			plt.title(f'Tof={tof_val:.1f} ms, MaxVal = {np.max(img)}')
			plt.show()
			hdul.close()
 
if __name__ == '__main__':
 
	wait_time_to_meas = 1
	setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME)

	time.sleep(0.5)
	write_and_acquire_bkg(t_probe=PROBE_TIME)

	for tof_val in tof_vals:
     
		write_and_acquire_mot(mot_base_name, img_base_name, t_probe=PROBE_TIME, tof_val=tof_val)

	show_imgs()
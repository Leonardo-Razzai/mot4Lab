import time
import numpy as np
import matplotlib.pyplot as plt
#from scipy.optimize import curve.fit

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir =  os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grandparent_dir)

from Modules.TempAnalyzer import *
from Modules.MOTAcqLib import *

RT_PARAMS= {
     '<SHIM_Y>' : 0
}

Iy_vals = [-1200., -800., -400., 0., 400., 800., 1200.] # in mA

CAM_GAIN = 5 # dB
CAM_EXP_TIME = 1000 # us
PROBE_TIME = 32 # us

# MOT coils
b_mot_axial= 0.133 # (G/mm/A)
b_mot = b_mot_axial/2
I_mot = 8.8 # A
Grad_mot = b_mot * I_mot # G/mm

# Compensation coils
a_comp = 1.4 # (G/A)

data_folder = f'../../raw_data/{str(Date)}/img/'
img_base_name = 'Calib_Mag'

def f_base_name(By):
	return f'{img_base_name}_Iy={By:.1f}mA.fits.gz'

mot_base_name = 'change_By' # template file name
			
def Get_MagFactor(plot=False):
	
	muz_vals = []
	muy_vals = []
	for By in Iy_vals:
		path_to_img = f"{data_folder}{f_base_name(By)}"
		print(f'Analyzing: {f_base_name(By)}')
		img = Image(path_to_img)
		img.select_roi(0, 300, 200, 500)
		img.fit_gaussian('x')
		img.fit_gaussian('y')
		muz, muy = img.GetCM()
		muz_vals.append(muz)
		muy_vals.append(muy)
		
	muz_arr = np.array(muz_vals) # in pixels
	muy_arr = np.array(muy_vals)
	Iy_arr = np.array(Iy_vals)*1e-3 # in A
	
	y_MOT_vals = Iy_arr * a_comp / Grad_mot

	def lin(x, m, c):
		return m*x +c

	popt, pcov = curve_fit(lin, y_MOT_vals, muy_arr) 
	m, c= popt
	dm, _ = np.sqrt(np.diag(pcov))

	M_fit = m
	dM = dm/m * M_fit

	if plot:
		y_fit = np.linspace(y_MOT_vals.min(), y_MOT_vals.max(), 5)
		plt.plot(y_MOT_vals, muy_arr, 'o', label='Data')
		plt.plot(y_fit, c + m*y_fit, '--', label=r'Linear Fit ($m \cdot z + c$) :' + f'\nm = {m:.2f} pix/mm\n' + f'\nM = ({M_fit:.2f}' + r'$\pm$' + f' {dM:.2f}) pix/mm')
		plt.xlabel('y_MOT (mm)')
		plt.ylabel('Displacement (pixels)')
		plt.title('Displacement along y: y CCD vs y MOT')
		plt.legend()
		plt.tight_layout()
		plt.savefig('lin_fit_y_CCD_vs_y_MOT.png')
		plt.show()
		return M_fit, dM
	
			
 
if __name__ == '__main__':
	
	setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME,n=1)

	time.sleep(0.5)
	for Iy_val in Iy_vals:
		RT_PARAMS['<SHIM_Y>'] = Iy_val
		write_and_acquire_mot(mot_base_name, img_base_name, params=RT_PARAMS,n=1)
		print(f_base_name(Iy_val))
		time.sleep(1)

	time.sleep(0.5)
	M, dM = Get_MagFactor(plot=True)

	print(f'Magnification : ({M:.3f} +- {dM:.3f}) pix/mm \n\n')

import time
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from Modules.MOTAcqLib import *
from Modules.TempAnalyzer import *

Iz_vals = [-500., -300., -200., 0., 200., 300., 500.] # in mA

CAM_GAIN = 5 # dB
CAM_EXP_TIME = 5000 # us
PROBE_TIME = 300 # us

# MOT coils
b_mot = 0.133 # (G/mm/A)
I_mot = 9 # A
Grad_mot = b_mot * I_mot # G/mm

# Compensation coils
a_comp = 1.4 # (G/A)

data_folder = f'../../raw_data/{str(Date)}/img/'
img_base_name = 'Calib_Mag'

def f_base_name(Bz):
	return f'{img_base_name}_Iz={Bz:.1f}mA.fits.gz'

mot_base_name = 'change_Bz' # template file name
			
def Get_MagFactor(plot=False):
	
	muz_vals = []
	muy_vals = []
	for Bz in Iz_vals:
		path_to_img = f"{data_folder}{f_base_name(Bz)}"
		print(f'Analyzing: {f_base_name(Bz)}')
		img = Image(path_to_img)
		img.select_roi(0, 300, 200, 500)
		img.fit_gaussian('x')
		img.fit_gaussian('y')
		muz, muy = img.GetCM()
		muz_vals.append(muz)
		muy_vals.append(muy)
		
	muz_arr = np.array(muz_vals) # in pixels
	muy_arr = np.array(muy_vals)
	Iz_arr = np.array(Iz_vals)*1e-3 # in A
	
	z_MOT_vals = Iz_arr * a_comp / Grad_mot

	def lin(x, m, c):
		return m*x +c

	popt, pcov = curve_fit(lin, z_MOT_vals, muz_arr) 
	m, c= popt
	dm, _ = np.sqrt(np.diag(pcov))

	M_fit = m
	dM = dm/m * M_fit

	if plot:
		z_fit = np.linspace(z_MOT_vals.min(), z_MOT_vals.max(), 5)
		plt.plot(z_MOT_vals, muz_arr, 'o', label='Data')
		plt.plot(z_fit, c + m*z_fit, '--', label=r'Linear Fit ($m \cdot z + c$) :' + f'\nm = {m:.2f} pix/mm\n' + f'\nM = ({M_fit:.2f}' + r'$\pm$' + f' {dM:.2f}) pix/mm')
		plt.xlabel('z_MOT (mm)')
		plt.ylabel('Displacement (pixels)')
		plt.title('Displacemenet along z: z CCD vs z MOT')
		plt.legend()
		plt.tight_layout()
		plt.savefig('lin_fit_z_CCD_vs_z_MOT.png')
		plt.show()
		return M_fit, dM
	
			
 
if __name__ == '__main__':
	
	setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME)

	time.sleep(0.5)
	for Iz_val in Iz_vals:
		write_and_acquire_mot(mot_base_name, img_base_name, shim_z=Iz_val)
		print(f_base_name(Iz_val))
		# write_mot_file(mot_base_name, shim_z=Iz_val)
		time.sleep(1)

	time.sleep(0.5)
	M, dM = Get_MagFactor(plot=True)

	print(f'Magnification : ({M:.3f} +- {dM:.3f}) pix/mm \n\n')
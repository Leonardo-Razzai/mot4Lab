from astropy.io import fits
import matplotlib.pyplot as plt
from MOTAcqLib import *
from Analysis.TempAnalyzer import *

CAM_GAIN = 0 # dB
CAM_EXP_TIME = 1000 # us
PROBE_TIME = 500 # us
TOF=35 # ms

fits_fname = F'odt=500mW'
mot_base_name = 'molasses_and_tof'

setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME)
mot_fname = write_mot_file(mot_base_name, t_probe=PROBE_TIME, tof_val=TOF)
acquire_img(mot_fname=mot_fname, fits_fname=fits_fname, t_probe=PROBE_TIME)
img = Image(img_folder + fits_fname + '.fits.gz')
img.select_roi(0, 450, 100, 600)
img.show_img()
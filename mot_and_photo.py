from astropy.io import fits
import matplotlib.pyplot as plt
from MOTAcqLib import *

CAM_GAIN = 0 # dB
CAM_EXP_TIME = 5000 # us
PROBE_TIME = 180 # us

fits_fname = F'CCD_t_probe={PROBE_TIME}'
mot_base_name = 'bkg'

setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME)
mot_fname = write_mot_file(mot_base_name, t_probe=PROBE_TIME)
acquire_img(mot_fname=mot_fname, fits_fname=fits_fname, t_probe=PROBE_TIME)
show_img(img_folder + fits_fname)
from astropy.io import fits
import matplotlib.pyplot as plt
from MOTAcqLib import acquire_img, setup_camera

CAM_GAIN = 0 # dB
CAM_EXP_TIME = 5000 # us
PROBE_TIME = 300 # us

fits_fname = 'mot_displeacement_shimz=-500mA'
mot_fname = 'mot_displeacement.mot'

setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME)

acquire_img(mot_fname, fits_fname, t_probe=PROBE_TIME)
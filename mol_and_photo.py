from astropy.io import fits
import matplotlib.pyplot as plt
from MOTAcqLib import *
from Analysis.TempAnalyzer import *

CAM_GAIN = 0 # dB
CAM_EXP_TIME = 1000 # us
PROBE_TIME = 500 # us
TOF=15 # ms

mot_base_name = 'molasses_and_tof'

ACQUIRE = True
if ACQUIRE:
    for i in range(1, 4):
        fits_fname = F'tof=15ms_odt=1300mW_{i:02d}'
        print(f'Acquiring {fits_fname}')
        setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME)
        mot_fname = write_mot_file(mot_base_name, t_probe=PROBE_TIME, tof_val=TOF)
        acquire_img(mot_fname=mot_fname, fits_fname=fits_fname, t_probe=PROBE_TIME)
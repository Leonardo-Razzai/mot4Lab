from astropy.io import fits
import matplotlib.pyplot as plt
from Modules.MOTAcqLib import *
from Modules.TempAnalyzer import *
import Params

fits_fname = F'Ix={Params.MOT_SHIM_X:.0f}_Iy={Params.MOT_SHIM_Y:.0f}_Iz={Params.MOT_SHIM_Z:.0f}'
mot_base_name = 'load_odt_map'

setup_camera(gain=Params.CAM_GAIN, exp_time=Params.CAM_EXP_TIME)
mot_fname = write_mot_file(mot_base_name, t_probe=Params.T_PROBE, tof_val=Params.TOF)
acquire_img(mot_fname=mot_fname, fits_fname=fits_fname, t_probe=Params.T_PROBE)

SHOW = False
if SHOW:
    img = Image(os.path.join(IMG_FOLDER, fits_fname) + '.fits.gz')
    img.select_roi(0, 450, 100, 600)
    img.show_img()
from datetime import date
import os
import subprocess
import numpy as np
import time

# 1. Get the absolute path of the folder containing THIS script
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Define paths relative to the module location
RAW_BASE_DIR = os.path.join(MODULE_DIR, '..', 'raw_data') 
MOT_FOLDER = os.path.join(MODULE_DIR, '..', 'mot_files')
CCD_FOLDER = os.path.join(MODULE_DIR, '..', 'ccd')

Date = date.today()
IMG_FOLDER = os.path.join(RAW_BASE_DIR, str(Date), 'img')
DATA_FOLDER = os.path.join(RAW_BASE_DIR, str(Date), 'data')

os.makedirs(IMG_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

VERBOSE = False
	
def setup_camera(gain: float, exp_time: int, manta=False):
    ccd_command_list = f"{os.path.join(CCD_FOLDER, 'ccdnew')} -g {gain} -t {exp_time} -a".split()
    if manta:
        ccd_command_list.append("-m")
    print(ccd_command_list)
    subprocess.run(ccd_command_list)
    
def acquire_img(mot_fname, fits_fname, t_probe=None, n=1, params={}, manta=False):
    ccd_command_list = [f"{os.path.join(CCD_FOLDER, 'ccdnew')}", '-a'] + ['-c', f"\"{params}\""] + ['-n', f"{n}"] + ['-f', f"{fits_fname}"]
    if manta:
        ccd_command_list.append("-m")
    print(ccd_command_list)
    ccd = subprocess.Popen(ccd_command_list)
    ccd.wait()


if __name__ == '__main__':
    params = {'a': 0, 'b': 1e-4, 'c' : 'testo'}
    setup_camera(10, 200, manta=True)
    acquire_img("motname", "test", t_probe=None, n=1, params=params, manta=True)

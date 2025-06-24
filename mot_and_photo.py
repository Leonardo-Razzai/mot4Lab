import subprocess
import os
import sys
import re
import time
from interface_app.Osc_RS import Osc_RS
import pandas as pd
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt

CAM_GAIN = 1 # dB
CAM_EXP_TIME = 5000 # us

base_name = 'mot_displeacement_shimz=-500mA'
mot_name = 'mot_displeacement.mot'

def send_to_fpga(outname):
	reset = "python3 -m mot4py -R"
	command = f"python3 -m mot4py -f {outname}"
	mot = subprocess.call(command.split())

def setup_camera(gain:float, exp_time: int):
	proc = subprocess.call(f"./ccd/ccd -g {gain} -t {exp_time} -a".split())

def show_imgs():
    with fits.open(f"./img/{base_name}.fits.gz") as hdul:
        img = hdul[0].data
        plt.imshow(img)
        plt.show()
        hdul.close()

setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME)

ccd = subprocess.Popen(f"./ccd/ccd -f ./img/{base_name}".split())
send_to_fpga(mot_name)
ccd.wait()

show_imgs()
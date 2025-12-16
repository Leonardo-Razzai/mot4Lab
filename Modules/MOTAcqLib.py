from datetime import date
from .Refactor import refactor_file
import os
import subprocess
from astropy.io import fits
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Get the absolute path of the folder containing THIS script
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Define paths relative to the module location
RAW_BASE_DIR = os.path.join(MODULE_DIR, '..', 'raw_data') 
MOT_FOLDER = os.path.join(MODULE_DIR, '..', 'mot_files')

Date = date.today()
IMG_FOLDER = os.path.join(RAW_BASE_DIR, str(Date), 'img')
DATA_FOLDER = os.path.join(RAW_BASE_DIR, str(Date), 'data')

os.makedirs(IMG_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

def write_mot_file(basename, params: dict):

    '''Return the output file name .mot'''

    try:
        inname = basename + '.tmpl'
        infile = open(inname, "r")
    except:
        exit("Cannot open input file")
        
    outname = basename + '.mot'
    outfile = open(os.path.join(MOT_FOLDER, outname), "w")
    print(f'Writing routine at {outfile}\n')
        
    for line in infile:
        out_str = line

        for label, value in params.items():
            out_str = out_str.replace(label, f'{value:.1f}')

        outfile.write(out_str)
        
    outfile.close()
    infile.close()

    refactor_file(inname)
        
    return outname

def send_to_fpga(outname):
    reset = "python3 -m mot4py -R"
    command = f"python3 -m mot4py -f {os.path.join(MOT_FOLDER, outname)}"
    mot = subprocess.call(command.split())

def setup_camera(gain:float, exp_time: int):
    proc = subprocess.call(f"./ccd/ccd -g {gain} -t {exp_time} -a".split())
 
def append_t_probe_fits(fits_fname, t_probe):
    with fits.open(fits_fname + '.fits.gz') as hdul:
        hdr = hdul[0].header
        data = hdul[0].data
        hdr['T_PROBE'] = (t_probe, 'Probe time in us')
        hdul.close()
    fits.writeto(fits_fname + '.fits.gz',data=data, header=hdr, overwrite=True)
        
def show_img(fits_fname):
    with fits.open(f"{fits_fname}.fits.gz") as hdul:
        img = hdul[0].data
        Gain = hdul[0].header['GAIN']
        t_probe = hdul[0].header['T_PROBE']
        
        fig, ax = plt.subplots(1)
        ax.imshow(img)
        legend = f"MaxCounts = {img.max():.0f}\n"
        legend += f"Gain = {Gain:.0f} dB\n"
        legend += f"T_probe = {t_probe} us"
            
        ax.text(10, 520, legend, bbox={'facecolor': 'white'}, fontdict={'fontsize': 10})
        plt.show()
        hdul.close()
        
def acquire_img(mot_fname, fits_fname, t_probe=None):
    
    ccd = subprocess.Popen(f"./ccd/ccd -f {os.path.join(IMG_FOLDER, fits_fname)}".split())
    send_to_fpga(mot_fname)
    ccd.wait()
    
    if t_probe:
        append_t_probe_fits(os.path.join(IMG_FOLDER, fits_fname), t_probe)
        
def write_and_acquire_bkg(t_probe):
        
    if t_probe is None:
        print("No t_probe specified for background acquisition")
        exit()
        
    bkg_mot_fname = write_mot_file('bkg', t_probe)
    bkg_fits_fname = f"bkg_exp={t_probe}us"

    acquire_img(bkg_mot_fname, bkg_fits_fname, t_probe=t_probe)

def write_and_acquire_mot(mot_base_name: str,
                          fits_fname: str,
                          params):
        
    mot_fname = write_mot_file(mot_base_name, params)

    t_probe = None
    for param in params:
        if param.label == '<TPR>':
            t_probe = param.value
                   
    acquire_img(mot_fname, fits_fname, t_probe=t_probe)
        
def save_data(data_filename: str, data_dict):
    df = pd.DataFrame(data_dict)
    out_name = os.path.join(DATA_FOLDER, data_filename)
    print(f'Saving data at {out_name}\n')
    df.to_csv(out_name)

if __name__ == '__main__':
    print(RAW_BASE_DIR)
    print(MOT_FOLDER)
    print(DATA_FOLDER)
    print(IMG_FOLDER)
    
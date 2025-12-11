from datetime import date
from Refactor import refactor_file
import os
import subprocess
from astropy.io import fits
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

Date = date.today()
os.makedirs('raw_data/' + str(Date) + '/img', exist_ok=True)
os.makedirs('raw_data/' + str(Date) + '/data', exist_ok=True)

mot_folder = './mot_files/'
tmpl_folder = './tmpl_files/'
img_folder = f'./raw_data/{str(Date)}/img/'

def write_mot_file(basename, t_probe = None, tof_val= None, shim_z = None):
    '''Return the output file name .mot'''
    try:
        inname = basename + '.tmpl'
        infile = open(tmpl_folder + inname, "r")
    except:
        exit("Cannot open input file")
        
    outname = basename + '.mot'
    outfile = open(mot_folder + outname, "w")
        
    for line in infile:
        out_str = line
        if t_probe:
            out_str = out_str.replace('<TPR>', f'{t_probe:.0f}')
        if tof_val:
            out_str = out_str.replace('<TOF>', f'{tof_val:.0f}')
        if shim_z:
            if np.abs(shim_z) < 2000:
                out_str = out_str.replace('<SHIM_Z>', f'{shim_z:.1f}')
            else:
                print('The chosen current value is too high. iT is ounded to (-2000, 2000) mA')
                exit()

        outfile.write(out_str)
        
    outfile.close()
    infile.close()

    refactor_file(tmpl_folder + inname)
    refactor_file(mot_folder + outname)
        
    return outname

def send_to_fpga(outname):
    reset = "python3 -m mot4py -R"
    command = f"python3 -m mot4py -f {mot_folder + outname}"
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
    
    ccd = subprocess.Popen(f"./ccd/ccd -f {img_folder + fits_fname}".split())
    send_to_fpga(mot_fname)
    ccd.wait()
    
    if t_probe:
        append_t_probe_fits(img_folder + fits_fname, t_probe)
        
def write_and_acquire_bkg(t_probe):
        
    if t_probe is None:
        print("No t_probe specified for background acquisition")
        exit()
        
    bkg_mot_fname = write_mot_file('bkg', t_probe)
    bkg_fits_fname = f"bkg_exp={t_probe}us"

    acquire_img(bkg_mot_fname, bkg_fits_fname, t_probe=t_probe)

def write_and_acquire_mot(mot_base_name: str, fits_fname: str, t_probe = None, tof_val = None, shim_z = None):
        
    mot_fname = write_mot_file(mot_base_name, t_probe, tof_val, shim_z)
    
    if tof_val:
        fits_fname += f"_tof={tof_val:.1f}ms"
    if shim_z:
        fits_fname += f"_Iz={shim_z:.1f}mA"
        
    acquire_img(mot_fname, fits_fname, t_probe=t_probe)
        
def save_data(data_filename: str, data_dict):
    df = pd.DataFrame(data_dict)
    df.to_csv(f'./raw_data/{str(Date)}/data/' + data_filename)
    
import subprocess
import os
import sys
import re
import time
import pandas as pd
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import os
from datetime import date
from refactor import refactor_file

Date = date.today()
os.makedirs('raw_data/' + str(Date) + '/img', exist_ok=True)
os.makedirs('raw_data/' + str(Date) + '/data', exist_ok=True)

tof_vals = np.arange(5, 30, 5) # ms
tof_vals = [2.0, 20.0]

CAM_GAIN = 0 # dB
CAM_EXP_TIME = 5000 # us
PROBE_TIME = 300 # us

img_base_name = 'mol7'

meas_dict = {'tof [ms]':[], 'S [V]':[]}

mot_base_name = 'molasses_and_tof' # template file name

mot_folder = './mot_files/'
tmpl_folder = './tmpl_files/'

def write_mot_file(basename, tof_val= None):
	'''Return the output file name .mot'''
	try:
		inname = basename + '.tmpl'
		infile = open(tmpl_folder + inname, "r")
	except:
		exit("Cannot open input file")
		
	outname = basename + '.mot'
	outfile = open(mot_folder + outname, "w")
		
	for line in infile:
		out_str = line.replace('<TPR>', f'{PROBE_TIME:.0f}')
		if tof_val:
			out_str = out_str.replace('<TOF>', f'{tof_val:.1f}')
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

def show_imgs():
	for tof_val in tof_vals:
		with fits.open(f"./raw_data/{str(Date)}/img/{img_base_name}_tof={tof_val:.1f}ms.fits.gz") as hdul:
			img = hdul[0].data
			plt.imshow(img)
			plt.title(f'Tof={tof_val:.1f} ms, MaxVal = {np.max(img)}')
			plt.show()
			hdul.close()

if __name__ == '__main__':
		
	from interface_app.Osc_RS import Osc_RS
	osc = Osc_RS()
 
	wait_time_to_meas = 1
	setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME)

	time.sleep(0.5)
	bkg_mot_fname = write_mot_file('bkg')
	bkg_fits_fname = f"./raw_data/{str(Date)}/img/bkg_exp={PROBE_TIME}us"  
	ccd = subprocess.Popen(f"./ccd/ccd -f {bkg_fits_fname}".split())
	send_to_fpga(bkg_mot_fname)
	ccd.wait()

	for tof_val in tof_vals:
		outname = write_mot_file(mot_base_name, tof_val)
		print(f"<TOF> = {tof_val} ms")
		
		fits_fname = f"./raw_data/{str(Date)}/img/{img_base_name}_tof={tof_val:.1f}ms"  
		ccd = subprocess.Popen(f"./ccd/ccd -f {fits_fname}".split())
		send_to_fpga(outname)
		ccd.wait()
		
		time.sleep(wait_time_to_meas)
		meas = osc.Get_Meas()
		if meas < 1e3:
			meas_dict['tof [ms]'].append(tof_val)
			meas_dict['S [V]'].append(meas)
			print(f'S = {meas} V\n')
		else:
			print('Meas. discarded')

	print(meas_dict)

	data_filename = f'data_{img_base_name}.csv'
	df = pd.DataFrame(meas_dict)
	df.to_csv(f'./raw_data/{str(Date)}/data/' + data_filename)

	show_imgs()
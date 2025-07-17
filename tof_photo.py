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

CAM_GAIN = 1 # dB
CAM_EXP_TIME = 5000 # us
PROBE_TIME = 300 # us

img_base_name = 'time_ramp_aom=0.6ms'

meas_dict = {'tof [ms]':[], 'S [V]':[]}

mot_base_name = 'molasses_and_tof_ramp_aom_amp' # template file name

mot_folder = './mot_files/'
tmpl_folder = './tmpl_files/'

def write_mot_file(basename, curr_val):
	'''Return the output file name .mot'''
	try:
		inname = basename + '.tmpl'
		infile = open(tmpl_folder + inname, "r")
	except:
		exit("Cannot open input file")
		
	outname = basename + '.mot'
	outfile = open(mot_folder + outname, "w")
		
	for line in infile:
		out_str = line.replace('<TOF>', f'{curr_val:.1f}')
		out_str = out_str.replace('<TPR>', f'{PROBE_TIME:.0f}')
		print(line)
		print(out_str)
		outfile.write(out_str)
		
	outfile.close()
	infile.close()
		
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

	# data_filename = f'data_{img_base_name}.csv'
	# df = pd.DataFrame(meas_dict)
	# df.to_csv('./data/' + data_filename)

	show_imgs()
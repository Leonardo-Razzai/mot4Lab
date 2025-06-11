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

osc = Osc_RS()

tof_vals = np.arange(5, 30, 5) # ms
tof_vals = [2.0]

img_base_name = 'test'

meas_dict = {'tof [ms]':[], 'S [V]':[]}

inname = 'molasses_and_tof.tmpl' # template file

try:
	infile = open(inname, "r")
except:
	exit("Cannot open input file")

base, ext = os.path.splitext(os.path.basename(inname))

def write_mot_file(outname, curr_val):
	outfile = open(outname, "w")
	for line in infile:
		out_str = line.replace('<TOF>', f'{curr_val:.1f}')   	
		outfile.write(out_str)
	outfile.close()
	infile.seek(0, 0)

def send_to_fpga(outname):
	reset = "python3 -m mot4py -R"
	command = f"python3 -m mot4py -f {outname}"
	#subprocess.run(reset, shell=True)
	#time.sleep(1)
	mot = subprocess.call(command.split())

def setup_camera(gain:float, exp_time: int):
	proc = subprocess.call(f"./ccd/ccd -g {gain} -t {exp_time} -a".split())

def show_imgs():
	for tof_val in tof_vals:
		with fits.open(f"./img/{img_base_name}_tof={tof_val:.1f}ms.fits.gz") as hdul:
			img = hdul[0].data
			plt.imshow(img)
			plt.title(f'Tof={tof_val:.1f} ms, MaxVal = {np.max(img)}')
			plt.show()
			hdul.close()

wait_time_to_meas = 1
setup_camera(gain=20, exp_time=5000)

for tof_val in tof_vals:
	outname = base + '.mot'
	write_mot_file(outname, tof_val)
	print(f"<TOF> = {tof_val} ms")

	ccd = subprocess.Popen(f"./ccd/ccd -f ./img/{img_base_name}_tof={tof_val:.1f}ms".split())
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
    	
    

infile.close()
print(meas_dict)

# data_filename = f'data_{img_base_name}.csv'
# df = pd.DataFrame(meas_dict)
# df.to_csv('./data/' + data_filename)

show_imgs()
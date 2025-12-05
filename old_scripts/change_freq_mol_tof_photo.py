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

freq_vals = np.arange(10.1, 10.65, 0.05)
freq_vals = freq_vals*1e6

img_base_name = 'photo'

meas_dict = {'DDS [MHz]':[], 'S [V]':[]}

try:
	if sys.argv[1] != '':
		inname = sys.argv[1]
	else:
		inname = 'molasses_and_tof_vs_freq'
	infile = open(inname, "r")
except:
	exit("Cannot open input file")

base, ext = os.path.splitext(os.path.basename(inname))

def write_mot_file(outname, curr_val):
	outfile = open(outname, "w")
	for line in infile:
		out_str = line.replace('<FREQ>', f'{curr_val:.1f}')   	
		outfile.write(out_str)
	outfile.close()
	infile.seek(0, 0)

def send_to_fpga(outname):
	reset = "python3 -m mot4py -R"
	command = f"python3 -m mot4py -f {outname}"
	#subprocess.run(reset, shell=True)
	#time.sleep(1)
	subprocess.run(command, shell=True)
	mot = subprocess.call(command.split())

wait_time_to_meas = 1

for freq_val in freq_vals:
	outname = base + '.mot'
	write_mot_file(outname, freq_val)
	print(f"<FREQ> = {freq_val/1e6} MHz")

	send_to_fpga(outname)
	
	time.sleep(wait_time_to_meas)
	meas = osc.Get_Meas()
	if meas < 1e3:
		meas_dict['DDS [MHz]'].append(freq_val/1e6)
		meas_dict['S [V]'].append(meas)
		print(f'S = {meas} V\n')
	else:
		print('Meas. discarded')
    	
    

infile.close()
print(meas_dict)

data_filename = f'tof_mol_vs_freq_ramp5.csv'
df = pd.DataFrame(meas_dict)
df.to_csv(data_filename)

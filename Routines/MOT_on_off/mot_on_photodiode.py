import time
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(current_dir))
grand_grandparent_dir  = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
grand_grand_grandparent_dir  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
sys.path.append(grandparent_dir)
sys.path.append(grand_grandparent_dir)
sys.path.append(grand_grand_grandparent_dir)

from Modules.MOTAcqLib import *
from Modules.TempAnalyzer import *
from interface_app.Osc_RS import *


# ROUTINE SETTINGS
MOT_BASE_NAME = 'mot_on_off'
FITS_BASE_NAME = MOT_BASE_NAME
REPETITIONS = 10
SLEEP_TIME = 1 # seconds between each run

RT_PARAMS= {
}

CAM_GAIN = 0 #dB
CAM_EXP_TIME = 1000 #us
()
# OSCILLOSCOPE SETTINGS
osc = Osc_RS(channel=1, channel_trigger=3)
osc.Set_coupling('DC')
osc.Set_vertical_range(3)
osc.Set_horizontal_range(1)

data_osc = {
    'time':[],
    'pd_sig (V)':[]
}

print("\n"+ "-"*30)
	
for i in range(1, REPETITIONS + 1):

    # execute routine
    fits_fname = FITS_BASE_NAME + (f'_{i:02d}')
    setup_camera(gain=CAM_GAIN, exp_time=CAM_EXP_TIME, n=1, manta=True)
    print(' --- Start exp -- '+fits_fname)
    write_and_acquire_mot(MOT_BASE_NAME, fits_fname, params=RT_PARAMS, n=1, manta=True)
    time.sleep(3)

    # Save data from oscilloscope
    now = time.localtime()
    now_str = f'{now.tm_hour}:{now.tm_min}:{now.tm_sec}'

    pd_vpp = osc.Get_Meas()
    print(f'PD phtovoltage Vpp: {pd_vpp*1e3:.0f} mV')
    data_osc['time'].append(now_str)
    data_osc['pd_sig (V)'].append(pd_vpp)

    time.sleep(SLEEP_TIME)

save_data('PD_MOT_signal.csv', data_osc)


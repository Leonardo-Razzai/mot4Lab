import time
import os
import sys
from pathlib import Path

current_dir = Path(__file__).resolve() 
sys.path.append(str(current_dir.parents[1]))
sys.path.append(str(current_dir.parents[2]))
sys.path.append(str(current_dir.parents[3]))
sys.path.append(str(current_dir.parents[4]))

from Modules.MOTAcqLib import *
from interface_app.SA_Rigol import *

# ROUTINE SETTINGS
MOT_BASE_NAME = 'test_dds_eom_freq_mod'
REPETITIONS = 1
SLEEP_TIME = 5 # seconds of outine duration

INIT_FREQ = 9.9 # MHz
FIN_FREQ = 10.0 # MHz

RT_PARAMS= {
    '<INIT_FREQ>':INIT_FREQ, # MHz
    '<FIN_FREQ>':FIN_FREQ # MHz
}

CENT_FREQ = FIN_FREQ * 683 * 1e6 # Hz
SWT = 10e-3 # s
RBW = 50e3 # Hz
PLOT = True

sa = SA_Rigol()

sa.Set_Trace_Write()
sa.Set_Scale('LIN')
sa.Set_Trigger('IMM')
sa.Set_Span(10e6)
sa.Set_Center_Freq(CENT_FREQ)
sa.Set_RBW(10*RBW)
time.sleep(2)
sa.Set_AutoRangeY()
time.sleep(2)
sa.Set_RBW(RBW)
time.sleep(1)
sa.Set_Center_Frequency_Peak()
time.sleep(2)
sa.Set_SWT(SWT)
sa.Set_Span(0)
sa.Set_Trigger('EXT')
time.sleep(2)

outname = write_mot_file(MOT_BASE_NAME, RT_PARAMS)
send_to_fpga(outname)
time.sleep(SLEEP_TIME)

data = sa.Get_Trace_Time()

save_data('rising_time_bco.csv', data)

if PLOT:
    plt.plot(data['t (s)']*1e3, data['y (V)']*1e3)
    plt.xlabel('Time (ms)')
    plt.ylabel('Amp (mV)')
    plt.grid()
    plt.show()
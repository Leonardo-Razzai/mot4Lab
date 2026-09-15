import time
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(grandparent_dir)

from Params import *
from Modules.MOTAcqLib import *
from Modules.TempAnalyzer import *

mot_name = 'MOL_shim.mot'
shim_value = 500
which_shim = 'x'
print('\n----------------------------------------------------------')
print('MOLASSES AND TRACE ACQUISITION')
trace_fname = f'RR_shim_'+which_shim+'={shim_value:04d}'

command = f"python3 -m mot4py -f {os.path.join(current_dir, mot_name)}"
#mot = subprocess.call(command.split())
#time.sleep(2)

print('--- Acquire trace, CH1 --'+trace_fname)
command = f"python3 gettrace.py rs:ch1 >> {os.path.join(current_dir, 'ch1.dat')}"
#subprocess.call(command.split())

#time.sleep(2)
print('--- Acquire trace, CH4 --'+trace_fname)
command = f"python3 gettrace.py rs:ch4 >> ch4.dat"
print(command)
print(command.split())
subprocess.call(command.split())
time.sleep(2)

    


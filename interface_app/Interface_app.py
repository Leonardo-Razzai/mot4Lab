import os
import platform
import subprocess
import threading
#from scapy.all import ARP, Ether, srp

import pyvisa
import time
import numpy as np
import pandas as pd

'''
INDIRIZZI STRUMENTI:
IP: 192.168.1.1, MAC: 54:b8:0a:09:0b:1c -> router?
IP: 192.168.1.11, MAC: 00:19:af:52:91:bf -> spectrum analyzer rigol
IP: 192.168.1.108, MAC: d0:c6:37:7c:7d:a6 -> this computer
IP: 192.168.1.114, MAC: 00:90:b8:28:20:b4 -> oscilloscope
'''

Lab_Instruments = {
  "SA_Rigol":{
    "ip_addr": "192.168.1.11",
    "mac_addr": "00:19:af:52:91:bf"
  },
  
  "Osc_RS":{
    "ip_addr": "192.168.1.12",
    "mac_addr": "00:90:b8:28:20:b4"
  },
  
  "DMM":{
    "ip_addr": "192.168.1.107",
    "mac_addr": ""
  },
  
  "FuncGen_Rigol":{
    "ip_addr": "192.168.1.102",
    "mac_addr": "00:19:AF:04:EC:69"
  },
  "Osc_Rigol":{
    "ip_addr": "",
    "mac_addr": ""
  }
}

def ping(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def get_mac(ip):
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    if answered_list:
        return answered_list[0][1].hwsrc
    else:
        return None

def scan_network(ip_range):
    ip_list = ip_range.split('.')
    base_ip = '.'.join(ip_list[:-1]) + '.'
    
    devices = []

    def worker(ip):
        if ping(ip):
            mac = get_mac(ip)
            if mac is not None:
              devices.append((ip, mac))

    threads = []
    for i in range(1, 255):  # Adjust range based on subnet mask
        ip = base_ip + str(i)
        thread = threading.Thread(target=worker, args=(ip,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    return devices

def LAN_addr(ip_addr: str):
    return f'TCPIP::{ip_addr}::INSTR'



rm = pyvisa.ResourceManager('@py')

class VISA_inst():
    """
    A base class for handling communication with instruments via the VISA interface.

    Attributes:
        dev (pyvisa.Resource): The instrument resource object for communication.
    """

    def __init__(self, instr_name: str) -> None:
        """
        Initializes the VISA instrument connection.

        Args:
            rm (pyvisa.ResourceManager): The resource manager object from PyVISA.
            instr_name (str): The name of the instrument to connect to.
        """
        self.dev = rm.open_resource(LAN_addr(Lab_Instruments[instr_name]["ip_addr"]))
        self.dev.read_termination = '\n'
        self.dev.write_termination = '\n'
    

class DMM(VISA_inst):
    def __init__(self) -> None:
        instr_name = "DMM"
        super().__init__(instr_name=instr_name)
    
    def Read_Meas(self):
        return float(self.dev.query('MEAS:VOLT:DC?'))
    

class Osc_Rigol(VISA_inst):
    def __init__(self) -> None:
        instr_name = "Osc_Rigol"
        super().__init__(instr_name=instr_name)


















# if __name__ == "__main__":
#     ip_range = "192.168.1.1/24"
#     devices = scan_network(ip_range)

#     print("\nDevices found:")
#     for ip, mac in devices:
#         print(f"IP: {ip}, MAC: {mac}")

import pyvisa, sys
import numpy as np

def usage():
    print("""Usage:
    python3 gettrace.py instr:trace
    where instr = "sa", "rg" or "rs"
    and trace = "tr1", "tr2" or "tr3" for "sa"
    or trace = "ch1", "ch2" or "math" for "rg"
    or trace = "ch1".."ch4" or "math1".."math5" or "fft", "fftavg" for "rs"
    
    or 

    python3 gettrace.py instr:trace "comment"
    where everything between quotes is treated as a comment 
    and pasted in the header
    """)
    exit()
    
if __name__ == '__main__':
    
    trdict = {"sa":("tr1", "tr2", "tr3"), "rg":("ch1", "ch2", "math"),
              "rs":("ch1", "ch2", "ch3", "ch4", "math1", "math2", "math3", "math4", "math5", "fft", "fftavg")}

    addrdict = {"sa" : "192.168.1.11", "rg" : "192.168.1.10", "rs" : "192.168.1.12"}
    
    if len(sys.argv) < 2:
        usage()
    else:
        comment = None
        writedata = False
        if len(sys.argv) == 3:
            comment = sys.argv[2]
        instr, trace = sys.argv[1].lower().split(":")
        if instr not in trdict.keys():
            print("Invalid instrument: %s" % (instr))
            usage()
        else:
            if trace not in trdict[instr]:
                print("Invalid trace: %s" % (trace))
                usage()

        rm = pyvisa.ResourceManager('@py')
        addr = "TCPIP0::" + addrdict[instr] + "::INSTR"

        with rm.open_resource(addr) as dev:
            if instr == "sa":
                ans = dev.query(":TRACE%c:MODE?" % (trace[-1]))
                if ans.startswith("BLAN"):
                    exit("Empty trace!")
                else:
                    #X
                    pts = int(dev.query(":SWE:POIN?"))
                    start = float(dev.query(":FREQ:STAR?"))
                    stop = float(dev.query(":FREQ:STOP?"))
                    x = np.linspace(start, stop, num=pts)
                    
                    # Y units, RBW
                    units = dev.query(":UNIT:POW?").rstrip()
                    rb = dev.query(":SENS:BAND:RES?").rstrip()
                    vb = dev.query(":SENS:BAND:VID?").rstrip()
                    swt = dev.query(":SENS:SWE:TIME?").rstrip()
                    
                    # Y
                    dev.write(":FORM:TRAC:DATA REAL,32")
                    dev.write(":FORM:BORD NORM")
                    y = dev.query_binary_values(":TRAC:DATA? TRACE%c" % (trace[-1]), 'f')
                    
                    #output
                    print("# RES BW = %s\n#" % (rb))
                    print("# VIDEO BW = %s\n#" % (vb))
                    print("# SWEEP TIME = %s\n#" % (swt))
                    writedata = True
                    
            elif instr == "rg":
                if trace == "math":
                    mode = dev.query(":CALC:MODE?").rstrip()
                    if mode.startswith("OFF"):
                        exit("Empty trace!")
                    fft = mode.startswith("FFT")
                    dev.write(":WAV:SOUR MATH")
                else:
                    if dev.query(":CHAN%c:DISP?" % (trace[-1])).startswith("0"):
                        exit("Empty trace!")
                    dev.write(":WAV:SOUR CHAN%c" % (trace[-1]))                        
                dev.write(":WAV:MODE NORM")
                dev.write(":WAV:FORM BYTE")
                preamb = dev.query(":WAV:PRE?").split(",")

                #X
                pts = int(preamb[2])
                if trace == 'math' and fft:
                    st = float(dev.query(":CALC:FFT:HOFF?"))
                    sp = st + 14 * float( dev.query(":CALC:FFT:HSP?"))
                    st = max(0., st)
                    units = dev.query(":CALC:FFT:VSM?").rstrip()
                    if units.startswith("DB"):
                        ch = dev.query(":CALC:FFT:SOUR?").rstrip()
                        if dev.query(":CHAN%c:IMP?" % (ch[-1])).startswith("FIFT"):
                            units = "dBm"
                        else:
                            units = "dBV"
                else:
                    st = float(preamb[5])
                    sp = st + float(preamb[4]) * pts
                    units = "V"
                x = np.linspace(st, sp, num=pts)

                #Y
                buf = np.array(dev.query_binary_values(":WAV:DATA?", 'B')) - 127
                dy = float(preamb[7])
                yoff = float(preamb[8])
                y = (buf - yoff) * dy

                #output
                if trace == "math":
                    print("#\n# MATH OP = %s\n#" % (mode))
                writedata = True

            elif instr == "rs":
                if trace not in trdict["rs"]:
                    exit("Empty trace!")
                dev.write("FORM REAL")
                if trace.startswith("ch"):
                    #header & X
                    cmd = "CHAN" + trace[-1] + ":STAT?"
                    if not int(dev.query(cmd)):
                        exit("Channel is off!")
                    cmd = "CHAN" + trace[-1] + ":DATA:HEAD?"
                    hdr = dev.query(cmd).split(",")
                    pts = int(hdr[2])
                    x = np.linspace(float(hdr[0]), float(hdr[1]), num=pts)
                    #Y
                    units = "V"
                    cmd = "CHAN" + trace[-1] + ":DATA?"
                    y = dev.query_binary_values(cmd, datatype='f', is_big_endian=False)
                    writedata = True
                elif trace.startswith("math"):
                    cmd = "CALC:MATH:" + trace[-1] + ":STAT?"
                    if not int(dev.query(cmd)):
                        exit("Math is off!")
                    cmd = "CALC:MATH" + trace[-1] + ":DATA:HEAD?"
                    hdr = dev.query(cmd).split(",")
                    pts = int(hdr[2])
                    x = np.linspace(float(hdr[0]), float(hdr[1]), num=pts)
                    #Y
                    units = "V"
                    cmd = "CALC:MATH" + trace[-1] + ":DATA?"
                    y = dev.query_binary_values(cmd, datatype='f', is_big_endian=False)
                else: #must be fft
                    prefix = "SPEC:WAV:SPEC:" if trace == "fft" else "SPEC:WAV:AVER:"
                    cmd = prefix + "ENAB?"
                    if not int(dev.query(cmd)):
                        exit("FFT is off!")
                    cmd = prefix + "DATA:HEAD?"
                    hdr = dev.query(cmd).split(",")
                    pts = int(hdr[2])
                    x = np.linspace(float(hdr[0]), float(hdr[1]), num=pts)
                    #Y
                    cmd = prefix + "DATA?"
                    y = dev.query_binary_values(cmd, datatype='f', is_big_endian=False)
                    units = dev.query("SPEC:FREQ:MAGN:SCAL?").rstrip()
                    rb = dev.query("SPEC:FREQ:BAND:VAL?").rstrip()
                    print("# RES BW = %s\n#" % (rb))
                    writedata = True
                    
            if writedata:
                print("#\n# Y UNITS = %s\n#" % (units))
                if comment:
                    print("# COMMENT: %s\n#" % (comment))
                    
                for i in range(pts):
                    print("%e\t%e" % (x[i], y[i]))

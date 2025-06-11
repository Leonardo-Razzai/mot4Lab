from interface_app.Interface_app import *

class SA_Rigol(VISA_inst):
    """
    A class for controlling a Rigol Spectrum Analyzer using the VISA interface.

    Inherits from the VISA_inst class.

    Attributes:
        dev (pyvisa.Resource): The instrument resource object for communication.
    """

    def __init__(self) -> None:
        """
        Initializes the SPA_Rigol object and sets the trace mode.

        Args:
            rm (pyvisa.ResourceManager): The resource manager object from PyVISA.
        """
        instr_name = "SA_Rigol"
        super().__init__(instr_name=instr_name)
        

    def Set_Trace_Write(self):
        self.dev.write(f':TRACe1:MODE WRIT')
        
    def Set_Scale(self, scale: str):
        """
        Sets the y-axis scale of the display.

        Args:
            scale (str): The desired scale for the y-axis. Can be 'LINear' or 'LOGarithmic'.
        """
        self.dev.write(f':DISP:WIN:TRAC:Y:SCAL:SPAC {scale}')

    def Set_AutoRangeY(self):
        """
        Automatically adjusts the y-axis scale to ensure the signal peak spans the entire vertical range of the display.
        """
        self.dev.write(":POWer:ASCale")

    def Set_Span(self, span: float):
        """
        Sets the frequency span of the spectrum analyzer.

        Args:
            span (float): The frequency span to set, in Hz.
        """
        self.dev.write(f':FREQ:SPAN {span}')

    def Set_Center_Freq(self, freq: float):
        """
        Sets the center frequency of the spectrum analyzer.

        Args:
            freq (float): The center frequency to set, in Hz.
        """
        self.dev.write(f':FREQ:CENT {freq}')

    def Set_TraceType(self, trace=1, trace_type='WRIT'):
        """
        Configures the type of trace operation.

        Args:
            trace (int): The trace number to configure (default is 1).
            trace_type (str): The trace mode. Options include 'WRITe', 'MAXHold', 'MINHold', 
                              'VIEW', 'BLANk', 'VIDeoavg', 'POWeravg'.
        """
        self.dev.write(f':TRACe<{trace}:MODE {trace_type}')

    def Get_Peak(self, span_about_cent=1e8):
        """
        Finds the peak signal in the current trace and centers the frequency around it.

        Args:
            span_about_cent (float): The span to set around the center frequency, in Hz (default is 2e8).

        Returns:
            tuple: A tuple containing the frequency (X coordinate) and amplitude (Y coordinate) of the peak.
        """
        self.dev.write(':CALC:MARK1:MAX:MAx')  # Find the peak on the right side
        self.dev.write(':CALC:MARK1:SET:CENT')  # Center about marker 1
        self.dev.write(f':FREQ:SPAN {span_about_cent}')
        time.sleep(1)
        self.dev.write(':CALC:MARK1:MAX:MAx')
        freq = self.dev.query(':CALC:MARK1:X?')  # Get X coordinate (frequency)
        height = self.dev.query(':CALC:MARK1:Y?')  # Get Y coordinate (amplitude)
        return freq, height
    
    def Get_Trace(self, file_name: str, trace=1):
        ans = self.dev.query(f":TRACE{trace}:MODE?")
        if ans.startswith("BLAN"):
            print("Empty trace!")
            exit()
        else:
            #X
            pts = int(self.dev.query(":SWE:POIN?"))
            start = float(self.dev.query(":FREQ:STAR?"))
            stop = float(self.dev.query(":FREQ:STOP?"))
            x = np.linspace(start, stop, num=pts)
            
            # Y units, RBW
            units = self.dev.query(":UNIT:POW?").rstrip()
            rb = self.dev.query(":SENS:BAND:RES?").rstrip()
            vb = self.dev.query(":SENS:BAND:VID?").rstrip()
            swt = self.dev.query(":SENS:SWE:TIME?").rstrip()
            
            # Y
            self.dev.write(":FORM:TRAC:DATA REAL,32")
            self.dev.write(":FORM:BORD NORM")
            y = self.dev.query_binary_values(f":TRAC:DATA? TRACE{trace}")
        
        with open(file_name, 'w') as file:
            #output
            file.write("#\n# Y UNITS = %s\n#" % (units))
            file.write("# RES BW = %s\n#" % (rb))
            file.write("# VIDEO BW = %s\n#" % (vb))
            file.write("# SWEEP TIME = %s\n" % (swt))
            file.write('Freq,Amp\n')
            
            for i in range(pts):
                file.write("%e, %e\n" % (x[i], y[i]))
    
    def Save_Result(self, file_name: str):
        self.dev.write(f':MMEMory:STORe:RESults E:\{file_name}')
        
    def Save_Trace(self, file_name: str, tr_label= 'TRACE1'):
        """
        Saves the current trace data to a file on the device's storage.

        Args:
            file_name (str): The name of the file to save the trace to.
            tr_label (str): The trace label to save (default is 'TRACE1').
        """
        self.dev.write(f':MMEM:STOR:TRAC {tr_label},E:{file_name}')
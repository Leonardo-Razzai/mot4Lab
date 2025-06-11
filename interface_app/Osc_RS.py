from interface_app.Interface_app import *

class Osc_RS(VISA_inst):
    """
    A class to control and retrieve data from the R&S RTM3000 oscilloscope using SCPI commands over VISA.
    
    Attributes
    ----------
    instr_name : str
        The name of the instrument.
    channel : int
        The oscilloscope channel to operate on, defaulting to channel 2.
    
    Methods
    -------
    Set_Channel(channel=2)
        Sets the active channel for measurements with validation.
        
    Set_coupling(coupling='DC')
        Sets the coupling for the current channel (DC or AC).
        
    Set_vertical_range(range=1.0)
        Sets the vertical range for the current channel in volts.
        
    Set_horizontal_range(range=1.0)
        Sets the horizontal (time) range in seconds.
        
    Start_acquisition()
        Starts data acquisition on the oscilloscope.
        
    Stop_acquisition()
        Stops data acquisition on the oscilloscope.
        
    Check_acquisition_complete()
        Checks if the acquisition is complete and ready for data retrieval.
        
    Get_Data()
        Retrieves waveform data from the oscilloscope. Returns the x (time) and y (voltage) data arrays.
        
    Acquire_and_Get_Data()
        Automates acquisition and data retrieval in one step.
    """

    def __init__(self, channel=2, channel_trigger=1, data_format='REAL') -> None:
        """
        Initializes the Osc_RS object with default channel and data format for the RTM3000 oscilloscope.
        
        Parameters
        ----------
        channel : int, optional
            The oscilloscope channel to use, by default 2.
        data_format : str, optional
            Data format for waveform (e.g., 'REAL'), by default 'UINT,16'.
        """
        instr_name = "Osc_RS"
        self.channel = channel
        self.channel_trigger = channel_trigger
        
        super().__init__(instr_name=instr_name)

        # Configure device with maximum data points and data format
        self.Set_data_format(data_format)
        self.Set_Channel()
        
    def Set_Channel(self, channel=2):
        """
        Sets the active channel for measurements after validation.
        
        Parameters
        ----------
        channel : int
            The channel number (1, 2, 3, or 4) depending on the oscilloscope model.
        
        Raises
        ------
        ValueError
            If the channel number is out of the oscilloscope’s supported range.
        """
        if channel not in (1, 2, 3, 4):  # RTM3004 supports up to 4 channels
            raise ValueError(f"Channel {channel} is not valid. Select a supported channel.")
        
        self.channel = channel
        self.dev.write(f'CHAN{self.channel}:STAT ON')
    
    def Set_Channel_trigger(self, channel=1):
        if channel not in (1, 2, 3, 4):  # RTM3004 supports up to 4 channels
            raise ValueError(f"Channel {channel} is not valid. Select a supported channel.")
        
        self.channel_trigger = channel
        self.dev.write(f'CHAN{self.channel_trigger}:STAT ON')

    def Set_data_format(self, data_format='REAL'):
        """
        Sets the data format for waveform retrieval.
        
        Parameters
        ----------
        data_format : str
            SCPI data format, e.g., 'UINT,16'.
        """
        self.dev.write('CHAN:TYPE HRES')
        self.dev.write(f'FORM {data_format}')
        self.dev.write("FORM:BORD LSBF")       # Little-endian format
        
    def Set_coupling(self, coupling='DC'):
        """
        Sets the input coupling mode for the current channel.
        
        Parameters
        ----------
        coupling : str
            Coupling mode, either 'DC' or 'AC'.
        """
        self.dev.write(f'CHAN{self.channel}:COUP {coupling}')
        
    def Set_vertical_range(self, range=1.0):
        """
        Sets the vertical range in volts for the specified channel.
        
        Parameters
        ----------
        range : float
            The vertical range in volts.
        """
        self.dev.write(f'CHAN{self.channel}:RANGe {range}')
        
    def Set_horizontal_range(self, range=1.0):
        """
        Sets the horizontal (time) range in seconds.
        
        Parameters
        ----------
        range : float
            The horizontal range in seconds.
        """
        self.dev.write(f'TIMebase:RANGe {range}')
        self.dev.write('CHAN:DATA:POINTS DMAX')
    
    def Start_single(self):
        """
        Starts single acquisition on the oscilloscope.
        """
        self.dev.write('SING; *OPC?')
    
    def Start_acquisition(self):
        """
        Starts single acquisition on the oscilloscope.
        """
        self.dev.write('RUN')
    
    def Stop_acquisition(self):
        """
        Stops acquisition on the oscilloscope.
        """
        self.dev.write('STOP')
        
    def Check_acquisition_complete(self):
        """
        Checks if acquisition is complete using the *OPC? command.

        Returns
        -------
        bool
            True if acquisition is complete, otherwise False.
        """
        return self.dev.query('*OPC?') == '1'
    
    def Wait_acquisition_end(self):
        while self.dev.query("ACQ:STAT?") != "COMP":
            time.sleep(0.1)
                    
    def Clear_Buffer(self):
        """Clear data buffer of oscilloscope
        """
        self.dev.write("*CLS")
        self.dev.write("STOP")
        self.dev.write(f"CHAN{self.channel}:DATA:CLE")

    def Get_Data(self):
        """
        Retrieves waveform data from the oscilloscope.
        
        Returns
        -------
        tuple
            A tuple containing x_data and y_data as NumPy arrays.
        
        Raises
        ------
        RuntimeError
            If data retrieval fails or acquisition is incomplete.
        """
        
        try:
            # Retrieve waveform header information
            header = self.dev.query(f'CHAN{self.channel}:DATA:HEAD?')
            x_min, x_max, record_length, _ = map(float, header.split(','))
            print(f'x_min = {x_min}, x_max = {x_max}, record_length = {record_length}')
            # Retrieve waveform data
            time.sleep(0.5)
            raw_data = self.dev.query_binary_values(f'CHAN{self.channel}:DATA?', datatype='f', is_big_endian=False)
            y_data = np.array(raw_data)

            # Generate x-axis time values based on header information
            dx = (x_max - x_min) / record_length
            x_data = np.arange(0, record_length) * dx
            
            self.Clear_Buffer()
            
            return x_data, y_data
        
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve data: {e}")
        
    def Acquire_and_Get_Data(self):
        """
        Starts acquisition, waits for completion, and retrieves waveform data.
        
        Returns
        -------
        tuple
            A tuple containing x_data and y_data as NumPy arrays.
        """
        self.Start_acquisition()
        if self.Check_acquisition_complete():
            time.sleep(1)
            return self.Get_Data()
        else:
            raise RuntimeError("Acquisition failed to complete.")
    
    def Get_Meas(self, channel=1):
        
        res = float(self.dev.query(f'MEAS{channel}:RESULT?'))
        return res
from interface_app.Interface_app import *

class Func_Gen(VISA_inst):
    def __init__(self) -> None:
        instr_name = "FuncGen_Rigol"
        super().__init__(instr_name=instr_name)
    
    def Set_Func(self, Func='SQU'):
        self.dev.write(f':SOUR1:FUNC {Func}')
        
    def Set_Amp(self, Amp: float):
        self.dev.write(f':SOUR1:VOLT {Amp}')
    
    def Set_Freq(self, Freq: float):
        self.dev.write(f':SOUR1:FREQ {Freq}')
    
    def Set_Offset(self, Offset: float):
        self.dev.write(f':SOUR1:VOLT:OFFS {Offset}')
        
    def Set_Output(self, State: str):
        self.dev.write(f':OUTP1 {State}')
from Modules.MOTAcqLib import show_img
import datetime
from sys import argv

f_name = argv[1] 
fits_name = f'raw_data/{datetime.today()}/img/{f_name}'

show_img(fits_name)
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import sys

def show_img(img_base_name, tof_val):

    with fits.open(f"./img/{img_base_name}_tof={tof_val:.1f}ms.fits.gz") as hdul:
        img = hdul[0].data
        plt.imshow(img)
        plt.title(f'Tof={tof_val:.1f} ms, MaxVal = {np.max(img)}')
        plt.show()
        hdul.close()

img_base_name = sys.argv[1]
tof_val = float(sys.argv[2])

show_img(img_base_name, tof_val)
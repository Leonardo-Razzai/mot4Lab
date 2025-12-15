import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import sys

def show_img(file_name):
    with fits.open(f"./img/{file_name}.fits.gz") as hdul:
        img = hdul[0].data
        plt.imshow(img)
        plt.title(f'Tot counts={np.sum(img):.2e}, MaxVal = {np.max(img):.2e}')
        plt.show()
        hdul.close()

def show_imgs_tof(img_base_name, tof_val):
    with fits.open(f"./img/{img_base_name}_tof={tof_val:.1f}ms.fits.gz") as hdul:
        img = hdul[0].data
        plt.imshow(img)
        plt.title(f'Tof={tof_val:.1f} ms, MaxVal = {np.max(img)}')
        plt.show()
        hdul.close()

file_name = sys.argv[1]

show_img(file_name)
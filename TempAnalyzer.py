# Description: This script is used to analyze the images in the images folder.
import matplotlib.pyplot as plt 
import numpy as np
from scipy.optimize import curve_fit
from astropy.io import fits

MEDIUM_SIZE = 13
BIGGER_SIZE = 15

plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize

base_font = {'family': 'serif',
        'size': MEDIUM_SIZE,
        }

title_font = {
  'fontsize' : BIGGER_SIZE, 
  'font' : 'serif', 
  'weight' : 'bold'
}

# Define constants
# M = 0.175 # magnification (nominally 0.25)
# err_rel_M = 0.02

# M = 0.4 # magnification from p/q
M = 0.33 # magnification from last calibration with mot (23-06-2025)
err_rel_M = 0.05 # relative error in magnification
PIXEL_SIZE = 0.0069 / M # mm # pixel size in MOT plane
M_Rb87 = 86.909 * 1.660539e-27 # Rb87 mass in kg
KB = 1.38064852e-23 # Boltzmann constant in J/K

# path to image folder
PATH_TO_IMG = './img'

class Image:
    def __init__(self, image):
        self.image = image
        with fits.open(f'{PATH_TO_IMG}/{image}') as hdul:
            self.im = hdul[0].data
            
        self.row_sum = self.im.sum(axis=0)
        self.col_sum = self.im.sum(axis=1)
        
        self.mu_x = 0.0
        self.mu_y = 0.0 
        self.sigma_x = 0.0
        self.sigma_y = 0.0
    
    def select_roi(self, y1, y2, x1, x2):
        self.im = self.im[y1:y2, x1:x2]
    
    def show_img(self):
        plt.imshow(self.im)
        plt.show()
    
    def plot_axis(self, axis='x'):
        if axis == 'x':
            xdata = np.arange(len(self.row_sum))
            ydata = np.array(self.row_sum)
        elif axis == 'y':
            xdata = np.arange(len(self.col_sum))
            ydata = np.array(self.col_sum)
        else:
            raise ValueError("Invalid axis")
                            
        plt.plot(xdata, ydata)
        plt.legend()
        plt.title(f'Sum along {axis} axis')
        plt.xlabel(f'{axis} (pixels)')
        plt.ylabel('Intensity')
        plt.grid()
        plt.show()
        plt.close()
    
    def fit_gaussian(self, axis='x', plot=False):
        if axis == 'x':
            xdata = np.arange(len(self.row_sum))
            ydata = np.array(self.row_sum)
        elif axis == 'y':
            xdata = np.arange(len(self.col_sum))
            ydata = np.array(self.col_sum)
        else:
            raise ValueError("Invalid axis")
        
        try:
            popt, pcov = curve_fit(gaussian, xdata, ydata, 
                        p0 = [np.max(ydata) - np.min(ydata), np.argmax(ydata), np.max(xdata) / 10, np.min(ydata)], maxfev=100000)
            
            if axis == 'x':
                self.mu_x = popt[1]
                self.sigma_x = abs(popt[2])
            elif axis == 'y':
                self.mu_y = popt[1]
                self.sigma_y = abs(popt[2])
                         
            if plot:
                plt.plot(xdata, ydata)
                plt.plot(xdata, gaussian(xdata, *popt), '--', color='red', label='Gaussian: ' + f'sigma={popt[2]:.0f}')
                plt.legend()
                plt.title(f'Fit of 2 Gaussians along {axis} axis')
                plt.xlabel(f'{axis} (pixels)')
                plt.ylabel('Intensity')
                plt.grid()
                plt.show()
                plt.close()

        except RuntimeError as err:
            print("Error in fitting" + " axis: " + axis + " image: " + self.image)
            print(f"Error: {err}")
            popt = []

        return popt
    

def gaussian(x, A, mu, sigma, C):
    return A * np.exp(-0.5 * ((x - mu) / sigma)**2) + C

def get_temperature(im1: Image, im2: Image, t1: float, t2: float):
    """
    Calculate the temperature from the variance and time of flight.
    """
    var1 = im1.sigma_x**2 * PIXEL_SIZE**2
    var2 = im2.sigma_x**2 * PIXEL_SIZE**2
    dvar1 = 2 * err_rel_M * var1
    dvar2 = 2 * err_rel_M * var2
    
    v_2 = (var2 - var1) / (t2**2 - t1**2)
    dv_2 = (dvar1 + dvar2) / (t2**2 - t1**2)
    
    T = v_2 * M_Rb87 /  KB * 1e6 # uK
    dT = dv_2 * M_Rb87 /  KB * 1e6
    
    return T, dT

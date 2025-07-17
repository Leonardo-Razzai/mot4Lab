# Description: This script is used to analyze the images in the images folder.
import matplotlib.pyplot as plt 
import numpy as np
from scipy.optimize import curve_fit
from astropy.io import fits

SMALL_SIZE = 8
MEDIUM_SIZE = 14
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

M_pix = 53 # pix/mm calibration 2 with mot (23-06-2025)
err_rel_M = 1/M_pix
PIXEL_SIZE = 1/M_pix

M_Rb87 = 86.909 * 1.660539e-27 # Rb87 mass in kg
KB = 1.38064852e-23 # Boltzmann constant in J/K

# path to image folder
Gamma = 2 * np.pi * 6.065e6 # Hz

def rescale_image(img_array):
    '''Rescales the image assuming format 16 bits and bith depth 12 bits.
    The least significant 4 bits are padding, so they have to be discarded.'''
    
    clean_img = img_array & ((1 << 16) - (1 << 4)) # set least significant 4 bits to 0
    return clean_img // 2**4

class Image:
    def __init__(self, image):
        self.image = image
        with fits.open(image) as hdul:
            self.im_orig = rescale_image(hdul[0].data)
            self.im = self.im_orig
            hdr = hdul[0].header
            self.Gain = hdr['GAIN'] # gain in dB
            
        self.row_sum = self.im.sum(axis=0)
        self.col_sum = self.im.sum(axis=1)
        self.tot_counts = self.im.sum()
        
        self.mu_x = 0.0
        self.mu_y = 0.0 
        self.sigma_x = 0.0
        self.sigma_y = 0.0
    
    def select_roi(self, y1, y2, x1, x2):
        self.im = self.im_orig[y1:y2, x1:x2]
        self.row_sum = self.im.sum(axis=0)
        self.col_sum = self.im.sum(axis=1)
        self.tot_counts = self.im.sum()
    
    def show_img(self):
        fig, ax = plt.subplots(1)
        ax.imshow(self.im)
        legend = f"MaxCounts = {self.im.max():.0f}\n" + f"Gain = {self.Gain:.0f} dB"
        ax.text(10, 40, legend, bbox={'facecolor': 'white'}, fontdict={'fontsize': SMALL_SIZE})
        plt.show()
            
    def plot_axis(self, axis='x'):
        self.row_sum = self.im.sum(axis=0)
        self.col_sum = self.im.sum(axis=1)
        self.tot_counts = self.im.sum()
        
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
        self.row_sum = self.im.sum(axis=0)
        self.col_sum = self.im.sum(axis=1)
        self.tot_counts = self.im.sum()
        
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
                self.int_x = popt[0] * np.sqrt(2 * np.pi) * self.sigma_x
                self.cx = popt[3] * len(xdata) # baseline counts
                Na, dNa = self.Get_Number_Of_Atoms('x')
                
            elif axis == 'y':
                self.mu_y = popt[1]
                self.sigma_y = abs(popt[2])
                self.int_y = popt[0] * np.sqrt(2 * np.pi) * self.sigma_y
                self.cy = popt[3] * len(xdata) # baseline counts
                Na, dNa = self.Get_Number_Of_Atoms('y')
                         
            if plot:
                plt.plot(xdata, ydata)
                label = 'Gaussian Fit: ' + f'\nA = {popt[0]:.0f}\n' + r'$\mu$ ='+f'{popt[1]:.0f}\n' r'$\sigma$ ='+f'{popt[2]:.0f}\n\n'
                num_label = r'$N_{atoms}$ = ' + f'({Na /1e8:.1f}' + r'$\pm$' + f'{dNa /1e8:.1f})' + r'x$10^8$'
                plt.plot(xdata, gaussian(xdata, *popt), '--', color='red', label=label+num_label)
                plt.legend(fontsize = SMALL_SIZE)
                plt.title(f'Gaussian Fit along {axis} axis')
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
    
    def Get_Number_Of_Atoms(self, axis='x'):
        """
        Calculate the number of atoms in the image from Integral of the Gaussian.
        
        NB: Assume 16 bit format, 12 bit depth
        """
        
        G_dB = self.Gain
        G = 10**(G_dB / 20) # convert dB to linear scale
        eta = 0.28 # quantum efficiency of the camera at 780 nm (Datasheet)
        eADU_0dB = 110.7 # 0.35 at 50 dB, 12 bit
        eADU_G = eADU_0dB / G # e/ADU at gain G
        
        R_lens = 1.42 # aperture radius in cm
        dist_mot = 18 # cm
        fractional_sigma = 0.25 * (R_lens/dist_mot)**2
        t_pulse = 300e-6 # s        

        Delta = 2.2 * Gamma
        N_ph_per_atom = SC_Rate(Delta) * t_pulse
        N_el_per_atom = N_ph_per_atom * fractional_sigma * eta
        N_counts_per_atom = N_el_per_atom / eADU_G
        
        if axis == 'x':
            N_counts_MOT = self.int_x
        elif axis == 'y':
            N_counts_MOT = self.int_y
        else:
            raise ValueError("Invalid axis")
        
        N_atoms = N_counts_MOT / N_counts_per_atom
        print(f'Number of Atoms = {N_atoms:.2e}')
        print(f'Integral of Gaussian = {N_counts_MOT:.2e}, N_tot by diff. = {self.tot_counts - self.cx:.2e}')
        
        return N_atoms, 0.1*N_atoms
    

def gaussian(x, A, mu, sigma, C):
    return A * np.exp(-0.5 * ((x - mu) / sigma)**2) + C

def Get_temperature(im1: Image, im2: Image, t1: float, t2: float):
    """
    Calculate the temperature from the variance along x and time of flight.
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

def SC_Rate(Delta):
    s0 = 34 # saturation parameter P = 65 mW
    return Gamma / 2 * s0 / (1 + s0 + 4 * (Delta / Gamma)**2)

def Analysis_Num_and_T(dataset, t1, t2):
    
    base_name = dataset['base_name']
    x_label = dataset['x_label']
    unit = dataset['unit']
    iterator = dataset['iterator']

    T_list = []
    err_T_list = []

    N_atoms_list = []
    err_N_atoms_list = []
    
    for val in iterator:
        print('----------------------------------------------------------')
        im1 = Image(f'{base_name}={val}{unit}_tof={t1:.1f}ms.fits.gz')
        im1.select_roi(0, 400, 0, 600)
        im1.fit_gaussian('x', plot=False)
        
        im2 = Image(f'{base_name}={val}{unit}_tof={t2:.1f}ms.fits.gz')
        im2.select_roi(0, 400, 0, 600)
        im2.fit_gaussian('x', plot=False)
        
        N_atoms, err_N_atoms = im2.Get_Number_Of_Atoms(axis='x')
        
        N_atoms_list.append(N_atoms)
        err_N_atoms_list.append(err_N_atoms)
        
        T, dT = Get_temperature(im1, im2, t1, t2)
        
        T_list.append(T)    
        err_T_list.append(dT)
        
        print(f'{x_label}: {val}, Temp: ({T:.2f} +- {dT:.2f}) uK\n')
        
    return T_list, err_T_list, N_atoms_list, err_N_atoms_list

def Analysis_and_Plotting(dataset):
    
    base_name = dataset['base_name']
    x_label = dataset['x_label']
    unit = dataset['unit']
    iterator = dataset['iterator']
    
    T_list, err_T_list, N_atoms_list, err_N_atoms_list = Analysis_Num_and_T(dataset, t1=2.0, t2=20.0)
        
    # plotting
    plt.figure(figsize=(8, 5))
    plt.errorbar(iterator, T_list, err_T_list, fmt='o', alpha=0.9, color='blue', ecolor='royalblue', capsize=5, label='Data')
    plt.xlabel(f'{x_label} ({unit})', fontdict=base_font)
    plt.ylabel('Temp (uK)', fontdict=base_font)
    plt.title(f'Temperature vs {x_label}', fontdict=title_font)
    plt.grid(linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'Temp_vs_{base_name}.png')
    plt.clf()
    plt.close()
    
    N_atoms = np.array(N_atoms_list) * 1e-8  # convert to 10^8
    err_N_atoms = np.array(err_N_atoms_list) * 1e-8  # assuming 10% error
    plt.figure(figsize=(8, 5))
    plt.errorbar(iterator, N_atoms, err_N_atoms, fmt='o', alpha=0.9, color='blue', ecolor='royalblue', capsize=5, label='Data')
    plt.xlabel(f'{x_label} ({unit})', fontdict=base_font)
    plt.ylabel(r'Num Atoms ($10^8$)', fontdict=base_font)
    plt.title(f'Num of Atoms vs {x_label}', fontdict=title_font)
    plt.grid(linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'Num_atoms_vs_{base_name}.png')
    plt.clf()
    plt.close()  
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

M_pix = 45.2 # pix/mm calibration 2 with mot (16-12-2025)
PIXEL_SIZE = 20.9e-3 # mm/px (Manta: claibrated on 02-09-2026)
err_rel_M = 0.2e-3/PIXEL_SIZE

# FLIR
# CCD_counts_per_photon = 0.58 # counts per photon calib 24-07-2025
# err_rel_counts_per_photon = 0.02

# Manta
CCD_counts_per_photon = 1/7.28 # counts per photon calib 16-06-2026
err_rel_counts_per_photon = 0.05

M_Rb87 = 86.909 * 1.660539e-27 # Rb87 mass in kg
KB = 1.38064852e-23 # Boltzmann constant in J/K

# path to image folder
Gamma = 2 * np.pi * 6.065e6 # Hz

def clean_image(img_array):
    '''Rescales the image assuming format 16 bits and bith depth 12 bits.
    The least significant 4 bits are padding, so they have to be discarded.'''
    
    clean_img = img_array & ((1 << 16) - (1 << 4)) # set least significant 4 bits to 0
    return clean_img

class Image:
    def __init__(self, image):
        self.image = image
        with fits.open(image) as hdul:
            self.im_orig = clean_image(hdul[0].data)
            # print(f'{self.image}: Min = {self.im_orig.min()}, Max = {self.im_orig.max()}')
            self.im = self.im_orig
            self.hdr = hdul[0].header
            self.Gain = self.hdr['GAIN'] # gain in dB
        
        
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
        
    def subtract_bkg(self, fn_bkg):
        img_bkg = Image(fn_bkg)
        if img_bkg.Gain != self.Gain:
            print('Different Gain between this image and background image')
        else:
            self.im = self.im - img_bkg.im
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
            
            Na =  None
            dNa = None
            if axis == 'x':
                self.mu_x = popt[1]
                self.sigma_x = abs(popt[2])
                self.int_x = popt[0] * np.sqrt(2 * np.pi) * self.sigma_x
                self.cx = popt[3] * len(xdata) # baseline counts
                Res_N = self.Get_Number_Of_Atoms('x')
                if Res_N != None:
                    Na, dNa = Res_N

            elif axis == 'y':
                self.mu_y = popt[1]
                self.sigma_y = abs(popt[2])
                self.int_y = popt[0] * np.sqrt(2 * np.pi) * self.sigma_y
                self.cy = popt[3] * len(xdata) # baseline counts
                Res_N = self.Get_Number_Of_Atoms('y')
                if Res_N != None:
                    Na, dNa = Res_N

            label = f'\nResults from 1 Gaussian Fit, axis = {axis}: ' + f'\nA = {popt[0]:.0f}\n' + 'mu ='+f'{popt[1]:.0f}\n' 'sigma ='+f'{popt[2]:.0f}'
            
            if Na != None:
                num_label = f'\nN = ({Na /1e8:.1f} +- {dNa /1e8:.1f}) x 10^8'
                label += num_label

            print(label)
            if plot:
                plt.plot(xdata, ydata)
                label = 'Gaussian Fit: ' + f'\nA = {popt[0]:.0f}\n' + r'$\mu$ ='+f'{popt[1]:.0f}\n' r'$\sigma$ ='+f'{popt[2]:.0f}\n'
                if Na != None:
                    num_label = r'$N_{atoms}$ = ' + f'({Na /1e8:.1f}' + r'$\pm$' + f'{dNa /1e8:.1f})' + r'x$10^8$'
                    label += num_label

                plt.plot(xdata, gaussian(xdata, *popt), '--', color='red', label=label)
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
        
        R_lens = 1.42 # aperture radius in cm
        dist_mot = 20 # cm
        fractional_sigma = 0.25 * (R_lens/dist_mot)**2
        t_pulse = None

        try:
            t_pulse = self.hdr['T_PROBE'] * 1e-6 # s
        except KeyError as e:
            print('No t_probe found. Continuing...')
            pass
        
        if t_pulse != None:
            Delta = 2.2 * Gamma
            N_ph_per_atom = SC_Rate(Delta) * t_pulse
            N_counts_per_atom = N_ph_per_atom * fractional_sigma * G * CCD_counts_per_photon
        
            if axis == 'x':
                N_counts_MOT = self.int_x
            elif axis == 'y':
                N_counts_MOT = self.int_y
            else:
                raise ValueError("Invalid axis")
            
            N_atoms = N_counts_MOT / N_counts_per_atom
            #print(f'Number of Atoms = {N_atoms:.2e}')
            #print(f'Integral of Gaussian = {N_counts_MOT:.2e}, N_tot by diff. = {self.tot_counts - self.cx:.2e}')
            
            err_rel_dist = 1 / dist_mot
            err_rel_sigma = 2 * err_rel_dist
            
            err_rel_N = err_rel_sigma + err_rel_counts_per_photon
            dN_atoms = N_atoms * err_rel_N
            
            return N_atoms, dN_atoms
        else:
            return None
    
    def Get_Number_Of_Atoms_avg(self):
        Nx, dNx = self.Get_Number_Of_Atoms('x')
        Ny, dNy = self.Get_Number_Of_Atoms('y')
        weights = np.array([1/dNx**2, 1/dNy**2])
        N_atoms = np.average([Nx, Ny], weights=weights)
        dN_atoms = np.sqrt(1 / np.sum(weights))
        return N_atoms, dN_atoms
    
    def GetCM(self):
        return (self.mu_x, self.mu_y)
    
def gaussian(x, A, mu, sigma, C):
    return A * np.exp(-0.5 * ((x - mu) / sigma)**2) + C

def Get_temperature_avg(im1: Image, im2: Image, t1: float, t2: float):
    Tx, dTx = Get_temperature(im1, im2, t1, t2, axis='x')
    Ty, dTy = Get_temperature(im1, im2, t1, t2, axis='y')
    weights = np.array([1/dTx**2, 1/dTy**2])
    T = np.average([Tx, Ty], weights=weights)
    dT = np.sqrt(1 / np.sum(weights))
    return T, dT
    
def Get_temperature(im1: Image, im2: Image, t1: float, t2: float, axis='x'):
    """
    Calculate the temperature from the variance along x and time of flight.
    """
    if axis == 'x':
        sigma1 = im1.sigma_x
        sigma2 = im2.sigma_x
    elif axis == 'y':
        sigma1 = im1.sigma_y
        sigma2 = im2.sigma_y
        
    var1 = sigma1**2 * PIXEL_SIZE**2
    var2 = sigma2**2 * PIXEL_SIZE**2
    dvar1 = 2 * err_rel_M * var1
    dvar2 = 2 * err_rel_M * var2
    
    v_2 = (var2 - var1) / (t2**2 - t1**2)
    dv_2 = (dvar1 + dvar2) / (t2**2 - t1**2)
    
    T = v_2 * M_Rb87 /  KB * 1e6 # uK
    dT = dv_2 * M_Rb87 /  KB * 1e6
    
    return T, dT

def Sat_param():
    
    P_MOT = 48 # mW, MOT beams power (measured on 15-09-2026)
    
    NA = 0.16
    f = 7.5 # cm
    w0 = NA * f
    P_cool_beam = 0.25 * P_MOT/3
    I_cool_beam = 2*P_cool_beam / (np.pi * w0**2)
    I_cool = 6 * I_cool_beam
    I_sat = 1.67 # mW/cm^2
    return I_cool / I_sat

def SC_Rate(Delta):
    s0 = Sat_param()# saturation parameter
    return Gamma / 2 * s0 / (1 + s0 + 4 * (Delta / Gamma)**2)  
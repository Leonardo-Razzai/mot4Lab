from TempAnalyzer import *

base_name = ''
x_label = 'keep_mol'
unit = 'ms'

iterator = [0.1, 5.0, 10.0, 15.0, 20.0, 25.0]
T_list = []
err_T_list = []

t1 = 2.0  # ms
t2 = 20.0  # ms
    
for val in iterator:
    im1 = Image(f'{base_name}={val}{unit}_tof={t1:.1f}ms.fits.gz')
    im1.fit_gaussian('x', plot=True)

    im2 = Image(f'{base_name}={val}{unit}_tof={t2:.1f}ms.fits.gz')
    im2.fit_gaussian('x', plot=True)
    
    T, dT = get_temperature(im1, im2, t1, t2)
    
    T_list.append(T)    
    err_T_list.append(dT)
    
    print(f'{x_label}: {val}, Temp: ({T:.2f} +- {dT:.2f}) uK')
    
# plotting
import matplotlib.pyplot as plt
plt.errorbar(iterator, T_list, err_T_list, fmt='o', alpha=0.9, color='blue', ecolor='royalblue', capsize=5, label='Data')
plt.xlabel(f'{x_label} ({unit})', fontdict=base_font)
plt.ylabel('Temp (uK)', fontdict=base_font)
plt.title(f'Temperature vs {x_label}', fontdict=title_font)
plt.grid()
plt.savefig(f'Temp_vs_{x_label}.png')


